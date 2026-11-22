"""Minimal LLM client (stdlib only) so the project has no install step.

Provider: Anthropic Messages API. Set ANTHROPIC_API_KEY (and optionally
SMARTSTUDY_MODEL). `LLM` is a tiny interface so tests can inject a fake.
"""
from __future__ import annotations
import json
import os
import time
import urllib.error
import urllib.request

API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = os.environ.get("SMARTSTUDY_MODEL", "claude-haiku-5-5")


class LLMError(RuntimeError):
    pass


class LLM:
    def complete(self, system: str, user: str, max_tokens: int = 2000, temperature: float = 0.0) -> str:
        raise NotImplementedError


class AnthropicLLM(LLM):
    def __init__(self, model: str = DEFAULT_MODEL, api_key: str | None = None, retries: int = 3):
        self.model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.retries = retries
        self.calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        if not self.api_key:
            raise LLMError("ANTHROPIC_API_KEY is not set")

    def complete(self, system, user, max_tokens=2000, temperature=0.0):
        body = json.dumps({"model": self.model, "max_tokens": max_tokens, "temperature": temperature,
                           "system": system, "messages": [{"role": "user", "content": user}]}).encode()
        headers = {"content-type": "application/json", "x-api-key": self.api_key,
                   "anthropic-version": "2023-06-01"}
        last = None
        for attempt in range(self.retries):
            try:
                req = urllib.request.Request(API_URL, data=body, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=90) as r:
                    data = json.load(r)
                self.calls += 1
                usage = data.get("usage", {})
                self.input_tokens += usage.get("input_tokens", 0)
                self.output_tokens += usage.get("output_tokens", 0)
                return "".join(b.get("text", "") for b in data.get("content", []))
            except urllib.error.HTTPError as e:
                last = f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}"
                if e.code not in (429, 500, 502, 503, 529):
                    break
            except (urllib.error.URLError, TimeoutError) as e:
                last = str(e)
            time.sleep(2 ** attempt)
        raise LLMError(last or "unknown LLM error")


class OllamaLLM(LLM):
    """Local model via Ollama (https://ollama.com): no API key, no cost, data stays on your machine."""
    def __init__(self, model: str = "llama3.1:8b", host: str | None = None):
        self.model = model
        self.url = (host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")).rstrip("/") + "/api/chat"
        self.calls = self.input_tokens = self.output_tokens = 0

    def complete(self, system, user, max_tokens=2000, temperature=0.0):
        msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
        body = json.dumps({"model": self.model, "messages": msgs, "stream": False,
                           "options": {"temperature": temperature, "num_predict": max_tokens, "num_ctx": 8192}}).encode()
        try:
            req = urllib.request.Request(self.url, data=body, headers={"content-type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=600) as r:
                data = json.load(r)
        except (urllib.error.URLError, TimeoutError) as e:
            raise LLMError(f"Ollama not reachable at {self.url} ({e}). Install it and run `ollama serve`, then `ollama pull {self.model}`.")
        self.calls += 1
        self.input_tokens += data.get("prompt_eval_count", 0)
        self.output_tokens += data.get("eval_count", 0)
        return data.get("message", {}).get("content", "")


KEY_FILE = os.path.expanduser("~/.config/smartstudy/gemini_key")   # outside the repository, never committed


def gemini_key() -> str | None:
    """GEMINI_API_KEY env var, or the first line of ~/.config/smartstudy/gemini_key."""
    k = os.environ.get("GEMINI_API_KEY")
    if not k and os.path.exists(KEY_FILE):
        k = open(KEY_FILE).readline().strip()
    return k or None


class GeminiLLM(LLM):
    """Google Gemini via the Gemini API (free key from https://aistudio.google.com/apikey).

    Fast retries (the web app must answer in well under a minute) and an optional fallback chain of other
    models, set with SMARTSTUDY_FALLBACK_MODELS (comma separated), used only when the main model keeps failing."""
    def __init__(self, model: str = "gemini-3.1-flash-lite", api_key: str | None = None, retries: int = 3, timeout: int = 40):
        self.model, self.retries, self.timeout = model, retries, timeout
        self.api_key = api_key or gemini_key()
        fb = os.environ.get("SMARTSTUDY_FALLBACK_MODELS", "")
        self.fallbacks = [m.strip() for m in fb.split(",") if m.strip() and m.strip() != model]
        self.calls = self.input_tokens = self.output_tokens = 0
        self.calls_log = []          # (model, seconds, attempts, last_error) per successful call; used for timing info
        if not self.api_key:
            raise LLMError("No Gemini key: set GEMINI_API_KEY or put it in ~/.config/smartstudy/gemini_key")

    def _payload(self, model, system, user, max_tokens, temperature):
        cfg = {"temperature": temperature, "maxOutputTokens": max(max_tokens, 4000)}
        cfg["thinkingConfig"] = {"thinkingBudget": 0} if "2.5" in model else {"thinkingLevel": "minimal"}
        payload = {"contents": [{"role": "user", "parts": [{"text": user}]}], "generationConfig": cfg}
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}
        return json.dumps(payload).encode()

    def complete(self, system, user, max_tokens=2000, temperature=0.0):
        headers = {"content-type": "application/json", "x-goog-api-key": self.api_key}
        last, started = None, time.time()
        for model in [self.model] + self.fallbacks:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            body = self._payload(model, system, user, max_tokens, temperature)
            for attempt in range(1, self.retries + 1):
                try:
                    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
                    with urllib.request.urlopen(req, timeout=self.timeout) as r:
                        data = json.load(r)
                    self.calls += 1
                    u = data.get("usageMetadata", {})
                    self.input_tokens += u.get("promptTokenCount", 0)
                    self.output_tokens += u.get("candidatesTokenCount", 0)
                    cands = data.get("candidates") or []
                    parts = (cands[0].get("content", {}).get("parts", []) if cands else [])
                    self.calls_log.append((model, round(time.time() - started, 1), attempt, last))
                    return "".join(x.get("text", "") for x in parts)
                except urllib.error.HTTPError as e:
                    last = f"HTTP {e.code}"
                    detail = e.read().decode(errors="replace")[:300]
                    if e.code not in (429, 500, 502, 503, 504):
                        raise LLMError(f"{last}: {detail}")
                    last = f"{last}: {detail}"
                except (urllib.error.URLError, TimeoutError, OSError) as e:
                    last = str(e)
                if attempt < self.retries:
                    time.sleep(2 * 2 ** (attempt - 1))      # 2 s, 4 s
        raise LLMError(last or "unknown LLM error")


def make_llm(provider: str = "anthropic", model: str | None = None) -> LLM:
    if provider == "gemini":
        return GeminiLLM(model or os.environ.get("SMARTSTUDY_MODEL", "gemini-3.1-flash-lite"))
    if provider == "ollama":
        return OllamaLLM(model or os.environ.get("SMARTSTUDY_MODEL", "llama3.1:8b"))
    return AnthropicLLM(model or DEFAULT_MODEL)
