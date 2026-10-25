#!/usr/bin/env python3
"""Talk-only marginal template nulls with raw E/B Gaussian covariance blocks.

C1 historical windows/iterations and C2 canonical windows follow their recipes.
No joint cross-test covariance is requested. Results are exploratory, not lc outputs.
"""
import sys, os, json, time, itertools, tarfile, pickle, hashlib, gc
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import healpy as hp
import pymaster as nmt
from scipy.stats import chi2
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'workflow/scripts'))
import tr1_systematics as base
import systematics_cycle2 as c2
from dr1_cmbx.eDR1data import spectra as sp
from dr1_cmbx.eDR1data import _covariance_blocks as blocks
from window_leakage import digest
BASE=ROOT/'results/scratch/gc8'
FP=Path('/leonardo_work/EUHPC_E07_074/cmbx/inputs/euclid/masks/tr1_footprint_south_effcov0p8_nside2048.fits')
KMAP=Path('/leonardo_work/EUHPC_E07_074/cmbx/inputs/spt/maps/lensing/winter/gmvbhttprf/kmapxx_kGMVbhTTprf_0_1.fits')
KMASK=Path('/leonardo_work/EUHPC_E07_074/cmbx/inputs/spt/masks/lensing/winter/mask2048_border_apod_mask_threshold0.1_allghz_dense_1500d_eetelensing-1920_mapmaking_mask_list_fluxcut6mJy_clusterSNcut10_dense_bmask2.fits')
NAMES=['extinction_vis','exposures_vis','noise_vis','psf_vis','zodiacal_vis','stars_gaia']

def dump(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix('.tmp');q.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n');q.replace(p)

def receipt(paths):
 return [dict(path=str(p),sha256=digest(p)) for p in paths]

def options(cycle,out):
 return SimpleNamespace(nside=2048,lmin=100,lmax=3000,nbins=15,field_lmax=6143,aposcale=.15,work_dir=str(out),gc_pkl=str(ROOT/f'results/{"tr1" if cycle==1 else "tr1_v2"}/map_products/gc_density_maps.pkl'),wl_tar=str(ROOT/f'results/{"tr1" if cycle==1 else "tr1_v2"}/map_products/{"wl_shear_maps.tar" if cycle==1 else "wl_shear_maps_coverage.tar"}'))

def templates(cycle,out):
 path=ROOT/f'results/{"tr1/tr1_systematics" if cycle==1 else "tr1_v2/systematics"}/template_bundle.tar'
 dest=out/f'extract{cycle}';dest.mkdir(parents=True,exist_ok=True)
 with tarfile.open(path) as t:base._safe_extract(t,dest)
 m=json.loads((dest/'bundle/manifest.json').read_text())
 return [(t['stem'],dest/'bundle'/t['map'],dest/'bundle'/t['mask']) for t in m['templates']],path

def fields(cycle,out,kappa=False,visibility=False):
 args=options(cycle,out);dest=out/f'maps{cycle}';dest.mkdir(parents=True,exist_ok=True)
 if cycle==2:g,w=c2.canonical_maps(args,dest)
 else:
  full=base._load_pickle(args.gc_pkl);g={f'bin{i}':full[f'bin{i}'] for i in range(1,7)}
  w={f'bin{i}':base._load_wl_bin(p,i,2048) for i,p in enumerate(base._ordered_wl(args.wl_tar,dest/'wl'),1)}
 if visibility:
  g=base._load_pickle(ROOT/'results/scratch/napoli/visibility_check/corrected.pkl')
  # Matched weights are necessary for the corrected density's Poisson sampling.
  for i in range(1,7):
   d=np.load(ROOT/f'results/scratch/napoli/visibility_check/maps_bin{i}.npz')
   assert np.array_equal(g[f'bin{i}']['ipix'],d['ipix'])
   g[f'bin{i}']=dict(g[f'bin{i}'],weights=d['w'])
  w=None
 opts=base._common_map_options(args)
 opts.update(n_iter=1 if cycle==1 else 0)
 if cycle==1:opts['extra_masks']={'footprint':np.asarray(hp.read_map(FP,dtype=float))>0}
 names=[f'g{i}' for i in range(6)] + ([f'l{i}' for i in range(6)] if w is not None else []) + (['kappa'] if kappa else [])
 if kappa:opts['kappa']=dict(map=str(KMAP),mask=str(KMASK),aposcale=.15)
 _,f=sp.map2cls(gc=g,wl=w,covariance=None,skipped_pairs=list(itertools.combinations_with_replacement(names,2)),return_fields=True,blind='none',pol_conv='COSMO' if cycle==1 else 'EUCLID',outdir=str(dest),outfile='fields.pkl',**opts)
 del g,w;gc.collect()
 return f,args

def legacy_cache(cycle,out,template):
 # Existing production workspaces are read through individual symlinks; misses
 # write exclusively into scratch. Production cache directories stay untouched.
 cache=out/f'workspace{cycle}'
 for sub in ['wksp_cl','wksp_cov']:
  (cache/sub).mkdir(parents=True,exist_ok=True)
  src=ROOT/f'results/cache/tr1/tr1_systematics/{template}/work/workspace'/sub if cycle==1 else ROOT/'results/cache/tr1_v2/systematics/gaussian_null_family/workspaces'/sub
  if src.exists():
   for p in src.glob('*.fits'):
    q=cache/sub/p.name
    if not q.exists():q.symlink_to(p.resolve())
 return cache

def native_c2(a,b):
 def spec(f):return [hashlib.sha256(np.ascontiguousarray(f.get_mask()).tobytes()).hexdigest(),f.spin,f.ainfo.lmax,f.ainfo_mask.lmax,f.n_iter_mask]
 config=[spec(a),spec(b),spec(a),spec(b)]
 key=hashlib.sha256(json.dumps([blocks.runtime_identity(),config]).encode()).hexdigest()
 p=ROOT/'results/cache/tr1_v2/systematics/gaussian_null_family/covariance/wksp_cov'/f'{key}.fits'
 return nmt.NmtCovarianceWorkspace.from_file(str(p)) if p.exists() else None

def score(x,cov,ell):
 cov=(cov+cov.T)/2;np.linalg.cholesky(cov)
 pull=x/np.sqrt(np.diag(cov));i=int(np.argmax(abs(pull)));q=float(x@np.linalg.solve(cov,x))
 return dict(ell=ell.tolist(),values=x.tolist(),covariance=cov.tolist(),sigma=np.sqrt(np.diag(cov)).tolist(),chi2=q,dof=len(x),pte=float(chi2.sf(q,len(x))),signed_pull=pull.tolist(),worst_band=dict(index=i,ell=float(ell[i]),signed_gaussian_pull=float(pull[i])))

def measure(a,b,bins,cache,cycle,conditional=True):
 sl=sp.science_slice(bins);ell=bins.get_effective_ells()[sl]
 wk=sp.get_workspace(a,b,bins,wksp_cache=str(cache))
 cl=wk.decouple_cell(nmt.compute_coupled_cell(a,b))[:,sl]
 fid=None
 if conditional:
  ab=nmt.get_iNKA_cell(a,b)
  fid={'11':nmt.get_iNKA_cell(a,a),'12':np.zeros_like(ab),'21':np.zeros_like(ab),'22':nmt.get_iNKA_cell(b,b)}
 cw=native_c2(a,b) if cycle==2 else None
 _,raw,cw=sp.compute_gaussian_covariance(a,b,a,b,bins,wksp_ab=wk,wksp_cd=wk,cov_wksp=cw,fiducial_spectra=fid,wksp_cache=str(cache))
 nc=2 if b.spin==2 else 1
 raw=raw.reshape(bins.get_n_bands(),nc,bins.get_n_bands(),nc)
 result={component:score(cl[i],raw[:,i,:,i][sl,sl],ell) for i,component in enumerate(['E','B'] if nc==2 else ['scalar'])}
 del cw,wk,raw;gc.collect()
 return result

def archived(cycle,template,binname):
 if cycle==1:
  p=ROOT/f'results/tr1/tr1_systematics/{template}.tar'
  with tarfile.open(p) as t:m=json.load(t.extractfile('measurement.json'))
  r=m['template_kappa'] if binname=='kappa' else m['WL' if binname[0]=='l' else 'GC'][binname]
  return score(np.array(r['cross']),np.array(r['covariance']),np.array(r['ell']))
 p=ROOT/'results/tr1_v2/systematics/gaussian_null_family.tar'
 with tarfile.open(p) as t:
  m=json.load(t.extractfile('summary.json'));z=np.load(t.extractfile('joint.npz'));x=z['observed'];cov=z['covariance']
 stem=c2.STEMS[NAMES.index(template)]
 i=m['test_names'].index(f'{stem}/{binname}')
 return score(x[i],cov[i*15:(i+1)*15,i*15:(i+1)*15],np.array(m['ell']))

def run_a():
 out=BASE/'window-leakage';out.mkdir(parents=True,exist_ok=True)
 f,args=fields(1,out,kappa=True);ts,p1=templates(1,out);ts2,p2=templates(2,out)
 _,p,m=ts[0];_,pnew,mnew=ts2[0]
 a=np.load(p);b=np.load(pnew);ma=np.load(m).astype(bool);mb=np.load(mnew).astype(bool)
 shift=float(np.median(a[ma&mb]-b[ma&mb]));a[mb&~ma]=b[mb&~ma]+shift
 bins,_=sp.make_bins(100,3000,nells=15,spacing='log',field_lmax=6143)
 cache=legacy_cache(1,out,'extinction_vis')
 result=dict(exploratory=True,null_wick='zero template-data cross',definition='Only extinction template window changes; all C1 tracer maps/windows/iterations held fixed. Rewindowed C1 template uses C2 support, C2 C2-type 0.15deg taper, C1 mean and n_iter=1.',inputs=receipt([p1,p2,Path(args.gc_pkl),Path(args.wl_tar),FP,KMAP,KMASK,Path(__file__)]),tests={})
 for label,v,mask,it,names in [('c1_rewindowed',a,mb,1,list(f)),('c1_original',a,ma,1,['g0','l0','kappa']),('c2prep_c1window',b,ma,0,['g0','l0','kappa'])]:
  # Fill missing C2 preparation only when using C1 window.
  if label=='c2prep_c1window':v=b.copy();v[ma&~mb]=a[ma&~mb]-shift
  w=nmt.mask_apodization(mask.astype(float),.15,apotype='C2');t=sp.make_field(v,w,lmax=6143,lmax_mask=6143,n_iter=it)
  for name in names:
   key=f'{label}/{name}';file=out/(key.replace('/','_')+'.json')
   if file.exists():r=json.loads(file.read_text())
   else:
    print('START A',key,time.ctime(),flush=True);r=measure(t,f[name],bins,cache,1);dump(file,r)
   result['tests'][key]=r
   if label=='c1_rewindowed':
    r['archived_C1']=archived(1,'extinction_vis',name);r['archived_C2']=archived(2,'extinction_vis',name)
    comp='E' if name.startswith('l') else 'scalar';orig=r['archived_C1']
    r['delta_cross_over_original_sigma']=((np.array(r[comp]['values'])-orig['values'])/orig['sigma']).tolist()
   dump(out/'crosses.json',result)
   comp='E' if name.startswith('l') else 'scalar';print('DONE A',key,r[comp]['chi2'],r[comp]['pte'],flush=True)
  del t,w;gc.collect()
 del f;gc.collect()
 fv,_=fields(1,out,visibility=True)
 t=sp.make_field(a,nmt.mask_apodization(mb.astype(float),.15,apotype='C2'),lmax=6143,lmax_mask=6143,n_iter=1)
 result['visibility_definition']='C1 archived visibility-corrected delta plus matched normalized 1+WEIGHT mask factors; original scratch correction omitted matched mask factors.'
 result['inputs']+=receipt([ROOT/'results/scratch/napoli/visibility_check/corrected.pkl']+[ROOT/f'results/scratch/napoli/visibility_check/maps_bin{i}.npz' for i in range(1,7)])
 for name,field in fv.items():
  key=f'c1_vis_rewindowed/{name}';file=out/(key.replace('/','_')+'.json')
  if file.exists():r=json.loads(file.read_text())
  else:print('START A',key,time.ctime(),flush=True);r=measure(t,field,bins,cache,1);dump(file,r)
  result['tests'][key]=r;dump(out/'crosses.json',result)
  print('DONE A',key,r['scalar']['chi2'],r['scalar']['pte'],flush=True)

def run_b(cycle):
 out=BASE/'shear-b';out.mkdir(parents=True,exist_ok=True)
 f,args=fields(cycle,out);f={n:v for n,v in f.items() if n.startswith('l')};ts,p=templates(cycle,out)
 bins,_=sp.make_bins(100,3000,nells=15,spacing='log',field_lmax=6143)
 result=dict(cycle=cycle,exploratory=True,inputs=receipt([p,Path(args.gc_pkl),Path(args.wl_tar),Path(__file__),ROOT/'workflow/scripts/systematics_cycle2.py',Path(sp.__file__)]+([FP] if cycle==1 else [])),null_wick='TT x raw shear-shear only; template-shear Wick spectra zero',B_component='cov_raw.reshape(nband,2,nband,2)[:,1,:,1][science,science]',n_iter=1 if cycle==1 else 0,tests={})
 for (stem,pmap,pmask),template in zip(ts,NAMES):
  cache=legacy_cache(cycle,out,template)
  mask=np.load(pmask).astype(bool)
  if cycle==1:mask&=np.asarray(hp.read_map(FP,dtype=float))>0
  t=sp.make_field(np.load(pmap),nmt.mask_apodization(mask.astype(float),.15,apotype='C2'),lmax=6143,lmax_mask=6143,n_iter=1 if cycle==1 else 0)
  for name,field in f.items():
   key=f'{template}/{name}';file=out/f'c{cycle}_{template}_{name}.json'
   if file.exists():r=json.loads(file.read_text())
   else:
    print('START B',cycle,key,time.ctime(),flush=True);r=measure(t,field,bins,cache,cycle);dump(file,r)
   ref=archived(cycle,template,name)
   r['archived_E']=ref
   r['E_consistency']=dict(max_abs_cross_difference_over_archived_sigma=float(np.max(abs(np.array(r['E']['values'])-ref['values'])/ref['sigma'])),max_sigma_ratio_difference=float(np.max(abs(np.array(r['E']['sigma'])/ref['sigma']-1))),chi2_difference=r['E']['chi2']-ref['chi2'],note='C1 archive uses observed-cross Wick term; this run conditions it to zero. C2 should reproduce both vector and covariance.')
   result['tests'][key]=r;dump(out/f'cycle{cycle}.json',result)
   print('DONE B',cycle,key,'E',r['E']['chi2'],r['E']['pte'],'B',r['B']['chi2'],r['B']['pte'],'parity',r['E_consistency'],flush=True)
  del t;gc.collect()

if __name__=='__main__':
 if sys.argv[1]=='a':run_a()
 else:run_b(int(sys.argv[2]))
