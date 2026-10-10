"""Mock recovery of shear x CMB lensing, redrawn for the Napoli CMBX talk.

The GLASS 6x2pt mock ensemble (10 seeds, ACT DR6 lensing mask and noise, TR1
Euclid mask, map estimator) measured gamma_i x kappa for the six source bins.
This is the analysis figure's shear row (lc output
results/tr1_act/glass_6x2pt_mocks/stack_review_figures.tar, fig_cmb_crosses.png)
redrawn at projector scale for a figure-text slide: the six bins in two rows of
three, each panel the 10-seed mean of ell C_ell against the input theory, with a
residual strip under it. All panels share one y axis and one exponent, so
heights compare across bins.

Main panels: points are the ensemble mean, bars are +-sigma_1, the seed-to-seed
scatter of ONE realization (sample std over the 10 seeds) -- what one survey of
this size is worth -- not the data's Gaussian sigma.  Residual strips:
(mean - input) / sigma_1, with the mean's own error bar 1/sqrt(10); the shaded
band is +-sigma_1/sqrt(10), where an unbiased pipeline puts about two points in
three.

The arrays are read with the analysis's own loader
(analyses/glass_6x2pt_mocks/src/twin_ensemble_figures.py: load_stores,
mock_series) from the committed recovery store, so the numbers here are the
analysis figure's numbers.

Output: images/napoli_mock_recovery_gk.png, at 2x the figure column of a
data-split="60" figure-text slide less a .source line (1000 x 740 px).

Run in the cmbx container: app python make_mock_recovery.py
"""
import os
import sys
import tempfile

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import FixedLocator, FuncFormatter, MaxNLocator, NullFormatter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "images", "napoli_mock_recovery_gk.png")
CMBX = "/leonardo_work/EUHPC_E07_074/cdaley00/cmbx"
GLASS = f"{CMBX}/analyses/glass_6x2pt_mocks"
STORE = f"{GLASS}/inputs/review_stack_recovery"
sys.path.insert(0, f"{GLASS}/src")
from twin_ensemble_figures import estimator_key, load_stores, mock_series  # noqa: E402

# euclid theme (house/themes/euclid.css)
INK, MUTED, RULE = "#111418", "#535B67", "#C6CEDA"
COBALT, TEAL, OCHRE = "#2E417C", "#1D6C78", "#9C7414"
BAND = "#D6DEEA"

# canvas: 1000 x 740 px displayed, drawn at 2x
W_PX, H_PX, DPI = 2000, 1480, 200
PT = DPI / 72 / 2            # displayed px per point
FAMILIES = [("gammaE", r"$\gamma_{i}\kappa$")]
COLOUR = {"delta": COBALT, "gammaE": TEAL}
ELL_TICKS = [100, 1000]
ELL_MINOR = [200, 300, 500, 2000, 3000]
TICK, LABEL = 24, 25         # pt; x PT -> 33 px, 35 px drawn, about 32 px as displayed


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
        print("font:", name, flush=True)
    except Exception as e:  # noqa: BLE001
        print("EB Garamond unavailable, using DejaVu Serif:", e, flush=True)
        plt.rcParams["font.family"] = "DejaVu Serif"


def load():
    store = load_stores([STORE], verbose=True)[0]
    st = store["stats"]
    out = {}
    for fam, _ in FAMILIES:
        rows = []
        for i in range(1, 7):
            key = estimator_key(f"{fam}_{i}xkappa_cmb", st, "map")
            m = mock_series(key, st)
            for k in ("mean", "truth", "sigma1"):     # C_ell -> ell C_ell; resid is unchanged
                m[k] = m["ell"] * m[k]
            rows.append(m)
        out[fam] = rows
    return out, len(store["seeds"])


def summarize(series, n):
    r = {fam: np.array([m["resid"] for m in rows]) for fam, rows in series.items()}
    allr = np.concatenate(list(r.values()))
    noise = np.sqrt(2 / np.pi) / np.sqrt(n)
    print(f"N seeds = {n};  expected mean|Δ|/σ₁ for an unbiased mean = {noise:.3f}")
    for fam, a in list(r.items()) + [("all", allr)]:
        j = np.unravel_index(np.nanargmax(np.abs(a)), a.shape)
        print(f"  {fam:7s} bands={a.size:3d}  mean|Δ|/σ₁={np.abs(a).mean():.3f}  "
              f"mean Δ/σ₁={a.mean():+.3f}  rms={np.sqrt((a ** 2).mean()):.3f}  "
              f"max|Δ|/σ₁={np.abs(a).max():.2f} (row {j[0] + 1}, band {j[1]})")
        print(f"          per-bin mean Δ/σ₁: " + " ".join(f"{x:+.2f}" for x in np.atleast_2d(a).mean(axis=1)))
    print(f"  Σ N·(Δ/σ₁)² = {(n * allr ** 2).sum():.1f} over {allr.size} bands "
          f"(bands treated as independent)")
    return {fam: np.abs(a).mean() for fam, a in r.items()}


def draw(series, n, mean_abs):
    plt.rcParams.update({
        "axes.linewidth": 1.4, "axes.edgecolor": MUTED,
        "xtick.color": MUTED, "ytick.color": MUTED, "axes.labelcolor": INK,
        "xtick.labelsize": TICK, "ytick.labelsize": TICK, "axes.labelsize": LABEL,
        "xtick.major.width": 1.4, "ytick.major.width": 1.4,
        "xtick.major.size": 7, "ytick.major.size": 7, "xtick.minor.size": 4,
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.facecolor": "white", "axes.facecolor": "white",
    })
    print(f"tick labels ≈ {TICK * PT:.0f} px, axis labels ≈ {LABEL * PT:.0f} px displayed")
    inner = 1 / np.sqrt(n)
    fam, tag = FAMILIES[0]
    rows = series[fam]
    expo = int(np.floor(np.log10(max(np.nanmax(m["mean"] + m["sigma1"]) for m in rows))))
    scale = 10.0 ** expo
    lo = min(np.nanmin(m["mean"] - m["sigma1"]) for m in rows) / scale
    hi = max(np.nanmax(m["mean"] + m["sigma1"]) for m in rows) / scale
    pad = 0.06 * (hi - lo)

    fig = plt.figure(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI)
    outer = fig.add_gridspec(2, 1, hspace=0.16, left=0.135, right=0.99, top=0.86, bottom=0.10)
    ax0 = axr0 = None
    for r in range(2):
        inner_gs = outer[r].subgridspec(2, 3, height_ratios=[2.5, 1], hspace=0.06, wspace=0.08)
        for c in range(3):
            i = 3 * r + c
            m = rows[i]
            ax = fig.add_subplot(inner_gs[0, c], sharey=ax0)
            axr = fig.add_subplot(inner_gs[1, c], sharex=ax, sharey=axr0)
            if ax0 is None:
                ax0, axr0 = ax, axr
            ell = m["ell"]
            ax.axhline(0, color=RULE, lw=1.2, zorder=0)
            ax.plot(ell, m["truth"] / scale, color=INK, lw=2.4, zorder=2)
            ax.errorbar(ell, m["mean"] / scale, yerr=m["sigma1"] / scale, fmt="o", ms=6.5,
                        color=COLOUR[fam], ecolor=COLOUR[fam], elinewidth=1.8, capsize=0,
                        mec="white", mew=0.8, zorder=3)
            ax.set_ylim(min(lo - pad, -pad), hi + pad)
            ax.text(0.95, 0.94, tag.format(i=i + 1), transform=ax.transAxes, fontsize=LABEL,
                    color=INK, ha="right", va="top")
            axr.axhspan(-inner, inner, color=BAND, lw=0, zorder=0)
            axr.axhline(0, color=MUTED, lw=1.2, zorder=1)
            axr.errorbar(ell, m["resid"], yerr=inner, fmt="o", ms=5.5, color=COLOUR[fam],
                         elinewidth=1.5, capsize=0, mec="white", mew=0.6, zorder=3)
            axr.set_ylim(-1.25, 1.25)
            axr.set_yticks([-1, 1])
            axr.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{v:+.0f}".replace("-", "\u2212")))
            axr.set_xscale("log")
            axr.set_xlim(0.8 * ell.min(), 1.25 * ell.max())
            axr.xaxis.set_major_locator(FixedLocator(ELL_TICKS))
            axr.xaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{int(v)}"))
            axr.xaxis.set_minor_locator(FixedLocator(ELL_MINOR))
            axr.xaxis.set_minor_formatter(NullFormatter())
            plt.setp(ax.get_xticklabels(), visible=False)
            ax.tick_params(axis="x", which="both", length=0)
            if r == 0:
                plt.setp(axr.get_xticklabels(), visible=False)
            if c:
                plt.setp(ax.get_yticklabels(), visible=False)
                plt.setp(axr.get_yticklabels(), visible=False)
            else:
                ax.yaxis.set_major_locator(MaxNLocator(3, integer=True))
                ax.set_ylabel(rf"$\ell C_\ell\;[10^{{{expo}}}]$", labelpad=6)
                axr.set_ylabel(r"$\Delta/\sigma_1$", labelpad=6)
            if r == 1 and c == 1:
                axr.set_xlabel(r"$\ell$", labelpad=2)
    fig.align_ylabels()

    # key along the top, two lines
    y1, y2 = 0.965, 0.915
    fig.add_artist(plt.Line2D([0.135, 0.175], [y1, y1], color=INK, lw=2.4, transform=fig.transFigure))
    fig.text(0.185, y1, "input theory", fontsize=LABEL, color=INK, ha="left", va="center")
    fig.add_artist(plt.Line2D([0.43], [y1], marker="o", ms=8, color=COLOUR[fam], mec="white",
                              transform=fig.transFigure))
    fig.text(0.445, y1, f"mean of {n} mocks $\\pm\\,\\sigma_1$ (one realization)",
             fontsize=LABEL, color=INK, ha="left", va="center")
    fig.text(0.135, y2, f"strips: (mean $-$ input)$/\\sigma_1$, band $\\pm\\,${inner:.2f}$\\,\\sigma_1$",
             fontsize=LABEL, color=MUTED, ha="left", va="center")
    fig.savefig(OUT, dpi=DPI)
    plt.close(fig)
    print("wrote", os.path.normpath(OUT))


def main():
    setup_font()
    series, n = load()
    mean_abs = summarize(series, n)
    draw(series, n, mean_abs)


if __name__ == "__main__":
    main()
