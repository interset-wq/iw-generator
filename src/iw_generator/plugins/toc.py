"""TOC (Table of Contents) plugin."""

from __future__ import annotations

import re

from ..core.config import Config
from ..core.file import Page
from ..core.plugin import PluginBase


class TocPlugin(PluginBase):
    name = "toc"

    def __init__(self, config: Config) -> None:
        super().__init__(config)

    def on_page_render(self, page: Page, html: str) -> str:
        toc, html_with_ids = self._generate_toc(html)
        page.frontmatter["_toc"] = toc
        return html_with_ids

    def _generate_toc(self, html: str) -> tuple[str, str]:
        """Extract headings and generate TOC HTML."""
        heading_re = re.compile(r"<(h[1-6])(?:\s[^>]*)?>(.*?)</\1>", re.IGNORECASE)
        headings = []
        counter = 0

        def make_id(match):
            nonlocal counter
            tag = match.group(1)
            content = match.group(2)
            # Strip HTML tags from heading text
            text = re.sub(r"<[^>]+>", "", content).strip()
            slug = re.sub(r"[^\w\s-]", "", text.lower())
            slug = re.sub(r"[\s]+", "-", slug).strip("-")
            counter += 1
            heading_id = f"{slug}-{counter}" if counter > 1 else slug
            headings.append((int(tag[1]), text, heading_id))
            return f'<{tag} id="{heading_id}">{content}</{tag}>'

        html_with_ids = heading_re.sub(make_id, html)

        if not headings:
            return "", html_with_ids

        # Build TOC
        toc_lines = ['<nav class="toc">', "<ul>"]
        prev_level = headings[0][0]
        for level, text, hid in headings:
            if level > prev_level:
                toc_lines.append("<ul>")
            elif level < prev_level:
                toc_lines.append("</ul>")
            toc_lines.append(f'<li><a href="#{hid}">{text}</a></li>')
            prev_level = level
        toc_lines.append("</ul></nav>")
        toc_html = "\n".join(toc_lines)

        return toc_html, html_with_ids
