# AGENTS.md

## Project

iw-generator: A general-purpose Markdown static site generator library (PyPI package). Currently in early scaffold stage.

## Setup

```bash
uv sync
```

Requires Python >= 3.11 (built-in `tomllib`). Use local Python for development.

## Key Files

- `PLAN.md` — Full architecture and implementation plan. Read this first for context on intended structure, plugin system, theme system, and build pipeline.
- `temp/` — Reference Gmeek project (the predecessor being refactored from). Ignore for production code.
- `main.py` — Placeholder entry point only.

## Architecture (from PLAN.md)

- Package name: `iw-generator`, import as `iw_generator`
- Config format: TOML (`iw.config.toml`) using Python `tomllib`
- Core engine: `src/iw_generator/core/` — config, engine, file model, markdown, jinja, plugin base
- Built-in plugins: `src/iw_generator/plugins/` — toc, highlight, search, rss, sitemap, blog, docs
- Default theme: `src/iw_generator/themes/iw/`
- CLI: Click-based, registered via `[project.scripts]`
- Plugin discovery: Python entry_points (`iw_generator.plugins`)

## Dependencies (planned)

- markdown-it-py, jinja2, click, rich, pygments
- TOML: stdlib `tomllib` (Python >= 3.11), no fallback needed

## Conventions

- `src/` layout (standard for PyPI packages)
- uv for package management
- hatchling as build backend

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
