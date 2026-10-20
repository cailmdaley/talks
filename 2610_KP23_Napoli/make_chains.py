"""KP2-3 update: blinded TR1 posteriors, kappa-only -> kappa+GL -> 3x2pt -> 5x2pt (3x2pt + kappa), as build frames.

Reads the nautilus posteriors (posterior_exact.npz: production-Limber reweighted) of the blinded
TR1 v1.1 runs in /leonardo_scratch/large/userexternal/cdaley00/tr1-chains/nested/ and draws the
blinded S8 against Omega_m: every run fits the same blinded (cmbx_dr1_a) data vector, so the absolute
values carry the blind's shift. One frame per probe set added; the SPT-3G and ACT DR6 versions share
axes. Writes images/kp23_chains_<cmb>_<k>.png and chains_<cmb>.json (blinded mean and sigma of S8).

Run: uv run --with numpy --with scipy --with matplotlib --with fonttools --with brotli python make_chains.py
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
from matplotlib.patches import Patch
import numpy as np
from scipy.ndimage import gaussian_filter

HERE = Path(__file__).resolve().parent
NESTED = Path('/leonardo_scratch/large/userexternal/cdaley00/tr1-chains/nested')
OUT = HERE.parent / 'images'
INK, MUTED = '#111418', '#535B67'
RUNS = [('kappa_only', r'$\kappa\gamma + \kappa\delta$', '#1D6C78'),
        ('kappa_gl', r'$+\ \gamma\delta$', '#9C7414'),
        ('3x2pt_rep', r'3×2pt: $\gamma\gamma + \gamma\delta + \delta\delta$', '#6E3A8A'),
        ('full_rep', r'5×2pt: 3×2pt + $\kappa\gamma + \kappa\delta$', '#2E417C')]
CMB = {'spt': 'tr1', 'act': 'tr1_act'}
W_PX, H_PX, DPI = 2054, 1542, 200
XLIM, YLIM = (0.1, 1.4), (0.65, 1.13)


def setup_font():
    source = HERE.parent / '2610_Napoli_CMBX/make_mock_recovery.py'
    tree = ast.parse(source.read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'setup_font')
    ns = {'os': os, 'tempfile': tempfile, 'font_manager': font_manager, 'plt': plt,
          'HERE': str(HERE.parent / '2610_Napoli_CMBX')}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(source), 'exec'), ns)
    ns['setup_font']()


def load(run):
    z = np.load(NESTED / run / 'posterior_exact.npz', allow_pickle=True)
    d = {n: z['derived'][:, i] for i, n in enumerate(z['derived_names'])}
    w = np.exp(z['log_w'] - z['log_w'].max())
    return d['Omega_m'], d['S8'], w / w.sum()


def levels(H, fracs=(0.68, 0.95)):
    h = np.sort(H.ravel())[::-1]
    c = np.cumsum(h) / h.sum()
    return sorted(h[np.searchsorted(c, f)] for f in fracs)


def contour(ax, x, y, w, color, z):
    bins = 120
    H, xe, ye = np.histogram2d(x, y, bins=bins, range=[XLIM, YLIM], weights=w)
    H = gaussian_filter(H, 2.2)
    xc, yc = (xe[1:] + xe[:-1]) / 2, (ye[1:] + ye[:-1]) / 2
    lv = levels(H)
    ax.contourf(xc, yc, H.T, levels=[lv[0], H.max() * 1.01], colors=[color], alpha=0.28, zorder=z)
    ax.contourf(xc, yc, H.T, levels=[lv[1], H.max() * 1.01], colors=[color], alpha=0.55, zorder=z + .1)
    ax.contour(xc, yc, H.T, levels=lv, colors=[color], linewidths=2.4, zorder=z + .2)


def draw(cmb):
    setup_font()
    plt.rcParams.update({'font.size': 28, 'axes.labelsize': 30, 'xtick.labelsize': 27, 'ytick.labelsize': 27,
                         'axes.linewidth': 2.4, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK,
                         'xtick.color': MUTED, 'ytick.color': MUTED, 'xtick.major.size': 12,
                         'ytick.major.size': 12, 'xtick.major.width': 2.4, 'ytick.major.width': 2.4,
                         'axes.spines.top': False, 'axes.spines.right': False})
    pre = CMB[cmb]
    stats = {}
    for k in range(1, len(RUNS) + 1):
        fig = plt.figure(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI)
        ax = fig.add_axes([0.15, 0.17, 0.82, 0.62])
        handles = []
        for i, (v, label, color) in enumerate(RUNS[:k]):
            om, s8, w = load(f'{pre}_{v}')
            contour(ax, om, s8, w, color, 2 + i)
            handles.append(Patch(facecolor=color, alpha=.6, edgecolor=color, label=label))
            m = np.average(s8, weights=w)
            stats[v] = {'S8_blinded': float(m), 'sigma_S8': float(np.sqrt(np.average((s8 - m) ** 2, weights=w)))}
        ax.set_xlim(XLIM)
        ax.set_ylim(YLIM)
        ax.set_xticks([0.2, 0.6, 1.0, 1.4])
        ax.set_yticks([0.7, 0.8, 0.9, 1.0, 1.1])
        ax.set_xlabel(r'$\Omega_\mathrm{m}$')
        ax.set_ylabel(r'$S_8$ (blinded)', labelpad=10)
        # Above the axes, two rows, so no entry sits on a contour.
        ax.legend(handles=handles, loc='lower left', bbox_to_anchor=(-0.02, 1.02), ncol=2, frameon=False,
                  fontsize=28, handlelength=1.2, handletextpad=0.4, columnspacing=1.2, borderaxespad=0)
        out = OUT / f'kp23_chains_{cmb}_{k}.png'
        fig.savefig(out, dpi=DPI)
        plt.close(fig)
        print('wrote', out)
    (HERE / f'chains_{cmb}.json').write_text(json.dumps(stats, indent=1) + '\n')
    print(cmb, json.dumps(stats))


if __name__ == '__main__':
    for c in CMB:
        draw(c)
