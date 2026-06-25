# Repository Guidelines

## Project Structure & Module Organization
Slide decks live in date-prefixed directories such as `25_ESLAB_Leiden/`, each containing a primary `.qmd` file, supporting `images/`, and optional `assets/` overrides. Shared resources sit at the top level: `assets/` for HTML partials, `images/` for cross-talk figures, and `styles.css` for global Reveal.js tweaks. `_quarto.yml` configures the umbrella Quarto site, while `_site/` holds rendered output—never edit files there. `_template_quarto/` stores starter material when creating a new talk. `index.qmd` uses Quarto's native `listing:` to auto-generate the talks index at render time. `collect_unused_assets.py` handles image housekeeping.

## Build, Test, and Development Commands
- `quarto check`: confirm the Quarto CLI and required engines are available.
- `quarto preview`: serve the full site locally with live reload for incremental edits.
- `quarto render <talk>/<talk>.qmd --to revealjs`: build an individual deck into `_site/`.
- `quarto render`: rebuild the entire site after sweeping content changes (auto-runs on push to main via `.github/workflows/publish.yml`).

## Coding Style & Naming Conventions
YAML front matter uses two-space indentation and kebab-case keys; keep metadata blocks compact and alphabetical when practical. Write Markdown with hard wraps at ~100 characters and favor fenced code blocks for math or code chunks. New talk directories should follow the `YY_EventName` pattern and keep file names lowercase with underscores, e.g., `assets/no_footer_on_titleslide.html`. Python utilities follow PEP 8 (4-space indentation, snake_case identifiers) and should include `if __name__ == "__main__":` guards.

## Testing and Git
Testing and commit workflows are handled directly by the repository maintainer.

## Asset Management
Each talk inherits `images/` and `assets/` as symlinks to the shared pools; keep them if you want
centralized reuse, or replace the symlink with a real folder when slides demand bespoke art.

### What NOT to commit
- **PDFs / pptx** — presentation exports. Gitignored. Re-export from `.qmd` source as needed
  (`decktape` commands are in comments at the top of each `.qmd`).
- **`_site/`** — rendered output. Gitignored.
- **`unused_images/`** — images pruned by `collect_unused_assets.py`. Gitignored.

### Meta-work is fine to commit
The repo is public but not sensitive — build scaffolding (speaker notes, per-talk `CLAUDE.md`,
outlines, internal reasoning, felt fiber names) is fine to commit and push; the only bar is genuine PII.

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
`quarto render` on the runner and publishes `_site` as a **Pages artifact**
(`upload-pages-artifact` → `deploy-pages`). The repo's Pages source is `build_type: workflow`
(deploy-from-Actions), **not** deploy-from-branch.

- **Just commit source to `main`.** The Action renders everything — do **not** commit rendered HTML
  or `_site` (gitignored). Only `.qmd` source, the `images/`/`assets/` symlinks, theme files, and any
  figures the deck references need to be tracked.
- **Do NOT run `quarto publish gh-pages`.** It pushes a local build to a `gh-pages` branch that Pages
  ignores (because `build_type` is `workflow`), so it deploys nothing and just leaves orphan clutter.
- **Drafts:** `draft: true` in a talk's front matter keeps it out of the index listing, but the Action
  still renders it and serves it at its direct URL (`.../<talk>/<talk>.html`).
- Live site: <https://cailmdaley.github.io/talks/>
