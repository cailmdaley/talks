# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "matplotlib", "seaborn"]
# ///
"""Cosmology-shift self-blind illustration for the SPT-summer talk (BLIND-SAFE).

The honesty figure for slide 16 ("blinding"): the cosmology-shift blind *moves*
the data vector, and the audience sees the **bandpower shape** and the
**per-bandpower error-bar sizes** — but NOT the amplitude. The blinded κ-cross
bandpowers are shown against the *windowed fiducial* theory (the same bandpower
window the estimator applies), so the eye can read shape-vs-fiducial without ever
recovering the absolute cross amplitude.

What's on display (all blind-safe):
  - 2 rows (δ_g×κ = kappa_g0..5 ; γ×κ = kappa_l0..5) × 6 tomographic bins.
  - BLINDED bandpowers from the sealed bundle ('cl' at 'leff'), as ℓ·Cℓ on log-ℓ.
  - Error bars = sqrt(diag) of that spectrum's RAW on-disk product covariance — the
    cov is blind-independent (the blind shifts central values, never the covariance),
    so showing it leaks nothing about the chosen cosmology.
  - Overlay: the WINDOWED fiducial theory  t = Bbl @ cl_full, with cl_full the
    UNSHIFTED Planck-18 fiducial interpolated to integer ℓ. The fiducial is never
    blinded; it is the reference the blinded data is allowed to be shifted off of.

Hard blinding contract (a leak unblinds the analysis):
  The ONLY blind-provenance token anywhere is the commitment-hash prefix. The
  figure carries NO chosen index, NO Omega_m/sigma8/S8/ΔS8/w/H0/any cosmology
  number, NO amplitude (not even blinded), NO autos, NO total-σ / data-diagonal
  figure, NO per-bin S/N, NO χ². Shape + per-bandpower error bars + commitment
  hash — nothing else.

Reading discipline (CLAUDE.md): plot ℓ·Cℓ on log-ℓ; read against the error bars.
"""
import json
import pickle
from pathlib import Path

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

ROOT = Path("/leonardo_work/EUHPC_E07_074/cdaley00/cmbx")
BUNDLE = ROOT / "results/baseline/cosmology_shift_talk_datavector/talk_datavector_blinded.pkl"
THEORY = ROOT / "results/redshift/theory_cls.pkl"
XS = ROOT / "results/rr2_v2_1_wl_031224-v0.1/cross_spectra"
SIGMA_PRODUCT = {  # row probe -> raw on-disk product carrying the blind-independent cov
    "delta_kappa": XS / "gc_x_spt_winter_gmv.pkl",       # δ_g×κ
    "gamma_kappa": XS / "shear_lensmc_x_spt_winter_gmv.pkl",  # γ×κ
}
OUT_PNG = ROOT / "docs/talks/images/spt26_selfblind_shift.png"
OUT_JSON = ROOT / "docs/talks/images/spt26_selfblind_shift.json"

# The one permitted blind-provenance token: the commitment hash (prefix shown).
COMMITMENT = "9ecd21338ed16fd7ac27fad294c970e8c59f2cdc010a95518d5c3700bc2a26d1"

LMAX = 3000
# Two rows: (bundle-key prefix, theory family flavor, raw-product key, row math label)
ROWS = [
    ("kappa_g", "g", "delta_kappa", r"$\ell\,C_\ell^{\delta_g\kappa}$"),  # δ_g×κ
    ("kappa_l", "e", "gamma_kappa", r"$\ell\,C_\ell^{\gamma\kappa}$"),    # γ×κ
]
TOM_BINS = range(6)  # 0-indexed bundle bins -> theory bins are (i+1), 1-indexed


def windowed_fiducial(theory, flavor, tomo_bin_1indexed, bbl):
    """t = Bbl @ cl_full: the (unshifted) fiducial pushed through THIS bandpower window.

    cl_full is the Planck-18 fiducial interpolated in log-log onto integer ℓ 0..LMAX,
    matching Bbl's (15, LMAX+1) shape. The fiducial is never blinded.
    """
    lmax = bbl.shape[1] - 1
    cl = np.asarray(theory["cls"][(flavor, "k", tomo_bin_1indexed, 0)], dtype=float)
    th_ells = np.asarray(theory["ells"], dtype=float)
    ell_full = np.arange(lmax + 1)
    cl_full = np.zeros_like(ell_full, dtype=float)
    valid = ell_full >= 2
    good = (th_ells >= 2) & np.isfinite(cl) & (cl > 0)
    cl_full[valid] = np.exp(np.interp(np.log(ell_full[valid]),
                                      np.log(th_ells[good]), np.log(cl[good])))
    return bbl @ cl_full


bundle = pickle.load(open(BUNDLE, "rb"))
cls = bundle["cls"]
theory = pickle.load(open(THEORY, "rb"))
# Raw on-disk products: blind-independent covariance (σ) per row probe.
sigma_products = {row: pickle.load(open(p, "rb")) for row, p in SIGMA_PRODUCT.items()}

sns.set_theme(context="talk", style="whitegrid")
plt.rcParams.update({"axes.edgecolor": "0.2", "axes.linewidth": 0.8,
                     "font.family": "DejaVu Sans", "legend.frameon": False})
palette = sns.color_palette("husl", 6)

fig, axes = plt.subplots(2, 6, figsize=(4.1 * 6, 6.2), sharex=True)

for r, (prefix, flavor, row_probe, ylabel) in enumerate(ROWS):
    product = sigma_products[row_probe]
    # common y-range per row so the bin-to-bin shape comparison is honest
    lo, hi = [], []
    cells = []
    for i in TOM_BINS:
        sp = cls[f"{prefix}{i}"]
        leff = np.asarray(sp["leff"], dtype=float)
        d = np.asarray(sp["cl"], dtype=float)               # BLINDED central value
        bbl = np.asarray(sp["Bbl"], dtype=float)
        sig = np.sqrt(np.diag(np.asarray(            # blind-independent covariance
            product["spectra"][f"bin{i + 1}"]["cov"], dtype=float)))
        t = windowed_fiducial(theory, flavor, i + 1, bbl)
        cells.append((leff, d, sig, t))
        vals = np.concatenate([leff * d + leff * sig, leff * d - leff * sig, leff * t])
        vals = vals[np.isfinite(vals)]
        lo.append(np.nanmin(vals)); hi.append(np.nanmax(vals))
    ymin, ymax = min(lo), max(hi)
    pad = 0.08 * (ymax - ymin)

    for i in TOM_BINS:
        ax = axes[r, i]
        leff, d, sig, t = cells[i]
        color = palette[i]
        ax.axhline(0.0, color="0.6", lw=0.7, zorder=0)
        ax.plot(leff, leff * t, color="0.35", lw=1.6, ls="--", zorder=1,
                label="windowed fiducial" if (r == 0 and i == 0) else None)
        ax.errorbar(leff, leff * d, yerr=leff * sig, fmt="o", ms=5, color=color,
                    ecolor=color, elinewidth=1.2, capsize=2.5, mfc="white", mew=1.4,
                    zorder=3, label="blinded data" if (r == 0 and i == 0) else None)
        ax.set_xscale("log")
        ax.set_xlim(90, 3100)
        ax.set_ylim(ymin - pad, ymax + pad)
        ax.yaxis.get_offset_text().set_size(8)
        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        ax.grid(which="both", alpha=0.15)
        ax.text(0.05, 0.07, f"bin {i + 1}", transform=ax.transAxes, fontsize=11,
                weight="bold", va="bottom", color=color)
        if i == 0:
            ax.set_ylabel(ylabel)
        if r == 1:
            ax.set_xlabel(r"$\ell$")

axes[0, 0].legend(loc="upper right", fontsize=9, framealpha=0.0)
fig.suptitle(
    "Cosmology-shift self-blind — blinded $\\kappa$-cross data vector vs windowed fiducial\n"
    f"commitment sha256: {COMMITMENT[:24]}…",
    y=0.995, fontsize=14.5, weight="bold")
# Row probe labels above each row.
fig.tight_layout(rect=(0, 0, 1, 0.93), h_pad=3.0)
for r, label in enumerate([r"Galaxy clustering $\times$ CMB-$\kappa$  ($\delta_g\times\kappa$)",
                           r"Cosmic shear $\times$ CMB-$\kappa$  ($\gamma\times\kappa$)"]):
    top = max(axes[r, c].get_position().y1 for c in range(6))
    fig.text(0.5, top + 0.008, label, ha="center", va="bottom", fontsize=13, weight="bold")

OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT_PNG, dpi=170, bbox_inches="tight")
print("wrote", OUT_PNG)

# Sidecar: ONLY state + commitment + binning. Nothing cosmological.
json.dump({"state": "BLINDED", "commitment_sha256": COMMITMENT, "binning": "log15"},
          open(OUT_JSON, "w"), indent=2)
print("wrote", OUT_JSON)
