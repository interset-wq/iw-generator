"""Code highlight plugin - adds toolbar to code blocks."""

from __future__ import annotations

import re

from pygments.formatters import HtmlFormatter

from ..core.plugin import PluginBase

# Regex to match Pygments-generated code blocks (with or without language class)
CODE_BLOCK_RE = re.compile(
    r'<div class="(?:language-(\w+) )?highlight">\s*<pre[^>]*>(.*?)</pre>\s*</div>',
    re.DOTALL,
)

# Language patterns to detect from code content (fallback only)
_LANG_PATTERNS = [
    (re.compile(r"^\s*#!/bin/(?:ba)?sh", re.MULTILINE), "bash"),
    (re.compile(r"^\s*(?:fn|impl|struct|enum|use\s+\w+::)\s+", re.MULTILINE), "rust"),
    (re.compile(r"^\s*(?:func|package|import\s+\")\s*", re.MULTILINE), "go"),
    (re.compile(r"^\s*(?:def|class|from\s+\w+\s+import)\s+", re.MULTILINE), "python"),
    (re.compile(r"^\s*(?:const|let|var|function|=>)\s+", re.MULTILINE), "javascript"),
    (re.compile(r"^\s*SELECT\s+", re.MULTILINE | re.IGNORECASE), "sql"),
    (re.compile(r"^\s*[.#@][\w-]+\s*[{,:]", re.MULTILINE), "css"),
    (re.compile(r"^\s*\{[\s\S]*:\s*", re.MULTILINE), "json"),
]


def _get_pygments_css() -> str:
    """Generate Pygments CSS for both light and dark themes."""
    # Light theme
    light_fmt = HtmlFormatter(style="default", cssclass="highlight")
    light_css = light_fmt.get_style_defs("")

    # Dark theme
    dark_fmt = HtmlFormatter(style="monokai", cssclass="highlight")
    dark_css = dark_fmt.get_style_defs("")

    # Wrap each theme with proper selectors
    light_lines = light_css.strip().split("\n")
    light_indented = "\n".join("  " + line for line in light_lines)
    light_scoped = (
        """/* Light theme */
[data-color-mode="light"] .highlight,
[data-color-mode="auto"][data-light-theme="light"] .highlight {
"""
        + light_indented
        + "\n}"
    )

    dark_lines = dark_css.strip().split("\n")
    dark_indented = "\n".join("  " + line for line in dark_lines)
    dark_scoped = (
        """/* Dark theme */
[data-color-mode="dark"] .highlight,
[data-color-mode="auto"][data-dark-theme*="dark"] .highlight {
"""
        + dark_indented
        + "\n}"
    )

    return light_scoped + "\n" + dark_scoped


def _detect_language(code: str) -> str:
    """Detect programming language from code content (fallback only)."""
    for pattern, lang in _LANG_PATTERNS:
        if pattern.search(code):
            return lang
    return ""


def _make_toolbar(lang: str) -> str:
    """Generate toolbar HTML for a code block."""
    lang_display = lang.upper() if lang else "CODE"
    copy_icon = (
        '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">'
        '<path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2'
        " .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2z"
        'm0 16H8V7h11v14z"/>'
        "</svg>"
    )
    return (
        '<div class="highlight-tools">'
        f'<span class="code-lang">{lang_display}</span>'
        f'<span class="copy-button" title="Copy code">{copy_icon}</span>'
        "</div>"
    )


def _wrap_code_block(match: re.Match) -> str:
    """Wrap a code block with toolbar."""
    content = match.group(0)
    # Get language from class (group 1) or detect from content
    lang_class = match.group(1)
    if lang_class:
        lang = lang_class
    else:
        # Fallback: detect from code content
        code_match = re.search(r"<code>(.*?)</code>", content, re.DOTALL)
        code = code_match.group(1) if code_match else ""
        code = re.sub(r"<[^>]+>", "", code)
        lang = _detect_language(code)
    toolbar = _make_toolbar(lang)
    return f'<div class="code-block">{toolbar}{content}</div>'


class HighlightPlugin(PluginBase):
    name = "highlight"

    def on_page_render(self, page, html):
        # Add Pygments CSS if not already present
        css = _get_pygments_css()
        if "<style>" in html and ".highlight" not in html:
            # Insert CSS before closing style tag
            html = html.replace("</style>", f"{css}\n</style>", 1)
        elif not html.startswith("<!DOCTYPE"):
            # Prepend CSS for non-full-page HTML
            html = f"<style>{css}</style>\n{html}"

        return CODE_BLOCK_RE.sub(_wrap_code_block, html)
