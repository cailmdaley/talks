#!/usr/bin/env python3
"""Audit every delivered band against its Gaussian error and archive parity."""
import json,pickle,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/'results/scratch/gc8'
STEMS=['GALACTICEXTINCTION_VIS','EXPOSURES_VIS','NOISE_VIS','PSF_VIS','ZODIACALLIGHT_VIS','STARNUMBERDENSITY_GAIACAM']
NAMES=['extinction_vis','exposures_vis','noise_vis','psf_vis','zodiacal_vis','stars_gaia']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rows=[];large=[];summary={};parity={}
 for cycle in [1,2]:
  p=BASE/f'shear-b/cycle{cycle}.json';j=json.loads(p.read_text())
  if len(j['tests'])!=36:raise ValueError(f'Cycle {cycle} incomplete')
  for key,r in j['tests'].items():
   for comp in ['E','B']:
    z=r[comp];x=np.array(z['values']);cov=np.array(z['covariance']);ell=np.array(z['ell'])
    assert x.shape==(15,) and cov.shape==(15,15)
    np.linalg.cholesky(cov);q=float(x@np.linalg.solve(cov,x));assert np.isclose(q,z['chi2'],rtol=1e-12)
    pulls=x/np.sqrt(np.diag(cov));assert np.allclose(pulls,z['signed_pull'],rtol=1e-12)
    rows.append(f"| {cycle} | {key} | {comp} | {z['pte']:.4g} | "+', '.join(f'{v:+.2f}' for v in pulls)+' |')
    for i in np.flatnonzero(abs(pulls)>3):large.append(dict(cycle=cycle,test=key,component=comp,ell=float(ell[i]),signed_gaussian_pull=float(pulls[i]),pte=z['pte']))
  bb=[(k,r['B']) for k,r in j['tests'].items()];worst=min(bb,key=lambda p:p[1]['pte']);peak=max(bb,key=lambda p:abs(p[1]['worst_band']['signed_gaussian_pull']))
  summary[str(cycle)]=dict(n_tests=36,B_tests_below_005=sum(r['B']['pte']<.05 for r in j['tests'].values()),E_tests_below_005=sum(r['E']['pte']<.05 for r in j['tests'].values()),smallest_B_pte_test=worst[0],smallest_B_pte=worst[1]['pte'],smallest_B_pte_chi2=worst[1]['chi2'],worst_B_band_test=peak[0],worst_B_band=peak[1]['worst_band'],max_E_vector_difference_over_archive_sigma=max(r['E_consistency']['max_abs_cross_difference_over_archived_sigma'] for r in j['tests'].values()),max_E_sigma_relative_change_from_archive=max(r['E_consistency']['max_sigma_ratio_difference'] for r in j['tests'].values()))
  if cycle==1:
   for name,stem in zip(NAMES,STEMS):
    pp=ROOT/f'results/cache/tr1/tr1_systematics/{name}/work/spectra/WL/{stem}.pkl'
    saved=pickle.load(pp.open('rb'))
    for i in range(6):
     key=f'{name}/l{i}';r=j['tests'][key]['B'];old=np.array(saved['cls'][f'y_l{i}']['cl_bb'])
     parity[key]=float(np.max(abs(old-r['values'])/np.array(r['sigma'])))
 lines=['# Pointwise Gaussian-error audit','','These are signed band values divided by the square root of the appropriate component Gaussian covariance diagonal.','All tests use the same 15 ell centres: 112, 140.5, 176.5, 221.5, 278, 349, 438.5, 550.5, 690.5, 866.5, 1087.5, 1364.5, 1712, 2148, 2695.5.','PTEs use the full band covariance, not these diagonal pulls alone.','','| Cycle | Template/bin | Component | PTE | All 15 signed Gaussian-normalized bands |','|---|---|---|---:|---|']+rows
 lines+=['','## Every band exceeding three Gaussian errors','','| Cycle | Template/bin | Component | ell | Signed pull | Full-test PTE |','|---|---|---|---:|---:|---:|']
 for r in large:lines.append(f"| {r['cycle']} | {r['test']} | {r['component']} | {r['ell']:.1f} | {r['signed_gaussian_pull']:+.4f} | {r['pte']:.4g} |")
 (BASE/'shear-b/band-audit.md').write_text('\n'.join(lines)+'\n')
 controls=json.loads((BASE/'window-leakage/crosses.json').read_text())
 # No aggregate may conceal an exceptional controlled-cross band.
 a_lines=['# Controlled-cross pointwise audit','','All numbers are signed values divided by the relevant component Gaussian error.','Low-only C2 rows use original-template errors as a reference metric, not as their own null calibration.','','| Test | Component | dof | PTE or reference PTE | Every signed Gaussian-normalized band |','|---|---|---:|---:|---|']
 a_count=0
 def audit_record(tag,comp,z):
  nonlocal a_count
  x=np.array(z['values']);cov=np.array(z['covariance']);np.linalg.cholesky(cov)
  assert np.isclose(x@np.linalg.solve(cov,x),z['chi2'],rtol=1e-12)
  pull=x/np.sqrt(np.diag(cov));a_count+=1
  a_lines.append(f"| {tag} | {comp} | {len(x)} | {z['pte']:.4g} | "+', '.join(f'{v:+.2f}' for v in pull)+' |')
 for key,r in controls['tests'].items():
  comp='E' if '/l' in key else 'scalar';audit_record(key,comp,r[comp])
 fals=json.loads((BASE/'window-leakage/c2-falsification-strict/summary.json').read_text())
 for key,r in fals['tests'].items():
  audit_record('C2 low-only/'+key,'original-covariance reference',r['low_only_high_bands'])
  audit_record('C2 high-pass/'+key,'own filtered covariance',r['high_pass_high_bands_own_covariance'])
 (BASE/'window-leakage/band-audit.md').write_text('\n'.join(a_lines)+'\n')
 audit=dict(complete=True,summary=summary,controlled_and_falsification_blocks_checked=a_count,all_bands_over_three_gaussian_errors=large,C1_B_saved_vector_parity_over_new_B_sigma=parity,max_C1_B_archive_vector_difference_over_new_B_sigma=max(parity.values()))
 (BASE/'shear-b/audit.json').write_text(json.dumps(audit,indent=2)+'\n')
 files=[BASE/'window-leakage'/p for p in ['auto.json','lowell.json','crosses.json','cross-lowell.json','HEADLINE.md','null-table.md','band-audit.md','c2-falsification/summary.json','c2-falsification-strict/summary.json']]+[BASE/'shear-b'/p for p in ['cycle1.json','cycle2.json','heatmap.json','report.md','band-audit.md','audit.json']]
 receipt=dict(outputs=[dict(path=str(p),sha256=digest(p)) for p in files],allocation='62248138',nside=2048,field_lmax=6143,threads_cap=36,exploratory=True,managed_lc_outputs_modified=False)
 (BASE/'window-leakage/run-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(audit['summary'],indent=2));print('C1 B vector parity max',max(parity.values()))
if __name__=='__main__':main()
