# CNRS Rising Talents — talk narrative

Build-facing narrative for the two CNRS AI Rising Talents interview decks. The full strategic
record (with the reasoning behind every choice) lives in the felt fiber
`ai-futures/application/interview/slides/bitter-lesson-frame` — read it for depth; this file is
what you build slides against.

**Interview:** Thursday 25 June 2026, on Zoom. Per the official invitation it's **two 15-min talks
+ ~13 min Q&A** — a *general* talk (research experience + four-year program) and an *in-depth
scientific* talk (one major contribution), candidate's choice of order. Both ship as **one combined
deck** (`26_CNRS_RT_interview.qmd`) with an **intermission slide** between them, ~30 slides. (An
earlier pass misread a mock-day "feels like one slot" aside as overriding the written invitation and
collapsed both into a single ~13-slide talk — that was wrong; the science deep-dive is a required
talk.) A mock jury ran 2026-06-09; its verdict is the current revision driver — see
[[ai-futures/application/interview/slides/mock-feedback]]. A follow-up rehearsal is planned the week
prior.

---

## The audience, and the job

The jury is **traditional ML researchers**, and they are tired of people "doing AI" by prompting.
The whole job is to read as a researcher with **original ideas and a real research plan** — a
competent, independent **adult** — not a cosmologist who discovered Claude. Filter on every slide:
*does this show me thinking about the practice, or just using it?*

**Sharpened by the 2026-06-09 mock** (read [[ai-futures/application/interview/slides/mock-feedback]]
for the full per-slide notes): the real panel is **ENS / DI — not astrophysicists**. Assume *zero*
cosmology knowledge and strip all jargon (LSS, weak lensing, UNIONS/SPT/Euclid, "collaboration,"
systematics, σ-tensions, COSEBIs, E/B-modes, PSF, CCD, S₈, tomographic…). **"Be pure, not
complete"** — explain the few things you show; cut the rest. It's an **AI position**: center the
talk on the **AI research program you're building**, cosmology as the proving ground — not a
cosmology talk with AI on top. **Lead with the pitch**, build the intro to a *crisis* (survey
science is bottlenecked on human labor / FTE; answering the big questions needs ever-larger
collaborations), then propose a **concrete, stepped plan** (memory systems → benchmark → diffusion),
not commentary on the problem. Make cosmology *matter* and explain why it's special (no ground
truth → needs taste → ideal testbed for agentic science). Swap raw lines-of-code for the
**FTE-equivalent**. Above all, **sell yourself** — clear, confident, fewer "um"s.

## The one thing to emphasize: dual modality (the loop)

Cosmology and the meta-practice of AI-research-itself are **not two interests** competing for time.
They are **one loop**, and the talk must make the loop *visible* rather than partitioning into
"first the cosmologist, then the AI stuff":

- **AI-first is the best way to do the cosmology**, and
- **doing real cosmology (a domain you're expert in) is the best way to learn the new practice** —
  because the practice is **general** (it belongs to all of research), not a machine-learning
  artifact, and it only reveals itself *through* domain research.

So cosmology is not the credibility ticket — it is the **laboratory**. Interleave the two
modalities; the mutual feeding *is* the thesis.

## The architecture — one argument, four levels

```
MACRO   — the Bitter Lesson (Sutton): invest in what compounds (practice, people, diffusion;
          tools only if they scale with use). Don't freeze human knowledge in tools.
MICRO   — the human skill that remains: judgment under expectation
          (taste / verification / telling systematics from signal). Not typing, not prompting.
DOMAIN  — cosmology: the ideal laboratory AND training ground — maximally judgment-dense
          (5-yr analyses, hundreds of decisions, signal vs systematic).
PROGRAM — hire + community + pedagogical partnerships to diffuse both the practice and the
          skill. Sovereignty = trained people, not only sovereign models. France leads.
```

The judgment skill (MICRO) is the centre, and it is **Cail's own** skill: telling systematics from
signal *is* taste *is* verification. His cosmology identity is the proof he already has the scarce
human skill the AI-first practice runs on.

## Voice — measure, not earnestness

**Register: measure, carefulness, professionalism.** Not earnest, not effusive, not hype. For a
jury wary of AI-evangelism, restraint *is* credibility. Statement-headlines that are calm and
exact, not breathless; claims hedged where honest ("in my biased view", "an open question"); the
AI material delivered matter-of-factly, as method, never as spectacle. The stakes here are very
large — which is exactly why the talk *underplays*: when the magnitude is this big, understatement
carries the weight. Never dramatize it on a slide.

## Hard rules

- **No topic-label headlines.** Every `##` is a complete-sentence "so what." The headline sequence
  must read as a narrative on its own.
- **Voice: researcher, not builder.** "led, produced, develop, contribute, characterise, design" —
  never "I built / I founded." Lightcone is *the open ecosystem I contribute to*, never "the
  startup I co-founded." **Never mention Lightcone's funding** (private).
- **Tools named: only `felt`**, as part of Lightcone, and only as *evidence the principle works*
  (it scales with use; building is a mode of experiment) — never as a "tools I built" slide.
  **Never mention Vellum.** (ASTRA dropped from the Lightcone slide 2026-06-09 per Cail — don't
  reintroduce it.)
- **The slide words are not precious — rewrite freely** — except the ΛCDM **"A successful but
  unsatisfying model"** slide, which Cail crafted; preserve its content.
- **But dictated copy is verbatim.** When Cail dictates actual slide text (not direction), use his
  exact wording — don't paraphrase, reorder, soften, or "improve" it. This is distinct from the
  freedom to rewrite *your own* drafts above; paraphrasing his dictation is a real error.
- Statement headlines, one message per slide, ~1 slide/minute, figures earn their place.

---

## Talk 1 — General (background + proposal). ~15 slides incl. title.

The proposal talk: who Cail is, and the four-year program. Carries the full agentic/meta thesis.
Talk 1 owns the program and the agentic argument; Talk 2 leans on them and stays science.

**Arc (per-slide intent):**

**DOMAIN — establish the cosmologist**
1. **(title)** — Cosmology with Agentic AI: research experience + a four-year program.
2. **I'm an observational cosmologist — close to the data, across collaborations.** *(NEW.)*
   Brief identity + trajectory + one headline credential ("some of the tightest constraints in the
   field, from SPT-3G"). Source from `../../ai-futures/cnrs-5pp/dossier.pdf` /
   `dossier-digest.md`. Keep distinct from slide 5 (this = identity; 5 = current breadth).
3. **A successful but unsatisfying model.** *(KEEP — Cail-crafted, preserve.)* ΛCDM, 95%
   phenomenological.
4. **Progress means telling systematics from signal.** *(KEEP.)* The judgment seed — pays off at
   slide 10.
5. **I lead analyses across three collaborations.** *(KEEP.)* SPT-3G / UNIONS / Euclid; controlling
   systematics across probes. Identity-forward ("I lead analyses in each"), not an abstract
   systematics-throughline.

**HINGE — domain into meta** *(transition wants polish)*
   Bridge device: systematics is where cosmology gets **hard, tedious, and quietly thankless** —
   doing it honestly means *loosening naively-tight constraints*, which the field under-rewards.
   That is exactly the work the new way of doing research transforms. (Career-incentive framing is
   *spoken*, never printed.)
6. **AI capabilities are doubling every few months.** *(KEEP — METR.)*
7. **As output outpaces verification, research becomes a design problem.** *(KEEP — the thesis.)*

**MACRO + the loop, proven**
8. **The Bitter Lesson: practice compounds, tools don't.** *(NEW.)* Sutton's own words; don't
   freeze knowledge; bet on what scales with compute/use. *(Candidate merge with 9 if 8→9 drags —
   see fiber.)*
9. **AI-first does better cosmology — and the cosmology is how I learn the practice.** *(REFRAME of
   the existence proof.)* The loop stated both ways; UNIONS Paper II (agent-produced, real result)
   is the proof; felt/ASTRA appear as tools that scale with use.

**MICRO**
10. **The skill that remains is judgment.** *(NEW.)* Anthropic "for now it's about taste" →
    cosmology is where taste matters most (5-yr analyses, hundreds of decisions) → closes back onto
    slide 4. Verify, don't type. *(Before the program — settled.)*

**PROGRAM**
11. **A four-year program on two axes.** *(KEEP.)* Program language from
    `../../ai-futures/cnrs-5pp/sections/research-programme.tex`.
12. **Benchmarks become certification.** *(REFRAME.)* You always reassess benchmarks — it's how you
    know how much better things are getting, otherwise you're unmoored. Open-ended benchmarks that
    characterise *real scientific work* → synthetic data / RL environments (what powers frontier
    progress) → a **sovereign training-signal** story. Pleias sovereign-vs-frontier sits here.
13. **Teaching judgment, not prompting.** *(NEW.)* The honest mentoring beat — students were
    AI-skeptical, Cail didn't force it; AI changed how he *supports* (reproduce / check / unblock),
    their work seeds the depth; learning is the open question (verify-not-type, scaffold by cheap
    experiment, the constraint is now curiosity + perseverance, not labour); partner with
    pedagogical centres.
14. **Sovereignty is trained people, not only sovereign models.** *(REFRAME.)* People / practice /
    diffusion; team + lab integration fold in here as evidence the ecosystem is in place. (Mind CNRS
    model-ban decorum — frame as sovereign *people/practice*.)

**CLOSE**
15. **France is where this program belongs.** *(KEEP — Cail to rename.)*

---

## Talk 2 — Deep-dive (UNIONS B-mode science). ~10–11 slides.

"Look at the cool science UNIONS is doing," focused on Cail's own work — exciting, competent,
fast-moving. **No program pitch; end on the scientific future.** Talk 2 carries *no* program /
agentic re-pitch (Talk 1 owns it); at most one light agentic clause at the very close.

Current arc reads well and is largely settled: what weak lensing is → UNIONS northern map → the E/B
fingerprint (shear is curl-free → E-modes signal, B-modes flag systematics) → catalog must be clean
→ three E/B-separable statistics → the disagreement is information (CCD-scale additive bias) →
disagreement sets catalog + scale cuts → S₈ conservative by design → iterate toward the multi-probe
gold standard.

**The deliberate cross-deck rhyme (keep):** S₈ *opens* Talk 1 as the cautionary tale (looked like
physics, was systematics — "where my work lives") and *closes* Talk 2 (the team widened error bars
on purpose to avoid being the next one). This is the matched-pair signature — don't break it.

Talk-2 accuracy is grounded in the paper source at
`ai-futures/application/interview/slides/bmode-paper/` (Daley et al. 2026, UNIONS-3500 WL II).
