# Astronomy on Tap: Astronomy at the Bottom of the World

**Date:** ~April 15, 2026
**Venue:** Astronomy on Tap (public bar talk)
**Format:** 20 min talk + 10 min Q&A. Two co-presenters.
**Audience:** General public — no equations, no publication figures, lots of pretty pictures.
**Goal:** Convey a few interesting things, provoke questions.

## Structure

- **Lennart Balkenhol** (~10 min): CMB and cosmology intro (separate deck).
  Ends having motivated the CMB and shown an SPT image.
- **Cail Daley** (~10 min, Part II): The observational and human side — the atmosphere
  drives site selection; the South Pole is where the drive ends up; life and science there.

## Narrative thread

**The atmosphere is the enemy, and it drives every choice.**

The ~15 slides walk the audience through the chain:

1. *Why not here?* (Paris rooftops) — cities obviously don't work: lights, clouds, humidity.
2. *Microwaves!* — pivot: microwaves are *light* too, and cities pollute the microwave sky
   just like the visible one (wifi, phones, ovens, radar). Speaker-side double point: (a) RFI
   would drown a CMB telescope in Paris, (b) atmospheric water vapor absorbs at the actual
   observing bands (95/150/220 GHz, driven by the 183 GHz line). Parkes peryton anecdote in
   speaker notes — but note: ovens at 2.45 GHz aren't directly in CMB bands; the real enemy
   is atmospheric H₂O.
3. *So we go up* (Pic du Midi) — mountaintops get us above lights and much of the weather.
4. *The sky isn't transparent* — the broader story: the atmosphere blocks most of the EM spectrum.
5. Three options: **space / balloons / ground** — tradeoffs, and we end up on the ground.
6. *Driest places on Earth*: Atacama, Tibet, South Pole.
7. *Why the Pole, specifically*: **HIGH / COLD / DRY / QUIET** (RFI-free).
   Drop the tropopause-altitude fact here ("feels more like 3400 m").
8. *Getting to the bottom* — logistics, isolation.
9. *Life at the bottom* — the human side (photos from Melanie, see below).
10. *The South Pole Telescope & SPT-3G*.
11. *Scanning the sky → the microwave sky → SPT sees everything* (COBE balloon-avoidance anecdote).
12. *What's next* — LiteBIRD and closing the loop back to space.

## Style notes (strict — keep these in mind every edit)

- **AoT = informal, public.** One punchy sentence (or *question*) per slide when possible.
- **Title + full-bleed image** is the default pattern. Credits are spoken or placed as
  HTML comments in the source, *not* as visible captions, unless we specifically want them.
- **No captions by default** — use `![](path.jpg)` (empty alt).
- **Do not use `{.r-stretch}` inside a `.column`** — it expands to the full slide height and
  overruns the footer. Plain `![](…)` sizes naturally; specify `{width="XX%"}` if needed.
- **No axis labels, no statistics, no jargon without a plain-language gloss.**
- Rhetorical-question fragments (`*…?*` inside `::: {.fragment}`) drive transitions.

## Credits policy

Cail will speak credits during the talk; the QMD keeps them as HTML comments or
small-print subtitles. Never delete credit info from the source file.

## Key image assets

Already placed in `images/`:
- `atmospheric_opacity_nasa.png` — Credit: NASA / Wikimedia
- `paris_eiffel_night.jpg` — Credit: Boreally (credit embedded in photo)
- `pic_du_midi_clouds.webp` — Credit: Matthieu Pinau

Available to pillage in `unused_images/` (gitignored, won't hit gh-pages):
- `unused_images/melanie_aot/` — 87 photos from Melanie Archipley's AoT deck
  (station interior, fuel arches, ice tunnels, shrines, NYE, auroras, pole-moving).
  Browse via `unused_images/_melanie_contact_sheet.html`.

Other sources to draw on:
- SPT photos: https://kicp.uchicago.edu/~bbenson/spt_pics/
- Tom Crawford's deck (`~/Downloads/Crawford_UIUC_2025_01_28.key`) — HIGH/COLD/DRY triad
  originally from his "Why the South Pole?" section.
- Shared `images/` pool (symlinked) with existing CMB/site figures.

## Workflow

- Render: `quarto render 26_AoT_BottomOfTheWorld/26_AoT_BottomOfTheWorld.qmd --to revealjs`
- Text QA: `node ~/.claude/skills/slides/scripts/slide-to-text.mjs _site/26_AoT_BottomOfTheWorld/26_AoT_BottomOfTheWorld.html --flags-only`
- Visual QA: headless Chrome screenshots at 1920×1080 (hash-navigation works: `#/N`)
- `quarto` command: currently served by `/usr/local/bin/quarto` → symlink to
  `~/Documents/projects/quarto-cli/package/dist/bin/quarto` (dev build, v99.9.9).

## What NOT to do

- Don't add Lennart to authors/footer — he has a separate deck.
- Don't include technical transmittance spectra, paper figures, or anything with GHz axes.
- Don't commit `unused_images/*` (already gitignored).
- Don't put images in a subfolder of `images/` unless it has a real reason —
  dump-folders go in `unused_images/`.
