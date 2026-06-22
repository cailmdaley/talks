# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "matplotlib", "seaborn"]
# ///
"""Which κ survey constrains where — error-bar size, SPT-3G GMV vs ACT DR6.

The two CMB-lensing crosses at the highest-S/N bin (6), log15 binning, stacked as
wide rows: cosmic shear × CMB-κ (γ×κ, top) and galaxy clustering × CMB-κ (δ_g×κ,
bottom). The point is the *error-bar size* and how it fluctuates with ℓ: ACT is
tighter at large scales (sample-variance limited, where its wider Euclid overlap
wins), SPT is tighter at small scales (reconstruction-noise limited, where its
depth/resolution win) — a clean crossover. The ℓ-region where SPT's error bar is
the smaller of the two is shaded (per panel, from the on-disk σ).

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

XS = ROOT / "results/rr2_v2_1_wl_031224-v0.1/cross_spectra"
ACT = ROOT / "results/act_dr6"
SURVEYS = {
    "SPT-3G GMV": dict(color="#c0392b", marker="o",
                       shear=XS / "shear_lensmc_x_spt_winter_gmv.pkl",
                       gc=XS / "gc_x_spt_winter_gmv.pkl"),
    "ACT DR6":    dict(color="#2a8c8c", marker="s",
                       shear=ACT / "shear_kappa_cross_spectra/shear_lensmc_x_act_dr6.pkl",
                       gc=ACT / "clustering_kappa_cross_spectra/gc_x_act_dr6.pkl"),
}
PANELS = [  # (family key in SURVEYS, theory key, ylabel, title)
    ("shear", ("e", "k", BIN, 0), r"$\ell\,C_\ell^{\gamma\kappa}$",
     r"Cosmic shear $\times$ CMB-$\kappa$   ($\gamma\times\kappa$)"),
    ("gc", ("g", "k", BIN, 0), r"$\ell\,C_\ell^{\delta_g\kappa}$",
     r"Galaxy clustering $\times$ CMB-$\kappa$   ($\delta_g\times\kappa$)"),
]

theory = pickle.load(open(THEORY, "rb"))
theory_ells = np.asarray(theory["ells"], dtype=float)
ell_full = np.arange(LMAX + 1)


def theory_full(key):
    """Fiducial theory on the integer-ℓ grid (log-log interp; ℓ<2 carries none)."""
    cl = np.asarray(theory["cls"][key], dtype=float)
    out = np.zeros_like(ell_full, dtype=float)
    valid = ell_full >= 2
    th = (theory_ells >= 2) & np.isfinite(cl) & (cl > 0)
    out[valid] = np.exp(np.interp(np.log(ell_full[valid]), np.log(theory_ells[th]), np.log(cl[th])))
    return out


def sigma_of(pkl):
    """(ℓ_eff, σ) for a survey×family at bin 6 — σ from the on-disk covariance diagonal."""
    spec = pickle.load(open(pkl, "rb"))["spectra"][f"bin{BIN}"]
    return np.asarray(spec["ells"], dtype=float), np.sqrt(np.diag(np.asarray(spec["cov"], dtype=float)))


def log_dodge(leff, n, frac=0.10):
    """Multiplicative ℓ-dodges so n points span `frac` of the mean log bin spacing."""
    if n < 2:
        return np.array([1.0])
    span = frac * np.mean(np.diff(np.log(np.asarray(leff, dtype=float))))
    return np.exp(np.linspace(-span / 2, span / 2, n))


def shade_spt_better(ax, ls, ss, la, sa, color):
    """Shade the ℓ-region(s) where SPT's error bar is the smaller of the two.

    σ(ℓ) is interpolated log-linearly on a fine grid over the common ℓ-range; each
    contiguous SPT-tighter run is shaded. Returns the ℓ-center of the widest run
    (in log-ℓ) for labelling, or None if SPT is never tighter.
    """
    lo, hi = max(ls.min(), la.min()), min(ls.max(), la.max())
    grid = np.logspace(np.log10(lo), np.log10(hi), 600)
    better = np.interp(np.log(grid), np.log(ls), ss) < np.interp(np.log(grid), np.log(la), sa)
    idx = np.where(better)[0]
    widest = None
    for grp in (np.split(idx, np.where(np.diff(idx) > 1)[0] + 1) if idx.size else []):
        ax.axvspan(grid[grp[0]], grid[grp[-1]], color=color, alpha=0.10, zorder=0)
        if widest is None or grp.size > widest.size:
            widest = grp
    return np.sqrt(grid[widest[0]] * grid[widest[-1]]) if widest is not None else None


# --------------------------------------------------------------------- figure
sns.set_theme(context="talk", style="whitegrid")
plt.rcParams.update({"axes.edgecolor": "0.2", "axes.linewidth": 0.8,
                     "font.family": "DejaVu Sans", "legend.frameon": False})

fig, axes = plt.subplots(2, 1, figsize=(14.5, 10.0), sharex=True)
spt, act = SURVEYS["SPT-3G GMV"], SURVEYS["ACT DR6"]
for ax, (fam, tkey, ylabel, title) in zip(axes, PANELS):
    cl_full = theory_full(tkey)
    ax.plot(ell_full[2:], ell_full[2:] * cl_full[2:], color="0.45", lw=2.0, alpha=0.85,
            zorder=1, label="fiducial theory")
    # SPT-tighter shading (drawn first so it sits underneath the markers).
    ls, ss = sigma_of(spt[fam])
    la, sa = sigma_of(act[fam])
    center = shade_spt_better(ax, ls, ss, la, sa, spt["color"])
    factors = log_dodge(ls, len(SURVEYS))   # cluster spans 10% of the bin spacing
    for k, (label, cfg) in enumerate(SURVEYS.items()):
        leff, sig = sigma_of(cfg[fam])
        # fake points sit EXACTLY on the theory curve; only the error bar is real.
        th_at = np.interp(leff, ell_full, cl_full)
        ax.errorbar(leff * factors[k], leff * th_at, yerr=leff * sig, fmt=cfg["marker"],
                    ms=8, color=cfg["color"], ecolor=cfg["color"], elinewidth=1.8, capsize=4.5,
                    mfc="white", mew=1.8, zorder=3, label=label)
    if center is not None:
        ax.text(center, 0.94, "SPT tighter", transform=ax.get_xaxis_transform(),
                ha="center", va="top", fontsize=12.5, color=spt["color"], weight="bold")
    ax.set_xscale("log")
    ax.set_xlim(95, 3050)
    ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    ax.yaxis.get_offset_text().set_size(11)
    ax.grid(which="both", alpha=0.15)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=16, pad=8)

axes[-1].set_xlabel(r"$\ell$")
axes[0].legend(loc="upper left", fontsize=13, title=f"bin {BIN}", title_fontsize=13)
# Note in the bottom-right of the lower panel — below the rising curve, clear of data.
axes[-1].text(0.985, 0.05, "markers placed on theory — only the error bar is real",
              transform=axes[-1].transAxes, fontsize=11, va="bottom", ha="right",
              color="0.4", style="italic")

fig.tight_layout()
fig.savefig(OUT, dpi=180, bbox_inches="tight")
print("wrote", OUT)
