"""The covariance slide's correlation matrix in the deck's colours and type.

Reads private/ice_covariance_correlation.png, the rendering of the 651-band correlation matrix by
cmbx/paper-figures/talk_covariance_correlation.py in pando (Gaussian below the diagonal, Gaussian + SSC
above, clipped at +-0.20), and redraws it without touching the data: every matrix pixel's RdBu_r colour is
read back to its correlation and laid again in the deck's blue-to-red wash, and the frame, block dividers,
family labels, the two corner labels and the colour bar are drawn afresh in EB Garamond. The pixels under
the source's two corner labels carry no data, so the new labels cover the same patches.

Writes private/ice_covariance_aquarelle.png, the matrix pixel for pixel as in the source.

Run: uv run --with matplotlib --with scipy --with pillow --with fonttools --with brotli python \
       2611_ICE_Barcelona/make_covariance.py
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('chains_style', HERE.parent / '2610_KP23_Napoli/make_chains.py')
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)
style.setup_font()
plt = style.plt
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

SRC = HERE / 'private/ice_covariance_correlation.png'
OUT = HERE / 'private/ice_covariance_aquarelle.png'
VMAX = 0.20
COUNTS = [22, 90, 92, 132, 315]  # fitted bands per family, in the order of the axes
NAMES = ['δκ', 'γκ', 'δδ', 'δγ', 'γγ']
WASH = LinearSegmentedColormap.from_list('aquarelle_div', [
    (0.00, '#1F3566'), (0.22, '#3D5BA0'), (0.40, '#9FBEDB'), (0.50, '#FFFFFF'),
    (0.60, '#E3A9A3'), (0.78, '#A8403A'), (1.00, '#6E221D')])
WASH.set_bad('#FFFFFF')


def frame(dark):
    """Pixel edges of the matrix: the outermost long dark runs that are 651 cells apart."""
    cols, rows = np.where(dark.mean(0) > 0.5)[0], np.where(dark.mean(1) > 0.4)[0]
    x0, y0 = cols[cols < 150].max() + 1, rows[rows < 50].max() + 1
    y1 = rows.max() - 1
    x1 = x0 + (y1 - y0)
    return int(x0), int(x1), int(y0), int(y1)


def read_back(rgb):
    """Correlation of each pixel from its RdBu_r colour, and how far the colour sits from the map."""
    lut = plt.get_cmap('RdBu_r')(np.linspace(0, 1, 1024))[:, :3] * 255
    dist, idx = cKDTree(lut).query(rgb.reshape(-1, 3))
    v = (idx / 1023 * 2 - 1) * VMAX
    return v.reshape(rgb.shape[:2]), dist.reshape(rgb.shape[:2])


def main():
    im = np.asarray(Image.open(SRC).convert('RGB')).astype(float)
    hh, ww, _ = im.shape
    x0, x1, y0, y1 = frame(im.sum(2) < 200)
    n = x1 - x0
    print(f'matrix {n} px square at ({x0}, {y0}) in {ww}x{hh}')
    v, dist = read_back(im[y0:y1, x0:x1])

    # the source's own ink: block dividers, and the two corner labels with their boxes
    edges = np.cumsum([0] + COUNTS) / sum(COUNTS) * n
    yy, xx = np.mgrid[0:n, 0:n]
    rule = np.zeros((n, n), bool)
    for e in edges[1:-1]:
        rule |= (np.abs(xx - e) < 4) | (np.abs(yy - e) < 4)
    off = dist > 5
    labels = []
    for corner in (off & ~rule & (yy < n / 2), off & ~rule & (yy > n / 2)):
        ys, xs = np.where(corner)
        labels.append((int(xs.min()) - 3, int(xs.max()) + 4, int(ys.min()) - 3, int(ys.max()) + 4))
    print('labels cover', labels)
    hole = np.zeros((n, n), bool)
    for a, b, c, d in labels:
        hole[c:d, a:b] = True
    print(f'pixels off the colour map outside rules and labels: {(off & ~rule & ~hole).sum()}')
    bad = rule | off
    v = v[tuple(distance_transform_edt(bad, return_distances=False, return_indices=True))]
    v[hole] = np.nan

    dpi = 218
    hh += 40  # room under the frame for the family labels' descenders
    fig = plt.figure(figsize=(ww / dpi, hh / dpi), dpi=dpi, facecolor='white')
    ax = fig.add_axes([x0 / ww, 1 - y1 / hh, n / ww, n / hh])
    img = ax.imshow(v, cmap=WASH, vmin=-VMAX, vmax=VMAX, interpolation='nearest', extent=(0, n, n, 0))
    for e in edges[1:-1]:
        ax.axhline(e, color=style.INK, lw=1.0)
        ax.axvline(e, color=style.INK, lw=1.0)
    for s in ax.spines.values():
        s.set_color(style.INK)
        s.set_linewidth(1.2)
    mids = (edges[:-1] + edges[1:]) / 2
    ax.set_xticks(mids, NAMES, fontsize=26, color=style.INK)
    ax.set_yticks(mids, NAMES, fontsize=26, color=style.INK)
    ax.tick_params(length=0, pad=7)
    for (a, b, c, d), text in zip(labels, ('Gaussian + SSC', 'Gaussian only')):
        ax.fill([a, b, b, a], [c, c, d, d], color='white', zorder=3, lw=0)
        ax.text((a + b) / 2, (c + d) / 2, text, ha='center', va='center_baseline', fontsize=21,
                color=style.INK, zorder=4)
    cax = fig.add_axes([1592 / ww, 1 - (y1 - 0.05 * n) / hh, 44 / ww, 0.9 * n / hh])
    cb = fig.colorbar(img, cax=cax, extend='both', ticks=[-0.2, -0.1, 0, 0.1, 0.2])
    cb.set_label('correlation', fontsize=23, color=style.INK)
    cb.ax.tick_params(labelsize=20, color=style.MUTED, labelcolor=style.INK, length=6)
    cb.ax.set_yticklabels(['−0.2', '−0.1', '0', '0.1', '0.2'])
    cb.outline.set_edgecolor(style.MUTED)
    cb.outline.set_linewidth(1.0)
    fig.savefig(OUT, dpi=dpi, facecolor='white')
    print('wrote', OUT)


if __name__ == '__main__':
    main()
