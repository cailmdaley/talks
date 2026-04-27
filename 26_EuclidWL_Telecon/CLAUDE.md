# Euclid WL SWG Telecon: UNIONS-3500 B-mode Validation

Informal 20-min telecon talk on Paper II (B-modes) for the Euclid Weak Lensing SWG.

## Framing Principles

**What this talk is:**
- A methodological story: three B-mode estimators, when they agree and when they don't, and why.
- The Euclid-relevant result: filter functions set sensitivity to contamination, not the measurement basis. COSEBIs computed from ξ± vs from C_ℓ bandpowers both fail at full range, while C_ℓ itself passes.
- A Stage-III lesson for Stage-IV: repeating additive shear bias at CCD scales recurs across surveys (CFHTLenS, KiDS-450, DES-SV, and now UNIONS — all with detector-level effects fixed in focal-plane coordinates). Whether Euclid sees the same depends on detector geometry and dither strategy.

**What this talk is NOT:**
- Not a cosmology talk. S₈, contours, and whisker plots belong in the companion-paper talks (Moriond).
- Not a survey advertisement. Paper I and the catalog story are Sacha's territory.
- Not a tutorial. The SWG audience knows B-modes and E/B decomposition; skip the "what is a B-mode" slides except in backup.

**Tone:** Chill, informal, methodology-forward. Cail lifts prose directly from the paper where possible — the corpus has been vetted through many rounds of editing.

## Talk Arc

### Opening
- UNIONS in the northern sky → UNIONS-3500 at a glance → Paper II within the five-paper release (Catalogues, B-modes/this work, Config-space cosmology, Harmonic-space cosmology, **Image simulations**).

### Why B modes, why this paper
- E modes (gradient) vs. B modes (curl) on cropped pattern figures, full-width text + side-by-side images.
- Stage-III failures have traced CCD additive bias (Asgari+19), PSF higher moments (Zhang+23), astrometric residuals (Wright+25), and HybridEB-driven flips (Jefferson+25). DES-Y6 is the counterexample — same HybridEB, passes, two-paragraph appendix. Filter functions, not estimators, set sensitivity.
- Asgari+19 priors: same oscillatory B_n shape across CFHTLenS / KiDS-450 / DES-SV; mock systematics each leave a fingerprint. UNIONS will look like this.

### Methods
- Three E/B-separable statistics: pure-mode ξ±^E/B, COSEBIs, catalog-based C_ℓ^EE/BB. Pure-mode and COSEBIs deproject ambiguous modes; the C_ℓ estimator absorbs leakage into BB.
- Gaussian-only covariance (CosmoCov + NaMaster iNKA), validated on 350 GLASS mocks. Conservative.

### Results
- Three data-vector slides: pure-mode (low-level structure outside cuts), COSEBIs (full-range >4σ first-mode excess, suppressed by cuts), C_ℓ^BB (low-level offset, passes adopted range).
- Catalog versions PTE table: only fiducial (tightened-size-cut) passes all three.
- Scale-cut PTE scan: adopted cuts sit in broad stable regions.

### The punch line
- COSEBIs from ξ± vs from C_ℓ bandpowers agree for all twenty modes; both fail where C_ℓ passes. Filter functions, not basis. Empirical support for the Asgari+19 and Jefferson+25 line of argument.

### Discussion
- Repeating additive bias: MegaCam lineage with CFHTLenS; UNIONS dithers by ~1/3 FoV (attenuate, not eliminate). Paper V identifies a pipeline-specific source: improper exposure-offset propagation imprints coherent additive shear at CCD scales.
- For Euclid: different detector geometry, same filter-function principle.

### Close
- B modes pass at adopted cuts across all three statistics; oscillatory COSEBI pattern at full range; only fiducial passes everywhere; filter functions, not basis. arXiv link on closing slide.

## Build

```bash
# Render slides
cd docs/talks && quarto render 26_EuclidWL_Telecon/26_EuclidWL_Telecon.qmd --to revealjs

# Text QA (faster, more precise than screenshots)
node ~/.claude/skills/slides/scripts/slide-to-text.mjs \
  _site/26_EuclidWL_Telecon/26_EuclidWL_Telecon.html [slide# or range] [--flags-only]

# Visual QA (decktape with absolute paths to avoid path doubling; run from /tmp)
cd /tmp && decktape reveal \
  "file://$(pwd -P /automnt/n17data/cdaley/unions/pure_eb/docs/talks)/_site/26_EuclidWL_Telecon/26_EuclidWL_Telecon.html" \
  deck.pdf --screenshots \
  --screenshots-directory /automnt/n17data/cdaley/unions/pure_eb/docs/talks/26_EuclidWL_Telecon/screenshots/qa \
  --size 1920x1080
```

## Citations

Main-deck citations are **manual markdown hyperlinks** to arXiv (e.g., `[Asgari+19](https://arxiv.org/abs/1810.02353)`), not `@citeprockey` syntax. This gives clickable references with zero dependency on a bib file or external CSL. The rendered citation is the link text; clicking opens arXiv.

A copy of `unions_bmodes.bib` remains in this dir for convenience (looking up arXiv IDs when adding new references), but nothing in the qmd references it.

## Styling

- `custom.scss` — copied from Moriond; Raleway font, 45px root, structural rules for columns, bullets, footer. Logo positioning rules left in but unused here.
- `title-slide.html` — Moriond partial with the three logo `<img>` tags stripped (CEA, CosmoStat, Moriond).
- No title-slide logos by design (informal internal telecon; the user asked for them off).

## Assets

- `images/` and `assets/` are symlinks to the shared `docs/talks/images/` and `docs/talks/assets/` pools. Never populate a local images dir — see the parent `CLAUDE.md`.

## Related fibers

- `euclid-wl-telecon-talk` — active fiber for this talk
- `catalog-versions-v1-4-5-through` — catalog version ground truth
- `paper-figures-unified-style` — figure styling conventions
