# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "matplotlib", "seaborn"]
# ///
"""SPT-summer talk — systematics-null summary figure.

The honest systematics slide. One panel per κ-cross (δ_g×κ, γ×κ); rows are the
contaminant templates the analysis *should* null-test; columns are the six Euclid
tomographic bins. Each cell is the coherent aggregate bias the template injects,
S_bias = √(Σ_ℓ (X/σ)²) in σ, from the DES/Chang contamination metric
X = C^{κS}·C^{fS}/C^{SS} (σ from the Knox-diagonal analytic variance).

Only the galactic-extinction row is populated — that is the one systematic redone
on the current (rr2_v2_1) catalog. Every other template row is greyed "not yet
redone": the figure itself says *one template is not a systematics budget*.

Reads the lc-native metric summary for the SPT-κ + log15 universe (`baseline`):
results/.../systematics/extinction_contamination_summary.csv  (refresh with
`lc run extinction_contamination_metric -u baseline`).
"""
import csv
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import seaborn as sns

ROOT = Path("/leonardo_work/EUHPC_E07_074/cdaley00/cmbx")
SUMMARY = ROOT / "results/rr2_v2_1_wl_031224-v0.1/systematics/extinction_contamination_summary.csv"
OUT = ROOT / "docs/talks/images/spt26_systematics_null.png"

BINS = [1, 2, 3, 4, 5, 6]
# rows top→bottom; only the first is quantified on this catalog
TEMPLATES = ["Galactic extinction", "Stellar density", "Exposure depth",
             "Zodiacal light", "N/S asymmetry"]
QUANTIFIED = "Galactic extinction"
PANELS = [("gc", r"$\delta_g \times \kappa$",  "clustering $\\times$ CMB lensing"),
          ("wl", r"$\gamma \times \kappa$",    "cosmic shear $\\times$ CMB lensing")]

# --- read S_bias per (tracer, bin) from the refreshed summary ---
sbias = {}  # sbias[tracer][bin] = S_bias in σ
with open(SUMMARY, newline="") as fh:
    for row in csv.DictReader(fh):
        sbias.setdefault(row["tracer"], {})[int(row["bin"])] = float(row["s_bias_sigma"])

vmax = max(v for t in sbias.values() for v in t.values()) * 1.05  # shared color scale
cmap = sns.color_palette("rocket_r", as_cmap=True)
norm = plt.Normalize(0, vmax)

sns.set_theme(style="white", context="talk")
fig, axes = plt.subplots(1, 2, figsize=(15.5, 5.6), sharey=True)

nrow, ncol = len(TEMPLATES), len(BINS)
for ax, (tracer, sym, sub) in zip(axes, PANELS):
    for r, tmpl in enumerate(TEMPLATES):          # r=0 is top row
        y = nrow - 1 - r
        quantified = tmpl == QUANTIFIED
        for c, b in enumerate(BINS):
            if quantified:
                val = sbias[tracer][b]
                ax.add_patch(Rectangle((c, y), 1, 1, facecolor=cmap(norm(val)),
                                       edgecolor="white", lw=2))
                ax.text(c + 0.5, y + 0.5, f"{val:.2f}", ha="center", va="center",
                        color="white" if norm(val) > 0.55 else "0.15",
                        fontsize=13, fontweight="bold")
            else:
                ax.add_patch(Rectangle((c, y), 1, 1, facecolor="0.93",
                                       edgecolor="white", lw=2, hatch="///"))
        if not quantified:
            ax.text(ncol / 2, y + 0.5, "not yet redone", ha="center", va="center",
                    color="0.55", fontsize=12, style="italic")
    ax.set_xlim(0, ncol); ax.set_ylim(0, nrow)
    ax.set_xticks(np.arange(ncol) + 0.5); ax.set_xticklabels([f"bin {b}" for b in BINS], fontsize=12)
    ax.set_yticks(np.arange(nrow) + 0.5)
    ax.set_yticklabels(list(reversed(TEMPLATES)), fontsize=12)
    ax.set_title(f"{sym}   {sub}", fontsize=16, pad=10)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_aspect("equal")

cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=axes,
                    fraction=0.025, pad=0.015)
cbar.set_label(r"coherent bias  $S_{\rm bias}=\sqrt{\sum_\ell (X/\sigma)^2}$   [$\sigma$]",
               fontsize=13)
fig.suptitle("Systematics-null summary — only galactic extinction redone on this catalog",
             fontsize=17, y=1.02)
fig.text(0.5, -0.02,
         r"DES/Chang $X=C^{\kappa S}C^{fS}/C^{SS}$ aggregated over the production range "
         r"$\ell\in[100,3000]$ — coherent bias sub-$\sigma$ in every bin; extinction's "
         r"large-scale ($\ell<100$) coupling is below the analysis floor.",
         ha="center", va="top", fontsize=11.5, color="0.35")
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print("wrote", OUT)

# speaker reference: aggregate range
allv = [v for t in sbias.values() for v in t.values()]
print(f"S_bias range {min(allv):.2f}–{max(allv):.2f}σ  (median {np.median(allv):.2f}σ)")
