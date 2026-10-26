#!/usr/bin/env python3
"""Authorized talk-only GNILC extension of the SFD/CSFD rho path.

Prediction recorded before computation: GNILC should correlate less than
VMPZ/SFD, but small-scale residuals may prevent CSFD-like nulls.
No production inputs or lc products are modified.
"""
import importlib.util
import itertools
import json
import pickle
import sys
from pathlib import Path
import numpy as np
import healpy as hp
ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'results/scratch/gc8/rho'
FIBER = Path.home() / 'loom/.felt/science/cmbx/gc8-systematics-update'
sys.path[:0] = [str(FIBER), str(ROOT / 'workflow/scripts')]
import sofia_cross as tool
import systematics_cycle2 as c2
import rho_missing as missing
import rho_collect as collect
SOURCE = Path('/leonardo_work/EUHPC_E07_074/cmbx/inputs/planck/maps/gnilc/COM_CompMap_Dust-GNILC-F545_2048_R2.00.fits')

def prepare():
    (OUT / 'gnilc_prediction.txt').write_text(__doc__ + '\n')
    values, valid = tool.read_template(SOURCE, 2048, coord='G')
    templates = c2.read_bundle(ROOT / 'results/tr1_v2/systematics/template_bundle.tar', OUT / 'bundle', 2048)
    support = templates['GALACTICEXTINCTION_VIS'][1]
    previous = hp.read_map(ROOT / 'results/scratch/gc8/union_support.fits') > 0
    assert np.array_equal(support, previous)
    assert valid[support].all()
    np.save(OUT / 'gnilc.npy', values)
    (OUT / 'gnilc_support_parity.json').write_text(json.dumps(dict(public_dust_vs_bundle_support_equal=True, different_pixels=int(np.count_nonzero(support != previous)), support_pixels=int(support.sum()), valid_gnilc_on_support=int(valid[support].sum()), source=str(SOURCE), rotation='sofia_cross.read_template G->C, interpolate at 2*NSIDE then area average', template_response='beam/interpolation retained, identical SFD/CSFD policy'), indent=2))

def gc(ib):
    path = OUT / f'gnilc-bin{ib}.json'
    if path.exists(): return
    d, fp, w = tool.load_gc(ROOT / 'results/tr1_v2/map_products/gc_density_maps.pkl', ib)
    support = hp.read_map(ROOT / 'results/scratch/gc8/union_support.fits') > 0
    # Bin 5 was the original pilot and stores its six cached blocks in covcache/.
    cache_name = 'covcache' if ib == 5 else f'covcache-bin{ib}'
    result = tool.cross_spectra(d, fp, w, np.load(OUT / 'gnilc.npy'), support, cache=str(ROOT / 'results/scratch/gc8' / cache_name))
    result.update(bin=ib, template='gnilc', exploratory=True, source=str(SOURCE))
    path.write_text(json.dumps(result, default=tool.jsonable, indent=2, allow_nan=False))
    print(ib, result['chi2'], result['pte'], flush=True)

def wl(control=False):
    support = hp.read_map(ROOT / 'results/scratch/gc8/union_support.fits') > 0
    values = np.load(ROOT / 'results/scratch/gc8/sfd.npy' if control else OUT / 'gnilc.npy')
    values[support] -= values[support].mean(); values[~support] = 0
    maps = c2.canonical_maps(missing.args, OUT / 'maps')[1]
    rec = json.loads((ROOT / 'results/tr1_v2/survey/kappa.json').read_text())
    masks = json.loads((ROOT / 'results/tr1_v2/map_products/pair_apodized_masks.json').read_text())
    mp = Path(masks['root']) / next(x['path'] for x in masks['files'] if x['path'].endswith('_apod_mask.fits'))
    names = ['kappa'] + [f'l{i}' for i in range(6)] + ['y']
    skip = [p for p in itertools.combinations_with_replacement(names, 2) if 'y' not in p] + [('y', 'y')]
    missing.product('c2_sfd_control_wl_kappa.pkl' if control else 'c2_gnilc_wl_kappa.pkl', wl=maps, kappa=dict(map=rec['map']['path'], mask=str(mp)), y=dict(map=values, mask=support.astype(float), aposcale=.15), skipped_pairs=skip)

def summarize():
    data = json.loads((OUT / 'rho.json').read_text())
    # Keep the exact saved SFD/CSFD theory snapshot: live theory may have rerun.
    edges = np.unique(np.geomspace(100, 3000, 16).astype(int)); edges[-1] = 3001
    ell = np.array([(a+b-1)/2 for a,b in zip(edges[:-1], edges[1:])])
    auto = np.asarray(json.loads((OUT / 'gnilc-bin1.json').read_text())['observed_auto_template'])
    cross = pickle.load(open(OUT / 'c2_gnilc_wl_kappa.pkl', 'rb'))
    for key in [f'g{i}' for i in range(6)] + [f'l{i}' for i in range(6)] + ['kappa']:
        f, i = ('k', 0) if key == 'kappa' else ('g', int(key[1:])+1) if key[0]=='g' else ('e', int(key[1:])+1)
        state = 'vis' if key[0]=='g' else 'native'
        xx = np.asarray(data['rows'][f'c2/sfd/{key}/{state}']['tracer_signal_auto'])
        if key[0]=='g':
            p = OUT / f'gnilc-bin{i}.json'; d = json.loads(p.read_text()); cl, cov = d['cl'], d['covariance_cl']
            ref = json.loads((ROOT / f'results/scratch/gc8/sfd-bin{i}.json').read_text())
            assert d['window_sha256'] == ref['window_sha256']
        else:
            p = OUT / 'c2_gnilc_wl_kappa.pkl'; ck = 'kappa_y' if key=='kappa' else 'y_'+key
            cl, cov = collect.vec(cross, ck), collect.block(cross, ck)
        state = 'vis' if key[0]=='g' else 'native'
        data['rows'][f'c2/gnilc/{key}/{state}'] = collect.row(cl, cov, xx, auto, ell, cycle='c2', template='gnilc', tracer=key, visibility=state, source=str(p), covariance_prescription='observed iNKA Gaussian, full 15x15 cross block, measured cross Wick')
    data['gnilc'] = dict(source=str(SOURCE), prediction=__doc__, theory_snapshot='Exact tracer_signal_auto arrays from saved c2/sfd rows, not regenerated live theory', shear_snapshot_parity=json.loads((OUT / 'shear_snapshot_parity.json').read_text()), support_parity=json.loads((OUT / 'gnilc_support_parity.json').read_text()), response='Retained 5 arcmin beam and rotation/interpolation response as for SFD/CSFD. No E(B-V) conversion; rho is amplitude-free. Beam cancels in ideal narrow-band rho, not exactly under mask coupling/band averaging; no claim of beam-independent precision at ell=3000.')
    for p in [SOURCE, OUT/'gnilc.npy', OUT/'c2_gnilc_wl_kappa.pkl'] + list(OUT.glob('gnilc-bin*.json')):
        collect.receipt(p)
    for p in [Path(__file__), Path(__file__).with_name('gnilc_plot.py'), Path(__file__).with_name('gnilc_verify.py'), FIBER/'sofia_cross.py', ROOT/'workflow/scripts/systematics_cycle2.py', ROOT/'code/dr1_cmbx/src/dr1_cmbx/eDR1data/spectra.py']:
        collect.receipt(p)
    data['gnilc_input_versions'] = list(collect.RECEIPTS.values())
    data['inputs'].extend(collect.RECEIPTS.values())
    (OUT / 'rho_four_dust.json').write_text(json.dumps(data, default=collect.safe, indent=2, allow_nan=False)+'\n')
    lines = ['|Tracer|VMPZ|SFD|CSFD|GNILC|', '|---|---|---|---|---|']
    for key in [f'g{i}' for i in range(6)] + [f'l{i}' for i in range(6)] + ['kappa']:
        state = 'vis' if key[0]=='g' else 'native'
        rs = [data['rows'][f'c2/{d}/{key}/{state}'] for d in ['vmpz','sfd','csfd','gnilc']]
        lines.append('|'+key+'|'+'|'.join(f'{r["mean_rho"]:+.4f} ± {r["mean_rho_error"]:.4f}' for r in rs)+'|')
        r=rs[-1]; print(key, r['chi2'], r['pte'], r['worst_band'], flush=True)
    (OUT / 'gnilc_table.md').write_text('\n'.join(lines)+'\n')

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'prepare': prepare()
    elif mode == 'wl': wl()
    elif mode == 'control': wl(control=True)
    elif mode == 'collect': summarize()
    else:
        import fcntl
        with open(OUT / f'gnilc-bin{int(mode)}.lock', 'w') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            gc(int(mode))
