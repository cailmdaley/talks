#!/usr/bin/env python3
"""Exploratory C2 MetaCal maps and marginal E/B template nulls.
Uses exactly select_wl -> coverage filter -> wl_cat2map, outer:pixel, map2cls.
"""
import json, pickle, sys, gc, time
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from kappa_common import ROOT, digest
sys.path.insert(0,str(ROOT/'workflow/scripts'))
import systematics_cycle2 as c2
import tr1_systematics as base
from wl_mask_weights import reweight_wl_bin

def main():
    import healpy as hp
    import pymaster as nmt
    import polars as pl
    from scipy.stats import chi2
    from dr1_cmbx.eDR1data import spectra as s
    from dr1_cmbx.eDR1data.maps import select_wl, wl_cat2map
    from build_wl_map import filter_by_footprint
    out=ROOT/'results/scratch/gc8/metacal';out.mkdir(parents=True,exist_ok=True)
    release=json.loads((ROOT/'results/tr1_v2/survey/release.json').read_text())
    catalog=release['catalogs']['wl']['path']; coverage=release['masks']['wl_coverage']['path']
    mapsfile=out/'metacal_maps.pkl'
    if not mapsfile.exists():
        cat=select_wl(pl.scan_parquet(catalog),method='metacal',survey='tr1')
        cat=filter_by_footprint(cat,hp.read_map(coverage,dtype=float)>0,2048)
        wl_cat2map(cat,method='metacal',bins=(1,2,3,4,5,6),combined=False,nside=2048,pol_conv='EUCLID',filename=str(mapsfile),source_catalog=catalog,verbose=True)
    with open(mapsfile,'rb') as f: meta=pickle.load(f)
    lens_tar=ROOT/'results/tr1_v2/map_products/wl_shear_maps_coverage.tar'
    lensfiles=base._ordered_wl(lens_tar,out/'lensmc_reference')
    rows=[]
    for i,lp in enumerate(lensfiles,1):
        m=meta[f'bin{i}'];l=base._load_wl_bin(lp,i,2048)
        def stats(d):
            return {k:float(d[k]) for k in ['n_eff_global','nmean_srad','sigma_eps_comp','c1_sub','c2_sub']}|dict(white_noise=float(d['sigma_eps_comp']**2/d['nmean_srad']),pixels=len(d['ipix']))
        ms,ls=stats(m),stats(l); ratio=ms['white_noise']/ls['white_noise']
        if not np.isfinite(ratio) or ratio<=0: raise ValueError('invalid MetaCal noise')
        rows.append(dict(bin=i,metacal=ms,lensmc=ls,white_noise_ratio=ratio))
    (out/'noise_check.json').write_text(json.dumps(rows,indent=2)+'\n')
    (out/'HEADLINE.md').write_text('# Exploratory Cycle-2 MetaCal\n\nMaps built with production corrected ellipticity, weights, TR1 quality selection and coverage support.\nNoise floor ratios MetaCal/LensMC: '+', '.join(f"{r['white_noise_ratio']:.3f}" for r in rows)+'.\nNulls still running; no mock-calibrated claim.\n')
    print('NOISE CHECK',rows,flush=True)
    bundle=ROOT/'results/tr1_v2/systematics/template_bundle.tar'
    inputs=[digest(p) for p in [catalog,coverage,mapsfile,lens_tar,bundle,Path(__file__),ROOT/'workflow/scripts/build_wl_map.py',ROOT/'code/dr1_cmbx/src/dr1_cmbx/eDR1data/maps.py',ROOT/'code/dr1_cmbx/src/dr1_cmbx/eDR1data/spectra.py']]
    args=SimpleNamespace(nside=2048,lmin=100,lmax=3000,nbins=15,field_lmax=6143,aposcale=0.15,work_dir=out,workspace_cache=out/'workspaces')
    templates=c2.read_bundle(bundle,out/'bundle_extract',2048)
    bins,_=s.make_bins(100,3000,nells=15,spacing='log',field_lmax=6143);sl=s.science_slice(bins);ell=bins.get_effective_ells()[sl]
    for i in range(1,7):
        d=reweight_wl_bin(meta[f'bin{i}'],'outer:pixel')
        _,fields=s.map2cls(wl={f'bin{i}':d},skipped_pairs=[('l0','l0')],covariance=None,return_fields=True,outdir=str(out),outfile=f'fields_bin{i}.pkl',**c2.map_options(args))
        sf=fields['l0'];ss=nmt.get_iNKA_cell(sf,sf)
        for stem,(values,support) in templates.items():
            dest=out/f'{stem}_bin{i}.json'
            if dest.exists():continue
            tick=time.monotonic();window=nmt.mask_apodization(support.astype(float),0.15,apotype='C2')
            tf=s.make_field(values,window,lmax=6143,lmax_mask=6143,n_iter=0)
            tt=nmt.get_iNKA_cell(tf,tf);zero=np.zeros((2,6144))
            w=s.get_workspace(tf,sf,bins,wksp_cache=str(args.workspace_cache))
            observed=w.decouple_cell(nmt.compute_coupled_cell(tf,sf))[:,sl]
            _,raw,cw=s.compute_gaussian_covariance(tf,sf,tf,sf,bins,wksp_ab=w,wksp_cd=w,fiducial_spectra={'11':tt,'12':zero,'21':zero,'22':ss},wksp_cache=str(args.workspace_cache))
            raw=raw.reshape(bins.get_n_bands(),2,bins.get_n_bands(),2)
            result=dict(template=stem,bin=i,ell=ell.tolist(),inputs=inputs,method='NaMaster Gaussian iNKA; zero template-data Wick; full 15x15 per component',mock_calibrated=False,wl_window='outer:pixel, coverage-support',pol_conv='EUCLID',field_lmax=6143,n_iter=0,seconds=time.monotonic()-tick,components={})
            for j,label in enumerate(['E','B']):
                cov=raw[:,j,:,j][sl,sl];np.linalg.cholesky(cov);v=observed[j];pull=v/np.sqrt(np.diag(cov));k=int(np.argmax(abs(pull)));q=float(v@np.linalg.solve(cov,v))
                result['components'][label]=dict(values=v.tolist(),covariance=cov.tolist(),chi2=q,pte=float(chi2.sf(q,len(v))),dof=len(v),pulls=pull.tolist(),worst_band=dict(ell=float(ell[k]),signed_gaussian_pull=float(pull[k])))
            dest.write_text(json.dumps(result,indent=2)+'\n'); print(stem,i,[(k,v['pte']) for k,v in result['components'].items()],flush=True)
            records=[json.loads(p.read_text()) for p in sorted(out.glob('*_bin*.json'))]
            text=['# Exploratory Cycle-2 MetaCal E/B template nulls','','Full within-test Gaussian covariance; no cross-test blocks; PTEs not mock calibrated.','','Noise floor ratios MetaCal/LensMC: '+', '.join(f"{r['white_noise_ratio']:.3f}" for r in rows)+'.','','| Template | Bin | Component | chi2/15 | PTE | Worst ell | signed pull |','|---|---:|---|---:|---:|---:|---:|']
            for r in records:
                for label,v in r['components'].items():text.append(f"| {r['template']} | {r['bin']} | {label} | {v['chi2']:.4g} | {v['pte']:.4g} | {v['worst_band']['ell']:.1f} | {v['worst_band']['signed_gaussian_pull']:.3f} |")
            (out/'HEADLINE.md').write_text('\n'.join(text)+'\n')
            del tf,cw,w;gc.collect()
        del sf,fields;gc.collect()
if __name__=='__main__':main()
