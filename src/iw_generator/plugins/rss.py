"""RSS feed generation plugin."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from ..core.file import Site
from ..core.plugin import PluginBase


class RssPlugin(PluginBase):
    name = "rss"

    def on_site_build_done(self, site: Site) -> None:
        if not site.pages:
            return

        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")
        ET.SubElement(channel, "title").text = self.config.site.name
        ET.SubElement(channel, "link").text = self.config.site.url
        ET.SubElement(channel, "description").text = self.config.site.description

        for page in sorted(site.pages, key=lambda p: p.date, reverse=True)[:20]:
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = page.title
            ET.SubElement(item, "link").text = f"{self.config.site.url}{page.url}"
            ET.SubElement(item, "description").text = page.raw_content[:300]

        tree = ET.ElementTree(rss)
        out_file = self.config.output_dir / "rss.xml"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        tree.write(out_file, encoding="unicode", xml_declaration=True)
