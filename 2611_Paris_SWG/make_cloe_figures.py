"""CLOE vs dr1_cmbx figures, drawn for the Paris CMBX SWG deck at slide size.

The two likelihoods compared: dr1_cmbx's Cobaya likelihood (eDR1like + CCL), sampled directly with
Nautilus, and the standalone CLOE likelihood in JAX (the euclid_spt_like package), also with Nautilus.

Sources:
  summary-{mock,data}.json    (felt fiber cmbx/standalone-cloe-fast-likelihood, direct-cobaya/) per-parameter
                              shift (CLOE in JAX - Cobaya mean) / Cobaya sigma, width ratio, Monte Carlo error
  nautilus-mock-summary.json  calls and seconds per evaluation of the Cobaya chain on the GLASS mock
  mcmc-mock/timeline.json     node-hours and R-1 of the Cobaya MCMC chain on the same mock
  timing-summary.json         (felt fiber cmbx/likelihood/cloe-vs-dr1-cmbx-posterior-and) single-core
                              CLOE + CAMB and CLOE + emulator evaluation times
Chains for the contour panel (GLASS mock; standardized coordinates):
  Cobaya        paris-direct-cobaya/nautilus-mock/posterior.npz
  CLOE in JAX   chain_full.npz of the Euclid-SPT group repository
Selections panel: chain_{full,3x2pt,kappa_crosses}.npz of the Euclid-SPT group repository
(~/code/euclid-spt-6x2pt, results/baseline; GLASS mock, unblinded).

Run in the cmbx container: app python make_cloe_figures.py
"""
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
PANDO = "/leonardo/home/userexternal/cdaley00/loom/.felt/pando/cmbx"
DIRECT = PANDO + "/standalone-cloe-fast-likelihood/direct-cobaya"
TIMING = PANDO + "/likelihood/cloe-vs-dr1-cmbx-posterior-and/timing-summary.json"
SCRATCH = "/leonardo_scratch/large/userexternal/cdaley00/paris-direct-cobaya"
REF_MOCK = SCRATCH + "/nautilus-mock/posterior.npz"
MCMC_TIMELINE = SCRATCH + "/mcmc-mock/timeline.json"
TRUTH = {"S8": 0.8251325595490734, "Omega_m": 0.31104864620402706}   # GLASS input (compare_direct.py)

# the three selections of the GLASS mock vector, made by lc materialize in the Euclid-SPT group repository
GROUP_CHAINS = "/leonardo/home/userexternal/cdaley00/code/euclid-spt-6x2pt/results/baseline"

# euclid theme (house/themes/euclid.css)
INK, MUTED, RULE = "#111418", "#535B67", "#C6CEDA"
ACCENT, COBALT, TEAL, OCHRE = "#435AA1", "#2E417C", "#1D6C78", "#9C7414"
BAND1, BAND2 = "#D6DEEA", "#EBF0F6"
JAX_C = "#B5523B"
REF_C, CLOE_C = INK, JAX_C        # eDR1like + CCL in Cobaya, CLOE in JAX
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
    rows = json.load(open(os.path.join(DIRECT, f"summary-{arm}.json")))["against"]["package"]["rows"]
    return {r["parameter"]: (r["shift_sigma"], r["mc_error_sigma"]) for r in rows}


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
    print(f"posteriors: mean MC error {mc:.4f}; max |shift| mock {max(abs(v) for v, _ in mock.values()):.3f}, "
          f"data {max(abs(v) for v, _ in data.values()):.3f}", flush=True)
    xl = 0.115
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
    ax.set_xlim(-xl, xl)
    ax.set_xticks([-0.1, -0.05, 0, 0.05, 0.1], ["−0.1", "−0.05", "0", "0.05", "0.1"])
    ax.set_xlabel(r"shift of each parameter's mean, CLOE in JAX − Cobaya, in $\sigma$")
    ax.text(-0.02, -0.85, "parameter family", transform=ax.get_yaxis_transform(), color=MUTED,
            fontsize=TICK, ha="right", va="center")
    ax.tick_params(axis="y", length=0, labelsize=LABEL, labelcolor=INK)
    ax.spines["left"].set_visible(False)
    ax.plot([-0.96 * xl], [-0.85], "o", ms=11, color=MOCK_C, mec="white")
    ax.text(-0.91 * xl, -0.85, "GLASS mock", color=MOCK_C, fontsize=TICK, ha="left", va="center")
    ax.plot([-0.41 * xl], [-0.85], "o", ms=11, color=DATA_C, mec="white")
    ax.text(-0.36 * xl, -0.85, "TR1 (blinded)", color=DATA_C, fontsize=TICK, ha="left", va="center")
    ax.text(0.99 * xl, -0.85, "shaded: 1σ, 2σ MC error", color=MUTED, fontsize=TICK, ha="right", va="center")

    vr, wr, mu, sd = standardized(REF_MOCK)
    vc, wc, _, _ = standardized(os.path.join(GROUP_CHAINS, "chain_full.npz"), mu, sd)
    ax2 = fig.add_axes([0.70, 0.15, 0.28 * H_PX / W_PX / 0.5 * 0.83, 0.83])
    contour(ax2, vr, wr, REF_C, "-")
    contour(ax2, vc, wc, CLOE_C, "--")
    tx, ty = (TRUTH["S8"] - mu[0]) / sd[0], (TRUTH["Omega_m"] - mu[1]) / sd[1]
    print(f"posteriors: GLASS input at ({tx:+.3f}, {ty:+.3f}) sigma of the Cobaya chain", flush=True)
    ax2.plot(tx, ty, "*", ms=26, color=MUTED, mec="white", mew=1.2, zorder=4)
    ax2.set_xlim(-3, 3)
    ax2.set_aspect("equal")
    ax2.set_xticks([-2, 0, 2])
    ax2.set_xlabel(r"$S_8$ − mean, in $\sigma$")
    ax2.set_ylabel(r"$\Omega_\mathrm{m}$ − mean, in $\sigma$")
    ax2.plot([], [], color=REF_C, lw=3, label="eDR1like + CCL (Cobaya)")
    ax2.plot([], [], color=CLOE_C, lw=3, ls="--", label="CLOE in JAX")
    ax2.plot([], [], "*", ms=22, color=MUTED, mec="white", label="GLASS mock input")
    ax2.legend(loc="upper center", bbox_to_anchor=(0.5, 1.02), ncol=1, frameon=False, handlelength=1.6)
    ax2.set_ylim(-3, 6.3)
    ax2.set_yticks([-2, 0, 2])
    ax2.spines["left"].set_bounds(-3, 3)
    fig.savefig(os.path.join(IMG, "paris26_cloe_posterior_shifts.png"), dpi=DPI)
    plt.close(fig)


def fig_cost():
    """Left: core-seconds per evaluation. Right: node-hours of one full chain on the GLASS mock. All measured."""
    t = json.load(open(TIMING))
    cob = json.load(open(os.path.join(DIRECT, "nautilus-mock-summary.json")))
    mcmc = json.load(open(MCMC_TIMELINE))[-1]
    cob_nh = 4 * (4 + 9 / 60)          # 4 nodes x 4 h 09 min (REPORT.md)
    jax_nh, jax_eval = 0.45, 0.57      # 1 node x 27 min; likelihood wall x 112 cores / points (REPORT.md)
    print(f"cost: Cobaya {cob['eval_s_median']:.1f} s/eval, {cob_nh:.1f} node-h; MCMC {mcmc['node_h']:.1f} node-h, "
          f"R-1 = {mcmc['Rminus1']:.3f}; ratio {cob_nh / jax_nh:.0f}", flush=True)
    fig = new_fig()
    ax = fig.add_axes([0.225, 0.15, 0.24, 0.78])
    rows = [("eDR1like + CCL\n(Cobaya)", cob["eval_s_median"], REF_C), ("CLOE + CAMB", t["camb_median_s"], OCHRE),
            ("CLOE + emulator", t["cpj_median_s"], TEAL), ("CLOE in JAX", jax_eval, JAX_C)]
    for i, (lab, v, c) in enumerate(rows):
        ax.barh(i, v, color=c, height=0.62)
        ax.text(v + 0.9, i, f"{v:.2f} s" if v < 1 else f"{v:.1f} s" if v < 30 else f"{v:.0f} s", va="center",
                fontsize=TICK, color=INK)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows])
    ax.tick_params(axis="y", length=0, labelsize=TICK, labelcolor=INK)
    ax.set_xlim(0, 35)
    ax.set_xticks([0, 10, 20, 30])
    ax.set_ylim(len(rows) - 0.5, -0.5)
    ax.set_xlabel("core-seconds per evaluation")
    ax.set_title("one likelihood evaluation", fontsize=LABEL, color=INK, loc="left")

    ax = fig.add_axes([0.665, 0.15, 0.16, 0.78])
    done = mcmc["Rminus1"] <= 0.02
    chains = [("Cobaya,\nMCMC", mcmc["node_h"], REF_C, not done,
               f"{mcmc['node_h']:.1f} node-h\n2 nodes × {mcmc['wall_h']:.1f} h" if done
               else f"> {mcmc['node_h']:.1f} node-h\n$R-1$ = {mcmc['Rminus1']:.2f}"),
              ("Cobaya,\nNautilus", cob_nh, REF_C, False, f"{cob_nh:.1f} node-h\n4 nodes × 4 h 09"),
              ("CLOE in JAX,\nNautilus", jax_nh, JAX_C, False, f"{jax_nh:.2f} node-h\n1 node × 27 min")]
    top = max(c[1] for c in chains)
    for i, (lab, v, c, open_, txt) in enumerate(chains):
        ax.barh(i, v, color="white" if open_ else c, edgecolor=c, hatch="//" if open_ else None, lw=2, height=0.62)
        ax.text(v + 0.04 * top, i, txt, va="center", fontsize=TICK, color=INK, linespacing=1.1)
    ax.set_yticks(range(len(chains)), [c[0] for c in chains])
    ax.tick_params(axis="y", length=0, labelsize=TICK, labelcolor=INK)
    ax.set_xlim(0, 1.02 * top)
    ax.set_xticks(range(0, int(top) + 1, 5 if top < 21 else 10))
    ax.set_ylim(len(chains) - 0.5, -0.5)
    ax.set_xlabel("node-hours" + ("" if done else "; hatched: not converged"), loc="left")
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
    fig_cost()
    fig_selections()
