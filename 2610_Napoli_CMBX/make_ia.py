"""Intrinsic alignments in the CMB-lensing crosses, for the Napoli CMBX talk.

Left: what NLA intrinsic alignments do to the lens ratio mu_i, from noiseless
injections through the exact estimator (results/scratch/napoli/lens_ratio_response,
response.json: TheoryVector bands at the fiducial plus A_IA, eta_IA = 0, pivot
z = 0.62, fitted with IA-free templates).
Right: the profile Delta chi^2(A_IA) of the gamma-delta / kappa-delta items alone
(results/scratch/napoli/lens_ratio_ia/ia_profile_<variant>.json: one shared mu, free
beta_j, NLA templates), for the four data variants, against the A_IA of the joint
fit to the full blinded data vector with cosmology and lens n(z) widths free
(results/scratch/napoli/ia_nz_fit, model M3, 0.42 +- 0.28).

Output: images/napoli_ia.png, 2x the figure layout's body less a .source line
(3424 x 1446 px).  Run in the cmbx container: app python make_ia.py
"""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_blind_rehearsal import setup_font  # noqa: E402

SCR = "/leonardo_work/EUHPC_E07_074/cdaley00/cmbx/results/scratch/napoli"
OUT = os.path.join(HERE, "..", "images", "napoli_ia.png")
INK, MUTED, RULE = "#111418", "#535B67", "#C6CEDA"
COBALT, TEAL, OCHRE = "#2E417C", "#1D6C78", "#9C7414"
GREY = "#A7AFBB"
BAND = "#D6DEEA"
VAR = {"lensmc_spt": ("LensMC × SPT-3G", OCHRE, 3.0), "lensmc_act": ("LensMC × ACT DR6", GREY, 1.8),
       "metacal_spt": ("MetaCal × SPT-3G", GREY, 1.8), "metacal_act": ("MetaCal × ACT DR6", GREY, 1.8)}
FULL = (0.42, 0.28)      # ia_nz_fit validated|free|M3
TEMPLATE_A = 0.6
DPI = 200
TICK, LABEL = 21, 23


def main():
    setup_font()
    resp = json.load(open(f"{SCR}/lens_ratio_response/response.json"))
    meanz = json.load(open(f"{SCR}/crosses/arrays/mean_z.json"))
    zs = [meanz[f"l{i}"] for i in range(6)]
    prof = {v: json.load(open(f"{SCR}/lens_ratio_ia/ia_profile_{v}.json"))["shared"] for v in VAR}
    plt.rcParams.update({
        "axes.linewidth": 1.4, "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.labelcolor": INK, "xtick.labelsize": TICK, "ytick.labelsize": TICK, "axes.labelsize": LABEL,
        "xtick.major.width": 1.4, "ytick.major.width": 1.4, "xtick.major.size": 7, "ytick.major.size": 7,
        "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": "white", "axes.facecolor": "white",
    })
    fig, (al, ar) = plt.subplots(1, 2, figsize=(3424 / DPI, 1446 / DPI), dpi=DPI,
                                 gridspec_kw=dict(width_ratios=[1, 1.15], wspace=0.24, left=0.07, right=0.985,
                                                  top=0.86, bottom=0.17))
    # left: response of mu_i to IA
    x = np.arange(6)
    al.axhline(1, color=INK, lw=1.4, ls=(0, (5, 4)), zorder=1)
    for key, a, c in (("NLA A_IA = 0.5", 0.5, TEAL), ("NLA A_IA = 1.0", 1.0, COBALT)):
        y = resp[key]["mu_i"]
        al.plot(x, y, color=c, lw=2.6, marker="o", ms=11, mec="white", mew=1.6, zorder=3)
        al.text(0.18, y[0], f"$A_{{\\rm IA}} = {a:g}$", color=c, fontsize=LABEL - 2, ha="left", va="center")
    al.set_xticks(x)
    al.set_xticklabels([f"{i+1}\n{z:.2f}" for i, z in enumerate(zs)])
    al.set_xlim(-0.3, 5.3); al.set_ylim(0.62, 1.04)
    al.set_xlabel("source bin, mean z")
    al.set_ylabel(r"lens ratio $\mu_i$ with IA-free templates")
    al.set_title("IA lowers γδ for sources just behind the lenses", fontsize=LABEL, color=MUTED, loc="left", pad=14)

    # right: profile chi^2
    ar.axvspan(FULL[0] - FULL[1], FULL[0] + FULL[1], color=BAND, lw=0, zorder=0)
    ar.axvline(FULL[0], color=COBALT, lw=2.2, zorder=1)
    for v, (lab, c, lw) in VAR.items():
        g, chi = np.array(prof[v]["grid"]), np.array(prof[v]["chi2"])
        ar.plot(g, chi - chi.min(), color=c, lw=lw, zorder=3 if c == OCHRE else 2)
    ar.plot([], [], color=OCHRE, lw=3, label="lens ratios, LensMC × SPT-3G")
    ar.plot([], [], color=GREY, lw=1.8, label="other three variants")
    import matplotlib.patches as mp
    h, l = ar.get_legend_handles_labels()
    h.append(mp.Patch(facecolor=BAND, edgecolor=COBALT, lw=1.6)); l.append("full 5×2pt fit, ±1σ\n(blinded, cosmology free)")
    ar.axhline(1, color=MUTED, lw=1.0, ls=(0, (2, 3)))
    ar.text(-1.45, 1.06, r"$\Delta\chi^2 = 1$", color=MUTED, fontsize=TICK - 2, ha="left", va="bottom")
    ar.legend(h, l, loc="upper right", fontsize=LABEL - 3, frameon=False, handlelength=1.6)
    ar.set_xlim(-1.5, 4.4); ar.set_ylim(0, 4)
    ar.set_xlabel(r"NLA amplitude $A_{\rm IA}$")
    ar.set_ylabel(r"$\Delta\chi^2$")
    ar.set_title(r"Lens ratios alone: $A_{\rm IA} = 0.05 \pm 0.7$", fontsize=LABEL, color=MUTED, loc="left", pad=14)
    fig.savefig(OUT, dpi=DPI)
    for v in VAR:
        p = prof[v]
        print(f"{v}: A_IA = {p['best']:.2f} +{p['hi']-p['best']:.2f} -{p['best']-p['lo']:.2f}")
    print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
