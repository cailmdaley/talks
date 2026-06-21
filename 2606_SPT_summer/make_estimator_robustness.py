# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "matplotlib", "seaborn"]
# ///
"""Robustness to the SPT-3G lensing estimator — one high-z bin, the two κ-crosses.

Single tomographic bin (the highest-S/N, highest-redshift bin 6), two panels — the
two CMB-lensing crosses: cosmic shear × CMB-κ (γ×κ) and galaxy clustering × CMB-κ
(δ_g×κ). Each panel overlays the four SPT-3G reconstruction estimators — GMV
(baseline), PP (polarization-only), GMVbhTTprf and TTbhTTprf (bias + profile-
hardened, foreground-clean) — so the eye reads their agreement directly: the
bandpowers sit on top of each other → estimator-robust. log15 binning (15 log
bins, ℓ≈112–2695).

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

ROOT = Path("/leonardo_work/EUHPC_E07_074/cdaley00/cmbx")
XS = ROOT / "results/rr2_v2_1_wl_031224-v0.1/cross_spectra"
BLINDED_PKL = ROOT / "results/baseline/cosmology_shift_talk_datavector/talk_datavector_blinded.pkl"
UNBLINDED_PKL = ROOT / "results/baseline/blinding/talk_datavector_unblinded.pkl"
OUT = ROOT / "docs/talks/images/spt26_estimator_robustness.png"

BIN = 6
ESTIMATORS = [  # (key, label, color)
    ("gmv", "GMV (baseline)", "#222222"),
    ("pp", "PP (pol-only)", "#2a7fb8"),
    ("gmvbhttprf", "GMVbhTTprf", "#c0392b"),
    ("ttbhttprf", "TTbhTTprf", "#1b9e77"),
]
# (panel prefix, blind-key probe, title)
PANELS = [
    ("shear_lensmc", "e", r"Cosmic shear $\times$ CMB-$\kappa$   ($\gamma\times\kappa$)"),
    ("gc", "g", r"Galaxy clustering $\times$ CMB-$\kappa$   ($\delta_g\times\kappa$)"),
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


def est_bin(prefix, est, probe, bin_id):
    """(ells, blinded Cℓ, σ) for one estimator's cross-spectrum at the tomographic bin."""
    spec = pickle.load(open(XS / f"{prefix}_x_spt_est_{est}.pkl", "rb"))["spectra"][f"bin{bin_id}"]
    ells = np.asarray(spec["ells"], dtype=float)
    cl = np.asarray(spec["cl"], dtype=float)
    if probe in delta:
        cl = cl + delta[probe]                     # same cosmology shift for every estimator
    return ells, cl, np.sqrt(np.diag(np.asarray(spec["cov"], dtype=float)))


def draw_estimators(ax, prefix, probe):
    """Overlay the four estimators' bandpowers (ℓCℓ), dodged, for the high-z bin."""
    dodge = np.linspace(-0.018, 0.018, len(ESTIMATORS))
    for (est, label, color), d in zip(ESTIMATORS, dodge):
        ells, cl, sig = est_bin(prefix, est, probe, BIN)
        ax.errorbar(ells * (1 + d), ells * cl, yerr=ells * sig, fmt="o", ms=6, color=color,
                    ecolor=color, elinewidth=1.3, capsize=3,
                    mfc=("white" if est != "gmv" else color), mew=1.4, label=label, zorder=3)
    ax.axhline(0.0, color="0.6", lw=0.7, zorder=0)
    ax.set_xscale("log")
    ax.set_xlim(95, 3050)
    ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    ax.yaxis.get_offset_text().set_size(10)
    ax.grid(which="both", alpha=0.15)
    ax.set_xlabel(r"$\ell$")


# --------------------------------------------------------------------- figure
sns.set_theme(context="talk", style="whitegrid")
plt.rcParams.update({"axes.edgecolor": "0.2", "axes.linewidth": 0.8,
                     "font.family": "DejaVu Sans", "legend.frameon": False})

fig, axes = plt.subplots(1, 2, figsize=(15.5, 7.0))
for ax, (prefix, probe, title) in zip(axes, PANELS):
    draw_estimators(ax, prefix, probe)
    ax.set_title(title, fontsize=16, pad=8)
    ax.set_ylabel(r"$\ell\,C_\ell$")
axes[0].legend(loc="upper right", fontsize=12.5, title=f"bin {BIN}", title_fontsize=12.5)

# No suptitle — the slide headline carries the title (avoid duplicate titles).
if not delta:
    fig.text(0.5, 0.5, "PRELIMINARY — UNBLINDED", ha="center", va="center",
             fontsize=52, color="0.85", weight="bold", rotation=18, zorder=0, alpha=0.5)
fig.tight_layout()
fig.savefig(OUT, dpi=180, bbox_inches="tight")
print("wrote", OUT)
