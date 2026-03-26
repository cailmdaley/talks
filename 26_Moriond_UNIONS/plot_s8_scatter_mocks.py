"""S8(config) vs S8(harmonic) scatter from 350 GLASS mocks.

Each mock is one point (2D KDE MAP). The UNIONS data crosshair
and equality line are overlaid. Marginal histograms on top and right.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

# ── Data ─────────────────────────────────────────────────────────────

SUMMARY_CSV = "/n09data/guerrini/glass_mock_chains/summary_parameter_constraints_merged_v6.txt"

# UNIONS v1.4.6.3 blind B — 2D marginalised MAP from papers
S8_CONFIG_DATA = 0.858
S8_HARMONIC_DATA = 0.917

# Fiducial (Planck18)
S8_FIDUCIAL = 0.8102 * (0.3111 / 0.3) ** 0.5


def load_mocks():
    df = pd.read_csv(SUMMARY_CSV, delimiter=";")
    # Use 2D KDE MAP — same estimator as the data values
    mask = df["S8_config_map_2D"].notna() & df["S8_harm_map_2D"].notna()
    s8_config = df.loc[mask, "S8_config_map_2D"].values
    s8_harm = df.loc[mask, "S8_harm_map_2D"].values
    return s8_config, s8_harm


def fraction_more_extreme(s8_config, s8_harm, s8c_data, s8h_data):
    """Fraction of mocks whose |Delta S8| exceeds the data's."""
    delta_mock = s8_config - s8_harm
    delta_data = s8c_data - s8h_data
    return np.mean(np.abs(delta_mock) >= np.abs(delta_data))


def make_plot(s8_config, s8_harm, outpath):
    """JointGrid-style scatter with marginal histograms."""
    frac = fraction_more_extreme(s8_config, s8_harm, S8_CONFIG_DATA, S8_HARMONIC_DATA)
    n_mocks = len(s8_config)

    # ── Layout: gridspec with marginals ──────────────────────────────
    fig = plt.figure(figsize=(7.5, 7.5))
    gs = gridspec.GridSpec(
        2, 2,
        width_ratios=[4, 1],
        height_ratios=[1, 4],
        hspace=0.05,
        wspace=0.05,
    )
    ax_main = fig.add_subplot(gs[1, 0])
    ax_top = fig.add_subplot(gs[0, 0], sharex=ax_main)
    ax_right = fig.add_subplot(gs[1, 1], sharey=ax_main)

    # Color palette: pink/red to match existing talk style
    hist_color = "#c86080"

    # ── Main panel: hexbin ───────────────────────────────────────────
    ax_main.hexbin(
        s8_config, s8_harm,
        gridsize=20,
        cmap="RdPu",
        mincnt=1,
        alpha=0.85,
        linewidths=0.3,
        edgecolors="white",
    )

    # Axis limits: ensure data point is visible with room
    pad = 0.01
    lo = min(s8_config.min(), s8_harm.min()) - pad
    hi = max(max(s8_config.max(), s8_harm.max()), S8_HARMONIC_DATA) + pad
    ax_main.set_xlim(lo, hi)
    ax_main.set_ylim(lo, hi)

    # Equality line
    ax_main.plot([lo, hi], [lo, hi], color="gray", ls="--", lw=1.2, alpha=0.7, zorder=1)

    # Data crosshair
    ax_main.axvline(S8_CONFIG_DATA, color="black", ls="--", lw=1.8, alpha=0.9, zorder=5)
    ax_main.axhline(S8_HARMONIC_DATA, color="black", ls="--", lw=1.8, alpha=0.9, zorder=5)
    ax_main.plot(
        S8_CONFIG_DATA, S8_HARMONIC_DATA,
        marker="+", ms=18, mew=3, color="black", zorder=10,
    )

    # Label the data point
    ax_main.annotate(
        "UNIONS",
        xy=(S8_CONFIG_DATA, S8_HARMONIC_DATA),
        xytext=(-55, -20), textcoords="offset points",
        fontsize=13, fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="black", lw=1.2),
    )

    ax_main.set_xlabel(r"$S_8$ (configuration space)", fontsize=16)
    ax_main.set_ylabel(r"$S_8$ (harmonic space)", fontsize=16)
    ax_main.tick_params(labelsize=13)

    # ── Top marginal ─────────────────────────────────────────────────
    ax_top.hist(
        s8_config, bins=25, color=hist_color, alpha=0.6,
        edgecolor="white", linewidth=0.5,
    )
    ax_top.axvline(S8_CONFIG_DATA, color="black", ls="--", lw=1.8, alpha=0.9)
    ax_top.axvline(S8_FIDUCIAL, color="gray", ls=":", lw=1.2, alpha=0.7)
    ax_top.tick_params(labelbottom=False, labelleft=False, left=False)
    ax_top.spines["top"].set_visible(False)
    ax_top.spines["right"].set_visible(False)
    ax_top.spines["left"].set_visible(False)

    # ── Right marginal ───────────────────────────────────────────────
    ax_right.hist(
        s8_harm, bins=25, orientation="horizontal",
        color=hist_color, alpha=0.6,
        edgecolor="white", linewidth=0.5,
    )
    ax_right.axhline(S8_HARMONIC_DATA, color="black", ls="--", lw=1.8, alpha=0.9)
    ax_right.axhline(S8_FIDUCIAL, color="gray", ls=":", lw=1.2, alpha=0.7)
    ax_right.tick_params(labelleft=False, labelbottom=False, bottom=False)
    ax_right.spines["top"].set_visible(False)
    ax_right.spines["right"].set_visible(False)
    ax_right.spines["bottom"].set_visible(False)

    # ── Annotation ───────────────────────────────────────────────────
    delta_data = S8_CONFIG_DATA - S8_HARMONIC_DATA
    frac_pct = frac * 100
    ax_main.text(
        0.03, 0.04,
        (
            rf"$\Delta S_8 = {delta_data:+.3f}$" "\n"
            rf"{frac_pct:.0f}\% of {n_mocks} mocks more extreme"
        ),
        transform=ax_main.transAxes,
        fontsize=12,
        va="bottom", ha="left",
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="gray", alpha=0.85),
    )

    fig.suptitle(
        r"$S_8$ consistency: configuration vs harmonic (350 GLASS mocks)",
        fontsize=15, y=0.98,
    )

    fig.savefig(outpath, dpi=200, bbox_inches="tight", facecolor="white")
    print(f"Saved {outpath}")
    plt.close(fig)


if __name__ == "__main__":
    try:
        outpath = snakemake.output[0]
    except NameError:
        outpath = "docs/talks/images/s8_scatter_config_vs_harmonic.png"

    s8_config, s8_harm = load_mocks()
    make_plot(s8_config, s8_harm, outpath)
