"""Core path utilities for resolving URLs in templates."""

from __future__ import annotations


def get_base_path(page_slug: str) -> str:
    """Get relative path from a page to site root.

    Examples:
        "" -> "./"           (index page)
        "page" -> "../"      (one level deep)
        "dir/page" -> "../../" (two levels deep)
    """
    depth = len(page_slug.split("/")) if page_slug else 0
    return "../" * depth if depth > 0 else "./"


def resolve_asset(path: str, base_path: str) -> str:
    """Resolve an asset path relative to the current page.

    Examples:
        resolve_asset("assets/style.css", "./") -> "./assets/style.css"
        resolve_asset("assets/style.css", "../") -> "../assets/style.css"
    """
    return f"{base_path}{path}"


def get_page_url(page_slug: str, base_path: str) -> str:
    """Get the URL for a page relative to the current page.

    Examples:
        get_page_url("other-page", "./") -> "./other-page/"
        get_page_url("other-page", "../") -> "../other-page/"
        get_page_url("", "./") -> "./"
    """
    if not page_slug:
        return base_path
    return f"{base_path}{page_slug}/"
