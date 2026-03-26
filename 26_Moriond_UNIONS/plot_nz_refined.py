"""Refined blind n(z) plot for Moriond slides — thinner lines, tighter layout."""

import numpy as np
import matplotlib.pyplot as plt

MPLSTYLE = "/n17data/cdaley/unions/pure_eb/code/sp_validation/cosmo_inference/notebooks/2D_cosmic_shear_paper_plots/config/paper.mplstyle"
plt.style.use(MPLSTYLE)

NZ_DIR = "/n17data/sguerrini/UNIONS/WL/nz/v1.4.6"
OUTPUT = "images/blind_nz_ABC.png"

BLINDS = ["A", "B", "C"]
COLORS = ["royalblue", "crimson", "forestgreen"]
LABELS = ["Blind A", "Blind B", "Blind C"]

fig, ax = plt.subplots(figsize=(6.5, 4.0))

for blind, color, label in zip(BLINDS, COLORS, LABELS):
    z, nz = np.loadtxt(f"{NZ_DIR}/nz_SP_v1.4.6_{blind}.txt", unpack=True)
    ax.plot(z, nz, linewidth=1.6, color=color, label=label, alpha=0.85)

ax.set_xlabel(r"$z$", fontsize=16)
ax.set_ylabel(r"$n(z)$", fontsize=16)
ax.set_xlim(0, 2.0)
ax.set_ylim(bottom=0)
ax.legend(frameon=False, loc="upper right", fontsize=14)
ax.tick_params(labelsize=14)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.tight_layout()
fig.savefig(OUTPUT, dpi=300, bbox_inches="tight", facecolor="white")
print(f"Saved {OUTPUT}")
