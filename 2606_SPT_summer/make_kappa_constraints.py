# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "matplotlib", "seaborn"]
# ///
"""Which κ survey constrains where — error-bar size, SPT-3G GMV vs ACT DR6 (Euclid TR1).

The two CMB-lensing crosses at a single tomographic bin (bin 5), log15 binning, stacked as
wide rows: cosmic shear × CMB-κ (γ×κ, top) and galaxy clustering × CMB-κ (δ_g×κ,
bottom). The point is the *error-bar size* and how it fluctuates with ℓ: ACT is
tighter only at the very largest scales (its wider Euclid overlap wins the lowest
2–3 bandpowers), SPT is tighter across the bulk (depth/resolution win) — a clean
crossover near ℓ≈200. The ℓ-region where SPT's error bar is the smaller of the two
is shaded (per panel, from the on-disk σ).

EXACT, not a bound. σ is the per-bandpower diagonal of each survey's **full
data-fiducial Gaussian covariance** (NaMaster mode-coupled, 24-spectrum log15
vector), sliced to the bin-5 κ-cross block — `sqrt(diag(cov[isp][isp]))` exactly
as eDR1like.likelihood reads it. This supersedes the earlier Knox-diagonal figure
+ conservative-ACT-bound argument: the full ACT Gaussian now exists on disk, so
both surveys carry their exact mode-coupled σ. (Datafid, not hybrid — the hybrid's
flagged near-null modes live in the WL-auto block, not the κ-cross blocks we use.)

NOT BLINDED, and it does not need to be: the markers are FAKE data placed *exactly
on the fiducial theory curve* (no measured amplitude anywhere), carrying only each
survey's real per-bandpower error bar (blind-independent). Nothing about the
measured cross amplitude appears — the figure is about constraining power, σ(ℓ).
"""
import pickle
from pathlib import Path

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from _ell_axis import style_ell_axis, fold_yscale

ROOT = Path("/leonardo_work/EUHPC_E07_074/cdaley00/cmbx")
THEORY = ROOT / "results/redshift_tr1/theory_cls.pkl"        # TR1 n(z) + self-Hann smoothing
OUT = ROOT / "docs/talks/images/spt26_kappa_constraints.png"
BIN = 5
LMAX = 3000

# Full data-fiducial Gaussian covariance per survey (24-spectrum log15 vector). The
# exact per-bandpower σ is the diagonal of the bin-5 κ-cross auto-block.
SURVEYS = {
    "SPT-3G GMV": dict(color="#c0392b", marker="o",
                       cov=ROOT / "results/tr1/covariance_gaussian/spt_winter_gmvbhttprf_covariance_gaussian_datafid_input.pkl"),
    "ACT DR6":    dict(color="#2a8c8c", marker="s",
                       cov=ROOT / "results/tr1_act/covariance_gaussian/act_dr6_covariance_gaussian_datafid_input.pkl"),
}
PANELS = [  # (cov spectrum stem, theory key, ylabel, title)
    ("kappa_l", ("e", "k", BIN, 0), r"$\ell\,C_\ell^{\gamma\kappa}$",
     r"Cosmic shear $\times$ CMB-$\kappa$   ($\gamma\times\kappa$)"),
    ("kappa_g", ("g", "k", BIN, 0), r"$\ell\,C_\ell^{\delta_g\kappa}$",
     r"Galaxy clustering $\times$ CMB-$\kappa$   ($\delta_g\times\kappa$)"),
]

theory = pickle.load(open(THEORY, "rb"))
theory_ells = np.asarray(theory["ells"], dtype=float)
ell_full = np.arange(LMAX + 1)
_covcache = {label: pickle.load(open(cfg["cov"], "rb")) for label, cfg in SURVEYS.items()}


def theory_full(key):
    """Fiducial theory on the integer-ℓ grid (log-log interp; ℓ<2 carries none)."""
    cl = np.asarray(theory["cls"][key], dtype=float)
    out = np.zeros_like(ell_full, dtype=float)
    valid = ell_full >= 2
    th = (theory_ells >= 2) & np.isfinite(cl) & (cl > 0)
    out[valid] = np.exp(np.interp(np.log(ell_full[valid]), np.log(theory_ells[th]), np.log(cl[th])))
    return out


def sigma_of(label, stem):
    """(ℓ_eff, σ) for a survey×family at bin 5 — σ = sqrt of the full-Gaussian diagonal block.

    The covariance is a list-of-lists over the 24-spectrum vector whose order is
    `list(cls.keys())`; the bin-5 κ-cross auto-block is cov[idx][idx] for
    idx = index of f"{stem}{BIN-1}" (bin 5 → kappa_l4 / kappa_g4, 0-indexed).
    """
    d = _covcache[label]
    key = f"{stem}{BIN - 1}"
    idx = list(d["cls"].keys()).index(key)
    leff = np.asarray(d["cls"][key]["leff"], dtype=float)
    return leff, np.sqrt(np.diag(np.asarray(d["cov"][idx][idx], dtype=float)))


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
sns.set_theme(context="talk", style="ticks")
plt.rcParams.update({"axes.edgecolor": "0.2", "axes.linewidth": 0.8,
                     "font.family": "DejaVu Sans", "legend.frameon": False})

fig, axes = plt.subplots(2, 1, figsize=(14.5, 10.0), sharex=True)
for ax, (stem, tkey, ylabel, title) in zip(axes, PANELS):
    cl_full = theory_full(tkey)
    ax.plot(ell_full[2:], ell_full[2:] * cl_full[2:], color="0.45", lw=2.0, alpha=0.85,
            zorder=1, label="fiducial theory")
    # SPT-tighter shading (drawn first so it sits underneath the markers).
    ls, ss = sigma_of("SPT-3G GMV", stem)
    la, sa = sigma_of("ACT DR6", stem)
    center = shade_spt_better(ax, ls, ss, la, sa, SURVEYS["SPT-3G GMV"]["color"])
    factors = log_dodge(ls, len(SURVEYS))   # cluster spans 10% of the bin spacing
    for k, (label, cfg) in enumerate(SURVEYS.items()):
        leff, sig = sigma_of(label, stem)
        # fake points sit EXACTLY on the theory curve; only the error bar is real.
        th_at = np.interp(leff, ell_full, cl_full)
        ax.errorbar(leff * factors[k], leff * th_at, yerr=leff * sig, fmt=cfg["marker"],
                    ms=8, color=cfg["color"], ecolor=cfg["color"], elinewidth=1.8, capsize=4.5,
                    mfc="white", mew=1.8, zorder=3, label=label)
    if center is not None:
        ax.text(center, 0.94, "SPT tighter", transform=ax.get_xaxis_transform(),
                ha="center", va="top", fontsize=12.5, color=SURVEYS["SPT-3G GMV"]["color"], weight="bold")
    style_ell_axis(ax, 95, 3050)
    fold_yscale(ax, ylabel)
    ax.set_title(title, fontsize=16, pad=8)

axes[-1].set_xlabel(r"$\ell$")
# Note in the bottom-right of the lower panel — below the rising curve, clear of data.
axes[-1].text(0.985, 0.05, "markers placed on theory — only the error bar is real",
              transform=axes[-1].transAxes, fontsize=11, va="bottom", ha="right",
              color="0.4", style="italic")

sns.despine(fig)
fig.tight_layout()
# Legend OUTSIDE the panels (right), guaranteed clear of every bandpower (no-overlap requirement).
h, lab = axes[0].get_legend_handles_labels()
fig.legend(h, lab, loc="center left", bbox_to_anchor=(1.0, 0.5), frameon=False,
           fontsize=13, title=f"bin {BIN}", title_fontsize=13)
fig.savefig(OUT, dpi=180, bbox_inches="tight")
print("wrote", OUT)
