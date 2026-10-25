#!/usr/bin/env python3
"""Resolve low-ell contributions to the measured C1 crosses, on both windows."""
from template_nulls import *

def main():
 out=BASE/'window-leakage';args=options(1,out)
 g=base._load_pickle(args.gc_pkl);g={'bin1':g['bin1']}
 files=base._ordered_wl(args.wl_tar,out/'cross_injection_wl')
 wl={'bin1':base._load_wl_bin(files[0],1,2048)}
 opts=base._common_map_options(args);opts['n_iter']=1
 _,f=sp.map2cls(gc=g,wl=wl,kappa=dict(map=str(KMAP),mask=str(KMASK),aposcale=.15),extra_masks={'footprint':np.asarray(hp.read_map(FP,dtype=float))>0},skipped_pairs=list(itertools.product(['kappa','g0','l0'],repeat=2)),covariance=None,return_fields=True,outdir=str(out/'injection_fields'),outfile='fields.pkl',blind='none',**opts)
 p=Path('/leonardo_work/EUHPC_E07_074/cdaley00/tmp/extinction-provenance/HFI_CompMap_ThermalDustModel_2048_R1.20.fits')
 dust=hp.read_map(p,field=2,dtype=float)*2.108
 alms=hp.map2alm(dust,lmax=99,iter=3);hp.Rotator(coord=['G','C']).rotate_alm(alms,inplace=True)
 low=hp.alm2map(alms,2048,lmax=99);del dust,alms
 bins,_=sp.make_bins(100,3000,nells=15,spacing='log',field_lmax=6143);sl=sp.science_slice(bins)
 data=json.loads((out/'crosses.json').read_text())
 result=dict(definition='Cross contribution from physical full-sky Planck EBV ell<=99, normalized by total-template Gaussian null errors. Contributions add linearly for crosses, unlike autos. Low-only science-band power is leakage by construction.',ell=bins.get_effective_ells()[sl].tolist(),inputs=receipt([p,Path(args.gc_pkl),Path(args.wl_tar),FP,KMAP,KMASK,Path(__file__)]),tests={})
 for cy,label in [(1,'c1_original'),(2,'c1_rewindowed')]:
  mask=np.load(out/f'bundle{cy}/bundle/GALACTICEXTINCTION_VIS.mask.npy').astype(bool)
  values=low.copy();values-=values[mask].mean()
  t=sp.make_field(values,nmt.mask_apodization(mask.astype(float),.15,apotype='C2'),lmax=6143,lmax_mask=6143,n_iter=1)
  for name,field in f.items():
   wk=sp.get_workspace(t,field,bins,wksp_cache=str(out/'workspace1'))
   cross=wk.decouple_cell(nmt.compute_coupled_cell(t,field))[:,sl]
   rr=data['tests'][f'{label}/{name}'];comp='E' if name=='l0' else 'scalar';ref=rr[comp]
   x=np.array(ref['values']);lo=cross[0];sigma=np.array(ref['sigma']);i=int(np.argmax(abs(lo/sigma)))
   result['tests'][f'{label}/{name}']=dict(low_only_values=lo.tolist(),residual_only_values=(x-lo).tolist(),total_values=x.tolist(),total_template_covariance=ref['covariance'],low_only_over_total_sigma=(lo/sigma).tolist(),worst_low_band=dict(ell=float(result['ell'][i]),signed_gaussian_normalized_contribution=float((lo/sigma)[i])))
   print(label,name,'last total/low',x[-1],lo[-1],'low/sigma last',lo[-1]/sigma[-1],flush=True)
   dump(out/'cross-lowell.json',result)
if __name__=='__main__':main()
