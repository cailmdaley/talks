# FORTH Crete keynote — Scaling Scientific Labor with Agentic Engineering

Build-facing narrative for the closing keynote at FORTH's Workshop on Physics-Informed Machine
Learning, Heraklion — **Fri 18 Sep 2026, 11:30–12:30** (30 min talk + 15 min live demo + 15 min
discussion). The strategic record lives in the felt fiber `2609-forth-crete` (constitution) and its
children `talk-direction` (the argument) and `harness-history-materials` (intro-beat assets +
citations). Read those for depth; this file is what you build slides against.

**Working on this deck: activate the `slides` skill first, every time.** This file is the evolving
narrative guide; `AGENTS.md` links here so both harnesses receive the same direction. Update it
as Cail refines the argument, ordering, and intent. New sessions should start here.
Speaker notes are a dump space for thoughts and supporting material; Cail does not read them.
Do not leave narrative decisions only in notes or invent a polished script in Cail's voice.
Prefer images, plots, diagrams, and short labels on slides. The opening overview deliberately
uses three substantial bullets; Cail approved this exception to the usual sparse-text approach.

## What we are trying to convey

This is a mixed tutorial and talk about scaling scientific labor, framed around three questions:
1. What can we do with agentic science now?
2. What do I want my scientific practice to be, given these capabilities?
3. What will agentic science be able to do in the future, and where does that leave us?

The change of subject (we → I → agentic science) leaves a tension about agency implicit.
Do not announce a predetermined loss of agency. Distinguish changes in the surrounding field
from the personal choice of how to work. The tutorial offers practical experience to inform
that choice, not an injunction to adopt agents. Cail usually finds this work very fun and
enjoyable; sharing that possibility is the motivation. A different framing of work is needed.
Keep enjoyment, understanding, responsibility, and freedom to choose central.

A possible later connection is the Bitter Lesson: apply expertise to framing problems and
building feedback and verification that let scalable computation help solve them. This is
Cail's application to scientific practice, not a claim that expertise or solving things
oneself is worthless. Human attention is limited; machine effort can scale with resources.
The transition now applies this idea through a checkable-problem diagram; it does not quote Sutton as endorsing every proposed agent workflow.

## Audience & register

Physics-informed-ML researchers who have **not** worked agentically. Their home intuitions are
pipelines and DAGs — exactly what the paradigm shift deletes, so the history beat must land
mechanically, not impressionistically. Register for the implications close: **agency and joy, not
grimness**. Tutorial-style throughout; this is the closing keynote, permission to be expansive.

## The arc (30 min ≈ 30 slides)

1. **Overview → capabilities → October 2025 Agent Builder → swarms.** Slide two frames three questions: what agentic science can
   do now; the practice each person wants; and where future capabilities leave us. This
   motivates the METR chart immediately afterward. The chart uses fixed 50% human-expert task
   horizons, uncertainty, and log/linear views. Spell out the human-expert-time axis and give
   concrete METR task examples. No trend extrapolation control. Initially show measurements
   through Mythos just above 16h, with an amber off-plot “Mythos Preview (saturates)” label and
   no shaded warning region. Axes stay fixed across all reveals; upper ticks use days. Label
   GPT-2, GPT-4, Claude 3.7 Sonnet, and Mythos. The sidebar first asks about human expert time to solve a Millennium Prize Problem.
   One arrow replaces the question with both Navier–Stokes (88h) and the recovered Hugging Face
   campaign (108h), together. Name the achievements: a Millennium Prize Problem and a
   multi-exploit intrusion into a major ML platform. Both case labels sit left of their points. A subtle upper-right axis, “Agent wall time,”
   spans 2–12 days and appears with the cases; human-time ticks on the left stop at 2 days.
   This deliberately juxtaposes different metrics rather than converting runtime to human effort.
   Keep numbers once: time on the plot, concurrency and bold approximate agent-hours beside it.
   Cost belongs in a separate falling-prices beat, motivated by Cail's supplied prinz tweet.
   Verify benchmark cost comparisons; do not adopt its 2028 mathematics prediction as fact.
   The following cost slide compares ARC-AGI-1 semi-private scores: o3-preview 87.5% at an
   estimated $4,560/task versus DeepSeek-V4-Flash 0731 High 87.0% at $0.0214/task. o3's cost
   was reconstructed using later o3-pro pricing. This supports cheaper comparable benchmark
   performance, not a forecast of Navier–Stokes cost. The Navier 130B tokens / $6.5M illustration
   lives here, after the HF swarm and before the history beat.
   The swarm headline is “The hardest problems are being solved by swarms.” Use “The Hugging Face attack” as the chart subheader. Animate on entry in about one
   second, with readable, unclipped dates and milestones. Put the stage legend inside the
   lower-left. The “~1,200 agents” count sits above the timeline and fades in at animation end; omit the attack count. Remove redundant hover
   readouts. No agent quotes. On the next advance, reveal the question on the right below the agent count,
   asking whether Navier–Stokes had similar swarm dynamics:
   parallel exploration, communication, then convergence. This is an analogy, not measured
   Navier trajectory data. Cost-slide sources and accounting detail live in a collapsed dropdown.
   After costs, connect personal practice to engineering: what would make more effort useful?
   The tutorial provides a practical window into another way of working so people can choose
   for themselves. Avoid urgency, compulsory adoption, or forecasts as prerequisites.

2. **Engineering scalable work (~12–15 min).** The transition asks what would make more effort
   useful: scientific judgment → a checkable problem → scalable effort. This is an invitation
   into a different practice, not a demand to adopt it. Clipboard → write/run/observe loop
   (two progressive reveals) → finite context → prompt caching → durable notes → skills →
   plugins → hooks → subagents/workflows → iteration with stopping rules → verification
   backpressure → experiment lineage → Lightcone → ASTRA. Each mechanism earns a diagram.
   Claude Code's February 2025 release made terminal execution accessible; it did not invent
   tool use. Harnesses execute requests and return observations; they do not remove brittleness.
   Caching reduces repeated input processing, not output cost or context limits. Checks carry
   judgment but do not prove scientific truth. Repeated effort without feedback can fail.
3. **Lightcone bridge.** Accumulating files and experiments risks crossing inputs, decisions,
   and outputs. Explicit records make work inspectable. François Lanusse and Liam Parker
   co-lead Lightcone, based at BIDS/UC Berkeley and CNRS AISSAI; Cail contributes. ASTRA
   specifies and validates the analysis, while agents/execution tooling run it. The singularity
   slide is removed. The Bitter Lesson informs the engineering framing as an analogy, not a
   prediction that direct human practice becomes worthless.
4. **The ASTRA tutorial (~15 min).** Exactly the tutorial at
   <https://lightconeresearch.github.io/agent-skills/latest/astra/> (extract:
   `astra_tutorial_reference.md`): measure dark energy from 580 Union2.1 supernovae. Five steps:
   data → spec (astra.yaml) → run (Ω_Λ = 0.722 ± 0.013) → verify against Suzuki et al. 2012
   (verify-quote, 0.705 +0.040/−0.043) → **the decision** (systematic covariance: error bar more
   than doubles to ±0.030, value barely moves — "the difference between a number that resembles
   theirs and a number you can put beside theirs"). Wrap with agentic-workflow-in-practice
   material from the CNRS deck: verification environments, long-running work, orchestration.
5. **Implications.** Dean Ball tweets (astrophysics as information science; the
   temporary meta-skill), the five-year stake in the ground, wave-or-eddies choice put to the
   audience — neither path is bad. Full tweet text + the stake wording in `talk-direction`.

Open taste calls: the live-demo content (15 min slot, separate from the 30 min talk), and how
far to develop the closing implications. Zvi's three-way distinction informs the overview;
do not use pill terminology. The Hugging Face swarm is now part of the opening exploration.

## Sources to reuse

- **CNRS decks** (`../26_CNRS_RisingTalents/`): the workflow-in-practice spine, house layout
  patterns, many images (task boards, compute scaling, timelines).
- **Theme**: house look from `../assets/house.scss` via `theme: [default, ../assets/house.scss,
  custom.scss]`; figure-on-ground via `assets/figure-treatment.html`.

## Live demo mechanics (tutorial beat)

Cail's terminal covers the **left half** of the screen during the live tutorial. Every tutorial
slide is a `.live-pair`: prompt card left (copied *before* the terminal opens — each card has a
`copy` button; `demo/prompts.md` holds all five for `cat`), "while it runs" panel right (the only
thing the audience sees while he types). Step 3's right panel is a `.live-figure` that polls
`~/forth-demo/results/hubble_diagram.png` every 1.5 s and swaps it in when the agent writes it
(`live-demo.html`; override the HTTP base with `?demo=http://127.0.0.1:4203` on the deck URL). Run the demo in
`~/forth-demo/`, or pass the override. Prompts follow the ASTRA tutorial verbatim except for the
explicit `results/hubble_diagram.png` save path.

## Build

```bash
cd ~/Documents/projects/talks
quarto render 2609_FORTH_Crete/2609_FORTH_Crete.qmd --to revealjs
node ~/.claude/skills/slides/scripts/slide-to-text.mjs _site/2609_FORTH_Crete/2609_FORTH_Crete.html
```

### Fiber embed (self-contained copy)

The fiber `2609-forth-crete` embeds `deck.html` from its own directory, not `_site/` — the site
render links `../site_libs/` relatively, which the felt viewer can't resolve (blank/unstyled iframe).
A project render ignores `embed-resources`, so build the copy outside the project:

```bash
S=$(mktemp -d); T=~/Documents/projects/talks
ln -s $T/assets $S/assets; ln -s $T/images $S/images; cp -R $T/2609_FORTH_Crete $S/
(cd $S/2609_FORTH_Crete && quarto render 2609_FORTH_Crete.qmd -M embed-resources:true -o deck.html)
cp $S/2609_FORTH_Crete/deck.html ~/loom/.felt/work/talks/2609-forth-crete/deck.html
```

Slide five now opens with Navier–Stokes cost, then the ARC comparison and takeaway: frontier
moonshots may stay expensive, while today’s hard problems can become cheap. Sources are linked
in readable dropdowns on slides four and five. The transition after costs now opens the personal-practice question and motivates the tutorial.

The Agent Builder slide now sits between capabilities and swarms: October 2025, less than a
year ago, using the large light-background screenshot. This sets up the contrast with swarms.
The case-study wall-time inset floats above the human-time plot on an independent mapping.
The overview keeps the parenthetical on the first line and bolds the question on the second.
Use slide IDs when discussing ordering; the rebuilt middle now runs from soon through astra-intro.
The deck currently has 41 main slides, plus backups. Budget roughly 8 minutes for the opening,
12–15 for mechanics, 15 for the tutorial, and 7–10 for implications; trim spoken depth to keep
45 minutes before questions. The later practice examples remain available for selective pacing.

## Tutorial display contract

The terminal covers the left half, including the prompt after copying. The right half is the
persistent audience view. Keep its YAML readable (32px), illustrative rather than a full spec,
and do not reveal fitted values or the comparison before an explicit advance. Copy buttons
copy prompt content only, independent of rendered visibility.

The Hubble image must appear at `/Users/cd280747/forth-demo/results/hubble_diagram.png`.
Start `python3 assets/crete-demo/serve_figure.py` from the talks repository. It serves only that
image at `http://127.0.0.1:4203/results/hubble_diagram.png`; the panel polls every 1.5 seconds.
Use `--root /another/demo` to change the disk directory. HTTP slides cannot load file:// images.
Lightcone uses the CNRS ecosystem framing and logos, with no personal-membership caption.

## Tutorial and closing sequence

The first practical hurdle is delegation of execution: using a chatbot for answers is different
from giving a tool-equipped agent a bounded piece of work. Questions remain valuable; avoid
implying inquiry itself is passive or inferior. The clipboard/harness pair makes the distinction.
Before the tutorial: low-level components and context, then organization / Lightcone / ASTRA.
After the tutorial: task versus question → reusable procedures → iteration → verification
backpressure → meta-skill → stake → pharmakon → differing practices / meaning → enjoyment.
Iteration and verification now generalize from the audience's actual tutorial experience.
Repeated/generalizable work should become procedures plus checks when worth the investment;
reliability is engineered around stochastic output. Do not promise deterministic correctness.
The task-board screenshots and duplicated CNRS practice/principles/science examples are backups,
as are the information-science and simulation/RL detours. No Shuttle UI required in the main arc.

Three exploratory slides follow reusable practice: iterative search → wiki as an addressable
knowledge primitive → past work informing new questions. Keep this distinct from the earlier
context-window mechanics. Wikis, plain files, grep, indexes, and semantic retrieval are tools
that can be combined; no claim that grep universally replaces RAG. Sources and upkeep matter.
The compounding-value diagram proposes connections to test, not automatic scientific truth.
These slides are material to refine and cut, not a requirement to fill the remaining slide budget.

Primitive sequence: execution loop → finite working memory → caching the unchanged prefix →
persistent external records. Build the analogy to classical engineering without conflating
context capacity, cached computation, and persistent storage. Permissions / tool boundaries
are a candidate missing primitive, not yet a new slide. The delegation/control slide is awaiting
Cail's next explanation; leave it alone until that arrives.

Interaction-pattern sequence replaces the old control-location slide: bounded delegation →
parallel independent questions → communicating teams → generated programmatic workflows.
Give each a full slide. Teams show ongoing direction and evidence exchange; workflows show
scatter/gather, adversarial review, acceptance criteria and bounded retry. Distinguish dynamic
communication from explicit orchestration code; stochastic workers can live inside a fixed
program. The forward graph is DAG-like but the retry path is a loop. Connect to October 2025
Agent Builder without claiming it was a 2024 example. Keep user control and inspectability central.

Team economics: a strong lead can concentrate design and decomposition, while cheaper models
execute well-scoped tasks; model choice still follows difficulty. The experiment-record bridge
uses a playful slop cannon to distinguish throughput from coherent scientific records. Lightcone
is presented in two layers: ASTRA specification/validator, then execution tools on that foundation,
with a visible project link and no personal-membership caption.

## Lightcone Lab trial

Installed jupyterlab-lightcone[ai] 0.0.6 in `/tmp/crete-lightcone-venv` for this trial.
Launch: `/tmp/crete-lightcone-venv/bin/jupyter lab --no-browser --ServerApp.ip=127.0.0.1 --ServerApp.port=8889 --ServerApp.root_dir=/Users/cd280747/forth-demo`.
The workbench is authenticated; use its runtime launch URL, never commit its token. Verified
Lightcone Agent / ASTRA Inventory / MySTRA Viewer launcher entries. No tutorial run or AI
provider configuration has been performed. The temporary environment is disposable; decide
whether to make this the tutorial surface after Cail tries it.

Lightcone Lab 0.0.6 resolves output artifacts as `results/<universe>/<output-id>.<format>`;
without named universes the directory is `default`. This was verified in the installed SDK's
artifactPath resolver. A loose `results/hubble_diagram.png` is invisible to its inventory.
Use `assets/crete-demo/workbench.sh --reset` to discard the current tutorial (including
.git/annex) in place, keeping Jupyter running at the same `~/forth-demo` root and localhost:8889 URL.
Run reset from a Jupyter terminal after stopping active agent work; start a fresh chat afterward. Previous
attempts are disposable: do not archive them. The priority is seeing each attempt's current
outputs in the ASTRA viewer. Materialize through Lightcone into the canonical paths above;
do not rely on compatibility links from an earlier attempt.

## Tutorial after rehearsal

Three prompts suffice for the 15-minute tutorial: initiate the Lightcone analysis, compare with
Suzuki et al.'s supernova-only constraint, then improve systematics and track changes as ASTRA
decisions. Keep representative YAML on the right of all three slides and a fixed vertical
centre for the prompt cards. No hard-coded uncertainty comparison, covariance diagram, or
extra "three more decisions" slide. Show actual results in JupyterLab. Universes can wait.
Installation stays on one slide, both harness command sets visible, with both ACP adapters
and Node/npm included in the optional isolated Jupyter environment.

Sources and notes use the shared `assets/sources-notes.html` include: a fixed bottom-left
button and compact overlay, never an expanding slide layout. Existing sources details and
same-origin embedded chart notes feed the same control. Use this shared pattern in future decks.

## Engineering transition and closing

Opening overview: what we can do now; how to engineer this way of working; what we want our
practice to become. Three transition slides replace the generic effort slide: computation
expanded science; software practices respond to constraints; agentic engineering introduces
new constraints on delegation, coordination and verification. IDEs/notebooks are responses to
constraints, not themselves the fundamental constraints. Carry memory, lazy loading, caching,
parallel workers and feedback analogies through the primitives without claiming exact equivalence.
Closing includes the reluctant self-revolution quotation (translated post linked), before
sources of meaning. Protecting some practices by scaling others remains a possibility.
Private anecdotes from the discussion must not enter slides or notes.

After verification, three practical review/management slides: understand implementation via
agent walkthroughs and inspect critical source; request HTML reports with plots and artifact
links for human review; track concurrent work in a board with status, blockers and evidence.
Symphony is a linked example. Personal custom tooling stays an oral aside. Reports and model
explanations are aids to scrutiny, not substitutes for checking actual behavior and evidence.

Published URL: `https://cailmdaley.github.io/talks/2609_FORTH_Crete/`. The deck uses
`output-file: index.html`; keep the source filename unchanged.
