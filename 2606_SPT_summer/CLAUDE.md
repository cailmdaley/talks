# 2606_SPT_summer — talk narrative & build notes

The talk Cail gives **remotely** at the **SPT Summer Collaboration Meeting 2026**
(F2F Mon Jun 29 – Thu Jul 2). Audience: the **SPT-3G collaboration** — they know
CMB lensing and the SPT-3G winter GMV reconstruction cold; they are *less*
familiar with Euclid TR1 (the new galaxy density + weak-lensing shear data) and
with the cross-correlation specifics. Spend the motivation budget on Euclid and
the overlap, not on what CMB lensing is.

**Headline:** a **status report** on the **Euclid MoU CMB-lensing ×
cross-correlation project** (Cail Daley & Margherita Lembo) — where the Euclid TR1
× SPT-3G κ-cross programme stands: footprints → blinding → data vectors (all three
crosses) → estimator consistency → SPT-vs-ACT → likelihood/bias plans →
systematics → simulations.

**Frame (non-negotiable, set by the managing constitution
`explorations/spt-talk-push`):** *status report under the blind*, not a results
talk. The detection/amplitude arc (the sub-unity Â ≈ 0.63 spine) is real but
**blinded and OFF this talk** while in progress. Every panel reads under the blind
— **shapes, relative consistency, error-bar sizes, never the absolute amplitude**.
We are honest about what is and isn't under control. This is the ~11-slide deck
below; the retired ~17-slide "detection + robustness" deck (Â≈0.63 headline,
amplitude/ℓ-flat/open-question slides) is GONE — do not reconstruct it.

## Claim discipline — the wording is load-bearing (Q&A too)

No amplitude number appears on any slide — the amplitude arc is blinded and
dropped. The only numbers that show are **blind-safe by construction**: estimator
pull RMS <1σ, extinction X_ℓ/σ sub-σ, the SPT-vs-ACT σ-crossover ℓ≈200. Each is
traceable to a trusted figure built from the sealed bundle. Two phrasings stay
**banned** because they over-reach (audit:
`…/5x2pt-amplitude-robustness/amplitude-claims-tempered`) — they matter most now
in **Q&A**, where the amplitude story will get probed:

- **NOT "foreground-clean-safe."** Say **"estimator-robust; the bias+profile-hardening
  correction is bounded at <1σ"** (γκ pull RMS 0.28σ, δκ 0.29σ, all 120 bandpowers
  <1σ, no detection-S/N cost). A foreground term *common* to GMV and the hardened
  estimator cancels in the difference and is *not* excluded; the direct test is the
  reserved Websky/Agora-with-HOD recovery, **not yet run**. (This is exactly the
  slide-5 caveat and its speaker note.)
- **NOT "the sub-unity amplitude is localised off the κ reconstruction onto Euclid."**
  Cross-probe localisation is *suggestive only*.

If pressed on the amplitude in Q&A, the honest background (NOT on a slide): the
spine is Â = 0.63 ± 0.05 (PTE 0.73), 12-cross equal-window full **data-fiducial
Gaussian** covariance; ℓ-flat at ~0.65 across ℓ∈[150,3000]; carries a ~1.6σ family
split (gc×κ 0.72 vs γ×κ 0.59). It *strengthens* under Knox→Gaussian. But the talk
reports status, not this number.

## The narrative arc (current deck — headlines read top-to-bottom as the story)

~11 slides for a ~20-min collaboration slot. Source: `2606_SPT_summer.qmd`.
Figures come ONLY from the trusted, blind-safe set (copied into `../images/`);
never regenerate a cosmology plot here.

1. **Status report (title/center)** — "A status report on the Euclid MoU
   CMB-lensing × cross-correlation project." Today's roadmap + timeline (Euclid
   cosmology products → June 2027; DR1 freeze slip — `[CONFIRM]` the exact prior
   date before presenting).
2. **Euclid footprints and overlaps** — r-stack reveal: Euclid TR1 → +SPT-3G
   winter → +ACT DR6. (`spt26_footprint_{1_euclid,2_spt,3_act}.png`; the real TR1
   effcov>0.8 South analysis mask, 380.6 deg², TR1∩SPT 189.3 deg².)
3. **Getting blinding out of the way** — Muir et al. 2019 parameter-shift blind
   (same family as SPT-3G D1 & Euclid 3×2pt); hidden cosmology θ_blind added to
   the **data** only; theory internal (eDR1like), plan to move toward CLOE.
   (`spt26_blinding_cosmologies.png`.)
4. **Data vectors: the three cross-correlations** — the spine is δ_g×κ and γ×κ
   (six bins each, NaMaster on the joint mask); third cross is GGL (δ_g×γ, the
   source-behind-lens config). Amplitudes/S/N stripped — shapes only.
   (`spt26_cross_spectra.png`; backup `spt26_ggl_matrix.png`.)
5. **Robust to the SPT-3G lensing estimator** — bin 6, γ×κ + δ_g×κ, GMV vs PP vs
   GMVbhTTprf sitting on top of each other → estimator-robust (hardening <1σ).
   (`spt26_estimator_robustness.png`.) ⏳ **STILL ON RR2** — see "Pending TR1".
6. **Two κ surveys on the same Euclid bins** — SPT-3G GMV vs ACT DR6 over the
   common fiducial theory; two independent reconstructions on the same southern
   bins. (`spt26_cross_survey.png`, TR1.)
7. **Which κ survey constrains where** — markers on fiducial theory, only the
   error bars real (exact full data-fiducial Gaussian σ, both surveys, TR1 log15):
   SPT tighter for ℓ≳200, ACT marginally tighter only at ℓ≲180; crossover ℓ≈200.
   (`spt26_kappa_constraints.png`.)
8. **Likelihood — the plan** — joint Gaussian likelihood over the cross vector;
   per-bin {A, b_i}; δ_gδ_g tightens b_i ~2.5× but does **not** break A–b (no
   amplitude numbers — blinded).
9. **Systematics: galactic extinction is sub-σ in every bin** — DES/Chang coherent
   bias X_ℓ = C^{κS}C^{fS}/C^{SS} in units of σ, per bin, δ_g×κ + γ×κ; sub-σ at
   every bandpower (worst |X/σ|≈0.46), aggregate 0.35–0.8σ. "One template is not a
   systematics budget." (`spt26_extinction_xell.png`.) ⏳ **STILL ON RR2** — see below.
10. **Simulations** — DEMNUni/FLASK → mock covariance; Agora (Gatti Euclid-like
    products) + systematics-injected GLASS box for foregrounds; D1 κ̂−κ_true noise
    realizations; the ambitious D1-on-FFP10 cross-covariance between Planck/ACT/SPT.
11. **Summary & next steps (center)** — status: maps & fields, self-blind, all
    three crosses, estimator- and cross-survey-consistent. Next: joint {A,b_i},
    mock cov, close systematics, DR1. Thanks.

## Pending TR1 — the two figures still reading RR2

Slides 5 (`spt26_estimator_robustness.png`) and 9 (`spt26_extinction_xell.png`)
still read the RR2 pipeline. They are **blind-safe and carry no RR2/TR1 label**, so
they don't misrepresent — and the scientific message (estimators agree; extinction
sub-σ) is identical on RR2 and TR1. For full honesty they should move to TR1, the
open task in `explorations/spt-talk-push`:

- **Extinction (slide 9)** — the three extinction recipes
  (`tracer_extinction_cross_spectra`, `kappa_extinction_cross_spectrum`,
  `extinction_contamination_metric`) are already `release_env.sh`-parameterized, so
  `lc run -u tr1 …` produces the TR1 products under
  `results/tr1_v1p1-v0.1/systematics/`. Then repoint `make_extinction_xell.py` (its
  `SYS`/`XS` roots) at TR1 and re-render.
- **Estimator (slide 5)** — the two estimator-cross recipes
  (`spt_estimator_datavector_comparison`, `clustering_estimator_datavector_comparison`)
  are **RR2-hardcoded** (the deferred "snakemake-bridge"); they need a
  `release_env.sh` refactor (mirror the migrated spectra recipes) before `lc run -u tr1`
  can build the per-estimator TR1 crosses `{shear_lensmc,gc}_x_spt_est_{gmv,pp,gmvbhttprf}`.
  Then repoint `make_estimator_robustness.py` and re-render.

## Blinding & figure provenance

Every data figure is built from the **re-sealed TR1 blinded bundle**
(`results/tr1/cosmology_shift_talk_datavector/talk_datavector_blinded.pkl`,
commitment `852da2ed…`; the unblinded twin + seal are gitignored soft-secrets under
`results/tr1/blinding/` — never commit/share). The figure scripts add the same
cosmology-shift ΔCℓ to every estimator/bin, so relative consistency is exact while
the absolute amplitude is hidden; `--unblinded` exists for debugging and is
watermarked + off by default. Harmonic axes use the shared
`_ell_axis.py` helper (labelled integer ticks: 100/200/300/500/1000/2000/3000).

## Build

Quarto + reveal.js. Scaffolding copied from `25_SPT_f2f` / `2606_SPT_secondaries`
(custom.scss, title-slide.html, assets/ + images/ symlinks).

```bash
cd /leonardo_work/EUHPC_E07_074/cdaley00/cmbx/docs/talks
quarto render 2606_SPT_summer/2606_SPT_summer.qmd --to revealjs   # → 2606_SPT_summer/index.html
node ~/.claude/skills/slides/scripts/slide-to-text.mjs _site/2606_SPT_summer/index.html --flags-only   # text QA
```

The self-contained render embedded at the top of the managing constitution is
`slides.html` (copied into the fiber dir). Deployment is Cail-gated: pushing the
`talks` repo to `main` triggers the Pages Action (see `../CLAUDE.md`); do not push
without Cail.

Figures live in the shared pool `../images/` (symlink). Source PNGs are copied from
the trusted dashboard set; record provenance in commits.
