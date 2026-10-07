"""Blinding rehearsal on a GLASS mock, redrawn for the Napoli CMBX talk.

Three Cobaya chains on the same noisy GLASS 6x2pt mock (seed 3000, 90 spectra x
15 bands, ACT-like kappa, fixed Gaussian covariance), each sampling
(Omega_m, S8) and six linear galaxy biases with Omega_b, h, n_s, m_nu fixed:

  unblinded   the mock data vector as delivered
              (felt: science/cmbx/likelihood/mock-cosmology-recovery, "full")
  blind A, B  the same data vector plus a throwaway parameter-shift blind
              (felt: science/cmbx/likelihood/blinded-mock-rehearsal); the
              shifts were drawn at random by the blinding module and revealed
              only after all chains converged.  The real TR1 blind was never
              touched.

Two chains per run, 30 % of each chain's weight discarded as burn-in (the
analysis's own loader, workflow/scripts/summarize_mock_cosmology_chains.py:load),
2D 68/95 % contours from getdist.

Left panel: the three posteriors where they land, arrows from the unblinded
mean to unblinded mean + injected shift.  Right panel: zoom on the truth, with
each blinded posterior moved back by its injected shift.  Three frames of one
plot for a slide stack, the right panel blank until the last:
  images/napoli_blind_rehearsal_1.png   left: unblinded mock posterior and truth
  images/napoli_blind_rehearsal_2.png   left: + blinds A and B
  images/napoli_blind_rehearsal_3.png   + right: blinds moved back
at 2x the figure layout's body box less a .source line (1712 x 723 px).

Run in the cmbx container: app python make_blind_rehearsal.py
"""
import os
import sys
import tempfile

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from getdist import MCSamples
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
OUTS = [os.path.join(HERE, "..", "images", f"napoli_blind_rehearsal_{k}.png") for k in (1, 2, 3)]
CMBX = "/leonardo_work/EUHPC_E07_074/cdaley00/cmbx"
sys.path.insert(0, f"{CMBX}/workflow/scripts")
from summarize_mock_cosmology_chains import load  # noqa: E402

RUNS = {
    "unblinded": "/leonardo_scratch/large/userexternal/cdaley00/lik-debug/chains/full",
    "A": "/leonardo_scratch/large/userexternal/cdaley00/rehearsal/chains/rehearsal-a",
    "B": "/leonardo_scratch/large/userexternal/cdaley00/rehearsal/chains/rehearsal-b",
}
REVEALED = "/leonardo_scratch/large/userexternal/cdaley00/rehearsal/revealed.json"
TRUTH = {"Omega_m": 0.3151963290820357, "S8": 0.83236211839153}   # chain records' truth
P = ["Omega_m", "S8"]

# euclid theme (house/themes/euclid.css)
INK, MUTED, RULE = "#111418", "#535B67", "#C6CEDA"
COBALT, TEAL, OCHRE = "#2E417C", "#1D6C78", "#9C7414"
COL = {"unblinded": INK, "A": COBALT, "B": OCHRE}
FILL = {"unblinded": "#AEB6C2", "A": "#9AA8CF", "B": "#D9C18A"}

W_PX, H_PX, DPI = 3424, 1446, 200
PT = DPI / 72 / 2
TICK, LABEL = 21, 23


def setup_font():
    """EB Garamond, the deck's face, from the deck's own node_modules (woff2 -> ttf)."""
    src = os.path.join(HERE, "..", "node_modules", "@fontsource-variable", "eb-garamond", "files",
                       "eb-garamond-latin-wght-normal.woff2")
    try:
        from fontTools.ttLib import TTFont
        ttf = os.path.join(tempfile.mkdtemp(), "EBGaramond.ttf")
        f = TTFont(src)
        f.flavor = None
        f.save(ttf)
        font_manager.fontManager.addfont(ttf)
        name = font_manager.FontProperties(fname=ttf).get_name()
        plt.rcParams["font.family"] = [name, "DejaVu Serif"]
        plt.rcParams["mathtext.fontset"] = "custom"
        for k in ("rm", "it", "bf"):
            plt.rcParams[f"mathtext.{k}"] = name + (":italic" if k == "it" else "")
    except Exception as e:  # noqa: BLE001
        print("EB Garamond unavailable, using DejaVu Serif:", e, flush=True)
        plt.rcParams["font.family"] = "DejaVu Serif"


def samples(run, shift=(0.0, 0.0)):
    chains, _ = load(run, 0.3)
    x = np.concatenate([np.c_[c[P[0]].to_numpy(float) - shift[0], c[P[1]].to_numpy(float) - shift[1]]
                        for c in chains])
    w = np.concatenate([c["weight"].to_numpy(float) for c in chains])
    return MCSamples(samples=x, weights=w, names=P, labels=[r"\Omega_m", "S_8"],
                     settings={"smooth_scale_2D": 0.4, "smooth_scale_1D": 0.4})


def contour_data(s):
    d = s.get2DDensityGridData(P[0], P[1], num_plot_contours=2)
    return d.x, d.y, d.P, sorted(d.contours)


def stats(s):
    m = s.getMeans()
    sd = np.sqrt(np.diag(s.getCov()))
    return m, sd


def main():
    import json
    setup_font()
    inj = {k: json.load(open(REVEALED))[f"rehearsal-{k.lower()}"]["injected"] for k in ("A", "B")}
    raw = {k: samples(v) for k, v in RUNS.items()}
    back = {k: samples(RUNS[k], (inj[k]["Omega_m"], inj[k]["S8"])) for k in ("A", "B")}
    m0, sd0 = stats(raw["unblinded"])
    print(f"unblinded: Ωm = {m0[0]:.4f} ± {sd0[0]:.4f}  S8 = {m0[1]:.4f} ± {sd0[1]:.4f}")
    print(f"  truth offsets: Ωm {(m0[0] - TRUTH['Omega_m']) / sd0[0]:+.2f}σ  S8 {(m0[1] - TRUTH['S8']) / sd0[1]:+.2f}σ")
    x, y, dens, lev = contour_data(raw["unblinded"])
    ti = np.argmin(abs(x - TRUTH["Omega_m"])); tj = np.argmin(abs(y - TRUTH["S8"]))
    print(f"  density at truth vs contour levels (95, 68): {dens[tj, ti]:.3g} vs {lev}")
    for k in ("A", "B"):
        m, sd = stats(raw[k])
        res = (m - m0 - np.array([inj[k]["Omega_m"], inj[k]["S8"]])) / sd0
        print(f"blind {k}: injected ({inj[k]['Omega_m']:+.4f}, {inj[k]['S8']:+.4f})  "
              f"mean ({m[0]:.4f}, {m[1]:.4f}) sd ({sd[0]:.4f}, {sd[1]:.4f})  "
              f"width ratio ({sd[0] / sd0[0]:.2f}, {sd[1] / sd0[1]:.2f})  residual/σ0 ({res[0]:+.2f}, {res[1]:+.2f})")
    for i, out in enumerate(OUTS):
        draw(out, i >= 1, i >= 2, raw, back, inj, m0, sd0)


def contours(ax, s, key, filled=True, lw=2.6, ls="-"):
    x, y, dens, lev = contour_data(s)
    if filled:
        ax.contourf(x, y, dens, levels=[lev[0], lev[1], np.inf], colors=[FILL[key] + "66", FILL[key]],
                    zorder=1)
    ax.contour(x, y, dens, levels=lev, colors=COL[key], linewidths=lw, linestyles=ls, zorder=2)


def truth_mark(ax):
    ax.axvline(TRUTH["Omega_m"], color=MUTED, lw=1.4, ls=(0, (4, 3)), zorder=0)
    ax.axhline(TRUTH["S8"], color=MUTED, lw=1.4, ls=(0, (4, 3)), zorder=0)


def draw(out, with_blinds, with_right, raw, back, inj, m0, sd0):
    plt.rcParams.update({
        "axes.linewidth": 1.4, "axes.edgecolor": MUTED,
        "xtick.color": MUTED, "ytick.color": MUTED, "axes.labelcolor": INK,
        "xtick.labelsize": TICK, "ytick.labelsize": TICK, "axes.labelsize": LABEL + 2,
        "xtick.major.width": 1.4, "ytick.major.width": 1.4,
        "xtick.major.size": 7, "ytick.major.size": 7,
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.facecolor": "white", "axes.facecolor": "white",
    })
    fig, (axl, axr) = plt.subplots(1, 2, figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI,
                                   gridspec_kw=dict(width_ratios=[1.25, 1], wspace=0.22, left=0.075,
                                                    right=0.985, top=0.90, bottom=0.15))
    # left: where each posterior lands
    truth_mark(axl)
    contours(axl, raw["unblinded"], "unblinded")
    axl.text(m0[0] + 0.004, m0[1] - 0.011, "unblinded mock", color=INK, fontsize=LABEL, ha="left", va="top")
    if with_blinds:
        for k, (dx, dy, ha) in {"A": (0.016, 0.004, "left"), "B": (-0.046, -0.005, "right")}.items():
            contours(axl, raw[k], k)
            tx, ty = m0[0] + inj[k]["Omega_m"], m0[1] + inj[k]["S8"]
            axl.annotate("", xy=(tx, ty), xytext=(m0[0], m0[1]), zorder=4,
                         arrowprops=dict(arrowstyle="-|>", color=COL[k], lw=2.2, ls=(0, (5, 3)),
                                         mutation_scale=26, shrinkA=10, shrinkB=10))
            axl.text(tx + dx, ty + dy, f"blind {k}", color=COL[k], fontsize=LABEL, ha=ha, va="center")
    axl.text(TRUTH["Omega_m"] - 0.002, 0.891, "truth", fontsize=LABEL, color=MUTED, ha="right", va="top")
    axl.set_xlim(0.205, 0.375)
    axl.set_ylim(0.782, 0.892)
    axl.set_xlabel(r"$\Omega_\mathrm{m}$")
    axl.set_ylabel(r"$S_8$")
    axl.set_title("posteriors as measured", fontsize=LABEL, color=MUTED, loc="left", pad=12)

    # right: injected shift removed
    if not with_right:
        axr.set_visible(False)
    truth_mark(axr)
    contours(axr, raw["unblinded"], "unblinded")
    for k in ("A", "B"):
        contours(axr, back[k], k, filled=False, lw=3.0)
        axr.plot([], [], color=COL[k], lw=3.0, label=f"blind {k}")
    axr.fill_between([], [], color=FILL["unblinded"], ec=INK, lw=2.6, label="unblinded mock")
    axr.legend(loc="lower right", fontsize=LABEL - 2, frameon=False, handlelength=1.6, ncol=3,
               columnspacing=1.2, borderaxespad=0.2)
    axr.plot(TRUTH["Omega_m"], TRUTH["S8"], marker="*", ms=22, color=INK, mec="white", mew=1.4, zorder=5)
    axr.text(TRUTH["Omega_m"] - 0.0008, 0.8462, "truth", fontsize=LABEL, color=MUTED,
             ha="right", va="top", zorder=5)
    axr.set_xlim(0.292, 0.362)
    axr.set_ylim(0.8165, 0.8465)
    axr.set_xticks([0.30, 0.32, 0.34, 0.36])
    axr.set_yticks([0.825, 0.835, 0.845])
    axr.set_xlabel(r"$\Omega_\mathrm{m}$")
    axr.set_ylabel(r"$S_8$")
    axr.set_title("blinds shifted back by their hidden shift", fontsize=LABEL, color=MUTED, loc="left", pad=12)
    fig.savefig(out, dpi=DPI)
    plt.close(fig)
    print("wrote", os.path.normpath(out))


if __name__ == "__main__":
    main()
