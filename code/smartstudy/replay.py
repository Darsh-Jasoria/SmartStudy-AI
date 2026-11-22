"""Record/replay LLM: lets prompts be answered by any external model (here: Claude run via Claude Code)
and then scored by the unchanged pipeline/evaluate code.

  collect  -> writes every prompt the pipeline needs but has no answer for into <dir>/pending/<version>/<key>.md
  answer   -> an external model writes its raw reply to <dir>/store/<key>.txt
  replay   -> pipeline reads those replies; a missing reply raises Missing
"""
from __future__ import annotations
import hashlib
from pathlib import Path

from .llm import LLM


class Missing(Exception):
    pass


def key_of(system: str, user: str) -> str:
    return hashlib.sha256((system + "\x00" + user).encode()).hexdigest()[:16]


class ReplayLLM(LLM):
    model = "replay"

    def __init__(self, root, label="replayed", collect_version=None):
        self.root, self.model = Path(root), label
        (self.root / "store").mkdir(parents=True, exist_ok=True)
        self.version, self.pending = collect_version, {}
        self.calls = self.input_tokens = self.output_tokens = 0

    def complete(self, system, user, max_tokens=2000, temperature=0.0):
        k = key_of(system, user)
        f = self.root / "store" / f"{k}.txt"
        if f.exists():
            self.calls += 1
            return f.read_text()
        self.pending[k] = (system, user)
        raise Missing(k)

    def write_pending(self, version):
        d = self.root / "pending" / version
        d.mkdir(parents=True, exist_ok=True)
        for k, (s, u) in self.pending.items():
            (d / f"{k}.md").write_text(f"=== SYSTEM PROMPT ===\n{s}\n\n=== USER MESSAGE ===\n{u}\n")
        return len(self.pending)
