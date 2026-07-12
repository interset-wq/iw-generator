"""Build icons_cache.json from .icons directory."""

import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

ICONS_DIR = Path("src/iw_generator/themes/.icons")
CACHE_FILE = Path("src/iw_generator/themes/icons_cache.json")


def extract_svg_path(svg_content: str) -> str:
    """Extract the d attribute from SVG path elements."""
    try:
        root = ET.fromstring(svg_content)
        paths = []
        for path in root.findall(".//{http://www.w3.org/2000/svg}path"):
            d = path.get("d")
            if d:
                paths.append(d)
        if not paths:
            for path in root.findall(".//path"):
                d = path.get("d")
                if d:
                    paths.append(d)
        return " ".join(paths) if paths else ""
    except ET.ParseError:
        pattern = r'd="([^"]+)"'
        matches = re.findall(pattern, svg_content)
        return " ".join(matches) if matches else ""


def build_cache():
    icons = {}
    for svg_file in ICONS_DIR.rglob("*.svg"):
        rel_path = svg_file.relative_to(ICONS_DIR)
        icon_name = str(rel_path.with_suffix("")).replace("\\", "/")
        svg_content = svg_file.read_text(encoding="utf-8")
        path_data = extract_svg_path(svg_content)
        if path_data:
            icons[icon_name] = path_data

    CACHE_FILE.write_text(json.dumps(icons, ensure_ascii=False), encoding="utf-8")
    print(f"Built icon cache: {len(icons)} icons -> {CACHE_FILE}")


if __name__ == "__main__":
    build_cache()
