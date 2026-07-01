# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "matplotlib", "seaborn"]
# ///
"""The two CMB-lensing cross-correlation data vectors for the SPT-summer talk.

Status-report figure (blinding-safe): the CMB-only 3×2pt this MoU actually proposes
is the three spectra of the 6×2pt that involve CMB-κ — γ×κ, δ_g×κ, and κκ (the last
folded in at the likelihood level, not plotted here, since we don't measure it
ourselves). Galaxy–galaxy lensing (δ_g×γ) is NOT one of these — it's a standard
Euclid 3×2pt product from the main 3×2pt group, not something new this MoU is
adding, so (Louis's point, 2026-07-01) it doesn't belong on this slide; it dropped
from 3 rows to 2. Both panels: cosmic shear × CMB-κ (γ×κ), galaxy clustering ×
CMB-κ (δ_g×κ), the SPT-3G winter GMV-profile-hardened (gmvbhttprf) estimator, on
the same NaMaster pseudo-Cℓ bandpowers (log15: 15 log bins, ℓ 100–3000).

Error bars are the FULL data-fiducial GAUSSIAN NaMaster covariance (per Louis's
question about what error bars are shown) — the same `covariance_gaussian`
product `make_kappa_constraints.py` reads, sliced to each bin's κ-cross diagonal
BLOCK (not just the per-bandpower Knox diagonal this figure used before
2026-07-01). No amplitude or suptitle is baked into the figure — the slide
headline carries the message, per the deck-wide "no suptitle" convention.

Full-page-width layout: 2 rows (one per cross) × 6 tomographic bins, with a
common y-range per row so the bin-to-bin amplitude comparison is honest. Dropping
the GGL row frees vertical space, so each panel renders bigger than before.

BLINDING.  The two CMB-κ rows can read BLINDED bandpowers: pass
``--blinded-pkl <blinded likelihood-input pkl>`` and the γ×κ / δ_g×κ central
values are overridden by the blinded ``kappa_l{j}`` / ``kappa_g{j}`` spectra
(the Gaussian covariance is blind-independent, unchanged). Without the flag the
figure shows the UNBLINDED data and stamps "PRELIMINARY — UNBLINDED" on the
canvas.

GGL (δ_g×γ) is no longer on the main slide, but the loaders/selection logic and
the backup full 6×6 source(shear)×lens(clustering) matrix (``spt26_ggl_matrix.png``)
are kept — still useful if GGL comes up in Q&A.
"""
import argparse
import pickle
from pathlib import Path

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from _ell_axis import style_ell_axis, fold_yscale, blinding_watermark

ROOT = Path("/leonardo_work/EUHPC_E07_074/cdaley00/cmbx")
# TR1 cross-spectra: SPT GMV κ-crosses (shear/clustering live in separate dirs) and
# the GGL per-bin npz (under the TR1 results-root; the tr1/ rerun κ-crosses share
# the same log15 binning).
SHEAR_KAPPA_PKL = ROOT / "results/tr1/shear_kappa_cross_spectra/shear_lensmc_x_spt_winter_gmvbhttprf.pkl"
GC_KAPPA_PKL = ROOT / "results/tr1/clustering_kappa_cross_spectra/gc_x_spt_winter_gmvbhttprf.pkl"
GGL_DIR = ROOT / "results/tr1_v1p1-v0.1/cross_spectra/individual"
THEORY = ROOT / "results/redshift_tr1/theory_cls.pkl"
# Full data-fiducial Gaussian covariance (same product make_kappa_constraints.py reads) —
# error bars on this slide are this covariance's diagonal, not the per-bin pkl's own Knox cov.
GAUSS_COV_PKL = ROOT / "results/tr1/covariance_gaussian/spt_winter_gmvbhttprf_covariance_gaussian_datafid_input.pkl"
OUT = ROOT / "docs/talks/images/spt26_cross_spectra.png"
OUT_MATRIX = ROOT / "docs/talks/images/spt26_ggl_matrix.png"
# Sealed cosmology-shift talk data vector (TR1 re-seal) — every blinded central value.
BLINDED_PKL = ROOT / "results/tr1/cosmology_shift_talk_datavector/talk_datavector_blinded.pkl"

TOM_BINS = [1, 2, 3, 4, 5, 6]
LMAX = 3000
# GGL slide row = single source(shear)-bin slice over its valid lens(clustering) bins
# (lens ≤ source: source-behind-or-equal). Bin 6 is the highest-combined-detection-S/N
# slice — it is the deepest source (every lens bin 1–5 sits behind it, plus the same-bin
# 6×6), so it both maximises √χ²₀ summed over valid panels AND fills all six columns. The
# per-source-bin S/N table is recomputed + printed at run time below to keep this honest.
GGL_SOURCE = 6

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--blinded-pkl", default=str(BLINDED_PKL),
               help="sealed blinded talk data vector (DEFAULT); blinded central values come "
                    "from its kappa_l*/kappa_g* (κ-cross) and l*_g* (GGL) keys, error bars stay raw")
p.add_argument("--unblinded", action="store_true",
               help="DELIBERATELY render the UNBLINDED data vector (watermarked). Off by default so "
                    "no batch job or recipe re-render can silently leak the amplitude.")
args = p.parse_args()

theory = pickle.load(open(THEORY, "rb"))
shear_kappa = pickle.load(open(SHEAR_KAPPA_PKL, "rb"))
gc_kappa = pickle.load(open(GC_KAPPA_PKL, "rb"))
gauss_cov = pickle.load(open(GAUSS_COV_PKL, "rb"))
gauss_keys = list(gauss_cov["cls"].keys())


def gaussian_cov_block(probe, bin_id):
    """Full per-bin covariance BLOCK (not just the diagonal) from the on-disk full
    data-fiducial Gaussian covariance — same product/indexing as
    make_kappa_constraints.sigma_of. probe='e'→γ×κ (kappa_l), 'g'→δ_g×κ (kappa_g).
    Blind-independent (the covariance never depends on the cosmology-shift blind)."""
    stem = "kappa_l" if probe == "e" else "kappa_g"
    idx = gauss_keys.index(f"{stem}{bin_id - 1}")
    return np.asarray(gauss_cov["cov"][idx][idx], dtype=float)

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
    z = np.load(GGL_DIR / f"wl_lensmc_bin-{src}_x_gc_bin-{lens}.npz",
                allow_pickle=True)
    ells, measured = np.asarray(z["ells"], dtype=float), np.asarray(z["cls"])[0]
    cov = np.asarray(z["cov"], dtype=float)
    if blinded is not None:
        measured = np.asarray(blinded[f"l{src - 1}_g{lens - 1}"]["cl"], dtype=float)
    return ells, measured, cov


def kappa_cross(product, probe, bin_id):
    """(ells, measured Cℓ, cov) for a κ-cross bin; blinded central values if armed.

    probe='e'→γ×κ (kappa_l), 'g'→δ_g×κ (kappa_g). cov is the full data-fiducial
    GAUSSIAN NaMaster covariance block (gaussian_cov_block), not the per-bin pkl's
    own Knox diagonal — Louis's question about the error bars, answered directly.
    """
    spec = product["spectra"][f"bin{bin_id}"]
    ells = np.asarray(spec["ells"], dtype=float)
    measured = np.asarray(spec["cl"], dtype=float)
    cov = gaussian_cov_block(probe, bin_id)
    if blinded is not None:
        key = f"kappa_l{bin_id - 1}" if probe == "e" else f"kappa_g{bin_id - 1}"
        measured = np.asarray(blinded[key]["cl"], dtype=float)
    return ells, measured, cov


def chi0(measured, cov):
    """Blinded detection χ² against the null (no-signal) hypothesis: d·C⁻¹·d.

    Uses the BLINDED central values (the default ``measured``) and the panel's own
    bandpower covariance, over the finite, positive-variance bandpowers. Blind-safe:
    the cosmology-shift moves d, so this reports the *blinded* detection strength,
    not the true amplitude. Returns (χ², n_bandpowers).
    """
    d = np.asarray(measured, dtype=float)
    C = np.asarray(cov, dtype=float)
    good = np.isfinite(d) & np.isfinite(np.diag(C)) & (np.diag(C) > 0)
    d, C = d[good], C[np.ix_(good, good)]
    if d.size == 0:
        return np.nan, 0
    return float(d @ np.linalg.solve(C, d)), int(d.size)


def draw_panel(ax, color, ells, measured, cov, probe_key):
    """One bandpower panel in ℓCℓ: ONE continuous theory curve + measured ± Knox."""
    cl_full = theory_full(probe_key)
    ax.axhline(0.0, color="0.6", lw=0.7, zorder=0)
    ax.plot(ell_full[2:], ell_full[2:] * cl_full[2:], color=color, lw=1.6,
            alpha=0.55, zorder=1, label="Planck-18 theory")
    ax.errorbar(ells, ells * measured, yerr=ells * np.sqrt(np.diag(cov)),
                fmt="o", ms=5, color=color, ecolor=color, elinewidth=1.2,
                capsize=2.5, mfc="white", mew=1.4, zorder=3, label="measured")
    style_ell_axis(ax, 90, 3100)


# --------------------------------------------- GGL source-bin selection (verify)
# For each candidate shear(source) bin s, the valid GGL panels are the lens(clustering)
# bins l ≤ s (source-behind-or-equal). The slide row is a SINGLE source-bin slice, so we
# pick the s whose valid panels carry the largest COMBINED detection S/N = √(Σ χ²₀) — the
# blind-safe null-detection significance, full bandpower covariance per panel. Printed so
# the GGL_SOURCE choice above stays falsifiable; also reports per-panel S/N (combined/√N).
print("\nGGL source-bin selection — combined detection S/N over valid lens bins (l ≤ s):")
ggl_combined = {}
for s in TOM_BINS:
    chi2s = [chi0(*load_ggl(s, l)[1:])[0] for l in TOM_BINS if l <= s]
    combined = float(np.sqrt(np.sum(chi2s)))
    ggl_combined[s] = combined
    print(f"  source {s}: Nvalid={len(chi2s)}  combined S/N={combined:5.1f}  "
          f"per-panel S/N={combined / np.sqrt(len(chi2s)):4.1f}")
best = max(ggl_combined, key=ggl_combined.get)
print(f"  -> highest combined S/N: source {best} ({ggl_combined[best]:.1f}); "
      f"GGL_SOURCE={GGL_SOURCE}" + ("" if best == GGL_SOURCE else "  [DIFFERS — review]"))

# ---------------------------------------------------------------- slide figure
sns.set_theme(context="talk", style="ticks", font_scale=1.3)
plt.rcParams.update({"axes.edgecolor": "0.2", "axes.linewidth": 0.8,
                     "font.family": "DejaVu Sans", "legend.frameon": False,
                     "axes.labelpad": 2.0, "xtick.major.pad": 2.0,
                     "ytick.major.pad": 2.0})
palette = sns.color_palette("husl", len(TOM_BINS))

rows = [
    (r"$\ell C_\ell^{\gamma\kappa}$", "Cosmic shear $\\times$ CMB-$\\kappa$",
     lambda j: kappa_cross(shear_kappa, "e", j), lambda j: ("e", "k", j, 0),
     lambda j: f"bin {j}"),
    (r"$\ell C_\ell^{\delta_g\kappa}$", "Galaxy clustering $\\times$ CMB-$\\kappa$",
     lambda j: kappa_cross(gc_kappa, "g", j), lambda j: ("g", "k", j, 0),
     lambda j: f"bin {j}"),
]
# GGL (δ_g×γ) is no longer a row here (Louis's point — it's a standard Euclid
# 3×2pt product, not part of the CMB-only 3×2pt this MoU proposes); the loaders
# above still feed the backup 6×6 matrix (fig2) below.

# Full-slide layout (~2:1 to fill the 16:9 content area). sharey="row" hides the
# inner y-tick labels so only column 0 carries them — buys the panels real width.
# 2 rows (was 3, pre-2026-07-01) — dropping GGL means each panel gets more height.
fig, axes = plt.subplots(2, len(TOM_BINS), figsize=(4.7 * len(TOM_BINS), 13.0),
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
        ax.text(0.05, 0.07, label_of(j), transform=ax.transAxes, fontsize=16,
                weight="bold", va="bottom", color=palette[c])
        chi2_0, ndof = chi0(measured, cov)
        sn0 = np.sqrt(chi2_0)  # combined detection S/N vs null (full-cov χ²₀ over all bandpowers)
        ax.text(0.95, 0.93, rf"$\mathrm{{S/N}}={sn0:.1f}$", transform=ax.transAxes,
                fontsize=17, ha="right", va="top", weight="bold", color=palette[c])
        print(f"  row{r} {label_of(j):>14s}: chi2_0={chi2_0:7.1f}  ndof={ndof:2d}  "
              f"S/N=sqrt(chi2_0)={sn0:4.1f}")
        if c == 0:
            fold_yscale(ax, ylabel)
        if r == len(rows) - 1:
            ax.set_xlabel(r"$\ell$")

axes[0, 0].legend(loc="upper left", fontsize=13, ncol=1, framealpha=0.0,
                  bbox_to_anchor=(0.0, 0.92), title="SPT-3G GMV-hardened", title_fontsize=13)
sns.despine(fig)
# No suptitle — the slide headline carries the title (deck-wide convention); the
# per-row labels below (Cosmic shear ×.../Galaxy clustering ×...) are NOT a
# duplicate title, they identify which κ-cross each row is.
fig.tight_layout(rect=(0, 0, 1, 0.97), h_pad=2.6, w_pad=0.2)
for r, (_yl, title, *_rest) in enumerate(rows):
    top = max(axes[r, c].get_position().y1 for c in range(len(TOM_BINS)))
    fig.text(0.5, top + 0.010, title, ha="center", va="bottom", fontsize=19,
             weight="bold")
blinding_watermark(fig, blinded is not None)
_bb = axes[1, 2].get_position()
print(f"DATA-AREA per panel: {_bb.width * fig.get_figwidth():.3f} x "
      f"{_bb.height * fig.get_figheight():.3f} in   figsize={tuple(fig.get_size_inches())}")
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
