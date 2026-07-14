"""Blog theme hooks: handles all blog routes generation."""

from __future__ import annotations

import json
from collections import defaultdict

from rich.console import Console

from iw_generator.core.jinja import render_template
from iw_generator.core.paths import get_base_path
from iw_generator.themes.shared.utils import sort_pages_by_date, write_search_index

console = Console()


def write_pages(engine, env, theme_dir):
    """Write all pages for blog/iw theme."""
    theme_context = engine._get_theme_context()
    nav = engine._build_nav()
    theme_name = engine.config.theme.name

    console.print(
        f"Writing [cyan]{len(engine.site.pages)}[/] pages (theme: {theme_name})"
    )

    # Build sorted page list for prev/next navigation
    sorted_pages = sort_pages_by_date(engine.site.pages)

    # Write individual post pages (skip index.md - it's the homepage)
    for i, page in enumerate(sorted_pages):
        if page.source_path.name == "index.md":
            continue

        # Get prev/next pages
        prev_page = sorted_pages[i - 1] if i > 0 else None
        next_page = sorted_pages[i + 1] if i < len(sorted_pages) - 1 else None

        # Skip index.md for prev/next
        while prev_page and prev_page.source_path.name == "index.md":
            i -= 1
            prev_page = sorted_pages[i - 1] if i > 0 else None
        while next_page and next_page.source_path.name == "index.md":
            next_page_index = sorted_pages.index(next_page)
            next_page = (
                sorted_pages[next_page_index + 1]
                if next_page_index < len(sorted_pages) - 1
                else None
            )

        page.dest_path.parent.mkdir(parents=True, exist_ok=True)
        base_path = get_base_path(page.slug)
        html = render_template(
            env,
            "post.html",
            {
                "site": engine.config.site,
                "page": page,
                "content": page.html_content,
                "nav": nav,
                "prev_page": prev_page,
                "next_page": next_page,
                "config": engine.config,
                "base_path": base_path,
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
    _write_about_page(engine, env, theme_context)
    _write_search_page(engine, env, theme_context)
    _write_post_list_json(engine)

    # Generate search index using shared utility
    write_search_index(engine.site.pages, engine.config.output_dir)


def _write_blog_index(engine, env, theme_context):
    """Write the blog index page."""
    index_path = engine.config.output_dir / "index.html"
    index_path.parent.mkdir(parents=True, exist_ok=True)

    # Build hierarchical navigation tree
    nav_tree = _build_nav_tree(engine.site.pages)

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
            "nav_items": nav_tree,
            "config": engine.config,
            "base_path": "./",
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
            "base_path": "./",
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
        cat_pages = sort_pages_by_date(pages_by_category[cat_name])
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
            "base_path": "./",
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

        sorted_pages = sort_pages_by_date(cat_pages)
        html = render_template(
            env,
            "category.html",
            {
                "site": engine.config.site,
                "category": cat_name,
                "pages": sorted_pages,
                "config": engine.config,
                "base_path": "../",
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
        tag_pages = sort_pages_by_date(pages_by_tag[tag_name])
        tags.append({"name": tag_name, "pages": tag_pages, "count": len(tag_pages)})

    html = render_template(
        env,
        "tags.html",
        {
            "site": engine.config.site,
            "tags": tags,
            "config": engine.config,
            "base_path": "./",
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

        sorted_pages = sort_pages_by_date(tag_pages)
        html = render_template(
            env,
            "tag_detail.html",
            {
                "site": engine.config.site,
                "tag": tag_name,
                "pages": sorted_pages,
                "config": engine.config,
                "base_path": "../",
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
            "base_path": "./",
            **theme_context,
        },
    )
    tag_path.write_text(html, encoding="utf-8")
    console.print(f"  Written: [cyan]{tag_path}[/]")


def _write_about_page(engine, env, theme_context):
    """Write the about page if docs/about.md exists."""
    # Find the about page in the site pages
    about_page = None
    for page in engine.site.pages:
        if page.source_path.name == "about.md":
            about_page = page
            break

    if not about_page:
        # Create a default about page if no about.md exists
        return

    about_path = engine.config.output_dir / "about" / "index.html"
    about_path.parent.mkdir(parents=True, exist_ok=True)

    html = render_template(
        env,
        "about.html",
        {
            "site": engine.config.site,
            "page": about_page,
            "content": about_page.html_content,
            "config": engine.config,
            "base_path": "../",
            **theme_context,
        },
    )
    about_path.write_text(html, encoding="utf-8")
    console.print(f"  Written: [cyan]{about_path}[/]")


def _write_search_page(engine, env, theme_context):
    """Write the search page."""
    search_path = engine.config.output_dir / "search.html"
    search_path.parent.mkdir(parents=True, exist_ok=True)

    html = render_template(
        env,
        "search.html",
        {
            "site": engine.config.site,
            "config": engine.config,
            "base_path": "./",
            **theme_context,
        },
    )
    search_path.write_text(html, encoding="utf-8")
    console.print(f"  Written: [cyan]{search_path}[/]")


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


def _build_nav_tree(pages: list) -> list:
    """Build hierarchical navigation tree from pages."""
    # Group pages by their parent directory
    tree = {}

    for page in pages:
        # Get relative path from content dir
        rel_path = page.source_path.relative_to(page.content_dir)
        parts = rel_path.parts[:-1]  # Directory parts (excluding filename)

        # Build tree structure
        current_level = tree
        for part in parts:
            if part not in current_level:
                current_level[part] = {"_pages": [], "_children": {}}
            current_level = current_level[part]["_children"]

        # Add page to current level
        current_level.setdefault("_pages", []).append(page)

    # Convert tree to list format for template
    def tree_to_list(tree_level):
        items = []

        # First add directory entries (as section headers)
        for dir_name, dir_data in sorted(tree_level.items()):
            if dir_name.startswith("_"):
                continue

            # Find if there's an index page for this directory
            index_page = None
            for page in dir_data.get("_pages", []):
                if page.source_path.name == "index.md":
                    index_page = page
                    break

            # Create directory item
            dir_item = {
                "title": dir_name.replace("-", " ").replace("_", " ").title(),
                "url": index_page.url if index_page else f"/{dir_name}/",
                "children": tree_to_list(dir_data["_children"]),
                "icon": "material/folder-outline",
            }

            # Add index page metadata if it exists
            if index_page:
                dir_item["category"] = index_page.category
                dir_item["tags"] = index_page.tags
                dir_item["date"] = index_page.date
                dir_item["pin"] = index_page.pin

            items.append(dir_item)

        # Then add pages in this directory
        for page in sorted(
            tree_level.get("_pages", []),
            key=lambda p: (-p.pin, p.date or "0000-00-00"),
            reverse=True,
        ):
            if page.source_path.name == "index.md":
                continue  # Skip index pages, they're directory headers

            items.append(
                {
                    "title": page.title,
                    "url": page.url,
                    "category": page.category,
                    "tags": page.tags,
                    "date": page.date,
                    "pin": page.pin,
                    "icon": "material/article-outline"
                    if page.pin == 0
                    else "material/push-pin",
                }
            )

        return items

    return tree_to_list(tree)
