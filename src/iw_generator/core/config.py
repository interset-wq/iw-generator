"""TOML configuration loading and validation."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_FILE = "iw.config.toml"

DEFAULT_CONFIG = {
    "site": {
        "name": "My Site",
        "url": "",
        "description": "",
    },
    "paths": {
        "content": "content",
        "output": "site",
        "static": "static",
    },
    "theme": {
        "name": "iw",
        "custom_dir": "",
        "palette": {"default": "light", "toggle": True},
        "font": {"text": "", "code": ""},
    },
    "plugins": {
        "enable": [],
    },
    "markdown": {
        "highlight_theme": "monokai",
    },
}


@dataclass
class SiteConfig:
    name: str = "My Site"
    url: str = ""
    description: str = ""


@dataclass
class PathsConfig:
    content: str = "content"
    output: str = "site"
    static: str = "static"


@dataclass
class ThemePaletteConfig:
    default: str = "light"
    toggle: bool = True


@dataclass
class ThemeFontConfig:
    text: str = ""
    code: str = ""


@dataclass
class ThemeConfig:
    name: str = "iw"
    custom_dir: str = ""
    palette: ThemePaletteConfig = field(default_factory=ThemePaletteConfig)
    font: ThemeFontConfig = field(default_factory=ThemeFontConfig)


@dataclass
class PluginsConfig:
    enable: list[str] = field(default_factory=list)


@dataclass
class MarkdownConfig:
    highlight_theme: str = "monokai"


@dataclass
class Config:
    site: SiteConfig = field(default_factory=SiteConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    theme: ThemeConfig = field(default_factory=ThemeConfig)
    plugins: PluginsConfig = field(default_factory=PluginsConfig)
    markdown: MarkdownConfig = field(default_factory=MarkdownConfig)
    _raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def load(cls, config_path: Path | str | None = None) -> Config:
        """Load config from TOML file, merging with defaults."""
        path = _resolve_config_path(config_path)
        raw = _read_toml(path) if path else {}
        return cls._from_dict(raw)

    @classmethod
    def _from_dict(cls, data: dict) -> Config:
        """Build Config from a raw dict, merging with defaults."""
        merged = _deep_merge(DEFAULT_CONFIG, data)
        return cls(
            site=SiteConfig(**merged.get("site", {})),
            paths=PathsConfig(**merged.get("paths", {})),
            theme=ThemeConfig(
                name=merged["theme"].get("name", "iw"),
                custom_dir=merged["theme"].get("custom_dir", ""),
                palette=ThemePaletteConfig(**merged["theme"].get("palette", {})),
                font=ThemeFontConfig(**merged["theme"].get("font", {})),
            ),
            plugins=PluginsConfig(**merged.get("plugins", {})),
            markdown=MarkdownConfig(**merged.get("markdown", {})),
            _raw=merged,
        )

    @property
    def content_dir(self) -> Path:
        return Path(self.paths.content)

    @property
    def output_dir(self) -> Path:
        return Path(self.paths.output)

    @property
    def static_dir(self) -> Path:
        return Path(self.paths.static)


def _resolve_config_path(config_path: Path | str | None) -> Path | None:
    if config_path is not None:
        p = Path(config_path)
        return p if p.exists() else None
    cwd = Path.cwd()
    candidate = cwd / CONFIG_FILE
    return candidate if candidate.exists() else None


def _read_toml(path: Path) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def _deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
