"""Crude estimators from the CMB-lensing crosses, redrawn for the Napoli CMBX talk.

Source: the exploratory estimators in results/scratch/napoli/crosses/ (README.md
there: method, ell ranges, caveats), run on each blinded TR1 likelihood input
(blind cmbx_dr1_a) and on 10 GLASS 6x2pt seeds.  Each data variant (shear
method x CMB lensing survey) has its own results_<shear>_<cmb>.json there; this
script draws every variant present and refits nothing.

Three estimators, all relative to the fiducial theory vector:

  Scale cut (results["scale_cut_used"]): the PT-validated split,
  k_max = 0.2 h/Mpc for delta-delta, 0.15 h/Mpc for delta-kappa and
  gamma-delta, ell_max = k_max chi(z_lens) - 1/2.

  lens ratio  mu_i = C^{gamma_i delta_j} / C^{kappa delta_j}, one amplitude per
              source bin with a free amplitude per lens bin, so galaxy bias and
              sigma8 cancel; mu_i ~ (1+m_i) x source-bin lensing efficiency
              relative to the CMB's.  Blind-immune (x0.98-1.04 over the
              public blinding envelope), so a variant's mu is drawn only when it
              is listed in MU_PUBLIC (Cail's explicit OK, talks CLAUDE.md).
  b           galaxy bias from delta-delta vs delta-kappa on linear scales.
              sigma8 cancels, Omega_m does not -> blinded.
  A^gk        gamma-kappa amplitude per source bin, 100 < ell < 3000;
              ~ S8^2.6 -> blinded.

Every variant is drawn on the same axes (the union of what the variants
need), so the slides' variant control changes only the points.

Outputs (images/), for the default variant (LensMC x SPT-3G):
  napoli_lens_ratio_1.png   mocks only: 10 seeds, median per bin, blind band
  napoli_lens_ratio_2.png   + the data and the shared-mu band
      at 2x the figure-text (60 %) figure cell less a .source line (989 x 723 px)
  napoli_galaxy_bias.png    b per lens bin, at the same figure-text cell size
  napoli_gk_amplitude.png   A^gk per source bin, at 2x the figure layout's body
                            less a caption and a .source line (1400 x 669 px)
and for every other variant the same names with __<shear>_<cmb> before .png,
which the slides list in data-alt.

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
BIAS_CUT = "0.2/0.15"         # delta-delta / delta-kappa k_max, h/Mpc
CROSSES = "/leonardo_work/EUHPC_E07_074/cdaley00/cmbx/results/scratch/napoli/crosses"
SHEARS = {"lensmc": "LensMC", "metacal": "MetaCal"}
CMBS = {"spt": "SPT-3G", "act": "ACT DR6"}
DEFAULT = ("lensmc", "spt")
# variants whose blind-immune lens ratio may be shown (Cail's explicit OK per variant)
MU_PUBLIC = {("lensmc", "spt")}
# lens bins 4 and 5 carry the delta-delta excess (felt: gg-amplitude-pattern-lens-nz),
# so b there is not read as measured whatever the CMB side
DD_EXCESS = {3, 4}
SNR_MEASURED = 4.0           # delta-kappa S/N inside the cut for b to count as measured

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


def load(src):
    r = json.load(open(src))
    assert r.get("blinded") == "cmbx_dr1_a", f"{src}: blind stamp {r.get('blinded')!r}"
    data_key = next(k for k in r if k.startswith("data_"))
    m, d, bs = r["mock"], r[data_key], r["blind_sensitivity"]["points"]
    z = r["mean_z"]
    out = {
        "zl": np.array([z[f"g{j}"] for j in range(6)]),       # lens bins
        "zs": np.array([z[f"l{i}"] for i in range(6)]),       # source bins
        "b_fid": np.array(m["b_true"]),
        "mock_mu": np.array([s["mu_point"] for s in m["lens"]]),        # (10, 6)
        "mock_mu_all": np.array([s["mu_all_point"] for s in m["lens"]]),
        "mu": np.array([[x["median"], x["lo"], x["hi"]] for x in d["lens"]["mu"]]),
        "mu_all": d["lens"]["mu_all"],
        "b": np.array([[x["b"]["median"], x["b"]["lo"], x["b"]["hi"]] for x in d["bias"][BIAS_CUT]]),
        "snr_dk": np.array([x["snr_dk"] for x in d["bias"][BIAS_CUT]]),
        "lmax": np.array([x["lmax_dk"] for x in d["bias"][BIAS_CUT]]),
        "mock_b_ratio": np.array([[x["b_point"] for x in s] for s in m["bias"][BIAS_CUT]]) / np.array(m["b_true"]),
        "A": np.array(d["gk"]["A"]), "A_err": np.array(d["gk"]["err"]),
        "mock_A": np.array([s["A"] for s in m["gk"]]),
        "blind_mu": np.array([p["mu"] for p in bs]),
        "blind_mu_all": np.array([p["mu_all"] for p in bs]),
        "blind_b": np.array([p["b_over_bfid"] for p in bs]),
        "blind_A": np.array([p["A_gk"] for p in bs]),
    }
    out["measured"] = np.array([s >= SNR_MEASURED and i not in DD_EXCESS for i, s in enumerate(out["snr_dk"])])
    return out


def variants():
    """Every (shear, cmb) whose results exist, the default first."""
    found = []
    for s in SHEARS:
        for c in CMBS:
            f = os.path.join(CROSSES, f"results_{s}_{c}.json")
            if os.path.exists(f):
                found.append((s, c, f))
    found.sort(key=lambda v: (v[:2] != DEFAULT, v[:2]))
    assert found and found[0][:2] == DEFAULT, f"no results_{DEFAULT[0]}_{DEFAULT[1]}.json in {CROSSES}"
    return found


def axes_ranges(all_a):
    """y ranges shared by every variant: the default's limits, widened where any variant needs it."""
    mu_lo = min(0.45, *(float((a["mu"][:, 0] - a["mu"][:, 1]).min()) - 0.05 for a in all_a))
    mu_hi = max(1.75, *(float((a["mu"][:, 0] + a["mu"][:, 2]).max()) + 0.05 for a in all_a))
    b_hi = max(4.2, *(float((a["b"][m, 0] + a["b"][m, 2]).max()) + 0.2 for a in all_a
                      for m in [a["measured"]] if m.any()))
    A_hi = max(1.6, *(float((a["A"] + a["A_err"]).max()) + 0.1 for a in all_a))
    return {"mu": (mu_lo, min(mu_hi, 2.5)), "b": min(b_hi, 6.0), "A": min(A_hi, 2.5)}


def name(base, variant):
    return f"{base}.png" if variant == DEFAULT else f"{base}__{variant[0]}_{variant[1]}.png"


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
    print(f"data b ({BIAS_CUT}): " + "  ".join(f"{v[0]:.2f}-{v[1]:.2f}+{v[2]:.2f}" for v in a["b"]))
    print("  (b - b_fid)/sigma_lo: " + " ".join(f"{(v[0] - f) / v[1]:+.1f}" for v, f in zip(a["b"], a["b_fid"])))
    print("  delta-kappa S/N: " + " ".join(f"{x:.1f}" for x in a["snr_dk"]))
    print("  ell_max: " + " ".join(f"{x:.0f}" for x in a["lmax"]))
    print("  mock median b/b_true: " + " ".join(f"{x:.2f}" for x in np.median(a["mock_b_ratio"], 0)))
    print(f"  mock bin-1 b/b_true range: {a['mock_b_ratio'][:, 0].min():.2f} to {a['mock_b_ratio'][:, 0].max():.2f}")
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


def lens_ratio(a, med, rob, R, variant):
    W_PX, H_PX = 1978, 1446
    n = a["mock_mu"].shape[0]
    lo_b, hi_b = a["blind_mu"].min(0), a["blind_mu"].max(0)
    bottom, top = R["mu"]
    for frame in (1, 2):
        fig = plt.figure(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI)
        ax = fig.add_axes([0.135, 0.165, 0.85, 0.665])
        x = bin_axis(ax, a["zs"], r"source bin, mean $z$")
        ax.set_ylim(bottom, top)
        ax.yaxis.set_major_locator(FixedLocator([v for v in np.arange(0.2, 2.6, 0.2) if bottom < v < top]))
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
            ax.text(1.0, 1.15, "TR1 data, blinded", transform=ax.transAxes, fontsize=LABEL,
                    color=DATA, ha="right", va="bottom", weight="bold")
            ax.text(1.0, 1.045, r"band: one shared $\mu \pm 1\sigma$",
                    transform=ax.transAxes, fontsize=LABEL, color=MUTED, ha="right", va="bottom")
        out = os.path.join(IMG, name(f"napoli_lens_ratio_{frame}", variant))
        fig.savefig(out, dpi=DPI)
        plt.close(fig)
        print("wrote", os.path.normpath(out))


def bias(a, R, variant):
    """Single panel: fiducial b as a line per bin, measured bins filled, the rest open."""
    W_PX, H_PX = 1978, 1446
    fig = plt.figure(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI)
    ax = fig.add_axes([0.115, 0.165, 0.87, 0.80])
    x = bin_axis(ax, a["zl"], r"lens bin, mean $z$")
    top = R["b"]
    ax.set_ylim(0, top)
    ax.yaxis.set_major_locator(FixedLocator([v for v in range(0, 7) if v < top]))
    ax.set_ylabel(r"galaxy bias $b$", labelpad=8)
    for xi, f in zip(x, a["b_fid"]):
        ax.plot([xi - 0.32, xi + 0.32], [f, f], color=INK, lw=2.4, zorder=1)
    v = a["b"]
    # measured: delta-kappa S/N >= SNR_MEASURED outside the delta-delta-excess bins
    measured = a["measured"]
    for i in range(6):
        col = DATA if measured[i] else GREYED
        hi = min(v[i, 0] + v[i, 2], top - 0.05) - v[i, 0]
        ax.errorbar(x[i], v[i, 0], yerr=[[v[i, 1]], [hi]], fmt="o", ms=15, color=col,
                    mfc=col if measured[i] else "white", mec="white" if measured[i] else col,
                    mew=1.4 if measured[i] else 2.6, elinewidth=3.2 if measured[i] else 2.4,
                    capsize=0, zorder=3 if measured[i] else 2, alpha=1.0 if measured[i] else 0.5)
        if v[i, 0] + v[i, 2] > top - 0.05:
            ax.annotate("", xy=(x[i], top + 0.02), xytext=(x[i], top - 0.3),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=2.4, mutation_scale=22, alpha=0.5),
                        annotation_clip=False)
    # key, upper left
    y0, dy = 0.95, 0.085
    ax.plot([0.03, 0.08], [y0, y0], transform=ax.transAxes, color=INK, lw=2.4)
    ax.text(0.10, y0, "fiducial", transform=ax.transAxes, fontsize=LABEL, color=INK, va="center")
    ax.plot([0.055], [y0 - dy], "o", transform=ax.transAxes, ms=15, color=DATA, mec="white", mew=1.4)
    ax.text(0.10, y0 - dy, "measured", transform=ax.transAxes, fontsize=LABEL, color=INK, va="center")
    ax.plot([0.055], [y0 - 2 * dy], "o", transform=ax.transAxes, ms=15, mfc="white", mec=GREYED, mew=2.6,
            alpha=0.5)
    ax.text(0.10, y0 - 2 * dy, "not counted: low S/N, or δδ high", transform=ax.transAxes,
            fontsize=LABEL, color=MUTED, va="center")
    out = os.path.join(IMG, name("napoli_galaxy_bias", variant))
    fig.savefig(out, dpi=DPI)
    plt.close(fig)
    print("wrote", os.path.normpath(out))


def amplitude(a, R, variant):
    """gamma-kappa amplitude per source bin, with the range a blind-sized shift could move it."""
    W_PX, H_PX = 2800, 1338
    fig = plt.figure(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI)
    ax = fig.add_axes([0.085, 0.18, 0.62, 0.79])
    x = bin_axis(ax, a["zs"], r"source bin, mean $z$")
    ax.set_ylim(0, R["A"])
    ax.yaxis.set_major_locator(FixedLocator([v for v in np.arange(0, 2.6, 0.5) if v < R["A"]]))
    ax.set_ylabel(r"$\gamma\kappa$ amplitude / fiducial", labelpad=8)
    ax.axhline(1, color=INK, lw=1.6, ls=(0, (5, 4)), zorder=1)
    for xi, l, h in zip(x, a["blind_A"].min(0), a["blind_A"].max(0)):
        ax.fill_between([xi - 0.36, xi + 0.36], l, h, color=BAND, lw=0, zorder=0)
    for i in range(6):
        g = i == 0
        col = GREYED if g else DATA
        ax.errorbar(x[i], a["A"][i], yerr=a["A_err"][i], fmt="o", ms=14, color=col,
                    mfc="white" if g else col, mec=col if g else "white", mew=2.6 if g else 1.4,
                    elinewidth=3.0, capsize=0, zorder=3)
    # key to the right of the axes
    kx, ky, dy = 1.04, 0.80, 0.13
    t = ax.transAxes
    ax.plot([kx + 0.02], [ky], "o", transform=t, ms=14, color=DATA, mec="white", mew=1.4, clip_on=False)
    ax.text(kx + 0.06, ky, "TR1 data, blinded", transform=t, fontsize=LABEL, color=INK, va="center")
    ax.add_patch(plt.Rectangle((kx, ky - dy - 0.035), 0.04, 0.07, transform=t, color=BAND, lw=0,
                               clip_on=False))
    ax.text(kx + 0.06, ky - dy, "range a blind-sized\ncosmology shift spans", transform=t,
            fontsize=LABEL, color=INK, va="center", linespacing=1.1)
    ax.plot([kx + 0.02], [ky - 2.25 * dy], "o", transform=t, ms=14, mfc="white", mec=GREYED, mew=2.6,
            clip_on=False)
    ax.text(kx + 0.06, ky - 2.25 * dy, "bin 1: mocks recover\nit 25 % high", transform=t,
            fontsize=LABEL, color=MUTED, va="center", linespacing=1.1)
    out = os.path.join(IMG, name("napoli_gk_amplitude", variant))
    fig.savefig(out, dpi=DPI)
    plt.close(fig)
    print("wrote", os.path.normpath(out))


def main():
    setup_font()
    found = variants()
    loaded = [(v[:2], load(v[2])) for v in found]
    R = axes_ranges([a for _, a in loaded])
    print("variants:", ", ".join(f"{s}_{c}" for (s, c), _ in loaded), "| shared ranges:", R)
    for variant, a in loaded:
        print(f"── TR1 {SHEARS[variant[0]]} × {CMBS[variant[1]]}")
        med, rob = summarize(a)
        if variant in MU_PUBLIC:
            lens_ratio(a, med, rob, R, variant)
        else:
            print("  lens ratio not drawn: blind-immune, needs Cail's OK (MU_PUBLIC)")
        bias(a, R, variant)
        amplitude(a, R, variant)


if __name__ == "__main__":
    main()
