# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "matplotlib", "seaborn"]
# ///
"""Ω_m–σ8 plane of the PUBLIC blinding cosmology list (BLIND-SAFE).

The right panel of the talk's blinding slide: the cloud of cosmologies the
self-blind draws ΔCℓ from. We show ALL 100 entries of the *public* list — a
tracked, shareable artifact — so nothing here is secret. The one entry actually
selected (the sealed index) is NEVER marked; the figure shows the *distribution
we draw from*, not the draw.

The list is drawn uniformly within fixed half-widths of the Planck-18 fiducial in
the (Ω_m, S8) plane — ±0.1 in Ω_m and ±0.075 in S8 (S8 = σ8·(Ω_m/0.3)^½ is the
lensing amplitude the cross probes). The S8 half-width is sized to COVER the S8
tension, so a tension-sized pull can't be reasoned away as "too big to be the
blind." We plot the (Ω_m, S8) plane the draw lives in.

Blind contract: NO selected index, NO single highlighted point, NO realized
cosmology — just the public cloud + the fiducial anchor.
"""
import json
from pathlib import Path

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

ROOT = Path("/leonardo_work/EUHPC_E07_074/cdaley00/cmbx")
LIST = ROOT / "results/tr1/cosmology_shift_list/blinding_cosmology_list.json"
OUT_PNG = ROOT / "docs/talks/images/spt26_blinding_cosmologies.png"

payload = json.loads(LIST.read_text())
header = payload["header"]
fid = header["fiducial"]
cosmos = payload["cosmologies"]
om = np.array([c["Omega_m"] for c in cosmos])
S8 = np.array([c["S8"] for c in cosmos])  # draw is uniform in (Ω_m, S8); plot the plane we draw in

sns.set_theme(context="talk", style="whitegrid")
plt.rcParams.update({"axes.edgecolor": "0.2", "axes.linewidth": 0.9,
                     "font.family": "DejaVu Sans", "legend.frameon": False})

fig, ax = plt.subplots(figsize=(7.0, 6.4))

# The sampled cloud — one calm hue, no point singled out.
cloud = sns.color_palette("mako", 6)[2]
ax.scatter(om, S8, s=95, color=cloud, alpha=0.55, edgecolor="white", linewidth=0.8,
           zorder=2, label="sampled cosmologies")

# Planck-18 fiducial anchor.
ax.scatter([fid["Omega_m"]], [fid["S8"]], marker="*", s=680, color="#e8a33d",
           edgecolor="0.15", linewidth=1.3, zorder=4, label="Planck-18 fiducial")

# Zoom out: the markers are large, so without padding the cloud edges clip the frame.
xpad = 0.18 * (om.max() - om.min())
ypad = 0.18 * (S8.max() - S8.min())
ax.set_xlim(om.min() - xpad, om.max() + xpad)
ax.set_ylim(S8.min() - ypad, S8.max() + ypad)

ax.set_xlabel(r"$\Omega_{\rm m}$")
ax.set_ylabel(r"$S_8 \equiv \sigma_8\,(\Omega_{\rm m}/0.3)^{1/2}$")
ax.tick_params(labelsize=15)
ax.grid(which="both", alpha=0.25)

ax.legend(loc="upper right", fontsize=15, handletextpad=0.4, borderpad=0.5,
          frameon=True, framealpha=0.9, facecolor="white", edgecolor="0.8")
# (No on-plot envelope label — the slide caption already states |ΔΩm|<0.1, |ΔS8|<0.075.)

fig.tight_layout()
OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT_PNG, dpi=180, bbox_inches="tight")
print("wrote", OUT_PNG)
