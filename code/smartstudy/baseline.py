"""v0: extractive, rule-based baseline (no LLM). A non-AI floor for the experiments."""
from __future__ import annotations
import re
from collections import Counter

STOP = set("the a an to of and for on in at by with is are be will it that this as or from its their can than then each which when if but not no so such into also one use used".split())


def sentences(notes: str):
    out = []
    for ln in notes.splitlines():
        ln = ln.strip().lstrip("-*• ").strip()
        if not ln or ln.lower().startswith("lecture"):
            continue
        out.extend(s.strip() for s in re.split(r"(?<=[.!?])\s+", ln) if len(s.split()) >= 4)
    return out


def extract(notes: str, n_questions: int = 5, max_words: int = 100) -> dict:
    sents = sentences(notes)
    freq = Counter(w for s in sents for w in re.findall(r"[a-z][a-z\-]+", s.lower()) if w not in STOP and len(w) > 3)
    ranked = sorted(sents, key=lambda s: -sum(freq[w] for w in re.findall(r"[a-z][a-z\-]+", s.lower())) / (len(s.split()) ** 0.5))
    summary, words = [], 0
    for s in ranked:
        if words + len(s.split()) > max_words:
            continue
        summary.append(s); words += len(s.split())
    terms = []
    for s in sents:  # "X is/are ..." definitional sentences give a term + definition
        m = re.match(r"^([A-Z][\w\- ()']{2,40}?) (?:is|are|means|measures|gives|uses|computes|runs)\b", s)
        if m and len(terms) < 12:
            terms.append({"term": m.group(1).strip(), "definition": s, "evidence": s})
    questions = []
    for s in sents:  # cloze question: blank the rarest long word
        cands = [w for w in re.findall(r"[A-Za-z][A-Za-z\-]{5,}", s) if w.lower() not in STOP]
        if cands and len(questions) < n_questions:
            ans = min(cands, key=lambda w: freq[w.lower()])
            questions.append({"type": "short", "question": s.replace(ans, "_____", 1), "options": None,
                              "answer": ans, "evidence": s})
    return {"summary": " ".join(summary), "key_terms": terms, "questions": questions, "warnings": []}
