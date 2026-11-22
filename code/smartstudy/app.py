"""SmartStudy web app and dashboard (standard library only).

    python3 -m smartstudy.app                              offline: workflow v0 only, any notes
    SMARTSTUDY_PROVIDER=replay python3 -m smartstudy.app   demo: saved real v0-v5 answers, no key
    ANTHROPIC_API_KEY=... python3 -m smartstudy.app        live: v1-v5 with your own key
    SMARTSTUDY_PROVIDER=ollama python3 -m smartstudy.app   live: free local model

Then open http://localhost:8000 (PORT=... changes the port). The server binds to 127.0.0.1 only and
stores nothing.
"""
from __future__ import annotations
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from . import __version__
from .pipeline import VERSIONS, run, to_markdown
from .replay import Missing

ROOT = Path(__file__).resolve().parent.parent.parent   # repository root
STATIC = Path(__file__).resolve().parent / "static" / "index.html"
SAMPLES = sorted((ROOT / "test-data" / "notes").glob("*.txt"))
LONG_WORDS = 500                     # same threshold as evaluate.py
# whitelist of project documents the dashboard may show (no arbitrary file access)
DOCS = {
    "experiment_log": "docs/experiment_log.md", "test_table": "docs/test_table.md",
    "technical_report": "docs/IntelliCore_TechnicalReport.md", "design": "docs/01_design_and_diagrams.md",
    "reel_script": "docs/reel_script.md", "setup": "SETUP_FOR_AI.md",
    "changelog": "CHANGELOG.md", "readme": "README.md",
}
NOTES_MIN = 40
NOTES_MAX = int(os.environ.get("SMARTSTUDY_MAX_CHARS", 20000))   # accepted notes length; lower it on a public deployment
MAX_QUESTIONS = int(os.environ.get("SMARTSTUDY_MAX_QUESTIONS", 15))
_llm = None


def get_llm():
    global _llm
    if _llm is None:
        provider = os.environ.get("SMARTSTUDY_PROVIDER", "anthropic")
        if provider == "replay":   # demo mode: serves the saved results for the sample notes (no key needed)
            from .replay import ReplayLLM
            _llm = ReplayLLM(ROOT / "test-data" / "replay_simulated_oct28", "replay")
        else:
            from .llm import make_llm
            _llm = make_llm(provider)
    return _llm


def _latest_files() -> dict:
    out = {}
    for v in VERSIONS:
        files = sorted((ROOT / "test-data" / "results").glob(f"{v}_*.json"))
        if files:
            out[v] = files[-1]
    return out


def latest_results() -> dict:
    """Latest saved evaluation per version (metrics, short/long groups) for the dashboard."""
    out = {}
    for v, f in _latest_files().items():
        d = json.loads(f.read_text())
        out[v] = {"metrics": d["metrics"], "groups": d.get("groups", {}), "model": d.get("model"),
                  "file": f.name, "runs": d.get("runs", 1)}
    return out


def results_matrix() -> dict:
    """Per-note scores for every version (first run), for the heat-map and the per-note tables."""
    out = {}
    for v, f in _latest_files().items():
        rows = []
        for x in json.loads(f.read_text())["detail"]:
            if x.get("run", 0) != 0:
                continue
            s, r = x["score"], x["result"]
            rows.append({"case": x["case"], "terms_found": s["terms_found"], "terms_gold": s["terms_gold"],
                         "cov": s["cov"], "cov_gold": s["cov_gold"], "n_terms": s["n_terms"], "halluc": s["halluc"],
                         "n_q": s["n_q"], "ungrounded": s["ungrounded"], "leaked": s["leaked"],
                         "constraints_ok": s["constraints_ok"], "summary_words": len(r["summary"].split()),
                         "q_types": len({q["type"] for q in r["questions"]}), "warnings": len(r["warnings"]),
                         "dropped": len(r["trace"].get("dropped", []))})
        out[v] = rows
    return out


def testset() -> list:
    out = []
    for p in SAMPLES:
        gold = json.loads((ROOT / "test-data" / "gold" / f"{p.stem}.json").read_text())
        words = len(p.read_text().split())
        out.append({"id": p.stem, "words": words, "group": "long" if words >= LONG_WORDS else "short",
                    "gold_terms": gold["key_terms"], "must_cover": gold["must_cover"],
                    "out_of_scope": gold["out_of_scope"]})
    return out


def prompts() -> dict:
    files = sorted((ROOT / "prompts").glob("*/*.txt"))
    return {"files": [{"name": f"{f.parent.name}/{f.name}", "text": f.read_text()} for f in files],
            "changelog": (ROOT / "CHANGELOG.md").read_text()}


def _clamp(value, lo, hi, default):
    try:
        return max(lo, min(hi, int(value)))
    except (TypeError, ValueError):
        return default


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body, ctype: str = "application/json"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _json(self, code: int, obj):
        self._send(code, json.dumps(obj))

    def do_GET(self):
        url = urlparse(self.path)
        route = url.path
        try:
            if route == "/":
                self._send(200, STATIC.read_bytes(), "text/html")
            elif route == "/api/samples":
                self._json(200, [{"name": p.stem, "text": p.read_text()} for p in SAMPLES])
            elif route == "/api/results":
                self._json(200, latest_results())
            elif route == "/api/matrix":
                self._json(200, results_matrix())
            elif route == "/api/testset":
                self._json(200, testset())
            elif route == "/api/prompts":
                self._json(200, prompts())
            elif route == "/api/doc":
                name = (parse_qs(url.query).get("name") or [""])[0]
                if name not in DOCS:
                    return self._json(404, {"error": "unknown document"})
                self._json(200, {"name": name, "path": DOCS[name], "text": (ROOT / DOCS[name]).read_text()})
            elif route == "/api/status":
                provider = os.environ.get("SMARTSTUDY_PROVIDER", "anthropic")
                self._json(200, {"versions": VERSIONS, "app_version": __version__, "provider": provider,
                                 "llm_available": bool(os.environ.get("ANTHROPIC_API_KEY")) or provider in ("ollama", "replay") or (provider == "gemini" and bool(__import__("smartstudy.llm", fromlist=["x"]).gemini_key()))})
            elif route == "/api/health":
                self._json(200, {"ok": True})
            else:
                self._json(404, {"error": "not found"})
        except FileNotFoundError as e:
            self._json(404, {"error": f"missing file: {e.filename}"})

    def do_POST(self):
        if urlparse(self.path).path != "/api/generate":
            return self._json(404, {"error": "not found"})
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0)) or 0))
            notes = str(req["notes"]).strip()
        except (ValueError, KeyError, TypeError):
            return self._json(400, {"error": "Send JSON with a 'notes' field."})
        version = str(req.get("version", "v5"))
        if version not in VERSIONS:
            return self._json(400, {"error": f"Unknown workflow '{version}'. Use one of {', '.join(VERSIONS)}."})
        if not NOTES_MIN <= len(notes) <= NOTES_MAX:
            return self._json(400, {"error": f"Notes must be between {NOTES_MIN} and {NOTES_MAX:,} characters."})
        try:
            res = run(notes, version, None if version == "v0" else get_llm(),
                      _clamp(req.get("n_questions"), 1, MAX_QUESTIONS, 5), _clamp(req.get("max_words"), 30, 300, 100),
                      str(req.get("subject", ""))[:80], str(req.get("difficulty", "")))
            res["markdown"] = to_markdown(res)
            self._json(200, res)
        except Missing:
            self._json(409, {"error": "Demo (replay) mode only has saved answers for the nine sample notes with 5 questions, "
                                      "100 words and no subject or difficulty. Pick a sample, use v0, or run with an API or Ollama model."})
        except Exception as e:  # shown in the UI as a message, never as a stack trace
            self._json(500, {"error": str(e)})

    def log_message(self, *args):
        pass


def main():
    port = int(os.environ.get("PORT", 8000))
    print(f"SmartStudy running at http://localhost:{port}  (Ctrl+C to stop)")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
