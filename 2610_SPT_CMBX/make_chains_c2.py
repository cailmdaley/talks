"""Cycle-2 blinded production posteriors, as cumulative SPT and ACT build frames.

Run: uv run --with numpy --with scipy --with matplotlib --with fonttools --with brotli python 2610_SPT_CMBX/make_chains_c2.py [--full]
--full includes each full-vector posterior when it exists; otherwise two frames are drawn.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CACHE = Path('/leonardo_scratch/large/userexternal/cdaley00/production-rerun-cache')
spec = importlib.util.spec_from_file_location('chains_style', HERE.parent / '2610_KP23_Napoli/make_chains.py')
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)
plt = style.plt
RUNS = [('kappa_only', r'$\kappa\gamma + \kappa\delta$', '#1D6C78'),
        ('kappa_gl', r'$+\ \gamma\delta$', '#9C7414'),
        ('full', r'5×2pt: 3×2pt + $\kappa\gamma + \kappa\delta$', '#2E417C')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--full', action='store_true', default=True, help='auto-detect and include available full-vector posteriors')
    args = parser.parse_args()
    data, paths = {}, {}
    for cmb, universe in [('spt', 'tr1_v2'), ('act', 'tr1_v2_act')]:
        paths[cmb] = {}
        for run, _, _ in RUNS[:2]:
            manifest = ROOT / 'results' / universe / 'production_chains' / f'nested_{run}.json'
            paths[cmb][run] = Path(json.loads(manifest.read_text())['root'])
        full = CACHE / f'chains-{cmb}-full2/nested_full/nested'
        if args.full and (full / 'posterior_exact.npz').is_file():
            paths[cmb]['full'] = full
        else:
            print(f'{cmb}: 2 frames; full posterior ' + ('not requested' if not args.full else 'not yet available'))
        data[cmb] = {}
        for run, path in paths[cmb].items():
            with np.load(path / 'posterior_exact.npz', allow_pickle=True) as z:
                d = {str(n): z['derived'][:, i] for i, n in enumerate(z['derived_names'])}
                w = np.exp(z['log_w'] - z['log_w'].max())
            data[cmb][run] = (d['Omega_m'], d['S8'], w / w.sum())

    # Expand only if appreciable posterior mass lies beyond the original axes.
    for axis, name in [(0, 'XLIM'), (1, 'YLIM')]:
        lo, hi = getattr(style, name)
        for runs in data.values():
            for samples in runs.values():
                x, w = samples[axis], samples[2]
                order = np.argsort(x)
                q = np.interp([0.001, 0.999], np.cumsum(w[order]), x[order])
                margin = (hi - lo) * 0.05
                if q[0] < lo + margin:
                    lo = float(q[0] - margin)
                if q[1] > hi - margin:
                    hi = float(q[1] + margin)
        setattr(style, name, (lo, hi))
    print('shared axes:', style.XLIM, style.YLIM)

    style.setup_font()
    plt.rcParams.update({'font.size': 28, 'axes.labelsize': 30, 'xtick.labelsize': 27, 'ytick.labelsize': 27,
                         'axes.linewidth': 2.4, 'axes.edgecolor': style.MUTED, 'axes.labelcolor': style.INK,
                         'xtick.color': style.MUTED, 'ytick.color': style.MUTED, 'xtick.major.size': 12,
                         'ytick.major.size': 12, 'xtick.major.width': 2.4, 'ytick.major.width': 2.4,
                         'axes.spines.top': False, 'axes.spines.right': False})
    stats = {}
    for cmb in data:
        stats[cmb] = {}
        for run, (om, s8, w) in data[cmb].items():
            entry = {'posterior': str(paths[cmb][run] / 'posterior_exact.npz')}
            for name, x in [('S8', s8), ('Omega_m', om)]:
                mean = np.average(x, weights=w)
                entry[name + '_blinded'] = float(mean)
                entry['sigma_' + name] = float(np.sqrt(np.average((x - mean)**2, weights=w)))
            summary = paths[cmb][run] / 'summary.json'
            if summary.exists():
                entry['summary'] = json.loads(summary.read_text())
            stats[cmb][run] = entry
        for k in range(1, len(data[cmb]) + 1):
            fig = plt.figure(figsize=(style.W_PX / style.DPI, style.H_PX / style.DPI), dpi=style.DPI)
            ax = fig.add_axes([0.15, 0.17, 0.82, 0.62])
            handles = []
            for i, (run, label, color) in enumerate(RUNS[:k]):
                style.contour(ax, *data[cmb][run], color, 2 + i)
                handles.append(Patch(facecolor=color, alpha=.6, edgecolor=color, label=label))
            ax.set_xlim(style.XLIM); ax.set_ylim(style.YLIM)
            ax.set_xticks([0.2, 0.6, 1.0, 1.4]); ax.set_yticks([0.7, 0.8, 0.9, 1.0, 1.1])
            ax.set_xlim(style.XLIM); ax.set_ylim(style.YLIM)
            ax.set_xlabel(r'$\Omega_\mathrm{m}$'); ax.set_ylabel(r'$S_8$ (blinded)', labelpad=10)
            ax.legend(handles=handles, loc='lower left', bbox_to_anchor=(-0.02, 1.02), ncol=2, frameon=False,
                      fontsize=28, handlelength=1.2, handletextpad=0.4, columnspacing=1.2, borderaxespad=0)
            out = HERE.parent / 'images' / f'spt_chains_c2_{cmb}_{k}.png'
            fig.savefig(out, dpi=style.DPI); plt.close(fig)
            print('wrote', out)
    (HERE / 'chains_c2.json').write_text(json.dumps(stats, indent=2) + '\n')
    for cmb, runs in stats.items():
        for run, s in runs.items():
            print(f"{cmb} {run}: S8 {s['S8_blinded']:.3f} ± {s['sigma_S8']:.3f}; Omega_m {s['Omega_m_blinded']:.3f} ± {s['sigma_Omega_m']:.3f}")


if __name__ == '__main__':
    main()
