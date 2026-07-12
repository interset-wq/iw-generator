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
    category: str = ""
    pin: int = 0  # Pin order (0 = not pinned, higher = more pinned)
    description: str = ""
    image: str = ""  # Cover image for og:image
    frontmatter: dict = field(default_factory=dict)
    raw_content: str = ""
    html_content: str = ""
    comments_count: int = 0  # For blog theme (from GitHub Issues)
    _slug: str = field(default="", repr=False)

    def __post_init__(self):
        if not self._slug:
            # Generate slug from dest_path
            # e.g., site/docs/guide.html -> docs/guide
            # e.g., site/index.html -> ""
            # e.g., site/post/foo.html -> post/foo
            try:
                parts = self.dest_path.with_suffix("").parts
                # Remove the output dir (first part) and handle index
                if len(parts) <= 1:
                    self._slug = ""
                elif parts[-1] == "index":
                    # e.g., ("site", "docs", "index") -> "docs"
                    self._slug = "/".join(parts[1:-1])
                else:
                    self._slug = "/".join(parts[1:])
            except (ValueError, IndexError):
                self._slug = ""

    @property
    def slug(self) -> str:
        return self._slug

    @property
    def url(self) -> str:
        return f"/{self.slug}/" if self.slug else "/"

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
