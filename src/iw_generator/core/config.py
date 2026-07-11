"""TOML configuration loading and validation with Pydantic."""

from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel, Field

CONFIG_FILE = "iw.config.toml"


class SiteSettings(BaseModel):
    name: str = "My Site"
    url: str = ""
    description: str = ""


class PathsSettings(BaseModel):
    content: str = "content"
    output: str = "site"
    static: str = "static"


class ThemePaletteSettings(BaseModel):
    default: str = "light"
    toggle: bool = True


class ThemeFontSettings(BaseModel):
    text: str = ""
    code: str = ""


class ThemeSettings(BaseModel):
    name: str = "iw"
    custom_dir: str = ""
    mode: str = "docs"  # "docs" or "blog"
    palette: ThemePaletteSettings = Field(default_factory=ThemePaletteSettings)
    font: ThemeFontSettings = Field(default_factory=ThemeFontSettings)


class PluginsSettings(BaseModel):
    enable: list[str] = Field(default_factory=list)


class MarkdownSettings(BaseModel):
    highlight_theme: str = "monokai"


class Config(BaseModel):
    site: SiteSettings = Field(default_factory=SiteSettings)
    paths: PathsSettings = Field(default_factory=PathsSettings)
    theme: ThemeSettings = Field(default_factory=ThemeSettings)
    plugins: PluginsSettings = Field(default_factory=PluginsSettings)
    markdown: MarkdownSettings = Field(default_factory=MarkdownSettings)

    @classmethod
    def load(cls, config_path: Path | str | None = None) -> Config:
        """Load config from TOML file, merging with defaults."""
        path = _resolve_config_path(config_path)
        raw = _read_toml(path) if path else {}
        return cls.model_validate(raw)

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
