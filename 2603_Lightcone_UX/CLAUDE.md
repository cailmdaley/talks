# Lightcone UX Hack — March 31, 2026

Informal presentation for the Lightcone Research team. Audience: the lightcone developers who built ASTRA, Prism, Tessera. They know their own tools; they don't know felt or the tapestry. Goal: share a concrete UX proposal for how ASTRA decisions and research evidence present together, grounded in what I've built and what the literature says works.

## Narrative

### Act 1: What I have (slides 1–4)

**Slide 1: Title.** Tapestry × ASTRA: visualizing research decisions.

**Slide 2: I have a running analysis with decisions tracked in ASTRA and evidence tracked in felt.**
Quick context: kinematic lensing project, ASTRA spec with 7 decisions, snakemake backend that generates scatter-gather rules from the spec, felt fibers carrying the evidence and reasoning. The question: how do these present together?

**Slide 3: The tapestry is a knowledge graph of research fibers.**
Screenshot or description of the current tapestry viewer — 19 evidence nodes, force-directed layout, fog/reveal mechanic. Each node is a piece of evidence (plots, metrics, judgment). But right now it doesn't know about ASTRA decisions.

**Slide 4: ASTRA decisions are the formal choices; fibers are the reasoning behind them.**
The mapping: decisions define what was chosen and what was excluded. Fibers carry why — the investigation, the evidence, the judgment. These are complementary, not competing.

### Act 2: The design proposal (slides 5–9)

**Slide 5: Don't restructure the data — restructure the view.**
Core insight: fibers stay organic. Tags (`evidence:decision_id`) wire them to ASTRA decisions. The tapestry dashboard assembles progressive-disclosure views from fibers + ASTRA spec + execution state. Three data sources, one view.

**Slide 6: The spine follows the structure of a scientific paper.**
Horizontal axis = paper sections (Intro → Data/Methods → Results → Conclusions), which align with sub-analyses. Vertical axis = investigation depth. More investigation makes it taller, not wider. The spine is fixed; branches expand below.

**Slide 7: Progressive disclosure in three levels.**
L0 Spine: sub-analysis verdict + worst-status badge. L1 Decisions: declarative title from fiber outcome + evidence count. L2 Evidence: full fiber with plots. Two clicks max. Fiber outcomes ARE the declarative titles — no extra writing.

**Slide 8: The default view is the delta.**
Returning researcher pattern: what changed since last session? New/changed nodes start revealed; everything else starts fogged. The existing fog mechanic already supports this — the change is making initial visibility data-driven by recency.

**Slide 9: Four epistemic states, encoded with shape over color.**
✓ resolved, ○ open, ? suspicious, ✕ blocked. Pipeline health ≠ scientific judgment. A mock can be generated (pipeline ✓) but suspicious (science ?). Separate channels.

### Act 3: Why this works (slides 10–12)

**Slide 10: Shneiderman's mantra — overview first, zoom and filter, details on demand.**
The three-level disclosure maps directly: spine = overview, decisions = zoom, evidence = details. URL-encoded state so views are bookmarkable. Collapsed branches show count + worst status, never blank.

**Slide 11: Minto's Pyramid Principle — conclusions first, evidence underneath.**
Verdict-first at every level. "Linear scaling exact (ratio=2.0)" not "Noise model results." The headline sequence reads as a coherent argument. This is what makes it a briefing, not a dashboard.

**Slide 12: The research meeting metaphor.**
The tapestry isn't a dashboard — it's a briefing. Lead with science not pipeline. Default to delta. Group by question not pipeline step. An agent could generate the BLUF entry: "Since last session: 10 mocks generated. sigma_floor still unresolved."

### Close (slide 13)

**Slide 13: Implementation path.**
Phase 1: tag existing fibers with evidence:decision_id. Phase 2: spine layout in portolan. Phase 3: delta view. Phase 4: decision drill-in with ASTRA metadata. Build on Tessera components where possible.

## Slide headlines

1. —
2. A running analysis with ASTRA decisions and felt evidence
3. The tapestry is a knowledge graph of research fibers
4. ASTRA decisions are formal; fibers are the reasoning behind them
5. Don't restructure the data — restructure the view
6. The spine follows the structure of a scientific paper
7. Progressive disclosure: three levels, two clicks
8. The default view is the delta
9. Four epistemic states, shape over color
10. Overview first, zoom and filter, details on demand
11. Conclusions first, evidence underneath
12. The tapestry is a briefing, not a dashboard
13. Implementation: tags → spine → delta → drill-in
