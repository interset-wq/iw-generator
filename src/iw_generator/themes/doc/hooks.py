"""Doc theme hooks: handles page writing, search index, and nav."""

from __future__ import annotations

from iw_generator.core.jinja import render_template
from iw_generator.core.paths import get_base_path
from iw_generator.themes.shared.utils import sort_pages_by_nav, write_search_index


def write_pages(engine, env, theme_dir):
    """Write all pages for doc theme."""
    theme_context = engine._get_theme_context()
    nav = engine._build_nav()
    theme_name = engine.config.theme.name

    # Build flat page list for prev/next navigation
    sorted_pages = sort_pages_by_nav(engine.site.pages, nav)

    print(f"  Writing {len(engine.site.pages)} pages (theme: {theme_name})")

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

    # Generate search index using shared utility
    write_search_index(engine.site.pages, engine.config.output_dir)
