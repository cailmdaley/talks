"""
Generate backup corner plots for Moriond talk:
1. Full corner plot (all cosmological + nuisance params) for harmonic-space blinds
2. S8–A_IA–Δz subset showing the degeneracy that caused accidental unblinding
"""

from getdist import plots, MCSamples
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
    """Set readable LaTeX labels on chain parameters."""
    label_map = {
        "OMEGA_M": r"\Omega_{\rm m}",
        "ombh2": r"\omega_{\rm b} h^2",
        "h0": r"h_0",
        "n_s": r"n_{\rm s}",
        "SIGMA_8": r"\sigma_8",
        "S_8": r"S_8",
        "s_8_input": r"S_8^{\rm input}",
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


def plot_full_corner(chains):
    """Full corner plot — all sampled + key derived parameters."""
    params = [
        "OMEGA_M", "SIGMA_8", "S_8",
        "n_s", "h0", "ombh2",
        "logt_agn", "a", "m1", "bias_1",
    ]
    g = plots.get_subplot_plotter(width_inch=24)
    g.settings.axes_fontsize = 16
    g.settings.axes_labelsize = 20
    g.settings.alpha_filled_add = 0.6
    g.settings.legend_fontsize = 20
    g.triangle_plot(
        chains,
        params,
        legend_labels=BLIND_LABELS,
        line_args=[{"color": c} for c in COLORS],
        contour_colors=COLORS,
        legend_loc="upper right",
        filled=True,
    )
    outpath = f"{OUTPUT_DIR}/corner_full_harmonic_blinds.png"
    g.export(outpath)
    print(f"Saved {outpath}")
    plt.close("all")


def plot_s8_aia_dz(chains):
    """S8–A_IA–Δz corner plot showing the degeneracy that caused unblinding."""
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
    outpath = f"{OUTPUT_DIR}/corner_s8_aia_dz.png"
    g.export(outpath)
    print(f"Saved {outpath}")
    plt.close("all")


if __name__ == "__main__":
    chains = load_harmonic_chains()
    set_labels(chains)
    plot_full_corner(chains)
    plot_s8_aia_dz(chains)
