"""CLOE vs dr1_cmbx figures, drawn for the Paris CMBX SWG deck at slide size.

Sources (the receipts of the felt fiber cmbx/likelihood/cloe-vs-dr1-cmbx-posterior-and):
  posterior-{mock,data}.csv   per-parameter shift (CLOE - eDR1like mean) / eDR1like sigma,
                              width ratio, weight-only Monte Carlo error
  truth-bias.json             (posterior mean - GLASS truth) / sigma, seed 3004 and ensemble
  timing-summary.json         single-core CLOE+CAMB and CLOE+emulator evaluation times
Chains for the contour panel (standardized coordinates only; never physical values):
  eDR1like  push-nov/cloe/frozen/reference-mock/posterior_exact.npz
  CLOE      cmbx-lanes/cloe-p4/.../full_mock_powerlaw/nested/posterior_exact.npz
Selections panel: chain_{full,3x2pt,kappa_crosses}.npz of the Euclid-SPT group repository
(~/code/euclid-spt-6x2pt, results/baseline; GLASS mock, unblinded).
Per-chain wall times are each chain's summary.json (also in posterior-*-summary.json).

Run in the cmbx container: app python make_cloe_figures.py
"""
import csv
import json
import os
import tempfile

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from scipy.ndimage import gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "images")
FIBER = "/leonardo/home/userexternal/cdaley00/loom/.felt/pando/cmbx/likelihood/cloe-vs-dr1-cmbx-posterior-and"
REF_MOCK = "/leonardo_scratch/large/userexternal/cdaley00/push-nov/cloe/frozen/reference-mock/posterior_exact.npz"
CLOE_MOCK = ("/leonardo_scratch/large/userexternal/cdaley00/cmbx-lanes/cloe-p4/results/cache/"
             "tr1_v2/cloe_parity/full_mock_powerlaw/nested/posterior_exact.npz")

# the three selections of the GLASS mock vector, made by lc materialize in the Euclid-SPT group repository
GROUP_CHAINS = "/leonardo/home/userexternal/cdaley00/code/euclid-spt-6x2pt/results/baseline"

# euclid theme (house/themes/euclid.css)
INK, MUTED, RULE = "#111418", "#535B67", "#C6CEDA"
ACCENT, COBALT, TEAL, OCHRE = "#435AA1", "#2E417C", "#1D6C78", "#9C7414"
BAND1, BAND2 = "#D6DEEA", "#EBF0F6"
REF_C, CLOE_C = INK, OCHRE        # eDR1like + CCL, CLOE
MOCK_C, DATA_C = TEAL, COBALT     # GLASS mock, blinded TR1 data

DPI = 200
W_PX, H_PX = 2 * 1712, 2 * 771    # drawn at 2x the slide's figure box
TICK, LABEL = 22, 24              # pt -> ~31, ~33 px displayed


def setup_font():
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
    plt.rcParams.update({
        "axes.linewidth": 1.4, "axes.edgecolor": MUTED,
        "xtick.color": MUTED, "ytick.color": MUTED, "axes.labelcolor": INK,
        "xtick.labelsize": TICK, "ytick.labelsize": TICK, "axes.labelsize": LABEL,
        "legend.fontsize": TICK, "xtick.major.width": 1.4, "ytick.major.width": 1.4,
        "xtick.major.size": 7, "ytick.major.size": 7,
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.facecolor": "white", "axes.facecolor": "white",
    })


def new_fig(**kw):
    return plt.figure(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI, **kw)


FAMILIES = [
    ("cosmology", lambda p: p in ("logA", "omch2", "ombh2", "h", "n_s", "S8", "sigma8", "Omega_m")
                  or p.startswith("HMCode")),
    ("intrinsic alignment", lambda p: p in ("A_IA", "eta_IA")),
    (r"$\Delta z$, sources", lambda p: p.startswith("delta_z_L")),
    (r"$\Delta z$, lenses", lambda p: p.startswith("delta_z_G")),
    ("shear $m$", lambda p: p.startswith("m_")),
    ("magnification", lambda p: p.startswith("mag_slope")),
    ("galaxy bias", lambda p: p.startswith("bias")),
]


def read_shifts(arm):
    with open(os.path.join(FIBER, f"posterior-{arm}.csv")) as f:
        return {r["parameter"]: (float(r["delta_mean_over_ref_sigma"]), float(r["weight_only_mc_error_over_ref_sigma"]))
                for r in csv.DictReader(f)}


def standardized(path, mu=None, sd=None):
    z = np.load(path)
    names = [str(n) for n in z["derived_names"]]
    x = np.stack([z["derived"][:, names.index("S8")], z["derived"][:, names.index("Omega_m")]], axis=1)
    w = np.exp(z["log_w"] - np.logaddexp.reduce(z["log_w"]))
    if mu is None:
        mu = w @ x
        sd = np.sqrt(w @ (x - mu) ** 2)
    return (x - mu) / sd, w, mu, sd


def contour(ax, v, w, color, ls):
    h, xe, ye = np.histogram2d(v[:, 0], v[:, 1], bins=90, range=[[-4, 4], [-4, 4]], weights=w)
    h = gaussian_filter(h, 2.5)
    h /= h.sum()
    o = np.sort(h.ravel())[::-1]
    c = o.cumsum()
    levels = sorted(o[np.searchsorted(c, m)] for m in (0.68, 0.95))
    ax.contour((xe[:-1] + xe[1:]) / 2, (ye[:-1] + ye[1:]) / 2, h.T, levels=levels,
               colors=[color], linestyles=ls, linewidths=3)


def fig_posteriors():
    mock, data = read_shifts("mock"), read_shifts("data")
    mc = np.mean([e for _, e in mock.values()] + [e for _, e in data.values()])
    fig = new_fig()
    ax = fig.add_axes([0.165, 0.15, 0.47, 0.83])
    for k, sig in ((2, BAND2), (1, BAND1)):
        ax.axvspan(-k * mc, k * mc, color=sig, zorder=0, lw=0)
    ax.axvline(0, color=MUTED, lw=1.4, zorder=1)
    for i, (label, sel) in enumerate(FAMILIES):
        for arm, d, dy, color in (("mock", mock, -0.17, MOCK_C), ("data", data, 0.17, DATA_C)):
            xs = [v for p, (v, _) in d.items() if sel(p)]
            ax.plot(xs, np.full(len(xs), i + dy), "o", ms=11, color=color, mec="white", mew=1.2, zorder=3)
    ax.set_yticks(range(len(FAMILIES)), [f[0] for f in FAMILIES])
    ax.set_ylim(len(FAMILIES) - 0.5, -1.15)
    ax.set_xlim(-0.08, 0.08)
    ax.set_xticks([-0.06, -0.03, 0, 0.03, 0.06], ["−0.06", "−0.03", "0", "0.03", "0.06"])
    ax.set_xlabel(r"shift of each parameter's mean, CLOE − eDR1like, in $\sigma$")
    ax.text(-0.02, -0.85, "parameter family", transform=ax.get_yaxis_transform(), color=MUTED,
            fontsize=TICK, ha="right", va="center")
    ax.tick_params(axis="y", length=0, labelsize=LABEL, labelcolor=INK)
    ax.spines["left"].set_visible(False)
    ax.plot([-0.077], [-0.85], "o", ms=11, color=MOCK_C, mec="white")
    ax.text(-0.073, -0.85, "GLASS mock", color=MOCK_C, fontsize=TICK, ha="left", va="center")
    ax.plot([-0.033], [-0.85], "o", ms=11, color=DATA_C, mec="white")
    ax.text(-0.029, -0.85, "TR1 (blinded)", color=DATA_C, fontsize=TICK, ha="left", va="center")
    ax.text(0.079, -0.85, "shaded: 1σ, 2σ MC error", color=MUTED, fontsize=TICK, ha="right", va="center")

    vr, wr, mu, sd = standardized(REF_MOCK)
    vc, wc, _, _ = standardized(CLOE_MOCK, mu, sd)
    ax2 = fig.add_axes([0.70, 0.15, 0.28 * H_PX / W_PX / 0.5 * 0.83, 0.83])
    contour(ax2, vr, wr, REF_C, "-")
    contour(ax2, vc, wc, CLOE_C, "--")
    ax2.set_xlim(-3, 3)
    ax2.set_ylim(-3, 3)
    ax2.set_aspect("equal")
    ax2.set_xticks([-2, 0, 2])
    ax2.set_yticks([-2, 0, 2])
    ax2.set_xlabel(r"$S_8$ − mean, in $\sigma$")
    ax2.set_ylabel(r"$\Omega_\mathrm{m}$ − mean, in $\sigma$")
    ax2.plot([], [], color=REF_C, lw=3, label="eDR1like + CCL")
    ax2.plot([], [], color=CLOE_C, lw=3, ls="--", label="CLOE")
    ax2.legend(loc="upper center", bbox_to_anchor=(0.5, 1.02), ncol=1, frameon=False, handlelength=1.6)
    ax2.set_ylim(-3, 5.2)
    ax2.set_yticks([-2, 0, 2])
    ax2.spines["left"].set_bounds(-3, 3)
    fig.savefig(os.path.join(IMG, "paris26_cloe_posterior_shifts.png"), dpi=DPI)
    plt.close(fig)


def fig_truth_bias():
    b = json.load(open(os.path.join(FIBER, "truth-bias.json")))["bias_sigma"]
    params = [("S8", r"$S_8$"), ("Omega_m", r"$\Omega_\mathrm{m}$"), ("sigma8", r"$\sigma_8$")]
    fig = new_fig()
    ax = fig.add_axes([0.08, 0.15, 0.56, 0.83])
    ax.axvline(0, color=MUTED, lw=1.4)
    for i, (p, _) in enumerate(params):
        r = b[p]
        # one chain: the posterior mean with its own 1 sigma, which is 1 in these units
        ax.errorbar(r["edr1like_ccl"], i - 0.22, xerr=1, fmt="o", ms=15, color=REF_C, capsize=6, lw=2.4, mew=2.4)
        ax.errorbar(r["cloe"], i, xerr=1, fmt="D", ms=13, color=CLOE_C, capsize=6, lw=2.4, mew=2.4)
        # mean over the 20 seeds with its standard error
        ax.errorbar(r["ensemble_mean"], i + 0.24, xerr=r["ensemble_mean_se"], fmt="s", ms=13, color="#8A929E",
                    capsize=6, lw=2.4, mew=2.4)
    ax.set_yticks(range(len(params)), [l for _, l in params])
    ax.tick_params(axis="y", length=0, labelsize=LABEL + 6, labelcolor=INK)
    ax.spines["left"].set_visible(False)
    ax.set_ylim(len(params) - 0.5, -0.6)
    ax.set_xlim(-1.8, 1.8)
    ax.set_xticks([-1.5, -1, -0.5, 0, 0.5, 1, 1.5], ["−1.5", "−1", "−0.5", "0", "0.5", "1", "1.5"])
    ax.set_xlabel(r"(posterior mean − GLASS truth) / posterior $\sigma$")
    hs = [plt.Line2D([], [], ls="-", lw=2.4, marker="o", ms=15, color=REF_C),
          plt.Line2D([], [], ls="-", lw=2.4, marker="D", ms=13, color=CLOE_C),
          plt.Line2D([], [], ls="-", lw=2.4, marker="s", ms=13, color="#8A929E")]
    fig.legend(hs, ["one mock, eDR1like + CCL\n(± posterior σ)", "the same mock, CLOE\n(± posterior σ)",
                    "mean of 20 mocks, eDR1like\n(± standard error)"],
               loc="center left", bbox_to_anchor=(0.665, 0.55), frameon=False, labelspacing=1.3,
               fontsize=LABEL)
    fig.savefig(os.path.join(IMG, "paris26_cloe_truth_bias.png"), dpi=DPI)
    plt.close(fig)


def fig_cost():
    t = json.load(open(os.path.join(FIBER, "timing-summary.json")))
    fig = new_fig()
    JAX_C = "#B5523B"
    # left: core-seconds per full-vector evaluation
    ax = fig.add_axes([0.205, 0.15, 0.25, 0.78])
    rows = [("eDR1like + CCL", 32.0, REF_C, "32 s"), ("CLOE + CAMB", t["camb_median_s"], CLOE_C, None),
            ("CLOE + emulator", t["cpj_median_s"], TEAL, None),
            ("CLOE projection", t["points"]["active_nuisance"]["cpj_s"], "#8A929E", None),
            ("CLOE in JAX", 0.45, JAX_C, "≤ 0.45 s")]
    for i, (lab, v, c, txt) in enumerate(rows):
        ax.barh(i, v, color=c, height=0.62)
        ax.text(v * 1.25, i, txt or f"{v:.3g} s", va="center", fontsize=TICK, color=INK)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows])
    ax.tick_params(axis="y", length=0, labelsize=TICK, labelcolor=INK)
    ax.set_xscale("log")
    ax.set_xlim(0.1, 300)
    ax.set_ylim(len(rows) - 0.5, -0.5)
    ax.set_xlabel("core-seconds per evaluation")
    ax.set_title("one likelihood evaluation", fontsize=LABEL, color=INK, loc="left")
    # right: wall time of one full chain on one node, hours
    ax = fig.add_axes([0.70, 0.15, 0.24, 0.78])
    chains = [("CLOE + CAMB", 11, 14, CLOE_C, True, "11–14 h"), ("CLOE + emulator", 4, 5, TEAL, True, "4–5 h"),
              ("CLOE in JAX", 0.54, 0.54, JAX_C, False, "32 min")]
    for i, (lab, lo, hi, c, est, txt) in enumerate(chains):
        ax.barh(i, hi, color="white" if est else c, edgecolor=c, hatch="//" if est else None, lw=2, height=0.62)
        ax.text(hi * 1.2, i, txt, va="center", fontsize=TICK, color=INK)
    ax.set_yticks(range(len(chains)), [c[0] for c in chains])
    ax.tick_params(axis="y", length=0, labelsize=TICK, labelcolor=INK)
    ax.set_xscale("log")
    ax.set_xlim(0.3, 60)
    ax.set_xticks([0.5, 1, 3, 10, 30], ["0.5", "1", "3", "10", "30"])
    ax.set_ylim(len(chains) - 0.5, -0.5)
    ax.set_xlabel("hours on one node; hatched: estimated")
    ax.set_title("one full chain", fontsize=LABEL, color=INK, loc="left")
    fig.savefig(os.path.join(IMG, "paris26_cloe_cost.png"), dpi=DPI)
    plt.close(fig)


def fig_selections():
    """S8-Omega_m of the three selections of the GLASS mock vector (unblinded mock, physical values)."""
    sel = [("3×2pt + κ crosses", "full", INK, "-"), ("3×2pt", "3x2pt", OCHRE, "--"),
           ("κ crosses", "kappa_crosses", TEAL, "-")]
    truth_om, truth_s8 = 0.3110, 0.8251   # chains/plot_variants.py --truth
    fig = new_fig()
    ax = fig.add_axes([0.10, 0.16, 0.44, 0.80])
    bx = fig.add_axes([0.72, 0.16, 0.25, 0.80])
    rng = [[0.15, 0.85], [0.70, 0.97]]
    for i, (lab, key, c, ls) in enumerate(sel):
        z = np.load(os.path.join(GROUP_CHAINS, f"chain_{key}.npz"))
        names = [str(n) for n in z["derived_names"]]
        om, s8 = z["derived"][:, names.index("Omega_m")], z["derived"][:, names.index("S8")]
        w = np.exp(z["log_w"] - np.logaddexp.reduce(z["log_w"]))
        h, xe, ye = np.histogram2d(om, s8, bins=90, range=rng, weights=w)
        h = gaussian_filter(h, 2.5)
        h /= h.sum()
        o = np.sort(h.ravel())[::-1]
        levels = sorted(o[np.searchsorted(o.cumsum(), m)] for m in (0.68, 0.95))
        ax.contour((xe[:-1] + xe[1:]) / 2, (ye[:-1] + ye[1:]) / 2, h.T, levels=levels,
                   colors=[c], linestyles=ls, linewidths=3)
        m = w @ s8
        sd = np.sqrt(w @ (s8 - m) ** 2)
        print(f"selection {key}: S8 = {m:.4f} +- {sd:.4f}, N = {len(w)}", flush=True)
        bx.errorbar(m, i, xerr=sd, fmt="o", color=c, ms=13, lw=3, capsize=0)
        bx.text(m, i - 0.22, f"{m:.3f} ± {sd:.3f}", ha="center", va="bottom", fontsize=TICK, color=INK)
        ax.plot([], [], color=c, ls=ls, lw=3, label=lab)
    ax.axvline(truth_om, color=MUTED, lw=1.4, ls=":")
    ax.axhline(truth_s8, color=MUTED, lw=1.4, ls=":")
    ax.set_xlim(*rng[0])
    ax.set_ylim(*rng[1])
    ax.set_xlabel(r"$\Omega_\mathrm{m}$")
    ax.set_ylabel(r"$S_8$")
    ax.legend(frameon=False, loc="upper right", handlelength=1.6)
    ax.text(truth_om + 0.008, rng[1][0] + 0.006, "mock input", fontsize=TICK, color=MUTED, va="bottom")
    bx.axvline(truth_s8, color=MUTED, lw=1.4, ls=":")
    bx.set_yticks(range(len(sel)), [s[0] for s in sel])
    bx.tick_params(axis="y", length=0, labelsize=TICK, labelcolor=INK)
    bx.set_ylim(len(sel) - 0.5, -0.6)
    bx.set_xlim(0.765, 0.865)
    bx.set_xticks([0.78, 0.80, 0.82, 0.84, 0.86])
    bx.set_xlabel(r"$S_8$, mean and 1$\sigma$; dotted: mock input")
    bx.spines["left"].set_visible(False)
    fig.savefig(os.path.join(IMG, "paris26_cloe_selections.png"), dpi=DPI)
    plt.close(fig)


if __name__ == "__main__":
    setup_font()
    fig_posteriors()
    fig_truth_bias()
    fig_cost()
    fig_selections()
