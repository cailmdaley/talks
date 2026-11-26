"""The first UNIONS release's harmonic-space posterior, read from the paper's own vector figure.

Guerrini et al. 2026 (arXiv:2605.13543), Figures/cosmological_constraints_cl_vs_xi/contours_s8_omegam_cell.pdf in the
arXiv source: the 68 and 95 % contours of "UNIONS C_ell (This work)" in (Omega_m, S8) and its two marginal densities,
as the paths GetDist drew them. Axes are calibrated on the figure's tick marks. Writes unions_release_contours.json.

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
CRIMSON = (.863, .078, .235)


def points(drawing):
    """The drawing's longest subpath: a filled 95 % band is the outer contour and the 68 % one as its hole."""
    paths, end = [], None
    for item in drawing['items']:
        pts = [(p.x, p.y) for p in item[1:] if isinstance(p, pymupdf.Point)]
        if end is None or np.hypot(pts[0][0] - end[0], pts[0][1] - end[1]) > 1e-3:
            paths.append([])
        paths[-1] += pts
        end = pts[-1]
    return np.array(max(paths, key=lambda q: np.ptp(np.array(q), axis=0).prod()))


def main():
    page = pymupdf.open(sys.argv[1])[0]
    d = page.get_drawings()
    fills = [x for x in d if x['type'] == 'f' and len(x['items']) > 100]
    lines = [x for x in d if x['type'] == 's' and x.get('color') and np.allclose(x['color'], CRIMSON, atol=.01)
             and len(x['items']) > 100]
    out = {}
    for name, f in (('95', fills[0]), ('68', fills[1])):          # the first two fills are the C_ell contours
        p = points(f)
        out[name] = {'Omega_m': OM(p[:, 0]).round(4).tolist(), 'S8': S8_Y(p[:, 1]).round(4).tolist()}
    for x in lines:
        r = x['rect']
        p = points(x)
        if r.y1 < 670:                                            # top left: Omega_m
            out['Omega_m'] = {'x': OM(p[:, 0]).round(4).tolist(), 'p': (665.1 - p[:, 1]).round(2).tolist()}
        elif r.x0 > 750:                                          # bottom right: S8
            out['S8'] = {'x': S8_X(p[:, 0]).round(4).tolist(), 'p': (1323.1 - p[:, 1]).round(2).tolist()}
    Path(__file__).with_name('unions_release_contours.json').write_text(json.dumps(out) + '\n')
    for k, v in out.items():
        print(k, {a: (min(b), max(b), len(b)) for a, b in v.items()})


if __name__ == '__main__':
    main()
