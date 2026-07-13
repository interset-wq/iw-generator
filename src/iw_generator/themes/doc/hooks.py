"""Doc theme hooks: handles page writing, search index, and nav."""

from __future__ import annotations

import json

from rich.console import Console

from iw_generator.core.jinja import render_template
from iw_generator.core.paths import get_base_path
from iw_generator.themes.icons import get_icon

console = Console()


def write_pages(engine, env, theme_dir):
    """Write all pages for doc theme."""
    # Register doc-theme-specific icon function
    env.globals["get_icon_svg"] = _get_icon_svg

    theme_context = engine._get_theme_context()
    nav = engine._build_nav()
    theme_name = engine.config.theme.name

    # Build flat page list for prev/next navigation
    sorted_pages = _sort_pages_by_nav(engine.site.pages, nav)

    console.print(
        f"Writing [cyan]{len(engine.site.pages)}[/] pages (theme: {theme_name})"
    )

    for i, page in enumerate(sorted_pages):
        page.dest_path.parent.mkdir(parents=True, exist_ok=True)
        # Calculate base_path for relative asset paths
        base_path = get_base_path(page.slug)

        # Get prev/next pages
        prev_page = sorted_pages[i - 1] if i > 0 else None
        next_page = sorted_pages[i + 1] if i < len(sorted_pages) - 1 else None

        html = render_template(
            env,
            "page.html",
            {
                "site": engine.config.site,
                "page": page,
                "content": page.html_content,
                "toc": page.toc_items,
                "nav": nav,
                "config": engine.config,
                "base_path": base_path,
                "prev_page": prev_page,
                "next_page": next_page,
                **theme_context,
            },
        )
        page.dest_path.write_text(html, encoding="utf-8")
        engine._run_plugin_hook("on_page_write", page, html)

    # Generate search index
    _write_search_index(engine)
    search_path = engine.config.output_dir / "search_index.json"
    console.print(f"  Written: [cyan]{search_path}[/]")


def _sort_pages_by_nav(pages, nav):
    """Sort pages according to navigation order."""
    # Build ordered list from nav tree
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


def _get_icon_svg(
    name: str,
    size: int = 24,
    *,
    classes: str = "",
    aria_label: str = "",
) -> str:
    """Get a complete <svg> element for MkDocs Material-style rendering."""
    path_data = get_icon(name)
    if not path_data:
        return ""

    cls_attr = f' class="{classes}"' if classes else ""
    aria_attr = f' aria-label="{aria_label}"' if aria_label else ""

    return (
        f'<svg{cls_attr}{aria_attr} width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="currentColor">'
        f'<path d="{path_data}"/></svg>'
    )


def _write_search_index(engine):
    """Write search_index.json for client-side search."""
    search_data = []
    for page in engine.site.pages:
        # Strip HTML tags for search content
        import re

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

    json_path = engine.config.output_dir / "search_index.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(search_data, ensure_ascii=False), encoding="utf-8")
