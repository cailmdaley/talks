"""Delta Omega_m histogram: config-space vs harmonic-space from 350 GLASS mocks.

Analogous to the existing Delta S8 histogram (Sacha's
2025_11_24_check_consistency.py, MAP 2D variant). Style matches the
S8_difference_config_harm_map_2D figure in Paper V.

Data values (v1.4.6.3 blind B, 2D marginalised mode):
  Config (Paper IV): Omega_m = 0.267
  Harmonic (Paper V): Omega_m = 0.221
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import norm

# ---------------------------------------------------------------------------
# Paths — from snakemake when available, hardcoded for standalone execution
# ---------------------------------------------------------------------------
try:
    mock_summary_path = snakemake.input.mock_summary  # noqa: F821
    out_path = str(snakemake.output[0])  # noqa: F821
except NameError:
    mock_summary_path = (
        "/n09data/guerrini/glass_mock_chains/"
        "summary_parameter_constraints_merged_v6.txt"
    )
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(
        out_dir, "images", "omega_m_difference_config_harm.png"
    )

# ---------------------------------------------------------------------------
# Style — match Sacha's paper.mplstyle
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.size": 12,
    "axes.labelsize": 14,
    "axes.titlesize": 14,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 11,
    "figure.autolayout": True,
})
sns.set_palette("husl")

# ---------------------------------------------------------------------------
# Load mock summary (same file Sacha uses, chain version v6)
# ---------------------------------------------------------------------------
df = pd.read_csv(mock_summary_path, delimiter=";")

# Use MAP 2D estimates (same as the S8 difference figure in Paper V)
col_config = "OMEGA_M_config_map_2D"
col_harm = "OMEGA_M_harm_map_2D"

selection = ~np.isnan(df[col_config]) & ~np.isnan(df[col_harm])
delta_Om = (df[col_config][selection] - df[col_harm][selection]).values

# ---------------------------------------------------------------------------
# Observed difference from unblinded data
# ---------------------------------------------------------------------------
Om_config = 0.267   # Paper IV, v1.4.6.3 blind B
Om_harm = 0.221     # Paper V,  v1.4.6.3 blind B
delta_Om_data = Om_config - Om_harm

# ---------------------------------------------------------------------------
# Histogram + PTE (same method as Sacha's S8 version)
# ---------------------------------------------------------------------------
n_bins = 20
counts, bin_edges = np.histogram(delta_Om, bins=n_bins, density=True)
bin_width = bin_edges[1] - bin_edges[0]

fig, ax = plt.subplots(figsize=(6.4, 4.8))

sns.histplot(
    delta_Om,
    bins=bin_edges,
    stat="density",
    kde=False,
    label=r"Difference (Config $-$ Harm)",
    color="blue",
    alpha=0.3,
    ax=ax,
)

# Data vertical line
ax.axvline(delta_Om_data, color="red", linestyle="--", linewidth=2,
           label="Difference in the analysis")

# PTE: fraction of mock distribution more extreme than the observed value
bin_index = np.digitize(delta_Om_data, bin_edges)
if delta_Om_data < 0:
    p_value = np.sum(counts[:bin_index]) * bin_width
else:
    p_value = np.sum(counts[bin_index:]) * bin_width

# N_sigma from the one-sided p-value (matches Sacha's convention)
n_sigma = norm.isf(p_value)
sign = "-" if delta_Om_data < 0 else "+"

# Format PTE string
mantissa, exponent = f"{p_value:.1e}".split("e")
exponent = int(exponent)
pte_str = rf"${{\rm PTE}} = {mantissa} \times 10^{{{exponent}}}$"
nsig_str = rf"$N_\sigma = {sign}{n_sigma:.2f}\sigma$"

# Place annotation in upper-right area (like the S8 figure)
ax.text(
    0.97, 0.88, pte_str,
    transform=ax.transAxes, ha="right", va="top",
    fontsize=12, color="black",
    bbox=dict(facecolor="white", edgecolor="lightgray", alpha=0.8, pad=3),
)
ax.text(
    0.97, 0.78, nsig_str,
    transform=ax.transAxes, ha="right", va="top",
    fontsize=12, color="black",
    bbox=dict(facecolor="white", edgecolor="lightgray", alpha=0.8, pad=3),
)

ax.set_xlabel(r"$\Delta\Omega_m$ estimated from mocks")
ax.set_ylabel("Density")
ax.legend(fontsize=11, framealpha=1.0, loc="upper left")

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
os.makedirs(os.path.dirname(out_path), exist_ok=True)
fig.savefig(out_path, dpi=300, bbox_inches="tight")
print(f"Saved {out_path}")
print(f"Delta Omega_m (data) = {delta_Om_data:.3f}")
print(f"PTE = {p_value:.3e}, N_sigma = {sign}{n_sigma:.2f}")
print(f"N mocks used = {selection.sum()}")
plt.close(fig)
