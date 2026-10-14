# Repository Guidelines

## Project Structure & Module Organization
Slide decks live in date-prefixed directories such as `2609_FORTH_Crete/`, each containing a primary `.qmd` file and symlinks to the shared `images/` and `assets/` directories. Shared resources sit at the top level: `assets/` for HTML partials, `images/` for all talk figures, and `styles.css` for global Reveal.js tweaks. `_quarto.yml` configures the umbrella Quarto site, while `_site/` holds rendered output—never edit files there. `_template_quarto/` stores starter material when creating a new talk. `index.qmd` uses Quarto's native `listing:` to auto-generate the talks index at render time. `collect_unused_assets.py` handles image housekeeping.

## Build, Test, and Development Commands
- `quarto check`: confirm the Quarto CLI and required engines are available.
- `quarto preview`: serve the full site locally with live reload for incremental edits.
- `quarto render <talk>/<talk>.qmd --to revealjs`: build an individual deck into `_site/`.
- `quarto render`: rebuild the entire site after sweeping content changes (auto-runs on push to main via `.github/workflows/publish.yml`).

## Coding Style & Naming Conventions
YAML front matter uses two-space indentation and kebab-case keys; keep metadata blocks compact and alphabetical when practical. New talk directories should follow the `YYMM_EventName` pattern and keep file names lowercase with underscores, e.g., `assets/no_footer_on_titleslide.html`. Python utilities follow PEP 8 (4-space indentation, snake_case identifiers) and should include `if __name__ == "__main__":` guards.

## Asset Management
Every talk uses `images/` and `assets/` symlinks pointing to the repository's shared directories.
Keep these symlinks; add all figures and supporting assets to the shared pools, including those made for a single talk.
Use descriptive filenames to avoid collisions.

### What NOT to commit
- **PDFs / pptx** — presentation exports. Gitignored. Re-export from `.qmd` source as needed
  (`decktape` commands are in comments at the top of each `.qmd`).
- **`_site/`** — rendered output. Gitignored.
- **`unused_images/`** — images pruned by `collect_unused_assets.py`. Gitignored.

### Meta-work is fine to commit — with two hard bars
The repo is public — build scaffolding (speaker notes, per-talk `CLAUDE.md`, outlines, internal
reasoning, felt fiber names) is fine to commit and push, subject to two bars: **genuine PII**, and
**unblinded results**. No unblinded number from a blinded analysis — no unblinded amplitude, no
sub-/super-unity statement about unblinded data, no figure of unblinded measurements against theory —
may be committed *anywhere* in the repo (speaker notes, per-talk CLAUDE.md, retired figures, planning
docs); that background belongs in the private felt store, and the repo carries a pointer at most.
**Blinded** data vectors and blinded estimates are allowed (Cail's decision, Oct 2026), labelled as
blinded, in decks that set `"noindex": true` in `deck.json`. The rule for what counts as blinded:
a quantity that carries cosmology is blinded; a non-cosmological quantity (a calibration such as the
lens ratio γδ/κδ, which the blind moves by only a few per cent) or a null (template × data, whose
expectation is zero whatever the cosmology) may be shown as it is. Call such a quantity
blind-insensitive, never "unblinded". **Outside the bar entirely (Cail, 12 Oct 2026):** Euclid TR1
measurements (TR1 is not a blinded release) and non-tomographic cross-spectra, e.g. a collaborator's
κ × shear over the whole source sample against a fiducial curve. Don't hold these back; the bar is for
cosmology inferred from blinded DR1 vectors. A noindex deck is unlisted, reachable only by its link like a
shared Google Slides deck, so it carries no further publicity gate: contributed and in-progress material
goes in, and Cail does the final pass before showing it.

### Image hygiene
- **Resolution over file size**: use figures at full resolution — scientific figures need to stay
  crisp on a projector, and degrading them to hit an arbitrary byte cap is the wrong tradeoff. Match
  the source figure's native resolution; don't downsample or re-compress to save space.
- **Pruning**: `python collect_unused_assets.py` (dry run by default) scans all `.qmd`, `.md`,
  `.html`, `.yml`, `.scss` files for `images/` references. Use `--move` to relocate orphans to
  `unused_images/`.
- **No git-lfs** — GitHub Pages cannot serve LFS-tracked files.
- **History matters**: large binaries bloat `.git/` permanently. When removing images, also
  consider `git filter-repo` to strip them from history (requires force push).

### Deployment (GitHub Pages via Actions)
Deployment is automatic: **pushing to `main` triggers `.github/workflows/publish.yml`**, which runs
the house tests and `house/check.mjs --all` (any failing house deck blocks the deploy), unpacks the
**frozen Quarto site** (release `frozen-quarto-site`: the Quarto decks and index as last rendered,
14 Oct 2026), builds the house decks on top with `house/build.mjs --all --out _site --web`, and
publishes `_site` as a Pages artifact. Pages source is `build_type: workflow`, not deploy-from-branch.

- **Quarto decks are frozen.** CI no longer renders them; editing a `.qmd` changes nothing online.
  To republish one, render it locally and replace its directory in the release tarball.
- **Just commit source to `main`.** Never commit `_site` (gitignored) or rendered HTML.
- **Do NOT run `quarto publish gh-pages`**: Pages ignores the `gh-pages` branch.
- Live site: <https://cailmdaley.github.io/talks/>

### Clean talk URLs
Set `output-file: index.html` in each deck front matter so the public URL is
`/talks/<talk-directory>/`, without repeating the talk name. Keep descriptive `.qmd` filenames.
