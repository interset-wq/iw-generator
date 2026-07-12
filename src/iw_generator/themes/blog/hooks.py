"""Blog theme hooks: handles post list, tag page, and post list JSON generation."""

from __future__ import annotations

import json

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

    # Generate blog index, tag page, and post list JSON
    _write_blog_index(engine, env, theme_context)
    _write_tag_page(engine, env, theme_context)
    _write_post_list_json(engine)


def _write_blog_index(engine, env, theme_context):
    """Write the blog index page."""
    index_path = engine.config.output_dir / "index.html"
    index_path.parent.mkdir(parents=True, exist_ok=True)

    # Sort pages by date (newest first)
    sorted_pages = sorted(
        engine.site.pages,
        key=lambda p: p.date or "0000-00-00",
        reverse=True,
    )

    html = render_template(
        env,
        "plist.html",
        {
            "site": engine.config.site,
            "pages": sorted_pages,
            "config": engine.config,
            **theme_context,
        },
    )
    index_path.write_text(html, encoding="utf-8")
    console.print(f"  Written: [cyan]{index_path}[/]")


def _write_tag_page(engine, env, theme_context):
    """Write the tag page."""
    tag_path = engine.config.output_dir / "tag.html"
    tag_path.parent.mkdir(parents=True, exist_ok=True)

    html = render_template(
        env,
        "tag.html",
        {
            "site": engine.config.site,
            "pages": [
                {
                    "title": p.title,
                    "url": p.url,
                    "tags": p.tags,
                    "date": p.date,
                }
                for p in engine.site.pages
            ],
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
