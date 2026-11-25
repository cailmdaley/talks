"""Blinded TR1 Cycle-2 production posteriors, SPT-3G against ACT DR6, one frame per probe set.

Reads the nested-sampling posteriors (posterior.npz) of the tr1_v2 (SPT-3G) and tr1_v2_act (ACT DR6)
production chains, the ones the cmbx root's results/<universe>/production_chains/nested_<run>.json
manifests point to (pure CLOE through the JAX adapter, 15 Nov 2026). Every chain fits the same blinded
data vector, so absolute positions carry the blind's shift; SPT-3G against ACT DR6 is meaningful.

Frames: kappa crosses alone, kappa crosses + galaxy-galaxy lensing, the full 5x2pt vector. Each frame
draws one probe set for both CMB maps on shared axes. Writes images/ice_chains_spt_act_<k>.png and
chains_spt_act.json.

Run: uv run --with "getdist @ git+https://github.com/benabed/getdist.git@113cd22a9a0d013b6f72fe734be81f260f3d3be5" \
       --with fonttools --with brotli python \
       2611_ICE_Barcelona/make_chains_spt_act.py --src ~/scratch/ice-chains/slim_ice.npz
slim_ice.npz holds <cmb>_<run>|d, |dn, |w (derived parameters, their names, weights) of the posteriors at
/leonardo_scratch/large/userexternal/cdaley00/cmbx-lanes/fp-{spt,act}/results/cache/tr1_v2{,_act}/production_chains/
nested_<run>/nested/posterior.npz.
"""
from __future__ import annotations

import argparse
import json

import numpy as np

from contour_style import HERE, Chain, posteriors, save

CMB = {'spt': ('SPT-3G', '#C0392B'), 'act': ('ACT DR6', '#2E6F95')}
RUNS = [('kappa_only', r'$\kappa\gamma + \kappa\delta$'),
        ('kappa_gl', r'$\kappa\gamma + \kappa\delta + \gamma\delta$'),
        ('full', '5×2pt')]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--src', required=True)
    z = np.load(p.parse_args().src)
    stats = {c: {} for c in CMB}
    for k, (run, label) in enumerate(RUNS, start=1):
        chains = []
        for cmb, (name, color) in CMB.items():
            names = list(z[f'{cmb}_{run}|dn'])
            d = {n: z[f'{cmb}_{run}|d'][:, names.index(n)] for n in ('Omega_m', 'S8')}
            c = Chain(d, z[f'{cmb}_{run}|w'], name, color, fill=cmb == 'spt')
            chains.append(c)
            stats[cmb][run] = {q: round(float(v), 4) for n in ('S8', 'Omega_m')
                               for q, v in zip((n + '_blinded', 'sigma_' + n), c.sigma(n))}
        fig = posteriors(chains, {'Omega_m': r'\Omega_\mathrm{m}', 'S8': r'S_8\ \mathrm{(blinded)}'}, title=label,
                         lims={'Omega_m': (0, 1.1), 'S8': (.64, 1.08)},
                         ticks={'Omega_m': [.2, .6, 1.], 'S8': [.7, .8, .9, 1.]})
        save(fig, f'ice_chains_spt_act_{k}.png')
    (HERE / 'chains_spt_act.json').write_text(json.dumps(stats, indent=1) + '\n')


if __name__ == '__main__':
    main()
