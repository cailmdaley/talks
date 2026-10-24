"""Scratch Cycle-2 CIB-route test; production inputs are read-only.

Run on a dedicated compute allocation with app python .../compute_cib_cycle2.py.
Uses the Napoli Lenz rotation/beam helpers without modifying their receipts.
Windows follow Cycle-2 GC and outer:pixel WL, not the old fragmented footprint.
"""
import importlib.util
import itertools
import json
import pickle
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from scipy.stats import chi2

R = Path(__file__).resolve().parents[3]
O = R / 'results/scratch/gc8/cib_shape_c2'
sys.path.insert(0, str(R / 'workflow/scripts'))
import systematics_cycle2 as c2
from dr1_cmbx.eDR1data import spectra
spec = importlib.util.spec_from_file_location('napoli_cib', R / 'results/scratch/napoli/cib_shape/compute.py')
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
O.mkdir(parents=True, exist_ok=True)
args = SimpleNamespace(nside=2048, field_lmax=6143, lmin=100, lmax=3000, nbins=15,
                       aposcale=0.15, work_dir=O,
                       gc_pkl=R / 'results/tr1_v2/map_products/gc_density_maps.pkl',
                       wl_tar=R / 'results/tr1_v2/map_products/wl_shear_maps_coverage.tar')


def product(name, **kw):
    path = O / name
    if not path.exists():
        opts = c2.map_options(args)
        opts.pop('wksp_cache')
        spectra.map2cls(outdir=str(O), outfile=name, wksp_cache=str(O / 'workspaces' / name),
                        covariance='namaster', diagonal_cov_only=True, **opts, **kw)
    with path.open('rb') as f:
        return pickle.load(f)


def vec(p, key):
    d = p['cls'][key]
    c = np.asarray(d['cl']).reshape(-1, 15)[0]
    C = np.asarray(d['cov']).reshape(15, 15)
    return c, np.sqrt(np.diag(C))


def main():
    templates = c2.read_bundle(R / 'results/tr1_v2/systematics/template_bundle.tar', O / 'bundle_cache', 2048)
    tmap, support = templates['GALACTICEXTINCTION_VIS']
    gc, wl = c2.canonical_maps(args, O)
    names = [f'g{i}' for i in range(6)] + [f'l{i}' for i in range(6)] + ['y']
    skip = [(a, b) for a, b in itertools.combinations_with_replacement(names, 2)
            if a != b and 'y' not in (a, b)]
    ext = dict(map=tmap, mask=support.astype(float), aposcale=0.15)
    te = product('extinction_tracers.pkl', gc=gc, wl=wl, y=ext, skipped_pairs=skip)
    ell = np.asarray(te['leff'])
    tb = np.asarray(json.loads((R / 'results/scratch/napoli/cib_shape/interp_transfer.json').read_text())['band_mean'])
    for freq in ('857', '545', '353'):
        d = old.lenz_dir(freq, '2.5e+20_gp20')
        mask, _ = old.read_gal(old.lenz_file(d, 'mask_bool'))
        _, bl = old.beam(d)
        fields = {}
        for label, stem in [('full', 'cib_fullmission'), ('odd', 'cib_oddring'), ('even', 'cib_evenring')]:
            gm, _ = old.read_gal(old.lenz_file(d, stem))
            m, w = old.to_equatorial(gm, mask > 0.5, support)
            fields[label] = dict(map=m, mask=w.astype(float), aposcale=0.15, beam=bl)
        ceprod = product(f'{freq}_extinction.pkl', kappa=fields['full'], y=ext)
        halves = product(f'{freq}_halves.pkl', kappa=fields['odd'], y=fields['even'],
                         skipped_pairs=[('kappa', 'kappa'), ('y', 'y')])
        tcprod = product(f'{freq}_tracers.pkl', gc=gc, wl=wl, y=fields['full'],
                         skipped_pairs=list(itertools.combinations_with_replacement(names[:-1], 2)) + [('y','y')])
        ce, sce = vec(ceprod, 'kappa_y'); ce, sce = ce/tb, sce/tb
        cc, scc = vec(halves, 'kappa_y'); cc, scc = cc/tb**2, scc/tb**2
        ee, _ = vec(ceprod, 'y_y')
        out = dict(ell=ell.tolist(), bins={}, cib_map=f'Lenz+19 {freq} GHz, N_HI < 2.5e20',
                   definition='Cycle-2 canonical windows; fixed total autos; diagonal NaMaster Gaussian errors; measured-predicted covariance omitted.',
                   cycle='tr1_v2', template_source='/leonardo_work/EUHPC_E07_074/cmbx/inputs/euclid/tr1_v2/systematics_dr1/galacticextinction_vis_dr1_r2_nside4096.fits')
        for i in range(6):
            for tracer, name in [(f'g{i}', f'delta{i+1}_vis'), (f'l{i}', f'gamma{i+1}')]:
                tt, _ = vec(te, f'{tracer}_{tracer}')
                nl = te['cls'][f'{tracer}_{tracer}'].get('nl')
                noise = np.zeros(15) if nl is None else np.asarray(nl).reshape(-1,15)[0]
                tt = tt + noise
                ct, st = vec(te, f'y_{tracer}')
                tc, stc = vec(tcprod, f'y_{tracer}'); tc, stc = tc/tb, stc/tb
                if np.any(tt <= 0) or np.any(ee <= 0) or np.any(cc <= 0):
                    raise ValueError(f'nonpositive auto {freq} {name}')
                norm = np.sqrt(tt * ee)
                measured, sm = ct/norm, st/norm
                predicted = tc*ce/cc/norm
                sp = np.sqrt((ce/cc/norm*stc)**2 + (tc/cc/norm*sce)**2 + (tc*ce/cc**2/norm*scc)**2)
                pull = (measured-predicted)/np.hypot(sm,sp)
                q = float(pull@pull)
                row = dict(r_measured=measured.tolist(), sigma_measured=sm.tolist(),
                           r_predicted=predicted.tolist(), sigma_predicted=sp.tolist(), pull=pull.tolist(),
                           chi2_diag=q, pte_diag=float(chi2.sf(q,15)), r_T_cib=(tc/np.sqrt(tt*cc)).tolist(),
                           r_cib_ext=(ce/np.sqrt(cc*ee)).tolist(), noise_fraction_of_TT=(noise/tt).tolist())
                out['bins'][name] = row
                j = np.argmax(abs(pull))
                B = np.sum(measured*predicted/sm**2)/np.sum(predicted**2/sm**2)
                sB = 1/np.sqrt(np.sum(predicted**2/sm**2))
                print(freq, name, f'B={B:.4f} +/- {sB:.4f}; chi2={q:.4f}/15 PTE={row["pte_diag"]:.5g}; worst ell={ell[j]:.2f} pull={pull[j]:+.3f}', flush=True)
                for l, m, p, s, ps, z in zip(ell,measured,predicted,sm,sp,pull):
                    print(f'  ell={l:.2f} measured={m:+.6f} +/- {s:.6f} predicted={p:+.6f} +/- {ps:.6f} pull={z:+.3f}', flush=True)
        (O / f'cib_rho_{freq}.json').write_text(json.dumps(out, indent=2)+'\n')


if __name__ == '__main__':
    main()
