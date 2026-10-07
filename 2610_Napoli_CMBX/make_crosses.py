"""Crude estimators from the CMB-lensing crosses, redrawn for the Napoli CMBX talk.

Source: the cmbx chair's exploratory estimators on the blinded TR1 x SPT-3G
likelihood input (blind cmbx_dr1_a) and 10 GLASS 6x2pt seeds,
results/scratch/napoli/crosses/ (README.md there: method, ell ranges, caveats;
results.json holds every number).  Nothing is refitted here: this reads
results.json and draws.

Three estimators, all relative to the fiducial theory vector:

  lens ratio  mu_i = C^{gamma_i delta_j} / C^{kappa delta_j}, one amplitude per
              source bin with a free amplitude per lens bin, so galaxy bias and
              sigma8 cancel; mu_i ~ (1+m_i) x source-bin lensing efficiency
              relative to the CMB's.  Blind-immune (x0.98-1.04 over the
              public blinding envelope).
  b           galaxy bias from delta-delta vs delta-kappa at ell < k_max chi(z),
              k_max = 0.2 h/Mpc.  sigma8 cancels, Omega_m does not -> blinded.
  A^gk        gamma-kappa amplitude per source bin, 100 < ell < 3000;
              ~ S8^2.6 -> blinded.

Outputs (images/):
  napoli_lens_ratio_1.png   mocks only: 10 seeds, median per bin, blind band
  napoli_lens_ratio_2.png   + TR1 x SPT-3G data and the shared-mu band
      at 2x the figure-text (60 %) figure cell less a .source line (989 x 723 px)
  napoli_bias_blinded.png, napoli_Agk_blinded.png
      at 2x one compare half less caption and source (824 x 669 px)

Run in the cmbx container: app python make_crosses.py
"""
import json
import os
import tempfile

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import FixedLocator

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "images")
SRC = "/leonardo_work/EUHPC_E07_074/cdaley00/cmbx/results/scratch/napoli/crosses/results.json"

# euclid theme (house/themes/euclid.css)
INK, MUTED, RULE = "#111418", "#535B67", "#C6CEDA"
COBALT, TEAL, OCHRE = "#2E417C", "#1D6C78", "#9C7414"
BAND = "#D6DEEA"           # blind-shift band, as the mock-recovery strips
DATA, MOCK = OCHRE, TEAL
DATA_FILL = "#EADDBE"
SEED = "#9DC3C9"
GREYED = "#9AA1AC"

DPI = 200
PT = DPI / 72 / 2          # displayed px per point (figures are drawn at 2x)
TICK, LABEL = 22, 24       # pt -> ~31, ~33 px displayed


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
    plt.rcParams.update({
        "axes.linewidth": 1.4, "axes.edgecolor": MUTED,
        "xtick.color": MUTED, "ytick.color": MUTED, "axes.labelcolor": INK,
        "xtick.labelsize": TICK, "ytick.labelsize": TICK, "axes.labelsize": LABEL,
        "xtick.major.width": 1.4, "ytick.major.width": 1.4,
        "xtick.major.size": 7, "ytick.major.size": 7,
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.facecolor": "white", "axes.facecolor": "white",
    })
    print(f"tick labels ~ {TICK * PT:.0f} px, labels ~ {LABEL * PT:.0f} px displayed")


def load():
    r = json.load(open(SRC))
    m, d, bs = r["mock"], r["data_spt"], r["blind_sensitivity"]["points"]
    z = r["mean_z"]
    out = {
        "zl": np.array([z[f"g{j}"] for j in range(6)]),       # lens bins
        "zs": np.array([z[f"l{i}"] for i in range(6)]),       # source bins
        "b_fid": np.array(m["b_true"]),
        "mock_mu": np.array([s["mu_point"] for s in m["lens"]]),        # (10, 6)
        "mock_mu_all": np.array([s["mu_all_point"] for s in m["lens"]]),
        "mu": np.array([[x["median"], x["lo"], x["hi"]] for x in d["lens"]["mu"]]),
        "mu_all": d["lens"]["mu_all"],
        "b": np.array([[x["b"]["median"], x["b"]["lo"], x["b"]["hi"]] for x in d["bias"]["0.2"]]),
        "snr_dk": np.array([x["snr_dk"] for x in d["bias"]["0.2"]]),
        "lmax": np.array([x["lmax"] for x in d["bias"]["0.2"]]),
        "A": np.array(d["gk"]["A"]), "A_err": np.array(d["gk"]["err"]),
        "mock_A": np.array([s["A"] for s in m["gk"]]),
        "blind_mu": np.array([p["mu"] for p in bs]),
        "blind_mu_all": np.array([p["mu_all"] for p in bs]),
        "blind_b": np.array([p["b_over_bfid"] for p in bs]),
        "blind_A": np.array([p["A_gk"] for p in bs]),
    }
    return out


def summarize(a):
    mm = a["mock_mu"]
    n = mm.shape[0]
    med = np.median(mm, 0)
    rob = 1.4826 * np.median(np.abs(mm - med), 0) / np.sqrt(n)
    print(f"mock mu per bin, median of {n} seeds: " + " ".join(f"{x:.3f}" for x in med))
    print("   robust scatter/sqrt(n):        " + " ".join(f"{x:.3f}" for x in rob))
    print("   mean:                          " + " ".join(f"{x:.3f}" for x in mm.mean(0)))
    sa = a["mock_mu_all"]
    print(f"mock shared mu: mean {sa.mean():.3f} +- {sa.std(ddof=1) / np.sqrt(n):.3f}, "
          f"seed std {sa.std(ddof=1):.3f}")
    ma = a["mu_all"]
    print(f"data shared mu: {ma['median']:.3f} -{ma['lo']:.3f} +{ma['hi']:.3f}  "
          f"(1 - mu)/sigma_hi = {(1 - ma['median']) / ma['hi']:.2f}")
    print("data mu_i: " + "  ".join(f"{v[0]:.2f}-{v[1]:.2f}+{v[2]:.2f}" for v in a["mu"]))
    print(f"blind range mu_i: {a['blind_mu'].min():.3f}-{a['blind_mu'].max():.3f}; "
          f"shared: {a['blind_mu_all'].min():.3f}-{a['blind_mu_all'].max():.3f}")
    print("data b (k_max 0.2): " + "  ".join(f"{v[0]:.2f}-{v[1]:.2f}+{v[2]:.2f}" for v in a["b"]))
    print("  (b - b_fid)/sigma_lo: " + " ".join(f"{(v[0] - f) / v[1]:+.1f}" for v, f in zip(a["b"], a["b_fid"])))
    print("  delta-kappa S/N (SPT): " + " ".join(f"{x:.1f}" for x in a["snr_dk"]))
    print("  ell_max: " + " ".join(f"{x:.0f}" for x in a["lmax"]))
    print(f"blind range b/b_fid: {a['blind_b'].min():.2f}-{a['blind_b'].max():.2f}")
    print("data A_gk: " + "  ".join(f"{x:.2f}+-{e:.2f}" for x, e in zip(a["A"], a["A_err"])))
    print("mock A_gk mean: " + " ".join(f"{x:.2f}" for x in a["mock_A"].mean(0)))
    print(f"blind range A_gk: {a['blind_A'].min():.2f}-{a['blind_A'].max():.2f}")
    return med, rob


def bin_axis(ax, z, label):
    x = np.arange(1, 7)
    ax.set_xlim(0.45, 6.55)
    ax.xaxis.set_major_locator(FixedLocator(x))
    ax.set_xticklabels([f"{i}\n{zz:.2f}" for i, zz in zip(x, z)])
    ax.tick_params(axis="x", length=0, pad=8)
    ax.set_xlabel(label, labelpad=6)
    return x


def lens_ratio(a, med, rob):
    W_PX, H_PX = 1978, 1446
    n = a["mock_mu"].shape[0]
    lo_b, hi_b = a["blind_mu"].min(0), a["blind_mu"].max(0)
    top = 1.75
    for frame in (1, 2):
        fig = plt.figure(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI)
        ax = fig.add_axes([0.135, 0.165, 0.85, 0.665])
        x = bin_axis(ax, a["zs"], r"source bin, mean $z$")
        ax.set_ylim(0.45, top)
        ax.yaxis.set_major_locator(FixedLocator([0.6, 0.8, 1.0, 1.2, 1.4, 1.6]))
        ax.set_ylabel(r"lens ratio $\mu_i$ / fiducial", labelpad=8)
        ax.axhline(1, color=INK, lw=1.6, ls=(0, (5, 4)), zorder=1.8)
        # blind-sized shift of mu, per bin, drawn above the data band
        for xi, l, h in zip(x, lo_b, hi_b):
            ax.fill_between([xi - 0.42, xi + 0.42], l, h, color=BAND, lw=0, zorder=1.2)
        dxm = -0.13 if frame == 2 else 0.0
        fade = 0.45 if frame == 2 else 1.0
        # per-seed values; any beyond the axis sit on its top edge as a triangle
        rng = np.random.default_rng(1)
        for xi, col in zip(x, a["mock_mu"].T):
            jit = rng.uniform(-0.07, 0.07, col.size)
            inside = col < top - 0.03
            ax.scatter(xi + dxm + jit[inside], col[inside], s=34, color=SEED, lw=0, alpha=fade, zorder=2)
            ax.scatter(xi + dxm + jit[~inside], np.full((~inside).sum(), top - 0.025), s=70, marker="^",
                       color=SEED, lw=0, alpha=fade, zorder=2, clip_on=False)
        ax.errorbar(x + dxm, med, yerr=rob, fmt="o", ms=11, color=MOCK, elinewidth=2.6, capsize=0,
                    mec="white", mew=1.2, alpha=fade, zorder=3)
        # key above the axes: mocks left, data right (frame 2)
        ax.text(0.0, 1.15, f"{n} GLASS mocks, truth 1", transform=ax.transAxes, fontsize=LABEL,
                color=MOCK, ha="left", va="bottom")
        ax.text(0.0, 1.045, r"median $\pm$ scatter$/\sqrt{10}$",
                transform=ax.transAxes, fontsize=LABEL, color=MUTED, ha="left", va="bottom")
        if frame == 2:
            ma = a["mu_all"]
            ax.axhspan(ma["median"] - ma["lo"], ma["median"] + ma["hi"], color=DATA_FILL, lw=0,
                       alpha=0.75, zorder=0.5)
            ax.axhline(ma["median"], color=DATA, lw=1.8, zorder=1.5)
            v = a["mu"]
            ax.errorbar(x + 0.13, v[:, 0], yerr=[v[:, 1], v[:, 2]], fmt="o", ms=13, color=DATA,
                        elinewidth=3.0, capsize=0, mec="white", mew=1.2, zorder=4)
            ax.text(1.0, 1.15, "TR1 × SPT-3G, blinded", transform=ax.transAxes, fontsize=LABEL,
                    color=DATA, ha="right", va="bottom", weight="bold")
            ax.text(1.0, 1.045, r"band: one shared $\mu \pm 1\sigma$",
                    transform=ax.transAxes, fontsize=LABEL, color=MUTED, ha="right", va="bottom")
        out = os.path.join(IMG, f"napoli_lens_ratio_{frame}.png")
        fig.savefig(out, dpi=DPI)
        plt.close(fig)
        print("wrote", os.path.normpath(out))


def blinded_tag(ax, x, y, ha="left"):
    ax.text(x, y, "BLINDED", transform=ax.transAxes, fontsize=LABEL, color=DATA, weight="bold",
            ha=ha, va="top")


def bias(a):
    W_PX, H_PX = 1648, 1338
    fig = plt.figure(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI)
    ax = fig.add_axes([0.13, 0.18, 0.85, 0.79])
    x = bin_axis(ax, a["zl"], r"lens bin, mean $z$")
    ax.set_ylim(0, 4.6)
    ax.yaxis.set_major_locator(FixedLocator([0, 1, 2, 3, 4]))
    ax.set_ylabel(r"galaxy bias $b$", labelpad=8)
    lo_b, hi_b = a["blind_b"].min(0), a["blind_b"].max(0)
    for xi, f, l, h in zip(x, a["b_fid"], lo_b, hi_b):
        ax.fill_between([xi - 0.36, xi + 0.36], f * l, f * h, color=BAND, lw=0, zorder=0)
        ax.plot([xi - 0.36, xi + 0.36], [f, f], color=INK, lw=2.0, zorder=1)
    v = a["b"]
    solid = np.array([False, False, True, False, False, True])
    for i in range(6):
        col = DATA if solid[i] else GREYED
        hi = min(v[i, 0] + v[i, 2], 4.55) - v[i, 0]
        ax.errorbar(x[i], v[i, 0], yerr=[[v[i, 1]], [hi]], fmt="o", ms=12, color=col,
                    mfc=col if solid[i] else "white", mew=2.2 if not solid[i] else 1.2,
                    mec=col if not solid[i] else "white", elinewidth=2.8, capsize=0, zorder=3)
        if v[i, 0] + v[i, 2] > 4.55:
            ax.annotate("", xy=(x[i], 4.58), xytext=(x[i], 4.3),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=2.6, mutation_scale=22))
    ax.text(1.5, 2.15, "low S/N", fontsize=LABEL, color=MUTED, ha="center", va="bottom")
    ax.text(4.42, 3.95, "$\\delta\\delta$ excess\nrising with $\\ell$", fontsize=LABEL, color=MUTED,
            ha="right", va="top", linespacing=1.1)
    blinded_tag(ax, 0.02, 0.99)
    out = os.path.join(IMG, "napoli_bias_blinded.png")
    fig.savefig(out, dpi=DPI)
    plt.close(fig)
    print("wrote", os.path.normpath(out))


def amplitude(a):
    W_PX, H_PX = 1648, 1338
    fig = plt.figure(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI)
    ax = fig.add_axes([0.13, 0.18, 0.85, 0.79])
    x = bin_axis(ax, a["zs"], r"source bin, mean $z$")
    ax.set_ylim(0, 2.0)
    ax.yaxis.set_major_locator(FixedLocator([0, 0.5, 1.0, 1.5]))
    ax.set_ylabel(r"$\gamma\kappa$ amplitude / fiducial", labelpad=8)
    ax.axhline(1, color=INK, lw=1.6, ls=(0, (5, 4)), zorder=1)
    for xi, l, h in zip(x, a["blind_A"].min(0), a["blind_A"].max(0)):
        ax.fill_between([xi - 0.36, xi + 0.36], l, h, color=BAND, lw=0, zorder=0)
    for i in range(6):
        g = i == 0
        col = GREYED if g else DATA
        ax.errorbar(x[i], a["A"][i], yerr=a["A_err"][i], fmt="o", ms=12, color=col,
                    mfc="white" if g else col, mec=col if g else "white", mew=2.2 if g else 1.2,
                    elinewidth=2.8, capsize=0, zorder=3)
    ax.text(1.12, 0.03, "mocks: 1.25 high", fontsize=LABEL, color=MUTED, ha="left", va="bottom")
    blinded_tag(ax, 0.02, 0.99)
    out = os.path.join(IMG, "napoli_Agk_blinded.png")
    fig.savefig(out, dpi=DPI)
    plt.close(fig)
    print("wrote", os.path.normpath(out))


def main():
    setup_font()
    a = load()
    med, rob = summarize(a)
    lens_ratio(a, med, rob)
    bias(a)
    amplitude(a)


if __name__ == "__main__":
    main()
