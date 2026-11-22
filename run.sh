#!/bin/bash
# SmartStudy launcher (macOS / Linux).   bash run.sh [app|live|test|eval|m2tests|help]
#   app      web app in DEMO mode (default, no key): replays saved answers for the 9 sample notes.
#            These saved answers are the SIMULATED October run, not live Gemini output.
#   live     web app with the real Gemini model (needs GEMINI_API_KEY in .env or the environment)
#   test     run the unit tests
#   eval     re-score the saved simulated results (offline)
#   m2tests  run the 12-input Milestone 2 test table with the live model (needs a key)
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/code" || exit 1
PY=$(command -v python3) || { echo "Python 3.9+ not found. Install it from https://www.python.org/downloads/"; exit 1; }
PORT=${PORT:-8000}
case "${1:-app}" in
  app)     echo "DEMO MODE: replaying saved (simulated, October) answers for the 9 sample notes. Use 'bash run.sh live' for the real model."
           SMARTSTUDY_PROVIDER=replay PORT=$PORT "$PY" -m smartstudy.app;;
  live)    SMARTSTUDY_PROVIDER=${SMARTSTUDY_PROVIDER:-gemini} PORT=$PORT "$PY" -m smartstudy.app;;
  test)    exec "$PY" -m unittest tests.test_smartstudy;;
  eval)    exec "$PY" -m smartstudy.evaluate --provider replay --versions v0 v1 v2 v3 v4 v5 --no-save;;
  m2tests) exec "$PY" -m smartstudy.m2_tests --provider gemini;;
  *)       sed -n '2,8p' "$0";;
esac
