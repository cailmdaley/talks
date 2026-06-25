# CNRS AI Rising Talents — Interview Talk Outlines

Interview date: **Thursday, June 25, 2026, 10:00 CET**
Format (per the official invitation): **two 15-min talks + ~13-min discussion** — a *general* talk
(research experience + four-year program) and an *in-depth scientific* talk (one contribution),
candidate's choice of order. Both ship as **one combined deck** (`26_CNRS_RT_interview.qmd`) with an
**intermission** between them. (An earlier pass misread a mock-day "feels like one slot" aside as
collapsing the two into a single ~13-slide talk — that was wrong; the science deep-dive is required.)
The combined LIVE deck is below. The standalone two-talk outlines further down are the **rehearsal-era
quarry** the science talk was rebuilt from — kept as source / fallback, not the deliverable.

---

## Combined two-talk deck (LIVE) — `26_CNRS_RT_interview.qmd`

Audience: a **non-astrophysicist AI/ML panel** (ENS / DI). Built against the mock-jury feedback (see
`[[ai-futures/application/interview/slides/mock-feedback]]` and the feedback-incorporation fiber's
`report.html` ledger). ~28 slides incl. title, ~30 min of content + discussion.

### Part I — general / program (15 content slides, ~15 min, ~1 min each unless noted)

The AI research program is the centre of gravity; cosmology is the proving ground.

1. **Pitch** *(~45s)* — A new way of doing science: agents execute, I supply the judgment; I'll
   build it into a program here and prove it on the universe. Roadmap line: why it's needed · what
   I'd build · why me. *(Lead with the proposal — audible in the first minute.)*
2. **Stakes** *(~1m)* — We still cannot explain 95% of the universe; we don't even know its age to
   better than a billion years. Plain language, no ΛCDM.
3. **Crisis** *(~1m)* — Answering these questions is bottlenecked on human labor: 60M galaxy shapes,
   a 1% signal, ~5-year analyses, hundreds of people. The limit is people and the years they cost.
4. **METR** *(~1m)* — AI can now do longer and longer expert work; the frontier doubles every few
   months. Why it continues: scaling laws, test-time compute, synthetic data.
5. **Judgment** *(~1m, the hinge)* — As agents do more, the bottleneck moves from *doing* to
   *knowing whether it's right* — judgment, the skill agents still lack.
6. **Why cosmology** *(~50s)* — The ideal proving ground: one universe, no answer key, so every step
   is a judgment call (signal or artifact?). The differentiator vs other 5-year fields.
7. **Proof** *(~1m)* — An entire analysis for a major sky survey, produced almost entirely by agents
   I direct; a team an order of magnitude smaller, doing dozens of people-years of work. My job was
   the judgment: designing the analysis and the checks. *(FTE framing, not lines-of-code.)*
8. **Science** *(~1.5m, the one plot)* — The surveys' disagreement on how clumpy the universe is
   wasn't new physics — it was each instrument's own artifacts; once removed, they line up. Telling
   signal from artifact is the judgment the program is built to scale. *(Plot lay-relabelled — jargon
   stripped, prediction-band anchored, earlier-low/latest-up draws the convergence, ours wide-on-purpose.
   Remaining taste-call: keep in Part I vs migrate — see the ledger.)*
9. **Program** *(~1m)* — Three pieces that build on each other: **memory → measurement → diffusion**.
   Cosmology — this survey now, Europe's flagship Euclid next — is where each is built and tested.
10. **Step one — Memory** *(~1.5m)* — `felt`: a shared, verifiable record + a scheduler that
    dispatches agents against open questions. Spend real time here.
11. **Step two — Benchmark** *(~1m)* — Benchmark the practice on real scientific work: scored not on
    the answer but on sound reasoning + a defensible record. Scoring without an answer key is an open
    problem in evaluating agents — and real science is exactly where it must be solved.
12. **Step two, continued — training signal** *(~1m)* — Those same benchmarks double as training
    environments; with Pleias / DATAIA, a sovereign signal France can own.
13. **Step three — Diffusion** *(~1m)* — Teach judgment, not prompting: form an expectation, test it,
    learn from the gap. How to teach it is an open question for the Paris-Saclay teaching centers.
14. **Mentoring + sovereignty** *(~1m)* — Students came in skeptical; AI changed how I *support* them,
    and we go deeper together. Sovereignty is trained people, not only sovereign models.
15. **Close** *(~1m)* — Why here, why me, why now: judgment is my native skill as a cosmologist, shown
    at scale; the ecosystem is here; France can lead trustworthy science with AI.

### Intermission

Divider slide ("Part Two — the science, up close"). Bridges from the program into the demonstration:
the whole program rests on one skill — telling a real signal from an instrument's fingerprint.

### Part II — in-depth science (11 content slides, ~15 min)

The UNIONS B-mode systematics work, told ENTIRELY in plain language for a zero-cosmology panel.
"Be pure, not complete." The through-line is the *judgment skill* in action; no program re-pitch,
one light agentic clause at the close.

1. **Hook** *(~1m)* — Gravity bends light, so a clump of invisible matter stretches the shapes of the
   galaxies behind it by ~1%. *(Lensing animation.)*
2. **Averaging → a map** *(~1m)* — Any one galaxy is already random, so a 1% nudge is invisible; but
   the nudge is *shared*, so averaged over millions the random shapes cancel and the stretch becomes a map.
3. **Independent + small team** *(~1m)* — To trust agreement between teams, measurements must be
   genuinely independent; ours is the first deep northern-sky map, from a team of ~10. *(Team photo.)*
4. **The difficulty** *(~1m)* — The signal is a ~1% stretch; the instrument distorts shapes about as
   much; and there's no answer key to check against.
5. **Blinding** *(~1.5m)* — With no answer key, we hide our own result from ourselves — exactly
   holding out a test set — and only reveal it once every analysis choice is locked.
6. **Forbidden pattern** *(~1.5m)* — Gravity can make only one pattern; a swirl is physically
   impossible — so any swirl is the instrument talking. A built-in lie detector. *(E/B patterns.)*
7. **Three rulers** *(~1m)* — We look for the forbidden swirl three ways, each blind to different
   mistakes. The interesting question is what happens when they disagree.
8. **Disagreement = discovery** *(~2m, the one plot)* — The sharpest of the three measures caught a
   swirl the other two missed; that disagreement traced the fingerprint to one size — the spacing of
   the camera's sensors. *(cosebis plot.)*
9. **The check designs the analysis** *(~1.5m)* — The disagreement, not our preferences, chose which
   data to trust and which range to throw away — locked in before unblinding.
10. **Conservative result** *(~1.5m)* — We unblinded, agreed with the other teams, then widened our
    own error bars on purpose. Better honest and wide than confident and wrong.
11. **Close** *(~1.5m)* — A small team did a thorough job because agents did the running and I did the
    judging; the same discipline scales straight to the far larger surveys coming. *(One light agentic
    beat. Thank you.)*

---

## Talk 1: General Presentation (15 min)  *(rehearsal-era — fallback)*

**Title:** *Cosmology with Agentic AI: Research Experience and a Four-Year Program*

**Arc:** *the design-problem thesis* → trajectory → results → the AI inflection point → program → why France

**Pacing:** 8–10 content slides + title + summary = ~12 slides at 1–1.5 min each. This committee will be fast, but leave room for the "bitter lesson" slides — that's the conceptual heart.

> **Revision 2026-06-04 (Shuttle):** a thesis frame — *"Science is becoming a design problem"* — now opens Talk 1 (new framing slide between Title and Research arc), so each numbered slide below shifts +1. The thesis pays off explicitly at the AI-inflection beat (*"this is the design problem"*), the four-year-program beat (*"a research system that scales its own checking"*), the verification beat (*"this is the design"*), and the summary bookend. House theming (EB Garamond / cinnabar accent / warm **rag** ground) applied to both decks via `custom.scss`. Before/after and the ground taste-question live in the fiber's `report.html`.

### Slide-by-slide structure

**Slide 1 — Title**  
Cail Daley, CosmoStat / CEA Paris-Saclay. The program title. Affiliations (UNIONS, Euclid, SPT).

---

**Framing slide — Science is becoming a design problem** *(NEW, opens Talk 1)*  
*~40 sec*  
The organizing idea, stated and let to breathe: research is accelerating and increasingly AI-mediated; output is starting to outpace verification; the question shifts from *producing results* to *designing research systems that check themselves as fast as they discover.* This is the through-line for everything that follows. Keep researcher altitude — the verification apparatus is the wake of doing the science, not the product.

---

**Slide 2 (now 3) — Research arc: from CMB to weak lensing**  
*~1 min*  
Timeline graphic or two-column layout:

- Left (past): CMB lensing with SPT-3G — graduation work, lensing reconstruction, Euclid cross-correlations MOU
- Right (now): UNIONS weak lensing (UNIONS-3500), cosmic shear cosmology; kinematic lensing (student supervision, Hopp & Wittman 2026)

Key beat: I work across **three international collaborations** and I lead analyses, not just contribute.

---

**Slide 3 — UNIONS-3500: B-modes and the first northern-sky cosmic shear constraints**  
*~2 min* (the flagship result; give it time)

- What UNIONS is: wide-field MegaCam survey, ~3500 deg², first northern-sky weak lensing at this depth
- What Paper II (B-modes) did: three independent statistics (COSEBIs, ξ±B, Cℓ) as systematics diagnostics — gating the cosmology
- Key finding: statistics don't all agree, which is itself the insight — forces scale cuts, identifies contamination
- What Papers III–V produced: S8 constraints agreeing with Planck and Stage III at ~1σ

*Visual: the B-mode data vector panel; the S8 comparison plot (from Moriond backup slides)*

*Beat to land:* "This analysis — ~10,000 lines of code, three statistical frameworks, full manuscript — was produced almost entirely by AI agents under my direction."

---

**Slide 4 — Euclid × CMB cross-correlations**  
*~45 sec*

- I am one of the principal postdocs in Euclid's CMB cross-correlations science working group
- Lead the SPT–Euclid Memorandum of Understanding project
- Cross-correlations are robust: independent systematics between CMB lensing and galaxy lensing
- DR1 (October 2026): first science coming

*Can be one image: the cross-correlation science case visual, or Euclid+SPT logos with "independent systematics" label*

---

**Slide 5 — The AI inflection point**  
*~2 min* (conceptual heart — don't rush)

Sutton's bitter lesson: general computation > encoded expertise, every time. Applied to science:

- Frontier models complete tasks requiring ~12 hours of human expert time
- Capability doubling time: ~4 months (METR 2026 data)
- If this holds: ~2,500× more capable in 4 years

The implication isn't that experts become irrelevant. It's that **expert time is better spent guiding computation than doing it.**  
The researcher's role shifts: specification, design, verification — not implementation.

*Visual: the METR capability trajectory graph (if available), or a simple timeline showing doubling*

---

**Slide 6 — The existence proof: UNIONS Paper II**  
*~45 sec* (builds on slide 3 — can be brief here if slide 3 already planted the seed)

- ~10,000 lines of analysis code
- Full manuscript (Daley et al. 2026)
- 120,000+ lines edited by agents across the project
- My role: designing the analysis, designing the validation tests, verifying correctness

*This is the proof of concept. But also the point: I'm not describing a future method — I'm already working this way.*

---

**Slide 7 — The four-year research program**  
*~2 min*

Two scientific axes:

**UNIONS:** tomographic cosmic shear → multi-probe (cosmic shear + galaxy–galaxy lensing + clustering). 4-year arc: first tomographic constraints (Year 1) → multi-probe analysis (Year 3). Percent-level S8 constraints.

**Euclid × CMB:** DR1 cross-correlation science (Year 1–2) → comprehensive multi-probe cross-correlations with DR2 (Year 3–4).

Running through both: **agentic methods make the breadth tractable** — more systematic exploration, more validation checks, a complete decision record.

Bullet the timeline years compactly. Emphasize: "milestones defined by scientific deliverables, not tooling."

---

**Slide 8 — Verification and benchmarks**  
*~1 min*

The risk that must be named: agentic science without appropriate checks weakens the science it's meant to strengthen. AI systems hallucinate. They optimize for plausibility over correctness.

The tools already in development (as part of Lightcone Research with François Lanusse):
- `felt` — traversable decision and progress graph
- ASTRA specification — structured, machine-readable analysis records
- *Tapestries* — browsable provenance visualization

Benchmarks: real analysis tasks (messy, multiple defensible solutions) — not isolated extractions from published papers. Year 2 deliverable; growing suite.

---

**Slide 9 — Team, mentorship, lab integration**  
*~1.5 min*

**Team:** 2 PhD students (Year 1) + 1 postdoc (Year 2). Co-supervision with Martin Kilbinger (HDR) and Samuel Farrens (HDR) at UMR AIM; François Lanusse for AI methods.

**The mentorship question:** agentic pedagogy — how do you develop verification instincts in students who haven't learned without AI? Early experiments in progress (current M2 internship); this is itself a research contribution.

**Lab integration:**
- UMR AIM (CosmoStat): home for UNIONS analyses, Lightcone Research; Kilbinger, Farrens, Lanusse
- IAS: Euclid CMB cross-correlations; Giulio Fabbian, Laura Salvati (both Euclid CMB working group leaders)
- Paris-Saclay ecosystem: DATAIA (DeMythif.AI, PostGenAI@Paris), Pleias collaboration (French Science Commons, sovereign AI)

---

**Slide 10 — Summary**  
*~30 sec*

Simple three-line close:
1. Strong track record: UNIONS Paper II, Euclid cross-correlations, SPT work
2. Clear program: UNIONS tomographic → multi-probe; Euclid-CMB DR1 → DR2; benchmarks
3. France is the right place: CosmoStat, IAS, DATAIA — the research ecosystem is here

---

## Talk 2: Deep-Dive Scientific Presentation (15 min)  *(rehearsal-era — fallback)*

**Title:** *B-mode systematics in the UNIONS-3500 weak lensing survey*  
(Alternative title framing: *When null tests disagree: systematics characterization for UNIONS weak lensing*)

**This is Paper II / the B-modes analysis.** Reasons to prefer this over kinematic lensing:
- Published / presented result; you can own it completely
- Showcases multiple statistical frameworks working in concert — strong methodological depth
- The "B-modes don't agree" finding is genuinely interesting, not just a pass/fail
- Directly connects to the agentic AI story (this paper was agent-written)
- You presented at Moriond in March — Moriond slides are a natural base to trim from

**Arc:** what cosmic shear is → UNIONS → why B-modes → three statistics → the disagreement and what it reveals → cosmology impact

### Slide-by-slide structure

**Slide 1 — Title**  
Paper II: "Characterizing systematics in UNIONS-3500 with B-mode estimators."

---

**Slide 2 — Cosmic shear: what we measure and why B-modes matter**  
*~2 min*

Gravitational lensing distorts galaxy shapes. We measure the shear field correlation function. The shear field decomposes into:
- **E-modes** (curl-free): the cosmological lensing signal
- **B-modes** (divergence-free): should be zero from lensing alone; non-zero B-modes diagnose residual systematics

This is the key diagnostic insight: any B-mode signal is a flag. What kind of systematics?
- PSF leakage (instrumental)
- Additive shear bias at detector scale
- Multiplicative shape calibration errors

*Visual: the E/B decomposition diagram (standard shear community figure); the UNIONS footprint*

---

**Slide 3 — UNIONS-3500**  
*~1 min*

- MegaCam on CFHT, ~3500 deg², r-band lensing
- Why UNIONS? Deepest wide-field northern-sky weak lensing survey; gap-filler between KiDS and LSST
- Small core analysis team (order of magnitude smaller than DES/KiDS) — coordination overhead is low, demands on research throughput are high
- The shear catalog: selection and calibration
- Paper II is the gatekeeper: decides which catalog version and which scales are clean enough for cosmology

---

**Slide 4 — Three statistics, one systematics test**  
*~2 min*

We don't use one B-mode test — we use three, in different statistical bases:

1. **ξ±B (configuration space)**: pure E/B decomposition of the two-point correlation function; direct but computationally intensive
2. **COSEBIs (Complete Orthogonal Sets of E/B-separating Integrals)**: discrete modes optimized to compress cosmological information; designed to be maximally sensitive to B-modes
3. **CℓBB (harmonic space)**: power spectrum in Fourier space; different scale weighting than real-space statistics

Each weights angular scales differently. Requiring all three to pass is more conservative and more diagnostic than a single test.

*Visual: The pure E/B data vector panel (images/pure_eb_data_vector.png from Moriond)*

---

**Slide 5 — Not all statistics agree**  
*~2 min* (the key finding)

Over the full angular range (1–250 arcmin, ℓ ≲ 2000):
- ξ±B: **passes**
- CℓBB: **passes**
- COSEBIs: **fails**

*Visual: cosebis_bsigma_talk.png — the oscillating B-mode signal in COSEBIs*

This is not a matter of real-space vs. harmonic-space. We compute COSEBIs from both ξ± and from the Cl bandpowers — they agree with each other, and both fail. The Cl themselves pass. **The sensitivity is set by the filter functions, not the basis.** COSEBIs' filter functions concentrate sensitivity on specific scales where there is contamination.

The oscillating pattern in COSEBIs is consistent with additive shear bias repeating at the CCD scale (Asgari et al. 2019). We cannot decisively identify the origin — this is an honest finding.

---

**Slide 6 — Using disagreement to inform the analysis**  
*~1.5 min*

The disagreement is the information. We use B-mode tests to:
1. **Select the catalog version**: only the PSF size-corrected catalog passes across all statistics and scale cuts
2. **Set angular scale cuts**: COSEBIs, which fail on the full range, pass after imposing θ ≥ 3.5 arcmin (ξ+), θ ≥ 40 arcmin (ξ-). These become the analysis scale cuts for Papers IV and V.
3. **Freeze all choices before unblinding**: catalog version, scale cuts, and robustness criteria are locked before the cosmology is revealed

*Visual: the scale cut diagram or the catalog comparison figure*

This is what rigorous null testing buys: not just "passed" or "failed," but **calibrated confidence in your choices.**

---

**Slide 7 — Cosmological constraints**  
*~1.5 min*

With the validated catalog and frozen scale cuts:

Papers IV (real space) and V (harmonic space) find:

- S8 = ... (value, with error)
- Agreement between two independent analyses to ~2σ (calibrated on 350 GLASS mocks)
- Agreement with Planck and Stage III surveys at ~1σ

*Visual: the S8 comparison plot (from the "Thank you" backup in Moriond, or the main S8 comparison)*

The IA prior is the dominant systematic: S8 is robust to analysis choices but sensitive to the intrinsic alignment model. This is an honest accounting — we marginalize conservatively.

---

**Slide 8 — Produced with agentic AI**  
*~1 min*

Brief: this analysis was conducted in agentic mode. ~10,000 lines of code, three independent statistical frameworks, full manuscript — under my direction, by Claude Code.

What that enables:
- Exploratory breadth that would be impractical with hand-coding (running all three statistics, testing multiple catalog versions, computing sensitivity across all scales)
- Every decision recorded in a structured provenance graph (felt + ASTRA)
- The verification question becomes: not "is the code right" but "are the decisions right" — which is where the astronomer's expertise actually belongs

Not a methodological detour — this is how frontier cosmological analysis will be done in 5 years.

---

**Slide 9 — Summary and forward**  
*~1 min*

- UNIONS-3500 delivers the first northern-sky cosmic shear constraints
- B-mode analysis reveals real contamination at specific scales; systematic use of multiple statistics turns disagreement into diagnosis
- Validated S8 constraints agree with the concordance model at ~1σ
- Next: tomographic cosmic shear (Year 1), then multi-probe (Year 3)
- The B-mode framework generalizes: it becomes the template for future UNIONS analyses as depth increases

---

## Notes on preparation

### Order recommendation
Do **Talk 1 first** (general), then **Talk 2** (deep-dive). The committee enters the science talk with the program context; the arc from "what I've done" to "what I've found" reads naturally.

### Harvesting existing slides
- Moriond talk (`26_Moriond_UNIONS/`) is the strongest base for Talk 2. Core slides to adapt: the pure_eb_data_vector panel, cosebis_bsigma_talk, scale cut figure, S8 comparison. Trim the cosmology setup (3 slides → 1) and the "thank you" recovery slides.
- DApPostdocSeminar (`25_DApPostdocSeminar/`) has the cosmology / ΛCDM context slides for Talk 1 if needed; the SPT/lensing overview is reusable.
- The general presentation will need new slides for the AI story (the METR curve, the bitter lesson framing). These don't exist in the current talk library.

### Lab name correction
The fiber body says "IAS or LISN" — the research programme and application say **UMR AIM** (CosmoStat, CEA) and **IAS**. LISN doesn't appear in the application. Update the fiber body.

### Key numbers to have ready for discussion
- UNIONS area: ~3500 deg²
- Number of source galaxies: **~61 million** (fiducial catalog v1.4.6.3), n_eff ≈ 5 arcmin⁻²
- S8 values (from companion papers III/IV, Papers III + IV in series): **config-space S8 = 0.86 ± 0.08**, **harmonic-space S8 = 0.92 ± 0.08** — both ~1σ consistent with Planck (S8 = 0.834 ± 0.016); config-harmonic agreement ~0.5σ. (Note: the harmonic abstract was later corrected to 0.891 after n(z) calibration fix; the rounded CNRS application values 0.86/0.92 are the right reference for the jury.)
- Agent capability doubling time: ~4 months (METR 2026)
- 2025 task horizon: ~12 hours of expert time (METR 2026 benchmark)
- Lines of code in UNIONS analysis: ~10,000 lines code, 120,000+ lines edited
- PhD students proposed: 2 (Year 1), 1 postdoc (Year 2)
- Program budget split: ~2/3 personnel, ~1/3 candidate position + compute + travel
