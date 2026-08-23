# FORTH Crete keynote — Scaling Scientific Labor with Agentic Engineering

Build-facing narrative for the closing keynote at FORTH's Workshop on Physics-Informed Machine
Learning, Heraklion — **Fri 18 Sep 2026, 11:30–12:30** (30 min talk + 15 min live demo + 15 min
discussion). The strategic record lives in the felt fiber `2609-forth-crete` (constitution) and its
children `talk-direction` (the argument) and `harness-history-materials` (intro-beat assets +
citations). Read those for depth; this file is what you build slides against.

**Working on this deck: activate the `slides` skill first, every time.** Script in the notes,
visuals on the slide. This deck especially: Cail's explicit direction is *not too much text on
slides — images/plots/diagrams instead, make your own SVGs where needed*. Resist the urge for
prose on slides. Every slide: one headline assertion, one strong visual, labels not sentences.

## Audience & register

Physics-informed-ML researchers who have **not** worked agentically. Their home intuitions are
pipelines and DAGs — exactly what the paradigm shift deletes, so the history beat must land
mechanically, not impressionistically. Register for the implications close: **agency and joy, not
grimness**. Tutorial-style throughout; this is the closing keynote, permission to be expansive.

## The arc (30 min ≈ 30 slides; four beats)

1. **History (slides ~1–5): chatbot → harness, two years.** Chatbot → chatbot-as-oracle
   (copy-paste code out) → hand-wired multi-LLM DAGs (`images/openai-agent-builder-dag.jpeg` is
   the "before" picture — intelligence in the boxes, plumbing between) → the modern harness
   (`images/earendil-harness.mp4` plays under narration: system prompt, tools, agentic loop,
   translation layer — control flow lives in the model). Pedagogical target: audience genuinely
   understands what a harness is and what "agentic" means. Blog link below slide:
   earendil.com/posts/what-is-a-harness/.
2. **The landing (slide ~6–7): we are at the beginning of the singularity.** Stripe investor
   letter (Axios 2026-08-19): "January 1st marked the beginning of the singularity, and we have
   since been operating on that basis." Supporting numbers in the materials fiber. Serious people
   now use this vocabulary descriptively. Zvi's accelerating-timeline (4.5 Gyr → … → LLMs 8 yr,
   "the math predicts a singularity") lands well from a cosmology speaker — orientation, not
   persuasion; a couple of minutes.
3. **The ASTRA tutorial (~15 min, slides ~8–20).** Exactly the tutorial at
   <https://lightconeresearch.github.io/agent-skills/latest/astra/> (extract:
   `astra_tutorial_reference.md`): measure dark energy from 580 Union2.1 supernovae. Five steps:
   data → spec (astra.yaml) → run (Ω_Λ = 0.722 ± 0.013) → verify against Suzuki et al. 2012
   (verify-quote, 0.705 +0.040/−0.043) → **the decision** (systematic covariance: error bar more
   than doubles to ±0.030, value barely moves — "the difference between a number that resembles
   theirs and a number you can put beside theirs"). Wrap with agentic-workflow-in-practice
   material from the CNRS deck: verification environments, long-running work, orchestration.
4. **Implications (slides ~21+).** Dean Ball tweets (astrophysics as information science; the
   temporary meta-skill), the five-year stake in the ground, wave-or-eddies choice put to the
   audience — neither path is bad. Full tweet text + the stake wording in `talk-direction`.

Open taste calls (Cail's): where Zvi's pills fold in (compressed into the landing vs. moved to
implications); the live-demo content (15 min slot, separate from the 30 min talk); whether the
ecologies-of-intelligence / OpenAI→HF incident thread fits this audience.

## Sources to reuse

- **CNRS decks** (`../26_CNRS_RisingTalents/`): the workflow-in-practice spine, house layout
  patterns, many images (task boards, compute scaling, timelines). Speaker-note style there is
  the model: verbatim script paragraphs per slide.
- **Theme**: house look from `../assets/house.scss` via `theme: [default, ../assets/house.scss,
  custom.scss]`; figure-on-ground via `assets/figure-treatment.html`.

## Build

```bash
cd ~/Documents/projects/talks
quarto render 2609_FORTH_Crete/2609_FORTH_Crete.qmd --to revealjs
node ~/.claude/skills/slides/scripts/slide-to-text.mjs _site/2609_FORTH_Crete/2609_FORTH_Crete.html
```
