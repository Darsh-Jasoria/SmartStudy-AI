"""Prompt workflows v0-v5 for lecture notes -> study pack. All return one normalised dict.

v0 rules (no LLM) | v1 zero-shot | v2 structured | v3 few-shot | v4 chain (outline, generate, quote guard,
moderator) | v5 = v4 + summary length guard. The prompt files live in ../prompts."""
from __future__ import annotations
import json
import re
from pathlib import Path

from . import baseline
from .llm import LLM

PROMPTS = Path(__file__).resolve().parent.parent.parent / "prompts"
VERSIONS = ("v0", "v1", "v2", "v3", "v4", "v5")


# Prompt files live in prompts/<version>/. The v5 (final) workflow reads prompts/final/P1..P4.
FINAL = {"v4_outline_system.txt": "P1_outline_system.txt", "v4_outline_user.txt": "P1_outline_user.txt",
         "v4_system.txt": "P2_generate_system.txt", "v4_user.txt": "P2_generate_user.txt",
         "v4_verify_system.txt": "P3_moderator_system.txt", "v4_verify_user.txt": "P3_moderator_user.txt",
         "v5_shorten_system.txt": "P4_shorten_system.txt", "v5_shorten_user.txt": "P4_shorten_user.txt"}


OLDER = {"v1": ("v1", "v1_prompt"), "v2": ("v2", "v2_prompt"), "v3": ("v3", "v3_prompt"), "v4": ("v4", "v4_generate"),
         "v4_outline": ("v4", "v4_outline"), "v4_verify": ("v4", "v4_moderator")}
SYS_MARK, USR_MARK = "===== SYSTEM PROMPT =====\n", "\n===== USER PROMPT TEMPLATE =====\n"


def load_prompt(name: str, final: bool = False) -> str:
    """v1-v4 prompts are separate files in prompts/<version>/. The final workflow keeps one file per prompt
    (prompts/final/P1..P4.txt) with a SYSTEM and a USER section."""
    if final:
        stem, part = FINAL[name].rsplit("_", 1)             # e.g. ("P1_outline", "system.txt")
        system, user = (PROMPTS / "final" / f"{stem}.txt").read_text().split(SYS_MARK, 1)[1].split(USR_MARK, 1)
        return system if part == "system.txt" else user
    folder, stem = OLDER[name.rsplit("_", 1)[0]]
    system, user = (PROMPTS / folder / f"{stem}.txt").read_text().split(SYS_MARK, 1)[1].split(USR_MARK, 1)
    return system if name.endswith("_system.txt") else user


def fill(template: str, **kw) -> str:
    """Placeholder substitution that is safe for prompts containing literal JSON braces."""
    for k, v in kw.items():
        template = template.replace("{" + k + "}", str(v))
    return template


def parse_json(text: str):
    t = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    a, b = t.find("{"), t.rfind("}")
    if a == -1 or b == -1:
        return None, "no JSON object found"
    try:
        return json.loads(t[a:b + 1]), None
    except json.JSONDecodeError as e:
        return None, f"invalid JSON: {e}"


def norm(s) -> str:
    s = str(s or "").lower().replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"[^a-z0-9']+", " ", s).strip()


def is_grounded(evidence, notes: str) -> bool:
    return bool(evidence) and norm(evidence) in norm(notes)


def _finish(obj, notes, version, trace, errors):
    obj = obj if isinstance(obj, dict) else {}
    terms, qs = [], []
    for t in obj.get("key_terms", []) or []:
        if isinstance(t, dict) and t.get("term"):
            ev = str(t.get("evidence") or "")
            terms.append({"term": str(t["term"]).strip(), "definition": str(t.get("definition", "")).strip(),
                          "evidence": ev, "grounded": is_grounded(ev, notes) if ev else None})
    for q in obj.get("questions", []) or []:
        if isinstance(q, dict) and q.get("question"):
            ev = str(q.get("evidence") or "")
            opts = q.get("options") if isinstance(q.get("options"), list) else None
            qs.append({"type": str(q.get("type") or "short").lower(), "question": str(q["question"]).strip(),
                       "options": opts, "answer": str(q.get("answer", "")).strip(), "evidence": ev,
                       "grounded": is_grounded(ev, notes) if ev else None})
    return {"version": version, "summary": str(obj.get("summary", "") or "").strip(), "key_terms": terms,
            "questions": qs, "warnings": obj.get("warnings", []) or [], "trace": trace, "errors": errors}


DIFFICULTY = {"easy": "easy (recall of definitions and facts)",
              "medium": "medium (understanding and explanation)",
              "hard": "hard (application and multi-step reasoning, still answerable from the notes)"}


def context_line(subject: str = "", difficulty: str = "") -> str:
    """Optional Subject / Difficulty lines prepended to the user message. Empty when neither is given,
    so default runs send exactly the same prompt as before (saved replay answers stay valid)."""
    lines = []
    if subject and subject.strip():
        lines.append(f"Subject: {subject.strip()[:80]}")
    d = (difficulty or "").strip().lower()
    if d in DIFFICULTY:
        lines.append(f"Difficulty level: {DIFFICULTY[d]}")
    return ("\n".join(lines) + "\n\n") if lines else ""


def _topics_outline(parsed) -> str:
    topics = parsed.get("topics", []) if isinstance(parsed, dict) else []
    return "\n".join(f"- {t.get('title')}: " + "; ".join(map(str, t.get("main_points", [])))
                     for t in topics if isinstance(t, dict))


def _quote_guard(obj: dict, notes: str, dropped: list) -> list:
    """Stage 3 (code): keep only terms and questions whose evidence quote exists in the notes."""
    terms = []
    for t in obj.get("key_terms", []) or []:
        if isinstance(t, dict) and is_grounded(t.get("evidence"), notes):
            terms.append(t)
        else:
            dropped.append({"term": t.get("term") if isinstance(t, dict) else None,
                            "reason": "evidence quote not in notes"})
    obj["key_terms"] = terms
    kept = []
    for q in obj.get("questions", []) or []:
        if isinstance(q, dict) and is_grounded(q.get("evidence"), notes):
            kept.append(q)
        else:
            dropped.append({"question": q.get("question") if isinstance(q, dict) else None,
                            "reason": "evidence quote not in notes"})
    return kept


def _moderate(cands: list, notes: str, llm: LLM, trace: dict, errors: list, dropped: list, final: bool = False) -> list:
    """Stage 4 (LLM): an independent reviewer answers each question from the notes only."""
    listing = json.dumps([{"id": i, "type": q.get("type"), "question": q.get("question"),
                           "options": q.get("options"), "proposed_answer": q.get("answer")}
                          for i, q in enumerate(cands)], indent=1)
    raw = llm.complete(load_prompt("v4_verify_system.txt", final),
                       fill(load_prompt("v4_verify_user.txt", final), notes=notes, candidates=listing), max_tokens=3000)
    parsed, err = parse_json(raw)
    trace["stages"].append("llm moderator"); trace["raw_verify"] = raw
    reviews = parsed.get("reviews") if isinstance(parsed, dict) else None
    if err or not isinstance(reviews, list):
        errors.append(f"verify: {err or 'no reviews list'} (candidates kept unverified)")
        return cands
    by_id = {r.get("id"): r for r in reviews if isinstance(r, dict)}
    final = []
    for i, q in enumerate(cands):
        r = by_id.get(i)
        if r is None or r.get("valid") is True:
            if r and r.get("answer"):
                q = {**q, "answer": r["answer"]}
            final.append(q)
        else:
            dropped.append({"question": q.get("question"), "reason": f"moderator: {r.get('reason', '')}"})
    return final


def _length_guard(obj: dict, max_words: int, llm: LLM, trace: dict, errors: list, final: bool = False) -> None:
    """Stage 6 (v5): count summary words in code; if over the limit, ask for one shortened version."""
    summary = str(obj.get("summary", "") or "")
    n = len(summary.split())
    trace["summary_words_before"] = n
    if n <= max_words:
        trace["stages"].append("length guard: ok")
        return
    raw = llm.complete(load_prompt("v5_shorten_system.txt", final),
                       fill(load_prompt("v5_shorten_user.txt", final), max_words=max_words, current_words=n, summary=summary))
    parsed, err = parse_json(raw)
    trace["stages"].append("length guard: shorten"); trace["raw_shorten"] = raw
    new = str(parsed.get("summary", "")) if isinstance(parsed, dict) else ""
    if err or not new.strip():
        errors.append(f"shorten: {err or 'empty summary'} (kept original)")
    else:
        obj["summary"] = new
    if len(str(obj["summary"]).split()) > max_words:
        obj.setdefault("warnings", []).append(f"summary still over {max_words} words after one retry")


def run(notes: str, version: str, llm: LLM | None = None, n_questions: int = 5, max_words: int = 100,
        subject: str = "", difficulty: str = "") -> dict:
    """Run one workflow (v0-v5) on the notes and return the normalised study pack."""
    if version not in VERSIONS:
        raise ValueError(f"unknown version {version}")
    trace, errors = {"stages": []}, []
    if version == "v0":
        trace["stages"].append("extractive rules")
        return _finish(baseline.extract(notes, n_questions, max_words), notes, version, trace, errors)
    if llm is None:
        raise ValueError("an LLM client is required for v1-v5")
    vars_ = dict(notes=notes, n_questions=n_questions, max_words=max_words, outline="")

    chain = version in ("v4", "v5")      # v5 = v4 + summary length guard
    final = version == "v5"              # v5 is the final workflow: prompts/final/P1-P4
    base = "v4" if chain else version     # v5 reuses the v4 prompts for stages 1-4
    if chain:                             # stage 1 (LLM): topic outline
        raw = llm.complete(load_prompt("v4_outline_system.txt", final), fill(load_prompt("v4_outline_user.txt", final), **vars_))
        parsed, err = parse_json(raw)
        trace["stages"].append("llm outline"); trace["raw_outline"] = raw
        if err:
            errors.append(f"outline: {err} (continuing without outline)")
        vars_["outline"] = "(unavailable)" if err else _topics_outline(parsed)
        vars_["n_questions"] = n_questions + 2          # over-generate, then filter

    system = fill(load_prompt(f"{base}_system.txt", final), **vars_)
    user = context_line(subject, difficulty) + fill(load_prompt(f"{base}_user.txt", final), **vars_)
    raw = llm.complete(system, user, max_tokens=4000)   # stage 2 (LLM): generate
    obj, err = parse_json(raw)
    trace["stages"].append("llm generate"); trace["raw_generate"] = raw
    if err or not isinstance(obj, dict):
        errors.append(f"generate: {err or 'top-level JSON is not an object'}")
        return _finish({}, notes, version, trace, errors)

    if chain:
        dropped: list = []
        cands = _quote_guard(obj, notes, dropped)
        trace["stages"].append("grounding guard")
        if cands:
            cands = _moderate(cands, notes, llm, trace, errors, dropped, final)
        obj["questions"] = cands[:n_questions]          # stage 5: keep first N, never pad
        trace["dropped"] = dropped
        if len(obj["questions"]) < n_questions:
            obj.setdefault("warnings", []).append(f"only {len(obj['questions'])} of {n_questions} questions passed review")
    if version == "v5":
        _length_guard(obj, max_words, llm, trace, errors, final)
    return _finish(obj, notes, version, trace, errors)


def to_markdown(r: dict) -> str:
    out = ["# Study pack", "", "## Summary", r["summary"] or "(none)", "", "## Key terms"]
    out += [f"- **{t['term']}**: {t['definition']}" for t in r["key_terms"]] or ["- (none)"]
    out += ["", "## Practice questions"]
    for i, q in enumerate(r["questions"], 1):
        out.append(f"{i}. [{q['type']}] {q['question']}")
        for j, o in enumerate(q["options"] or []):
            out.append(f"   - {'ABCD'[j] if j < 4 else j+1}. {o}")
    out += ["", "## Answer key"]
    out += [f"{i}. {q['answer']}  _(source: \"{q['evidence']}\")_" for i, q in enumerate(r["questions"], 1)]
    for w in r["warnings"]:
        out.append(f"\n> Warning: {w}")
    out.append("\n_AI-generated from your notes - check against the lecture before relying on it._")
    return "\n".join(out)
