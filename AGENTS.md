# AGENTS.md

## Project

iw-generator: A general-purpose Markdown static site generator library (PyPI package) with a default `iw` theme supporting docs mode (MkDocs Material-like) and blog mode (Gmeek-like).

## Setup

```bash
uv sync
```

Requires Python >= 3.11 (built-in `tomllib`). Use local Python for development.

## Key Files

- `PLAN.md` — Full architecture and implementation plan. Read this first for context on intended structure, plugin system, theme system, and build pipeline.
- `docs/CSS_CONVENTION.md` — CSS naming conventions and design tokens. **Must read before any CSS work.**
- `temp/material/` — Cloned MkDocs Material repo for CSS/SCSS reference
- `main.py` — Placeholder entry point only.

## Architecture (from PLAN.md)

- Package name: `iw-generator`, import as `iw_generator`
- Config format: TOML (`iw.config.toml`) using Python `tomllib`
- Core engine: `src/iw_generator/core/` — config, engine, file model, markdown, jinja, plugin base
- Built-in plugins: `src/iw_generator/plugins/` — toc, highlight, search, rss, sitemap, blog, docs
- Default theme: `src/iw_generator/themes/blog/`
- Shared components: `src/iw_generator/themes/shared/` — CSS, JS, templates shared across themes
- CLI: Click-based, registered via `[project.scripts]`
- Plugin discovery: Python entry_points (`iw_generator.plugins`)

## Dependencies

- markdown, pymdown-extensions, jinja2, click, rich, pygments, beautifulsoup4
- TOML: stdlib `tomllib` (Python >= 3.11), no fallback needed

## Conventions

- `src/` layout (standard for PyPI packages)
- uv for package management
- hatchling as build backend
- English only for AGENTS.md and code comments

## Git Rules

- Never use `git add .` or `git add -A`. Always specify files: `git add xxx.py`
- Atomic commits: one commit = one logical change. Commit message must match actual change.
- Use conventional commits with scope: `feat(core): add config loader`, `feat(plugins): add toc plugin`
- Common scopes: `core`, `cli`, `plugins`, `themes`, `docs`, `tests`
- Example: added tests -> `git add tests/` + `git commit -m "test(core): add config tests"`
- Example: changed config -> `git add pyproject.toml` + `git commit -m "chore: update pyproject.toml"`

## Code Quality

- Use **ruff** for linting and formatting
- Run before committing: `ruff check src/` and `ruff format src/`
- Rules: E, F, I, W, UP, B, SIM
- Pre-commit hooks configured: ruff check + ruff format run automatically
