# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "matplotlib", "seaborn"]
# ///
"""The three Euclid cross-correlation data vectors for the SPT-summer talk.

Status-report figure (blinding-safe): the analysis measures *three* crosses, all
on the same NaMaster pseudo-Cℓ bandpowers (log15: 15 log bins, ℓ 100–3000) —
cosmic shear × CMB-κ (γ×κ), galaxy clustering × CMB-κ (δ_g×κ), and galaxy–galaxy
lensing (δ_g×γ, Euclid-internal). Each panel shows the measured bandpowers with
Knox error bars and ONE continuous fiducial Planck-18 theory curve. No amplitude
or per-bin S/N is annotated — the message is "three crosses, consistently binned,
tracking theory," carried by the figure.

Full-page-width layout: 3 rows (one per cross) × 6 tomographic bins, with a
common y-range per row so the bin-to-bin amplitude comparison is honest.

BLINDING.  The two CMB-κ rows can read BLINDED bandpowers: pass
``--blinded-pkl <blinded likelihood-input pkl>`` and the γ×κ / δ_g×κ central
values are overridden by the blinded ``kappa_l{j}`` / ``kappa_g{j}`` spectra
(error bars and binning unchanged — the loose blind touches the cross block
only).  GGL (δ_g×γ) is blinded too: its central values come from the bundle's
``l{src}_g{lens}`` keys (raw error bars/cov retained).  Without the flag the
figure shows the UNBLINDED data and stamps "PRELIMINARY — UNBLINDED" on the
canvas.

GGL is a 6×6 source(shear)×lens(clustering) matrix; the slide row shows the
deepest shear source bin (6 — always behind) × each clustering lens bin, parallel
to the κ-cross rows.  Full 6×6 matrix → companion ``spt26_ggl_matrix.png``.
"""
import argparse
import pickle
from pathlib import Path

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

ROOT = Path("/leonardo_work/EUHPC_E07_074/cdaley00/cmbx")
XS = ROOT / "results/rr2_v2_1_wl_031224-v0.1/cross_spectra"
THEORY = ROOT / "results/redshift/theory_cls.pkl"
OUT = ROOT / "docs/talks/images/spt26_cross_spectra.png"
OUT_MATRIX = ROOT / "docs/talks/images/spt26_ggl_matrix.png"
# Sealed cosmology-shift talk data vector — the source of every blinded central value.
BLINDED_PKL = ROOT / "results/baseline/cosmology_shift_talk_datavector/talk_datavector_blinded.pkl"

TOM_BINS = [1, 2, 3, 4, 5, 6]
LMAX = 3000
GGL_SOURCE = 6  # deepest shear bin shown on the slide (always "source behind")

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--blinded-pkl", default=str(BLINDED_PKL),
               help="sealed blinded talk data vector (DEFAULT); blinded central values come "
                    "from its kappa_l*/kappa_g* (κ-cross) and l*_g* (GGL) keys, error bars stay raw")
p.add_argument("--unblinded", action="store_true",
               help="DELIBERATELY render the UNBLINDED data vector (watermarked). Off by default so "
                    "no batch job or recipe re-render can silently leak the amplitude.")
args = p.parse_args()

theory = pickle.load(open(THEORY, "rb"))
shear_kappa = pickle.load(open(XS / "shear_lensmc_x_spt_winter_gmv.pkl", "rb"))
gc_kappa = pickle.load(open(XS / "gc_x_spt_winter_gmv.pkl", "rb"))

# Blinded BY DEFAULT — the talk figure must never silently render the true amplitude.
# kappa_l{j}=γ×κ, kappa_g{j}=δ_g×κ, l{s}_g{l}=GGL (0-indexed). --unblinded is the explicit,
# watermarked opt-out; a missing seal fails loud rather than degrading to unblinded.
blinded = None
if not args.unblinded:
    bl = pickle.load(open(args.blinded_pkl, "rb"))
    blinded = bl["cls"] if "cls" in bl else bl
    print(f"BLINDED: κ-cross + GGL central values from {args.blinded_pkl}")
else:
    print("UNBLINDED: rendering raw data vector with PRELIMINARY watermark (deliberate --unblinded)")

ell_full = np.arange(LMAX + 1)
theory_ells = np.asarray(theory["ells"], dtype=float)


def theory_full(probe_key):
    """Fiducial theory on the integer-ℓ grid (log-log interp; ℓ<2 carries none)."""
    cl = np.asarray(theory["cls"][probe_key], dtype=float)
    out = np.zeros_like(ell_full, dtype=float)
    valid = ell_full >= 2
    th_valid = (theory_ells >= 2) & np.isfinite(cl) & (cl > 0)
    out[valid] = np.exp(np.interp(np.log(ell_full[valid]),
                                  np.log(theory_ells[th_valid]),
                                  np.log(cl[th_valid])))
    return out


def load_ggl(src, lens):
    """δ_g×γ pair: (ells, measured Cℓ, cov) for shear src × clustering lens.

    Blinded when armed: GGL (δ_g×γ) is inside the blinded bundle, keyed
    ``l{src-1}_g{lens-1}``. The blinded central value overrides the raw on-disk
    Cℓ; the error bars/cov stay raw (the blind touches only central values).
    """
    z = np.load(XS / f"individual/wl_lensmc_bin-{src}_x_gc_bin-{lens}.npz",
                allow_pickle=True)
    ells, measured = np.asarray(z["ells"], dtype=float), np.asarray(z["cls"])[0]
    cov = np.asarray(z["cov"], dtype=float)
    if blinded is not None:
        measured = np.asarray(blinded[f"l{src - 1}_g{lens - 1}"]["cl"], dtype=float)
    return ells, measured, cov


def kappa_cross(product, probe, bin_id):
    """(ells, measured Cℓ, cov) for a κ-cross bin; blinded central values if armed.

    probe='e'→γ×κ (kappa_l), 'g'→δ_g×κ (kappa_g).
    """
    spec = product["spectra"][f"bin{bin_id}"]
    ells = np.asarray(spec["ells"], dtype=float)
    measured = np.asarray(spec["cl"], dtype=float)
    cov = np.asarray(spec["cov"], dtype=float)
    if blinded is not None:
        key = f"kappa_l{bin_id - 1}" if probe == "e" else f"kappa_g{bin_id - 1}"
        measured = np.asarray(blinded[key]["cl"], dtype=float)
    return ells, measured, cov


def draw_panel(ax, color, ells, measured, cov, probe_key):
    """One bandpower panel in ℓCℓ: ONE continuous theory curve + measured ± Knox."""
    cl_full = theory_full(probe_key)
    ax.axhline(0.0, color="0.6", lw=0.7, zorder=0)
    ax.plot(ell_full[2:], ell_full[2:] * cl_full[2:], color=color, lw=1.6,
            alpha=0.55, zorder=1, label="Planck-18 theory")
    ax.errorbar(ells, ells * measured, yerr=ells * np.sqrt(np.diag(cov)),
                fmt="o", ms=5, color=color, ecolor=color, elinewidth=1.2,
                capsize=2.5, mfc="white", mew=1.4, zorder=3, label="measured")
    ax.set_xscale("log")
    ax.set_xlim(90, 3100)
    ax.yaxis.get_offset_text().set_size(8)
    ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    ax.grid(which="both", alpha=0.15)


# ---------------------------------------------------------------- slide figure
sns.set_theme(context="talk", style="whitegrid")
plt.rcParams.update({"axes.edgecolor": "0.2", "axes.linewidth": 0.8,
                     "font.family": "DejaVu Sans", "legend.frameon": False})
palette = sns.color_palette("husl", len(TOM_BINS))

rows = [
    (r"$\ell C_\ell^{\gamma\kappa}$", "Cosmic shear $\\times$ CMB-$\\kappa$",
     lambda j: kappa_cross(shear_kappa, "e", j), lambda j: ("e", "k", j, 0),
     lambda j: f"bin {j}"),
    (r"$\ell C_\ell^{\delta_g\kappa}$", "Galaxy clustering $\\times$ CMB-$\\kappa$",
     lambda j: kappa_cross(gc_kappa, "g", j), lambda j: ("g", "k", j, 0),
     lambda j: f"bin {j}"),
    (r"$\ell C_\ell^{\delta_g\gamma}$",
     f"Galaxy–galaxy lensing  $\\delta_g\\times\\gamma$  (clustering bin $\\times$ shear bin {GGL_SOURCE})",
     lambda j: load_ggl(GGL_SOURCE, j), lambda j: ("e", "g", GGL_SOURCE, j),
     lambda j: f"GC{j}$\\times$WL{GGL_SOURCE}"),
]

# Full-slide layout (~2:1 to fill the 16:9 content area). sharey="row" hides the
# inner y-tick labels so only column 0 carries them — buys the panels real width.
fig, axes = plt.subplots(3, len(TOM_BINS), figsize=(4.0 * len(TOM_BINS), 11.6),
                         sharex=True, sharey="row")

# Collect per-row data once so we can (a) draw and (b) fix a common y-range per row.
row_data = []
for getter, probe_of in [(r[2], r[3]) for r in rows]:
    cells = []
    for j in TOM_BINS:
        ells, measured, cov = getter(j)
        cells.append((ells, measured, cov, probe_of(j)))
    row_data.append(cells)

for r, ((ylabel, _title, getter, probe_of, label_of), cells) in enumerate(zip(rows, row_data)):
    # common y-range for the row: span of ℓ·(theory, measured±σ) across all bins.
    lo, hi = [], []
    for ells, measured, cov, pk in cells:
        sig = ells * np.sqrt(np.diag(cov))
        vals = np.concatenate([ells * measured + sig, ells * measured - sig,
                               ell_full[2:] * theory_full(pk)[2:]])
        vals = vals[np.isfinite(vals)]
        lo.append(np.nanmin(vals)); hi.append(np.nanmax(vals))
    ymin, ymax = min(lo), max(hi)
    pad = 0.08 * (ymax - ymin)
    for c, j in enumerate(TOM_BINS):
        ax = axes[r, c]
        ells, measured, cov, pk = cells[c]
        draw_panel(ax, palette[c], ells, measured, cov, pk)
        ax.set_ylim(ymin - pad, ymax + pad)
        ax.text(0.05, 0.07, label_of(j), transform=ax.transAxes, fontsize=11,
                weight="bold", va="bottom", color=palette[c])
        if c == 0:
            ax.set_ylabel(ylabel)
        if r == 2:
            ax.set_xlabel(r"$\ell$")

axes[0, 0].legend(loc="upper left", fontsize=8.5, ncol=1, framealpha=0.0,
                  bbox_to_anchor=(0.0, 0.92))
suptitle = "Euclid RR2 $\\times$ SPT-3G winter GMV — the three cross-correlation data vectors"
fig.suptitle(suptitle, y=1.0, fontsize=15.5, weight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.965), h_pad=3.2)
for r, (_yl, title, *_rest) in enumerate(rows):
    top = max(axes[r, c].get_position().y1 for c in range(len(TOM_BINS)))
    fig.text(0.5, top + 0.012, title, ha="center", va="bottom", fontsize=13,
             weight="bold")
if blinded is None:
    fig.text(0.5, 0.5, "PRELIMINARY — UNBLINDED", ha="center", va="center",
             fontsize=46, color="0.85", weight="bold", rotation=18, zorder=0, alpha=0.5)
fig.savefig(OUT, dpi=170, bbox_inches="tight")
print("wrote", OUT)

# ------------------------------------------------------- full 6×6 GGL backup
fig2, axes2 = plt.subplots(6, 6, figsize=(20, 18), sharex=True)
for ri, src in enumerate(TOM_BINS):            # row = shear (source) bin
    for ci, lens in enumerate(TOM_BINS):       # col = clustering (lens) bin
        ax = axes2[ri, ci]
        ells, measured, cov = load_ggl(src, lens)
        config = ("source behind" if src > lens else
                  "same bin" if src == lens else "source front")
        color = "#c0392b" if src > lens else "#888888" if src == lens else "#2a8c8c"
        draw_panel(ax, color, ells, measured, cov, ("e", "g", src, lens))
        ax.text(0.05, 0.07, f"WL{src}$\\times$GC{lens}\n{config}",
                transform=ax.transAxes, fontsize=8, va="bottom", color=color)
        if ci == 0:
            ax.set_ylabel(f"shear {src}\n" r"$\ell C_\ell^{\delta_g\gamma}$", fontsize=10)
        if ri == 5:
            ax.set_xlabel(r"$\ell$")
        if ri == 0:
            ax.set_title(f"clustering {lens}", fontsize=11)
fig2.suptitle("Galaxy–galaxy lensing $\\delta_g\\times\\gamma$ — full 6$\\times$6 source(shear)$\\times$lens(clustering) matrix\n"
              "red = source behind (highest S/N) | grey = same bin | teal = source front",
              y=0.995, fontsize=15, weight="bold")
fig2.tight_layout(rect=(0, 0, 1, 0.975))
fig2.savefig(OUT_MATRIX, dpi=130, bbox_inches="tight")
print("wrote", OUT_MATRIX)
