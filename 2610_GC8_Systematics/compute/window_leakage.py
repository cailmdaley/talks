#!/usr/bin/env python3
"""Talk-only controlled extinction-window experiment. No production writes."""
import sys, json, tarfile, hashlib, time, gc
from pathlib import Path
import numpy as np
import pymaster as nmt
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'workflow/scripts'))
from dr1_cmbx.eDR1data import spectra as sp
OUT=ROOT/'results/scratch/gc8/window-leakage'
OUT.mkdir(parents=True,exist_ok=True)

def digest(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
 return h.hexdigest()

def bundle(cycle):
 p=ROOT/('results/tr1/tr1_systematics/template_bundle.tar' if cycle==1 else 'results/tr1_v2/systematics/template_bundle.tar')
 dest=OUT/f'bundle{cycle}';dest.mkdir(exist_ok=True)
 with tarfile.open(p) as t:
  for name in ['bundle/manifest.json','bundle/GALACTICEXTINCTION_VIS.npy','bundle/GALACTICEXTINCTION_VIS.mask.npy']:
   t.extract(name,dest,filter='data')
 return np.load(dest/'bundle/GALACTICEXTINCTION_VIS.npy'),np.load(dest/'bundle/GALACTICEXTINCTION_VIS.mask.npy').astype(bool),dict(path=str(p),sha256=digest(p))

def main():
 a,ma,pa=bundle(1);b,mb,pb=bundle(2)
 shift=float(np.median(a[ma&mb]-b[ma&mb]))
 # Extend each preparation onto the other support using the measured constant offset.
 ae=a.copy();ae[mb&~ma]=b[mb&~ma]+shift
 be=b.copy();be[ma&~mb]=a[ma&~mb]-shift
 bins,_=sp.make_bins(100,3000,nells=15,spacing='log',field_lmax=6143)
 sl=sp.science_slice(bins)
 result=dict(inputs=[pa,pb],offset_c1_minus_c2=shift,common_pixel_residual_max=float(np.max(abs(a[ma&mb]-b[ma&mb]-shift))),ell=bins.get_effective_ells()[sl].tolist(),tests={})
 # Independent changes: support, mean, apodization and transform iteration.
 cases=[('c1_original',ae,ma,1,0.15),('c2_original',be,mb,0,0.15),
        ('c1prep_c2window',ae,mb,1,0.15),('c2prep_c1window',be,ma,0,0.15),
        ('c1_iter0',ae,ma,0,0.15),('c1_mean2',be,ma,1,0.15),
        ('c1_binary',ae,ma,1,0),('c2_binary',be,mb,0,0)]
 for name,values,mask,it,apo in cases:
  print('START',name,time.ctime(),flush=True)
  w=nmt.mask_apodization(mask.astype(float),apo,apotype='C2') if apo else mask.astype(float)
  f=sp.make_field(values,w,lmax=6143,lmax_mask=6143,n_iter=it)
  wk=sp.get_workspace(f,f,bins,wksp_cache=str(OUT/'workspace'))
  cl=wk.decouple_cell(nmt.compute_coupled_cell(f,f))[0,sl]
  result['tests'][name]=dict(values=cl.tolist(),n_iter=it,aposcale=apo,positive_pixels=int((w>0).sum()),sum_weights=float(w.sum()),window_sha256=hashlib.sha256(w.tobytes()).hexdigest())
  (OUT/'auto.json').write_text(json.dumps(result,indent=2)+'\n')
  print('DONE',name,'high=',cl[-1],flush=True)
  del f,wk,w;gc.collect()
if __name__=='__main__':main()
