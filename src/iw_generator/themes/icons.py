"""Shared SVG icons for all themes. Loads from icons.json."""

from __future__ import annotations

import json
from pathlib import Path

_ICONS_PATH = Path(__file__).parent / "icons.json"
ICONS: dict[str, str] = {}


def _load_icons() -> dict[str, str]:
    """Load icons from JSON file."""
    if not ICONS:
        with open(_ICONS_PATH, encoding="utf-8") as f:
            ICONS.update(json.load(f))
    return ICONS


def get_icon(name: str) -> str:
    """Get SVG icon by name.

    Args:
        name: Icon name in format "provider/name" (e.g., "material/menu")

    Returns:
        SVG string or empty string if not found
    """
    return _load_icons().get(name, "")


def get_icon_or_default(name: str, default: str = "material/school") -> str:
    """Get SVG icon by name with fallback to default.

    Args:
        name: Icon name in format "provider/name"
        default: Default icon name to use if requested icon not found

    Returns:
        SVG string
    """
    icons = _load_icons()
    return icons.get(name, icons.get(default, ""))
