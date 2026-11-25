"""UNIONS v2 forecast in the (Omega_m, S8) plane: cosmic shear alone, then the 3x2pt with the LSx lenses.

Reads the nested-sampling posteriors of the noiseless UNIONS x LSx vectors (slim.npz: derived parameters and weights of
each chain, named <cut>_<probes>, from /leonardo_scratch/large/userexternal/cdaley00/unions-forecast).
Writes images/ice_unions_forecast_<k>.png (build frames) and unions_forecast.json (mean and sigma of S8, Omega_m and
sigma8 of every chain, the figure of merit 1/sqrt(det C) of (Omega_m, S8), and the wall time).

Run: uv run --with numpy --with scipy --with matplotlib --with fonttools --with brotli \
       python 2611_ICE_Barcelona/make_unions_forecast.py --src ~/scratch/ufc/slim.npz
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
from matplotlib.patches import Patch
from scipy.stats import gaussian_kde

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('dr1_forecast', HERE / 'make_dr1_forecast.py')
dr1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dr1)
style, plt = dr1.style, dr1.plt

SHEAR, JOINT = '#3D5BA0', '#A8403A'
XLIM, YLIM = (0.1, 0.65), (0.755, 0.915)
TRUTH = dict(Omega_m=0.3190, S8=0.8387)


def density(z, name):
    """Smoothed (Omega_m, S8) density on a grid, and its 68 and 95 % levels."""
    d, w = z[name + '|d'].astype(float), z[name + '|w'].astype(float)
    x = d[:, [dr1.DERIVED.index('Omega_m'), dr1.DERIVED.index('S8')]].T
    xc, yc = np.linspace(*XLIM, 180), np.linspace(*YLIM, 180)
    H = gaussian_kde(x, weights=w, bw_method=0.28)(np.stack(np.meshgrid(xc, yc)).reshape(2, -1)).reshape(180, 180)
    return xc, yc, H, style.levels(H)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--src', required=True)
    args = p.parse_args()
    z = np.load(args.src)
    style.setup_font()
    plt.rcParams.update({'font.size': 28, 'axes.labelsize': 30, 'xtick.labelsize': 27, 'ytick.labelsize': 27,
                         'axes.linewidth': 2.4, 'axes.edgecolor': style.MUTED, 'axes.labelcolor': style.INK,
                         'xtick.color': style.MUTED, 'ytick.color': style.MUTED, 'xtick.major.size': 12,
                         'ytick.major.size': 12, 'xtick.major.width': 2.4, 'ytick.major.width': 2.4,
                         'axes.spines.top': False, 'axes.spines.right': False})
    layers = [('first_LL_hi', SHEAR, 'cosmic shear'), ('first_3x2_hi', JOINT, '3×2pt with SPHEREx lenses')]
    for k in range(1, len(layers) + 1):
        fig = plt.figure(figsize=(style.W_PX / style.DPI, style.H_PX / style.DPI), dpi=style.DPI)
        ax = fig.add_axes([0.15, 0.17, 0.82, 0.62])
        handles = []
        for i, (name, color, label) in enumerate(layers[:k]):
            xc, yc, H, lv = density(z, name)
            ax.contourf(xc, yc, H, levels=[lv[0], H.max() * 1.01], colors=[color], alpha=.28, zorder=2 + i)
            ax.contourf(xc, yc, H, levels=[lv[1], H.max() * 1.01], colors=[color], alpha=.55, zorder=2.1 + i)
            ax.contour(xc, yc, H, levels=lv, colors=[color], linewidths=2.4, zorder=2.2 + i)
            handles.append(Patch(facecolor=color, alpha=.6, edgecolor=color, label=label))
        ax.plot(TRUTH['Omega_m'], TRUTH['S8'], marker='+', ms=26, mew=3.5, color=style.INK, zorder=9)
        ax.set_xlim(XLIM); ax.set_ylim(YLIM)
        ax.set_xticks([0.1, 0.2, 0.3, 0.4, 0.5, 0.6]); ax.set_yticks([0.76, 0.80, 0.84, 0.88])
        ax.set_xlabel(r'$\Omega_\mathrm{m}$'); ax.set_ylabel(r'$S_8$', labelpad=10)
        ax.legend(handles=handles, loc='lower left', bbox_to_anchor=(-0.02, 1.02), ncol=2, frameon=False,
                  fontsize=28, handlelength=1.4, handletextpad=0.4, columnspacing=1.4, borderaxespad=0)
        out = HERE.parent / 'images' / f'ice_unions_forecast_{k}.png'
        fig.savefig(out, dpi=style.DPI); plt.close(fig)
        print('wrote', out)
    names = sorted({k.split('|')[0] for k in z.files})
    (HERE / 'unions_forecast.json').write_text(
        json.dumps({n: {**dr1.stats(z, n), 'wall_s': round(float(z[n + '|wall']))} for n in names}, indent=1) + '\n')


if __name__ == '__main__':
    main()
