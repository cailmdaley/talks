"""DR1 6x2pt forecast: what CMB lensing adds to Euclid DR1 3x2pt, in the (Omega_m, S8) plane and on shear m.

Reads the nested-sampling posteriors of the noiseless DR1 chains, chain names dr1_<kappa>_<probes>, from
/leonardo_scratch/large/userexternal/cdaley00/dr1-forecast: slim.npz (derived parameters and weights) and slim_ice.npz
(the same, with shear m and source redshift shifts, for the two chains whose priors on both are ten times wider).
Everything is drawn relative to the input cosmology. Writes to images/:
  ice_dr1_forecast_<k>.png   build frames: the 3x2pt alone; the 5x2pt with SPT-3G and with ACT over it; the 6x2pt in
                             their place; the wide-prior 3x2pt and 5x2pt (its own, wider axes)
  ice_dr1_shear_m.png        shear m of each source bin in the wide-prior chains, 3x2pt against 5x2pt
and dr1_forecast.json (sigma of S8, Omega_m, sigma8 for every chain, and the figure of merit 1/sqrt(det C) of
(Omega_m, S8)).

Run: uv run --with "getdist @ git+https://github.com/benabed/getdist.git@113cd22a9a0d013b6f72fe734be81f260f3d3be5" \
       --with fonttools --with brotli python \
       2611_ICE_Barcelona/make_dr1_forecast.py --src ~/scratch/dr1fc/slim.npz --wide ~/scratch/ice-chains/slim_ice.npz
"""
from __future__ import annotations

import argparse
import json

import numpy as np

from contour_style import D, HERE, Chain, joint, save, style

plt = style.plt
DERIVED = ['sigma8', 'S8', 'Omega_m']
EUCLID, SPT, ACT = '#535B67', '#C0392B', '#2E6F95'


def stats(z, name):
    d, w = z[name + '|d'].astype(float), z[name + '|w'].astype(float)
    w /= w.sum(); m = w @ d
    s = np.sqrt(w @ (d - m) ** 2)
    out = {n: {'mean': round(float(a), 4), 'sigma': round(float(b), 4)} for n, a, b in zip(DERIVED, m, s)}
    q = d[:, [DERIVED.index('Omega_m'), DERIVED.index('S8')]] - m[[DERIVED.index('Omega_m'), DERIVED.index('S8')]]
    out['fom'] = round(float(np.linalg.det((q * w[:, None]).T @ q) ** -0.5))
    return out


def chain(z, name, label, color, fill=True):
    d = z[name + '|d']
    return Chain({n: d[:, DERIVED.index(n)] for n in ('Omega_m', 'S8')}, z[name + '|w'], label, color, fill)


def fig_m(z):
    """Mean and sigma of each bin's m, with the prior's sigma as a band."""
    fig = plt.figure(figsize=(1330 / style.DPI, style.H_PX / style.DPI), dpi=style.DPI)
    ax = fig.add_axes([.24, .17, .74, .66])
    ax.axhspan(-.1, .1, color=style.MUTED, alpha=.10, lw=0, zorder=0)
    ax.axhline(0, color=style.MUTED, lw=1.2, alpha=.6, zorder=1)
    ax.text(6.4, .094, r'prior, $\pm0.10$', color=style.MUTED, fontsize=27, va='top', ha='right')
    for k, (name, label, color, dx) in enumerate([('dr1_3x2_pw10', '3×2pt', EUCLID, -.14),
                                                  ('dr1_MS_5x2_pw10', '5×2pt, SPT-3G', SPT, .14)]):
        w = z[name + '|w'].astype(float); w /= w.sum()
        x = z[name + '|x'][:, [list(z[name + '|xn']).index(f'm_{i}') for i in range(6)]]
        m = w @ x; s = np.sqrt(w @ (x - m) ** 2)
        ax.errorbar(np.arange(1, 7) + dx, m, yerr=s, fmt='o', color=color, ms=12, lw=6, zorder=3)
        fig.text(.24, .945 - .06 * k, label, color=color, fontsize=27, va='center')
        print(name, 'sigma(m)', s.round(4))
    ax.set_xlim(.5, 6.5); ax.set_ylim(-.12, .12)
    ax.set_xticks(range(1, 7)); ax.set_yticks([-.1, -.05, 0, .05, .1])
    ax.set_xlabel('source redshift bin'); ax.set_ylabel('shear bias $m$', labelpad=6)
    save(fig, 'ice_dr1_shear_m.png')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--src', required=True)
    p.add_argument('--wide', required=True)
    args = p.parse_args()
    z, zw = np.load(args.src), np.load(args.wide)
    truth = dict(zip(DERIVED, z['dr1_3x2|t'].astype(float)))
    base = chain(z, 'dr1_3x2', '3×2pt', EUCLID)
    frames = [[base]] + [[base, chain(z, f'dr1_MS_{n}x2', f'{n}×2pt, SPT-3G', SPT),
                          chain(z, f'dr1_A_{n}x2', f'{n}×2pt, ACT DR6', ACT, False)] for n in (5, 6)]
    frames.append([chain(zw, 'dr1_3x2_pw10', '3×2pt, free $m$', EUCLID),
                   chain(zw, 'dr1_MS_5x2_pw10', '5×2pt, free $m$', SPT),
                   chain(z, 'dr1_3x2', '3×2pt, $m$ to 1 %', style.INK, False)])
    for k, chains in enumerate(frames, 1):
        wide = k == 4
        fig = joint(chains, 'Omega_m', 'S8', D,
                    {'Omega_m': (-.08, .08) if wide else (-.07, .07), 'S8': (-.095, .095) if wide else (-.036, .036)},
                    ticks={'Omega_m': [-.05, 0, .05], 'S8': [-.05, 0, .05] if wide else [-.02, 0, .02]},
                    center=truth, rows=3, decimals={'Omega_m': 3, 'S8': 4})
        save(fig, f'ice_dr1_forecast_{k}.png')
    fig_m(zw)
    names = sorted({k.split('|')[0] for k in z.files if k.startswith(('dr1_', 'tr1_'))})
    out = {n: stats(z, n) for n in names} | {n: stats(zw, n) for n in ('dr1_3x2_pw10', 'dr1_MS_5x2_pw10')}
    (HERE / 'dr1_forecast.json').write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
