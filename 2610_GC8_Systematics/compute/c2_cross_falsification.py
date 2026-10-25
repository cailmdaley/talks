#!/usr/bin/env python3
"""Priority falsification: can ell<=99 extinction alone explain C2 crosses?"""
from template_nulls import *

def subset_score(x,c,ell,sel):return score(x[sel],c[np.ix_(sel,sel)],ell[sel])
def fraction(model,target,c):
 precision_target=np.linalg.solve(c,target)
 norm=float(target@precision_target)
 return float(model@precision_target/norm)

def main():
 strict='--strict' in sys.argv
 out=BASE/('window-leakage/c2-falsification-strict' if strict else 'window-leakage/c2-falsification');out.mkdir(parents=True,exist_ok=True)
 args=options(2,out);g,w=c2.canonical_maps(args,out/'maps')
 kr=ROOT/'results/tr1_v2/survey/kappa.json';mr=ROOT/'results/tr1_v2/map_products/pair_apodized_masks.json'
 km=json.loads(kr.read_text());ms=json.loads(mr.read_text());kp=Path(km['map']['path']);mp=Path(ms['root'])/next(x['path'] for x in ms['files'] if x['path'].endswith('_apod_mask.fits'))
 names=['kappa']+[f'g{i}' for i in range(6)]+[f'l{i}' for i in range(6)]
 print('Building C2 fields',time.ctime(),flush=True)
 _,f=sp.map2cls(gc=g,wl=w,kappa=dict(map=str(kp),mask=str(mp)),covariance=None,skipped_pairs=list(itertools.product(names,repeat=2)),return_fields=True,outdir=str(out/'fields'),outfile='fields.pkl',**c2.map_options(args))
 del g,w;gc.collect()
 ts,bundlepath=templates(2,out);_,pmap,pmask=ts[0];total=np.load(pmap);mask=np.load(pmask).astype(bool)
 parent=Path('/leonardo_work/EUHPC_E07_074/cdaley00/tmp/extinction-provenance/HFI_CompMap_ThermalDustModel_2048_R1.20.fits')
 print('Full-sky ell<=99 Planck decomposition',time.ctime(),flush=True)
 dust=np.float32(2.108)*hp.read_map(parent,field=2,dtype=np.float32)
 # Reconstruct the full-sky delivered VMPZ operator before filtering: nearest
 # Galactic parent at every equatorial NSIDE-2048 pixel centre, float32 units.
 # Filtering a zero-padded TR1 map would itself manufacture boundary leakage.
 native=np.empty(hp.nside2npix(2048),dtype=np.float32);rot=hp.Rotator(coord=['C','G'])
 for start in range(0,len(native),1000000):
  stop=min(start+1000000,len(native));theta,phi=hp.pix2ang(2048,np.arange(start,stop))
  tg,pg=rot(theta,phi);native[start:stop]=dust[hp.ang2pix(2048,tg,pg)]
 residual=native[mask].astype(float)-total[mask];offset=float(np.median(residual));model_residual=float(np.max(abs(residual-offset)))
 print('Full-sky VMPZ reconstruction max centered residual',model_residual,flush=True)
 if model_residual>1e-7:raise ValueError('Full-sky parent reconstruction fails delivered-template identity')
 alms=hp.map2alm(native,lmax=99,iter=3)
 low=hp.alm2map(alms,2048,lmax=99);del dust,native,alms
 # In strict mode assign the original footprint-mean subtraction entirely to
 # the low component. Recentring the high-pass map would reintroduce ell=0.
 low-=offset if strict else np.mean(low[mask]);high=total-low
 window=nmt.mask_apodization(mask.astype(float),.15,apotype='C2')
 lo=sp.make_field(low,window,lmax=6143,lmax_mask=6143,n_iter=0)
 hi=sp.make_field(high,window,lmax=6143,lmax_mask=6143,n_iter=0)
 tot=sp.make_field(total,window,lmax=6143,lmax_mask=6143,n_iter=0)
 del low,high,total,window;gc.collect()
 bins,_=sp.make_bins(100,3000,nells=15,spacing='log',field_lmax=6143);sl=sp.science_slice(bins);ell=bins.get_effective_ells()[sl];sel=np.flatnonzero(ell>965)
 cache=legacy_cache(2,out,'extinction_vis')
 result=dict(exploratory=True,mock_calibrated=False,runtime_identity=blocks.runtime_identity(),inputs=receipt([bundlepath,Path(args.gc_pkl),Path(args.wl_tar),kr,mr,kp,mp,parent,ROOT/'results/tr1_v2/systematics/gaussian_null_family.tar',Path(__file__),Path(sp.__file__)]),ell=ell.tolist(),high_ell_indices=sel.tolist(),strict_highpass=strict,mean_policy='Original total-template mean assigned entirely to low component; high component not re-centred.' if strict else 'Both components independently footprint-mean-centred; high component therefore includes a constant subtraction.',native_template_model_max_centered_residual=model_residual,filter='Full-sky VMPZ extinction reconstructed from Planck EBV with exact nearest-parent Galactic lookup at equatorial NSIDE2048 pixel centres and float32 2.108 conversion. Equatorial alms ell<=99, then low map mean-centered over exact C2 support; high map = delivered C2 prepared extinction minus low map. Both use original C2 mask, taper, and n_iter=0. No zero-padded regional filtering.',coherent_amplitude='A = observed^T C_original^-1 filtered / (observed^T C_original^-1 observed), on ell>965; descriptive signed projection fraction onto the measured shape, not an independent fitted-model significance.',tests={})
 for name,b in f.items():
  path=out/f'{name}.json'
  if path.exists():r=json.loads(path.read_text())
  else:
   print('START FALSIFICATION',name,time.ctime(),flush=True)
   ref=archived(2,'extinction_vis',name);x=np.array(ref['values']);cov=np.array(ref['covariance'])
   wk=sp.get_workspace(lo,b,bins,wksp_cache=str(cache))
   lowcross=wk.decouple_cell(nmt.compute_coupled_cell(lo,b))[0,sl]
   originalcross=wk.decouple_cell(nmt.compute_coupled_cell(tot,b))[0,sl]
   hm=measure(hi,b,bins,cache,2);comp='E' if b.spin==2 else 'scalar';h=hm[comp];highcross=np.array(h['values']);highcov=np.array(h['covariance'])
   ratio=np.divide(lowcross,x,out=np.full_like(x,np.nan),where=x!=0)
   ratio=[None if not np.isfinite(v) else float(v) for v in ratio]
   ch=cov[np.ix_(sel,sel)]
   r=dict(original=ref,low_only_same_original_covariance=score(lowcross,cov,ell),high_pass_own_covariance=h,low_only_high_bands=subset_score(lowcross,cov,ell,sel),original_high_bands=subset_score(x,cov,ell,sel),high_pass_high_bands_own_covariance=subset_score(highcross,highcov,ell,sel),high_pass_same_original_covariance=score(highcross,cov,ell),high_pass_high_bands_original_covariance=subset_score(highcross,cov,ell,sel),low_to_measured_ratio=ratio,high_to_measured_ratio=[None if v is None else 1-v for v in ratio],coherent_low_fraction=fraction(lowcross[sel],x[sel],ch),coherent_high_fraction=fraction(highcross[sel],x[sel],ch),max_original_reproduction_difference_over_sigma=float(np.max(abs(originalcross-x)/ref['sigma'])),max_linearity_error_over_sigma=float(np.max(abs(lowcross+highcross-originalcross)/ref['sigma'])))
   dump(path,r)
  result['tests'][name]=r;dump(out/'summary.json',result)
  print('DONE FALSIFICATION',name,'orig high Q',r['original_high_bands']['chi2'],'lowQ',r['low_only_high_bands']['chi2'],'highQ',r['high_pass_high_bands_own_covariance']['chi2'],'Alo',r['coherent_low_fraction'],'Ahi',r['coherent_high_fraction'],flush=True)
if __name__=='__main__':main()
