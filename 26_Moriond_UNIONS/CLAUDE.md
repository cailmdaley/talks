# Moriond 2026 Talk: UNIONS-3500 First Cosmological Constraints from 2D Cosmic Shear

## Framing Principles

**What this talk is NOT about:**
- The S8 tension. KiDS-Legacy and DES Y6 both find results consistent with Planck. The obsession with S8 tension is receding. We cannot contribute to it anyway — our non-tomographic error bars are ~5x wider than DES Y6, which is also being presented at this conference.
- Tightest constraints on anything. We are non-tomographic by design. Anyone wanting the best S8 should look elsewhere.

**What this talk IS about:**
- A new survey in a new hemisphere doing careful work. UNIONS is the only deep wide-field lensing survey in the northern sky. That makes it uniquely valuable for cross-correlations (DESI, Euclid, CMB lensing at high northern declination).
- Systematic rigor as proving ground for Stage IV. This is what we can show that's genuinely new and distinctive.
- Future potential. When tomography and 3x2pt arrive, UNIONS becomes competitive.
- Honest science from a small team. Fewer than ten people built these five papers. The pipeline isn't as mature as DES or KiDS — but we're building it right.

**Tone:** Good-natured honesty. Not defensive about wide error bars. Not mechanical about the pipeline. Straightforward about what we can and can't say.

## Two Axes

### Axis 1: Systematic Rigor

The distinctive things we did, and why they matter beyond this analysis:

1. **Three B-mode statistics in different bases.** Pure E/B (configuration space), COSEBIs (discrete modes), pseudo-Cl (harmonic space). No single null test is gospel — the power is in convergence across all three. They agree on where the clean scales are, and only one catalog version passes all of them. This determines the scale cuts that the cosmology papers inherit.

2. **PSF leakage marginalized in inference (Paper IV).** Most surveys correct for PSF leakage at the catalog level and move on. Paper IV goes further: the leakage parameters alpha and beta are inferred from rho/tau statistics, then carried into the cosmological likelihood as Gaussian priors — so the uncertainty in the PSF model propagates into the cosmological error budget. This is new. The joint chi-squared includes both the shear correlation functions and the PSF diagnostic statistics. Paper V validates independently: the shift between corrected and uncorrected ellipticities is 0.00 sigma.

3. **Intrinsic alignment: honest about the degeneracy.** With a single redshift bin, A_IA is essentially degenerate with S8. We cannot break this from the data alone. Instead of pretending we can (flat prior → the posterior just follows the degeneracy direction), we construct a tight Gaussian prior from external measurements: red/blue galaxy split using W3 CFHTLenS, combined A_IA = 0.83 +/- 0.7 (conservatively widened from 0.39). This is the right thing to do for a non-tomographic analysis, and we're explicit that if the prior is wrong, S8 shifts correspondingly. Tomography breaks the degeneracy — that's coming.

4. **Two independent pipelines agreeing.** Configuration space (Paper IV) and harmonic space (Paper V) share the same blinded catalog, n(z), and B-mode-informed scale cuts — but use independent likelihood codes. They agree to ~0.5 sigma. This is validated on 350 GLASS mocks where the scatter between the two is 0.4 sigma. The config-vs-harmonic consistency test, calibrated on simulations and used as an unblinding criterion, is a distinctive contribution of this release.

### Axis 2: Future Potential

What comes next and why it matters:

- **Tomography.** The main reason our constraints are wide is that we use a single redshift bin. Multi-bin photo-z calibration is the bottleneck; once it's in place, constraints tighten substantially and the IA degeneracy breaks.
- **3x2pt.** Galaxy-galaxy lensing and galaxy clustering from UNIONS + spectroscopic overlaps (DESI) will add complementary information.
- **Cross-correlations.** Northern sky coverage is uniquely positioned for CMB lensing (ACT, Planck at high dec), Euclid overlap, and DESI spectroscopic cross-correlations. These are things southern surveys cannot do as easily.
- **Stage IV proving ground.** Lessons learned here — blinding strategy, multi-statistic B-mode validation, pipeline consistency tests — transfer directly to LSST and Euclid analyses. A small team building the infrastructure right.

## Talk Arc (Prose)

### Opening (slides 1-3)

Start with what cosmic shear measures — the matter power spectrum — and position UNIONS as the first deep wide-field lensing survey from the northern sky. Don't lean on S8 tension as motivation. Instead: cosmic shear surveys are now mature enough to produce precise constraints, but the field needs independent datasets from different instruments and different hemispheres. UNIONS provides exactly that.

This is a 2D (non-tomographic) release — deliberately conservative. The goal is to get the systematics right before chasing constraining power. Tomography and 3x2pt will follow.

### Context (slides 4-5)

Team slide: fewer than ten people. This matters — it means a tighter, more focused analysis pipeline. Not as sophisticated as DES or KiDS in some respects, but every choice is understood.

Overall analysis framing: three companion papers forming a chain. Paper III validates the shear field (B-modes → scale cuts). Papers IV and V take those validated scales and fit cosmology in two independent bases. The PTE table shows that only one catalog version passes all three B-mode tests — this is the gatekeeper.

### Blinding caveat (slide 8)

The cosmology-paper authors were inadvertently partially unblinded a couple of weeks before the official ceremony. What happened: the maximum likelihood estimate — which isn't penalized by priors — peaked at the same S8 for all three blinds. The n(z) shift maps onto S8 the same way intrinsic alignment does, and the ML was free to compensate with extreme A_IA values that the MAP would have rejected. So they could infer which blind was physical. Analysis choices were already frozen, and we believe this didn't affect them — but we're transparent about it. This is discussed openly in the papers.

### B-modes (slides 9-12)

Three slides, one per statistic, each introducing the relevant scale cuts:

1. **Pure E/B** — configuration space. Gray shading marks the adopted angular cuts (12-83 arcmin). This is the most direct view of where B-modes sit in angle.

2. **Pseudo-Cl** — harmonic space. Gray shading marks ell = 300-1600. BB and EB both consistent with zero at these scales.

3. **COSEBIs combined** — Figure 10 from the paper. COSEBIs computed from both config-space xi_pm and harmonic-space band powers. The two paths agree. The key insight from the discussion: "The sensitivity to systematic contamination is set by the filter functions, not by the basis in which the two-point function is measured." This is the estimator consistency argument.

Then the PTE heatmap synthesizes: a 2D scan over angular cuts showing where all three statistics agree the field is clean. The small-scale failures trace the MegaCam CCD scale (~9.4 arcmin).

### Cosmology (slides 10-13 region)

Bridge from validation to inference. Photo-z, covariance, likelihoods — compress this. The key points: same n(z), same scale cuts from Paper III, different likelihood codes.

Show the data vectors: xi_pm with best-fit (Paper IV), C_ell EE with best-fit (Paper V). These are the measurements behind the contours.

The contour slide: config (orange) vs harmonic (red) vs Planck (pink). All overlapping. The error bars are wide — that's the 2D reality. The important result is not the width but the consistency: two independent pipelines landing in the same place.

Whisker plot: comprehensive summary. S8 from both pipelines across all three blinds, comparison with Planck and Stage III surveys, robustness tests. Everything shifts by less than 0.2 sigma.

Config-vs-harmonic scatter plot on GLASS mocks: 0.4 sigma consistency. This is the distinctive UNIONS result — a cross-check calibrated on simulations and used as an unblinding criterion.

### Close (slides 14-15)

Summary: UNIONS provides the first northern-sky cosmic shear constraints. The B-mode validation is thorough. The two pipelines agree. The constraints are broad but stable.

Outlook: tomography, 3x2pt, and cross-correlations with CMB lensing will sharpen this into a competitive cosmology dataset. The infrastructure we're building — blinding, multi-statistic validation, pipeline consistency — is the real deliverable for the Stage IV era.

## Key Numbers

- Survey area: ~3500 deg2 (2894 deg2 effective after masking)
- Source galaxies: 61M (v1.4.6.3)
- n_eff: 4.957 gal/arcmin2
- sigma_e: 0.378 combined (0.267 per component)
- Scale cuts: 12-83 arcmin (config), ell 300-1600 (harmonic)
- S8 (v1.4.6.3 blind B): Harmonic 0.920 +/- 0.081, Config 0.870 +/- 0.089
- Config-harmonic agreement: ~0.5 sigma
- Planck tension: ~1 sigma
- A_IA prior: 0.83 +/- 0.7 (Gaussian, from red/blue split)
- PSF leakage priors (Paper IV): alpha = 0.005 +/- 0.002, beta = 0.810 +/- 0.113

## Build

```bash
# Render slides
cd docs/talks && quarto render 26_Moriond_UNIONS/26_Moriond_UNIONS.qmd --to revealjs

# Regenerate figure PNGs from paper repos
snakemake talk_figures -j4 --nolock

# Screenshot for QA
cd 26_Moriond_UNIONS && npx decktape reveal "file://$(pwd)/../_site/26_Moriond_UNIONS/26_Moriond_UNIONS.html" screenshots/qa/deck.pdf --screenshots --screenshots-directory screenshots/qa --size 1920x1080
```
