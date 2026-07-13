"""Shared icon rendering for all themes."""

from __future__ import annotations

from ..icons import get_icon


def get_icon_svg(
    name: str,
    size: int = 24,
    *,
    classes: str = "",
    aria_label: str = "",
) -> str:
    """Get a complete <svg> element for the given icon name.

    Returns a full SVG tag with the icon path data embedded.
    Compatible with all themes.

    Args:
        name: Icon name (e.g., 'material/home', 'simple/github')
        size: Icon size in pixels
        classes: Optional CSS classes
        aria_label: Optional aria label for accessibility
    """
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
