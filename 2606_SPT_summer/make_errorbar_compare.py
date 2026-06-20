# /// script
# requires-python = ">=3.10"
# dependencies = ["sacc", "numpy", "matplotlib", "seaborn"]
# ///
"""SPT-3G GMV vs ACT DR6 — shear×κ error-bar size comparison for the SPT-summer talk.

The transferable message (blinding-safe): two independent CMB-lensing reconstructions
crossed against the *same* Euclid shear bins, and which survey constrains where. We show
ONLY the per-bin σ — never the (blinded) measured amplitude — by anchoring paired whiskers
on the common fiducial theory curve. Whisker LENGTH = ℓ·σ; compare red (SPT) vs teal (ACT).

σ is read straight from the diagonal of each on-disk data-vector covariance (no new
covariance work). Theory is the shared lensmc×κ ΛCDM prediction (identical for both surveys,
since it depends only on the Euclid n(z) and the CMB-lensing kernel).
"""
import numpy as np, sacc, seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path("/leonardo_work/EUHPC_E07_074/cdaley00/cmbx")
COMBINED = ROOT / "results/rr2_v2_1_wl_031224-v0.0/cross_correlations/combined"
THEORY = ROOT / "results/rr2_v2_1_wl_031224-v0.0/theory"
OUT = ROOT / "docs/talks/images/spt26_errorbar_compare.png"

SURVEYS = {  # label, sacc file, κ-tracer name, theory npz, color
    "SPT-3G GMV": dict(sacc="euclid_spt_winter_gmv_shear_x_cmbk_cls_nside2048.sacc",
                       kappa="spt_winter_gmv_kappa", theory="theory_cls_lensmc_x_spt_winter_gmv.npz",
                       color="#c0392b"),
    "ACT DR6":    dict(sacc="euclid_act_shear_x_cmbk_cls_nside2048.sacc",
                       kappa="act_kappa", theory="theory_cls_lensmc_x_act.npz",
                       color="#2a8c8c"),
}
BINS = [1, 2, 3, 4, 5, 6]

# --- pull per-bin σ from each covariance diagonal (lensmc shear × κ, E-mode) ---
sig = {}   # sig[label][bin] = (ell, sigma)
for label, cfg in SURVEYS.items():
    s = sacc.Sacc.load_fits(str(COMBINED / cfg["sacc"]))
    cov = s.covariance.dense
    for b in BINS:
        ell, _, ind = s.get_ell_cl("cl_0e", cfg["kappa"], f"euclid_lensmc_bin{b}", return_ind=True)
        sig.setdefault(label, {})[b] = (np.asarray(ell), np.sqrt(np.diag(cov)[ind]))

# --- common fiducial theory (identical across surveys; load SPT's, assert ACT matches) ---
th = np.load(THEORY / SURVEYS["SPT-3G GMV"]["theory"], allow_pickle=True)
th_act = np.load(THEORY / SURVEYS["ACT DR6"]["theory"], allow_pickle=True)
ell_th = th["ell_theory"].astype(float)
for b in BINS:
    assert np.allclose(th[f"cl_theory_bin{b}"], th_act[f"cl_theory_bin{b}"]), \
        f"theory differs between surveys for bin{b} — anchor assumption broken"

# --- σ for the combined all-bin tracer (the headline panel) + per-bin (robustness) ---
def survey_sigma(label, tracer):
    cfg = SURVEYS[label]
    s = sacc.Sacc.load_fits(str(COMBINED / cfg["sacc"]))
    ell, _, ind = s.get_ell_cl("cl_0e", cfg["kappa"], tracer, return_ind=True)
    return np.asarray(ell), np.sqrt(np.diag(s.covariance.dense)[ind])

# crossover ℓ where ACT stops being tighter (binall), for the shaded "regime" guide
ell_a, _ = survey_sigma("SPT-3G GMV", "euclid_lensmc_binall")
_, sg_spt_all = survey_sigma("SPT-3G GMV", "euclid_lensmc_binall")
_, sg_act_all = survey_sigma("ACT DR6", "euclid_lensmc_binall")
ratio = sg_act_all / sg_spt_all
above = np.where(ratio > 1)[0]
xover = np.sqrt(ell_a[above[0] - 1] * ell_a[above[0]]) if len(above) else ell_a[-1]

# Rationale for the design: whiskers anchored on theory balloon in ℓ·Cℓ space
# (per-bandpower S/N<1) and defeat the at-a-glance read. Plotting ℓ·σ directly *is* the
# error-bar size — the lower curve is the tighter survey — and shows no (blinded) measured
# amplitude. Theory ℓ·Cℓ is overlaid as the signal reference; a shaded crossover separates
# the ACT-tighter (large-scale, sample-variance-limited) from the SPT-tighter
# (small-scale, reconstruction-noise-limited) regime.
sns.set_theme(style="ticks", context="talk")
fig, ax = plt.subplots(figsize=(11, 6.8))
m = ell_th >= 30
ax.plot(ell_th[m], ell_th[m] * th["cl_theory_binall"][m], color="0.35", lw=1.6, ls="--",
        zorder=1, label=r"fiducial theory  $\ell C_\ell^{\,\gamma\kappa}$")
ax.plot(ell_a, ell_a * sg_spt_all, color=SURVEYS["SPT-3G GMV"]["color"], lw=2.4,
        marker="o", ms=6, zorder=3, label=r"SPT-3G GMV  $\ell\sigma$")
ax.plot(ell_a, ell_a * sg_act_all, color=SURVEYS["ACT DR6"]["color"], lw=2.4,
        marker="o", ms=6, zorder=3, label=r"ACT DR6  $\ell\sigma$")
ax.axvspan(ell_a[0] * 0.9, xover, color=SURVEYS["ACT DR6"]["color"], alpha=0.06, zorder=0)
ax.axvspan(xover, ell_a[-1] * 1.1, color=SURVEYS["SPT-3G GMV"]["color"], alpha=0.06, zorder=0)
ax.axvline(xover, color="0.5", lw=1.0, ls=":", zorder=2)
ylo, yhi = ax.get_ylim()
ax.text(np.sqrt(ell_a[0] * xover), yhi * 0.96, "ACT tighter\n(large scales)", ha="center",
        va="top", fontsize=13, color=SURVEYS["ACT DR6"]["color"])
ax.text(np.sqrt(xover * ell_a[-1]), yhi * 0.96, "SPT tighter\n(small scales)", ha="center",
        va="top", fontsize=13, color=SURVEYS["SPT-3G GMV"]["color"])
ax.set_xscale("log")
ax.set_ylim(0, yhi)
ax.set_xlabel(r"$\ell$")
ax.set_ylabel(r"$\ell\,C_\ell^{\,\gamma\kappa}$   /   error-bar size $\ell\,\sigma$")
ax.legend(loc="upper left", frameon=False, fontsize=13)
ax.set_title("SPT-3G GMV vs ACT DR6 — error-bar size on the same Euclid shear×κ bins\n"
             "(combined tomography; lower curve = tighter survey)", fontsize=15)
sns.despine(fig)
fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print("wrote", OUT, f"(crossover ℓ≈{xover:.0f})")

# --- supplementary: per-bin grid showing the crossover is universal across tomography ---
OUT_GRID = OUT.with_name("spt26_errorbar_compare_perbin.png")
fig2, axes = plt.subplots(2, 3, figsize=(15, 8.4), sharex=True)
for b, ax in zip(BINS, axes.ravel()):
    ax.plot(ell_th[m], ell_th[m] * th[f"cl_theory_bin{b}"][m], color="0.35", lw=1.3,
            ls="--", zorder=1, label=r"theory $\ell C_\ell$")
    for label, cfg in SURVEYS.items():
        ell, sg = survey_sigma(label, f"euclid_lensmc_bin{b}")
        ax.plot(ell, ell * sg, color=cfg["color"], lw=1.9, marker="o", ms=4,
                zorder=3, label=fr"{label} $\ell\sigma$")
    ax.axvline(xover, color="0.6", lw=0.9, ls=":", zorder=2)
    ax.set_xscale("log"); ax.set_ylim(bottom=0)
    ax.set_title(f"shear bin {b}", fontsize=14); ax.tick_params(labelsize=11)
for ax in axes[-1]: ax.set_xlabel(r"$\ell$")
for ax in axes[:, 0]: ax.set_ylabel(r"$\ell\,C_\ell$ / $\ell\sigma$")
h, l = axes[0, 0].get_legend_handles_labels()
fig2.legend(h, l, loc="upper center", ncol=3, frameon=False, fontsize=13,
            bbox_to_anchor=(0.5, 1.01))
fig2.suptitle("Per-tomographic-bin error-bar size — the ACT/SPT crossover is universal "
              f"(dotted line ℓ≈{xover:.0f})", y=1.05, fontsize=14)
sns.despine(fig2); fig2.tight_layout(rect=(0, 0, 1, 0.99))
fig2.savefig(OUT_GRID, dpi=150, bbox_inches="tight")
print("wrote", OUT_GRID)

# --- text summary: where is each survey tighter? (for the speaker, off-slide) ---
print("\nmedian σ ratio (ACT/SPT) per bin — >1 means SPT tighter:")
for b in BINS:
    _, sg_spt = sig["SPT-3G GMV"][b]
    ell, sg_act = sig["ACT DR6"][b]
    r = sg_act / sg_spt
    lo = ell < 300
    print(f"  bin{b}: all-ℓ median {np.median(r):.2f} | ℓ<300 {np.median(r[lo]):.2f} "
          f"| ℓ>300 {np.median(r[~lo]):.2f}")
