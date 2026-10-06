"""Mock recovery of the CMB-lensing crosses, redrawn for the Napoli CMBX talk.

The GLASS 6x2pt mock ensemble (10 seeds, ACT DR6 lensing mask and noise, TR1
Euclid mask, map estimator) measured delta_i x kappa and gamma_i x kappa for the
six tomographic bins.  The analysis figure (lc output
results/tr1_act/glass_6x2pt_mocks/stack_review_figures.tar, fig_cmb_crosses.png)
draws twelve spectrum panels with residual strips; at slide scale only the
residuals carry the claim, so this figure draws them alone: one row per family,
the six bins overlaid in a sequential ramp and nudged apart in ell.

y is (ensemble mean - input) / sigma_1, where sigma_1 is the seed-to-seed scatter
of ONE realization (sample std over the 10 seeds), not the data's Gaussian sigma.
The mean of 10 seeds is known to sigma_1 / sqrt(10), so an unbiased pipeline
puts the points inside +-0.32 sigma_1 about two times in three.

The arrays are read with the analysis's own loader
(analyses/glass_6x2pt_mocks/src/twin_ensemble_figures.py: load_stores,
mock_series) from the committed recovery store, so the numbers here are the
analysis figure's numbers.

Output: images/napoli_mock_recovery_cmb.png, at 2x the figure layout's body box
less a .source line (1712 x 723 px).

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
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "images", "napoli_mock_recovery_cmb.png")
CMBX = "/leonardo_work/EUHPC_E07_074/cdaley00/cmbx"
GLASS = f"{CMBX}/analyses/glass_6x2pt_mocks"
STORE = f"{GLASS}/inputs/review_stack_recovery"
sys.path.insert(0, f"{GLASS}/src")
from twin_ensemble_figures import estimator_key, load_stores, mock_series  # noqa: E402

# euclid theme (house/themes/euclid.css)
INK, MUTED, RULE = "#111418", "#535B67", "#C6CEDA"
COBALT, TEAL, OCHRE = "#2E417C", "#1D6C78", "#9C7414"
BAND_OUTER, BAND_INNER = "#DCE3EE", "#BFCADB"

# canvas: 1712 x 723 px displayed, drawn at 2x
W_PX, H_PX, DPI = 3424, 1446, 200
PT = DPI / 72 / 2            # displayed px per point
FAMILIES = [("delta", r"$\delta_i \times \kappa$"), ("gammaE", r"$\gamma_i \times \kappa$")]
ELL_TICKS = [100, 300, 1000, 3000]


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
            rows.append(mock_series(key, st))
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
        "xtick.labelsize": 22, "ytick.labelsize": 22, "axes.labelsize": 25,
        "xtick.major.width": 1.4, "ytick.major.width": 1.4,
        "xtick.major.size": 7, "ytick.major.size": 7,
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.facecolor": "white", "axes.facecolor": "white",
    })
    print(f"tick labels ≈ {22 * PT:.0f} px, axis labels ≈ {25 * PT:.0f} px displayed")
    cmap = LinearSegmentedColormap.from_list("bins", [COBALT, TEAL, OCHRE])
    colours = [cmap(t) for t in np.linspace(0, 1, 6)]
    inner = 1 / np.sqrt(n)

    fig, axes = plt.subplots(2, 1, figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI, sharex=True,
                             gridspec_kw=dict(hspace=0.12, left=0.085, right=0.80,
                                              top=0.905, bottom=0.115))
    lim = 1.15
    for ax, (fam, tag) in zip(axes, FAMILIES):
        rows = series[fam]
        ell = rows[0]["ell"]
        ax.axhspan(-1, 1, color=BAND_OUTER, lw=0, zorder=0)
        ax.axhspan(-inner, inner, color=BAND_INNER, lw=0, zorder=0)
        ax.axhline(0, color=MUTED, lw=1.4, zorder=1)
        for i, (m, c) in enumerate(zip(rows, colours)):
            x = m["ell"] * 1.032 ** (i - 2.5)
            ax.plot(x, m["resid"], "o", ms=11, color=c, mec="white", mew=1.2, zorder=3)
        ax.set_xscale("log")
        ax.set_xlim(0.86 * ell.min(), 1.16 * ell.max())
        ax.set_ylim(-lim, lim)
        ax.set_yticks([-1, 0, 1])
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{v:+.0f}".replace("-", "\u2212") if v else "0"))
        ax.text(0.012, 0.95, tag, transform=ax.transAxes, fontsize=30, color=INK,
                ha="left", va="top", zorder=5)
        ax.text(1.015, 0.5, f"mean $|\\Delta|$ = {mean_abs[fam]:.2f} $\\sigma_1$",
                transform=ax.transAxes, fontsize=22, color=INK, ha="left", va="center")
        # band labels at the right edge
        ax.text(1.015, (1 + lim) / (2 * lim) - 0.03, r"$\pm 1\,\sigma_1$", transform=ax.transAxes,
                fontsize=22, color=MUTED, ha="left", va="center")
        ax.text(1.015, (inner + lim) / (2 * lim) + 0.03, r"$\pm \sigma_1/\sqrt{10}$",
                transform=ax.transAxes, fontsize=22, color=MUTED, ha="left", va="center")
    ax = axes[-1]
    ax.xaxis.set_major_locator(FixedLocator(ELL_TICKS))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{int(v)}"))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xlabel(r"multipole $\ell$")
    fig.supylabel(r"$\Delta / \sigma_1$  (one realization)", fontsize=25, color=INK, x=0.012)

    # bin key along the top, in the bins' own colours
    x0 = 0.085
    fig.text(x0, 0.955, "tomographic bin", fontsize=22, color=MUTED, ha="left", va="center")
    for i, c in enumerate(colours):
        fig.text(x0 + 0.13 + 0.035 * i, 0.955, f"{i + 1}", fontsize=24, color=c,
                 fontweight="bold", ha="center", va="center")
    fig.text(0.80, 0.955, f"mean of {n} GLASS seeds − input", fontsize=22, color=MUTED,
             ha="right", va="center")
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
