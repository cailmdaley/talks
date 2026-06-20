# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "matplotlib", "seaborn"]
# ///
"""The three Euclid cross-correlation data vectors for the SPT-summer talk.

Status-report figure (blinding-safe): the analysis measures *three* crosses, all
on the same NaMaster pseudo-Cℓ bandpowers — galaxy–galaxy lensing (δ_g×γ,
Euclid-internal) and the two CMB-lensing crosses (δ_g×κ, γ×κ). Each panel shows
the measured bandpowers with Knox error bars, the fiducial Planck-18 theory
windowed through the *same* bandpower windows (horizontal ticks), and the
continuous theory curve. **No amplitude or per-bin S/N is annotated** — the
detection/amplitude arc is blinded and dropped from this talk; the message is
"three crosses, consistently binned, tracking theory," carried by the figure.

GGL is a 6×6 source(shear)×lens(clustering) matrix, not a single-field cross. The
broad Euclid n(z) overlap means theory is non-zero for every pair (no clean
geometric null); src>lens ("source behind") is the highest-S/N subset. The slide
figure shows the deepest shear source bin (bin 6 — always behind) crossed with
each clustering lens bin, one clean spectrum per panel, parallel to the κ-cross
rows. The full 6×6 matrix is the companion `spt26_ggl_matrix.png`; the amplitude
fit (reported off-slide) uses all 36 pairs.
"""
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

TOM_BINS = [1, 2, 3, 4, 5, 6]
LMAX = 3000
GGL_SOURCE = 6  # deepest shear bin shown on the slide (always "source behind")

theory = pickle.load(open(THEORY, "rb"))
shear_kappa = pickle.load(open(XS / "shear_lensmc_x_spt_winter_gmv.pkl", "rb"))
gc_kappa = pickle.load(open(XS / "gc_x_spt_winter_gmv.pkl", "rb"))

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


def bin_theory(bpws, cl_full):
    """Window full-ℓ theory through the signal bandpower windows (out 0, in 0)."""
    return np.asarray(bpws)[0, :, 0, :] @ cl_full


def load_ggl(src, lens):
    """δ_g×γ pair: (ells, measured Cℓ, cov, binned theory) for shear src × clustering lens."""
    z = np.load(XS / f"individual/wl_lensmc_bin-{src}_x_gc_bin-{lens}.npz",
                allow_pickle=True)
    ells = np.asarray(z["ells"], dtype=float)
    measured = np.asarray(z["cls"])[0]                     # signal leg E×δ
    cov = np.asarray(z["cov"], dtype=float)
    binned = bin_theory(z["bpws"], theory_full(("e", "g", src, lens)))
    return ells, measured, cov, binned


def kappa_cross(product, probe, bin_id):
    spec = product["spectra"][f"bin{bin_id}"]
    ells = np.asarray(spec["ells"], dtype=float)
    measured = np.asarray(spec["cl"], dtype=float)
    cov = np.asarray(spec["cov"], dtype=float)
    binned = bin_theory(spec["bpws"], theory_full((probe, "k", bin_id, 0)))
    return ells, measured, cov, binned


def draw_panel(ax, color, ells, measured, cov, binned, probe_key):
    """One bandpower panel in ℓCℓ: theory curve + windowed theory + measured ± Knox."""
    cl_full = theory_full(probe_key)
    ax.axhline(0.0, color="0.6", lw=0.7, zorder=0)
    ax.plot(ell_full[2:], ell_full[2:] * cl_full[2:], color=color, lw=1.2,
            alpha=0.45, zorder=1, label="theory")
    ax.plot(ells, ells * binned, marker="_", ls="none", ms=11, mew=1.6,
            color=color, alpha=0.9, zorder=2, label="theory (binned)")
    ax.errorbar(ells, ells * measured, yerr=ells * np.sqrt(np.diag(cov)),
                fmt="o", ms=4.5, color=color, ecolor=color, elinewidth=1.1,
                capsize=2, mfc="white", mew=1.3, zorder=3, label="measured")
    ax.set_xscale("log")
    ax.set_xlim(60, 2900)
    ax.yaxis.get_offset_text().set_size(7.5)
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

fig, axes = plt.subplots(3, len(TOM_BINS), figsize=(3.05 * len(TOM_BINS), 10.6),
                         sharex=True)
for r, (ylabel, _title, getter, probe_of, label_of) in enumerate(rows):
    for c, j in enumerate(TOM_BINS):
        ax = axes[r, c]
        color = palette[c]
        ells, measured, cov, binned = getter(j)
        draw_panel(ax, color, ells, measured, cov, binned, probe_of(j))
        ax.text(0.05, 0.07, label_of(j), transform=ax.transAxes, fontsize=10,
                weight="bold", va="bottom", color=color)
        if c == 0:
            ax.set_ylabel(ylabel)
        if r == 2:
            ax.set_xlabel(r"$\ell$")

axes[0, 0].legend(loc="upper left", fontsize=7.5, ncol=1, framealpha=0.0,
                  bbox_to_anchor=(0.0, 0.9))
fig.suptitle("Euclid RR2 $\\times$ SPT-3G winter GMV — the three cross-correlation data vectors",
             y=1.0, fontsize=14.5, weight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.97), h_pad=3.6)
for r, (_yl, title, *_rest) in enumerate(rows):
    top = max(axes[r, c].get_position().y1 for c in range(len(TOM_BINS)))
    fig.text(0.5, top + 0.013, title, ha="center", va="bottom", fontsize=12,
             weight="bold")
fig.savefig(OUT, dpi=170, bbox_inches="tight")
print("wrote", OUT)

# ------------------------------------------------------- full 6×6 GGL backup
fig2, axes2 = plt.subplots(6, 6, figsize=(20, 18), sharex=True)
for ri, src in enumerate(TOM_BINS):            # row = shear (source) bin
    for ci, lens in enumerate(TOM_BINS):       # col = clustering (lens) bin
        ax = axes2[ri, ci]
        ells, measured, cov, binned = load_ggl(src, lens)
        config = ("source behind" if src > lens else
                  "same bin" if src == lens else "source front")
        color = "#c0392b" if src > lens else "#888888" if src == lens else "#2a8c8c"
        draw_panel(ax, color, ells, measured, cov, binned, ("e", "g", src, lens))
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
