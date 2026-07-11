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

- **禁止** `git add .` 或 `git add -A`，必须指定具体文件：`git add xxx.py`
- 原子化提交：一个 commit 只做一件事，commit 信息必须与实际修改对应
- 例如添加了测试 → `git add tests/` + `git commit -m "test: add xxx tests"`
- 例如修改了配置 → `git add pyproject.toml` + `git commit -m "chore: update config"`

## Code Quality

- 使用 **ruff** 进行代码检查和格式化
- 提交前运行：`ruff check src/` 和 `ruff format src/`
- 规则：E, F, I, W, UP, B, SIM
