"""UNIONS v2 forecast in the (Omega_m, S8) plane: cosmic shear alone, then the 3x2pt with the LSx lenses.

Reads the nested-sampling posteriors (slim_fir.npz: derived parameters and weights of each chain). The two drawn are
chains on the model prediction with no noise added, run on fir (~/scratch/ufc there): v092f100_first_LL_hi_s1 and
v092f100_first_3x2_hi_s1, in which the four source bins carry the whole v2 sample's shear weight (their densities
times 1/0.54, as the slide's first bullet says). The v092f_* chains have the bins' own densities. Names without a prefix are the 25 November chains from Leonardo, mockg_* chains on noisy Gaussian
skies and glass_* chains on GLASS mocks.
The contours are drawn relative to the input cosmology. Under them are the first release's posteriors in harmonic
and real space (unions_release_contours.json, read from the paper's figure by digitize_unions_release.py), each shifted
so that the mean of each of its marginals sits at zero and with its contours smoothed in angle; a release's row shows
its marginal with the standard deviation. The first frame shows the release alone. Writes images/ice_unions_forecast_<k>.png (build frames) and unions_forecast.json (mean and sigma of S8, Omega_m and
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
RELEASES = [('harmonic', 'first release, harmonic', style.MUTED, True),
            ('real', 'first release, real space', '#A08A6C', False)]
LAYERS = [('v092f100_first_LL_hi_s1', 'v2 cosmic shear', SHEAR), ('v092f100_first_3x2_hi_s1', 'v2 3×2pt', JOINT)]
PEAK = .36     # height of a marginal density in units of the row spacing, which leaves air above each curve
SMOOTH = 5.   # degrees: width of the smoothing of a digitized contour around its centre


def moments(x, p):
    """Mean and standard deviation of a density sampled along x."""
    x, p = np.asarray(x), np.asarray(p)
    m = np.trapezoid(x * p, x) / np.trapezoid(p, x)
    return m, np.sqrt(np.trapezoid((x - m) ** 2 * p, x) / np.trapezoid(p, x))


def smooth(xy):
    """The contour with its radius about the centre smoothed in angle, which rounds off the chain's sampling spikes."""
    scale = np.ptp(xy, axis=0)
    q = (xy - xy.mean(0)) / scale
    th, r = np.arctan2(q[:, 1], q[:, 0]), np.hypot(*q.T)
    o = np.argsort(th)
    grid = np.linspace(-np.pi, np.pi, 720, endpoint=False)
    r = np.interp(grid, th[o], r[o], period=2 * np.pi)
    k = np.exp(-.5 * (np.minimum(np.arange(720), 720 - np.arange(720)) * .5 / SMOOTH) ** 2)
    r = np.fft.irfft(np.fft.rfft(r) * np.fft.rfft(k / k.sum()), 720)
    out = np.column_stack([r * np.cos(grid), r * np.sin(grid)]) * scale + xy.mean(0)
    return np.vstack([out, out[:1]])


def add_releases(fig, n_chains):
    """Draw the first release under the chains: contours, and a row each at the foot of the marginal panels.

    The first n_chains of the chains drawn are kept, so a frame can show the release alone.
    """
    rel = json.loads((HERE / 'unions_release_contours.json').read_text())
    contour, top, right = fig.axes[0], fig.axes[1], fig.axes[2]
    if not n_chains:
        for c in list(contour.collections):
            c.remove()
    size, pad, effects = top.texts[0].get_fontsize(), top.texts[0].get_position()[1] % 1 - 1, top.texts[0].get_path_effects()
    for ax in (top, right):
        for a in list(ax.lines) + list(ax.texts) + list(ax.collections):   # the chains' rows move above the release's
            data = not isinstance(a, style.plt.Line2D) or a.get_transform() == ax.transData
            if not n_chains and data:
                a.remove()
            elif isinstance(a, style.plt.Line2D) and data:
                y = np.asarray(a.get_ydata(), float)
                base = np.floor(y.min() + 1e-9)
                a.set_ydata(base + (y - base) * PEAK / .5 + len(RELEASES))
            elif isinstance(a, style.plt.Text):
                a.set_y(a.get_position()[1] + len(RELEASES))
            elif data:
                a.set_segments([seg + [0, len(RELEASES)] for seg in a.get_segments()])
    stats, handles = {}, []
    for row, (key, label, color, fill) in enumerate(RELEASES):
        r = rel[key]
        mom = {n: moments(r[n]['x'], r[n]['p']) for n in ('S8', 'Omega_m')}
        for level, alpha in (('95', .13), ('68', .22)):
            xy = smooth(np.column_stack([np.array(r[level]['S8']) - mom['S8'][0],
                                         np.array(r[level]['Omega_m']) - mom['Omega_m'][0]]))
            if fill:
                contour.fill(*xy.T, fc=color, ec='none', alpha=alpha, zorder=.5)
            contour.plot(*xy.T, color=color, lw=2.2 if fill else 3., alpha=.7 if fill else .95, zorder=.6 + .1 * row)
        for ax, n in ((top, 'S8'), (right, 'Omega_m')):
            m, s = mom[n]
            x, p = np.array(r[n]['x']) - m, np.array(r[n]['p'])
            ax.plot(x, row + PEAK * p / p.max(), color=color, lw=3., zorder=2)
            ax.plot([-s, s], [row, row], color=color, lw=3., zorder=2)
            ax.plot([0], [row], 'o', color=color, ms=11, zorder=2.1)
            ax.text(0, row + pad, rf'$\pm {s:.3f}$', color=color, fontsize=size, ha='center', va='baseline', zorder=1.5,
                    path_effects=effects)
        handles.append(style.plt.matplotlib.patches.Patch(fc=color, ec=color, alpha=.45) if fill else
                       style.plt.Line2D([], [], color=color, lw=3.9))
        stats[key] = {n: {'mean': round(float(m), 4), 'sigma': round(float(s), 4)} for n, (m, s) in mom.items()}
    old = fig.legends[0]
    handles = (old.legend_handles if n_chains else []) + handles[::-1]
    labels = ([t.get_text() for t in old.get_texts()] if n_chains else []) + [x[1] for x in RELEASES][::-1]
    fig.legends.clear()
    leg = fig.legend(handles, labels, frameon=False, fontsize=size, handlelength=1.2, handletextpad=.5, labelspacing=.45,
                     borderaxespad=0, alignment='left', loc='upper left',
                     bbox_to_anchor=(contour.get_position().x1 + .022, top.get_position().y1))
    for h in leg.get_patches():
        h.set_height(18)
    return stats


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--src', required=True)
    z = np.load(p.parse_args().src)
    chains = [dr1.chain(z, *layer) for layer in LAYERS]
    for k in (0, 1, 2):
        fig = posteriors(chains[:max(k, 1)], D, center=TRUTH, value=False, rows=len(RELEASES) + 2,
                         lims={'Omega_m': (-.27, .40), 'S8': (-.23, .25)},
                         ticks={'Omega_m': [-.2, 0, .2], 'S8': [-.2, 0, .2]})
        release = add_releases(fig, k)
        save(fig, f'ice_unions_forecast_{k}.png')
    names = sorted({k.split('|')[0] for k in z.files})
    (HERE / 'unions_forecast.json').write_text(
        json.dumps({'first_release_digitized': release,
                    **{n: {**dr1.stats(z, n), 'wall_s': round(float(z[n + '|wall']))} for n in names}}, indent=1) + '\n')


if __name__ == '__main__':
    main()
