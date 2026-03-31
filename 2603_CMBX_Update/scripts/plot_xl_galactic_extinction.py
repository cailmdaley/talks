"""Galactic extinction X_l contamination metric for talk slide.

2×3 grid: rows = density, lensmc; columns = ACT, SPT GMV, SPT PP.
Adapted from plot_contamination_composite.py.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from snakemake_helpers import snakemake_log
from plot_utils import FW, FH, setup_theme, LABELS, BIN_PALETTE, TOM_BINS
from spectrum_utils import load_cross_spectrum

snakemake = snakemake  # type: ignore # noqa: F821

output_png = Path(snakemake.output.png)

# Derive directories from input files
cmbk_sys_dir = Path(snakemake.input.cmbk_sys_npz[0]).parent
sys_dir = Path(snakemake.input.sys_npz[0]).parent
signal_dir = Path(snakemake.input.signal_ref[0]).parent

methods = ["density", "lensmc"]
cmbk_list = ["act", "spt_winter_gmv", "spt_winter_pp"]
cmbk_labels = {"act": "ACT DR6", "spt_winter_gmv": "SPT-3G GMV", "spt_winter_pp": "SPT-3G PP"}
method_labels = {"density": "Galaxy density", "lensmc": "Cosmic shear (lensmc)"}

setup_theme()
fig, axes = plt.subplots(2, 3, figsize=(3 * FW, 1.8 * FH), sharex=True)

for row, method in enumerate(methods):
    for col, cmbk in enumerate(cmbk_list):
        ax = axes[row, col]

        cmbk_sys_path = cmbk_sys_dir / f"galactic_extinction_x_{cmbk}_cls.npz"
        if not cmbk_sys_path.exists():
            ax.text(0.5, 0.5, "No data", transform=ax.transAxes, ha="center", va="center")
            continue

        cmbk_sys = np.load(str(cmbk_sys_path), allow_pickle=True)
        cl_kS = cmbk_sys["cls"][0]
        ells = cmbk_sys["ells"]
        cl_SS = cmbk_sys["cl_sys_auto"] if "cl_sys_auto" in cmbk_sys else None

        for i, bin_id in enumerate(TOM_BINS):
            fS_path = sys_dir / f"galactic_extinction_x_{method}_bin{bin_id}_cls.npz"
            if not fS_path.exists():
                continue

            fS_data = np.load(str(fS_path), allow_pickle=True)
            cl_fS = fS_data["cls"][0]

            if cl_SS is not None:
                safe = np.abs(cl_SS) > 1e-30
                metric = np.zeros_like(cl_kS)
                metric[safe] = cl_kS[safe] * cl_fS[safe] / cl_SS[safe]
            else:
                metric = cl_kS * cl_fS

            ax.plot(ells, ells * metric, color=BIN_PALETTE[i], lw=1.0, alpha=0.85,
                    label=f"bin {bin_id}" if row == 0 and col == 0 else None)

        # Reference uncertainty band from bin 3
        ref_path = signal_dir / f"{method}_bin3_x_{cmbk}_cls.npz"
        if ref_path.exists():
            ref = load_cross_spectrum(ref_path)
            if ref["cov_primary"] is not None and np.allclose(ref["ells"], ells):
                sigma = ref["err"]
                ax.fill_between(ells, -ells * 0.01 * sigma, ells * 0.01 * sigma,
                                color="gray", alpha=0.3,
                                label=r"1% of $\sigma$" if row == 0 and col == 0 else None)
                ax.fill_between(ells, -ells * 0.10 * sigma, ells * 0.10 * sigma,
                                color="gray", alpha=0.12,
                                label=r"10% of $\sigma$" if row == 0 and col == 0 else None)

        ax.axhline(0, color="gray", ls="--", lw=0.5, alpha=0.4)
        ax.set_xscale("log")

        if row == 0:
            ax.set_title(cmbk_labels[cmbk], fontsize=12, fontweight="bold")
        if col == 0:
            ax.set_ylabel(method_labels[method], fontsize=10, fontweight="bold")
        if row == 1:
            ax.set_xlabel(r"Multipole $\ell$")

fig.legend(loc="upper center", ncol=8, fontsize=9, bbox_to_anchor=(0.5, 1.02),
           frameon=True, fancybox=False, edgecolor="0.8")

fig.suptitle(
    r"Galactic extinction contamination: $\ell\, X^f_S(\ell)$",
    fontsize=13, fontweight="bold", y=1.06,
)

sns.despine()
fig.tight_layout(rect=[0, 0, 1, 0.97])

output_png.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(output_png, bbox_inches="tight", dpi=150)
plt.close(fig)

snakemake_log(snakemake, f"Saved: {output_png}")
