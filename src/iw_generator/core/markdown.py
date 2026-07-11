"""Markdown to HTML rendering with frontmatter parsing."""

from __future__ import annotations

import tomllib
from pathlib import Path

from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML (---) or TOML (+++) frontmatter from markdown content."""
    content = content.lstrip("\ufeff")

    # YAML frontmatter: ---
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            raw_fm = content[3:end].strip()
            body = content[end + 3 :].lstrip("\n")
            return _parse_yaml_fm(raw_fm), body

    # TOML frontmatter: +++
    if content.startswith("+++"):
        end = content.find("+++", 3)
        if end != -1:
            raw_fm = content[3:end].strip()
            body = content[end + 3 :].lstrip("\n")
            return _parse_toml_fm(raw_fm), body

    return {}, content


def _parse_yaml_fm(raw: str) -> dict:
    """Minimal YAML frontmatter parser for simple key-value pairs."""
    result: dict = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            # Remove surrounding quotes
            if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
                value = value[1:-1]
            # Parse lists: [a, b, c]
            if value.startswith("[") and value.endswith("]"):
                inner = value[1:-1]
                value = [v.strip().strip("\"'") for v in inner.split(",") if v.strip()]
            # Parse booleans
            elif value.lower() in ("true", "false"):
                value = value.lower() == "true"
            result[key] = value
    return result


def _parse_toml_fm(raw: str) -> dict:
    """Parse TOML frontmatter."""
    return tomllib.loads(raw)


def _highlight_code(code: str, lang: str) -> str:
    """Highlight code with Pygments."""
    try:
        lexer = get_lexer_by_name(lang)
    except Exception:
        lexer = TextLexer()
    formatter = HtmlFormatter(cssclass="highlight", wrapcode=True)
    return highlight(code, lexer, formatter)


def create_markdown_parser() -> MarkdownIt:
    """Create a markdown-it-py parser with common extensions."""
    md = MarkdownIt().enable("table").enable("strikethrough")

    # Custom fence renderer for code highlighting
    def fence_highlight(tokens, idx, options, env):
        token = tokens[idx]
        info = token.info.strip() if token.info else ""
        lang = info.split(None, 1)[0] if info else ""
        code = token.content
        if lang:
            return f'<pre class="language-{lang}">{_highlight_code(code, lang)}</pre>\n'
        return f"<pre><code>{code}</code></pre>\n"

    md.renderer.rules["fence"] = fence_highlight
    return md


class MarkdownRenderer:
    """Renders markdown files to HTML with frontmatter extraction."""

    def __init__(self) -> None:
        self.md = create_markdown_parser()

    def render_file(self, path: Path) -> tuple[dict, str]:
        """Render a markdown file, returning (frontmatter, html)."""
        raw = path.read_text(encoding="utf-8")
        return self.render_string(raw)

    def render_string(self, raw: str) -> tuple[dict, str]:
        """Render a markdown string, returning (frontmatter, html)."""
        frontmatter, body = _parse_frontmatter(raw)
        html = self.md.render(body)
        return frontmatter, html
