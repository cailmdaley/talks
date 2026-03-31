# SPT Secondaries and Cross-Correlations Call — March 30, 2026

Informal update for the SPT secondaries call. Audience: SPT collaboration members, including Abhi Maniyar (y-maps), Aaron Ouellette (DES×SPT), and the broader secondaries group. They know SPT; they may not know Euclid internals.

## Narrative

### Act 1: Context (slides 1–2)

**Slide 1: Title.** Euclid × CMB Lensing. Cail Daley. Informal, no logos.

**Slide 2: Euclid DR1 targets October 2026, but this will be extremely challenging.**
The setup: DR1 is coming, but it's hard. ESA hack, B-modes under investigation, unprecedented turnaround. The CMBX group in Paris meets weekly for full-day hacks — [member list]. We're building a pipeline for Euclid × CMB lensing and tSZ. We haven't used SPT y-maps yet but would like to — Abhi's maps for DR1? (cautious, question mark — political, floating the idea on this call).

Speaker carries: the ESA hack disrupted operations for months. B-modes in Euclid shear are still under investigation — not resolved, not blocking, but consuming attention. "Unprecedented turnaround" = only ~1 year from first internal data to cosmology results, which is genuinely unprecedented for a Stage IV survey. The collaboration has mostly moved on to TR1 (more blinded); we're deliberately staying on unblinded RR2 to build understanding.

### Act 2: RR2 data (slides 3–5)

**Slide 3: Euclid RR2 is unblinded — we're building a full pipeline to cosmology while we can still poke around.**
Two columns: text left, south-patch footprint overlap (from shared_map_conventions, right column only) on the right. Below both columns: Margherita's RR2 footprint plot (euclid_cmbx_rr2dr1_footprints.png), credited. RR2 = ~30% of DR1 area (385 deg²). Cross-correlating with ACT DR6 and SPT-3G winter κ maps. Two tracers (δκ, γκ), 6 tomographic bins. Pseudo-Cℓ with NaMaster, Gaussian covariance.

Speaker carries: most of the collaboration skipped checks on the unblinded data. We're taking time now because it gives us much more understanding before the blinded data arrives.

**Slide 4: Six tomographic bins span z = 0.3–1.7 in weak lensing and z = 0.3–0.9 in galaxy clustering.**
Two columns: WL n(z) on top/left, GC n(z) on bottom/right — both from euclid_nz_overview, cropped to individual panels. Text on the left: catalog details (~50M WL, ~30M GC), two shear pipelines (lensmc, metacal). The point: this is a real catalog with real depth.

Speaker carries: the n(z) distributions are from the Euclid photometric pipeline (RR2_v2_Nz_WL_C2020_sel_pv.fits — matching the catalog version). The WL bins go deeper (mean z up to 1.72) while GC stops at z~0.9 — different populations, complementary tracers. Both feed into the cross-correlation.

**Slide 5: Eleven VMPZ-ID systematic maps track observational effects across the RR2 footprint.**
Scrollable slide showing the full composite of all 11 systematic maps (stellar density, galactic extinction, PSF, noise, persistence, etc.). Visual impact — let the audience see what we're working with.

**Slide 6: Galactic extinction contamination is well below the noise floor across all tracers.**
X_l contamination metric for galactic extinction: 2×2 grid showing density × ACT, density × SPT GMV, lensmc × ACT, lensmc × SPT GMV. Plus SPT PP for comparison. This is the setup for why we trust the null tests later.

Speaker carries: X_l = ℓ C_ℓ^{κS} C_ℓ^{fS} / C_ℓ^{SS} where S is the systematic and f is the galaxy field. 1% and 10% of σ(C_ℓ^{κE}) bands shown. Contamination is below 1% of the error bar for ℓ > 100. Template marginalization changes A_lens by < 0.05.

### Act 3: Results (slides 6–10)

**Slide 6: All cross-spectra are detected, but SPT amplitudes are systematically low.**
Full analysis summary figure. Let it land.

**Slide 7: ACT and SPT agree in spectral shape across all bins and both tracers.**
The shape agreement is important — the deficit is an overall amplitude, not a spectral distortion.

**Slide 8: The SPT deficit is 23% and appears in both galaxy tracers.**
A_lens values. Both tracers see it → CMB-side origin. Not contamination, not mask effects.

**Slide 9: SPT temperature-based estimators show lower amplitudes than polarization.**
TT–PP decomposition. The ℓ≈84 spike is foreground (confirmed). TT systematically lower than PP.

**Slide 10: High-ℓ SPT bandpowers actively suppress the fitted amplitude.**
ℓ-range robustness test. ACT stable, SPT drops. Scale-dependent effect.

### Act 4: Summary (slide 11)

**Slide 11: The deficit is genuinely puzzling.**
What we find, what we can rule out. This slide stays visible during Q&A.

## Slide headlines (narrative thread)

1. —
2. Euclid DR1 targets October 2026, but this will be extremely challenging
3. Euclid RR2 is unblinded — we're building a full pipeline while we can still poke around
4. Six tomographic bins span z = 0.3–1.7 in weak lensing and z = 0.3–0.9 in galaxy clustering
5. Eleven systematic maps track observational effects across the footprint
6. All cross-spectra are detected, but SPT amplitudes are systematically low
7. ACT and SPT agree in spectral shape across all bins and both tracers
8. The SPT deficit is 23% and appears in both galaxy tracers
9. SPT temperature-based estimators show lower amplitudes than polarization
10. High-ℓ SPT bandpowers actively suppress the fitted amplitude
11. The deficit is genuinely puzzling
