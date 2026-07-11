"""Search index plugin (generates JSON index for client-side search)."""

from __future__ import annotations

import json

from ..core.file import Site
from ..core.plugin import PluginBase


class SearchPlugin(PluginBase):
    name = "search"

    def on_site_build_done(self, site: Site) -> None:
        index = []
        for page in site.pages:
            index.append(
                {
                    "title": page.title,
                    "url": page.url,
                    "content": page.raw_content[:500],
                }
            )

        out_dir = self.config.output_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        search_file = out_dir / "search_index.json"
        search_file.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
