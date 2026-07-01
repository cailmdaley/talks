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

Layout: a single tomographic bin (bin 5), the two probe families stacked as wide rows (TOP
γ×κ, BOTTOM δ_g×κ). Each panel overlays SPT (red, ○) and ACT (teal, □), ℓ-dodged
multiplicatively so the two surveys' points read cleanly apart on the log axis,
against one continuous fiducial theory curve.

BLINDING. Central values are the SEALED BLINDED bandpowers (cosmology-shift
additive ΔCℓ) from the talk datavector bundle: γ×κ → kappa_l{j}/act_kappa_l{j},
δ_g×κ → kappa_g{j}/act_kappa_g{j} (0-indexed). Error bars come from each
survey's OWN raw on-disk covariance (blind-independent), and the theory curve is
the UNSHIFTED fiducial. Each panel annotates each survey's blinded detection
S/N = √χ²₀ (χ²₀ = d·C⁻¹·d on the blinded bandpowers + that survey's own full 15×15
covariance — the same blind-safe quantity the data-vector slide shows; mirrors
make_three_cross_spectra.chi0). NO amplitude, NO Â is annotated — this is a
blinding-safe consistency status figure.

CONSISTENCY χ² (blind-safe). Computed per panel (not drawn in the panel — the slide
overlays a plain-language "Naive χ² / considerable overlap" caption instead, see the
.qmd; the number itself is logged to console for the speaker notes) as a reduced-χ²
for the SPT-vs-ACT difference Δ = d_SPT − d_ACT over the 15 log15 bandpowers:
χ²_ν = Δ·Cov_diff⁻¹·Δ / dof, dof = 15. This is blind-safe BY CONSTRUCTION: the
cosmology-shift blind adds the SAME experiment-agnostic theory ΔCℓ to both
surveys' same-bin κ-cross (selfblind_shift.py: κ theory pair is identical for
kappa_* and act_kappa_*; metadata cmb_lensing_experiment_agnostic), so the
common blind cancels in the difference and Δ carries no absolute amplitude. (The
two surveys' bandpower windows Bbl differ at the ~15% level from their different
κ masks, so cancellation is exact only to the window-shape difference acting on a
SMOOTH cosmology-shift ΔCℓ — a second-order, sub-error-bar residual that still
leaks no amplitude.) Cov_diff = Cov(SPT) + Cov(ACT): the shared-Euclid cross
covariance Cov(SPT,ACT) is NOT in the bundle (cov_structure: block_diagonal, the
SPT↔ACT block is identically zero), so it is NEGLECTED. The two κ reconstructions
on the same field are positively correlated → this OVERSTATES the difference
variance → UNDERSTATES any tension; the reduced-χ² is therefore CONSERVATIVE.
"""
import pickle
from pathlib import Path

import numpy as np
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt

from _ell_axis import style_ell_axis, fold_yscale, sn_row, blinding_watermark, legend_right, PANEL_YLIM, SPT_COLOR, ACT_COLOR

ROOT = Path("/leonardo_work/EUHPC_E07_074/cdaley00/cmbx")
# TR1 re-sealed blinded talk data vector (cosmology-shift self-blind on TR1 data).
BLINDED = ROOT / "results/tr1/cosmology_shift_talk_datavector/talk_datavector_blinded.pkl"
THEORY = ROOT / "results/redshift_tr1/theory_cls.pkl"
OUT = ROOT / "docs/talks/images/spt26_cross_survey.png"

# Each survey's OWN raw product (blind-independent covariance), per family — TR1.
SURVEYS = {
    "spt": {
        "label": "SPT-3G GMV", "color": SPT_COLOR, "marker": "o",
        "prefix": "",  # blinded keys: kappa_l{j}, kappa_g{j}
        "shear_pkl": ROOT / "results/tr1/shear_kappa_cross_spectra/shear_lensmc_x_spt_winter_gmvbhttprf.pkl",
        "gc_pkl": ROOT / "results/tr1/clustering_kappa_cross_spectra/gc_x_spt_winter_gmvbhttprf.pkl",
    },
    "act": {
        "label": "ACT DR6", "color": ACT_COLOR, "marker": "s",
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


def cross_survey_chi2(family, bin_id):
    """Blind-safe SPT-vs-ACT reduced-χ² for one probe family at the tomographic bin.

    Δ = d_SPT − d_ACT on the BLINDED bandpowers (common cosmology-shift blind
    cancels — see module docstring); Cov_diff = Cov(SPT) + Cov(ACT) from each
    survey's OWN full 15×15 on-disk covariance (cross-survey covariance neglected
    → conservative). Returns (χ²_ν, PTE, dof)."""
    stem = "kappa_l" if family == "e" else "kappa_g"
    fam_pkl = "shear" if family == "e" else "gc"
    d_spt = np.asarray(blinded[f"kappa_{'l' if family == 'e' else 'g'}{bin_id - 1}"]["cl"], dtype=float)
    d_act = np.asarray(blinded[f"act_{stem}{bin_id - 1}"]["cl"], dtype=float)
    delta = d_spt - d_act
    cov_diff = (np.asarray(SURVEYS["spt"][fam_pkl]["spectra"][f"bin{bin_id}"]["cov"], dtype=float)
                + np.asarray(SURVEYS["act"][fam_pkl]["spectra"][f"bin{bin_id}"]["cov"], dtype=float))
    chi2 = float(delta @ np.linalg.solve(cov_diff, delta))
    dof = delta.size
    return chi2 / dof, float(stats.chi2.sf(chi2, dof)), dof


def chi0(d, cov):
    """Blinded detection χ² vs the no-signal null: d·C⁻¹·d over the finite,
    positive-variance bandpowers. Mirrors make_three_cross_spectra.chi0 so the talk's
    detection S/N (= √χ²₀) is ONE definition. Blind-safe: the cosmology shift moves d,
    so this is the BLINDED detection strength, not the true amplitude. Returns (χ², n)."""
    d = np.asarray(d, dtype=float)
    C = np.asarray(cov, dtype=float)
    good = np.isfinite(d) & np.isfinite(np.diag(C)) & (np.diag(C) > 0)
    d, C = d[good], C[np.ix_(good, good)]
    return (float(d @ np.linalg.solve(C, d)), int(d.size)) if d.size else (np.nan, 0)


def survey_sn(survey, family, bin_id):
    """Blinded detection S/N = √χ²₀ for a survey×family×bin: the survey's BLINDED
    bandpowers against its OWN full 15×15 on-disk covariance (the plotted points)."""
    cfg = SURVEYS[survey]
    product = cfg["shear"] if family == "e" else cfg["gc"]
    cov = np.asarray(product["spectra"][f"bin{bin_id}"]["cov"], dtype=float)
    stem = "kappa_l" if family == "e" else "kappa_g"
    cl = np.asarray(blinded[f"{cfg['prefix']}{stem}{bin_id - 1}"]["cl"], dtype=float)
    return np.sqrt(chi0(cl, cov)[0])


# ----------------------------------------------------------- figure (1 high-z bin)
sns.set_theme(context="talk", style="ticks")
# Bumped fonts for a projected talk slide; wide figsize so the stacked panels fill the
# 16:9 content area (the data area / absolute-points error bars stay large under the text).
plt.rcParams.update({"axes.edgecolor": "0.2", "axes.linewidth": 0.8,
                     "font.family": "DejaVu Sans", "legend.frameon": False,
                     "axes.titlesize": 26, "axes.labelsize": 26,
                     "xtick.labelsize": 22, "ytick.labelsize": 22})

BIN = 5  # tomographic bin shown for the single-bin cross-survey panel
PANELS = [
    ("e", r"$\ell\,C_\ell^{\gamma\kappa}$", r"Cosmic shear $\times$ CMB-$\kappa$   ($\gamma\times\kappa$)",
     lambda j: ("e", "k", j, 0)),
    ("g", r"$\ell\,C_\ell^{\delta_g\kappa}$", r"Galaxy clustering $\times$ CMB-$\kappa$   ($\delta_g\times\kappa$)",
     lambda j: ("g", "k", j, 0)),
]

fig, axes = plt.subplots(2, 1, figsize=(19.0, 11.0), sharex=True)
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
    ax.set_ylim(*PANEL_YLIM[family])   # shared across slides 6/7/8 — see _ell_axis.PANEL_YLIM
    fold_yscale(ax, ylabel, nbins=6)
    ax.set_title(title, pad=8)
    # χ²_ν(SPT−ACT)/PTE is no longer drawn IN the panel — Cail's call: the slide carries
    # only the plain-language takeaway ("Naive χ² — considerable overlap", overlaid on
    # the slide itself, see the .qmd) and the number stays off-figure, in the console
    # log below (and available for the speaker notes if wanted).
    chi2_red, pte, dof = cross_survey_chi2(family, BIN)
    print(f"  {family}-cross naive χ²_ν(SPT-ACT) = {chi2_red:.2f}, PTE = {pte:.2f} ({dof} dof)")
    # Detection S/N as a horizontal, color-matched row along the bottom centre (same
    # treatment as the estimator slide); identity read off the survey colour.
    segments = [("detection S/N", "0.35", "normal")] + [(f"{survey_sn(s, family, BIN):.1f}",
                cfg["color"], "bold") for s, cfg in SURVEYS.items()]
    sn_row(ax, segments, fontsize=23)
    for s, cfg in SURVEYS.items():
        print(f"  {family}-cross {cfg['label']:>12s}: blinded S/N = {survey_sn(s, family, BIN):.2f}")

axes[-1].set_xlabel(r"$\ell$")
# No suptitle — the slide headline carries the title (avoid duplicate titles).
blinding_watermark(fig, blinded=True)   # central values are always the sealed blinded bundle
sns.despine(fig)
fig.tight_layout()
# Legend OUTSIDE the panels (right), in a FIXED margin — see legend_right() docstring:
# keeps this figure's canvas the same size as the neighbouring estimator-robustness /
# kappa-constraints slides regardless of this legend's shorter labels.
legend_right(fig, legend_handles.values(), legend_handles.keys(), title=f"bin {BIN}")
fig.savefig(OUT, dpi=180)
print("wrote", OUT)
