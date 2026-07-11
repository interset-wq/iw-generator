"""File and Page data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Page:
    """Represents a single Markdown page in the site."""

    source_path: Path
    dest_path: Path
    content_dir: Path
    title: str = ""
    date: str = ""
    tags: list[str] = field(default_factory=list)
    frontmatter: dict = field(default_factory=dict)
    raw_content: str = ""
    html_content: str = ""

    @property
    def slug(self) -> str:
        """URL-friendly slug derived from relative path."""
        rel = self.source_path.relative_to(self.content_dir)
        parts = list(rel.with_suffix("").parts)
        if parts[-1] == "index":
            parts = parts[:-1]
        return "/".join(parts) if parts else ""

    @property
    def url(self) -> str:
        slug = self.slug
        return f"/{slug}/" if slug else "/"

    @property
    def relative_path(self) -> str:
        return str(self.source_path.relative_to(self.content_dir))


@dataclass
class Site:
    """Collection of all pages in the site."""

    pages: list[Page] = field(default_factory=list)

    def get_page(self, slug: str) -> Page | None:
        for page in self.pages:
            if page.slug == slug:
                return page
        return None

    def get_pages_by_tag(self, tag: str) -> list[Page]:
        return [p for p in self.pages if tag in p.tags]

    def all_tags(self) -> dict[str, int]:
        tags: dict[str, int] = {}
        for page in self.pages:
            for tag in page.tags:
                tags[tag] = tags.get(tag, 0) + 1
        return dict(sorted(tags.items(), key=lambda x: -x[1]))
