"""S8 convergence whisker plot WITH UNIONS constraints.

For the contour slide animation: contours crossfade to this whisker showing
UNIONS is consistent with everything. Wider format for 50% slide column.
"""

import matplotlib.pyplot as plt
import numpy as np

surveys = ["KiDS-1000", "DES Y3", "HSC Y3", "KiDS-Legacy", "DES Y6"]
s8 =      [0.759, 0.759, 0.769, 0.815, 0.798]
err_lo =  [0.021, 0.023, 0.034, 0.021, 0.015]
err_hi =  [0.024, 0.025, 0.031, 0.016, 0.014]

c_kids = "#2ca02c"
c_des  = "#e07020"
c_hsc  = "#7b4fae"
c_unions = "#d42020"
colors = [c_kids, c_des, c_hsc, c_kids, c_des]

# UNIONS constraints (Paper IV line 655, Paper V line 516 — 2D marginalised mode)
unions_surveys = [r"UNIONS $\xi_\pm$", r"UNIONS $C_\ell$"]
unions_s8 =      [0.858, 0.917]
unions_err_lo =  [0.081, 0.079]
unions_err_hi =  [0.082, 0.077]
unions_colors =  [c_unions, "#a01818"]

cmb_s8, cmb_lo, cmb_hi = 0.836, 0.013, 0.012

# Wider figure for 50% slide column (~960px at 130 DPI)
fig, ax = plt.subplots(figsize=(7.4, 5.2))

y = np.arange(len(surveys)) * 1.1
y_unions = np.array([len(surveys) * 1.1 + 0.6, len(surveys) * 1.1 + 1.7])

# CMB band
ax.axvspan(cmb_s8 - cmb_lo, cmb_s8 + cmb_hi, color="#d4a0a0", alpha=0.3, zorder=0,
           ymin=0, ymax=0.92)
ax.axvline(cmb_s8, color="#b04040", ls="-", lw=1.5, alpha=0.5, zorder=0,
           ymin=0, ymax=0.92)

ax.text(cmb_s8, -1.0, "CMB SPA", fontsize=16, fontweight="bold",
        color="#b04040", va="bottom", ha="center")

# Stage III surveys
for i in range(len(surveys)):
    ax.errorbar(
        s8[i], y[i],
        xerr=[[err_lo[i]], [err_hi[i]]],
        fmt="o", color=colors[i], ms=8, lw=2.2,
        capsize=5, capthick=1.8, zorder=5,
    )

for i, name in enumerate(surveys):
    ax.text(0.648, y[i] - 0.18, name, fontsize=14, fontweight="bold",
            va="bottom", ha="left", color=colors[i])

# Separator line
sep_y = len(surveys) * 1.1 - 0.15
ax.axhline(sep_y, color="gray", ls=":", lw=1, alpha=0.5)

# UNIONS constraints
for i in range(len(unions_surveys)):
    ax.errorbar(
        unions_s8[i], y_unions[i],
        xerr=[[unions_err_lo[i]], [unions_err_hi[i]]],
        fmt="s", color=unions_colors[i], ms=10, lw=2.8,
        capsize=6, capthick=2.0, zorder=5,
    )

for i, name in enumerate(unions_surveys):
    ax.text(0.648, y_unions[i] - 0.18, name, fontsize=14, fontweight="bold",
            va="bottom", ha="left", color=unions_colors[i])

ax.set_xlabel(r"$S_8$ from cosmic shear", fontsize=17, labelpad=8)
ax.set_xlim(0.645, 1.02)
ax.set_ylim(-1.3, y_unions[-1] + 0.5)
ax.invert_yaxis()
ax.set_yticks([])
ax.set_xticks([0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00])
ax.tick_params(axis="x", labelsize=16, length=5)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)

plt.tight_layout()
try:
    outpath = snakemake.output[0]
except NameError:
    outpath = "docs/talks/images/s8_convergence_with_unions.png"

plt.savefig(outpath, dpi=130, bbox_inches="tight", facecolor="white")
print("Saved")
