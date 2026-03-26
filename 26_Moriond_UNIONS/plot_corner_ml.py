"""
Corner plot: S8-A_IA-Dz with ML point markers.

The maximum likelihood points converge across blinds (A_IA compensates n(z) shift),
revealing the physical blind — this is the key visual for the backup slide.
"""

from getdist import plots
import numpy as np
import matplotlib.pyplot as plt

# ── Chain paths ──────────────────────────────────────────────────────
CHAIN_DIR = "/n09data/guerrini/output_chains"
BLINDS = ["A", "B", "C"]
COLORS = ["royalblue", "crimson", "forestgreen"]
BLIND_LABELS = [rf"$C_\ell$ Blind {b}" for b in BLINDS]
OUTPUT_DIR = "images"


def load_harmonic_chains():
    """Load v1.4.6.3 harmonic-space chains for all three blinds."""
    g = plots.get_subplot_plotter()
    chains = []
    for blind in BLINDS:
        root = f"SP_v1.4.6.3_leak_corr_{blind}"
        chain_root = f"{CHAIN_DIR}/{root}/{root}/getdist_{root}_cell"
        chain = g.samples_for_root(
            chain_root,
            cache=False,
            settings={"ignore_rows": 0, "smooth_scale_2D": 0.5, "smooth_scale_1D": 0.5},
        )
        chains.append(chain)
    return chains


def set_labels(chains):
    label_map = {
        "OMEGA_M": r"\Omega_{\rm m}",
        "SIGMA_8": r"\sigma_8",
        "S_8": r"S_8",
        "logt_agn": r"\log T_{\rm AGN}",
        "a": r"A_{\rm IA}",
        "m1": r"m_1",
        "bias_1": r"\Delta z_1",
    }
    for chain in chains:
        pnames = chain.getParamNames()
        for name, label in label_map.items():
            p = pnames.parWithName(name)
            if p is not None:
                p.label = label


def get_ml_values(chain, params):
    """Get parameter values at the maximum likelihood sample."""
    ml_idx = np.argmin(chain.loglikes)
    p = chain.getParams()
    return {name: getattr(p, name)[ml_idx] for name in params}


def plot_s8_aia_dz_with_ml(chains):
    """S8-A_IA-Dz corner plot with ML points highlighted."""
    params = ["S_8", "a", "bias_1"]

    g = plots.get_subplot_plotter(width_inch=8)
    g.settings.axes_fontsize = 20
    g.settings.axes_labelsize = 24
    g.settings.alpha_filled_add = 0.6
    g.settings.legend_fontsize = 18
    g.triangle_plot(
        chains,
        params,
        legend_labels=BLIND_LABELS,
        line_args=[{"color": c} for c in COLORS],
        contour_colors=COLORS,
        legend_loc="upper right",
        filled=True,
    )

    # Add ML markers
    for chain, color, label in zip(chains, COLORS, BLINDS):
        ml = get_ml_values(chain, params)
        print(f"Blind {label} ML: S8={ml['S_8']:.4f}, A_IA={ml['a']:.4f}, Dz={ml['bias_1']:.5f}")

        # 2D panels: star markers at ML
        for i in range(len(params)):
            for j in range(i):
                ax = g.subplots[i][j]
                if ax is not None:
                    ax.scatter(
                        ml[params[j]], ml[params[i]],
                        marker="*", s=280, color=color,
                        edgecolors="black", linewidths=0.8, zorder=10,
                    )

            # 1D panels: vertical line at ML
            ax = g.subplots[i][i]
            if ax is not None:
                ax.axvline(ml[params[i]], color=color, ls="--", lw=1.5, alpha=0.7, zorder=5)

    outpath = f"{OUTPUT_DIR}/corner_s8_aia_dz.png"
    g.export(outpath)
    print(f"Saved {outpath}")
    plt.close("all")


if __name__ == "__main__":
    chains = load_harmonic_chains()
    set_labels(chains)
    plot_s8_aia_dz_with_ml(chains)
