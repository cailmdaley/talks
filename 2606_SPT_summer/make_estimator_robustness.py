# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "matplotlib", "seaborn"]
# ///
"""Robustness to the SPT-3G lensing estimator — one high-z bin, the two κ-crosses.

Single tomographic bin (the highest-S/N, highest-redshift bin 6), two stacked
panels (top/bottom) — the two CMB-lensing crosses: cosmic shear × CMB-κ (γ×κ) and
galaxy clustering × CMB-κ (δ_g×κ). Each panel overlays three SPT-3G reconstruction
estimators — GMV (baseline), GMV pol-only (PP) and GMV profile-hardened (the bias +
profile-hardened GMVbhTTprf) — over the fiducial theory curve, so the eye reads
their agreement directly: the bandpowers sit on top of each other → estimator-robust.
log15 binning (15 log bins, ℓ≈112–2695).

BLINDING (blinded by default).  The κ-cross amplitude is under the cosmology-shift
self-blind, so the absolute level must not show. We add the SAME cosmology shift
ΔCℓ that blinds the talk data vector to EVERY estimator's bandpowers — ΔCℓ is
purely cosmological (depends on the hidden cosmology + tomo bin + the κ tracer, not
on the estimator), so estimator *agreement* is preserved exactly while the absolute
amplitude is hidden. ΔCℓ = blinded_bundle[kappa_*] − unblinded_twin[kappa_*]; the
twin is a gitignored soft-secret read only at build time, and only blinded
bandpowers reach the PNG. ``--unblinded`` renders the raw amplitude with a
PRELIMINARY watermark (off by default so no re-render can silently leak it).
"""
import argparse
import pickle
from pathlib import Path

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from _ell_axis import style_ell_axis, fold_yscale

ROOT = Path("/leonardo_work/EUHPC_E07_074/cdaley00/cmbx")
# TR1. The per-estimator κ-cross pickles ({prefix}_x_spt_est_{est}.pkl) are written
# to the $RESULTS_ROOT working tree by `lc run -u tr1 {spt,clustering}_estimator_
# datavector_comparison` (only the comparison json/png get copied to the lc-canonical
# results/tr1/<output_id>/ tree). The blind bundle is the re-sealed TR1 talk data
# vector (commitment 852da2ed…) under the lc-canonical results/tr1/ tree.
XS = ROOT / "results/tr1_v1p1-v0.1/cross_spectra"
BLINDED_PKL = ROOT / "results/tr1/cosmology_shift_talk_datavector/talk_datavector_blinded.pkl"
UNBLINDED_PKL = ROOT / "results/tr1/blinding/talk_datavector_unblinded.pkl"
THEORY = ROOT / "results/redshift_tr1/theory_cls.pkl"
OUT = ROOT / "docs/talks/images/spt26_estimator_robustness.png"

BIN = 6
LMAX = 3000
ESTIMATORS = [  # (key, label, color)
    ("gmv", "GMV", "#222222"),
    ("pp", "GMV pol-only", "#2a7fb8"),
    ("gmvbhttprf", "GMV profile-hardened", "#c0392b"),
]
# (panel prefix, blind-key probe, theory key, title)
PANELS = [
    ("shear_lensmc", "e", ("e", "k", BIN, 0),
     r"Cosmic shear $\times$ CMB-$\kappa$   ($\gamma\times\kappa$)"),
    ("gc", "g", ("g", "k", BIN, 0),
     r"Galaxy clustering $\times$ CMB-$\kappa$   ($\delta_g\times\kappa$)"),
]

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--unblinded", action="store_true",
               help="DELIBERATELY render the raw (unblinded) amplitude, watermarked. Off by default.")
args = p.parse_args()

# Cosmology-shift ΔCℓ — blinded by default, identical shift for every estimator.
delta = {}
if not args.unblinded:
    bl = pickle.load(open(BLINDED_PKL, "rb"))["cls"]
    ub = pickle.load(open(UNBLINDED_PKL, "rb"))["cls"]
    for probe in ("e", "g"):
        key = f"kappa_l{BIN - 1}" if probe == "e" else f"kappa_g{BIN - 1}"
        delta[probe] = np.asarray(bl[key]["cl"], dtype=float) - np.asarray(ub[key]["cl"], dtype=float)
    print(f"BLINDED: estimator bandpowers shifted by the cosmology-shift ΔCℓ (bin {BIN})")
else:
    print("UNBLINDED: raw amplitude with PRELIMINARY watermark (deliberate --unblinded)")

# Fiducial theory curve — UNshifted, exactly as the neighbouring cross-survey slide
# draws it. Under the blind the estimator bandpowers sit at a (secret) offset from
# fiducial theory; that offset is hidden by ΔCℓ, so the curve is blind-safe and the
# slide's message is unchanged — three estimators sitting on top of *each other*.
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


def est_bin(prefix, est, probe, bin_id):
    """(ells, blinded Cℓ, σ) for one estimator's cross-spectrum at the tomographic bin."""
    spec = pickle.load(open(XS / f"{prefix}_x_spt_est_{est}.pkl", "rb"))["spectra"][f"bin{bin_id}"]
    ells = np.asarray(spec["ells"], dtype=float)
    cl = np.asarray(spec["cl"], dtype=float)
    if probe in delta:
        cl = cl + delta[probe]                     # same cosmology shift for every estimator
    return ells, cl, np.sqrt(np.diag(np.asarray(spec["cov"], dtype=float)))


def log_dodge(leff, n, frac=0.20):
    """Multiplicative ℓ-dodges so n points span `frac` of the mean log bin spacing."""
    if n < 2:
        return np.array([1.0])
    span = frac * np.mean(np.diff(np.log(np.asarray(leff, dtype=float))))
    return np.exp(np.linspace(-span / 2, span / 2, n))


def draw_estimators(ax, prefix, probe, theory_key):
    """One panel: fiducial theory curve + the estimators' bandpowers (ℓCℓ), dodged."""
    ax.axhline(0.0, color="0.6", lw=0.7, zorder=0)
    cl_full = theory_full(theory_key)
    ax.plot(ell_full[2:], ell_full[2:] * cl_full[2:], color="0.55", lw=1.6, alpha=0.8,
            zorder=1, label="fiducial theory")
    rows = [est_bin(prefix, est, probe, BIN) for est, _, _ in ESTIMATORS]
    factors = log_dodge(rows[0][0], len(ESTIMATORS))   # cluster spans 20% of the bin spacing
    for (est, label, color), (ells, cl, sig), fac in zip(ESTIMATORS, rows, factors):
        ax.errorbar(ells * fac, ells * cl, yerr=ells * sig, fmt="o", ms=6, color=color,
                    ecolor=color, elinewidth=1.3, capsize=3,
                    mfc=("white" if est != "gmv" else color), mew=1.4, label=label, zorder=3)
    style_ell_axis(ax, 95, 3050)
    fold_yscale(ax, r"$\ell\,C_\ell$")


# --------------------------------------------------------------------- figure
sns.set_theme(context="talk", style="ticks")
plt.rcParams.update({"axes.edgecolor": "0.2", "axes.linewidth": 0.8,
                     "font.family": "DejaVu Sans", "legend.frameon": False})

fig, axes = plt.subplots(2, 1, figsize=(15.0, 10.0), sharex=True)
for ax, (prefix, probe, theory_key, title) in zip(axes, PANELS):
    draw_estimators(ax, prefix, probe, theory_key)
    ax.set_title(title, fontsize=16, pad=8)
axes[-1].set_xlabel(r"$\ell$")
sns.despine(fig)

# No suptitle — the slide headline carries the title (avoid duplicate titles).
if not delta:
    fig.text(0.5, 0.5, "PRELIMINARY — UNBLINDED", ha="center", va="center",
             fontsize=52, color="0.85", weight="bold", rotation=18, zorder=0, alpha=0.5)
fig.tight_layout()
# Legend OUTSIDE the panels (right), guaranteed clear of every bandpower (no-overlap requirement).
h, lab = axes[0].get_legend_handles_labels()
fig.legend(h, lab, loc="center left", bbox_to_anchor=(1.0, 0.5), frameon=False,
           fontsize=13, title=f"bin {BIN}", title_fontsize=13)
fig.savefig(OUT, dpi=180, bbox_inches="tight")
print("wrote", OUT)
