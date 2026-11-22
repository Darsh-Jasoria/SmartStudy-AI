"""python3 -m smartstudy.collect --versions v1 v2 --dir results/replay
Writes prompts that still need an answer. Re-run after answers are stored until it reports 0 pending."""
from __future__ import annotations
import argparse
from pathlib import Path

from .evaluate import ROOT, load_cases, N_Q, MAX_W
from .pipeline import run
from .replay import Missing, ReplayLLM


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--versions", nargs="+", default=["v1", "v2", "v3", "v4"])
    ap.add_argument("--dir", default=str(ROOT / "test-data" / "replay_simulated_oct28"))
    a = ap.parse_args()
    cases = load_cases(ROOT / "test-data")
    for v in a.versions:
        llm = ReplayLLM(a.dir)
        for c in cases:
            try:
                run(c["notes"], v, llm, N_Q, MAX_W)
            except Missing:
                pass
        n = llm.write_pending(v)
        print(f"{v}: {n} prompts pending ({len(cases) - n if v != 'v4' else 'n/a'} cases already answered)")


if __name__ == "__main__":
    main()
