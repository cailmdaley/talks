# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "matplotlib", "seaborn"]
# ///
"""Cross-survey CMB-lensing consistency surface for the SPT-summer talk.

Status-report figure (blinding-safe): the same Euclid tomographic tracers
crossed against *two independent* CMB-lensing reconstructions — SPT-3G winter
GMV and ACT DR6 — over six tomographic bins and two probe families (cosmic
shear γ×κ, galaxy clustering δ_g×κ). The CMB-κ source plane is common
(z≈1100), so a single fiducial theory curve per panel is the honest reference,
and the two surveys agreeing on it *is* the cross-survey consistency message.

Layout: 2 rows (TOP γ×κ, BOTTOM δ_g×κ) × 6 columns (tomo bins 1..6). Each panel
overlays SPT (red, ○) and ACT (teal, □), ℓ-dodged multiplicatively so the error
bars read cleanly on the log axis, against one continuous fiducial theory curve.

BLINDING. Central values are the SEALED BLINDED bandpowers (cosmology-shift
additive ΔCℓ) from the talk datavector bundle: γ×κ → kappa_l{j}/act_kappa_l{j},
δ_g×κ → kappa_g{j}/act_kappa_g{j} (0-indexed). Error bars come from each
survey's OWN raw on-disk covariance (blind-independent), and the theory curve is
the UNSHIFTED fiducial. NO amplitude, NO per-bin S/N, NO Â annotated anywhere —
this is a blinding-safe consistency status figure.
"""
import pickle
from pathlib import Path

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

ROOT = Path("/leonardo_work/EUHPC_E07_074/cdaley00/cmbx")
BLINDED = ROOT / "results/baseline/cosmology_shift_talk_datavector/talk_datavector_blinded.pkl"
THEORY = ROOT / "results/redshift/theory_cls.pkl"
OUT = ROOT / "docs/talks/images/spt26_cross_survey.png"

# Each survey's OWN raw product (blind-independent covariance), per family.
SURVEYS = {
    "spt": {
        "label": "SPT-3G GMV", "color": "#c0392b", "marker": "o", "dodge": 1.0 - 0.035,
        "prefix": "",  # blinded keys: kappa_l{j}, kappa_g{j}
        "shear_pkl": ROOT / "results/rr2_v2_1_wl_031224-v0.1/cross_spectra/shear_lensmc_x_spt_winter_gmv.pkl",
        "gc_pkl": ROOT / "results/rr2_v2_1_wl_031224-v0.1/cross_spectra/gc_x_spt_winter_gmv.pkl",
    },
    "act": {
        "label": "ACT DR6", "color": "#2a8c8c", "marker": "s", "dodge": 1.0 + 0.035,
        "prefix": "act_",  # blinded keys: act_kappa_l{j}, act_kappa_g{j}
        "shear_pkl": ROOT / "results/act_dr6/shear_kappa_cross_spectra/shear_lensmc_x_act_dr6.pkl",
        "gc_pkl": ROOT / "results/act_dr6/clustering_kappa_cross_spectra/gc_x_act_dr6.pkl",
    },
}

TOM_BINS = [1, 2, 3, 4, 5, 6]
LMAX = 3000

blinded = pickle.load(open(BLINDED, "rb"))["cls"]
theory = pickle.load(open(THEORY, "rb"))
for s in SURVEYS.values():
    s["shear"] = pickle.load(open(s["shear_pkl"], "rb"))
    s["gc"] = pickle.load(open(s["gc_pkl"], "rb"))

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


def survey_point(survey, family, bin_id):
    """(ℓ_eff, blinded Cℓ, σ) for a survey×family×bin.

    Central value: SEALED BLINDED bandpower; σ: sqrt(diag) of the survey's OWN
    raw on-disk covariance (blind-independent). family='e'→γ×κ (kappa_l),
    'g'→δ_g×κ (kappa_g). Blinded bins are 0-indexed → bin_id-1.
    """
    cfg = SURVEYS[survey]
    product = cfg["shear"] if family == "e" else cfg["gc"]
    spec = product["spectra"][f"bin{bin_id}"]
    leff = np.asarray(spec["ells"], dtype=float)
    sigma = np.sqrt(np.diag(np.asarray(spec["cov"], dtype=float)))
    stem = "kappa_l" if family == "e" else "kappa_g"
    cl = np.asarray(blinded[f"{cfg['prefix']}{stem}{bin_id - 1}"]["cl"], dtype=float)
    return leff, cl, sigma


# --------------------------------------------------------------------- figure
sns.set_theme(context="talk", style="whitegrid")
plt.rcParams.update({"axes.edgecolor": "0.2", "axes.linewidth": 0.8,
                     "font.family": "DejaVu Sans", "legend.frameon": False})

families = [
    (r"$\ell C_\ell^{\gamma\kappa}$", "Cosmic shear $\\times$ CMB-$\\kappa$",
     "e", lambda j: ("e", "k", j, 0)),
    (r"$\ell C_\ell^{\delta_g\kappa}$", "Galaxy clustering $\\times$ CMB-$\\kappa$",
     "g", lambda j: ("g", "k", j, 0)),
]

fig, axes = plt.subplots(2, len(TOM_BINS), figsize=(3.3 * len(TOM_BINS), 8.0),
                         sharex=True)

legend_handles = {}
for row, (ylabel, _title, family, key_of) in enumerate(families):
    # Gather the row's data so we can set an honest common y-range per row.
    panels = []
    for bin_id in TOM_BINS:
        cl_full = theory_full(key_of(bin_id))
        pts = {s: survey_point(s, family, bin_id) for s in SURVEYS}
        panels.append((bin_id, cl_full, pts))

    lo, hi = [], []
    for _bin_id, cl_full, pts in panels:
        vals = [ell_full[2:] * cl_full[2:]]
        for leff, cl, sigma in pts.values():
            vals += [leff * cl + leff * sigma, leff * cl - leff * sigma]
        v = np.concatenate(vals); v = v[np.isfinite(v)]
        lo.append(np.nanmin(v)); hi.append(np.nanmax(v))
    ymin, ymax = min(lo), max(hi)
    pad = 0.08 * (ymax - ymin)

    for col, (bin_id, cl_full, pts) in enumerate(panels):
        ax = axes[row, col]
        ax.axhline(0.0, color="0.6", lw=0.7, zorder=0)
        (th,) = ax.plot(ell_full[2:], ell_full[2:] * cl_full[2:], color="0.45",
                        lw=1.2, alpha=0.75, zorder=1)
        legend_handles.setdefault("fiducial theory", th)
        for s, cfg in SURVEYS.items():
            leff, cl, sigma = pts[s]
            ells_d = leff * cfg["dodge"]
            container = ax.errorbar(
                ells_d, leff * cl, yerr=leff * sigma,
                fmt=cfg["marker"], ms=5, color=cfg["color"], ecolor=cfg["color"],
                elinewidth=1.2, capsize=2.5, mfc="white", mew=1.4, zorder=3)
            legend_handles.setdefault(cfg["label"], container)
        ax.set_xscale("log")
        ax.set_xlim(90, 3100)
        ax.set_ylim(ymin - pad, ymax + pad)
        ax.yaxis.get_offset_text().set_size(8)
        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        ax.grid(which="both", alpha=0.15)
        ax.text(0.05, 0.07, f"bin {bin_id}", transform=ax.transAxes, fontsize=11,
                weight="bold", va="bottom", color="0.15")
        if col == 0:
            ax.set_ylabel(ylabel)
        if row == 1:
            ax.set_xlabel(r"$\ell$")

fig.legend(legend_handles.values(), legend_handles.keys(),
           loc="upper center", ncol=len(legend_handles), fontsize=11,
           frameon=False, bbox_to_anchor=(0.5, 0.952))
fig.suptitle(
    "Euclid RR2 $\\times$ CMB lensing — cross-survey tomographic consistency "
    "(SPT-3G GMV vs ACT DR6)",
    y=0.995, fontsize=14, weight="bold",
)
fig.tight_layout(rect=(0, 0, 1, 0.93), h_pad=3.6)
for row, (_yl, title, *_rest) in enumerate(families):
    top = max(axes[row, c].get_position().y1 for c in range(len(TOM_BINS)))
    fig.text(0.5, top + 0.018, title, ha="center", va="bottom",
             fontsize=12, weight="bold")
fig.savefig(OUT, dpi=170, bbox_inches="tight")
print("wrote", OUT)
