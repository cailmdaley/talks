"""Standalone COSEBIS B_n PTE heatmap for Moriond 2026 talk.

Produces a single-panel figure matching the aesthetics of the paper's
config_space_pte_matrices.py (same colormap, normalization, tick format,
fiducial marker), but sized for a talk slide column (~40% width).

Data source: results/tapestry/cosebis_pte_matrix/pte_values/
"""

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

# Resolve project root and add scripts dir to path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "workflow" / "scripts"))

from plotting_utils import (
    PAPER_MPLSTYLE,
    format_pte_colorbar,
    make_pte_colormap,
    make_pte_norm,
)

plt.style.use(PAPER_MPLSTYLE)

# ── Config (mirrors workflow/config/config.yaml fiducial block) ──────────
VERSION = "SP_v1.4.6.3_leak_corr"
BLIND = "A"
MIN_SEP = 1.0       # arcmin
MAX_SEP = 250.0     # arcmin
NBINS = 20
NMODES = 6          # COSEBIS modes for PTE
FIDUCIAL_MIN_SCALE = 12   # arcmin
FIDUCIAL_MAX_SCALE = 83   # arcmin

# ── Paths ────────────────────────────────────────────────────────────────
PTE_DIR = (
    PROJECT_ROOT
    / "results"
    / "tapestry"
    / "cosebis_pte_matrix"
    / "pte_values"
    / VERSION
    / BLIND
)
OUTPUT = PROJECT_ROOT / "docs" / "talks" / "images" / "pte_cosebis_talk.png"


def load_cosebis_pte_matrix():
    """Load COSEBIS PTE values from JSON files into matrix."""
    theta_grid = np.geomspace(MIN_SEP, MAX_SEP, NBINS + 1)
    n_theta = len(theta_grid)
    pte_matrix = np.full((n_theta, n_theta), np.nan)

    for pte_file in sorted(PTE_DIR.glob("pte_*.json")):
        with open(pte_file) as f:
            data = json.load(f)

        i_min, i_max = data["i_min"], data["i_max"]

        # Skip single-bin cases
        if i_max - i_min < 2:
            continue

        key = f"nmodes_{NMODES}"
        if key in data:
            pte_val = data[key]["pte_B"]
        else:
            pte_val = data.get("pte_B", np.nan)

        if not np.isnan(pte_val):
            pte_matrix[i_min, i_max] = pte_val

    return pte_matrix, theta_grid


def main():
    pte_matrix, theta_grid = load_cosebis_pte_matrix()
    n_theta = len(theta_grid)

    # Fiducial scale cut indices (same logic as config_space_pte_matrices.py)
    fid_start = np.argmin(np.abs(theta_grid[:-1] - FIDUCIAL_MIN_SCALE))
    fid_stop = np.argmin(np.abs(theta_grid[1:] - FIDUCIAL_MAX_SCALE)) + 1

    # ── Figure ───────────────────────────────────────────────────────────
    # Square figure sized for ~40% of a 1920px-wide slide column
    fig, ax = plt.subplots(figsize=(3.6, 3.6))

    pte_cmap = make_pte_colormap()
    pte_norm = make_pte_norm()

    im = ax.imshow(
        pte_matrix.T,
        origin="lower",
        aspect="equal",
        cmap=pte_cmap,
        norm=pte_norm,
        extent=[0, n_theta, 0, n_theta],
    )

    # Fiducial scale cut marker
    ax.add_patch(
        Rectangle(
            (fid_start, fid_stop),
            1, 1,
            fill=False,
            edgecolor="black",
            linewidth=2.0,
        )
    )

    # Label inside plot (matching paper style)
    ax.text(
        0.95, 0.05,
        r"COSEBIS $B_n$",
        transform=ax.transAxes,
        ha="right", va="bottom",
        fontsize=14,
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8),
    )

    # ── Ticks ────────────────────────────────────────────────────────────
    tick_step = 2
    tick_indices = np.arange(0, n_theta, tick_step)
    x_tick_labels = [f"{theta_grid[i]:.0f}" for i in tick_indices]
    y_tick_labels = [
        f"{theta_grid[min(i + 1, n_theta - 1)]:.0f}" for i in tick_indices
    ]

    ax.set_xticks(tick_indices)
    ax.set_xticklabels(
        x_tick_labels, rotation=45, ha="right", rotation_mode="anchor", fontsize=12
    )
    ax.set_yticks(tick_indices + 1)
    ax.set_yticklabels(y_tick_labels, fontsize=12)

    ax.set_xlabel(r"$\theta_{\min}$ [arcmin]", fontsize=14)
    ax.set_ylabel(r"$\theta_{\max}$ [arcmin]", fontsize=14)

    # ── Colorbar ─────────────────────────────────────────────────────────
    fig.canvas.draw()
    ax_pos = ax.get_position()
    cax = fig.add_axes([ax_pos.x1 + 0.015, ax_pos.y0, 0.035, ax_pos.height])
    cbar = fig.colorbar(im, cax=cax, spacing="proportional")
    format_pte_colorbar(cbar)
    cbar.set_label("PTE", fontsize=14)
    cbar.ax.tick_params(labelsize=12)

    # ── Save ─────────────────────────────────────────────────────────────
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {OUTPUT}")

    # Print fiducial PTE for verification
    fid_pte = pte_matrix[fid_start, fid_stop]
    print(f"Fiducial PTE at [{FIDUCIAL_MIN_SCALE}, {FIDUCIAL_MAX_SCALE}] arcmin: {fid_pte:.4e}")


if __name__ == "__main__":
    main()
