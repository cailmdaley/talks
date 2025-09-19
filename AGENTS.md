# Repository Guidelines

## Project Structure & Module Organization
Slide decks live in date-prefixed directories such as `25_ESLAB_Leiden/`, each containing a primary `.qmd` file, supporting `images/`, and optional `assets/` overrides. Shared resources sit at the top level: `assets/` for HTML partials, `images/` for cross-talk artwork, and `styles.css` for global Reveal.js tweaks. `_quarto.yml` configures the umbrella Quarto site, while `_site/` holds rendered output—never edit files there. `_template_quarto/` stores starter material when creating a new talk. Utility scripts like `generate_index.py` and `collect_unused_assets.py` automate housekeeping.

## Build, Test, and Development Commands
- `quarto check`: confirm the Quarto CLI and required engines are available.
- `quarto preview`: serve the full site locally with live reload for incremental edits.
- `quarto render <talk>/<talk>.qmd --to revealjs`: build an individual deck into `_site/`.
- `quarto render`: rebuild the entire site after sweeping content changes.
- `python generate_index.py`: refresh the static `index.html` list that complements `index.qmd`.

## Coding Style & Naming Conventions
YAML front matter uses two-space indentation and kebab-case keys; keep metadata blocks compact and alphabetical when practical. Write Markdown with hard wraps at ~100 characters and favor fenced code blocks for math or code chunks. New talk directories should follow the `YY_EventName` pattern and keep file names lowercase with underscores, e.g., `assets/no_footer_on_titleslide.html`. Python utilities follow PEP 8 (4-space indentation, snake_case identifiers) and should include `if __name__ == "__main__":` guards.

## Testing Guidelines
Treat every render as a test: run `quarto render` before committing to verify slides, embedded assets, and math typeset correctly. For reveal decks, also open `_site/<talk>/<talk>.html` in a browser and ensure speaker notes (`:::notes`) behave as expected. If exporting PDFs, use the commented `dcktape` commands in each talk after confirming the HTML build. No automated coverage gates exist, so document manual checks in the pull request description.

## Commit & Pull Request Guidelines
Keep commits small and focused with present-tense imperatives (`update reveal footer`, `fix image path`). Reference talk directories in the subject when relevant. Pull requests should outline the talk(s) touched, summarize visual or content changes, list render commands executed, and attach before/after screenshots if the layout changed. Link to any event issue or schedule entry so reviewers understand deadlines and publication expectations.

## Asset Management
Unused shared images accumulate quickly; prefer talk-local `images/` folders unless artwork is reused. Run `python collect_unused_assets.py` selectively (it moves orphaned top-level images into `unused_images/`; review before deleting). Store high-resolution figures under `images/` and downsample only within Quarto to preserve flexibility.
