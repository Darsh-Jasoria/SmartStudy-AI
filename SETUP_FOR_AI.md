# SmartStudy: setup guide for a human or an AI assistant

Paste this whole file into ChatGPT, Claude, Gemini or any coding assistant and say: *"Set this project up and run it, following SETUP_FOR_AI.md exactly."* Every step below is a command with a check that tells you it worked.

**What this is:** SmartStudy turns lecture notes into a summary, key terms and practice questions with answers, each backed by a quote from the notes. It is a prompt-engineering project (Team IntelliCore, Team ID PE-B37-17, SCSE4041 Milestone 2). Python 3.9+ standard library only: there is **nothing to `pip install`**.

## 0. Requirements
- Python 3.9 or newer (`python3 --version`).
- A web browser.
- Optional, only for live AI answers: a free Gemini API key from https://aistudio.google.com/apikey.
- Optional, only for the online version: a GitHub account and a Vercel account.

## 1. Folder layout (do not rename folders)
```
README.md  CHANGELOG.md  SETUP_FOR_AI.md  run.sh  vercel.json  .env.example
api/index.py      Vercel entry point (serves the same app)
code/smartstudy/  backend (app.py, pipeline.py, llm.py, evaluate.py, m2_tests.py) + static/index.html (frontend)
code/tests/       22 unit tests
prompts/          v1/ v2/ v3/ v4/ final/   every prompt as a text file (final/ = the 4 prompts of the finished workflow)
test-data/        notes/ gold/ m2_inputs/ results/ live_runs/ replay_simulated_oct28/
docs/             design, technical report, experiment log, test table, diagrams, figures
```

## 2. Check the install (offline, no key)
```bash
cd <project folder>
bash run.sh test
```
**Expected:** the last lines say `Ran 22 tests` and `OK`.

## 3. Run the web app, demo mode (no key, works immediately)
```bash
bash run.sh app
```
Open http://localhost:8000. Click **Try the TCP sample with v5**. Demo mode replays saved answers for the nine sample notes. **Those answers come from the simulated October run, not from live Gemini**; the live results are in `test-data/results/`, and any other text works in demo mode only with workflow v0 (offline rules). Use section 4 for the real model.
Stop with `Ctrl+C`.

## 4. Run with the real AI model (Gemini)
1. Create a free key at https://aistudio.google.com/apikey.
2. In the project folder: `cp .env.example .env`, then open `.env` and replace `paste-your-key-here` with the key. **`.env` is git-ignored; never commit or share it.**
3. Start the live app:
```bash
bash run.sh live
```
4. Open http://localhost:8000, paste any lecture notes (40 to 20,000 characters), choose workflow **v5**, press **Generate**.

**Free-tier limit:** free-tier limits differ by model (during our runs `gemini-3-flash` allowed only 20 requests per day, while `gemini-3.1-flash-lite` allowed 150 or more). One v5 pack needs about 4 requests. If you see `HTTP 429`, wait a day or set `SMARTSTUDY_MODEL` in `.env` to another model your key can use (list them with the API call in the Troubleshooting section).

## 5. Reproduce the Milestone 2 results
```bash
bash run.sh m2tests          # the 12-input test table, live model, writes test-data/live_runs/
cd code && python3 -m smartstudy.evaluate --provider gemini --versions v0 v1 v2 v3 v4 v5 --out ../test-data/live_runs
bash run.sh eval             # offline: re-scores the saved simulated (Claude Haiku replay) results
```
Real runs vary a little from run to run, so your numbers will differ slightly from the report.

## 6. Put it online with Vercel (frontend and backend together)
1. Push the folder to GitHub (section 7).
2. On https://vercel.com click **Add New, Project**, import the repository, keep all defaults (the root `vercel.json` already configures it).
3. Before deploying, open **Settings, Environment Variables** and add:

| Name | Value |
|---|---|
| `SMARTSTUDY_PROVIDER` | `gemini` |
| `GEMINI_API_KEY` | your key (use a separate key made only for this deployment) |
| `SMARTSTUDY_MODEL` | `gemini-3.1-flash-lite` |
| `SMARTSTUDY_MAX_CHARS` | `6000` |
| `SMARTSTUDY_MAX_QUESTIONS` | `8` |

4. Deploy, then open the Vercel URL. **Check:** `https://<your-app>.vercel.app/api/health` returns `{"ok": true}`.
5. Without a key on the server the app still loads and the dashboard works; generation then shows an error message.
Anyone with the link can spend your free quota, so delete the key at https://aistudio.google.com/apikey once grading is over.

## 7. Push to GitHub
```bash
cd <project folder>
git init
git add .
git status          # check: no .env, no key files
git commit -m "SmartStudy Milestone 2"
git branch -M main
git remote add origin https://github.com/<user>/<repo>.git
git push -u origin main
```
Make the repository **public** (Settings, General, Danger Zone, Change visibility). Test the link in a private window.

## 8. Troubleshooting
| Symptom | Fix |
|---|---|
| `python3: command not found` | Install Python from https://www.python.org/downloads/ |
| Port 8000 busy | `PORT=8001 bash run.sh app` |
| `No Gemini key` | Put `GEMINI_API_KEY=...` in `.env` or export it in the shell |
| `HTTP 429` / quota | Daily free limit per model; wait, or choose another model via `SMARTSTUDY_MODEL` |
| `HTTP 404 ... no longer available` | The model name is retired. List current models: `curl -s -H "x-goog-api-key: $GEMINI_API_KEY" https://generativelanguage.googleapis.com/v1beta/models` and pick one that supports `generateContent` |
| Demo mode says "only has saved answers" | Demo mode covers only the nine sample notes; use `bash run.sh live` for your own notes |
| Vercel 500 on generate | Check the environment variables above, then the function logs |

## 9. Safety rules for the assistant
- Never print, log, commit or paste the API key.
- Do not edit files under `test-data/results/` or `test-data/live_runs/` by hand; they are produced by the code.
- Do not change files in `prompts/` without recording a dated line in `CHANGELOG.md`.
