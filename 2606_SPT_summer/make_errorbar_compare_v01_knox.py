# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "matplotlib", "seaborn"]
# ///
"""Which κ survey constrains where — ACT DR6 vs SPT-3G GMV error bars, plus GGL.

PARKED ALTERNATIVE — NOT wired into the deck (the slide uses make_errorbar_compare.py,
the v0.0-sacc / FullCovariance / combined-tomography figure with the ℓ≈1350 crossover).
This v0.1-pkl variant reads the Knox-diagonal covariance (the only one the v0.1 ACT
product carries) at a single tomographic bin, which shifts the crossover to ℓ≈250 and
*overstates* SPT's reach to an SPT audience — Knox is the project's companion-only basis
(Full is the headline; see explorations/spt-talk-push/spt-vs-act-errorbar-crossover and
amplitude-claims-tempered). Promote this only if (a) a Full/Gaussian covariance for the
ACT v0.1 cross is built, or (b) Cail accepts stating the crossover on the Knox basis with
that caveat. Adds a GGL panel the v0.0 figure lacks — its main draw.


Blinding-safe "wire" comparison for the SPT-summer talk: for one high-redshift
tomographic bin, three panels (one per cross-correlation), each showing the
fiducial Planck-18 theory curve with the *absolute* per-bandpower error bars
attached at each point.  The central values are THEORY (never the blinded
measurement), so nothing about the amplitude leaks — what you read off is purely
which survey's error bar is smaller where.

 - γ×κ and δ_g×κ: SPT-3G GMV and ACT DR6 error bars overlaid on the same theory
   wire (the κ map is the only thing that differs), so you see directly where each
   survey wins — ACT at large scales (sample-variance regime, wider Euclid
   overlap), SPT at small scales (reconstruction-noise regime, depth/resolution).
 - δ_g×γ (galaxy–galaxy lensing): Euclid×Euclid, no CMB-lensing map, so no
   ACT/SPT split — a single error-bar set that contextualises GGL's precision
   against the κ-crosses and completes the 3×2pt.

All three panels share consistent scientific-notation y-axes; log15 binning
(15 log bins, ℓ 100–3000).  Reads the v0.1 per-spectrum products (same Knox
covariance pipeline for both surveys → a fair σ comparison).
"""
import pickle
from pathlib import Path

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

ROOT = Path("/leonardo_work/EUHPC_E07_074/cdaley00/cmbx")
XS = ROOT / "results/rr2_v2_1_wl_031224-v0.1/cross_spectra"
THEORY = ROOT / "results/redshift/theory_cls.pkl"
OUT = ROOT / "docs/talks/images/spt26_errorbar_compare.png"

BIN = 6          # high-redshift tomographic bin for the κ-crosses
LMAX = 3000

theory = pickle.load(open(THEORY, "rb"))
theory_ells = np.asarray(theory["ells"], dtype=float)
ell_full = np.arange(LMAX + 1)


def theory_cont(probe_key):
    """Continuous fiducial theory on the integer-ℓ grid (log-log interp)."""
    cl = np.asarray(theory["cls"][probe_key], dtype=float)
    out = np.zeros_like(ell_full, dtype=float)
    valid = ell_full >= 2
    th = (theory_ells >= 2) & np.isfinite(cl) & (cl > 0)
    out[valid] = np.exp(np.interp(np.log(ell_full[valid]),
                                  np.log(theory_ells[th]), np.log(cl[th])))
    return out


def kappa_bin(fname, bin_id):
    """(effective ells, σ) for a κ-cross tomographic bin from a per-spectrum pkl."""
    spec = pickle.load(open(XS / fname, "rb"))["spectra"][f"bin{bin_id}"]
    ells = np.asarray(spec["ells"], dtype=float)
    return ells, np.sqrt(np.diag(np.asarray(spec["cov"], dtype=float)))


def ggl_bin(src, lens):
    z = np.load(XS / f"individual/wl_lensmc_bin-{src}_x_gc_bin-{lens}.npz", allow_pickle=True)
    return np.asarray(z["ells"], dtype=float), np.sqrt(np.diag(np.asarray(z["cov"], dtype=float)))


def best_ggl_lens(src):
    """Pick the lens bin giving the strongest src-behind GGL detection S/N."""
    best, best_snr = max(src - 1, 1), -1.0
    for lens in range(1, src):                     # source strictly behind lens
        ells, sig = ggl_bin(src, lens)
        th = np.interp(ells, ell_full, theory_cont(("e", "g", src, lens)))
        snr = np.sqrt(np.nansum((th / sig) ** 2))
        if snr > best_snr:
            best, best_snr = lens, snr
    return best


def wire(ax, ells, theory_key, series, color_map):
    """Theory wire at `ells` with absolute ℓσ error bars per survey (dodged)."""
    th = np.interp(ells, ell_full, theory_cont(theory_key))
    ax.plot(ell_full[2:], ell_full[2:] * theory_cont(theory_key)[2:],
            color="0.35", lw=1.4, alpha=0.7, zorder=1, label="Planck-18 theory")
    dodge = np.linspace(-0.012, 0.012, len(series)) if len(series) > 1 else [0.0]
    for (label, sig), d in zip(series, dodge):
        x = ells * (1 + d)
        ax.errorbar(x, ells * th, yerr=ells * sig, fmt="o", ms=4.5,
                    color=color_map[label], ecolor=color_map[label], elinewidth=1.6,
                    capsize=3, capthick=1.6, mfc="white", mew=1.2, zorder=3, label=label)
    ax.set_xscale("log")
    ax.set_xlim(90, 3100)
    ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    ax.yaxis.get_offset_text().set_size(9)
    ax.grid(which="both", alpha=0.15)


# --------------------------------------------------------------------- figure
sns.set_theme(context="talk", style="whitegrid")
plt.rcParams.update({"axes.edgecolor": "0.2", "axes.linewidth": 0.8,
                     "font.family": "DejaVu Sans", "legend.frameon": False})
C_SPT, C_ACT, C_GGL = "#c0392b", "#2a7fb8", "#6a51a3"
cmap = {"SPT-3G GMV": C_SPT, "ACT DR6": C_ACT, "Euclid GGL": C_GGL}

lens = best_ggl_lens(BIN)
e_s, s_s = kappa_bin("shear_lensmc_x_spt_winter_gmv.pkl", BIN)
e_a, s_a = kappa_bin("shear_lensmc_x_act_dr6.pkl", BIN)
g_s, gs_s = kappa_bin("gc_x_spt_winter_gmv.pkl", BIN)
g_a, gs_a = kappa_bin("gc_x_act_dr6.pkl", BIN)
gg_e, gg_s = ggl_bin(BIN, lens)

fig, axes = plt.subplots(1, 3, figsize=(18.5, 5.6))

wire(axes[0], e_s, ("e", "k", BIN, 0),
     [("SPT-3G GMV", s_s), ("ACT DR6", np.interp(e_s, e_a, s_a))], cmap)
axes[0].set_title(r"Cosmic shear $\times$ CMB-$\kappa$   ($\gamma\times\kappa$)", fontsize=13)
axes[0].set_ylabel(r"$\ell\,C_\ell$")

wire(axes[1], g_s, ("g", "k", BIN, 0),
     [("SPT-3G GMV", gs_s), ("ACT DR6", np.interp(g_s, g_a, gs_a))], cmap)
axes[1].set_title(r"Galaxy clustering $\times$ CMB-$\kappa$   ($\delta_g\times\kappa$)", fontsize=13)

wire(axes[2], gg_e, ("e", "g", BIN, lens), [("Euclid GGL", gg_s)], cmap)
axes[2].set_title(rf"Galaxy–galaxy lensing   ($\delta_g\times\gamma$, shear {BIN}$\times$clustering {lens})", fontsize=12.5)

for ax in axes:
    ax.set_xlabel(r"$\ell$")
    ax.legend(loc="upper right", fontsize=10)
fig.suptitle(f"Which survey constrains where — absolute error bars on the Planck-18 theory wire (tomographic bin {BIN})",
             y=1.0, fontsize=14.5, weight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.95))
fig.savefig(OUT, dpi=175, bbox_inches="tight")
print("wrote", OUT, "| GGL lens =", lens)
