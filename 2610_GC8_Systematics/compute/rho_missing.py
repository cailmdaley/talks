#!/usr/bin/env python3
"""Talk-only missing rho crosses, production operators, resumable pickle products."""
import gc, importlib.util, itertools, json, pickle, sys
from pathlib import Path
from types import SimpleNamespace
import numpy as np
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'workflow/scripts'))
import systematics_cycle2 as c2
from dr1_cmbx.eDR1data import spectra
OUT=ROOT/'results/scratch/gc8/rho'
OUT.mkdir(parents=True,exist_ok=True)
args=SimpleNamespace(nside=2048,field_lmax=6143,lmin=100,lmax=3000,nbins=15,aposcale=.15,work_dir=OUT,gc_pkl=ROOT/'results/tr1_v2/map_products/gc_density_maps.pkl',wl_tar=ROOT/'results/tr1_v2/map_products/wl_shear_maps_coverage.tar')

def product(name,**kw):
    if (OUT/name).exists(): return
    opts=c2.map_options(args);opts.pop('wksp_cache')
    print('start',name,flush=True)
    spectra.map2cls(outdir=str(OUT),outfile=name,wksp_cache=str(OUT/'workspaces'/'shared'),covariance='namaster',diagonal_cov_only=True,**opts,**kw)
    print('done',name,flush=True);gc.collect()

def main():
    mode=sys.argv[1]
    templates=c2.read_bundle(ROOT/'results/tr1_v2/systematics/template_bundle.tar',OUT/'bundle',2048)
    tmap,support=templates['GALACTICEXTINCTION_VIS']
    if mode=='raw':
        maps=pickle.load(open(args.gc_pkl,'rb'))
        raw={}
        for i in range(1,7):
            d=dict(maps[f'bin{i}']);counts=np.asarray(d['counts_per_pixel']);mean=counts.mean()
            d.update(map=counts/mean-1,shot_noise_variance=counts/mean**2,nmean_srad=mean/(4*np.pi/(12*2048**2)),noise_cl=(4*np.pi/(12*2048**2))/mean,gc_selection_correction='none; reconstructed from identical supported counts')
            for k in ['weights','selection_coverage','visibility','noise_cl_convention']:d.pop(k,None)
            raw[f'bin{i}']=d
        with open(OUT/'c2_raw_gc.pkl','wb') as f:pickle.dump(raw,f)
        names=[f'g{i}' for i in range(6)]+['y']
        skip=[p for p in itertools.combinations_with_replacement(names,2) if 'y' not in p]
        product('c2_raw_extinction.pkl',gc=raw,y=dict(map=tmap,mask=support.astype(float),aposcale=.15),skipped_pairs=skip)
        spec=importlib.util.spec_from_file_location('old',ROOT/'results/scratch/napoli/cib_shape/compute.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
        d=old.lenz_dir('857','2.5e+20_gp20');gm,_=old.read_gal(old.lenz_file(d,'cib_fullmission'));mask,_=old.read_gal(old.lenz_file(d,'mask_bool'))
        cm,good=old.to_equatorial(gm,mask>.5,support);_,bl=old.beam(d)
        product('c2_raw_cib857.pkl',gc=raw,y=dict(map=cm,mask=good.astype(float),aposcale=.15,beam=bl),skipped_pairs=skip+[('y','y')])
    elif mode in ('dust','kappa'):
        import healpy as hp
        wl=None if mode=='kappa' else c2.canonical_maps(args,OUT/'maps')[1]
        rec=json.loads((ROOT/'results/tr1_v2/survey/kappa.json').read_text())
        masks=json.loads((ROOT/'results/tr1_v2/map_products/pair_apodized_masks.json').read_text())
        kp=rec['map']['path'];mp=Path(masks['root'])/next(x['path'] for x in masks['files'] if x['path'].endswith('_apod_mask.fits'))
        kappa=dict(map=kp,mask=str(mp))
        # This one extra scalar test supplies observed-Wick errors for VMPZ
        # kappa too, so every comparison can use the same covariance policy.
        product('c2_vmpz_kappa.pkl',kappa=kappa,y=dict(map=tmap,mask=support.astype(float),aposcale=.15),skipped_pairs=[('kappa','kappa'),('y','y')])
        if mode=='kappa':return
        names=['kappa']+[f'l{i}' for i in range(6)]+['y']
        skip=[p for p in itertools.combinations_with_replacement(names,2) if 'y' not in p]
        for label in ['sfd','csfd']:
            # Cache created by sofia_cross.read_template: Galactic->Celestial,
            # interpolate at 2*NSIDE then average, valid on the complete union support.
            values=np.load(ROOT/f'results/scratch/gc8/{label}.npy')
            values[support]-=values[support].mean();values[~support]=0
            # Exact same template field as cached public-dust GC spectra;
            # reuse its y_y auto, avoiding a redundant auto covariance.
            product(f'c2_{label}_wl_kappa.pkl',wl=wl,kappa=kappa,y=dict(map=values,mask=support.astype(float),aposcale=.15),skipped_pairs=skip+[('y','y')])
    else:raise ValueError(mode)
if __name__=='__main__':main()
