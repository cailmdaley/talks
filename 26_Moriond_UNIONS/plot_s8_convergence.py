"""S8 convergence whisker plot for Moriond slide 2.

Narrow strip (20% of slide width) — large text, color-coded by survey family.
Labels above data points to avoid overlap with error bars.
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
colors = [c_kids, c_des, c_hsc, c_kids, c_des]

cmb_s8, cmb_lo, cmb_hi = 0.836, 0.013, 0.012

# 25% of 1920 = 480px column. Render at ~480px wide so no downscaling.
# 130 DPI × 3.6in = 468px wide. Fonts at matplotlib size ≈ screen px.
fig, ax = plt.subplots(figsize=(3.6, 5.2))

y = np.arange(len(surveys)) * 1.1

# CMB band — stop it below the label area
ax.axvspan(cmb_s8 - cmb_lo, cmb_s8 + cmb_hi, color="#d4a0a0", alpha=0.3, zorder=0,
           ymin=0, ymax=0.88)
ax.axvline(cmb_s8, color="#b04040", ls="-", lw=1.5, alpha=0.5, zorder=0,
           ymin=0, ymax=0.88)

# CMB label in clean space above the band
ax.text(cmb_s8, -1.0, "CMB SPA", fontsize=18, fontweight="bold",
        color="#b04040", va="bottom", ha="center")

for i in range(len(surveys)):
    ax.errorbar(
        s8[i], y[i],
        xerr=[[err_lo[i]], [err_hi[i]]],
        fmt="o", color=colors[i], ms=8, lw=2.2,
        capsize=5, capthick=1.8, zorder=5,
    )

for i, name in enumerate(surveys):
    ax.text(0.688, y[i] - 0.18, name, fontsize=16, fontweight="bold",
            va="bottom", ha="left", color=colors[i])

ax.set_xlabel(r"$S_8$ from cosmic shear", fontsize=19, labelpad=8)
ax.set_xlim(0.685, 0.865)
ax.set_ylim(-1.3, y[-1] + 0.5)
ax.invert_yaxis()
ax.set_yticks([])
ax.set_xticks([0.75, 0.80, 0.85])
ax.tick_params(axis="x", labelsize=19, length=5)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)

plt.tight_layout()
try:
    outpath = snakemake.output[0]
except NameError:
    outpath = "docs/talks/images/s8_convergence_whisker.png"

plt.savefig(outpath, dpi=130, bbox_inches="tight", facecolor="white")
print("Saved")
