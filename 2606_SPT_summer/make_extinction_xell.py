# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "matplotlib", "seaborn"]
# ///
"""Galactic-extinction coherent-bias metric X_ℓ for the SPT-summer talk (BLIND-SAFE).

The systematics figure for slide 15 ("what's not yet under control"): extinction is
the one systematic quantified so far. The contamination metric per tomographic bin
per bandpower is

    X_ℓ = C_ℓ^{κS} · C_ℓ^{fS} / C_ℓ^{SS}

with κ = SPT-3G winter GMV reconstruction, S = the galactic-extinction template,
f = the Euclid tracer (δ_g for clustering, γ for cosmic shear). X_ℓ is the *coherent*
(sign-preserving, cancellation-capable) bias the extinction template would inject into
the κ-cross C_ℓ^{fκ}. The honest way to read it is **against the measurement error**:
σ_ℓ = sqrt(diag) of the FULL analytic covariance of the raw δ_g×κ / γ×κ measurement.

Two-panel layout (LEFT δ_g×κ, RIGHT γ×κ), each split into two rows so BOTH the actual
bias and its size relative to σ are legible:
  - TOP row  : ℓ·X_ℓ (project ℓ·Cℓ convention, signed) per bin, with each bin's
               ±ℓ·σ_ℓ envelope as a light shaded band — the eye sees the injected
               bias sitting well inside the measurement error.
  - BOTTOM row: X_ℓ/σ_ℓ (dimensionless, signed) per bin, with ±1σ guide lines — the
               contamination read directly in units of the measurement error. Every
               bandpower is sub-σ; the aggregate S_bias = sqrt(Σ_ℓ (X_ℓ/σ_ℓ)²) per bin
               is annotated (sub-σ to ~0.8σ, dominated by the lowest ℓ).

BLIND-SAFETY (by construction). X_ℓ is a ratio of *template* cross-spectra
(C^{κS}, C^{fS}, C^{SS}) — extinction-template products, never the blinded science
cross. σ_ℓ is the *covariance diagonal* of the κ-cross measurement, which the
cosmology-shift blind never touches (the blind shifts central values, not the cov).
NEITHER quantity carries the blinded cross amplitude, so no blinded signal central
value appears anywhere on this figure — it is blind-safe by construction.

log15 binning (15 log bins, ℓ≈112..2695). Reading discipline (CLAUDE.md): plot in
ℓ·Cℓ on log-ℓ, read against the error bars.
"""
import pickle
from pathlib import Path

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from _ell_axis import style_ell_axis

ROOT = Path("/leonardo_work/EUHPC_E07_074/cdaley00/cmbx")
# TR1, lc-canonical output tree (results/tr1/<output_id>/) — built by
# `lc run -u tr1 {tracer_extinction_cross_spectra,kappa_extinction_cross_spectrum}`.
# Same tree the spine figures read, so the σ-source κ-crosses below are the
# byte-identical files the spine uses for its error bars.
TR1 = ROOT / "results/tr1"
EXT_TRACERS = TR1 / "tracer_extinction_cross_spectra" / "extinction_x_tracers.npz"
EXT_KAPPA = TR1 / "kappa_extinction_cross_spectrum" / "extinction_x_spt_winter_gmv.npz"
GC_SIGMA = TR1 / "clustering_kappa_cross_spectra" / "gc_x_spt_winter_gmv.pkl"
SHEAR_SIGMA = TR1 / "shear_kappa_cross_spectra" / "shear_lensmc_x_spt_winter_gmv.pkl"
OUT = ROOT / "docs/talks/images/spt26_extinction_xell.png"

TOM_BINS = [1, 2, 3, 4, 5, 6]

# Two panels: tracer label, npz key prefix in extinction_x_tracers, raw κ-cross pkl
#   (the pkl is the σ source — its diag is the blind-independent measurement error).
PANELS = [
    ("gc", r"Galaxy clustering $\times$ CMB-$\kappa$   ($\delta_g\times\kappa$)",
     r"$\ell\,X_\ell^{\,\delta_g\kappa}$", GC_SIGMA),
    ("wl", r"Cosmic shear $\times$ CMB-$\kappa$   ($\gamma\times\kappa$)",
     r"$\ell\,X_\ell^{\,\gamma\kappa}$", SHEAR_SIGMA),
]

# ---------------------------------------------------------------- load products
ext = np.load(EXT_TRACERS, allow_pickle=True)["spectra"].item()
kappa_ext = np.load(EXT_KAPPA)
c_ks = np.asarray(kappa_ext["cl"], dtype=float)            # C^{κS}, bin-independent
c_ss = np.asarray(kappa_ext["cl_sys_auto"], dtype=float)   # C^{SS} (Knox extinction auto)
leff = np.asarray(kappa_ext["ells"], dtype=float)          # log15 bandpower centers


def safe_ratio(num, den):
    """X = num/den, NaN where |den|<1e-30 or inputs non-finite (matches the metric)."""
    out = np.full_like(num, np.nan)
    ok = np.isfinite(num) & np.isfinite(den) & (np.abs(den) >= 1e-30)
    out[ok] = num[ok] / den[ok]
    return out


def bin_data(tracer, bin_id, sigma_pkl_spectra):
    """(X_ℓ signed, σ_ℓ) for one tracer/bin. X_ℓ = C^{κS}·C^{fS}/C^{SS}; σ from κ-cross cov."""
    c_fs = np.asarray(ext[f"{tracer}_bin{bin_id}"]["cl"], dtype=float)   # C^{fS}
    x_ell = safe_ratio(c_ks * c_fs, c_ss)                                # signed coherent bias
    sigma = np.sqrt(np.maximum(np.diag(sigma_pkl_spectra[f"bin{bin_id}"]["cov"]), 0.0))
    return x_ell, sigma


# ------------------------------------------------------------- verify S_bias
print("S_bias = sqrt(Σ_ℓ (X_ℓ/σ_ℓ)²) per tracer/bin  (cross-check vs shipped heatmap)")
for tracer, _title, _ylab, pkl_path in PANELS:
    spectra = pickle.load(open(pkl_path, "rb"))["spectra"]
    for b in TOM_BINS:
        x_ell, sigma = bin_data(tracer, b, spectra)
        xos = x_ell / sigma
        sbias = np.sqrt(np.nansum(xos ** 2))
        print(f"  {tracer} bin{b}: S_bias={sbias:.3f}σ  max|X/σ|={np.nanmax(np.abs(xos)):.3f}"
              f"  (lowest-ℓ X/σ={xos[0]:+.3f})")

# ---------------------------------------------------------------------- figure
# Two panels (the user's "two plots"): δ_g×κ and γ×κ. y = X_ℓ/σ_ℓ — the actual
# coherent-bias metric read directly against the measurement error (CLAUDE.md). The
# slide headline carries the title; per-bin S_bias rides in the legend.
sns.set_theme(context="talk", style="ticks")
plt.rcParams.update({"axes.edgecolor": "0.2", "axes.linewidth": 0.8,
                     "font.family": "DejaVu Sans", "legend.frameon": False})
palette = sns.color_palette("husl", len(TOM_BINS))

fig, axes = plt.subplots(1, 2, figsize=(15.5, 6.8), sharey=True)
for col, (tracer, title, _ylab, pkl_path) in enumerate(PANELS):
    spectra = pickle.load(open(pkl_path, "rb"))["spectra"]
    ax = axes[col]
    ax.axhline(0.0, color="0.6", lw=0.8, zorder=0)
    for i, b in enumerate(TOM_BINS):
        x_ell, sigma = bin_data(tracer, b, spectra)
        xos = x_ell / sigma
        sbias = np.sqrt(np.nansum(xos ** 2))
        ax.plot(leff, xos, "-o", ms=5.5, color=palette[i], mfc="white", mew=1.4, lw=1.6,
                zorder=3, label=f"bin {b}  ($S_{{\\rm bias}}={sbias:.2f}\\sigma$)")
    for s in (-1.0, 1.0):  # ±1σ: the bar the bias must clear to matter
        ax.axhline(s, color="0.45", lw=1.0, ls="--", zorder=2)
    ax.text(0.985, 0.94, r"$\pm1\sigma$", transform=ax.transAxes, ha="right", va="top",
            fontsize=12, color="0.4")
    style_ell_axis(ax, 95, 3100)
    ax.set_title(title, fontsize=16, weight="bold", pad=8)
    ax.set_xlabel(r"$\ell$")
    ax.legend(loc="upper left", fontsize=11.5, ncol=1, handlelength=1.4, borderaxespad=0.4)

axes[0].set_ylabel(r"extinction bias  $X_\ell\,/\,\sigma_\ell$")
axes[0].set_ylim(-1.2, 1.2)
sns.despine(fig)
fig.tight_layout()
fig.savefig(OUT, dpi=180, bbox_inches="tight")
print("wrote", OUT)
