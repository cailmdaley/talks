"""Plot COSEBIS B_n/sigma_n for talk — matching paper figure aesthetics exactly.

Only B-mode row (no E-modes), two panels (all scales, fiducial cuts).
Colors, markers, gray band all match harmonic_config_cosebis_comparison.py.
"""
import numpy as np
import matplotlib.pyplot as plt

MPLSTYLE = "/n17data/cdaley/unions/pure_eb/code/sp_validation/cosmo_inference/notebooks/2D_cosmic_shear_paper_plots/config/paper.mplstyle"
plt.style.use(MPLSTYLE)

d = np.load("images/cosebis_precomputed.npz")
modes = d["modes"]
nmodes = len(modes)

# Exact colors from the paper figure
c_cfg = "#2c5f8a"   # steel blue (config-space)
c_harm = "#c45a2c"  # burnt orange (harmonic-space)

RELIABLE_MODE_MAX = 6
FIG_WIDTH = 7.24  # matches FIG_WIDTH_FULL from paper

fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(FIG_WIDTH, FIG_WIDTH * 0.25),
                                  sharey=True)

for ax, key, title in [(ax_l, "full", "All scales"), (ax_r, "fiducial", "Fiducial scale cuts")]:
    bn_c = d[f"config_Bn_{key}"] / d[f"config_sigma_B_{key}"]
    bn_h = d[f"harm_Bn_{key}"] / d[f"harm_sigma_B_{key}"]

    ax.errorbar(
        modes - 0.1, bn_c, yerr=np.ones(nmodes),
        fmt="o", color=c_cfg, mfc=c_cfg, ms=4, alpha=0.8,
        capsize=2, capthick=0.8, elinewidth=0.8,
        label="Config-space" if key == "fiducial" else None,
    )
    ax.errorbar(
        modes + 0.1, bn_h, yerr=np.ones(nmodes),
        fmt="s", color=c_harm, mfc="white", mew=0.8, ms=4, alpha=0.8,
        capsize=2, capthick=0.8, elinewidth=0.8,
        label="Harmonic-space" if key == "fiducial" else None,
    )
    ax.axhline(0.0, color="black", lw=0.8, alpha=0.6)
    ax.axvspan(0.5, RELIABLE_MODE_MAX + 0.5, color="0.95", alpha=0.5, zorder=0)
    ax.set_title(title)
    ax.set_xlabel("COSEBI mode $n$")
    ax.set_xticks(np.arange(1, nmodes + 1))
    ax.set_xticklabels(
        [str(i) for i in range(1, nmodes + 1)],
        rotation=45, ha="right", rotation_mode="anchor",
    )
    ax.set_xlim(0.5, nmodes + 0.5)
    ax.tick_params(axis="both", width=0.5, length=3)

ax_l.set_ylabel(r"$B_n / \sigma_n$")
ax_l.set_ylim(-3.5, 6.0)
ax_l.set_yticks([0, 3])
ax_r.legend(loc="upper right", framealpha=0.9, ncol=2)

plt.tight_layout()
plt.subplots_adjust(wspace=0.13)
out = "images/cosebis_bsigma_talk.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
print(f"Saved {out}")
