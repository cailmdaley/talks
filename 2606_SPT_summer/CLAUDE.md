# 2606_SPT_summer — talk narrative & build notes

The talk Cail gives **remotely** at the **SPT Summer Collaboration Meeting 2026**
(F2F Mon Jun 29 – Thu Jul 2). Audience: the **SPT-3G collaboration** — they know
CMB lensing and the SPT-3G winter GMV reconstruction cold; they are *less*
familiar with Euclid TR1 (the new galaxy density + weak-lensing shear data) and
with the cross-correlation specifics. Spend the motivation budget on Euclid and
the overlap, not on what CMB lensing is.

**Headline:** the first high-S/N **Euclid TR1 × SPT-3G CMB-lensing (κ)
cross-correlation**.

**Frame (non-negotiable, set by the managing constitution
`explorations/spt-talk-push`):** *detection + robustness*, with the **sub-unity
amplitude Â ≈ 0.63 ± 0.05 (PTE 0.73)** presented as **the genuine open question**,
not a result to explain away. We are honest about what is and isn't under control.

## Claim discipline — the wording is load-bearing

Every number below reproduces from the on-disk product. Two phrasings are
**banned** because they over-reach (audit:
`…/5x2pt-amplitude-robustness/amplitude-claims-tempered`):

- **NOT "foreground-clean-safe."** Say **"estimator-robust; the bias+profile-hardening
  correction is bounded at <1σ"** (γκ RMS 0.28σ, δκ 0.29σ, all 120 bandpowers <1σ,
  no detection-S/N cost). A foreground term *common* to GMV and the hardened
  estimator cancels in the difference and is *not* excluded; the direct test is
  the reserved Websky/Agora-with-HOD recovery, **not yet run**.
- **NOT "the sub-unity amplitude is localised off the κ reconstruction onto Euclid."**
  Cross-probe localisation is *suggestive only*. State the family split as a
  separate, honest axis (below).

Amplitude conventions — keep distinct, never conflate:
- **Â = 0.63 ± 0.05, PTE 0.73** — 12-cross equal-window, full **data-fiducial
  Gaussian** covariance. **THE HEADLINE.**
- **Â = 0.74 ± 0.03 (Knox-diagonal)** — companion only; Knox *over-tightened* the
  fit (cross-only PTE 1.9e-6 → 0.73 under the Gaussian off-diagonals). The
  sub-unity amplitude *strengthens* under a better covariance.
- **Â = 0.61 ± 0.05 (GLS joint estimator)** — ~0.4σ from the equal-window number;
  mention only if asked, don't imply it's the same number.
- Â = data / **untuned Planck-18** prediction (windowed fiducial theory, no
  IA/m/n(z) tuning). So "0.63" = 63% of the untuned prediction.

The ℓ-shape (locked astra finding `gaussian_cross_amplitude_flat_in_ell`):
- **A is ℓ-FLAT at ~0.65 across ℓ ∈ [150, 3000]** on the Gaussian basis. Not a
  high-ℓ feature (kills baryons / nonlinear bias / high-ℓ systematic by
  ℓ-signature) and not a low-ℓ feature.
- **ℓ < 150 is covariance-unstable** (cond 8.4e5) — consistent with *both* 0.63
  and unity. Don't read a low-ℓ story into it (both round-0 low-ℓ stories were
  covariance artifacts pulling opposite ways).
- Caveat the flat number carries: it is an aggregate over a **~1.6σ family split**
  — gc×κ 0.72 ± 0.06 vs γ×κ 0.59 ± 0.06. ℓ-flat and probe-consistent are
  *different axes*; do not let "ℓ-independent normalization" silently absorb the
  family offset.

## The narrative arc (headline = the "so what", one transferable message each)

~17 slides for a ~20-min collaboration slot. Headlines read top-to-bottom as the
story. Figures come ONLY from the trusted set assembled in the dashboard
(`explorations/spt-talk-push/report.html`) — copied into `../images/`; never
regenerate a cosmology plot here.

1. **Title** — "The first Euclid × SPT-3G CMB-lensing cross-correlation."
2. **Bottom line up front** — "We detect Euclid TR1 × SPT-3G κ at high S/N — at an
   amplitude ~⅓ below an untuned Planck-18 prediction, and that deficit is the
   honest open question." (text teaser; sets the frame)
3. **Why this cross** — "CMB-lensing × galaxy cross-correlations pin growth and
   self-calibrate the galaxy tracers — SPT-3G + Euclid open a new high-S/N
   southern overlap." (κ is mass, bias-free; cross-calibrates shear m & n(z))
4. **Euclid TR1** — "Euclid TR1 brings ~30% of DR1: galaxy density and weak-lensing
   shear over the southern sky." (the tracers δ_g, γ; tomographic n(z))
5. **The footprint** — "The SPT-3G winter GMV field overlaps Euclid TR1 — this is
   the patch the analysis lives on." (FOOTPRINT figure)
6. **The data vector** — "We form a 5×2pt data vector; the spine for SPT is the two
   CMB-lensing crosses, δ_g×κ and γ×κ." (NaMaster bandpowers; estimator one-liner)
7. **Detection** — "Both κ cross-spectra are detected at high S/N and track the
   Planck-18 shape." (BANDPOWERS-VS-THEORY spine figure; S/N ~22–24 per cross)
8. **Amplitude headline** — "A single-amplitude fit gives Â = 0.63 ± 0.05 (PTE 0.73)
   — a robust detection at a sub-unity amplitude." (AMPLITUDE figure)
9. **ℓ-flat** — "The deficit is ℓ-flat at ~0.65 across ℓ∈[150,3000]; ℓ<150 is
   covariance-unstable." (AMPLITUDE-BY-ℓ figure) — kills high-ℓ/low-ℓ stories.
10. **The open question** — "What is an ℓ-independent ~0.65 deficit consistent with?"
    Favored: normalization — n(z) mean-z/tail, shear multiplicative m, IA — or a
    genuine low amplitude. Demoted by wrong ℓ-signature: baryons, nonlinear/scale-
    dependent bias, high-ℓ systematics. **The centerpiece; ask the collaboration.**
11. **Robustness — covariance** — "The sub-unity amplitude survives and *strengthens*
    when Knox → full data-fiducial Gaussian (PTE 1.9e-6 → 0.73)." (COVARIANCE/Knox-vs-
    Gaussian figure if available; else the amplitude shift stated)
12. **Robustness — estimator + family split** — "The crosses are estimator-robust
    (hardening <1σ); the one honest tension is the ~1.6σ gc×κ (0.72) vs γ×κ (0.59)
    split." (δκ estimator-comparison figure)
13. **δδ supporting** — "Galaxy clustering is consistent with the same sub-unity
    story (3-probe χ²=9.5/6, PTE 0.15) but does not yet break the amplitude–bias
    degeneracy." (δδ JOINT-FIT figure; flag bin4 −2.4σ, tilt at ℓ≈130–390)
14. **GLASS mocks / scale cut** — "GLASS mocks show the GC-auto high-ℓ excess is NGP
    gridding aliasing — an empirical ℓ≲865 scale cut; mechanism proven, no closed-
    form factor." (GLASS RECOVERY figure; consistent w/ Wolz 2024 App. B)
15. **What's not yet under control** — "Two honest gaps: the on-disk shear auto is a
    broken spin-2 product (no Â_γγ yet), and systematics are quantified only for
    extinction (~1.5σ) — one number does not close systematics."
16. **Blinding** — "Cross-correlations are out of SGS blinding scope by
    construction; we roll a standalone loose self-blind on the talk timescale."
    (optional / can fold into #15 or #17)
17. **Summary & outlook** — "First Euclid×SPT-3G κ-cross: a covariance- and
    estimator-robust detection at Â=0.63±0.05; the ℓ-flat sub-unity amplitude is the
    open question. Next: γγ fix, joint {A,b_i}, mock covariance, DR1." (+ Thanks)

## Build

Quarto + reveal.js. Scaffolding copied from `25_SPT_f2f` / `2606_SPT_secondaries`
(custom.scss, title-slide.html, assets/ + images/ symlinks).

```bash
cd /leonardo_work/EUHPC_E07_074/cdaley00/cmbx/docs/talks
quarto render 2606_SPT_summer/2606_SPT_summer.qmd --to revealjs   # → 2606_SPT_summer/index.html
node ~/.claude/skills/slides/scripts/slide-to-text.mjs _site/2606_SPT_summer/index.html --flags-only   # text QA
```

Figures live in the shared pool `../images/` (symlink). Source PNGs are copied
from the trusted dashboard set; record provenance in commits.
