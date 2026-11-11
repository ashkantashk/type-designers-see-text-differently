"""Draw the graphical abstract shown on the repository front page.

The TVA curves use the population-level posterior-mean parameters reported in
the manuscript (Figure 6); the points are the observed mean number of letters
reported per condition and exposure time (Section 8 of the notebook).

Run from the repository root:  python docs/make_graphical_abstract.py
"""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).resolve().parent / "graphical_abstract.png"

# ---- colours (same encoding as the manuscript figures) ----------------------
NOVICE, EXPERT = "#1f77b4", "#d62728"
INK, INK2, RULE, SURFACE, PANEL = "#1a1a1a", "#4d4d4d", "#c9c9c9", "#ffffff", "#f3f4f6"

# ---- population-level posterior means: K (letters), C (letters/s), t0 (s) ---
PARAMS = {
    ("Helvetica", "Novice"):   (4.295, 86.703, 0.015044),
    ("Helvetica", "Expert"):   (4.409, 113.019, 0.012694),
    ("Klimax Plus", "Novice"): (3.117, 46.946, 0.021508),
    ("Klimax Plus", "Expert"): (3.676, 72.047, 0.021554),
}
# ---- observed mean letters reported at each group's actual exposure times ---
T_NOV = [16.67, 33.33, 50.0, 66.67, 100.0, 216.67]
T_EXP = [10, 20, 30, 40, 50, 60, 90, 200]
OBS = {
    ("Helvetica", "Novice"):   [0.444, 1.410, 2.147, 2.709, 3.247, 3.926],
    ("Helvetica", "Expert"):   [0.176, 0.728, 1.618, 2.390, 2.610, 3.176, 3.540, 4.294],
    ("Klimax Plus", "Novice"): [0.104, 0.506, 1.188, 1.656, 2.190, 2.730],
    ("Klimax Plus", "Expert"): [0.059, 0.147, 0.581, 1.199, 1.632, 1.868, 2.688, 3.382],
}


def tva(t_ms, K, C, t0):
    dt = np.clip(t_ms / 1000.0 - t0, 0, None)
    return K * (1 - np.exp(-(C / K) * dt))


def box(ax, x, y, w, h, text, fc=PANEL, ec=RULE, fs=10.5, weight="normal", color=INK, lw=1.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.012",
                                fc=fc, ec=ec, lw=lw, transform=ax.transAxes, clip_on=False))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=color, weight=weight, transform=ax.transAxes, linespacing=1.35)


def arrow(ax, x0, y0, x1, y1):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), transform=ax.transAxes,
                                 arrowstyle="-|>", mutation_scale=14, lw=1.2, color=INK2,
                                 clip_on=False))


plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5,
                     "axes.edgecolor": RULE, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2})

fig = plt.figure(figsize=(14, 7.6), facecolor=SURFACE)
gs = fig.add_gridspec(nrows=2, ncols=3, width_ratios=[1.15, 1, 1], height_ratios=[1, 0.42],
                      left=0.03, right=0.975, top=0.78, bottom=0.06, wspace=0.28, hspace=0.55)

# ---- title -------------------------------------------------------------------
fig.text(0.03, 0.955, "Do type designers see text differently?", fontsize=20, weight="bold",
         color=INK, ha="left", va="top")
fig.text(0.03, 0.893, "Short-exposure letter recognition in 17 professional type designers and 17 novices, "
         "analysed with the Theory of Visual Attention (TVA)",
         fontsize=11.5, color=INK2, ha="left", va="top")

# ---- left: design schematic --------------------------------------------------
ax0 = fig.add_subplot(gs[0, 0])
ax0.set_axis_off()
ax0.set_xlim(0, 1); ax0.set_ylim(0, 1)
ax0.text(0.0, 1.0, "Experiment", fontsize=12.5, weight="bold", color=INK, va="top", transform=ax0.transAxes)

box(ax0, 0.00, 0.72, 0.44, 0.17, "Experts\n17 type designers\n(≥ 3 years of practice)", fc="#fbe9e9", ec=EXPERT, fs=9.8)
box(ax0, 0.56, 0.72, 0.44, 0.17, "Novices\n17 lay readers,\nage-matched", fc="#e8f1f9", ec=NOVICE, fs=9.8)

# trial sequence
seq_y, seq_h = 0.41, 0.17
box(ax0, 0.00, seq_y, 0.20, seq_h, "+\nfixation", fs=9.5)
box(ax0, 0.265, seq_y, 0.30, seq_h, "a v f o l\n10–200 ms", fs=11, weight="bold")
box(ax0, 0.63, seq_y, 0.17, seq_h, "mask\n800 ms", fs=9.5)
box(ax0, 0.865, seq_y, 0.135, seq_h, "type\nletters", fs=9.5)
arrow(ax0, 0.205, seq_y + seq_h / 2, 0.26, seq_y + seq_h / 2)
arrow(ax0, 0.57, seq_y + seq_h / 2, 0.625, seq_y + seq_h / 2)
arrow(ax0, 0.805, seq_y + seq_h / 2, 0.86, seq_y + seq_h / 2)
ax0.text(0.5, seq_y - 0.045, "Whole report of random five-letter strings, 160 trials per participant",
         ha="center", va="top", fontsize=9.3, color=INK2, transform=ax0.transAxes)

box(ax0, 0.00, 0.06, 0.47, 0.17, "Helvetica\nfamiliar text face", fs=10)
box(ax0, 0.53, 0.06, 0.47, 0.17, "Klimax Plus\nheavy, unfamiliar display face", fs=10)
ax0.text(0.5, 0.26, "Two typefaces (within-subjects)", ha="center", va="bottom", fontsize=9.5,
         color=INK2, transform=ax0.transAxes)

# ---- middle / right: TVA curves ---------------------------------------------
t_grid = np.linspace(0, 220, 441)
notes = {
    "Helvetica": "No credible group difference\n(both groups near the 5-letter ceiling)",
    "Klimax Plus": "Experts report +0.7 letters more\nat 100 ms (95% CrI [0.13, 1.30]);\ncredible from 55 to 200 ms",
}
for col, font in enumerate(["Helvetica", "Klimax Plus"]):
    ax = fig.add_subplot(gs[0, col + 1])
    ax.set_facecolor(SURFACE)
    for grp, color, ls, mk, t_obs in [("Novice", NOVICE, "-", "s", T_NOV), ("Expert", EXPERT, "--", "o", T_EXP)]:
        K, C, t0 = PARAMS[(font, grp)]
        ax.plot(t_grid, tva(t_grid, K, C, t0), color=color, ls=ls, lw=2.2, label=grp, zorder=3)
        ax.scatter(t_obs, OBS[(font, grp)], color=color, marker=mk, s=34, zorder=4,
                   edgecolor=SURFACE, linewidth=0.8)
    ax.set_title(font, fontsize=12.5, weight="bold", color=INK, loc="left", pad=8)
    ax.set_xlim(0, 225); ax.set_ylim(0, 5)
    ax.set_yticks([0, 1, 2, 3, 4, 5])
    ax.set_xlabel("Exposure duration (ms)")
    if col == 0:
        ax.set_ylabel("Letters reported (of 5)")
    ax.grid(alpha=0.25, lw=0.8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.text(0.97, 0.05, notes[font], transform=ax.transAxes, ha="right", va="bottom", fontsize=9.3,
            color=INK, bbox=dict(boxstyle="round,pad=0.4", fc=SURFACE, ec=RULE, lw=0.8))
    if col == 0:
        ax.legend(loc="center right", bbox_to_anchor=(1.0, 0.42), frameon=False, fontsize=10)
    # direct labels on the curves at the right edge, offset so they never touch
    for grp, color, dy, va in [("Novice", NOVICE, -0.13, "top"), ("Expert", EXPERT, 0.13, "bottom")]:
        K, C, t0 = PARAMS[(font, grp)]
        ax.text(205, tva(205, K, C, t0) + dy, grp, color=color, fontsize=9.3, ha="right",
                va=va, weight="bold")

fig.text(0.37, 0.845, "Posterior TVA curves (population-level posterior means) with observed condition means",
         fontsize=10.5, color=INK2, ha="left", va="bottom")

# ---- bottom: key messages ----------------------------------------------------
msgs = [
    ("Font effect: large and certain",
     "Klimax Plus lowers capacity K and speed C and\nraises threshold t0 for everyone (P ≈ 1.000)."),
    ("Expertise effect: capacity, display face only",
     "Experts hold more letters in VSTM under\nKlimax Plus (P(ΔK > 0) = .946; d = 0.98),\nnot under Helvetica."),
    ("Implication for typeface testing",
     "Type designers read a demanding display face\nbetter than its intended readers, so legibility\n"
     "tests should use non-expert readers."),
]
for col, (head, body) in enumerate(msgs):
    axb = fig.add_subplot(gs[1, col])
    axb.set_axis_off()
    axb.set_xlim(0, 1); axb.set_ylim(0, 1)
    axb.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.03",
                                 fc=PANEL, ec=RULE, lw=1.0, transform=axb.transAxes, clip_on=False))
    axb.text(0.05, 0.80, head, fontsize=11, weight="bold", color=INK, va="center", transform=axb.transAxes)
    axb.text(0.05, 0.36, body, fontsize=9.8, color=INK2, va="center", transform=axb.transAxes, linespacing=1.4)

fig.text(0.985, 0.012, "Mangas, Tashk, Bækgaard & Beier — Do Type Designers See Text Differently?",
         fontsize=8.5, color=INK2, ha="right", va="bottom")

fig.savefig(OUT, dpi=160, facecolor=SURFACE)
print(f"wrote {OUT}")
