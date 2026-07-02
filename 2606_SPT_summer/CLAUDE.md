# 2606_SPT_summer — talk narrative & build notes

The talk Cail gives **remotely** at the **SPT Summer Collaboration Meeting 2026**
(F2F Mon Jun 29 – Thu Jul 2). Audience: the **SPT-3G collaboration** — they know
CMB lensing and the SPT-3G winter GMV reconstruction cold; they are *less*
familiar with Euclid TR1 (the new galaxy density + weak-lensing shear data) and
with the cross-correlation specifics. Spend the motivation budget on Euclid and
the overlap, not on what CMB lensing is.

**Headline:** a **status report** on the **Euclid MoU CMB-lensing ×
cross-correlation project** (Cail Daley & Margherita Lembo) — where the Euclid TR1
× SPT-3G κ-cross programme stands: footprints → blinding → data vectors (the
CMB-only 3×2pt) → estimator consistency → SPT-vs-ACT → systematics →
likelihood/bias plans → simulations.

**Frame (non-negotiable, set by the managing constitution
`explorations/spt-talk-push`):** *status report under the blind*, not a results
talk. The detection/amplitude arc is real but **blinded and OFF this talk** while
in progress. Every panel reads under the blind — **shapes, relative consistency,
error-bar sizes, never the absolute amplitude**. We are honest about what is and
isn't under control. This is the ~11-slide deck below; the retired ~17-slide
"detection + robustness" deck (amplitude headline, ℓ-trend/open-question slides)
is GONE — do not reconstruct it.

**This repo is public.** No unblinded number — no amplitude value, no
sub-/super-unity statement about this data — may appear anywhere in it: not in
slides, not in speaker notes, not in tracked figures, and not in this file. The
blinded background lives in the (private) felt store, not here.

## Claim discipline — the wording is load-bearing (Q&A too)

No amplitude number appears on any slide — the amplitude arc is blinded and
dropped. The only numbers that show are **blind-safe by construction**: estimator
pull RMS <1σ, extinction X_ℓ/σ sub-σ, the SPT-vs-ACT σ-crossover ℓ≈200. Each is
traceable to a trusted figure built from the sealed bundle. Two phrasings stay
**banned** because they over-reach (audit:
`…/5x2pt-amplitude-robustness/amplitude-claims-tempered`) — they matter most now
in **Q&A**, where the amplitude story will get probed:

- **NOT "foreground-clean-safe."** Say **"estimator-robust; the bias+profile-hardening
  correction is bounded at <1σ"** (TR1: γκ pull RMS 0.29σ, δκ 0.29σ, all 90 log15 bandpowers
  <1σ, no detection-S/N cost — S/N if anything rises). A foreground term *common* to GMV and the hardened
  estimator cancels in the difference and is *not* excluded; the direct test is the
  reserved Websky/Agora-with-HOD recovery, **not yet run**. (This is exactly the
  slide-5 caveat and its speaker note.)
- **NOT any claim localising the amplitude onto one side** (the κ reconstruction
  vs the Euclid probes). Cross-probe localisation is *suggestive only*.

If pressed on the amplitude in Q&A, the honest background lives OFF this public
repo: `felt show science/cmbx/explorations/spt-talk-push/qa-amplitude-background`
(private felt store). The talk reports status, not numbers.

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
4. **Data vectors: Gaussian NaMaster error bars** — the CMB-only 3×2pt (Louis's
   framing, 2026-07-01): of the 6×2pt's six spectra, only δ_g×κ and γ×κ are
   measured here — κκ is the third that involves CMB-κ but folds in only at the
   likelihood level, not plotted; galaxy–galaxy lensing (δ_g×γ) is dropped
   entirely — it's a standard Euclid 3×2pt product from the main 3×2pt group
   already, not something new this MoU proposes (was a third row through
   2026-06-30; removing it also let the remaining two rows render bigger). SPT-3G
   GMV-hardened, six bins each, NaMaster on the joint mask, error bars now the
   FULL data-fiducial Gaussian covariance (was Knox through 2026-06-30 — Louis
   asked directly what error bars were shown, so it's on the slide title itself
   now). Amplitudes stripped — shapes + blinded per-bin S/N only.
   (`spt26_cross_spectra.png`; backup `spt26_ggl_matrix.png`, GGL still generated
   for Q&A even though it's off the main slide.)
5. **Robust to the SPT-3G lensing estimator** — bin 5, γ×κ + δ_g×κ, GMV vs the
   bias + profile-hardened reconstruction (GMVbhTTprf) sitting on top of each
   other → estimator-robust (hardening RMS 0.29σ both crosses, all 90 bandpowers
   <1σ, no S/N cost); PP (pol-only) noisier at high ℓ. (`spt26_estimator_robustness.png`, TR1.)
6. **SPT and ACT are consistent, SPT is higher S/N** — SPT-3G GMV-hardened vs ACT
   DR6 over the common fiducial theory; two independent reconstructions on the
   same southern bins. In-panel PTE(SPT-ACT) only (not the full reduced-χ²); the
   slide overlays a plain-language "Naive PTE / considerable overlap" caption.
   (`spt26_cross_survey.png`, TR1.)
7. **Which κ survey constrains where** — markers on fiducial theory, only the
   error bars real (exact full data-fiducial Gaussian σ, both surveys, TR1 log15):
   SPT tighter for ℓ≳200, ACT marginally tighter only at ℓ≲180; crossover ℓ≈200.
   Overlay caption: "Ongoing validation: ℓ_max, apodization scale" (replaced
   "time to start thinking about scale cuts" 2026-07-01 — Léa Dumilly's
   Cℓ-settings sweep is already running; see
   `felt show science/cmbx/methodology/lea-cl-settings-validation`).
   (`spt26_kappa_constraints.png`.)
8. **Systematics: extinction is sub-σ for shear, ~1σ at high-ℓ for clustering** —
   (now precedes Likelihood — reordered 2026-07-01) DES/Chang coherent bias
   X_ℓ = C^{κS}C^{fS}/C^{SS} in units of σ, per bin, δ_g×κ + γ×κ. On TR1
   (`lc run -u tr1`): shear sub-σ everywhere (aggregate 0.4–0.85σ); clustering
   sub-σ at low/mid-ℓ but rises at high-ℓ (ℓ≳1000) toward 1σ, growing with z-bin
   (coherent S_bias 0.9→1.5σ, gc bin6 bandpower at 1.0σ). Surprising: largest at
   HIGH ℓ, opposite the smooth-template expectation. "One template is not a
   systematics budget." (`spt26_extinction_xell.png`, TR1.) See
   `…/spt-talk-push/tr1-extinction-highell-clustering`.
9. **Likelihoods are coming together** (retitled from "Likelihood — what's
   built, and the plan" 2026-07-01: active assertion, not a label) — content
   verified line-by-line
   against the eDR1like code on the `cail` branch (which contains the full
   `origin/update_likelihood` tip — Margherita's branch, MR !7 → v1.0)
   2026-07-01. **In place**: Gaussian likelihood over ANY subset of the 6×2pt
   (γγ IS supported — WeakLensingTracer; κκ enters here, the slide-2 promise);
   NaMaster covariance from file; Cobaya sampling; CCL Limber theory,
   HMCode-2020 nonlinear, RSD + magnification bias (fixed s(z), NOT sampled);
   galaxy bias fit on RR2+TR1 (linear b_i global/per-bin, b₂/b_s available);
   photo-z Δz_i + w_z,i marginalization (global or binwise). **Not yet in the
   sampled model** (all verified absent): no multiplicative m_i anywhere; IA is
   a fixed constant-amplitude template in the shear tracer (NLA params loaded
   but not wired, not marginalized); Hartlap/Sellentin absent (needed only once
   the covariance comes from mocks — in the notes, NOT on the slide; Cail
   trimmed it 2026-07-01 as non-crucial). Right column is two blocks for
   evenness: "Not yet in the sampled model:" (m_i + IA one bullet; mock cov →
   see next slide) then "CLOE: Euclid's inference framework — theory done,
   likelihood in progress" (wording chosen 2026-07-02 so the header fits one
   line in small-caps). The two column hrs are pixel-aligned: the right column's
   hr takes `calc(0.55em + 60px)` top margin (custom.scss, `.likelihood` slide
   class) so the rules sit level (Cail 2026-07-02 — near-miss alignment read as
   a mistake). The A–b degeneracy is NOT on this slide anymore — it's a thing to
   *try*, moved to slide 11's Next line (δ_gδ_g tightens b_i ~2.5× but A·b stays
   degenerate — notes carry it).
10. **Simulations: covariance & systematics** (rebuilt 2026-07-02 from "mocks
    for covariance, foregrounds, and noise" — two conceptual halves, one per
    column). **Left, covariance** (no bullets — one item per colhead, Cail
    2026-07-02): DEMNUni/FLASK → mock data vector + mock-based covariance;
    "**D1 lensing reconstructions**" with a forced line break after the bold
    phrase, then "minus truth (κ̂−κ_true) → realistic κ noise" (the
    parenthetical was wrapping alone — Cail 2026-07-02); cross-covariance
    *(ambitious)* — D1 pipeline on Planck FFP10 → Planck/ACT/SPT. **Right,
    systematics — "three simulated skies":** Agora (CMB side, correlated
    extragalactic foregrounds; Euclid-like WL products from its halos +
    density shells — Marco Gatti, in progress), Flagship (Euclid side:
    realistic, one realization — Agora's counterpart; it is to Euclid what
    Agora is to the CMB), GLASS (fast lognormal mocks with KNOWN Euclid
    systematics injected — extinction/depth/stars), with a sub-bullet: →
    could port the same injections into the Euclid-like Agora mocks.
    Deck-wide, `.colhead` small-caps headers are cinnabar (Cail 2026-07-02,
    aesthetics; the `(ambitious)` aside drops to weight 400 so it still reads
    as an aside). Speaker notes carry the *grounded* DEMNUni
    story from the KP3 wiki (see
    `felt show science/cmbx/talks/spt-secondaries-2606-slides`): CMBX sim team
    (Calabrese/Vielzeuf/Carbone/Fabbian/Baldi, paper in prep), 2 Gpc/h N-body
    across ΛCDM / Mν=0.16,0.32,0.53 eV / f(R) (DUSTGRAIN), SUBFIND → SHAM
    galaxies calibrated to Flagship bias+n(z), full-sky nside-4096 correlated
    κ_CMB(+ISW-RS)/WL/galaxy maps, QE recons with SO noise; niche = correlated
    *signal* mock data vector for likelihood validation, while covariance
    proper is the FLASK-lognormal + Gaussian-fiducial route (the DES×SPT /
    ACT×DES recipe: lognormal signal + per-experiment recon-noise residuals).
11. **Summary & next steps (center)** — status: maps & fields, self-blind, all
    three crosses, estimator- and cross-survey-consistent (headers in the
    `.colhead` treatment: "Where we are:", "Systematics checked:",
    "Systematics to check:", "Next:"). Next: joint {A,b_i},
    try breaking A–b (shear-ratio geometry? δ_gδ_g scale range? — the open
    design question, notes invite thoughts), mock cov, close systematics, DR1. Closes on a simple "Thank you for
    listening — and to the SPT and Euclid members who made this work possible"
    (simplified 2026-07-01; the fuller named acknowledgment lives in the speaker
    notes, spoken not shown).

## TR1 migration — complete (every data figure on TR1)

**Extinction (slide 9) — on TR1.** Built via `lc run -u tr1`
(`tracer_extinction_cross_spectra`, `kappa_extinction_cross_spectrum`,
`extinction_contamination_metric`); products in the lc-canonical `results/tr1/<output_id>/`
tree (the same tree the spine reads). `make_extinction_xell.py` points there. The TR1
numbers shifted the slide honestly (slide 9 above) — a real finding, not a cosmetic swap.

**Estimator (slide 6) — on TR1.** The three estimator recipes
(`spt_estimator_spike_comparison` + the two `*_estimator_datavector_comparison` outputs)
were the last RR2-hardcoded holdouts; migrated to the `release_env.sh` pattern
(`data_release` in decisions, `$RESULTS_ROOT`/`$VALIDATED_ROOT`/`$REDSHIFT_ROOT`).
`lc run -u tr1` (job 47833097) builds the per-estimator crosses
`{shear_lensmc,gc}_x_spt_est_{gmv,pp,gmvbhttprf,ttbhttprf}` into the
`results/tr1_v1p1-v0.1/cross_spectra/` working tree; `make_estimator_robustness.py`
reads them there. **TR1 confirmed the RR2 story to <0.01σ**: gmvbhttprf vs GMV RMS 0.29σ
in both crosses, all 90 log15 bandpowers <1σ, no S/N cost; PP (pol-only) noisier at high
ℓ. Slide caption/notes updated honestly (PP no longer lumped into the <1σ claim); the
gmv-estimator cross is byte-identical to the spine.

## Blinding & figure provenance

Every data figure is built from the **re-sealed TR1 blinded bundle**
(`results/tr1/cosmology_shift_talk_datavector/talk_datavector_blinded.pkl`,
commitment `852da2ed…`; the unblinded twin + seal are gitignored soft-secrets under
`results/tr1/blinding/` — never commit/share). The figure scripts add the same
cosmology-shift ΔCℓ to every estimator/bin, so relative consistency is exact while
the absolute amplitude is hidden; `--unblinded` exists for debugging and is
watermarked + off by default. Figures use a clean seaborn `ticks` aesthetic (no
in-plot grid) via the shared `_ell_axis.py` helper: `style_ell_axis` (labelled
integer ℓ-ticks 100/200/500/1000/3000 + minor ticks) and `fold_yscale` (the y-axis
scale factor folded into the label, `ℓCℓ [×10⁻⁶]`, not a floating offset;
y-tick mantissas are forced INTEGER deck-wide via `MaxNLocator(steps=[1,2,5,10])` —
decimal tick labels are wider and visibly resize the axes box between sibling
figures; Cail 2026-07-01).

## Build

Quarto + reveal.js, on the **shared house theme** (`../assets/house.scss`): warm
parchment ground, EB Garamond + IBM Plex Mono, a single cinnabar accent, the
figure-on-ground halo, small-caps footer/occasion, a cinnabar kicker-rule under
each `##`. The deck consumes it in two lines —
`theme: [default, ../assets/house.scss, custom.scss]` plus `margin: 0` and the
`assets/figure-treatment.html` include (which multiplies the white seaborn figures
onto the ground; no figure regeneration needed). **Big in-column section headers deck-wide use `[Header:]{.colhead}`** — EB
Garamond small-caps + trailing colon (custom.scss), replacing the old
bold-Garamond + em-dash look (Cail 2026-07-02: "colons for all the big
headers", small-caps face; same OpenType treatment as the house
footer/occasion). The cinnabar `[(ambitious)]{.ambitious}` aside nests inside a
colhead. `custom.scss` is otherwise thin (the title logo-bar nudges); `title-slide.html` uses the house spacer + an
Euclid·CEA·CosmoStat logo bar. Text slides that should sit vertically centred use
`{.vcenter}` (the house opt-in; reveal's `.center` is pinned to top:0 by the
theme). The house theme is the going-forward look, extracted from the CNRS
Rising-Talents deck (`26_CNRS_RisingTalents`); to re-skin the palette, set vars in
a `brand.scss` listed *before* house.scss.

```bash
cd /leonardo_work/EUHPC_E07_074/cdaley00/cmbx/docs/talks
quarto render 2606_SPT_summer/2606_SPT_summer.qmd --to revealjs   # → 2606_SPT_summer/index.html
node ~/.claude/skills/slides/scripts/slide-to-text.mjs _site/2606_SPT_summer/index.html --flags-only   # text QA
```

The self-contained render embedded at the top of the managing constitution is
`slides.html` (copied into the fiber dir). Build it with
`quarto render 2606_SPT_summer/2606_SPT_summer.qmd --to revealjs -M embed-resources:true`
then copy `_site/2606_SPT_summer/index.html` to the fiber's `slides.html`
(**not** `--output slides.html`, which breaks reveal.js initialization — the
output lands unstyled); re-run the plain render afterwards so `_site` isn't
left with an embedded index. Deployment is Cail-gated: pushing the
`talks` repo to `main` triggers the Pages Action (see `../CLAUDE.md`); do not push
without Cail.

Figures live in the shared pool `../images/` (symlink). Source PNGs are copied from
the trusted dashboard set; record provenance in commits.
