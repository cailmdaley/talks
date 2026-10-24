"""GC-8: every TR1 tracer crossed with the VMPZ extinction template, band by band, in Gaussian sigma.

Reads the Cycle-1 lc output results/tr1/tr1_systematics/extinction_vis.tar (its measurement.json:
TR1 v1.1 coverage-only density delta_i, LensMC shear E-modes gamma_i, SPT-3G winter GMV kappa,
each crossed with GALACTICEXTINCTION_VIS) and draws signed_pull = C_ell^{T,ext} / sigma_G per band,
three panels on one y axis. The same numbers as the fiber figure extinction_null_pulls.png
(science/cmbx/methodology/systematics/tr1-systematics-crosses/extinction-template-carries-lss),
re-drawn at slide size.

Run: app python docs/talks/2610_GC8_Systematics/make_extinction_pulls.py
"""
from __future__ import annotations

import ast
import json
import os
import tarfile
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TAR = ROOT / 'results/tr1/tr1_systematics/extinction_vis.tar'
OUT = HERE.parent / 'images/gc8_extinction_pulls.png'
INK, MUTED, RULE = '#111418', '#535B67', '#C6CEDA'
W_PX, H_PX, DPI = 3840, 1600, 200
TICK, LABEL = 34, 38
DELTA = LinearSegmentedColormap.from_list('d', ['#9FC3E6', '#14305E'])
GAMMA = LinearSegmentedColormap.from_list('g', ['#E8A3A0', '#7A1712'])


def setup_font():
    """Execute the Napoli deck's font function (EB Garamond from node_modules)."""
    source = HERE.parent / '2610_Napoli_CMBX/make_mock_recovery.py'
    tree = ast.parse(source.read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'setup_font')
    ns = {'os': os, 'tempfile': tempfile, 'font_manager': font_manager, 'plt': plt,
          'HERE': str(HERE.parent / '2610_Napoli_CMBX')}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(source), 'exec'), ns)
    ns['setup_font']()


def main():
    setup_font()
    with tarfile.open(TAR) as t:
        d = json.load(t.extractfile('measurement.json'))
    fig, axs = plt.subplots(1, 3, figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI, sharey=True,
                            gridspec_kw={'wspace': 0.06})
    panels = [(axs[0], d['GC'], DELTA, 'Density δ', r'\delta'),
              (axs[1], d['WL'], GAMMA, 'Shear γ', r'\gamma')]
    for ax, fam, cmap, title, sym in panels:
        for j, r in enumerate(fam.values()):
            ell = np.array(r['ell']) * (1 + 0.015 * (j - 2.5))
            ax.plot(ell, r['signed_pull'], 'o-', ms=7, lw=2.2, color=cmap(j / 5),
                    label=rf'${sym}_{j + 1}$')
        ax.set_title(title, fontsize=LABEL, color=INK, pad=14)
        ax.legend(fontsize=TICK, ncol=3, loc='upper left', frameon=False, handlelength=1.0,
                  columnspacing=0.8, handletextpad=0.3, borderaxespad=0.2)
    r = d['template_kappa']
    axs[2].plot(r['ell'], r['signed_pull'], 'o-', ms=7, lw=2.2, color=INK)
    axs[2].set_title('CMB lensing κ (SPT-3G)', fontsize=LABEL, color=INK, pad=14)
    for ax in axs:
        ax.set_xscale('log')
        ax.set_xlim(90, 3300)
        ax.set_ylim(-2.4, 6.8)
        ax.axhline(0, color=MUTED, lw=1.2)
        ax.axhspan(-1, 1, color='#E3E7EE', zorder=0, lw=0)
        ax.axhspan(-2, 2, color='#F0F2F6', zorder=-1, lw=0)
        ax.set_xlabel(r'$\ell$', fontsize=LABEL, color=INK)
        ax.tick_params(labelsize=TICK, colors=INK, length=8, width=1.4)
        ax.tick_params(which='minor', length=4, width=1)
        for s in ('top', 'right'):
            ax.spines[s].set_visible(False)
        for s in ('left', 'bottom'):
            ax.spines[s].set_color(MUTED)
    axs[0].set_ylabel('cross / Gaussian σ', fontsize=LABEL, color=INK)
    fig.subplots_adjust(left=0.07, right=0.995, bottom=0.18, top=0.89)
    fig.savefig(OUT, dpi=DPI, facecolor='white')
    print('wrote', OUT)


if __name__ == '__main__':
    main()
