"""The first UNIONS release's posteriors in harmonic and real space, read from the paper's own vector figure.

Guerrini et al. 2026 (arXiv:2605.13543), Figures/cosmological_constraints_cl_vs_xi/contours_s8_omegam_cell.pdf in the
arXiv source: the 68 and 95 % contours in (Omega_m, S8) and the two marginal densities of "UNIONS C_ell (This work)"
and of "UNIONS xi_pm (Goh et al., 2026)", as the paths GetDist drew them, with the curves flattened. Axes are
calibrated on the figure's tick marks. Writes unions_release_contours.json, keyed harmonic and real.

Run: curl -sL https://arxiv.org/e-print/2605.13543 | tar -xz -C <dir>
     uv run --with pymupdf python 2611_ICE_Barcelona/digitize_unions_release.py <dir>/Figures/cosmological_constraints_cl_vs_xi/contours_s8_omegam_cell.pdf
"""
import json
import sys
from pathlib import Path

import numpy as np
import pymupdf

OM = lambda x: .2 + (x - 265.7) / (460.4 - 265.7) * .2            # x of the left column
S8_Y = lambda y: .6 + (y - 1275.4) / (744.4 - 1275.4) * .5        # y of the contour panel
S8_X = lambda x: .6 + (x - 808.8) / (1341.7 - 808.8) * .5         # x of the S8 marginal
COLORS = {'harmonic': (.863, .078, .235), 'real': (1., .647, 0.)}  # the lines; fills come in the same order
T = np.linspace(0, 1, 9)[1:, None]


def path(drawing):
    """The drawing's longest subpath: a filled 95 % band is the outer contour and the 68 % one as its hole."""
    paths, end = [], None
    for item in drawing['items']:
        p = np.array([(q.x, q.y) for q in item[1:]])
        if end is None or np.hypot(*(p[0] - end)) > 1e-3:
            paths.append([p[0]])
        if item[0] == 'c':
            paths[-1] += list((1 - T) ** 3 * p[0] + 3 * (1 - T) ** 2 * T * p[1] + 3 * (1 - T) * T ** 2 * p[2] + T ** 3 * p[3])
        else:
            paths[-1].append(p[-1])
        end = p[-1]
    return max((np.array(q) for q in paths), key=lambda q: np.ptp(q, axis=0).prod())


def main():
    d = pymupdf.open(sys.argv[1])[0].get_drawings()
    fills = [x for x in d if x['type'] == 'f' and len(x['items']) > 100]
    out = {}
    for k, (name, color) in enumerate(COLORS.items()):
        o = out[name] = {}
        for level, f in zip(('95', '68'), fills[2 * k:2 * k + 2]):
            p = path(f)
            o[level] = {'Omega_m': OM(p[:, 0]).round(4).tolist(), 'S8': S8_Y(p[:, 1]).round(4).tolist()}
        for x in d:
            if x['type'] == 's' and x.get('color') and np.allclose(x['color'], color, atol=.01) and len(x['items']) > 100:
                p, r = path(x), x['rect']
                if r.y1 < 670:                                    # top left: Omega_m
                    o['Omega_m'] = {'x': OM(p[:, 0]).round(4).tolist(), 'p': (665.1 - p[:, 1]).round(2).tolist()}
                elif r.x0 > 750:                                  # bottom right: S8
                    o['S8'] = {'x': S8_X(p[:, 0]).round(4).tolist(), 'p': (1323.1 - p[:, 1]).round(2).tolist()}
        print(name, {a: {b: (min(c), max(c), len(c)) for b, c in v.items()} for a, v in o.items()})
    Path(__file__).with_name('unions_release_contours.json').write_text(json.dumps(out) + '\n')


if __name__ == '__main__':
    main()
