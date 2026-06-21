# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "matplotlib", "seaborn"]
# ///
"""Which κ survey constrains where — error-bar size, SPT-3G GMV vs ACT DR6.

Cosmic shear × CMB-κ (γ×κ), the highest-S/N bin (6), log15 binning. The point is
the *error-bar size* and how it fluctuates with ℓ: ACT is tighter at large scales
(sample-variance limited, where its wider Euclid overlap wins), SPT is tighter at
small scales (reconstruction-noise limited, where its depth/resolution win) — a
clean crossover.

NOT BLINDED, and it does not need to be: the markers are FAKE data placed *exactly
on the fiducial theory curve* (no measured amplitude anywhere), carrying only each
survey's real per-bandpower error bar (σ = sqrt(diag) of that survey's on-disk
covariance, blind-independent). Nothing about the measured cross amplitude appears —
the figure is about constraining power, σ(ℓ), not the signal.
"""
import pickle
from pathlib import Path

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

ROOT = Path("/leonardo_work/EUHPC_E07_074/cdaley00/cmbx")
THEORY = ROOT / "results/redshift/theory_cls.pkl"
OUT = ROOT / "docs/talks/images/spt26_kappa_constraints.png"
BIN = 6
LMAX = 3000

SURVEYS = {
    "SPT-3G GMV": dict(color="#c0392b", marker="o", dodge=1.0 - 0.02,
                       pkl=ROOT / "results/rr2_v2_1_wl_031224-v0.1/cross_spectra/shear_lensmc_x_spt_winter_gmv.pkl"),
    "ACT DR6":    dict(color="#2a8c8c", marker="s", dodge=1.0 + 0.02,
                       pkl=ROOT / "results/act_dr6/shear_kappa_cross_spectra/shear_lensmc_x_act_dr6.pkl"),
}

theory = pickle.load(open(THEORY, "rb"))
theory_ells = np.asarray(theory["ells"], dtype=float)
ell_full = np.arange(LMAX + 1)
cl = np.asarray(theory["cls"][("e", "k", BIN, 0)], dtype=float)  # γ×κ, bin 6
cl_full = np.zeros_like(ell_full, dtype=float)
valid = ell_full >= 2
th = (theory_ells >= 2) & np.isfinite(cl) & (cl > 0)
cl_full[valid] = np.exp(np.interp(np.log(ell_full[valid]), np.log(theory_ells[th]), np.log(cl[th])))


def sigma_at(pkl):
    spec = pickle.load(open(pkl, "rb"))["spectra"][f"bin{BIN}"]
    leff = np.asarray(spec["ells"], dtype=float)
    return leff, np.sqrt(np.diag(np.asarray(spec["cov"], dtype=float)))


# --------------------------------------------------------------------- figure
sns.set_theme(context="talk", style="whitegrid")
plt.rcParams.update({"axes.edgecolor": "0.2", "axes.linewidth": 0.8,
                     "font.family": "DejaVu Sans", "legend.frameon": False})

fig, ax = plt.subplots(figsize=(12.5, 7.2))
ax.plot(ell_full[2:], ell_full[2:] * cl_full[2:], color="0.45", lw=2.0, alpha=0.85,
        zorder=1, label="fiducial theory")

for label, cfg in SURVEYS.items():
    leff, sig = sigma_at(cfg["pkl"])
    # fake points sit EXACTLY on the theory curve; only the error bar is real.
    th_at = np.interp(leff, ell_full, cl_full)
    ax.errorbar(leff * cfg["dodge"], leff * th_at, yerr=leff * sig, fmt=cfg["marker"],
                ms=8, color=cfg["color"], ecolor=cfg["color"], elinewidth=1.8, capsize=4.5,
                mfc="white", mew=1.8, zorder=3, label=label)

ax.set_xscale("log")
ax.set_xlim(95, 3050)
ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
ax.yaxis.get_offset_text().set_size(11)
ax.grid(which="both", alpha=0.15)
ax.set_xlabel(r"$\ell$")
ax.set_ylabel(r"$\ell\,C_\ell^{\gamma\kappa}$")
ax.legend(loc="upper right", fontsize=14, title=f"$\\gamma\\times\\kappa$, bin {BIN}",
          title_fontsize=14)
# No title — the slide headline carries it (avoid duplicate titles).
ax.text(0.03, 0.05, "markers placed on theory — only the error bar is real",
        transform=ax.transAxes, fontsize=12, va="bottom", ha="left", color="0.4", style="italic")

fig.tight_layout()
fig.savefig(OUT, dpi=180, bbox_inches="tight")
print("wrote", OUT)
