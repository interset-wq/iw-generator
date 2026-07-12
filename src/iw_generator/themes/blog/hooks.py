"""Blog theme hooks: handles all blog routes generation."""

from __future__ import annotations

import json
from collections import defaultdict

from rich.console import Console

from iw_generator.core.jinja import render_template

console = Console()


def write_pages(engine, env, theme_dir):
    """Write all pages for blog/iw theme."""
    theme_context = engine._get_theme_context()
    nav = engine._build_nav()
    theme_name = engine.config.theme.name

    console.print(
        f"Writing [cyan]{len(engine.site.pages)}[/] pages (theme: {theme_name})"
    )

    # Write individual post pages
    for page in engine.site.pages:
        page.dest_path.parent.mkdir(parents=True, exist_ok=True)
        html = render_template(
            env,
            "post.html",
            {
                "site": engine.config.site,
                "page": page,
                "content": page.html_content,
                "nav": nav,
                "config": engine.config,
                **theme_context,
            },
        )
        page.dest_path.write_text(html, encoding="utf-8")
        engine._run_plugin_hook("on_page_write", page, html)

    # Generate blog routes
    _write_blog_index(engine, env, theme_context)
    _write_archives(engine, env, theme_context)
    _write_categories(engine, env, theme_context)
    _write_tags_page(engine, env, theme_context)
    _write_post_list_json(engine)


def _write_blog_index(engine, env, theme_context):
    """Write the blog index page."""
    index_path = engine.config.output_dir / "index.html"
    index_path.parent.mkdir(parents=True, exist_ok=True)

    # Sort pages: pinned first, then by date (newest first)
    sorted_pages = _sort_pages(engine.site.pages)

    # Default Gmeek-style tag and year colors
    tag_colors = {
        "软件": "#D93F0B",
        "Gmeek": "#DF0467",
        "日常": "#4F61FC",
        "硬件": "#0E8A16",
    }
    year_colors = {
        "2024": "#bc4c00",
        "2025": "#0969da",
        "2026": "#1f883d",
    }

    html = render_template(
        env,
        "plist.html",
        {
            "site": engine.config.site,
            "pages": sorted_pages,
            "config": engine.config,
            "tag_colors": tag_colors,
            "year_colors": year_colors,
            **theme_context,
        },
    )
    index_path.write_text(html, encoding="utf-8")
    console.print(f"  Written: [cyan]{index_path}[/]")


def _write_archives(engine, env, theme_context):
    """Write the archives page (all posts by year)."""
    archives_path = engine.config.output_dir / "archives.html"
    archives_path.parent.mkdir(parents=True, exist_ok=True)

    # Group pages by year
    pages_by_year: dict[str, list] = defaultdict(list)
    for page in engine.site.pages:
        year = page.date[:4] if page.date else "Unknown"
        pages_by_year[year].append(page)

    # Sort years descending, pages within year by date descending
    sorted_years = sorted(pages_by_year.keys(), reverse=True)
    archives = []
    for year in sorted_years:
        year_pages = sorted(
            pages_by_year[year], key=lambda p: p.date or "", reverse=True
        )
        archives.append({"year": year, "pages": year_pages})

    html = render_template(
        env,
        "archives.html",
        {
            "site": engine.config.site,
            "archives": archives,
            "total_posts": len(engine.site.pages),
            "config": engine.config,
            **theme_context,
        },
    )
    archives_path.write_text(html, encoding="utf-8")
    console.print(f"  Written: [cyan]{archives_path}[/]")


def _write_categories(engine, env, theme_context):
    """Write categories page and individual category pages."""
    # Group pages by category
    pages_by_category: dict[str, list] = defaultdict(list)
    for page in engine.site.pages:
        if page.category:
            pages_by_category[page.category].append(page)

    # Write categories index
    categories_path = engine.config.output_dir / "categories.html"
    categories_path.parent.mkdir(parents=True, exist_ok=True)

    categories = []
    for cat_name in sorted(pages_by_category.keys()):
        cat_pages = _sort_pages(pages_by_category[cat_name])
        categories.append(
            {
                "name": cat_name,
                "pages": cat_pages,
                "count": len(cat_pages),
            }
        )

    html = render_template(
        env,
        "categories.html",
        {
            "site": engine.config.site,
            "categories": categories,
            "config": engine.config,
            **theme_context,
        },
    )
    categories_path.write_text(html, encoding="utf-8")
    console.print(f"  Written: [cyan]{categories_path}[/]")

    # Write individual category pages
    category_dir = engine.config.output_dir / "category"
    for cat_name, cat_pages in pages_by_category.items():
        cat_path = category_dir / f"{cat_name}.html"
        cat_path.parent.mkdir(parents=True, exist_ok=True)

        sorted_pages = _sort_pages(cat_pages)
        html = render_template(
            env,
            "category.html",
            {
                "site": engine.config.site,
                "category": cat_name,
                "pages": sorted_pages,
                "config": engine.config,
                **theme_context,
            },
        )
        cat_path.write_text(html, encoding="utf-8")
    num_cats = len(pages_by_category)
    console.print(f"  Written: [cyan]{category_dir}/[/] ({num_cats} categories)")


def _write_tags_page(engine, env, theme_context):
    """Write tags page and individual tag pages."""
    # Group pages by tag
    pages_by_tag: dict[str, list] = defaultdict(list)
    for page in engine.site.pages:
        for tag in page.tags:
            pages_by_tag[tag].append(page)

    # Write tags index
    tags_path = engine.config.output_dir / "tags.html"
    tags_path.parent.mkdir(parents=True, exist_ok=True)

    tags = []
    for tag_name in sorted(pages_by_tag.keys()):
        tag_pages = _sort_pages(pages_by_tag[tag_name])
        tags.append({"name": tag_name, "pages": tag_pages, "count": len(tag_pages)})

    html = render_template(
        env,
        "tags.html",
        {
            "site": engine.config.site,
            "tags": tags,
            "config": engine.config,
            **theme_context,
        },
    )
    tags_path.write_text(html, encoding="utf-8")
    console.print(f"  Written: [cyan]{tags_path}[/]")

    # Write individual tag pages
    tag_dir = engine.config.output_dir / "tag"
    for tag_name, tag_pages in pages_by_tag.items():
        tag_path = tag_dir / f"{tag_name}.html"
        tag_path.parent.mkdir(parents=True, exist_ok=True)

        sorted_pages = _sort_pages(tag_pages)
        html = render_template(
            env,
            "tag_detail.html",
            {
                "site": engine.config.site,
                "tag": tag_name,
                "pages": sorted_pages,
                "config": engine.config,
                **theme_context,
            },
        )
        tag_path.write_text(html, encoding="utf-8")
    console.print(f"  Written: [cyan]{tag_dir}/[/] ({len(pages_by_tag)} tags)")

    # Keep legacy tag.html for backward compatibility
    _write_legacy_tag_page(engine, env, theme_context, pages_by_tag)


def _write_legacy_tag_page(engine, env, theme_context, pages_by_tag):
    """Write legacy tag.html for backward compatibility."""
    tag_path = engine.config.output_dir / "tag.html"
    tag_path.parent.mkdir(parents=True, exist_ok=True)

    # Build tag data for JS-based filtering (Gmeek compatible)
    post_list = []
    for page in engine.site.pages:
        post_list.append(
            {
                "title": page.title,
                "url": page.url,
                "tags": page.tags,
                "date": page.date,
            }
        )

    html = render_template(
        env,
        "tag.html",
        {
            "site": engine.config.site,
            "pages": post_list,
            "config": engine.config,
            **theme_context,
        },
    )
    tag_path.write_text(html, encoding="utf-8")
    console.print(f"  Written: [cyan]{tag_path}[/]")


def _write_post_list_json(engine):
    """Write postList.json for tag page filtering."""
    json_path = engine.config.output_dir / "postList.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)

    post_list = []
    for page in engine.site.pages:
        post_list.append(
            {
                "title": page.title,
                "url": page.url,
                "tags": page.tags,
                "date": page.date,
            }
        )

    json_path.write_text(json.dumps(post_list, ensure_ascii=False), encoding="utf-8")
    console.print(f"  Written: [cyan]{json_path}[/]")


def _sort_pages(pages: list) -> list:
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
