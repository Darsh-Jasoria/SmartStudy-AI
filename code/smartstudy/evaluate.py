"""Rubric-based evaluation: python3 -m smartstudy.evaluate --versions v0 v1 v2 v3 v4

Automatic rubric (all computed against gold files in data/gold):
  term_recall       gold key terms found among output terms ("a|b" = accepted synonyms)
  coverage          share of gold must-cover ideas present in summary + definitions
  term_halluc       output terms that do not appear in the notes
  ungrounded_q      questions whose evidence quote is not a quote from the notes (0 evidence = ungrounded)
  answer_support    share of questions whose answer words are mostly present in the notes
  outside_know      count of out-of-scope terms (true but NOT taught in the notes) that leaked into the pack
  constraints       share of runs meeting: N questions, summary <= word limit, >=3 question types incl. mcq
  json_fail         runs whose output could not be parsed
Human rubric (clarity, correctness, usefulness, 1-5) is in docs/human_eval_rubric.md.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import time
from pathlib import Path

from .llm import LLMError
from .pipeline import VERSIONS, norm, run
from .replay import Missing

ROOT = Path(__file__).resolve().parent.parent.parent   # repository root
N_Q, MAX_W = 5, 100


def load_cases(data_dir: Path):
    out = []
    for p in sorted((data_dir / "notes").glob("*.txt")):
        out.append({"id": p.stem, "notes": p.read_text().strip(),
                    "gold": json.loads((data_dir / "gold" / f"{p.stem}.json").read_text())})
    return out


def has(text_norm: str, phrase: str) -> bool:
    p = norm(phrase)
    return bool(p) and re.search(rf"(?<![a-z0-9]){re.escape(p)}", text_norm) is not None


def term_match(out_term: str, gold_alts: str) -> bool:
    o = norm(out_term)
    for g in gold_alts.split("|"):
        g = norm(g)
        if g and (o == g or (len(g) > 3 and (g in o or o in g) and len(o) > 3)):
            return True
    return False


def score(res: dict, case: dict) -> dict:
    notes_n, gold = norm(case["notes"]), case["gold"]
    terms, qs = res["key_terms"], res["questions"]
    found = sum(1 for g in gold["key_terms"] if any(term_match(t["term"], g) for t in terms))
    body = norm(" ".join([res["summary"]] + [t["definition"] for t in terms]))
    cov = sum(1 for grp in gold["must_cover"] if any(has(body, k) for k in grp))
    halluc = sum(1 for t in terms if not has(notes_n, t["term"]))
    # v1's prompt never asks for evidence, so groundedness is unmeasurable there (reported as n/a, not as a failure)
    checkable = res["version"] != "v1"
    ungrounded = sum(1 for q in qs if q["grounded"] is not True) if checkable else 0
    supported = 0
    for q in qs:
        words = [w for w in norm(q["answer"]).split() if len(w) > 3]
        if q["answer"].strip().lower() in ("true", "false") or (words and sum(w in notes_n for w in words) / len(words) >= 0.6):
            supported += 1
    pack_text = norm(" ".join([res["summary"]] + [t["term"] + " " + t["definition"] for t in terms] +
                              [q["question"] + " " + q["answer"] + " " + " ".join(q["options"] or []) for q in qs]))
    leaked = sum(1 for o in gold["out_of_scope"] if has(pack_text, o))
    types = {q["type"] for q in qs}
    ok = (len(qs) == N_Q and len(res["summary"].split()) <= MAX_W and len(types) >= 3 and "mcq" in types)
    return {"terms_found": found, "terms_gold": len(gold["key_terms"]), "cov": cov, "cov_gold": len(gold["must_cover"]),
            "n_terms": len(terms), "halluc": halluc, "n_q": len(qs), "n_q_checkable": len(qs) if checkable else 0, "ungrounded": ungrounded, "supported": supported,
            "leaked": leaked, "constraints_ok": int(ok), "json_fail": int(bool(res["errors"]) and not qs and not terms)}


def aggregate(rows):
    s = {k: sum(r[k] for r in rows) for k in rows[0]}
    d = lambda a, b: round(a / b, 3) if b else 0.0
    return {"term_recall": d(s["terms_found"], s["terms_gold"]), "coverage": d(s["cov"], s["cov_gold"]),
            "term_halluc": d(s["halluc"], s["n_terms"]), "ungrounded_q": d(s["ungrounded"], s["n_q_checkable"]) if s["n_q_checkable"] else "n/a",
            "answer_support": d(s["supported"], s["n_q"]), "outside_know": s["leaked"],
            "constraints": d(s["constraints_ok"], len(rows)), "json_fail": s["json_fail"]}


COLS = ["term_recall", "coverage", "term_halluc", "ungrounded_q", "answer_support", "outside_know", "constraints", "json_fail"]


def table(summaries):
    out = ["| Version | " + " | ".join(COLS) + " |", "|---|" + "---|" * len(COLS)]
    for s in summaries:
        out.append(f"| {s['version']} | " + " | ".join(str(s["metrics"][c]) for c in COLS) + " |")
    return "\n".join(out)


LONG_WORDS = 500   # notes with at least this many words form the "long" group


def is_long(case):
    return len(case["notes"].split()) >= LONG_WORDS


def evaluate(version, cases, llm, runs=1):
    metrics_runs, detail = [], []
    for k in range(runs):
        rows = []
        for c in cases:
            res = run(c["notes"], version, llm, N_Q, MAX_W)
            row = score(res, c)
            rows.append(row)
            detail.append({"run": k, "case": c["id"], "score": row, "result": res})
        metrics_runs.append(aggregate(rows))
    first = [d for d in detail if d["run"] == 0]
    groups = {}
    for name, flag in (("short", False), ("long", True)):
        rows = [d["score"] for d, c in zip(first, cases) if is_long(c) == flag]
        if rows:
            groups[name] = {"n_notes": len(rows), "metrics": aggregate(rows)}
    return {"version": version, "runs": runs, "metrics": metrics_runs[0], "groups": groups,
            "metrics_per_run": metrics_runs, "detail": detail}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--versions", nargs="+", default=["v0"], choices=VERSIONS)
    ap.add_argument("--data", default=str(ROOT / "test-data"))
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--model", default=None)
    ap.add_argument("--replay-dir", default=str(ROOT / "test-data" / "replay_simulated_oct28"))
    ap.add_argument("--out", default=str(ROOT / "test-data" / "results"), help="folder for the result JSON files")
    ap.add_argument("--no-save", action="store_true", help="print the tables but do not write result files")
    ap.add_argument("--provider", choices=["anthropic", "gemini", "ollama", "replay"], default="anthropic")
    a = ap.parse_args(argv)
    cases = load_cases(Path(a.data))
    llm = None
    if any(v != "v0" for v in a.versions):
        from .llm import make_llm
        try:
            if a.provider == "replay":
                from .replay import ReplayLLM
                llm = ReplayLLM(a.replay_dir, a.model or "replayed")
            else:
                llm = make_llm(a.provider, a.model)
        except LLMError as e:
            sys.exit(f"{e}. Use --provider ollama (no key), --versions v0 (offline), or export ANTHROPIC_API_KEY.")
    Path(a.out).mkdir(parents=True, exist_ok=True)
    stamp, summaries = time.strftime("%Y%m%d-%H%M%S"), []
    for v in a.versions:
        try:
            s = evaluate(v, cases, llm, a.runs)
        except Missing:
            sys.exit("A reply is missing for some prompt: run `python3 -m smartstudy.collect` and answer the pending prompts first.")
        except LLMError as e:
            sys.exit(f"LLM error: {e}")
        s["model"] = getattr(llm, "model", None) if v != "v0" else None
        summaries.append(s)
        if not a.no_save:
            (Path(a.out) / f"{v}_{stamp}.json").write_text(json.dumps(s, indent=1))
    print(f"Test set: {len(cases)} lecture notes; {N_Q} questions and <= {MAX_W} words requested per run")
    print("ALL notes")
    print(table(summaries))
    for g in ("short", "long"):
        sub = [dict(s, metrics=s["groups"][g]["metrics"]) for s in summaries if g in s["groups"]]
        if sub and len(sub) == len(summaries) and len(sub[0]["groups"]) > 1:
            n = summaries[0]["groups"][g]["n_notes"]
            print(f"\n{g.upper()} notes only ({n} notes; long = at least {LONG_WORDS} words)")
            print(table(sub))
    if llm:
        print(f"LLM calls: {llm.calls}, tokens in/out: {llm.input_tokens}/{llm.output_tokens}")


if __name__ == "__main__":
    main()
