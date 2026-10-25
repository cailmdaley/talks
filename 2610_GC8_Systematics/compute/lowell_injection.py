#!/usr/bin/env python3
"""Physical full-sky Planck EBV ell<=99 injection through both template windows."""
from window_leakage import *
import healpy as hp

def main():
 a,ma,pa=bundle(1);b,mb,pb=bundle(2)
 p=Path('/leonardo_work/EUHPC_E07_074/cdaley00/tmp/extinction-provenance/HFI_CompMap_ThermalDustModel_2048_R1.20.fits')
 print('Planck low ell transform',flush=True)
 dust=hp.read_map(p,field=2,dtype=float)*2.108
 alms=hp.map2alm(dust,lmax=99,iter=3)
 hp.Rotator(coord=['G','C']).rotate_alm(alms,inplace=True)
 low=hp.alm2map(alms,2048,lmax=99)
 del dust,alms
 bins,_=sp.make_bins(100,3000,nells=15,spacing='log',field_lmax=6143);sl=sp.science_slice(bins)
 result=dict(inputs=[pa,pb,dict(path=str(p),sha256=digest(p))],ell=bins.get_effective_ells()[sl].tolist(),tests={})
 for cy,original,mask,it in [(1,a,ma,1),(2,b,mb,0)]:
  for kind in ['low','residual']:
   v=low.copy();v-=np.mean(v[mask])
   if kind=='residual':v=original-v
   w=nmt.mask_apodization(mask.astype(float),0.15,apotype='C2')
   f=sp.make_field(v,w,lmax=6143,lmax_mask=6143,n_iter=it)
   wk=sp.get_workspace(f,f,bins,wksp_cache=str(OUT/'workspace'))
   cl=wk.decouple_cell(nmt.compute_coupled_cell(f,f))[0,sl]
   result['tests'][f'c{cy}_{kind}']=dict(values=cl.tolist())
   print(cy,kind,cl[-1],flush=True)
   (OUT/'lowell.json').write_text(json.dumps(result,indent=2)+'\n')
   del f,wk,w,v;gc.collect()
if __name__=='__main__':main()
