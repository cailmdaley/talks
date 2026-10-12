"""Napoli foreground-pattern figure, drawn only from scratch correlation JSON.

Run: app python docs/talks/2610_Napoli_CMBX/make_cib_extinction.py
No scientific library, HEALPix, NaMaster or tracer autos are loaded here.
The deck's actual setup_font() is reused without importing its mock-data loader.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
from pathlib import Path
import tempfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.ticker import NullFormatter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = Path(HERE).parents[2]
DEFAULT_INPUT = ROOT / 'results/scratch/napoli/cib_extinction/cib_pattern.json'
DEFAULT_OUTPUT = Path(HERE).parent / 'images/napoli_cib_extinction.png'
INK, MUTED = '#111418', '#535B67'
COBALT, TEAL, OCHRE = '#2E417C', '#1D6C78', '#9C7414'
RULE = '#C6CEDA'
W_PX, H_PX, DPI = 3424, 1300, 200
TICK, LABEL = 22, 24


def setup_font():
    """Execute the unchanged font function, not the module's science imports."""
    source = Path(HERE) / 'make_mock_recovery.py'
    tree = ast.parse(source.read_text())
    function = next(node for node in tree.body
                    if isinstance(node, ast.FunctionDef) and node.name == 'setup_font')
    namespace = {'os': os, 'tempfile': tempfile, 'font_manager': font_manager,
                 'plt': plt, 'HERE': HERE}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), 'exec'), namespace)
    namespace['setup_font']()


def draw(data, output):
    setup_font()
    plt.rcParams['mathtext.cal'] = plt.rcParams['mathtext.rm']
    plt.rcParams.update({
        'font.size': LABEL, 'axes.labelsize': LABEL,
        'xtick.labelsize': TICK, 'ytick.labelsize': TICK,
        'axes.linewidth': 1.4, 'axes.edgecolor': MUTED,
        'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': MUTED,
        'xtick.major.size': 7, 'ytick.major.size': 7,
        'xtick.major.width': 1.4, 'ytick.major.width': 1.4,
        'axes.spines.top': False, 'axes.spines.right': False,
        'figure.facecolor': 'white', 'axes.facecolor': 'white',
    })
    fig = plt.figure(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI)
    a = fig.add_axes([.095, .245, .36, .435])
    b = fig.add_axes([.57, .245, .41, .435])
    ell = np.asarray(data['ell'])
    # The grey range is the predeclared average used in B, not a confidence band.
    a.axvspan(300, 2000, color=RULE, alpha=.20, lw=0)
    a.axhline(0, color=MUTED, lw=1.3)
    styles = [
        ('extinction', 'Extinction', COBALT, 'o', '-'),
        ('exposures', 'Exposures', MUTED, 's', '-'),
        ('noise', 'Noise', INK, '^', ':'),
        ('psf', 'PSF', TEAL, 'v', '--'),
        ('stars', 'Stars', OCHRE, 'D', '-.'),
        ('zodiacal', 'Zodiacal', MUTED, 'x', '--'),
    ]
    handles = []
    lo, hi = 0., 0.
    for name, label, color, marker, line in styles:
        x = data['panel_a']['templates'][name]
        r, sig = np.asarray(x['r']), np.asarray(x['sigma'])
        prominent = name == 'extinction'
        a.errorbar(ell, r, yerr=sig, color=color, fmt=marker, ls=line,
                    lw=2.6 if prominent else 1.25, ms=6 if prominent else 4,
                    elinewidth=1.5 if prominent else .85,
                    alpha=1 if prominent else .65, capsize=0,
                    zorder=5 if prominent else 2, label=label)
        handles.append(Line2D([], [], color=color, marker=marker, ls=line,
                              lw=2.6 if prominent else 1.4, ms=7, label=label))
        lo = min(lo, np.min(r-sig))
        hi = max(hi, np.max(r+sig))
    padding = .045*(hi-lo)
    a.set_ylim(lo-padding, hi+padding)
    a.set_xscale('log')
    a.set_xlim(95, 3050)
    a.set_xticks([100, 300, 1000, 3000], ['100', '300', '1000', '3000'])
    a.xaxis.set_minor_formatter(NullFormatter())
    a.set_xlabel(r'Multipole $\ell$', labelpad=8)
    a.set_ylabel(r'$r_\ell$(template, CIB 545)', labelpad=8)
    a.legend(handles=handles, loc='lower left', bbox_to_anchor=(-.015, 1.03),
             ncol=2, fontsize=LABEL, frameon=False, handlelength=1.8,
             columnspacing=1.4, handletextpad=.45, borderaxespad=0)
    fig.text(.095, .965, 'A', color=INK, fontsize=LABEL, va='top')

    keys = [*[f'g{i}' for i in range(6)], 'kappa']
    xticks = [*[rf'$\delta_{i}$' for i in range(1, 7)], r'$\kappa$' + '\nSPT-3G']
    b.axhline(0, color=MUTED, lw=1.3)
    series = [
        (0, -.20, COBALT, 'o', r'Measured: $r(T,\mathrm{extinction})$'),
        (1, 0., TEAL, 's', r'CIB route: $r(T,\mathrm{CIB})\,r(\mathrm{extinction},\mathrm{CIB})$'),
        (2, .20, OCHRE, '^', r'Clean dust: $r(T,\mathrm{dust})$'),
    ]
    for index, offset, color, marker, label in series:
        values = np.array([data['panel_b'][key]['mean'][index] for key in keys])
        sigma = np.array([data['panel_b'][key]['mean_sigma'][index] for key in keys])
        b.errorbar(np.arange(7)+offset, values, yerr=sigma,
                   fmt=marker, color=color, ms=9, capsize=4,
                   elinewidth=1.8, mec='white', mew=.8, label=label)
    b.set_xticks(np.arange(7), xticks)
    b.set_xlim(-.6, 6.6)
    b.set_ylabel(r'Mean correlation coefficient $r$', labelpad=8)
    b.legend(loc='lower left', bbox_to_anchor=(-.015, 1.03), ncol=1,
             fontsize=LABEL, frameon=False, handletextpad=.45, borderaxespad=0)
    fig.text(.57, .965, 'B', color=INK, fontsize=LABEL, va='top')
    fig.text(.52, .085,
             r'Shading: B’s band-centre range $\ell=300$–$2000$; equal band weights, matched masks; bars: $1\sigma$ joint Gaussian.',
             ha='center', va='center', fontsize=TICK, color=MUTED)
    all_positive = all(data['panel_b'][key]['mean'][j] > 0 for key in keys for j in [0, 1])
    sign = 'Positive tracer means have the CIB-expected sign. ' if all_positive else ''
    fig.text(.52, .008, sign + 'CIB route: a projection through the observed CIB map, not a fitted amplitude.',
             ha='center', va='bottom', fontsize=TICK, color=INK)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=DPI)
    plt.close(fig)
    print('wrote', output)
    print('dimensions:', W_PX, H_PX)
    for key in keys:
        row = data['panel_b'][key]
        print(key, 'mean:', row['mean'], 'sigma:', row['mean_sigma'],
              'measured-minus-route / sigma:', row['residual_z'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=DEFAULT_INPUT)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    draw(json.loads(args.input.read_text()), args.output)


if __name__ == '__main__':
    main()
