"""South-patch footprint overlap for talk slide."""

from pathlib import Path

import healpy as hp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import skyproj
from matplotlib import colors as mcolors
from matplotlib.patches import Patch

import pickle

from dr1_cmbx.eDR1data.plotting import RR2Coverage
from snakemake_helpers import snakemake_log
from plot_utils import setup_theme

snakemake = snakemake  # type: ignore # noqa: F821

act_mask_path = Path(snakemake.input.act_mask)
spt_mask_path = Path(snakemake.input.spt_mask)
output_png = Path(snakemake.output.png)
nside = int(snakemake.config["nside"])

snakemake_log(snakemake, "Loading footprint masks")
act_mask = hp.read_map(str(act_mask_path), dtype=np.float64)
if hp.npix2nside(len(act_mask)) != nside:
    act_mask = hp.ud_grade(act_mask, nside)

spt_mask = hp.read_map(str(spt_mask_path), dtype=np.float64)
if hp.npix2nside(len(spt_mask)) != nside:
    spt_mask = hp.ud_grade(spt_mask, nside)

with open(snakemake.input.shear_pkl, "rb") as f:
    shear_data = pickle.load(f)
bd = shear_data[snakemake.params.all_bin_idx]
npix = hp.nside2npix(nside)
shear_weights = np.zeros(npix)
shear_weights[bd["ipix"]] = bd["weights"]

act_bin = (act_mask > 0).astype(np.int8)
spt_bin = (spt_mask > 0).astype(np.int8)
euclid_bin = (shear_weights > 0).astype(np.int8)

category = act_bin + (2 * spt_bin) + (4 * euclid_bin)
coverage = RR2Coverage.from_mask(nside, category > 0, sparse=True)
cat_sparse = coverage.sparsify(category.astype(float))

labels = {
    1: "ACT only",
    2: "SPT only",
    3: "ACT + SPT",
    4: "Euclid only",
    5: "ACT + Euclid",
    6: "SPT + Euclid",
    7: "ACT + SPT + Euclid",
}

palette = [
    "#ffffff", "#1f77b4", "#ff7f0e", "#9467bd",
    "#2ca02c", "#17becf", "#bcbd22", "#d62728",
]
cmap = mcolors.ListedColormap(palette)
bounds = np.arange(-0.5, 8.5, 1.0)
norm = mcolors.BoundaryNorm(bounds, cmap.N)

counts = {f"code_{i}": int(np.sum(category == i)) for i in range(8)}
area = {f"code_{i}": float(counts[f"code_{i}"] / category.size * 41253.0) for i in range(8)}

# South patch only
setup_theme("whitegrid")
fig, ax = plt.subplots(1, 1, figsize=(10, 10), layout="constrained")

pp = {"lon_0": 45, "lat_0": -64, "extent": [32, 70, -44, -63.5]}
sp = skyproj.GnomonicSkyproj(ax, **pp)
sp.draw_hpxpix(
    nside, coverage.ipix_sparse, cat_sparse,
    nest=coverage.nest, zoom=False, cmap=cmap, norm=norm,
)

legend_handles = [
    Patch(facecolor=palette[k], edgecolor="none", label=f"{labels[k]} ({area[f'code_{k}']:.0f} deg²)")
    for k in [1, 2, 3, 4, 5, 6, 7]
    if counts[f"code_{k}"] > 0
]
ax.legend(handles=legend_handles, loc="upper right", fontsize=12, frameon=True)

output_png.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(output_png, bbox_inches="tight", dpi=150)
plt.close(fig)
snakemake_log(snakemake, f"Saved {output_png}")
