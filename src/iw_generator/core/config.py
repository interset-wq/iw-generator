"""TOML configuration loading and validation with Pydantic."""

from __future__ import annotations

import tomllib
from pathlib import Path
from types import SimpleNamespace

from pydantic import BaseModel, Field

CONFIG_FILE = "iw.config.toml"


class SiteSettings(BaseModel):
    name: str = "My Site"
    url: str = ""
    description: str = ""


class PathsSettings(BaseModel):
    content: str = "content"
    output: str = "site"


class ThemeSettings(BaseModel):
    name: str = "blog"
    lang: str = "en"
    favicon: str = ""
    avatar: str = ""


class PluginsSettings(BaseModel):
    enable: list[str] = Field(default_factory=list)


class Config(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    site: SiteSettings = Field(default_factory=SiteSettings)
    paths: PathsSettings = Field(default_factory=PathsSettings)
    theme: ThemeSettings = Field(default_factory=ThemeSettings)
    plugins: PluginsSettings = Field(default_factory=PluginsSettings)
    theme_config: SimpleNamespace = Field(default_factory=SimpleNamespace)

    @classmethod
    def load(cls, config_path: Path | str | None = None) -> Config:
        """Load config from TOML file, merging with defaults."""
        path = _resolve_config_path(config_path)
        raw = _read_toml(path) if path else {}
        cfg = cls.model_validate(raw)

        # Load theme.toml from theme directory
        _load_theme_config(cfg)

        return cfg

    @property
    def content_dir(self) -> Path:
        return Path(self.paths.content)

    @property
    def output_dir(self) -> Path:
        return Path(self.paths.output)

    @property
    def static_dir(self) -> Path:
        return self.content_dir / "static"


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


def _load_theme_config(cfg: Config) -> None:
    """Load theme.toml from theme directory and attach to config.theme_config."""
    from .jinja import get_theme_dir

    theme_dir = get_theme_dir(cfg)
    theme_toml = theme_dir / "theme.toml"

    if not theme_toml.exists():
        return

    with open(theme_toml, "rb") as f:
        theme_raw = tomllib.load(f)

    # Store entire theme.toml as nested namespace on config.theme_config
    cfg.theme_config = _dict_to_namespace(theme_raw)


def _dict_to_namespace(d: dict) -> SimpleNamespace:
    """Convert a dict to a nested SimpleNamespace for attribute access."""
    result = SimpleNamespace()
    for key, value in d.items():
        if isinstance(value, dict):
            setattr(result, key, _dict_to_namespace(value))
        else:
            setattr(result, key, value)
    return result
