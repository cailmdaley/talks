"""UNIONS v2 forecast in the (Omega_m, S8) plane: cosmic shear alone, then the 3x2pt with the LSx lenses.

Reads the nested-sampling posteriors (slim_fir.npz: derived parameters and weights of each chain). The two drawn are
chains on the model prediction with no noise added, run on fir (~/scratch/ufc there): v092f_first_LL_hi_s1 and
v092f_first_3x2_hi_s1. Names without a prefix are the 25 November chains from Leonardo, mockg_* chains on noisy Gaussian
skies and glass_* chains on GLASS mocks.
The contours are drawn relative to the input cosmology. Under them, in grey, is the first release's harmonic-space
posterior (unions_release_contours.json, read from the paper's figure by digitize_unions_release.py), shifted so that
the mean of each of its marginals sits at zero: its row shows that marginal with its standard deviation. Writes images/ice_unions_forecast_<k>.png (build frames) and unions_forecast.json (mean and sigma of S8, Omega_m and
sigma8 of every chain, the figure of merit 1/sqrt(det C) of (Omega_m, S8), and the wall time).

Run: uv run --with "getdist @ git+https://github.com/benabed/getdist.git@113cd22a9a0d013b6f72fe734be81f260f3d3be5" \
       --with fonttools --with brotli python \
       2611_ICE_Barcelona/make_unions_forecast.py --src ~/scratch/ufc-fir/slim_fir.npz
"""
from __future__ import annotations

import argparse
import json

import numpy as np

import make_dr1_forecast as dr1
from contour_style import D, HERE, posteriors, save, style

SHEAR, JOINT = '#3D5BA0', '#A8403A'
TRUTH = dict(Omega_m=0.3190, S8=0.8387)
RELEASE, RELEASE_LABEL = style.MUTED, 'first release'
LAYERS = [('v092f_first_LL_hi_s1', 'cosmic shear', SHEAR), ('v092f_first_3x2_hi_s1', '3×2pt', JOINT)]


def moments(x, p):
    """Mean and standard deviation of a density sampled along x."""
    x, p = np.asarray(x), np.asarray(p)
    m = np.trapezoid(x * p, x) / np.trapezoid(p, x)
    return m, np.sqrt(np.trapezoid((x - m) ** 2 * p, x) / np.trapezoid(p, x))


def add_release(fig, chains):
    """Draw the first release under the chains: contours, and a row at the foot of each marginal panel."""
    rel = json.loads((HERE / 'unions_release_contours.json').read_text())
    mom = {n: moments(rel[n]['x'], rel[n]['p']) for n in ('S8', 'Omega_m')}
    contour, top, right = fig.axes[0], fig.axes[1], fig.axes[2]
    for level, alpha in (('95', .13), ('68', .22)):
        xy = np.column_stack([np.array(rel[level]['S8']) - mom['S8'][0], np.array(rel[level]['Omega_m']) - mom['Omega_m'][0]])
        contour.fill(*xy.T, fc=RELEASE, ec='none', alpha=alpha, zorder=.5)
        contour.plot(*xy.T, color=RELEASE, lw=2.2, alpha=.7, zorder=.6)
    for ax, n in ((top, 'S8'), (right, 'Omega_m')):
        size, pad = ax.texts[0].get_fontsize(), ax.texts[0].get_position()[1] % 1 - 1
        for a in list(ax.lines) + list(ax.texts) + list(ax.collections):   # every row moves up one
            if isinstance(a, style.plt.Line2D):
                if a.get_transform() == ax.transData:
                    a.set_ydata(np.asarray(a.get_ydata(), float) + 1)
            elif isinstance(a, style.plt.Text):
                a.set_y(a.get_position()[1] + 1)
            else:
                a.set_segments([seg + [0, 1] for seg in a.get_segments()])
        m, s = mom[n]
        x, p = np.array(rel[n]['x']) - m, np.array(rel[n]['p'])
        ax.plot(x, .5 * p / p.max(), color=RELEASE, lw=3., zorder=2, clip_on=True)
        ax.plot([-s, s], [0, 0], color=RELEASE, lw=3., zorder=2)
        ax.plot([0], [0], 'o', color=RELEASE, ms=11, zorder=2.1)
        ax.text(0, pad, rf'$\pm {s:.3f}$', color=RELEASE, fontsize=size, ha='center', va='baseline', zorder=1.5,
                path_effects=ax.texts[0].get_path_effects())
    old = fig.legends[0]
    handles = old.legend_handles + [style.plt.matplotlib.patches.Patch(fc=RELEASE, ec=RELEASE, alpha=.45)]
    labels = [t.get_text() for t in old.get_texts()] + [RELEASE_LABEL]
    pos = contour.get_position()
    fig.legends.clear()
    leg = fig.legend(handles, labels, frameon=False, fontsize=size, handlelength=1.2, handletextpad=.5, labelspacing=.45,
                     borderaxespad=0, alignment='left', loc='upper left', bbox_to_anchor=(pos.x1 + .022, top.get_position().y1))
    for h in leg.get_patches():
        h.set_height(18)
    return {n: {'mean': round(float(m), 4), 'sigma': round(float(s), 4)} for n, (m, s) in mom.items()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--src', required=True)
    z = np.load(p.parse_args().src)
    chains = [dr1.chain(z, *layer) for layer in LAYERS]
    for k in (1, 2):
        fig = posteriors(chains[:k], D, center=TRUTH, value=False, rows=3,
                         lims={'Omega_m': (-.27, .40), 'S8': (-.23, .25)},
                         ticks={'Omega_m': [-.2, 0, .2], 'S8': [-.2, 0, .2]})
        release = add_release(fig, chains[:k])
        save(fig, f'ice_unions_forecast_{k}.png')
    names = sorted({k.split('|')[0] for k in z.files})
    (HERE / 'unions_forecast.json').write_text(
        json.dumps({'first_release_digitized': release,
                    **{n: {**dr1.stats(z, n), 'wall_s': round(float(z[n + '|wall']))} for n in names}}, indent=1) + '\n')


if __name__ == '__main__':
    main()
