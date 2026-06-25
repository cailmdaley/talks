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

**Working on this deck: activate the `slides` skill first, every time.** It carries the cognitive
model (two modalities — script in the notes, visuals on the slide; compression vs. transcription),
the build patterns (column layouts, figures on a colored ground), and the QA loop. Don't edit the
QMD without it.

**The live preview is the QA surface — keep it running, check it at the start.** A `quarto preview`
of the interview deck should always be live at
**`http://localhost:4321/26_CNRS_RisingTalents/26_CNRS_RT_interview.html`**. Cail keeps it open in a
browser, so it live-reloads as you edit — **he watches changes land there; don't send him
screenshots.** First thing each session, confirm it's up
(`curl -s -o /dev/null -w "%{http_code}" http://localhost:4321/26_CNRS_RisingTalents/26_CNRS_RT_interview.html`);
if it isn't (`000`/`404`), start it in the background:
`cd 26_CNRS_RisingTalents && quarto preview 26_CNRS_RT_interview.qmd --to revealjs --no-browser --port 4321 --host localhost`.
For your *own* visual QA, screenshot a single slide headlessly by its hash —
`…/26_CNRS_RT_interview.html#/<slide-id>` (reveal.js `hash: true` is on) — driving a headless
browser against the **http** preview, never `file://` (the figure-treatment blend needs http to read
pixels). Read the screenshot yourself; only surface a file to Cail when the rendered artifact *is*
the thing he asked to see.

**Two modalities: the script lives in the speaker notes; the slide is visual.** This is the working
rule for the deck (see the `slides` skill's Core Model for the why). For each slide, the
**speaker notes hold the prose Cail will actually say** — verbatim or close. That is where the
message gets litigated and rehearsed, and it's the source of truth for *content*. The **slide body
is a different modality**: graphics, images, labelled structure, numbers — what speech can't carry.
The slide must not transcribe the script back as sentences; complete-sentence *headlines* and short
labels are the only prose it earns. **The script is Cail's voice — treat the notes like dictated
copy.** You may change visuals freely, and sometimes both surfaces change together; but never let
*what's said* drift as a side effect of a layout edit. If reshaping a slide genuinely implies the
message should shift, **flag it and change the script with Cail** — don't silently substitute your
phrasing. That is the exact failure to avoid: "we tweaked the slide and now the words aren't mine."
The two sovereignty slides (`sovereignty-stakes`, `sovereignty`) and the choice/closed-science pair
are the worked examples.

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

## Sovereignty — the thesis, and how much of it to show

The opening now builds to **sovereignty** as its stakes, so the argument has to be exact. It has
two halves and **both matter** — this is *not* a "models don't matter, only know-how does" position:

- **Sovereign models** — capable, and (as the shutoff proved) able to be switched off.
- **Savoir-faire** — the skill to wield them and think *with* them. The scarce half, and the only
  half a researcher and CNRS can actually move.

The model gap is real and **widening**, and the mechanism is the exponential — the same curve METR
shows. On an exponential, a *constant* relative position is an *exploding* absolute gap: both the US
and Europe grow compute ~15× by 2031, the ratio barely moves (~12:1 at either end), and the outcome
is still bleak because 12× of a huge number is a chasm. Capability is the same story — Chinese labs
run ~6 months behind the US frontier, Mistral ~18 months, and 18 months *on a doubling curve* is
several doublings of absolute distance, not a near-miss. And the gap-closers — open weights, free
access — are exactly what stops being shared once frontier capability becomes a strategic asset: the
US ordering the model off for foreign nationals (the Le Monde story) is the first instance; a
Chinese frontier model would plausibly behave the same — kept internal to harden their own systems
before any release. Access is structurally fragile for everyone outside the lab that trains the model.

**Cail's view changed on this evidence — and the change is an asset.** The dossier, written months
earlier, treated sovereignty as overblown ("just use the best models"). That did not survive the
week the best model was switched off. Said plainly, the conversion sells him as someone who updates
on evidence (driver #5), and it lets sovereignty land through his own change of mind rather than as
borrowed alarm.

**Register and scope — the root system, not the canopy.** The full geopolitics (China timing; the
Moonshot — a $500B sovereign-model coalition; Europe 2031) is the *conviction behind the measured
line* and the Q&A backbone. It is **not** the on-slide beat. State sovereignty in one or two
measured slides and **turn back to the program** — which contributes the *savoir-faire* half
(trained people, one field at a time): both the decorum-safe framing (mind the CNRS model-race line)
and the half Cail can actually move. The stakes are huge, so the slide underplays; magnitude carries
itself. The cleanest landing pays the exponential off from the METR curve already on screen ("the
same curve that makes these tools powerful makes falling behind irreversible") rather than importing
a second chart. *(Open, with Cail: whether to show Europe-2031's compute-divergence chart — the
"same ratio, exploding gap" data point, two states 2026→2031 — or carry it spoken with the Le Monde
clip alone. Europe 2031 is a serious forecasting project, an AI-2027 analog, not a Substack; the
Moonshot is the Substack.)*

## Voice — measure, not earnestness

**Register: measure, carefulness, professionalism.** Not earnest, not effusive, not hype. For a
jury wary of AI-evangelism, restraint *is* credibility. Statement-headlines that are calm and
exact, not breathless; claims hedged where honest ("in my biased view", "an open question"); the
AI material delivered matter-of-factly, as method, never as spectacle. The stakes here are very
large — which is exactly why the talk *underplays*: when the magnitude is this big, understatement
carries the weight. Never dramatize it on a slide.

## Build notes — the METR landscape slide (the live iframe)

The `#metr` slide embeds METR's live `horizon-chart-embed` iframe (zoomed + cropped, our own title
overlaid). Three gotchas cost hours; do not relearn them:

- **METR draws its own multi-line header** — a jargony title *and* a "Measurements above 16 hrs are
  unreliable / with our current task suite" note box — sitting right above the 16h plot top. Cropping
  the iframe (`.metr-embed` `top` more negative) to remove it **eats the 16h plot top and exposes
  other METR chrome** — there is no clean crop. The fix is the **`.metr-chart-title` overlay band**
  (parchment bg, `z-index:3`) sized to mask *both* the title and the note box (currently `top:
  -22px; padding: 48px 6px 28px 6px; width: 1000px` — band bg is `$ground` = `$body-bg`, i.e. the
  slide background, so it's invisible parchment, not a visible "bar"; tune the title's vertical
  position with the padding split, not by moving the band), leaving 16h visible. **Mask, don't crop.**
- **`.metr-cropbox` `margin-top` is inert** — `.metr-chart-wrap` is flex `align-items:flex-end`, so
  the cropbox is bottom-anchored. Vertical position is set by the wrap `bottom` + `.metr-embed` `top`,
  never `margin-top`. Don't try to "move the iframe down" with it.
- **`quarto preview` does NOT watch `custom.scss`** — after any SCSS edit you **must `touch` the
  `.qmd`** to force a recompile, else the served theme CSS (and the live preview) stays stale. Verify
  by fetching the theme-CSS hash and grepping the new value, not just re-fetching the page.
- A clean static fallback (`images/metr_capability_trajectory.png`, with a "~4-year program" band)
  exists, but Cail wants the **live** chart — keep the iframe.

## Hard rules

- **No topic-label headlines.** Every `##` is a complete-sentence "so what." The headline sequence
  must read as a narrative on its own.
- **No italics in slide/figure text** unless Cail explicitly asks — they read poorly projected.
  Emphasize with color or weight, not slant; keep on-slide and SVG text upright.
- **Voice: researcher, not builder.** "led, produced, develop, contribute, characterise, design" —
  never "I built / I founded." Lightcone is *the open ecosystem I contribute to*, never "the
  startup I co-founded."
- **Tools named: `felt` and `Lightcone`** — Cail names Lightcone (the panel knows it; he names it in
  Talk 1). In **Part I**, name tools only as *evidence the principle works* (it scales with use), not
  as a "tools I built" pitch. **Part II is the deliberate exception**: its agentic timeline shows the
  practice Cail built (memory systems, constitutions, autonomous tasks, lightcone). **Never mention
  Vellum.** (ASTRA dropped from the Lightcone slide 2026-06-09 per Cail — don't reintroduce it.)
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

**The deliberate cross-deck rhyme (keep):** the *systematics-not-new-physics* story is the matched
pair. It is **planted as a taste in Talk 1** — the slide where the disagreement between surveys turns
out to be each instrument's own artifacts, "where my work lives" — and **told in full in Talk 2**,
closing on the conservative-by-design result (wider error bars on purpose, so as not to be the next
false alarm). Talk 1 does **not** open with S₈ — it opens on the AI landscape (METR); the cosmology,
and this taste, enter later. Planted-taste → full-payoff is the signature — don't break it.

> Note: the per-slide arcs below were written for the **old single-talk decks**
> (`RT_1_general`, `RT_2_deepdive`); the live deliverable is the **combined** `RT_interview.qmd`,
> whose Part I/Part II have since evolved. Treat the arcs as intent, not a line-by-line map, and
> reconcile against the combined deck before trusting a slide number.

Talk-2 accuracy is grounded in the paper source at
`ai-futures/application/interview/slides/bmode-paper/` (Daley et al. 2026, UNIONS-3500 WL II).
