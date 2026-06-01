# SPT Secondaries and Cross-Correlations Call — June 1, 2026

Informal update for the SPT secondaries call. Same recurring call as the March 30 deck
(`2603_CMBX_Update`), same audience: SPT collaboration members (Abhi Maniyar / y-maps,
Aaron Ouellette / DES×SPT, the broader secondaries group). They know SPT and know Agora; they
may not know Euclid internals.

**Division of labour:** Louis Legrand gives the 15–20 min CMBX KP overview. Cail follows with a
*few* slides. The Euclid DR1 timeline is mentioned aloud by Louis, not slided.

**Framing (revised).** Don't lead with "here is Agora" — everyone on this call already knows Agora.
Lead with the *question we're actually working on*: **what is our simulation landscape?** Building
Euclid × CMB-lensing cross-correlations, there's a range of mocks we could draw on — each isolating
a different piece (a correlated signal mock; foregrounds; systematics; a realistic noise covariance).
Agora is one entry in that landscape, not the headline.

Full grounding + the simulation-landscape facts live in the constitution fiber
`talks/spt-secondaries-2606-slides` (`felt show talks/spt-secondaries-2606-slides --body`).

## Narrative

### Slide 1: Title
Euclid × SPT: the simulation landscape. Cail Daley, on behalf of the Euclid CMBX team.

### Slide 2: What have prior cross-correlation analyses used simulations for?
A survey of prior practice — the historical context, placed **first** (Cail's call). Two columns;
headline takeaway: **galaxy bias was never measured from sims**. On-slide citations: Omori et al. 2023
& Chang et al. 2023 (DES Y3 × SPT+Planck I/II, 2203.12439/440), Shaikh et al. 2024 (ACT-DR4 × DES
shear, 2309.04412), Xavier et al. 2016 (FLASK), Fosalba et al. 2015 (MICE).
- **Covariance** — correlated *signal* from cheap **lognormal (FLASK)** mocks (κ + δ_g + γ via theory
  Cℓ); **reconstruction noise** from each experiment's correlated sim suite (*noise only*); run the
  full estimator on the mocks to check recovered parameters are unbiased.
- **Bias characterization** — galaxy bias is a **free parameter** per bin, marginalized, *not*
  calibrated from sims; N-body sims (e.g. **MICE**) only **validate** the non-linear bias model and
  set **scale cuts**; magnification bias is **fixed** from external measurements.

### Slide 3: A landscape of mocks — each isolates a different piece
Posed as the mocks we *could draw on* (not a checklist of things we must get right), split into a
CMB/large-scale-side column and a Euclid-side column. Five rows:
- **Agora** → coherent multi-probe **foreground** sky (CMB-side N-body); Euclidise via the **GLASS**
  forward model — needs density shells + halo catalogs.
- **Flagship2** → *(ΛCDM N-body, no κ_CMB)* the official Euclid **galaxy + WL** mock; gold-standard
  galaxy realism, the **bias & n(z) reference**. Symmetric Euclid-side counterpart to Agora.
- **DEMNUni** → correlated **κ_CMB + galaxies + WL** across ΛCDM / massive-ν / f(R); SHAM galaxies
  with **FS2-calibrated bias & n(z)** → Margherita's 6×2pt **mock data vector** (the CMBX sim team:
  Calabrese, Carbone, Fabbian, Baldi). DEMNUni *has* κ_CMB — that's its point.
- **Contaminated GLASS** (Porredon & Souki) → inject Euclid systematics, watch the cross-spectrum.
- **Per-experiment recon suites** (Planck/ACT/SPT) → each experiment's **κ-reconstruction noise** for
  a realistic covariance (the response/normalization is already baked into the released κ map).

Two distinct jobs to land verbally: a correlated **signal** mock (DEMNUni) and realistic **noise** for
the covariance (the recon suites). **Agora & Flagship2** are the realistic CMB-side / Euclid-side
N-bodies (symmetric); **GLASS** is the one forward model that Euclidises any N-body. (Gower St
deliberately omitted — not official Euclid.)

### Slide 4: Euclid-like Agora — we just need the density + halo shells
Marco Gatti and I have been talking about building **Euclid-like WL + GC** from Agora, on NERSC
(`m5099`), via the **same GLASS forward model** that Euclidises any N-body. The mechanics are simple:
we just need Agora's **density shells + halo catalogs** to generate the Euclid samples. **The open
question: do those already exist on NERSC?** (They're the low-level products on Yuuki Omori's Globus
endpoint — the ask is to get them onto `m5099`.) This is the worked example of slide 3's mechanism.

Hero visual: `agora_maps.png` (the multi-component sky), introduced briefly, not laboured.

### Slide 5: Our covariance recipe — and the open SPT question
**Consistent with Louis' KP2/3 update** (his slides 22–25, "Simulations and Covariance" — Luchina,
Calabrese, Haridasu, Carbone, Baccigalupi, Vielzeuf): covariance = **FLASK** lognormal realizations
**calibrated on the 50 DEMNUni-Cov N-body sims**, generating correctly-correlated *g, γ, κ, y* fields
(incl. constrained ISW-RS), with noise generation + lensing QE on CMB masks. So **DEMNUni does double
duty**: the 6×2pt mock data vector *and* the lognormal calibration — the same lognormal-from-N-body
recipe as prior work, now Euclid-specific. **Don't pose "DEMNUni vs FLASK"** — 50 N-body sims can't be
a direct covariance (Hartlap), they *calibrate the lognormal shape* (mean + shift); FLASK supplies the
many draws. **The open question (our SPT-side value-add):** the **SPT × ACT** cross-covariance when
both enter one data vector (shared signal, independent reconstruction noise) — mining **Qu et al's**
joint ACT+SPT+Planck combination. Louis flags SPT/ACT/Planck consistency + super-sample covariance as
ongoing (his p14) but *not* SPT×ACT cross-cov specifically. Seed of [[covariance-response-lit-synthesis]].

NB the dropped claim: the earlier "SPT response ~uniform vs ACT position-dependent" line is **not**
substantiated in the literature we have — left off the slide on purpose.

## Slide headlines (narrative thread)
1. — (title) Euclid × SPT: the simulation landscape
2. What have prior cross-correlation analyses used simulations for? (covariance | bias) — w/ citations
3. A landscape of mocks — each isolates a different piece
4. Euclid-like Agora — we just need the density + halo shells (do they exist on NERSC?)
5. Our covariance recipe (FLASK calibrated on 50 DEMNUni-Cov sims) — and the open SPT × ACT question
