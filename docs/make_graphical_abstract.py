"""Draw the graphical abstract shown on the repository front page.

The model curves are computed from the posterior draws of the full hierarchical
TVA model (results/posterior_full.nc, archived on Zenodo), as in manuscript
Figure 2: posterior median and 95% credible band of the predicted number of
letters reported. The points are the observed mean number of letters reported at
each group's actual exposure times, computed from the trial data with the same
preprocessing as the notebook (duplicate audit, participant exclusions, novice
frame-snap with dominant-only mapping).

Run from the repository root:  python docs/make_graphical_abstract.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "Data_Expert_Novice_Combined_Data.csv"
POSTERIOR_FILE = ROOT / "results" / "posterior_full.nc"
OUT = ROOT / "docs" / "graphical_abstract.png"

REPO_URL = "github.com/ashkantashk/type-designers-see-text-differently"
DATA_DOI = "10.5281/zenodo.24152973"

FONTS = ["Helvetica", "Klimax Plus"]
GROUPS = ["Novice", "Expert"]                      # group index 0 = Novice, 1 = Expert
NOVICE, EXPERT = "#1f77b4", "#d62728"              # same encoding as the manuscript figures
INK, INK2, RULE, SURFACE, PANEL = "#1a1a1a", "#4d4d4d", "#c9c9c9", "#ffffff", "#f3f4f6"
STYLE = {"Novice": dict(color=NOVICE, ls="-", marker="s"),
         "Expert": dict(color=EXPERT, ls="--", marker="o")}


# ---------------------------------------------------------------------------
# Data: observed mean letters reported per font, group and actual exposure time
# ---------------------------------------------------------------------------
def observed_means():
    raw = pd.read_csv(DATA_FILE)
    raw["Font"] = raw["Font"].replace({"KlimaxStd-Plus": "Klimax Plus"})
    raw = raw[~raw["Participants_ID"].isin(["R17_Novice", "R8_Expert"])].copy()

    def n_correct(letters, responses):
        """Each stimulus letter can be matched once (duplicate-response audit)."""
        if pd.isna(responses) or responses in ("[]", ""):
            return 0
        pool, n = list(str(letters)), 0
        for ch in str(responses):
            if ch in pool:
                pool.remove(ch)
                n += 1
        return n

    raw["P"] = [n_correct(l, r) for l, r in zip(raw["Letters"], raw["Responses"])]

    frame = 1000.0 / 60.0
    novice = raw["GroupCondition"].eq("Novice")
    snapped = np.round(raw["TargetDisplay_chrono"] * 60.0 / 1000.0) * frame
    raw["t"] = np.where(novice, snapped, raw["TargetDisplay_ms"].astype(float))
    dominant_frames = {10: 1, 20: 2, 30: 2, 40: 3, 50: 4, 60: 4, 90: 6, 200: 13}
    on_dominant = (raw["t"] - raw["TargetDisplay_ms"].map(dominant_frames) * frame).abs() < 0.1
    dat = raw[~novice | on_dominant]
    assert len(dat) == 5281, f"expected 5,281 analysed trials, got {len(dat)}"
    return dat.groupby(["Font", "GroupCondition", "t"])["P"].mean()


# ---------------------------------------------------------------------------
# Posterior: population-level K, C, t0 draws for each font x group
# ---------------------------------------------------------------------------
def posterior_parameters():
    if not POSTERIOR_FILE.exists():
        sys.exit(f"{POSTERIOR_FILE} not found. Download it from https://doi.org/{DATA_DOI} "
                 "into results/ (see README, 'Posterior draws').")
    names = [f"{a}_{p}" for a in ("group_mean", "font", "fontgroup") for p in ("klin", "clin", "tlin")]
    with xr.open_dataset(POSTERIOR_FILE, group="posterior") as post:
        v = {}
        for name in names:
            da = post[name].stack(sample=("chain", "draw"))
            v[name] = (da if da.dims[0] == "sample" else da.transpose("sample", ...)).values
    params = {}
    for font in FONTS:
        for gi, group in enumerate(GROUPS):
            isK, isE = float(font == "Klimax Plus"), float(group == "Expert")
            lin = {p: v[f"group_mean_{p}"][:, gi] + v[f"font_{p}"] * isK + v[f"fontgroup_{p}"] * isK * isE
                   for p in ("klin", "clin", "tlin")}
            params[font, group] = (5.0 / (1.0 + np.exp(-lin["klin"])),   # K (letters)
                                   np.exp(lin["clin"]),                   # C (letters/s)
                                   np.exp(lin["tlin"]))                   # t0 (s)
    return params


def tva_curves(K, C, t0, t_ms):
    """Predicted letters reported, one row per posterior draw."""
    dt = np.clip(t_ms[None, :] / 1000.0 - t0[:, None], 0.0, None)
    return K[:, None] * (1.0 - np.exp(-(C / K)[:, None] * dt))


obs = observed_means()
params = posterior_parameters()

# Expert - Novice difference on the common 0-200 ms grid (manuscript Figure 9)
t_common = np.arange(0.0, 201.0)
delta = {}
for font in FONTS:
    d = tva_curves(*params[font, "Expert"], t_common) - tva_curves(*params[font, "Novice"], t_common)
    lo = np.quantile(d, 0.025, axis=0)
    hi = np.quantile(d, 0.975, axis=0)
    credible = t_common[lo > 0]
    delta[font] = dict(credible=credible, at100=(d[:, 100].mean(), lo[100], hi[100]))
    del d
K_expert_minus_novice = params["Klimax Plus", "Expert"][0] - params["Klimax Plus", "Novice"][0]
p_dK = float(np.mean(K_expert_minus_novice > 0))

print("Observed means:")
print(obs.round(3).to_string())
for font in FONTS:
    c = delta[font]["credible"]
    print(f"{font}: credible window {'none' if c.size == 0 else f'{c.min():.0f}-{c.max():.0f} ms ({c.size} points)'}; "
          "Delta(100 ms) = {:+.3f} [{:+.3f}, {:+.3f}]".format(*delta[font]["at100"]))
print(f"P(Delta K > 0 | Klimax Plus) = {p_dK:.3f}")


# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
def box(ax, x, y, w, h, text, fc=PANEL, ec=RULE, fs=10, weight="normal", lw=1.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.015",
                                fc=fc, ec=ec, lw=lw, transform=ax.transAxes, clip_on=False))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=INK,
            weight=weight, transform=ax.transAxes, linespacing=1.35)


def arrow(ax, x0, x1, y):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), transform=ax.transAxes, arrowstyle="-|>",
                                 mutation_scale=13, lw=1.2, color=INK2, clip_on=False))


plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5, "axes.edgecolor": RULE,
                     "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2})
fig = plt.figure(figsize=(13.5, 7.3), facecolor=SURFACE)

fig.text(0.025, 0.958, "Do type designers see text differently?", fontsize=21, weight="bold",
         color=INK, va="top")
fig.text(0.025, 0.893, "Short-exposure letter recognition in 17 professional type designers and "
         "17 novices, analysed with the Theory of Visual Attention (TVA)",
         fontsize=11.5, color=INK2, va="top")

# ---- experiment schematic ----------------------------------------------------
ax0 = fig.add_axes([0.025, 0.30, 0.315, 0.53])
ax0.set_axis_off()
ax0.text(0.0, 1.0, "Experiment", fontsize=12.5, weight="bold", color=INK, va="top",
         transform=ax0.transAxes)
box(ax0, 0.00, 0.69, 0.47, 0.21, "Experts\n17 type designers\n≥ 3 years of practice", fc="#fbe9e9", ec=EXPERT)
box(ax0, 0.53, 0.69, 0.47, 0.21, "Novices\n17 lay readers\nage-matched", fc="#e8f1f9", ec=NOVICE)

y_seq, h_seq = 0.38, 0.18
box(ax0, 0.000, y_seq, 0.190, h_seq, "+\nfixation")
box(ax0, 0.255, y_seq, 0.300, h_seq, "a v f o l\n10–200 ms", fs=11, weight="bold")
box(ax0, 0.620, y_seq, 0.170, h_seq, "mask\n800 ms")
box(ax0, 0.855, y_seq, 0.145, h_seq, "type\nletters")
for x0, x1 in [(0.193, 0.252), (0.558, 0.617), (0.793, 0.852)]:
    arrow(ax0, x0, x1, y_seq + h_seq / 2)
ax0.text(0.5, y_seq - 0.04, "Whole report of random five-letter strings, 160 trials each",
         ha="center", va="top", fontsize=9.8, color=INK2, transform=ax0.transAxes)

ax0.text(0.5, 0.215, "Two typefaces, within subjects", ha="center", va="bottom", fontsize=9.8,
         color=INK2, transform=ax0.transAxes)
box(ax0, 0.00, 0.00, 0.47, 0.19, "Helvetica\nfamiliar text face")
box(ax0, 0.53, 0.00, 0.47, 0.19, "Klimax Plus\nheavy display face")

# ---- posterior TVA curves ------------------------------------------------------
fig.text(0.40, 0.848, "Posterior median and 95% credible band of the TVA model; points: observed means",
         fontsize=10.5, color=INK2, va="top")
t_grid = np.arange(0.0, 221.0)
for col, font in enumerate(FONTS):
    ax = fig.add_axes([0.40 + col * 0.315, 0.355, 0.265, 0.41])
    ax.set_facecolor(SURFACE)
    medians = {}
    for group in GROUPS:
        st = STYLE[group]
        curves = tva_curves(*params[font, group], t_grid)
        lo, med, hi = np.quantile(curves, [0.025, 0.5, 0.975], axis=0)
        del curves
        medians[group] = med
        ax.fill_between(t_grid, lo, hi, color=st["color"], alpha=0.16, lw=0, zorder=2)
        ax.plot(t_grid, med, color=st["color"], ls=st["ls"], lw=2.2, zorder=3)
        o = obs.loc[font, group]
        ax.scatter(o.index, o.values, color=st["color"], marker=st["marker"], s=36, zorder=4,
                   edgecolor=SURFACE, linewidth=0.8)
    # direct labels at the right end of each median curve (ink, not series colour)
    i205 = 205
    for group, dy, va in [("Expert", 0.17, "bottom"), ("Novice", -0.17, "top")]:
        ax.text(i205, medians[group][i205] + dy, group, fontsize=10, color=INK, weight="bold",
                ha="right", va=va, zorder=5,
                bbox=dict(boxstyle="round,pad=0.15", fc=SURFACE, ec="none", alpha=0.75))

    ax.set_title(font, fontsize=13, weight="bold", color=INK, loc="left", pad=6)
    ax.set_xlim(0, 222)
    ax.set_ylim(0, 5.1)
    ax.set_yticks(range(6))
    ax.set_xlabel("Exposure duration (ms)")
    if col == 0:
        ax.set_ylabel("Letters reported (of 5)")
    ax.grid(alpha=0.25, lw=0.8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    c = delta[font]["credible"]
    if c.size == 0:
        note = "No credible group difference:\n95% CrI includes 0 at all exposures\n(close to the 5-letter ceiling)"
    else:
        m, lo100, hi100 = delta[font]["at100"]
        note = f"At 100 ms experts report\n{m:+.2f} letters (95% CrI {lo100:.2f} to {hi100:.2f})"
        # bracket over the window where the 95% CrI of Expert - Novice excludes zero
        yb = 4.30
        ax.plot([c.min(), c.min(), c.max(), c.max()], [yb - 0.10, yb, yb, yb - 0.10], color=INK, lw=1.2)
        ax.text((c.min() + c.max()) / 2, yb + 0.07,
                f"Expert advantage credible\nfrom {c.min():.0f} to {c.max():.0f} ms (95% CrI > 0)",
                ha="center", va="bottom", fontsize=9.8, color=INK, linespacing=1.3)
    ax.text(0.97, 0.04, note, transform=ax.transAxes, ha="right", va="bottom", fontsize=9.8,
            color=INK, linespacing=1.35, zorder=6,
            bbox=dict(boxstyle="round,pad=0.4", fc=SURFACE, ec=RULE, lw=0.8))
    if col == 0:
        handles = [Line2D([], [], color=STYLE[g]["color"], ls=STYLE[g]["ls"], lw=2.2,
                          marker=STYLE[g]["marker"], markersize=6, label=g) for g in GROUPS]
        ax.legend(handles=handles, loc="center right", bbox_to_anchor=(1.0, 0.46),
                  frameon=False, fontsize=10.5)

# ---- key messages --------------------------------------------------------------
msgs = [
    ("Font effect: large and certain",
     "Klimax Plus lowers capacity K and speed C\nand raises threshold t0 in both groups\n"
     "(posterior probability 1.000)."),
    ("Expertise: probable, capacity only",
     f"Under Klimax Plus, experts hold more letters\nin VSTM: P(ΔK > 0) = {p_dK:.3f}".replace("0.", ".", 1)
     + ", d = 0.98.\n"
     "Helvetica: no credible difference (ceiling)."),
    ("Implication for typeface testing",
     "Type designers read a demanding display\nface better than its intended readers, so\n"
     "legibility tests should use non-experts."),
]
for col, (head, body) in enumerate(msgs):
    axb = fig.add_axes([0.025 + col * 0.322, 0.065, 0.31, 0.175])
    axb.set_axis_off()
    axb.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.04",
                                 fc=PANEL, ec=RULE, lw=1.0, transform=axb.transAxes, clip_on=False))
    axb.text(0.05, 0.84, head, fontsize=11.5, weight="bold", color=INK, va="center",
             transform=axb.transAxes)
    axb.text(0.05, 0.40, body, fontsize=10.3, color=INK2, va="center", transform=axb.transAxes,
             linespacing=1.4)

fig.text(0.025, 0.018, f"Code: {REPO_URL}     Posterior draws: doi.org/{DATA_DOI}",
         fontsize=9, color=INK2, va="bottom")
fig.text(0.975, 0.018, "Mangas, Tashk, Bækgaard & Beier", fontsize=9, color=INK2,
         ha="right", va="bottom")

fig.savefig(OUT, dpi=160, facecolor=SURFACE)
print(f"wrote {OUT}")
