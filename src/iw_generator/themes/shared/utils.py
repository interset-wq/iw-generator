"""Shared utility functions for all themes."""

from __future__ import annotations

import json
import re

from rich.console import Console

console = Console()


def write_search_index(pages, output_dir):
    """Generate search_index.json for client-side search."""
    search_data = []
    for page in pages:
        # Strip HTML tags for search content
        plain_text = re.sub(r"<[^>]+>", " ", page.html_content)
        plain_text = re.sub(r"\s+", " ", plain_text).strip()

        search_data.append(
            {
                "title": page.title,
                "url": page.url,
                "text": plain_text[:2000],
                "tags": page.tags,
                "category": page.category,
            }
        )

    json_path = output_dir / "search_index.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(search_data, ensure_ascii=False), encoding="utf-8")
    console.print(f"  Written: [cyan]{json_path}[/]")


def sort_pages_by_nav(pages, nav):
    """Sort pages according to navigation order."""
    ordered = []

    def collect_from_nav(items):
        for item in items:
            if "children" in item:
                collect_from_nav(item["children"])
            else:
                # Find matching page
                for page in pages:
                    if page.url == item.get("url"):
                        if page not in ordered:
                            ordered.append(page)
                        break

    collect_from_nav(nav)

    # Add any pages not in nav (fallback to path order)
    for page in pages:
        if page not in ordered:
            ordered.append(page)

    return ordered


def sort_pages_by_date(pages):
    """Sort pages: pinned first (by pin order), then by date (newest first)."""
    pinned = sorted(
        [p for p in pages if p.pin > 0],
        key=lambda p: -p.pin,
    )
    unpinned = sorted(
        [p for p in pages if p.pin == 0],
        key=lambda p: p.date or "0000-00-00",
        reverse=True,
    )
    return pinned + unpinned
