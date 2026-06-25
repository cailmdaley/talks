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

Layout: the highest-S/N bin (6), the two probe families stacked as wide rows (TOP
γ×κ, BOTTOM δ_g×κ). Each panel overlays SPT (red, ○) and ACT (teal, □), ℓ-dodged
multiplicatively so the two surveys' points read cleanly apart on the log axis,
against one continuous fiducial theory curve.

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

from _ell_axis import style_ell_axis, fold_yscale

ROOT = Path("/leonardo_work/EUHPC_E07_074/cdaley00/cmbx")
# TR1 re-sealed blinded talk data vector (cosmology-shift self-blind on TR1 data).
BLINDED = ROOT / "results/tr1/cosmology_shift_talk_datavector/talk_datavector_blinded.pkl"
THEORY = ROOT / "results/redshift_tr1/theory_cls.pkl"
OUT = ROOT / "docs/talks/images/spt26_cross_survey.png"

# Each survey's OWN raw product (blind-independent covariance), per family — TR1.
SURVEYS = {
    "spt": {
        "label": "SPT-3G GMV", "color": "#c0392b", "marker": "o",
        "prefix": "",  # blinded keys: kappa_l{j}, kappa_g{j}
        "shear_pkl": ROOT / "results/tr1/shear_kappa_cross_spectra/shear_lensmc_x_spt_winter_gmv.pkl",
        "gc_pkl": ROOT / "results/tr1/clustering_kappa_cross_spectra/gc_x_spt_winter_gmv.pkl",
    },
    "act": {
        "label": "ACT DR6", "color": "#2a8c8c", "marker": "s",
        "prefix": "act_",  # blinded keys: act_kappa_l{j}, act_kappa_g{j}
        "shear_pkl": ROOT / "results/tr1_act/shear_kappa_cross_spectra/shear_lensmc_x_act_dr6.pkl",
        "gc_pkl": ROOT / "results/tr1_act/clustering_kappa_cross_spectra/gc_x_act_dr6.pkl",
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


def log_dodge(leff, n, frac=0.10):
    """Multiplicative ℓ-dodges so n points span `frac` of the mean log bin spacing."""
    if n < 2:
        return np.array([1.0])
    span = frac * np.mean(np.diff(np.log(np.asarray(leff, dtype=float))))
    return np.exp(np.linspace(-span / 2, span / 2, n))


# ----------------------------------------------------------- figure (1 high-z bin)
sns.set_theme(context="talk", style="ticks")
plt.rcParams.update({"axes.edgecolor": "0.2", "axes.linewidth": 0.8,
                     "font.family": "DejaVu Sans", "legend.frameon": False})

BIN = 6  # highest-S/N, highest-redshift bin
PANELS = [
    ("e", r"$\ell\,C_\ell^{\gamma\kappa}$", r"Cosmic shear $\times$ CMB-$\kappa$   ($\gamma\times\kappa$)",
     lambda j: ("e", "k", j, 0)),
    ("g", r"$\ell\,C_\ell^{\delta_g\kappa}$", r"Galaxy clustering $\times$ CMB-$\kappa$   ($\delta_g\times\kappa$)",
     lambda j: ("g", "k", j, 0)),
]

fig, axes = plt.subplots(2, 1, figsize=(15.0, 10.0), sharex=True)
legend_handles = {}
for ax, (family, ylabel, title, key_of) in zip(axes, PANELS):
    cl_full = theory_full(key_of(BIN))
    ax.axhline(0.0, color="0.6", lw=0.7, zorder=0)
    (th,) = ax.plot(ell_full[2:], ell_full[2:] * cl_full[2:], color="0.45", lw=1.6,
                    alpha=0.8, zorder=1)
    legend_handles.setdefault("fiducial theory", th)
    factors = log_dodge(survey_point("spt", family, BIN)[0], len(SURVEYS))
    for k, (s, cfg) in enumerate(SURVEYS.items()):
        leff, cl, sigma = survey_point(s, family, BIN)
        container = ax.errorbar(leff * factors[k], leff * cl, yerr=leff * sigma,
                                fmt=cfg["marker"], ms=8, color=cfg["color"], ecolor=cfg["color"],
                                elinewidth=1.5, capsize=4, mfc="white", mew=1.7, zorder=3)
        legend_handles.setdefault(cfg["label"], container)
    style_ell_axis(ax, 95, 3050)
    fold_yscale(ax, ylabel)
    ax.set_title(title, fontsize=16, pad=8)

axes[-1].set_xlabel(r"$\ell$")
# No suptitle — the slide headline carries the title (avoid duplicate titles).
sns.despine(fig)
fig.tight_layout()
# Legend OUTSIDE the panels (right), guaranteed clear of every bandpower (no-overlap requirement).
fig.legend(legend_handles.values(), legend_handles.keys(), loc="center left",
           bbox_to_anchor=(1.0, 0.5), frameon=False, fontsize=13,
           title=f"bin {BIN}", title_fontsize=13)
fig.savefig(OUT, dpi=180, bbox_inches="tight")
print("wrote", OUT)
