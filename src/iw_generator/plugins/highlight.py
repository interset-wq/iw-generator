"""Code highlight plugin (Pygments CSS injection)."""

from __future__ import annotations

from ..core.plugin import PluginBase


class HighlightPlugin(PluginBase):
    name = "highlight"

    def on_page_render(self, page, html):
        # Pygments CSS is already handled by markdown.py fence renderer
        # This plugin can be extended to inject theme-specific CSS
        return html
