# Technical report: SmartStudy: AI-Powered Lecture Notes to Study Pack Generator
**Team IntelliCore (PE-B37-17), batch B37-48, faculty Pawan Kumar.** Problem Pool C2.

## Problem
Students need summaries and practice questions from long lecture notes, but chatbots add facts that are not in the notes and break format limits. We study how prompt design controls this, using a real model and a gold-labelled test set.

## Architecture
A Python 3 standard-library backend (`pipeline.py`, `llm.py`, `app.py`, `evaluate.py`) and a single-page frontend. The same code runs locally and on Vercel (`api/index.py`). The final workflow v5 has four prompts and two code checks: P1 outline (LLM), P2 generate summary, key terms and N+2 questions each with a verbatim quote (LLM), quote guard (code), P3 moderator answers every question from the notes only (LLM), keep first N (code), word count and P4 shorten if needed (code + LLM).

## Tools and models
Gemini 3.1 Flash-Lite (gemini-3.1-flash-lite) via the Gemini API; temperature 0.0, thinking level minimal. Python 3.9+, no third-party packages. Earlier simulated runs (Claude Haiku via helper agents) are kept separately and not used here.

## Prompt design
Techniques: role and constraints, strict JSON schema, one few-shot example with a negative case, source-grounding by quote with a code check, prompt chaining, over-generate and filter (N+2), an escape hatch (`warnings`), and a deterministic length check. Five saved versions: v1 zero-shot, v2 role + schema + quotes, v3 + example, v4 chain, v5 + length guard.

## Test results
Nine notes, eight metrics (live run, one run per version): constraints met v1 0.0 to v2 1.0; flagged terms v1 0.091 to v2 0.0; answer support 0.725 to 0.956; coverage v3 0.568 to v4 0.676; term recall best v1 0.358, v5 0.254. The chain gave more coverage but needs 3x the calls. The 13-input test table passes 11 of 13; failures: test 8, test 12.

## Limitations
The model pads thin or non-lecture input to 5 questions instead of warning (tests 8 and 12); key-term recall is low (3 to 6 terms per note against 10 to 15); metrics are automatic proxies with no human scoring yet; one run, one model, nine computer-science notes, free-tier request limits that restrict repeated runs.
