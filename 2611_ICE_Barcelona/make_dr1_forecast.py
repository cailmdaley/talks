"""DR1 6x2pt forecast: what CMB lensing adds to Euclid DR1 3x2pt, in the (Omega_m, sigma8) plane.

Reads the nested-sampling posteriors of the noiseless DR1 chains (slim.npz, the derived parameters and weights of
each chain; chain names dr1_<kappa>_<probes>, from /leonardo_scratch/large/userexternal/cdaley00/dr1-forecast).
Writes images/ice_dr1_forecast_<k>.png (build frames: Euclid alone, then with SPT-3G, then with ACT) and
dr1_forecast.json (sigma of S8, Omega_m, sigma8 for every chain).

Run: uv run --with numpy --with scipy --with matplotlib --with fonttools --with brotli \
       python 2611_ICE_Barcelona/make_dr1_forecast.py --src ~/scratch/dr1fc/slim.npz
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from scipy.stats import gaussian_kde

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('chains_style', HERE.parent / '2610_KP23_Napoli/make_chains.py')
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)
plt = style.plt

DERIVED = ['sigma8', 'S8', 'Omega_m']
EUCLID, SPT, ACT = '#535B67', '#C0392B', '#2E6F95'
XLIM, YLIM = (0.25, 0.40), {'S8': (0.805, 0.872), 'sigma8': (0.72, 0.91)}


def stats(z, name):
    d, w = z[name + '|d'].astype(float), z[name + '|w'].astype(float)
    w /= w.sum(); m = w @ d
    s = np.sqrt(w @ (d - m) ** 2)
    return {n: {'mean': round(float(a), 4), 'sigma': round(float(b), 4)} for n, a, b in zip(DERIVED, m, s)}


def density(z, name, y):
    """Smoothed (Omega_m, y) density on a grid, and its 68 and 95 % levels."""
    d, w = z[name + '|d'].astype(float), z[name + '|w'].astype(float)
    x = d[:, [DERIVED.index('Omega_m'), DERIVED.index(y)]].T
    k = gaussian_kde(x, weights=w, bw_method=0.3)
    xc, yc = np.linspace(*XLIM, 160), np.linspace(*YLIM[y], 160)
    H = k(np.stack(np.meshgrid(xc, yc)).reshape(2, -1)).reshape(160, 160)
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
    truth = z['dr1_3x2|t']
    layers = [('dr1_3x2', EUCLID, 'fill', 'Euclid DR1 3×2pt'),
              ('dr1_MS_6x2', SPT, 'fill', '6×2pt with SPT-3G'),
              ('dr1_A_6x2', ACT, 'line', '6×2pt with ACT DR6')]
    for y, ylab, yticks in (('sigma8', r'$\sigma_8$', [0.75, 0.80, 0.85, 0.90]),):
        dens = [density(z, n, y) for n, *_ in layers]
        for k in range(1, 4):
            fig = plt.figure(figsize=(style.W_PX / style.DPI, style.H_PX / style.DPI), dpi=style.DPI)
            ax = fig.add_axes([0.15, 0.17, 0.82, 0.62])
            handles = []
            for i, (name, color, kind, label) in enumerate(layers[:k]):
                xc, yc, H, lv = dens[i]
                if kind == 'fill':
                    ax.contourf(xc, yc, H, levels=[lv[0], H.max() * 1.01], colors=[color], alpha=.28, zorder=2 + i)
                    ax.contourf(xc, yc, H, levels=[lv[1], H.max() * 1.01], colors=[color], alpha=.55, zorder=2.1 + i)
                    ax.contour(xc, yc, H, levels=lv, colors=[color], linewidths=2.4, zorder=2.2 + i)
                    handles.append(Patch(facecolor=color, alpha=.6, edgecolor=color, label=label))
                else:
                    ax.contour(xc, yc, H, levels=lv, colors=[color], linewidths=[2.4, 4.0],
                               linestyles=['--', '-'], zorder=2 + i)
                    handles.append(Line2D([], [], color=color, lw=4, label=label))
            ax.plot(truth[2], truth[DERIVED.index(y)], marker='+', ms=26, mew=3.5, color=style.INK, zorder=9)
            ax.set_xlim(XLIM); ax.set_ylim(YLIM[y])
            ax.set_xticks([0.25, 0.30, 0.35, 0.40]); ax.set_yticks(yticks)
            ax.set_xlabel(r'$\Omega_\mathrm{m}$'); ax.set_ylabel(ylab, labelpad=10)
            ax.legend(handles=handles, loc='lower left', bbox_to_anchor=(-0.02, 1.02), ncol=2, frameon=False,
                      fontsize=28, handlelength=1.4, handletextpad=0.4, columnspacing=1.4, borderaxespad=0)
            out = HERE.parent / 'images' / f'ice_dr1_forecast_{k}.png'
            fig.savefig(out, dpi=style.DPI); plt.close(fig)
            print('wrote', out)
    names = sorted({k.split('|')[0] for k in z.files if k.startswith(('dr1_', 'tr1_'))})
    (HERE / 'dr1_forecast.json').write_text(json.dumps({n: stats(z, n) for n in names}, indent=1) + '\n')


if __name__ == '__main__':
    main()
