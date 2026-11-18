"""Blinded TR1 Cycle-2 production posteriors, SPT-3G against ACT DR6, one frame per probe set.

Reads the nested-sampling posteriors (posterior.npz) of the tr1_v2 (SPT-3G) and tr1_v2_act (ACT DR6)
production chains, the ones the cmbx root's results/<universe>/production_chains/nested_<run>.json
manifests point to (pure CLOE through the JAX adapter, 15 Nov 2026). Every chain fits the same blinded
data vector, so absolute positions carry the blind's shift; SPT-3G against ACT DR6 is meaningful.

Frames: kappa crosses alone, kappa crosses + galaxy-galaxy lensing, the full 5x2pt vector. Each frame
draws one probe set for both CMB maps on shared axes. Writes images/ice_chains_spt_act_<k>.png and
chains_spt_act.json.

Run: uv run --with numpy --with scipy --with matplotlib --with fonttools --with brotli \
       python 2611_ICE_Barcelona/make_chains_spt_act.py --src <dir holding {spt,act}_{kappa_only,kappa_gl,full}.npz>
On cineca, --src can be omitted: the lane paths below are read directly.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('chains_style', HERE.parent / '2610_KP23_Napoli/make_chains.py')
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)
plt = style.plt

LANES = Path('/leonardo_scratch/large/userexternal/cdaley00/cmbx-lanes')
UNIVERSE = {'spt': 'fp-spt/results/cache/tr1_v2', 'act': 'fp-act/results/cache/tr1_v2_act'}
CMB = {'spt': ('SPT-3G', '#C0392B'), 'act': ('ACT DR6', '#2E6F95')}
RUNS = [('kappa_only', r'$\kappa\gamma + \kappa\delta$'),
        ('kappa_gl', r'$\kappa\gamma + \kappa\delta + \gamma\delta$'),
        ('full', r'5×2pt: $\gamma\gamma + \gamma\delta + \delta\delta + \kappa\gamma + \kappa\delta$')]
XLIM, YLIM = (0.1, 1.1), (0.62, 1.08)


def load(src, cmb, run):
    path = (Path(src) / f'{cmb}_{run}.npz') if src else (
        LANES / UNIVERSE[cmb] / 'production_chains' / f'nested_{run}' / 'nested' / 'posterior.npz')
    with np.load(path, allow_pickle=True) as z:
        d = {str(n): z['derived'][:, i] for i, n in enumerate(z['derived_names'])}
        w = np.exp(z['log_w'] - z['log_w'].max())
    return d['Omega_m'], d['S8'], w / w.sum()


def outline(ax, x, y, w, color, z):
    """ACT drawn as lines only, so SPT's fill shows through."""
    H, xe, ye = np.histogram2d(x, y, bins=120, range=[XLIM, YLIM], weights=w)
    H = style.gaussian_filter(H, 2.2)
    xc, yc = (xe[1:] + xe[:-1]) / 2, (ye[1:] + ye[:-1]) / 2
    ax.contour(xc, yc, H.T, levels=style.levels(H), colors=[color], linewidths=[2.4, 4.0],
               linestyles=['--', '-'], zorder=z)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--src', help='local directory of copied posteriors')
    args = p.parse_args()
    style.XLIM, style.YLIM = XLIM, YLIM
    style.setup_font()
    plt.rcParams.update({'font.size': 28, 'axes.labelsize': 30, 'xtick.labelsize': 27, 'ytick.labelsize': 27,
                         'axes.linewidth': 2.4, 'axes.edgecolor': style.MUTED, 'axes.labelcolor': style.INK,
                         'xtick.color': style.MUTED, 'ytick.color': style.MUTED, 'xtick.major.size': 12,
                         'ytick.major.size': 12, 'xtick.major.width': 2.4, 'ytick.major.width': 2.4,
                         'axes.spines.top': False, 'axes.spines.right': False})
    stats = {}
    for k, (run, label) in enumerate(RUNS, start=1):
        fig = plt.figure(figsize=(style.W_PX / style.DPI, style.H_PX / style.DPI), dpi=style.DPI)
        ax = fig.add_axes([0.15, 0.17, 0.82, 0.62])
        om, s8, w = load(args.src, 'spt', run)
        style.contour(ax, om, s8, w, CMB['spt'][1], 2)
        om_a, s8_a, w_a = load(args.src, 'act', run)
        outline(ax, om_a, s8_a, w_a, CMB['act'][1], 4)
        for cmb, (x, y, ww) in [('spt', (om, s8, w)), ('act', (om_a, s8_a, w_a))]:
            entry = stats.setdefault(cmb, {}).setdefault(run, {})
            for name, v in [('S8', y), ('Omega_m', x)]:
                m = np.average(v, weights=ww)
                entry[name + '_blinded'] = round(float(m), 4)
                entry['sigma_' + name] = round(float(np.sqrt(np.average((v - m) ** 2, weights=ww))), 4)
        ax.set_xlim(XLIM); ax.set_ylim(YLIM)
        ax.set_xticks([0.2, 0.4, 0.6, 0.8, 1.0]); ax.set_yticks([0.7, 0.8, 0.9, 1.0])
        ax.set_xlabel(r'$\Omega_\mathrm{m}$'); ax.set_ylabel(r'$S_8$ (blinded)', labelpad=10)
        handles = [Patch(facecolor=CMB['spt'][1], alpha=.6, edgecolor=CMB['spt'][1], label=CMB['spt'][0]),
                   Line2D([], [], color=CMB['act'][1], lw=4, label=CMB['act'][0])]
        ax.legend(handles=handles, loc='lower left', bbox_to_anchor=(-0.02, 1.10), ncol=2, frameon=False,
                  fontsize=28, handlelength=1.4, handletextpad=0.4, columnspacing=1.4, borderaxespad=0)
        ax.text(0.0, 1.03, label, transform=ax.transAxes, fontsize=28, color=style.INK, va='bottom')
        out = HERE.parent / 'images' / f'ice_chains_spt_act_{k}.png'
        fig.savefig(out, dpi=style.DPI); plt.close(fig)
        print('wrote', out)
    (HERE / 'chains_spt_act.json').write_text(json.dumps(stats, indent=1) + '\n')
    for cmb, runs in stats.items():
        for run, s in runs.items():
            print(f"{cmb} {run}: S8 {s['S8_blinded']:.3f} ± {s['sigma_S8']:.3f}")


if __name__ == '__main__':
    main()
