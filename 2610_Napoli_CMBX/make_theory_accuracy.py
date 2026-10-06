"""Theory-vector numerical accuracy, redrawn for the Napoli CMBX talk.

The likelihood's fast theory operator (dr1_cmbx eDR1like TheoryVector: Limber
integrals on a sparse ell grid, interpolated and convolved with each bandpower
window, nuisances applied by cached responses) is compared with a dense
reference: pyccl angular_cl with qag_quad integration at every integer ell up to
each window's last nonzero entry, convolved with the same windows.  The
reference builds its own CCL tracers and does not use TheoryVector's projection
code, but it rests on the same CCL library.

Every one of the 1350 retained bands (90 spectra x 15 bands, ell 100-3000, the
shape of the GLASS seed-3000 ACT-like mock export; no real data) is shown as
(fast - dense) / sigma, sigma the square root of the diagonal of the product's
Gaussian covariance.  Two parameter points: the fiducial with every nuisance at
zero, and one with A_IA = 1.4, eta_IA = -0.7, dz_G0 = +0.02, dz_L0 = -0.02,
m_0 = 0.01.  A variant using spline Limber integration is the foil.

Input: the validation run's JSON (validate_theory_vector_nuisances.py) under
/leonardo_scratch/large/userexternal/cdaley00/lik-nuisance-validation/.

Output: images/napoli_theory_accuracy.png, at 2x the figure layout's body box
less a .source line (1712 x 723 px).

Run in the cmbx container: app python make_theory_accuracy.py
"""
import json
import os
import tempfile

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "images", "napoli_theory_accuracy.png")
SRC = "/leonardo_scratch/large/userexternal/cdaley00/lik-nuisance-validation/full90canonical.json"

# euclid theme (house/themes/euclid.css)
INK, MUTED, RULE = "#111418", "#535B67", "#C6CEDA"
ACCENT, COBALT, TEAL, OCHRE = "#435AA1", "#2E417C", "#1D6C78", "#9C7414"
SHADE = "#EEF1F6"

# canvas: 1712 x 723 px displayed, drawn at 2x
W_PX, H_PX, DPI = 3424, 1446, 200
PT = DPI / 72 / 2            # displayed px per point


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


def family(pair):
    """Product pair key -> spectrum family; g is galaxy density, l is shear."""
    a, b = pair.split("_")
    if a == "kappa":
        return r"$\delta\kappa$" if b[0] == "g" else r"$\gamma\kappa$"
    return {"gg": r"$\delta\delta$", "gl": r"$\gamma\delta$", "ll": r"$\gamma\gamma$"}[a[0] + b[0]]


def load():
    d = json.load(open(SRC))
    out = {}
    for point in ("zero_nuisance", "nonzero_nuisance"):
        for method in ("qag_quad", "spline"):
            bands = d["points"][point]["comparisons"][method]["bands"]
            out[point, method] = np.array([b["sigma"] for b in bands])
    labels = [(b["pair"], b["band"]) for b in d["points"]["zero_nuisance"]["comparisons"]["qag_quad"]["bands"]]
    return out, labels, d


def summarize(r, labels):
    for (point, method), s in r.items():
        i = int(np.argmax(np.abs(s)))
        print(f"{point:17s} {method:8s} n={s.size}  max|Δ|/σ={abs(s).max():.4f} "
              f"(worst {s[i]:+.4f}, {labels[i][0]} band {labels[i][1]})  "
              f"rms={np.sqrt((s ** 2).mean()):.2e}  median|Δ|={np.median(abs(s)):.1e}  "
              f"n>0.01={int((abs(s) > 0.01).sum())}  n>0.1={int((abs(s) > 0.1).sum())}")


def segments(labels):
    """Contiguous runs of one family, merging the interleaved δδ/γδ block."""
    fams = [family(p) for p, _ in labels]
    merged = [f if f not in (r"$\delta\delta$", r"$\gamma\delta$") else "3x2" for f in fams]
    segs, start = [], 0
    for i in range(1, len(merged) + 1):
        if i == len(merged) or merged[i] != merged[start]:
            segs.append((merged[start], start, i - 1))
            start = i
    names = {"3x2": r"$\delta\delta$ and $\gamma\delta$"}
    return [(names.get(f, f), a, b) for f, a, b in segs]


def draw(r, labels):
    plt.rcParams.update({
        "axes.linewidth": 1.4, "axes.edgecolor": MUTED,
        "xtick.color": MUTED, "ytick.color": MUTED, "axes.labelcolor": INK,
        "xtick.labelsize": 22, "ytick.labelsize": 22, "axes.labelsize": 24,
        "xtick.major.width": 1.4, "ytick.major.width": 1.4,
        "xtick.major.size": 7, "ytick.major.size": 7,
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.facecolor": "white", "axes.facecolor": "white",
    })
    print(f"tick labels ≈ {22 * PT:.0f} px, axis labels ≈ {24 * PT:.0f} px displayed")
    x = np.arange(len(labels))
    segs = segments(labels)

    fig, (top, bot) = plt.subplots(
        2, 1, figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI, sharex=True,
        gridspec_kw=dict(height_ratios=[1.25, 1], hspace=0.16, left=0.085, right=0.80,
                         top=0.88, bottom=0.085))

    def frame(ax, lim, ticks, fmt):
        for k, (_name, a, b) in enumerate(segs):
            if k % 2 == 0:
                ax.axvspan(a - 0.5, b + 0.5, color=SHADE, lw=0, zorder=0)
        ax.axhline(0, color=MUTED, lw=1.2, zorder=1)
        ax.set_ylim(*lim)
        ax.yaxis.set_major_locator(FixedLocator(ticks))
        ax.yaxis.set_major_formatter(FuncFormatter(
            lambda v, _p: (fmt.format(v).replace("-", "−") if v else "0")))
        ax.set_xlim(-12, len(x) + 11)

    # top: the fast operator at both points
    frame(top, (-0.021, 0.021), [-0.02, -0.01, 0, 0.01, 0.02], "{:+.2f}")
    z, n = r["zero_nuisance", "qag_quad"], r["nonzero_nuisance", "qag_quad"]
    top.plot(x, z, "o", ms=9, mfc="none", mec=COBALT, mew=1.6, zorder=3)
    top.plot(x, n, "o", ms=5, color=ACCENT, mew=0, zorder=4)
    for s, va, dy, pre in ((z, "bottom", 0.0016, "nuisances 0: "), (n, "top", -0.0016, "nuisances on: ")):
        i = int(np.argmax(np.abs(s)))
        top.annotate(f"{pre}{s[i]:+.3f}".replace("-", "−") + r"$\,\sigma$",
                     (x[i], s[i]), (x[i] + 25, s[i] + dy), fontsize=22, color=INK,
                     ha="left", va=va)
    top.text(1.015, 0.70, "fast operator", transform=top.transAxes, fontsize=26,
             color=INK, ha="left", va="center", fontweight="bold")
    top.text(1.015, 0.52, "used in the chains", transform=top.transAxes, fontsize=22,
             color=MUTED, ha="left", va="center")
    top.plot([1.025], [0.33], "o", ms=9, mfc="none", mec=COBALT, mew=1.6, transform=top.transAxes,
             clip_on=False)
    top.text(1.045, 0.33, "nuisances at 0", transform=top.transAxes, fontsize=22, color=INK,
             ha="left", va="center")
    top.plot([1.025], [0.18], "o", ms=5, color=ACCENT, transform=top.transAxes, clip_on=False)
    top.text(1.045, 0.18, "IA, Δz, m on", transform=top.transAxes, fontsize=22, color=INK,
             ha="left", va="center")

    # bottom: the spline foil
    frame(bot, (-0.1, 0.3), [-0.1, 0, 0.1, 0.2, 0.3], "{:+.1f}")
    bot.axhline(0.1, color=OCHRE, lw=1.4, ls=(0, (5, 4)), zorder=1)
    sp = r["zero_nuisance", "spline"]
    bot.plot(x, sp, "o", ms=5, color=MUTED, mew=0, zorder=3)
    i = int(np.argmax(np.abs(sp)))
    bot.annotate(f"{sp[i]:+.2f}" + r"$\,\sigma$" + "\n" + r"high-$\ell$ $\delta\delta$, bin 6",
                 (x[i], sp[i]), (x[i] - 40, sp[i] - 0.01), fontsize=22, color=INK,
                 ha="right", va="top", linespacing=1.1)
    bot.text(1.015, 0.88, "spline variant", transform=bot.transAxes, fontsize=26,
             color=INK, ha="left", va="center", fontweight="bold")
    bot.text(1.015, 0.72, "rejected", transform=bot.transAxes, fontsize=22,
             color=MUTED, ha="left", va="center")
    bot.text(1.015, 0.5, r"$0.1\,\sigma$ bar", transform=bot.transAxes, fontsize=22,
             color=OCHRE, ha="left", va="center")

    fig.supylabel(r"(fast $-$ dense) / Gaussian $\sigma$", fontsize=24, color=INK, x=0.012)
    bot.xaxis.set_major_locator(NullLocator())
    bot.xaxis.set_minor_locator(NullLocator())
    bot.set_xlabel(f"all {len(x)} bandpowers: 90 spectra × 15 bands, $\\ell$ = 100–3000")

    # family names along the top
    for name, a, b in segs:
        fig.text(top.transData.transform(((a + b) / 2, 0))[0] / fig.bbox.width, 0.915, name,
                 fontsize=24, color=INK, ha="center", va="center")
    fig.savefig(OUT, dpi=DPI)
    plt.close(fig)
    print("wrote", os.path.normpath(OUT))


def main():
    setup_font()
    r, labels, _d = load()
    summarize(r, labels)
    draw(r, labels)


if __name__ == "__main__":
    main()
