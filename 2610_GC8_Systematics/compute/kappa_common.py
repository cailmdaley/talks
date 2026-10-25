#!/usr/bin/env python3
"""Talk-only marginal nulls; production C2 scalar operators, zero cross Wick.
Common window = delivered apodized CMB window * C2-apodized template support.
Never writes lc-managed products. Resume at each test JSON.
"""
import argparse, hashlib, json, sys, tarfile, time, gc
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'workflow/scripts'))
import systematics_cycle2 as c2

def digest(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(8*1024**2),b''): h.update(b)
    return dict(path=str(Path(p).resolve()),sha256=h.hexdigest())

def main():
    import healpy as hp
    import pymaster as nmt
    from scipy.stats import chi2
    from dr1_cmbx.eDR1data import spectra as s
    p=argparse.ArgumentParser(); p.add_argument('--experiment',choices=['spt','act'],required=True); p.add_argument('--cycle',default='tr1_v2'); a=p.parse_args()
    universe=a.cycle+('_act' if a.experiment=='act' else '')
    out=ROOT/'results/scratch/gc8/kappa_common'/universe; out.mkdir(parents=True,exist_ok=True)
    cache=out/'workspaces';cache.mkdir(exist_ok=True)
    kr=ROOT/f'results/{universe}/survey/kappa.json'
    krecord=json.loads(kr.read_text()); kp=krecord['map']['path']
    mr=ROOT/f'results/{universe}/map_products/pair_apodized_masks.json'
    md=json.loads(mr.read_text()); maskpath=Path(md['root'])/next(x['path'] for x in md['files'] if x['path'].endswith('_apod_mask.fits'))
    bundle=ROOT/f'results/{a.cycle}/systematics/template_bundle.tar'
    inputs=[digest(x) for x in [kp,maskpath,bundle,kr,mr,Path(__file__),ROOT/'workflow/scripts/systematics_cycle2.py',ROOT/'code/dr1_cmbx/src/dr1_cmbx/eDR1data/spectra.py']]
    kmap=hp.read_map(kp,dtype=float); kmask=hp.read_map(maskpath,dtype=float)
    templates=c2.read_bundle(bundle,out/'bundle_extract',2048)
    bins,_=s.make_bins(100,3000,nells=15,spacing='log',field_lmax=6143); sl=s.science_slice(bins); ell=bins.get_effective_ells()[sl]
    pixelarea=hp.nside2pixarea(2048,degrees=True)
    def field(v,w): return s.make_field(v,w,lmax=6143,lmax_mask=6143,n_iter=0)
    full=field(kmap,kmask); fullauto=nmt.get_iNKA_cell(full,full)
    for stem,(values,support) in templates.items():
        window=nmt.mask_apodization(support.astype(float),0.15,apotype='C2')
        tf=field(values,window); tt=nmt.get_iNKA_cell(tf,tf)
        for mode in ['full','common']:
            dest=out/f'{stem}_{mode}.json'
            if dest.exists(): continue
            tick=time.monotonic(); kw=kmask if mode=='full' else kmask*window
            kf=full if mode=='full' else field(kmap,kw)
            kk=fullauto if mode=='full' else nmt.get_iNKA_cell(kf,kf)
            w=s.get_workspace(tf,kf,bins,wksp_cache=str(cache))
            measured=w.decouple_cell(nmt.compute_coupled_cell(tf,kf))[0,sl]
            zero=np.zeros_like(tt)
            cov,_,cw=s.compute_gaussian_covariance(tf,kf,tf,kf,bins,wksp_ab=w,wksp_cd=w,
                fiducial_spectra={'11':tt,'12':zero,'21':zero,'22':kk},wksp_cache=str(cache))
            cov=cov[sl,sl]; np.linalg.cholesky(cov)
            q=float(measured@np.linalg.solve(cov,measured)); pull=measured/np.sqrt(np.diag(cov)); j=int(np.argmax(abs(pull)))
            area=dict(template_positive_deg2=float(support.sum()*pixelarea),cmb_positive_deg2=float((kmask>0).sum()*pixelarea),overlap_positive_deg2=float((support&(kmask>0)).sum()*pixelarea),kappa_window_positive_deg2=float((kw>0).sum()*pixelarea),kappa_window_integral_deg2=float(kw.sum()*pixelarea),kappa_window_squared_integral_deg2=float((kw**2).sum()*pixelarea),cross_window_integral_deg2=float((kw*window).sum()*pixelarea))
            result=dict(template=stem,universe=universe,mode=mode,ell=ell.tolist(),values=measured.tolist(),covariance=cov.tolist(),chi2=q,pte=float(chi2.sf(q,len(ell))),dof=len(ell),pulls=pull.tolist(),worst_band=dict(ell=float(ell[j]),signed_gaussian_pull=float(pull[j])),areas=area,inputs=inputs,window_definition='full: delivered apodized CMB; common: delivered CMB * C2 C2-type 0.15deg apodized template GC-union-WL support; template unchanged',null_wick='raw TT x raw kk; template-data Wick zero',field_lmax=6143,n_iter=0,covariance_method='NaMaster Gaussian iNKA full 15x15',mock_calibrated=False,seconds=time.monotonic()-tick)
            dest.write_text(json.dumps(result,indent=2)+'\n'); print(stem,mode,q,result['pte'],result['worst_band'],flush=True)
            del cw,w
            if mode=='common': del kf
            gc.collect()
            records=[json.loads(x.read_text()) for x in sorted(out.glob('*_full.json'))+sorted(out.glob('*_common.json'))]
            lines=['# Exploratory kappa template nulls', '', 'Full within-test Gaussian covariance; zero template-data Wick spectra; PTEs not mock calibrated.', '', '| Template | Window | chi2 / 15 | PTE | Worst ell | signed pull | overlap deg2 |','|---|---|---:|---:|---:|---:|---:|']
            for r in records:
                lines.append(f"| {r['template']} | {r['mode']} | {r['chi2']:.4g} | {r['pte']:.5g} | {r['worst_band']['ell']:.1f} | {r['worst_band']['signed_gaussian_pull']:.3f} | {r['areas']['overlap_positive_deg2']:.3f} |")
            (out/'HEADLINE.md').write_text('\n'.join(lines)+'\n')
        del tf;gc.collect()
if __name__=='__main__':main()
