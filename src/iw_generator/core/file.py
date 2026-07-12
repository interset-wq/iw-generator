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
    _slug: str = field(default="", repr=False)

    def __post_init__(self):
        if not self._slug:
            # Generate slug from dest_path
            # e.g., /path/to/site/page/index.html -> /page
            try:
                rel = self.dest_path.parent.relative_to(self.dest_path.parents[1])
                self._slug = "/" + str(rel).replace("\\", "/")
            except (ValueError, IndexError):
                self._slug = ""

    @property
    def slug(self) -> str:
        return self._slug

    @property
    def url(self) -> str:
        return f"{self.slug}/" if self.slug else "/"

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
