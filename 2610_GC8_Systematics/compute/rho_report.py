#!/usr/bin/env python3
"""Render the observed numbers, with worst bands for every failing diagnostic."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'results/scratch/gc8/rho'
x=json.loads((OUT/'rho.json').read_text());D=x['rows'];P=x['cib_route']
def g(c,d,k,state=None):return D.get(f'{c}/{d}/{k}/{state or ("vis" if k.startswith("g") else "native")}')
def f(r):return 'pending' if r is None else f"{r['mean_rho']:+.4f} ± {r['mean_rho_error']:.4f}"
def name(k):return 'κ SPT' if k=='kappa' else ('δ' if k.startswith('g') else 'γE')+str(int(k[1:])+1)
keys=[f'g{i}' for i in range(6)]+[f'l{i}' for i in range(6)]+['kappa']
lines=['# Extinction, CIB and public dust: talk-only rho measurements','',
'Cycle 2 retains a positive VMPZ extinction correlation after its visibility correction, with density-bin mean coefficients about 0.09–0.13.',
'The correction changes those Cycle-2 density means much less than it changed Cycle 1.',
'The Lenz 857-GHz CIB route reproduces the Cycle-2 density means in bins 2–6 closely; bin 1 retains an excess over that prediction.',
'In Cycle 1, the visibility correction suppresses extinction much more than it suppresses CIB, so the simple CIB-route equality does not hold for several corrected density bins.',
'These are observed comparisons, not calibrated difference significances; the shared-sky cross-covariances have not been computed.','',
'For Cycle-2 density, SFD means are about 0.04–0.06 and CSFD means about −0.003–0.020.',
'All six SFD density spectra have diagnostic PTE < 0.05; all six CSFD density spectra have PTE > 0.38.',
'All 13 CSFD tracer tests have PTE > 0.27; SFD still correlates with high-redshift shear (γE6 PTE about 2.1e-9), while SFD × κ has PTE about 0.63.',
'A CSFD galaxy null is not independent evidence that no LSS was removed: its LSS correction was constructed using galaxy tracers.','',
'**Do not say that every tracer fails the Cycle-2 extinction null.**',
'All six density bins do, but shear bins 2 and 3 have PTEs about 0.18 and 0.09.',
'The strongest corrected density band is δ6 at ℓ=2695.5, about +10.4 Gaussian errors; the strongest shear band is γE6 at ℓ=2148, about +9.5 Gaussian errors.',
'These large bands sit in a coherent positive high-ℓ trend rather than forming isolated sign-changing spikes.','',
'## Definition and limitations','',
'ρℓ = Cℓ(X,T) / sqrt[Cℓ(X,X) Cℓ(T,T)].',
'For every tracer, Cℓ(X,X) is the **release-specific fiducial signal model**, with no shot, shape or reconstruction noise, averaged uniformly over the exact integer science bins.',
'This is a model-normalized estimate of the signal correlation coefficient, not the coefficient formed from observed total autos.',
'The same policy applies to δ, γE and κ and to all dust/CIB comparisons.',
'It avoids clipping the negative noise-subtracted EE autos present in the caches.',
'The template auto is measured; the CIB auto is the odd-ring × even-ring spectrum with the cached interpolation transfer correction.',
'The signal-model averaging uses top-hat science bins, not a fit to a tracer auto and not the exact masked auto bandpower windows.',
'This is a transparent normalization approximation; null χ² and individual cross/σ values are exactly invariant to it.','',
'σρ = σGaussian(CXT) / sqrt(CXX CTT), holding both denominators fixed.',
'Every covariance_rho is the complete 15×15 Gaussian cross-spectrum block divided by the outer product of those normalizations.',
'These errors do not include denominator variance.',
'With signal rather than total-auto normalization, shape/reconstruction noise can make the errors strongly scale dependent; the simple 1/sqrt(Nmodes) intuition need not hold.',
'The final comparison uses observed iNKA Gaussian Wick terms throughout; the official Cycle-2 zero-template-cross-Wick blocks and χ²/PTEs are retained under production_null in rho.json.',
'PTEs are Gaussian diagnostics, not matched-mock calibrated probabilities.',
'ρbar is the GLS constant-ρ estimate over 100<ℓ<3000, using the full block; its error is (1ᵀ Cρ⁻¹ 1)^−1/2.',
'The CIB prediction mean uses the **same compression weights as the measured extinction mean**.',
'Prediction errors combine the full Gaussian blocks of δ×CIB, CIB×extinction and the odd×even CIB auto, while omitting their mutual covariance; no prediction-minus-measurement PTE is claimed.','',
'C1 retains its archived legacy windows and response convention; C2 uses canonical map windows, pixel-response corrections and outer:pixel shear weights.',
'This is a release comparison, not an experiment changing only the extinction map.',
'C1 corrected maps change density values on the fixed old footprint; C2 raw maps remove both the source visibility correction and its field weights, on exactly the already-supported Cycle-2 catalogue pixels.',
'The roughly 10% of pixels excluded by the Cycle-2 visibility-support cut are not restored.',
'Public SFD/CSFD template support matches the VMPZ Cycle-2 support exactly: 391871 pixels, zero differences (support_parity.json).',
'SFD/CSFD Galactic→equatorial rotation reuses sofia_cross.read_template (sample at twice target NSIDE, then average); support means are removed before crossing.',
'κ uses the delivered canonical SPT pair mask, not a newly restricted common-footprint variant.','',
'## VMPZ extinction, corrected density in both cycles','',
'| Tracer | Cycle 1 ρbar ± error | Cycle 2 ρbar ± error | C2 χ²/15 | C2 PTE | C2 worst band (ℓ, signed Gaussian pull) |',
'|---|---:|---:|---:|---:|---:|']
for k in keys:
 a,b=g('c1','vmpz',k),g('c2','vmpz',k);w=b['worst_band']
 lines.append(f"| {name(k)} | {f(a)} | {f(b)} | {b['chi2']:.3f} | {b['pte']:.4g} | {w['ell']:.1f}, {w['signed_pull']:+.3f} |")
lines+=['','## Visibility comparison','', '| Cycle | Tracer | Extinction without | Extinction with | CIB without | CIB with |','|---|---|---:|---:|---:|---:|']
for c in ['c1','c2']:
 for k in keys[:6]:lines.append(f"| {c} | {name(k)} | {f(g(c,'vmpz',k,'raw'))} | {f(g(c,'vmpz',k,'vis'))} | {f(g(c,'cib857',k,'raw'))} | {f(g(c,'cib857',k,'vis'))} |")
lines+=['','## Cycle-2 dust maps','', '| Tracer | VMPZ ρbar ± error | SFD ρbar ± error | CSFD ρbar ± error |','|---|---:|---:|---:|']
for k in keys:lines.append(f"| {name(k)} | {f(g('c2','vmpz',k))} | {f(g('c2','sfd',k))} | {f(g('c2','csfd',k))} |")
lines+=['','## CIB-route means using matched compression weights','', '| Cycle | Tracer | Visibility | Measured extinction | CIB-route prediction |','|---|---|---|---:|---:|']
for key,p in P.items():
 c,k,state=key.split('/');m=D[p['measured_key']]
 lines.append(f"| {c} | {name(k)} | {state} | {f(m)} | {p['mean_rho_pred']:+.4f} ± {p['mean_rho_pred_error']:.4f} |")
lines+=['','## Every failing Gaussian diagnostic (PTE < 0.05)','',
'Each row names its worst single band; no multiple-testing or post-training independence claim is made.','',
'| Test | χ²/15 | PTE | Worst ℓ | ρℓ ± σρ | Signed Gaussian pull |','|---|---:|---:|---:|---:|---:|']
for key,r in D.items():
 if r['pte']>=.05:continue
 w=r['worst_band'];lines.append(f"| {key} | {r['chi2']:.3f} | {r['pte']:.4g} | {w['ell']:.1f} | {w['rho']:+.4f} ± {w['sigma_rho']:.4f} | {w['signed_pull']:+.3f} |")
lines+=['','## Files and reproduction','',
'`rho.json` contains every ell, cross, rho, Gaussian covariance block, fixed normalization, GLS mean, null test and worst-band record, plus hashed inputs.',
'`verification.json` checks the transformations, positive-definite blocks, exact χ² invariance and matched prediction compression.',
'`A_spectra_c1.png` and `A_spectra_c2.png` show extinction against corrected δ, γE and κ with every point carrying an error bar and common axes.',
'`B1_cycles.png` compares cycle means; `B2_visibility_vmpz.png` and `B2_visibility_cib857.png` compare visibility states.',
'`B2_cib_route.png` compares measured and CIB-predicted means on identical compression weights.',
'`B3_dust_maps_c2.png` compares VMPZ, SFD and CSFD for all 13 tracers.',
'`A_spectra_sfd_c2.png` and `A_spectra_csfd_c2.png` expose every public-dust band with the same three-panel layout and shared axis range.',
'`route_spectra_<c1|c2>_<raw|vis>.png` shows each density-bin extinction spectrum against its CIB-route prediction, with error bars on both.',
'Figures have no titles and use the deck’s EB Garamond matplotlib style.',
'GNILC E(B−V) was not added: the inspected on-disk GNILC directory contains frequency-specific emission/CIB maps, not a directly interchangeable E(B−V) product.','',
'All code is in `docs/talks/2610_GC8_Systematics/compute/rho_*.py`.',
'The missing crosses ran through `spectra.map2cls(covariance="namaster", diagonal_cov_only=True)` on shared allocation 62248138 with 36 threads.',
'Here diagonal_cov_only means independent spectrum blocks, not diagonal multipole covariance.',
'No lc-managed output, workflow, universe or ASTRA definition was edited.','',
'```bash',
'source ~/loom/shell-functions.sh',
'# Heavy missing crosses (resumable; reuse allocation only while it exists):',
'srun --jobid=62248138 --overlap -n1 -c36 bash -c \'source ~/loom/shell-functions.sh; export OMP_NUM_THREADS=36 DUCC0_NUM_THREADS=36 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1; app python docs/talks/2610_GC8_Systematics/compute/rho_missing.py raw; app python docs/talks/2610_GC8_Systematics/compute/rho_missing.py dust\'',
'# Collection and presentation:',
'for stage in collect verify plot report; do app python docs/talks/2610_GC8_Systematics/compute/rho_${stage}.py; done',
'```','']
(OUT/'HEADLINE.md').write_text('\n'.join(lines))
print('Wrote',OUT/'HEADLINE.md','rows',len(D))
