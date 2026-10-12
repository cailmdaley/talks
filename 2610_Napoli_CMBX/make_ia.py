"""Intrinsic alignments and the CMB-lensing crosses, for the Napoli CMBX talk.

Left: how NLA intrinsic alignments enter each spectrum, as the fractional change
(C(A_IA = 1) - C(A_IA = 0)) / C(A_IA = 0) at the ell ~ 350 band, per source bin, for the
shear auto-spectrum (GI + II), shear x galaxy density with the lens bin of the same index
(GI-like), and shear x CMB lensing (I kappa, linear only).
Right: Fisher sigma(A_IA) on the TR1 x SPT-3G setup (validated bands, product Gaussian
covariance, cosmology Omega_m and S8 free, biases, eta_IA, m_i ~ N(0, 0.01), delta-z ~
N(0, 0.02) marginalised), with and without the CMB-lensing crosses.

Both from results/scratch/napoli/ia_kappa (fisher.py: fisher.json, ia_terms.npz), computed
on the fiducial model vector, not on data.

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
INK, MUTED = "#111418", "#535B67"
COBALT, TEAL, OCHRE = "#2E417C", "#1D6C78", "#9C7414"
LIGHT = "#C6CEDA"
DPI = 200
TICK, LABEL = 21, 23
BAND = 5  # ell ~ 350


def main():
    setup_font()
    z = np.load(f"{SCR}/ia_kappa/ia_terms.npz", allow_pickle=True)
    fis = json.load(open(f"{SCR}/ia_kappa/fisher.json"))["combos"]
    meanz = json.load(open(f"{SCR}/crosses/arrays/mean_z.json"))
    zs = [meanz[f"l{i}"] for i in range(6)]
    order = [str(o) for o in z["order"]]
    v0, v1 = z["v0"], z["v1"]

    def frac(k):
        n = order.index(k) * 15 + BAND
        return (v1[n] - v0[n]) / v0[n]

    plt.rcParams.update({
        "axes.linewidth": 1.4, "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.labelcolor": INK, "xtick.labelsize": TICK, "ytick.labelsize": TICK, "axes.labelsize": LABEL,
        "xtick.major.width": 1.4, "ytick.major.width": 1.4, "xtick.major.size": 7, "ytick.major.size": 7,
        "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": "white", "axes.facecolor": "white",
    })
    fig, (al, ar) = plt.subplots(1, 2, figsize=(3424 / DPI, 1446 / DPI), dpi=DPI,
                                 gridspec_kw=dict(width_ratios=[1, 1.05], wspace=0.30, left=0.075, right=0.975,
                                                  top=0.86, bottom=0.17))
    # left: where IA enters
    x = np.arange(6)
    al.axhline(0, color=MUTED, lw=1.2, zorder=1)
    rows = [(r"$\gamma\kappa$: I$\kappa$ only, linear in $A_{\rm IA}$", [f"kappa_l{i}" for i in range(6)], TEAL, 3.4),
            ("γγ: GI + II", [f"l{i}_l{i}" for i in range(6)], COBALT, 2.4),
            ("γδ, same-index lens bin", [f"g{i}_l{i}" for i in range(6)], OCHRE, 2.4)]
    for lab, keys, c, lw in rows:
        y = 100 * np.array([frac(k) for k in keys])
        al.plot(x, y, color=c, lw=lw, marker="o", ms=11, mec="white", mew=1.6, zorder=3, label=lab)
    al.set_xticks(x)
    al.set_xticklabels([f"{i+1}\n{zz:.2f}" for i, zz in enumerate(zs)])
    al.set_xlim(-0.3, 5.3)
    al.set_ylim(-31, 3)
    al.set_xlabel("source bin, mean z")
    al.set_ylabel(r"IA change of $C_\ell$ at $A_{\rm IA}=1$ (%)")
    al.legend(loc="lower right", fontsize=LABEL - 3, frameon=False, handlelength=1.6)
    al.set_title("IA enters γκ differently: one linear term, larger at high z",
                 fontsize=LABEL, color=MUTED, loc="left", pad=14)

    # right: what the kappa crosses buy
    pairs = [("γγ", "gg|m0.01", "+ γκ", "gg+gk|m0.01"),
             ("3×2pt", "3x2pt|m0.01", "+ γκ, δκ", "5x2pt|m0.01")]
    yb = []
    for j, (la, ka, lb, kb) in enumerate(pairs):
        sa, sb = fis[ka]["sigma"]["A_IA"], fis[kb]["sigma"]["A_IA"]
        y0 = 3.2 * (1 - j)
        ar.barh(y0 + 0.55, sa, height=0.95, color=LIGHT, edgecolor=MUTED, lw=1.2)
        ar.barh(y0 - 0.55, sb, height=0.95, color=TEAL, edgecolor=TEAL, lw=1.2)
        ar.text(sa + 0.012, y0 + 0.55, f"{sa:.2f}", va="center", fontsize=TICK, color=INK)
        ar.text(sb + 0.012, y0 - 0.55, f"{sb:.2f}  (−{100 * (1 - sb / sa):.0f} %)", va="center",
                fontsize=TICK, color=TEAL)
        yb += [(y0 + 0.55, la), (y0 - 0.55, lb)]
    ar.set_yticks([p for p, _ in yb], [l for _, l in yb], fontsize=LABEL - 1)
    ar.tick_params(axis="y", length=0, colors=INK)
    ar.spines["left"].set_visible(False)
    ar.set_xlim(0, 0.86)
    ar.set_xlabel(r"Fisher $\sigma(A_{\rm IA})$, TR1 × SPT-3G")
    ar.set_title("TR1: κ adds 15 % to shear alone, 4 % to 3×2pt",
                 fontsize=LABEL, color=MUTED, loc="left", pad=14)
    fig.savefig(OUT, dpi=DPI)
    for k, v in fis.items():
        print(f"{k:18s} sigma(A_IA) = {v['sigma']['A_IA']:.3f}  sigma(S8) = {v['sigma']['S8']:.4f}")
    print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
