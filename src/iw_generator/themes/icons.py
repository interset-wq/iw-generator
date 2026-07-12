"""Shared SVG icons for all themes. Loads from icons_cache.json (built from .icons/)."""

from __future__ import annotations

import json
from pathlib import Path

_CACHE_PATH = Path(__file__).parent / "icons_cache.json"
_ICONS: dict[str, str] = {}


def _load_icons() -> dict[str, str]:
    """Load icons from pre-built JSON cache."""
    global _ICONS
    if _ICONS:
        return _ICONS
    if _CACHE_PATH.exists():
        with open(_CACHE_PATH, encoding="utf-8") as f:
            _ICONS = json.load(f)
    return _ICONS


def get_icon(name: str) -> str:
    """Get SVG path data by name (e.g., 'material/home-outline')."""
    return _load_icons().get(name, "")


def get_icon_or_default(name: str, default: str = "material/home-outline") -> str:
    """Get SVG path data by name with fallback."""
    icons = _load_icons()
    return icons.get(name, icons.get(default, ""))
