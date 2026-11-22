# Changelog since Milestone 1

Team IntelliCore · Team ID PE-B37-17 · SmartStudy (Problem Pool C2). Dates are real file or run dates.

## 2026-11-22 · Milestone 2 submission build
- Reorganised the repository to the required layout: `prompts/v1..v4, final/`, `code/`, `test-data/`, `docs/`.
- `final/P1..P4` are the four prompts of the finished workflow (outline, generate, moderator, shorten). They are identical in text to the v4 and v5 prompts used in the October experiments.
- Added a Gemini provider (`code/smartstudy/llm.py`) so the workflows run on a real hosted model. Default: `gemini-3.1-flash-lite`.
- **First real runs.** Ran the 12-input Milestone 2 test table (`code/smartstudy/m2_tests.py`) and scored workflows v0 to v5 on the nine notes with the live model. Outputs: `test-data/live_runs/`.
- Test table result: 10 of 12 pass. Two honest failures: test 7 (3-sentence note) and test 11 (casual chat) both produced 5 questions with no warning, i.e. the workflow padded instead of refusing. Logged in `docs/experiment_log.md`.
- Added edge and invalid inputs in `test-data/m2_inputs/` (thin note, Hinglish, prompt injection, missing slide, chat text, 5-character input).
- Added Vercel deployment (`api/index.py`, `vercel.json`), `.env` loading, input limits for a public deployment, `run.sh`, `.env.example`, and `SETUP_FOR_AI.md`.
- Added Team Member 4 (Arnav Singh) to all team documents. Removed enrollment numbers from the public web page.

## 2026-10-28 · Prototype and experiments (before the live runs)
- Wrote prompt versions v1 to v5 and the pipeline: zero-shot (v1), role + schema + evidence quotes (v2), few-shot with a negative example (v3), outline → generate → quote guard → moderator chain (v4), and a summary length guard (v5).
- Wrote nine original lecture notes (six short, three long) with gold key terms, must-cover ideas and out-of-scope terms.
- Wrote the evaluation harness (eight metrics), 22 unit tests, the web app (flashcards, quiz, compare, plan) and the evaluation dashboard.
- Those LLM answers were **simulated**: Claude Haiku answered the saved prompts through Claude Code helper agents because no API key existed. They are kept in `test-data/replay_simulated_oct28/` and are not used for any Milestone 2 claim.

## Milestone 1 baseline
- Baseline prompt: read the notes and produce a concise summary, five key terms with definitions, five practice questions and an answer key, using only the supplied notes (see `prompts/v1/` for the zero-shot form used in experiments).
