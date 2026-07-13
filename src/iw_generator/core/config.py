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
    author: str = ""
    copyright: str = ""
    license: str = ""
    keywords: list[str] = Field(default_factory=list)
    og_image: str = ""
    google_analytics: str = ""


class PathsSettings(BaseModel):
    content: str = "content"
    output: str = "site"
    ignore: list[str] = Field(default_factory=list)


class ThemeSettings(BaseModel):
    name: str = "blog"
    lang: str = "en"
    favicon: str = ""
    avatar: str = ""
    custom_css: list[str] = Field(default_factory=list)
    custom_js: list[str] = Field(default_factory=list)


class SocialItem(BaseModel):
    icon: str = ""
    link: str = ""


class SocialSettings(BaseModel):
    """Social links - supports both dict and list format."""

    github: str = ""
    twitter: str = ""
    telegram: str = ""
    email: str = ""
    bilibili: str = ""
    douyin: str = ""
    kuaishou: str = ""
    tiktok: str = ""
    linkedin: str = ""
    instagram: str = ""
    youtube: str = ""
    rss: str = ""
    items: list[SocialItem] = Field(default_factory=list)

    def get_all_links(self) -> list[dict[str, str]]:
        """Get all social links as list of {icon, link} dicts.

        Handles both dict format (github = "url") and list format ([[social]]).
        """
        result = []
        # Known icon mappings for dict format
        icon_map = {
            "github": "simple/github",
            "twitter": "simple/twitter",
            "telegram": "simple/telegram",
            "bilibili": "simple/bilibili",
            "douyin": "simple/tiktok",
            "kuaishou": "material/video",
            "tiktok": "simple/tiktok",
            "linkedin": "simple/linkedin",
            "instagram": "simple/instagram",
            "youtube": "simple/youtube",
            "rss": "material/rss",
            "email": "material/email-outline",
        }
        # Dict format
        for field_name, icon in icon_map.items():
            value = getattr(self, field_name, "")
            if value:
                if field_name == "email":
                    result.append({"icon": icon, "link": f"mailto:{value}"})
                else:
                    result.append({"icon": icon, "link": value})
        # List format
        for item in self.items:
            if item.link:
                result.append({"icon": item.icon, "link": item.link})
        return result


class GiscusConfig(BaseModel):
    repo: str = ""
    repo_id: str = ""
    category: str = ""
    category_id: str = ""
    mapping: str = "pathname"
    reactions_enabled: bool = True
    theme: str = "light"


class TwikooConfig(BaseModel):
    env_id: str = ""
    region: str = ""


class CommentSettings(BaseModel):
    provider: str = ""
    giscus: GiscusConfig = Field(default_factory=GiscusConfig)
    twikoo: TwikooConfig = Field(default_factory=TwikooConfig)


class NavigationSettings(BaseModel):
    order: list[str] = Field(default_factory=list)
    hide: list[str] = Field(default_factory=list)
    sidebar: bool = True


class PluginsSettings(BaseModel):
    enable: list[str] = Field(default_factory=list)


class ExtraSettings(BaseModel):
    head_inject: str = ""
    footer_inject: str = ""


class Config(BaseModel):
    site: SiteSettings = Field(default_factory=SiteSettings)
    paths: PathsSettings = Field(default_factory=PathsSettings)
    theme: ThemeSettings = Field(default_factory=ThemeSettings)
    social: SocialSettings = Field(default_factory=SocialSettings)
    comment: CommentSettings = Field(default_factory=CommentSettings)
    navigation: NavigationSettings = Field(default_factory=NavigationSettings)
    plugins: PluginsSettings = Field(default_factory=PluginsSettings)
    extra: ExtraSettings = Field(default_factory=ExtraSettings)

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
