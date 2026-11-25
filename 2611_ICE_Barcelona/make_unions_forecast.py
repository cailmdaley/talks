"""UNIONS v2 forecast in the (Omega_m, S8) plane: cosmic shear alone, then the 3x2pt with the LSx lenses.

Reads the nested-sampling posteriors (slim_fir.npz: derived parameters and weights of each chain). The two drawn are
chains on the model prediction with no noise added, run on fir (~/scratch/ufc there): v092f_first_LL_hi_s1 and
v092f_first_3x2_hi_s1. Names without a prefix are the 25 November chains from Leonardo, mockg_* chains on noisy Gaussian
skies and glass_* chains on GLASS mocks.
The contours are drawn relative to the input cosmology. Writes images/ice_unions_forecast_<k>.png (build frames) and unions_forecast.json (mean and sigma of S8, Omega_m and
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
from contour_style import D, HERE, joint, save

SHEAR, JOINT = '#3D5BA0', '#A8403A'
TRUTH = dict(Omega_m=0.3190, S8=0.8387)
LAYERS = [('v092f_first_LL_hi_s1', 'cosmic shear', SHEAR), ('v092f_first_3x2_hi_s1', '3×2pt', JOINT)]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--src', required=True)
    z = np.load(p.parse_args().src)
    chains = [dr1.chain(z, *layer) for layer in LAYERS]
    for k in (1, 2):
        fig = joint(chains[:k], 'Omega_m', 'S8', D, {'Omega_m': (-.24, .36), 'S8': (-.088, .088)},
                    ticks={'Omega_m': [-.2, 0, .2], 'S8': [-.05, 0, .05]}, center=TRUTH, rows=2, side=(.27, .25),
                    split=.5)
        save(fig, f'ice_unions_forecast_{k}.png')
    names = sorted({k.split('|')[0] for k in z.files})
    (HERE / 'unions_forecast.json').write_text(
        json.dumps({n: {**dr1.stats(z, n), 'wall_s': round(float(z[n + '|wall']))} for n in names}, indent=1) + '\n')


if __name__ == '__main__':
    main()
