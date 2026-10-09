"""The null-test heatmap of the Napoli systematics-overview slide.

Each cell is the chi^2 probability to exceed, over the 15 bands (100 < l < 3000), of
one tracer's cross-spectrum with one VMPZ systematics template against zero: lens
bins delta_1..6 (full Gaussian covariance), source bins gamma_1..6 (full Gaussian
covariance) and the CMB lensing map kappa (diagonal only), read from the materialized
template measurements results/<universe>/tr1_systematics/<template>[_act].tar.
Tracers are rows and templates columns, so the figure sits beside the slide's text
(figure-text, 60 % split); the plot's title says what is drawn and it carries no
other caption (the slide's .source line holds the details).

Writes images/napoli_systematics_heatmap[__<shear>_<cmb>].png for the four variants
(LensMC x SPT-3G the default).

Run in the cmbx container: app python private/make_pte_heatmap.py
"""
import json
import os
import tarfile
import tempfile

import matplotlib
import numpy as np
from scipy import stats

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGES = os.path.join(HERE, "..", "..", "images")
CMBX = "/leonardo_work/EUHPC_E07_074/cdaley00/cmbx"
T = [("extinction_vis", "Extinction"), ("exposures_vis", "Exposures"), ("noise_vis", "Noise"),
     ("psf_vis", "PSF"), ("zodiacal_vis", "Zodiacal\nlight"), ("stars_gaia", "Stars")]
VARIANTS = [("lensmc", "spt", "tr1", ""), ("metacal", "spt", "tr1_metacal", ""),
            ("lensmc", "act", "tr1_act", "_act"), ("metacal", "act", "tr1_act_metacal", "_act")]
INK, MUTED = "#111418", "#535B67"
DPI = 200
W_IN, H_IN = 10.0, 7.6        # ~1000 x 760 px displayed: 2x the figure-text figure cell


def setup_font():
    src = os.path.join(HERE, "..", "..", "node_modules", "@fontsource-variable", "eb-garamond", "files",
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
        plt.rcParams["mathtext.fallback"] = "cm"
        for k in ("rm", "it", "bf"):
            plt.rcParams[f"mathtext.{k}"] = name + (":italic" if k == "it" else "")
    except Exception as e:  # noqa: BLE001
        print("EB Garamond unavailable:", e)


def ptes(universe, suffix):
    """(13 tracers, 6 templates): delta_1..6, gamma_1..6, kappa against each template."""
    P = np.zeros((13, len(T)))
    for a, (name, _) in enumerate(T):
        with tarfile.open(f"{CMBX}/results/{universe}/tr1_systematics/{name}{suffix}.tar") as t:
            m = json.load(t.extractfile("measurement.json"))
        j = 0
        for fam in ("GC", "WL"):
            for _, r in m[fam].items():
                cl = np.asarray(r["cross"])
                C = np.asarray(r["covariance"])
                P[j, a] = stats.chi2.sf(cl @ np.linalg.solve(C, cl), cl.size)
                j += 1
        p = np.asarray(m["template_kappa"]["signed_pull"])
        P[12, a] = stats.chi2.sf(np.sum(p ** 2), p.size)
    return P


def fmt(p):
    if p >= 0.01:
        return f"{p:.2f}"
    if p < 1e-6:
        return r"$<\!10^{-6}$"
    m, e = f"{p:.1e}".split("e")
    return rf"${m}\!\times\!10^{{{int(e)}}}$"


def heatmap(P, out):
    rows = [rf"$\delta_{i}$" for i in range(1, 7)] + [rf"$\gamma_{i}$" for i in range(1, 7)] + [r"$\kappa$"]
    Z = np.clip(-np.log10(np.maximum(P, 1e-300)), 0, 6)
    # light above PTE ~0.05 (-log10 = 1.3), saturated by 1e-6
    cmap = LinearSegmentedColormap.from_list(
        "calm", [(0, "#FFFFFF"), (1.3 / 6, "#FBF6EA"), (2.0 / 6, "#F1DFB8"), (3.2 / 6, "#D9A85A"),
                 (4.6 / 6, "#A8542B"), (1, "#7A2318")])
    fig = plt.figure(figsize=(W_IN, H_IN), dpi=DPI)
    ax = fig.add_axes([0.075, 0.015, 0.915, 0.80])
    ax.imshow(Z, cmap=cmap, vmin=0, vmax=6, aspect="auto")
    for (i, j), p in np.ndenumerate(P):
        z = Z[i, j]
        ax.text(j, i, fmt(p), ha="center", va="center", fontsize=16.5,
                color="white" if z > 4.0 else (INK if z > 1.3 else MUTED))
    ax.set_yticks(range(13), rows, fontsize=20)
    ax.xaxis.tick_top()
    ax.set_xticks(range(len(T)), [t[1] for t in T], fontsize=18, linespacing=0.95)
    ax.tick_params(length=0, colors=INK, pad=6)
    for sp in ax.spines.values():
        sp.set_visible(False)
    for y in (5.5, 11.5):
        ax.axhline(y, color="white", lw=6)
    fig.text(0.075, 0.985, r"$\chi^2$ PTE of each tracer $\times$ template cross-spectrum against zero",
             fontsize=20, color=INK, ha="left", va="top")
    fig.savefig(out, dpi=DPI, facecolor="white")
    plt.close(fig)


def main():
    setup_font()
    for shear, cmb, universe, suffix in VARIANTS:
        tag = "" if (shear, cmb) == ("lensmc", "spt") else f"__{shear}_{cmb}"
        out = os.path.normpath(os.path.join(IMAGES, f"napoli_systematics_heatmap{tag}.png"))
        P = ptes(universe, suffix)
        heatmap(P, out)
        print("wrote", out, f"min shear PTE {P[6:12].min():.3f}, min kappa PTE {P[12].min():.2f}")


if __name__ == "__main__":
    main()
