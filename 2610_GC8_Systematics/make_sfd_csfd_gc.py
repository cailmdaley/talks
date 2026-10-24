#!/usr/bin/env python3
"""GC-8 slide 6: TR1 Cycle-2 delta x SFD, CSFD and CSFD - SFD, as rho_l per band with Gaussian errors.

Reads ~/loom/.felt/science/cmbx/gc8-systematics-update/sfd-csfd-gc.json (results/scratch/gc8/run_dust.py;
same numbers as sfd-csfd-gc.png), drawn for a 1371 px wide slide figure (all text >= 32 px as displayed).

Run in the cmbx container: app python docs/talks/2610_GC8_Systematics/make_sfd_csfd_gc.py
"""
import json, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_cycles  # noqa: E402
J = Path.home()/'loom/.felt/science/cmbx/gc8-systematics-update/sfd-csfd-gc.json'
OUT = Path(__file__).resolve().parents[1] / 'images/gc8_sfd_csfd_gc.png'
data = json.loads(J.read_text())['bins']
NAMES = ('sfd', 'csfd', 'difference'); COLORS = ('#0072B2', '#D55E00', '#009E73')
LABELS = ('SFD', 'CSFD', 'CSFD − SFD'); EDGES = [(.2,.34),(.34,.49),(.49,.59),(.59,.71),(.71,.83),(.83,1.)]
make_cycles.setup_font()
TICK, LAB = 26, 28
plt.rcParams.update({'font.size': TICK})
fig, axes = plt.subplots(2, 3, figsize=(15, 7.8), dpi=200, sharex=True, sharey=True,
                         gridspec_kw={'wspace': 0.06, 'hspace': 0.32})
for i, ax in enumerate(axes.flat, 1):
    for k, (n, c, lab) in enumerate(zip(NAMES, COLORS, LABELS)):
        x = data[str(i)][n]
        ax.errorbar(np.array(x['ell'])*np.exp((k-1)*.035), x['r'], yerr=x['sigma_r'],
                    fmt=('o','s','^')[k], ms=6.5, capsize=0, lw=1.8, color=c, label=lab)
    ax.axhline(0, color='#535B67', lw=1.2)
    ax.set_xscale('log'); ax.set_xlim(95, 3200); ax.set_ylim(-0.75, 0.65)
    ax.set_yticks([-0.5, 0, 0.5]); ax.set_yticklabels(['−0.5', '0', '0.5'])
    ax.set_title(rf'$\delta_{i}$   ${EDGES[i-1][0]:.2f}<z_\mathrm{{ph}}<{EDGES[i-1][1]:.2f}$', fontsize=LAB, pad=6)
    ax.tick_params(labelsize=TICK, length=7, width=1.3)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    if i in (1, 4): ax.set_ylabel(r'$\rho_\ell(\delta,S)$', fontsize=LAB)
    if i >= 4: ax.set_xlabel(r'$\ell$', fontsize=LAB)
fig.legend(*axes[0,0].get_legend_handles_labels(), loc='lower center', ncol=3, frameon=False,
           fontsize=LAB, bbox_to_anchor=(0.5, -0.025), handletextpad=0.3, columnspacing=2.5)
fig.subplots_adjust(left=0.095, right=0.995, top=0.925, bottom=0.235)
fig.savefig(OUT, dpi=200)
print(OUT)
