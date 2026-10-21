"""SPT-3G vs ACT DR6: per-bandpower error-bar ratio sigma_ACT / sigma_SPT on the kappa crosses, TR1 and DR1.

Reads the Napoli data-vector export (2610_Napoli_CMBX/private/dv_vector.json, LensMC variants), whose
sig is sigma_G, the square root of the diagonal of each survey's full NaMaster Gaussian covariance, for
the 12 kappa crosses (6 shear bins, 6 lens bins) in 15 bandpowers from ell = 100 to 3000. Only error
bars enter, so the figure carries no measured amplitude and is blind-independent.

The twelve crosses give the same ratio to within a few per cent (the CMB-lensing noise sets it), so one
line is drawn: their mean. The DR1 line projects it with sigma proportional to A^-1/2 for each survey's
overlap with Euclid: ratio_DR1 = ratio_TR1 * sqrt((A_ACT,TR1 / A_ACT,DR1) * (A_SPT,DR1 / A_SPT,TR1)).
Writes images/spt_sigma_ratio.png.

Run: uv run --with numpy --with matplotlib --with fonttools --with brotli python make_sigma_ratio.py
"""
from __future__ import annotations

import ast
import json
import os
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
import numpy as np

HERE = Path(__file__).resolve().parent
DV = HERE.parent / '2610_Napoli_CMBX/private/dv_vector.json'
OUT = HERE.parent / 'images/spt_sigma_ratio.png'
INK, MUTED = '#111418', '#535B67'
SHADE = '#1D6C78'
W_PX, H_PX, DPI = 2054, 1542, 200
# overlaps with Euclid, deg²: TR1 from the RR2 photometric footprint (NSIDE 512), DR1 effective (VMPZ R2 valid tiles)
AREA = {'tr1': {'act': 345.0, 'spt': 149.0}, 'dr1': {'act': 1069.0, 'spt': 353.0}}
TR1_C, DR1_C = '#2E417C', '#B3261E'


def setup_font():
    source = HERE.parent / '2610_Napoli_CMBX/make_mock_recovery.py'
    tree = ast.parse(source.read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'setup_font')
    ns = {'os': os, 'tempfile': tempfile, 'font_manager': font_manager, 'plt': plt,
          'HERE': str(HERE.parent / '2610_Napoli_CMBX')}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(source), 'exec'), ns)
    ns['setup_font']()


def main():
    setup_font()
    plt.rcParams.update({'font.size': 28, 'axes.labelsize': 30, 'xtick.labelsize': 27, 'ytick.labelsize': 27,
                         'axes.linewidth': 2.4, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK,
                         'xtick.color': MUTED, 'ytick.color': MUTED, 'xtick.major.size': 12,
                         'ytick.major.size': 12, 'xtick.major.width': 2.4, 'ytick.major.width': 2.4,
                         'xtick.minor.size': 0, 'axes.spines.top': False, 'axes.spines.right': False})
    d = json.load(open(DV))['variants']
    spt, act = d['lensmc|spt'], d['lensmc|act']
    keys = sorted(k for k in spt if k.startswith('kappa_'))
    fig = plt.figure(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI)
    ax = fig.add_axes([0.14, 0.17, 0.80, 0.70])
    ax.axhspan(1, 2.8, color=SHADE, alpha=0.08, lw=0, zorder=0)
    ax.text(125, 2.55, 'SPT-3G tighter', color=SHADE, fontsize=30, va='center')
    ax.text(125, 0.72, 'ACT DR6 tighter', color=MUTED, fontsize=30, va='center')
    ax.axhline(1, color=MUTED, lw=2.4, zorder=1)
    ratios = []
    for k in keys:
        ell = np.array(spt[k]['ell'])
        ratios.append(np.array(act[k]['sig']) / np.array(spt[k]['sig']))
    r = np.array(ratios)
    tr1 = r.mean(0)
    scale = np.sqrt(AREA['tr1']['act'] / AREA['dr1']['act'] * AREA['dr1']['spt'] / AREA['tr1']['spt'])
    dr1 = tr1 * scale
    ax.plot(ell, tr1, color=TR1_C, lw=4, marker='o', ms=9, zorder=3)
    ax.plot(ell, dr1, color=DR1_C, lw=4, marker='o', ms=9, ls='--', zorder=3)
    ax.set_xscale('log')
    ax.set_xlim(100, 3000)
    ax.set_ylim(0.6, 2.8)
    ax.set_xticks([100, 200, 500, 1000, 2000, 3000])
    ax.set_xticklabels(['100', '200', '500', '1000', '2000', '3000'])
    ax.set_yticks([1, 1.5, 2, 2.5])
    ax.set_xlabel(r'$\ell$')
    ax.set_ylabel(r'$\sigma_\mathrm{ACT}\,/\,\sigma_\mathrm{SPT}$', labelpad=10)
    ax.legend(handles=[Line2D([], [], color=TR1_C, lw=4, marker='o', ms=9, label='TR1, measured'),
                       Line2D([], [], color=DR1_C, lw=4, marker='o', ms=9, ls='--', label='DR1, area-scaled')],
              loc='lower left', bbox_to_anchor=(-0.02, 1.0), ncol=2, frameon=False, fontsize=28,
              handlelength=1.8, borderaxespad=0)
    fig.savefig(OUT, dpi=DPI)
    print('wrote', OUT)
    print('ell', np.round(ell).astype(int).tolist())
    print('spread across the 12 crosses (max-min)/mean', np.round(((r.max(0) - r.min(0)) / tr1).max(), 3))
    print('scale', round(float(scale), 3))
    print('tr1', np.round(tr1, 2).tolist())
    print('dr1', np.round(dr1, 2).tolist())


if __name__ == '__main__':
    main()
