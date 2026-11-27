import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
from data import *

OUT = ROOT / "submission_ieee" / "figs"
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 7.5, "axes.linewidth": 0.6,
                     "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 300})
C = {"llm": "#cfe2f3", "code": "#d9ead3", "io": "#fff2cc", "bad": "#f4cccc", "edge": "#1f3a5f"}
VC = ["#999999", "#E69F00", "#56B4E9", "#009E73", "#0072B2", "#D55E00"]   # Okabe-Ito, one per version

def box(ax, x, y, w, h, text, kind, fs=7.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.03", fc=C[kind], ec=C["edge"], lw=0.8))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, linespacing=1.15)

def arrow(ax, p, q, style="-|>", ls="-", rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=7, lw=0.8, color=C["edge"], linestyle=ls,
                                 connectionstyle=f"arc3,rad={rad}"))

def workflow(path, w=3.45, h=4.7):
    fig, ax = plt.subplots(figsize=(w, h)); ax.set_xlim(0, 10); ax.set_ylim(-0.6, 14.6); ax.axis("off")
    steps = [("Input: lecture notes,\nN questions, word limit", "io"),
             ("P1 Outline  (LLM)\nlist the topics the notes teach", "llm"),
             ("P2 Generate  (LLM)\nsummary, key terms, N+2 questions,\neach with a verbatim source quote", "llm"),
             ("Quote guard  (code)\nis every quote really in the notes?", "code"),
             ("P3 Moderator  (LLM)\nanswers each question from notes only", "llm"),
             ("Keep first N  (code)\nnever pad; warn if fewer", "code"),
             ("Length guard  (code)\nsummary words <= limit?", "code"),
             ("Study pack: summary, terms, Q&A,\nwarnings, workflow trace", "io")]
    hs = [1.1, 1.2, 1.5, 1.2, 1.2, 1.2, 1.2, 1.1]
    y = 14.4; pos = []
    for (t, k), hh in zip(steps, hs):
        y -= hh; box(ax, 0.2, y, 6.2, hh, t, k); pos.append((y, hh)); y -= 0.55
    for i in range(len(steps) - 1):
        arrow(ax, (3.3, pos[i][0] - 0.02), (3.3, pos[i + 1][0] + pos[i + 1][1] + 0.02))
    # dropped-items log
    box(ax, 7.0, 6.2, 2.9, 1.5, "Dropped items\nlogged in the\nworkflow trace", "bad", 6.8)
    arrow(ax, (6.4, pos[3][0] + 0.6), (7.0, 7.3), ls="--"); arrow(ax, (6.4, pos[4][0] + 0.6), (7.0, 6.6), ls="--")
    # P4 shorten loop
    box(ax, 7.0, 1.4, 2.9, 1.5, "P4 Shorten\n(LLM, once)", "llm", 6.8)
    arrow(ax, (6.4, pos[6][0] + 0.75), (7.0, 2.6)); arrow(ax, (7.0, 1.7), (6.4, pos[6][0] + 0.35), rad=0.0)
    ax.text(6.55, pos[6][0] + 1.25, "too long", fontsize=6, ha="left")
    for (lab, k), xx in zip((("LLM", "llm"), ("code", "code"), ("data", "io")), (0.2, 2.5, 4.6)):
        ax.add_patch(plt.Rectangle((xx, -0.45), 0.35, 0.3, fc=C[k], ec=C["edge"], lw=0.6)); ax.text(xx + 0.5, -0.3, lab, fontsize=6.5, va="center")
    fig.savefig(path, bbox_inches="tight", pad_inches=0.03); plt.close(fig)

def metrics(path, w=3.45, h=3.3):
    keys = [("term_recall", "Term recall (higher better)"), ("coverage", "Coverage (higher better)"),
            ("answer_support", "Answer support (higher better)"), ("term_halluc", "Flagged-term rate (lower better)")]
    fig, axs = plt.subplots(2, 2, figsize=(w, h))
    for ax, (k, ttl) in zip(axs.flat, keys):
        vals = [RES[v]["metrics"][k] for v in VERS]
        bars = ax.bar(VERS, vals, color=VC, edgecolor="black", lw=0.4)
        for b, x in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, x + 0.015, f"{x:.2f}".lstrip("0") if x < 1 else "1.0", ha="center", fontsize=5.8)
        ax.set_title(ttl, fontsize=6.8, pad=2); ax.set_ylim(0, max(vals) * 1.28 + 0.01)
        ax.tick_params(labelsize=6, length=2, pad=1); ax.set_yticks([])
        ax.spines["left"].set_visible(False)
    fig.tight_layout(pad=0.4, h_pad=0.8, w_pad=0.5)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.03); plt.close(fig)

def heatmap(path, w=3.45, h=3.0, key=("cov", "cov_gold"), title="Coverage"):
    M = np.array([ratio(v, *key) for v in VERS]).T
    fig, ax = plt.subplots(figsize=(w, h))
    im = ax.imshow(M, cmap="Blues", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(6)); ax.set_xticklabels(VERS); ax.set_yticks(range(9)); ax.set_yticklabels([NOTE_LABEL[c] for c in CASES])
    ax.tick_params(labelsize=6.3, length=0); [s.set_visible(False) for s in ax.spines.values()]
    for i in range(9):
        for j in range(6):
            ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", fontsize=5.8, color="white" if M[i, j] > .6 else "black")
    ax.set_title(f"{title}: share of gold must-cover ideas present", fontsize=6.8, pad=3)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.03); plt.close(fig)

def ceiling(path, w=3.45, h=2.3):
    gold = per_note("v5", "terms_gold"); emit = per_note("v5", "n_terms")
    x = np.arange(9); fig, ax = plt.subplots(figsize=(w, h))
    ax.bar(x - .2, gold, .4, color="#bbbbbb", edgecolor="black", lw=.4, label="Gold key terms")
    ax.bar(x + .2, emit, .4, color=VC[5], edgecolor="black", lw=.4, label="Terms emitted by v5")
    for i, (g, e) in enumerate(zip(gold, emit)):
        ax.text(i - .2, g + .6, g, ha="center", fontsize=5.8); ax.text(i + .2, e + .6, e, ha="center", fontsize=5.8)
    ax.set_xticks(x); ax.set_xticklabels([NOTE_LABEL[c].replace(" (L)", "*") for c in CASES], rotation=35, ha="right", fontsize=6)
    ax.set_ylabel("Number of terms", fontsize=6.8); ax.tick_params(labelsize=6, length=2); ax.legend(fontsize=6.3, frameon=False, loc="upper left")
    ax.set_ylim(0, 42)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.03); plt.close(fig)

def tradeoff(path, w=3.45, h=2.4):
    calls = {"v0": 0, "v1": 1, "v2": 1, "v3": 1, "v4": 3, "v5": 3}
    fig, ax = plt.subplots(figsize=(w, h))
    off = {"v0": (0.07, -.035), "v1": (-.1, .02), "v2": (.07, -.02), "v3": (.07, -.04), "v4": (.1, .012), "v5": (.1, -.035)}
    for v in VERS:
        m = RES[v]["metrics"]
        ax.scatter(calls[v] + (0.04 if v == "v2" else -0.04 if v == "v3" else 0), m["coverage"], s=20 + 120 * m["answer_support"] ** 2, c=VC[VERS.index(v)], edgecolor="black", lw=.5, zorder=3)
        lab = {"v4": "v4 = v5 (identical)", "v5": ""}.get(v, v)
        if lab: ax.annotate(lab, (calls[v], m["coverage"]), xytext=(calls[v] + (-0.62 if v == "v4" else 0.24 if v == "v2" else 0.13), m["coverage"] + (0.014 if v == "v4" else -0.004)), fontsize=6.5)
    ax.set_xlabel("LLM calls per study pack (v5: +1 only if the summary is too long)", fontsize=6.5)
    ax.set_ylabel("Coverage", fontsize=6.8); ax.set_xticks([0, 1, 3]); ax.set_xlim(-0.4, 3.6); ax.set_ylim(.52, .72)
    ax.tick_params(labelsize=6.3, length=2); ax.grid(alpha=.25, lw=.4)
    ax.text(3.55, .525, "bubble area ~ answer support", fontsize=5.8, ha="right")
    fig.savefig(path, bbox_inches="tight", pad_inches=0.03); plt.close(fig)

def artifact(path, w=3.45, h=2.3):
    """Why answer_support dipped v3->v4: share of unsupported answers that are short-token MCQ answers (proxy artifact)."""
    fig, ax = plt.subplots(figsize=(w, h))
    labels = ["Short answer\n(<=3-char tokens,\ne.g. UDP, O(n^2))", "Paraphrase\n(overlap 0.33-0.57)"]
    vals = [4, 2]
    ax.bar(labels, vals, color=[VC[5], VC[1]], edgecolor="black", lw=.4, width=.5)
    for i, v in enumerate(vals): ax.text(i, v + .1, v, ha="center", fontsize=7)
    ax.set_ylim(0, 5); ax.set_ylabel("v4 answers flagged unsupported", fontsize=6.8); ax.tick_params(labelsize=6.5, length=2)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.03); plt.close(fig)

if __name__ == "__main__":
    workflow(OUT / "fig_workflow.png"); metrics(OUT / "fig_metrics.png"); heatmap(OUT / "fig_heat_cov.png")
    ceiling(OUT / "fig_ceiling.png"); tradeoff(OUT / "fig_tradeoff.png")
    # wide variants for the slide deck
    workflow(OUT / "wide_workflow.png", 4.6, 6.2); metrics(OUT / "wide_metrics.png", 7.0, 3.6)
    heatmap(OUT / "wide_heat_cov.png", 5.8, 3.6); heatmap(OUT / "wide_heat_recall.png", 5.8, 3.6, ("terms_found", "terms_gold"), "Term recall")
    ceiling(OUT / "wide_ceiling.png", 6.2, 3.3); tradeoff(OUT / "wide_tradeoff.png", 5.6, 3.4)
    print("ok")
