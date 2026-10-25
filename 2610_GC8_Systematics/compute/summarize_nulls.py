#!/usr/bin/env python3
"""Render compact, reproducible tables from completed talk-only null JSONs."""
import json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'results/scratch/gc8'

def label(name):
 return ('gamma'+str(int(name[1:])+1)) if name.startswith('l') else ('delta'+str(int(name[1:])+1)) if name.startswith('g') else 'kappa_SPT'
def fmt(r):return f"{r['chi2']:.2f}; {r['pte']:.3g}"
def a_report():
 p=BASE/'window-leakage/crosses.json'
 if not p.exists():return
 j=json.loads(p.read_text());lines=['# Extinction-window null tests','','All chi-squared values use 15 bands and full within-test NaMaster Gaussian covariance.','PTEs are uncalibrated Gaussian reference probabilities, not mock-calibrated significance.','The controlled rerun changes only the extinction window; C1 tracer windows and maps are held fixed.','','| Tracer | C1 archived chi2; PTE | C1 rewindowed chi2; PTE | C2 archived chi2; PTE | high-ell sigma new/old | largest cross shift / old sigma | new worst ell; pull |','|---|---:|---:|---:|---:|---:|---:|']
 for key,r in j['tests'].items():
  if not key.startswith('c1_rewindowed/'):continue
  name=key.split('/')[1];comp='E' if name.startswith('l') else 'scalar';z=r[comp];old=r['archived_C1'];new=r['archived_C2'];w=z['worst_band']
  lines.append(f"| {label(name)} | {fmt(old)} | {fmt(z)} | {fmt(new)} | {z['sigma'][-1]/old['sigma'][-1]:.3f} | {max(abs(np.array(r['delta_cross_over_original_sigma']))):.3f} | {w['ell']:.1f}; {w['signed_gaussian_pull']:+.2f} |")
 lines+=['','C1 archived covariance retains observed template-data Wick spectra; controlled reruns condition these spectra to zero, as C2 does.','For kappa the table uses the full archived band covariance, rather than the old deck diagonal-only statistic.','','## Visibility-corrected C1 density with matched mask weights','','| Bin | Rewindowed chi2; PTE | Worst ell; Gaussian pull |','|---|---:|---:|']
 for key,r in j['tests'].items():
  if key.startswith('c1_vis_rewindowed/'):
   z=r['scalar'];w=z['worst_band'];lines.append(f"| {label(key.split('/')[1])} | {fmt(z)} | {w['ell']:.1f}; {w['signed_gaussian_pull']:+.2f} |")
 lines+=['',j.get('visibility_definition','Visibility tests not complete.'),'','Exact band vectors, full covariance matrices, signed pulls, inputs and hashes are in `crosses.json`.']
 (p.parent/'null-table.md').write_text('\n'.join(lines)+'\n')

def b_report():
 heat=dict(templates=['extinction_vis','exposures_vis','noise_vis','psf_vis','zodiacal_vis','stars_gaia'],bins=list(range(1,7)),cycles={},exploratory=True,statistic='15-band full-block Gaussian chi2, zero template-shear Wick cross; uncalibrated marginal PTE')
 lines=['# LensMC shear E/B template nulls','','Each PTE uses its own full 15-by-15 NaMaster Gaussian covariance.','B uses the B-B block of the raw spin-0 by spin-2 covariance, not the E covariance.','Template-shear Wick spectra are set to zero in both cycles.','These are uncalibrated marginal Gaussian PTEs; 36 tests per component per cycle are not independent.']
 for cycle in [1,2]:
  p=BASE/f'shear-b/cycle{cycle}.json'
  if not p.exists():continue
  j=json.loads(p.read_text());rows={}
  lines+=['',f'## Cycle {cycle}','','| Template | Bin | E chi2; PTE | B chi2; PTE | B worst ell; pull |','|---|---:|---:|---:|---:|']
  for key,r in j['tests'].items():
   name,b=key.split('/');i=int(b[1:]);w=r['B']['worst_band']
   rows[key]=r
   lines.append(f"| {name} | {i+1} | {fmt(r['E'])} | {fmt(r['B'])} | {w['ell']:.1f}; {w['signed_gaussian_pull']:+.2f} |")
  matrices={component:{stat:[[rows.get(f'{t}/l{i}',{}).get(component,{}).get(stat) for i in range(6)] for t in heat['templates']] for stat in ['pte','chi2']} for component in ['E','B']}
  matrices['tests']=rows;matrices['inputs']=j['inputs'];heat['cycles'][str(cycle)]=matrices
  lines+=['','### E-mode archive consistency','','| Template/bin | Max absolute cross difference / archived sigma | Max sigma ratio departure from one | chi2 difference |','|---|---:|---:|---:|']
  for key,r in rows.items():
   q=r['E_consistency'];lines.append(f"| {key} | {q['max_abs_cross_difference_over_archived_sigma']:.4g} | {q['max_sigma_ratio_difference']:.4g} | {q['chi2_difference']:.4g} |")
  lines+=['','### Tests with marginal PTE below 0.05','','Every failing test is listed with its worst single Gaussian-normalized band.','','| Template/bin | Component | PTE | Worst ell | Signed Gaussian pull |','|---|---|---:|---:|---:|']
  for key,r in rows.items():
   for comp in ['E','B']:
    z=r[comp]
    if z['pte']<.05:
     w=z['worst_band'];lines.append(f"| {key} | {comp} | {z['pte']:.3g} | {w['ell']:.1f} | {w['signed_gaussian_pull']:+.2f} |")
 (BASE/'shear-b/heatmap.json').write_text(json.dumps(heat,indent=2)+'\n')
 (BASE/'shear-b/report.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':a_report();b_report()
