# House deck system

Talks are hand-authored HTML on reveal.js, written against one design system and verified by a checker that renders every slide. There is no Markdown layer: one file per slide, a small index, and a build that inlines everything into a single offline HTML file.

```
node house/build.mjs <deck-dir>        # → _site/<deck>/index.html and report.html
node house/check.mjs <deck-dir>        # lint + render; screenshots in <deck-dir>/_check/
node house/check.mjs <deck-dir> --steps          # also one screenshot per fragment step
node house/check.mjs <deck-dir> --only a,b       # just these slides
npm test                               # the checker's own tests (demo passes, fixtures fail)
```

First time on a machine: `npm install` at the repo root. PDF figures need `pdftocairo` (poppler).

## A deck

```
2610_Napoli_CMBX/
├── deck.json
├── slides/
│   ├── title.html
│   ├── footprint.html
│   └── …
└── images -> ../images        # the shared figure pool; add new figures there
```

`deck.json` is the index: metadata, theme, and the sections in order, each with a one-sentence outline and its slides (file names without `.html`). Every file in `slides/` must be listed; spare slides go in a `Backup` section.

```json
{
  "title": "Euclid × CMB lensing",
  "author": "Cail Daley",
  "venue": "OU-SHE × WLSWG, Napoli",
  "date": "2026-10-13",
  "description": "One line for the talks index.",
  "footer": "Cail Daley · Euclid CMBX · Napoli · October 2026",
  "theme": "euclid",
  "draft": false,
  "macros": { "Ckk": "C_\\ell^{\\kappa\\kappa}" },
  "sections": [
    { "title": "Data", "outline": "RR2 overlaps ACT and SPT lensing over 385 deg².",
      "slides": ["title", "footprint", "nz"] }
  ]
}
```

`theme` is one of the files in `house/themes/` (default `house`). `macros` are TeX macros for every slide. `css` names an optional deck stylesheet for rare one-offs; classes it defines join the vocabulary the linter accepts. `draft: true` keeps the deck off the talks index but still publishes it at its URL.

A slide file holds exactly one `<section>` with a `data-layout`, a headline, its content, and speaker notes:

```html
<section data-layout="figure">
  <h2>Mock bandpowers follow the model to $\ell \approx 2000$</h2>
  <figure>
    <img src="images/house_demo_spectrum.pdf" alt="Mock bandpowers against a model spectrum">
    <mark class="box fragment" data-box="63 38 33 46" data-label="small scales"></mark>
    <span class="source">Synthetic spectrum made by house/demo/make_demo_figure.py.</span>
  </figure>
  <aside class="notes">
    <p>The paragraph a reader needs: what is plotted, what to see, why it matters.</p>
  </aside>
</section>
```

The headline is a claim, one line. The notes are prose: the report variant prints them under each slide, so they are written for a reader, not as a script fragment. Math is TeX between `$…$` or `$$…$$`, typeset at build time; a TeX error fails the build. Put punctuation that follows inline math inside it (`$b_i,$`), or the line may break before it.

## The canvas and its budget

Every slide is a fixed 1920×1080 frame. The content box is x 104–1816, y 72–968 (1712 × 896 px); the footer sits below it. With a one-line headline the body box is **1712 × 771 px** (y 197–968). Space is arithmetic: count before you write, and when content does not fit, **split the slide — nothing shrinks**. The checker rejects inline type sizes and anything below 24 px.

The type scale has five sizes. Emphasis is weight (`<strong>`) or colour (`.accent`, `.muted`), never another size.

| token | px | used for | line pitch | chars per line: full 1712 | points 1560 | text column 659 | half 824 | third 544 |
|---|---|---|---|---|---|---|---|---|
| `--t-display` | 104 | title, section divider, big numbers | 108 | 41 | — | 16 | 20 | 13 |
| `--t-head` | 60 | headlines, statements, quotes | 67 | 72 | 65 | 27 | 34 | 22 |
| `--t-body` | 44 | body text, bullets | 59 | 101 | 92 | 39 | 48 | 32 |
| `--t-small` | 32 | captions, table cells, stat labels, nested bullets | 43 | 139 | 127 | 53 | 67 | 44 |
| `--t-fine` | 24 | sources, kickers, footer — the floor | 32 | 185 | 169 | 71 | 89 | 59 |

Characters per line are measured averages for prose in EB Garamond; plan on about 85 % of them, since words wrap whole. Rules of thumb for the 771 px body:

- a one-line bullet costs 79 px (line plus gap), a two-line bullet 139 px: at most **nine one-line bullets**, about five two-line ones;
- a headline that wraps to two lines costs 67 px of body; three lines is an error;
- a figure caption (`figcaption`) costs 54 px and a `.source` line 48 px off the figure's height;
- a figure fills its cell at its own aspect ratio: in the `figure` layout a 16:9 plot is 1371 × 771, a 4:3 plot 1028 × 771; each half of `compare` is 824 wide, so a landscape plot there is width-limited.

Above 60 words of on-screen text the checker warns: the audience reads instead of listening.

## Layouts

`data-layout` on the `<section>`; the checker enforces what each may hold at its top level, after the headline.

| layout | holds | for |
|---|---|---|
| `title` | `<h1>`, `p.subtitle`, `p.byline`, `p.affil`, `p.venue`, `p.date`, `div.logos` | the opening slide; no footer |
| `section` | `<h2>`, one `<p>` | a divider: section title and its outline |
| `statement` | `<h2>`, up to two `<p>` | one claim, vertically centred |
| `points` | `<h2>`, lists, `<p>`, `div.eq`, `div.cols`, `<pre>`, `.source` | a text slide |
| `figure` | `<h2>`, one `<figure>` | one figure filling the body |
| `figure-text` | `<h2>`, one `<figure>`, one `div.text` | figure beside labels or key numbers; `data-split="50|60|70"` is the figure's share (default 60), `data-flip` puts the text left |
| `compare` | `<h2>`, two `<figure>` | side by side, each with a `figcaption` label |
| `grid` | `<h2>`, three to six `<figure>` | three columns; four make a 2 × 2 |
| `number` | `<h2>`, one to three `div.stat` | key numbers: `<div class="stat"><span class="value">385</span><span class="label">deg² …</span></div>` |
| `bleed` | optional `<h2>`, one `<figure>` | a photograph filling the canvas; headline on a band |
| `table` | `<h2>`, one `<table>`, `.source` | `th`/`td`; `td.r` right-aligns, `tr.hl` highlights a row |
| `quote` | one `<blockquote>`, `.source` | a quotation |
| `closing` | `<h2>`, an `<ol>` of takeaways, `p.contact` | stays on screen for questions |

## Figures

A `<figure>` holds an optional `<figcaption>` (a label above), one image, optional `<mark>` highlights, and an optional `.source` line under it.

- **Pre-rendered figures are the normal case.** PNG, JPEG, SVG and PDF work as `<img src="images/…">`; a PDF's first page is rasterised to 3200 px on its long side at build time (cached in `node_modules/.cache/house`). The image takes the largest box of its aspect ratio that fits its cell. White plot backgrounds multiply into the slide ground, so plots sit on the paper without a white rectangle; a figure whose background is content (a photograph, a map with a cream ground) takes `class="plain"`.
- **Text in figures** must be legible on screen too, and the checker cannot read pixels: make axis labels and legends at least 24 px *as displayed*. A plot shown 1371 px wide from a 12-inch matplotlib figure at 100 dpi is scaled by 1.14, so 22 pt labels are about 35 px. Look at the screenshots.
- **Highlights** are the one emphasis device for data figures: `<mark class="box fragment" data-box="x y w h">` outlines a region given in percent of the image (from its top left); `data-label="…"` adds a tag above it (`class="below"` puts it under). `<mark class="spot fragment" data-box="…">` dims everything outside the region instead. Add `fade-in-then-out` to a box that should disappear at the next step.
- **Schematics are inline SVG**, for diagrams with no plot behind them. Put the `<svg viewBox="…">` directly in the `<figure>`; it scales like an image. Colour it with theme classes so it recolours with the theme — `fill-ink`, `fill-muted`, `fill-accent`, `fill-teal`, `fill-cobalt`, `fill-ochre`, `fill-rule`, `fill-panel`, `fill-ground`, `fill-none`, and `stroke-…` for each colour — and leave text unstyled (it takes the deck's face and ink). Give `font-size` in viewBox units; the checker measures it on screen against the 24 px floor. `<g class="fragment">` reveals parts in order. Ids must be unique across the whole deck (prefix them with the slide name).
- `<div class="placeholder">figure to come</div>` in place of the image marks a figure not made yet; the checker warns while one remains.

## Components

- `<div class="eq"><span class="kicker">Label</span>$$…$$</div>` — a labelled display equation.
- `.kicker` — small-caps label above a block. `.source` — attribution in the fine size. `.num` — a key number inline. `.tag` — a pill.
- `.accent`, `.muted`, `.teal`, `.cobalt` — colour emphasis. `.small`, `.fine` — the two smaller sizes, for secondary lines.
- `<div class="cols">` — two or more equal columns inside a `points` body.
- `<pre><code>` — code in the mono face at the fine size.
- Fragments are reveal's: `class="fragment"` on any element, with reveal's variants (`fade-in-then-out`, `semi-fade-out`, …).

## Depth on demand

A detail is a slide outside the linear order: a null test, the per-bin version of a plot. Write it inside the slide's `<section>` as

```html
<aside class="detail" data-label="Per-bin fits" data-layout="grid">
  <h2>Each bin fits on its own</h2>
  <figure>…</figure> …
</aside>
```

with any layout. A chip labelled with `data-label` appears above the footer; clicking it (or pressing `D`) opens the detail over the slide, and Escape returns to the same slide and fragment. The checker renders and measures every detail; the report prints each one after its slide. There are no vertical slides.

## The checker

`node house/check.mjs <deck>` exits 1 on any error and writes `<deck>/_check/`: one screenshot per slide with all fragments shown (`NN-name.png`), one per detail, `contact.png` (every frame on one sheet, errors outlined red, warnings amber) and `check.txt`. Look at the contact sheet before calling a deck done; a passing check says nothing about whether a figure's own labels are legible.

Errors: an unknown layout or a class outside the vocabulary (house.css, the themes, the deck's css); content a layout does not allow, or too many of it; an inline font size; a TeX error or missing image (build failure); anything outside the content box or off the canvas; an element clipping its content; body blocks overlapping each other; text set below 24 px, including SVG text as displayed; text contrast below 4.5:1 against its background; a three-line headline; a page error or any network request (decks must work offline).

Warnings: a two-line headline; more than 60 words on screen; missing speaker notes; a placeholder; inline styles; images without alt text.

## Themes

A theme is a token set in `house/themes/<name>.css` over the same layouts; `deck.json` names it.

- `house` — warm paper (`#F7F0E1`), ink, one cinnabar accent, EB Garamond.
- `house-dark` — the same palette on a dark ground; figures sit on white cards instead of multiplying.

A theme sets `--ground`, `--ground-deep`, `--ink`, `--muted`, `--accent`, `--teal`, `--cobalt`, `--ochre`, `--rule`, `--panel`, `--veil`, `--figure-card`, `--figure-blend` and may add furniture (a logo, a band) with ordinary CSS; `url(…)` paths in a theme are resolved relative to `house/themes/` and inlined. Contrast is checked per deck, so a new theme is tested by running the demo with it.

## Output

`_site/<deck>/index.html` is the deck: one self-contained file (fonts, reveal, figures and typeset math inlined), works offline and from `file://`. `S` opens reveal's speaker view with the notes. For a PDF, `decktape reveal --size 1920x1080 _site/<deck>/index.html out.pdf`.

`_site/<deck>/report.html` is the same slides scaled into a scrolling document, each followed by its notes and details: the written version of the talk, from the same source.

Publishing: pushing to `main` runs `.github/workflows/publish.yml`, which renders the Quarto site, builds every directory holding a `deck.json` into `_site/`, and lists non-draft house decks on the index (via `house-decks.yml`, generated with `node house/build.mjs --listing house-decks.yml`). The public URL is `https://cailmdaley.github.io/talks/<deck-dir>/`. Older Quarto decks build as before.
