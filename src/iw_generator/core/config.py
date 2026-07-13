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


class ThemeSocialSettings(BaseModel):
    github: str = ""
    twitter: str = ""
    telegram: str = ""
    email: str = ""


class GiscusSettings(BaseModel):
    enabled: bool = False
    repo: str = ""
    repo_id: str = ""
    category: str = ""
    category_id: str = ""
    mapping: str = "pathname"
    reactions_enabled: bool = True
    theme: str = "light"


class IwThemeSettings(BaseModel):
    """Settings specific to the iw theme (GitHub Pages + GitHub Issues)."""

    github_repo: str = ""  # owner/repo format
    github_token: str = ""  # GitHub Personal Access Token
    categories: dict[str, str] = Field(default_factory=dict)
    default_category: str = "Uncategorized"
    exclude_labels: list[str] = Field(default_factory=list)  # labels to exclude
    posts_per_page: int = 20


class ThemeSettings(BaseModel):
    name: str = "blog"
    mode: str = "blog"  # "iw", "doc", or "blog"
    lang: str = "en"
    favicon: str = ""
    avatar: str = ""
    social: ThemeSocialSettings = Field(default_factory=ThemeSocialSettings)
    giscus: GiscusSettings = Field(default_factory=GiscusSettings)
    iw: IwThemeSettings = Field(default_factory=IwThemeSettings)


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
