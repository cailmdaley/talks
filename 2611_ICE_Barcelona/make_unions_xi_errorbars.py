"""Non-tomographic UNIONS v2 xi+ and xi- (concealed) with two sets of error bars, coloured by
release: the first release's covariance and v2's. Writes images/unions_xi_errorbars.png.

The points and bars are read off the two frames images/unions_xi_blink_{old,new}.png (2400 x 1000,
identical except the bars), whose axes are fixed: xi+ y in [0.3, 1.5], xi- y in [-0.15, 1.35],
20 log bins in theta listed in THETA. Both frames show the full-area v2 sample (170.6 M galaxies,
4690 deg^2) with OneCovariance Gaussian + non-Gaussian + SSC errors.

Run: uv run --with numpy --with scipy --with pillow --with matplotlib --with fonttools --with brotli \
       python 2611_ICE_Barcelona/make_unions_xi_errorbars.py
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('chains_style', HERE.parent / '2610_KP23_Napoli/make_chains.py')
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)
plt = style.plt

INK, MUTED, RULE, ACCENT = '#1B1611', '#685D4B', '#C5B89E', '#B03E32'
FIRST = '#C97B6E'
THETA = np.array([1.1656642514519624, 1.536421375750621, 2.0250241358898715, 2.669007616104,
                  3.5176989478470797, 4.6361444064867605, 6.11034080098325, 8.053100297561006,
                  10.613352397270301, 13.987723324477045, 18.435986026847495, 24.295626348109124,
                  32.020066870911954, 42.199524042911854, 55.615679176162416, 73.295267054184,
                  96.5941186997687, 127.2983059131898, 167.7677425692767, 221.09635683564235])
PANELS = {'+': ((21, 23, 26), (0.3, 1.5)), '-': ((59, 111, 160), (-0.15, 1.35))}


def read_bars(path, half, rgb, yrange):
    """Bar ends in data units for the 20 bins of one panel (half 0 = left, 1 = right)."""
    im = np.asarray(Image.open(path).convert('RGB')).astype(int)
    w = im.shape[1] // 2
    im = im[:, half * w:(half + 1) * w]
    dark = im.sum(axis=2) < 150
    rows = np.where(dark.sum(axis=1) > 0.6 * w)[0]          # the frame's top and bottom spines
    top, bottom = rows.min(), rows.max()
    cols = np.where(dark.sum(axis=0) > 0.5 * (bottom - top))[0]   # its left and right spines
    left, right = cols.min(), cols.max()
    mark = (np.abs(im - np.array(rgb)).sum(axis=2) < 40)
    mark[:top + 4] = False; mark[bottom - 3:] = False
    mark[:, :left + 4] = False; mark[:, right - 3:] = False
    height = mark.sum(axis=0)
    on = np.where(height > 0)[0]
    groups = np.split(on, np.where(np.diff(on) > 3)[0] + 1)
    assert len(groups) == 20, len(groups)
    lo, hi = [], []
    for g in groups:
        c = g[np.argmax(height[g])]                          # the bar's own column
        r = np.where(mark[:, c])[0]
        y = lambda row: yrange[0] + (bottom - row) / (bottom - top) * (yrange[1] - yrange[0])
        lo.append(y(r.max() + 0.5)); hi.append(y(r.min() - 0.5))
    return np.array(lo), np.array(hi)


def main():
    style.setup_font()
    plt.rcParams.update({'font.size': 34, 'xtick.labelsize': 32, 'ytick.labelsize': 32,
                         'axes.linewidth': 2.4, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK,
                         'xtick.color': MUTED, 'ytick.color': MUTED, 'xtick.major.size': 12,
                         'ytick.major.size': 12, 'xtick.major.width': 2.4, 'ytick.major.width': 2.4,
                         'xtick.minor.size': 6, 'xtick.minor.width': 1.6,
                         'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(2, 1, figsize=(1800 / 200, 1700 / 200), dpi=200, sharex=True)
    fig.subplots_adjust(left=0.105, right=0.985, top=0.985, bottom=0.2, hspace=0.09)
    for ax, (sign, (rgb, yr)), half in zip(axes, PANELS.items(), (0, 1)):
        lo1, hi1 = read_bars(HERE / 'images/unions_xi_blink_old.png', half, rgb, yr)
        lo2, hi2 = read_bars(HERE / 'images/unions_xi_blink_new.png', half, rgb, yr)
        mid = 0.5 * (lo2 + hi2)
        print(f'xi{sign}: sigma_v2/sigma_first, bins inside 12-83 arcmin:',
              np.round(((hi2 - lo2) / (hi1 - lo1))[(THETA > 12) & (THETA < 83)], 2))
        ax.axvspan(1, 12, color=RULE, alpha=0.13, lw=0); ax.axvspan(83, 250, color=RULE, alpha=0.13, lw=0)
        if sign == '-':
            ax.axhline(0, color=MUTED, lw=1.2)
        ax.vlines(THETA, lo1, hi1, color=FIRST, lw=5, capstyle='butt')
        ax.vlines(THETA, lo2, hi2, color=INK, lw=5, capstyle='butt')
        ax.plot(THETA, mid, 'o', color=INK, ms=10)
        ax.set_xscale('log'); ax.set_xlim(1, 250); ax.set_ylim(*yr)
        ax.set_yticks([0.5, 1.0] if sign == '+' else [0, 0.5, 1.0])
        ax.text(0.03, 0.9, rf'$10^4\,\theta\,\xi_{sign}$', transform=ax.transAxes, color=INK, va='top')
    axes[1].text(0.03, 0.70, 'first-release errors', transform=axes[1].transAxes, color=FIRST, va='top')
    axes[1].text(0.03, 0.56, 'v2 errors', transform=axes[1].transAxes, color=INK, va='top')
    axes[1].set_xticks([1, 10, 100]); axes[1].set_xticklabels(['1', '10', '100'])
    axes[1].set_xlabel(r'$\theta$ [arcmin]')
    out = HERE / 'images/unions_xi_errorbars.png'
    fig.savefig(out, dpi=200, transparent=True); plt.close(fig)
    print('wrote', out)


if __name__ == '__main__':
    main()
