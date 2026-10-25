#!/usr/bin/env python3
"""Write the completed strict-filter C2 cross falsification beside the headline."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[4]/'results/scratch/gc8/window-leakage'
def main():
 p=R/'c2-falsification-strict/summary.json';j=json.loads(p.read_text())
 if len(j['tests'])!=13:raise ValueError('Falsification is incomplete')
 rows=[];strong=0
 for name,r in j['tests'].items():
  low=r['low_only_high_bands'];high=r['high_pass_high_bands_own_covariance'];orig=r['original_high_bands'];w=high['worst_band'];strong+=high['pte']<.05
  ratios=[r['low_to_measured_ratio'][i] for i in j['high_ell_indices']]
  rows.append(f"| {name} | {orig['chi2']:.2f} | {low['chi2']:.2f}; {low['pte']:.3g} | {high['chi2']:.2f}; {high['pte']:.3g} | {r['coherent_low_fraction']:+.3f} | {r['coherent_high_fraction']:+.3f} | {min(ratios):+.3f} to {max(ratios):+.3f} | {w['ell']:.1f}; {w['signed_gaussian_pull']:+.2f} |")
 lines=['## C2 cross-signal falsification','','This test splits a reconstructed full-sky VMPZ extinction map into ell<=99 and ell>=100 **before** masking, then uses the exact C2 template window and C2 tracer fields.','The full-sky nearest-parent reconstruction matches the delivered template on its support to '+f"{j['native_template_model_max_centered_residual']:.3g} mag after a constant offset.",'The original total-template footprint mean is assigned entirely to the low component; the high component is not re-centred, because that would reintroduce a monopole.','Low and high cross vectors add back to the original within recorded floating-point tolerance.','','All rows below use the five science bands with ell>965 (1087.5, 1364.5, 1712, 2148, 2695.5).','Low-only chi2/PTE uses the **original measured-template Gaussian block**, as requested.','High-pass chi2/PTE uses a newly contracted **high-pass-template Gaussian block** with zero template-data Wick spectra, on the same cached NaMaster mask workspace.','The original-block high-pass statistic is also saved in JSON.','A_low and A_high are descriptive signed projection fractions onto the measured cross shape, using the original covariance; they sum to one and are not independent fitted-model significances.','','| Tracer | Original chi2 / 5 | Low-only chi2; PTE | High-pass chi2; PTE | A_low | A_high | Per-band low/original range | High-pass worst ell; Gaussian pull |','|---|---:|---:|---:|---:|---:|---:|---:|']+rows
 lines+=['',f'High-pass correlations have marginal Gaussian PTE<0.05 in {strong}/13 high-ell tests.','Every per-band ratio, full 15-band and restricted 5-band covariance, original and filtered vector, PTE and worst-band residual is saved in `c2-falsification-strict/summary.json`.','The independently mean-centred decomposition is retained separately in `c2-falsification/summary.json` as a monopole-preparation control.','','These Gaussian PTEs are not mock calibrated.','A cutoff at ell=100 separates scales below and above 100; it does not prove that a measured ell~2700 correlation originates at ell~2700 rather than at ell=100-965.']
 text='\n'.join(lines)+'\n';(p.parent/'report.md').write_text(text)
 head=R/'HEADLINE.md';old=head.read_text().split('\n## C2 cross-signal falsification')[0].rstrip();head.write_text(old+'\n\n'+text)
if __name__=='__main__':main()
