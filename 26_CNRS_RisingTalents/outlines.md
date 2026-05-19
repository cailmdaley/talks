# CNRS AI Rising Talents — Interview Talk Outlines

Interview date: **Thursday, June 25, 2026, 10:00 CET**  
Format: 15-min general + 15-min deep-dive + ~13-min discussion  
Order: candidate's choice — recommend **general first, then deep-dive**

---

## Talk 1: General Presentation (15 min)

**Title:** *Cosmology with Agentic AI: Research Experience and a Four-Year Program*

**Arc:** trajectory → results → the AI inflection point → program → why France

**Pacing:** 8–10 content slides + title + summary = ~12 slides at 1–1.5 min each. This committee will be fast, but leave room for the "bitter lesson" slides — that's the conceptual heart.

### Slide-by-slide structure

**Slide 1 — Title**  
Cail Daley, CosmoStat / CEA Paris-Saclay. The program title. Affiliations (UNIONS, Euclid, SPT).

---

**Slide 2 — Research arc: from CMB to weak lensing**  
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
- IAS: Euclid CMB cross-correlations; Giulio Fabbian, Laura Salvati (both Euclid CMB working group leaders), Tony Bonnaire (generative AI for cosmology)
- Paris-Saclay ecosystem: DATAIA (DeMythif.AI, PostGenAI@Paris), Pleias collaboration (French Science Commons, sovereign AI)

---

**Slide 10 — Summary**  
*~30 sec*

Simple three-line close:
1. Strong track record: UNIONS Paper II, Euclid cross-correlations, SPT work
2. Clear program: UNIONS tomographic → multi-probe; Euclid-CMB DR1 → DR2; benchmarks
3. France is the right place: CosmoStat, IAS, DATAIA — the research ecosystem is here

---

## Talk 2: Deep-Dive Scientific Presentation (15 min)

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
- Number of source galaxies: [check paper]
- S8 value and uncertainty: [check paper]
- Agent capability doubling time: ~4 months (METR 2026)
- 2025 task horizon: ~12 hours of expert time
- Lines of code in UNIONS analysis: ~10,000 lines code, 120,000+ lines edited
- PhD students proposed: 2 (Year 1), 1 postdoc (Year 2)
- Program budget split: ~2/3 personnel, ~1/3 candidate position + compute + travel
