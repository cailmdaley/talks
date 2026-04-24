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

### Opening (slides 1-3)
- Title + Paper II context within the five-paper release.
- Motivation: B-modes as Stage-III systematics diagnostic. Stage-III failures have traced CCD additive bias, PSF higher moments, astrometric systematics. Frame as shared Stage-III/IV problem.

### Methods (slides 4-5)
- Three E/B-separable statistics in one slide: pure-mode ξ±^E/B, COSEBIs, C_ℓ^BB. Emphasize that pure-mode and COSEBIs deproject ambiguous modes; harmonic doesn't.
- Covariance: Gaussian-only (conservative), CosmoCov + MC propagation in config, NaMaster iNKA in harmonic, validated on 350 GLASS mocks.

### Results (slides 6-10)
- Three data-vector slides: pure E/B, COSEBIs (orange = full range oscillations; blue = after cuts), C_ℓ^BB.
- Catalog versions PTE table: four variants tested, only fiducial passes all three.
- Scale-cut PTE scan: adopted cuts sit in broad stable regions.

### The punch line (slide 11)
- Filter functions, not basis, set sensitivity. COSEBIs from ξ± and from C_ℓ agree for all twenty modes; both fail where C_ℓ passes. Empirical support for Asgari+19a and Jefferson+25.

### Discussion (slides 12-13)
- Repeating additive shear bias: MegaCam lineage with CFHTLenS. UNIONS dithers by ~1/3 FoV which may attenuate but not eliminate. Paper V identifies pipeline-specific exposure-offset source in addition.
- Implications for Euclid: different detector geometry but same filter-function principle. Paper V identifies pipeline-specific exposure-offset source that could be informative.

### Close (slide 14)
- Conclusions: consistent with zero at adopted cuts; oscillatory COSEBI pattern at full range; only fiducial passes everywhere; filter functions, not basis; any failure warrants scrutiny across all frameworks.

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

## Bibliography

`unions_bmodes.bib` is copied from `../../unions_release/unions_bmodes/unions_bmodes.bib`. If the paper bib changes and those changes affect citations used here, re-copy.

Citation style: A&A (via CSL). Keys use the `asgari.etal19a` / `schneider.etal22` convention from the paper.

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
