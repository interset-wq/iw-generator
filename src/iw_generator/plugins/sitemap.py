"""Sitemap.xml generation plugin."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from ..core.file import Site
from ..core.plugin import PluginBase


class SitemapPlugin(PluginBase):
    name = "sitemap"

    def on_site_build_done(self, site: Site) -> None:
        urlset = ET.Element(
            "urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        )

        for page in site.pages:
            url_el = ET.SubElement(urlset, "url")
            ET.SubElement(url_el, "loc").text = f"{self.config.site.url}{page.url}"
            if page.date:
                ET.SubElement(url_el, "lastmod").text = page.date

        tree = ET.ElementTree(urlset)
        out_file = self.config.output_dir / "sitemap.xml"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        tree.write(out_file, encoding="unicode", xml_declaration=True)
