#!/usr/bin/env python3
"""Matched-weight original-window C1 density controls for the window-only test."""
from template_nulls import *
def main():
 out=BASE/'window-leakage';f,args=fields(1,out,visibility=True)
 a=np.load(out/'bundle1/bundle/GALACTICEXTINCTION_VIS.npy');mask=np.load(out/'bundle1/bundle/GALACTICEXTINCTION_VIS.mask.npy').astype(bool)
 t=sp.make_field(a,nmt.mask_apodization(mask.astype(float),.15,apotype='C2'),lmax=6143,lmax_mask=6143,n_iter=1)
 bins,_=sp.make_bins(100,3000,nells=15,spacing='log',field_lmax=6143);cache=legacy_cache(1,out,'extinction_vis')
 result=json.loads((out/'crosses.json').read_text());result['inputs']+=receipt([Path(__file__)])
 old=json.loads((ROOT/'results/scratch/napoli/visibility_check/extinction_vis.json').read_text())
 for name,field in f.items():
  key=f'c1_vis_original/{name}';file=out/(key.replace('/','_')+'.json')
  if file.exists():r=json.loads(file.read_text())
  else:
   print('START VIS ORIGINAL',name,time.ctime(),flush=True);r=measure(t,field,bins,cache,1);dump(file,r)
  before=old['GC'][name]['after']
  r['archived_visibility_without_matched_mask']=score(np.array(before['cross']),np.array(before['covariance']),np.array(before['ell']))
  result['tests'][key]=r;dump(out/'crosses.json',result)
  print('DONE VIS ORIGINAL',name,r['scalar']['chi2'],r['scalar']['pte'],flush=True)
if __name__=='__main__':main()
