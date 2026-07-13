"""Markdown to HTML rendering with frontmatter parsing."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import markdown
from pymdownx import emoji


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML (---) or TOML (+++) frontmatter from markdown content."""
    content = content.lstrip("\ufeff")

    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            raw_fm = content[3:end].strip()
            body = content[end + 3 :].lstrip("\n")
            return _parse_yaml_fm(raw_fm), body

    if content.startswith("+++"):
        end = content.find("+++", 3)
        if end != -1:
            raw_fm = content[3:end].strip()
            body = content[end + 3 :].lstrip("\n")
            return _parse_toml_fm(raw_fm), body

    return {}, content


def _parse_yaml_fm(raw: str) -> dict:
    result: dict = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
                value = value[1:-1]
            if value.startswith("[") and value.endswith("]"):
                inner = value[1:-1]
                value = [v.strip().strip("\"'") for v in inner.split(",") if v.strip()]
            elif value.lower() in ("true", "false"):
                value = value.lower() == "true"
            result[key] = value
    return result


def _parse_toml_fm(raw: str) -> dict:
    return tomllib.loads(raw)


def slugify(text: str) -> str:
    """Convert text to URL-safe slug. Handles CJK characters by converting to hex."""
    text = text.strip().lower()
    # Replace spaces and underscores with hyphens
    text = re.sub(r"[\s_]+", "-", text)
    # Keep ASCII alphanumeric, hyphens, and dots
    result = []
    for char in text:
        if char.isascii() and (char.isalnum() or char in "-."):
            result.append(char)
        elif not char.isascii():
            # Convert non-ASCII (CJK etc.) to hex
            encoded = char.encode("utf-8").hex()
            result.append(f"-{encoded}-")
    slug = "".join(result)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def create_markdown_instance() -> markdown.Markdown:
    """Create a Markdown instance with pymdown-extensions."""
    md = markdown.Markdown(
        extensions=[
            "pymdownx.highlight",
            "pymdownx.superfences",
            "pymdownx.tabbed",
            "pymdownx.tasklist",
            "pymdownx.details",
            "pymdownx.emoji",
            "pymdownx.smartsymbols",
            "pymdownx.mark",
            "pymdownx.critic",
            "pymdownx.striphtml",
            "pymdownx.saneheaders",
            "toc",
            "tables",
            "attr_list",
            "md_in_html",
            "def_list",
            "footnotes",
            "abbr",
        ],
        extension_configs={
            "pymdownx.highlight": {
                "linenums": False,
                "css_class": "highlight",
                "use_pygments": True,
                "pygments_style": "monokai",
                "pygments_lang_class": True,
            },
            "pymdownx.superfences": {
                "css_class": "highlight",
            },
            "pymdownx.tabbed": {
                "alternate_style": True,
            },
            "toc": {
                "permalink": False,
            },
            "pymdownx.emoji": {
                "emoji_index": emoji.twemoji,
                "emoji_generator": emoji.to_svg,
            },
        },
    )
    return md


class MarkdownRenderer:
    """Renders markdown files to HTML with frontmatter extraction."""

    def __init__(self) -> None:
        self.md = create_markdown_instance()

    def render_file(self, path: Path) -> tuple[dict, str, list[dict]]:
        raw = path.read_text(encoding="utf-8")
        return self.render_string(raw)

    def render_string(self, raw: str) -> tuple[dict, str, list[dict]]:
        frontmatter, body = _parse_frontmatter(raw)
        self.md.reset()
        html = self.md.convert(body)

        # Extract TOC tokens (structured data for sidebar)
        toc_items = []
        if hasattr(self.md, "toc_tokens"):
            toc_items = _flatten_toc_tokens(self.md.toc_tokens)

        return frontmatter, html, toc_items


def _flatten_toc_tokens(tokens: list[dict], level: int = 1) -> list[dict]:
    """Flatten TOC tokens into a flat list with level info."""
    items = []
    for token in tokens:
        items.append(
            {
                "id": token.get("id", ""),
                "title": token.get("name", ""),
                "level": level,
            }
        )
        children = token.get("children", [])
        if children:
            items.extend(_flatten_toc_tokens(children, level + 1))
    return items
