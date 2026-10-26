"""Independent algebraic and support checks for the four-dust extension."""
import json
import pickle
import rho_collect as collect
from pathlib import Path
import numpy as np
from scipy.stats import chi2
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'results/scratch/gc8/rho'
x=json.loads((OUT/'rho_four_dust.json').read_text())
old=json.loads((OUT/'rho.json').read_text())
for key,value in old['rows'].items(): assert x['rows'][key]==value
checks=[]
for key,r in x['rows'].items():
 if '/gnilc/' not in key:continue
 c=np.asarray(r['cross']); C=np.asarray(r['covariance_cross']); norm=np.asarray(r['normalization'])
 R=np.asarray(r['covariance_rho']); rho=np.asarray(r['rho'])
 assert C.shape==(15,15)
 np.linalg.cholesky(C);np.linalg.cholesky(R)
 np.testing.assert_allclose(rho,c/norm,rtol=1e-13)
 expected=C/np.outer(norm,norm)
 np.testing.assert_allclose(R,(expected+expected.T)/2,rtol=1e-13,atol=1e-18)
 q=float(c@np.linalg.solve(C,c));np.testing.assert_allclose(q,r['chi2'],rtol=1e-12)
 np.testing.assert_allclose(chi2.sf(q,15),r['pte'],rtol=1e-12)
 j=int(np.argmax(abs(c/np.sqrt(np.diag(C)))))
 assert r['worst_band']['ell']==r['ell'][j]
 base=old['rows'][key.replace('/gnilc/','/sfd/')]
 assert r['tracer_signal_auto']==base['tracer_signal_auto']
 if r['tracer'].startswith('g'):
  ib=int(r['tracer'][1:])+1
  a=json.loads((OUT/f'gnilc-bin{ib}.json').read_text())
  b=json.loads((ROOT/f'results/scratch/gc8/sfd-bin{ib}.json').read_text())
  assert a['window_sha256']==b['window_sha256']
 checks.append(dict(key=key,chi2=q,pte=r['pte'],worst=r['worst_band'],offdiagonal_max=float(np.max(abs(R-np.diag(np.diag(R)))))))
assert len(checks)==13
assert all(all(row.values()) for row in x['gnilc']['shear_snapshot_parity'].values())
a=pickle.load(open(OUT/'c2_sfd_wl_kappa.pkl','rb'))
b=pickle.load(open(OUT/'c2_sfd_control_wl_kappa.pkl','rb'))
control=[]
for key in [f'y_l{i}' for i in range(6)]+['kappa_y']:
 delta={}
 for label,fn in [('cl',collect.vec),('cov',collect.block)]:
  va,vb=fn(a,key),fn(b,key)
  rel=float(np.linalg.norm(va-vb)/np.linalg.norm(va))
  assert rel<1e-8,(key,label,rel)
  delta[label+'_relative_norm_difference']=rel
 control.append(dict(key=key,**delta))
(OUT/'gnilc_verification.json').write_text(json.dumps(dict(passed=True,unchanged_existing_rows=len(old['rows']),checks=checks,sfd_control_current_vs_archived=control),indent=2))
print('SFD current/archived operator control:',json.dumps(control,indent=2))
print(json.dumps(checks,indent=2))
