"""Plugin base class and discovery mechanism."""

from __future__ import annotations

from importlib.metadata import entry_points

from .config import Config
from .file import Page, Site


class PluginBase:
    """Base class for all iw-generator plugins."""

    name: str = "base"

    def __init__(self, config: Config) -> None:
        self.config = config

    def on_config_loaded(self, config: Config) -> None:
        """Called after config is loaded."""

    def on_page_read(self, page: Page) -> None:
        """Called after a page's markdown is read."""

    def on_page_render(self, page: Page, html: str) -> str:
        """Called after markdown is rendered to HTML. Return modified HTML."""
        return html

    def on_page_write(self, page: Page, html: str) -> None:
        """Called before a page is written to disk."""

    def on_site_build_done(self, site: Site) -> None:
        """Called after the entire site is built."""


def discover_plugins(config: Config) -> list[PluginBase]:
    """Discover and instantiate plugins from entry_points and built-in."""
    plugins: list[PluginBase] = []

    # Load plugins from entry_points
    eps = entry_points(group="iw_generator.plugins")
    for ep in eps:
        try:
            plugin_cls = ep.load()
            if isinstance(plugin_cls, type) and issubclass(plugin_cls, PluginBase):
                plugins.append(plugin_cls(config))
        except Exception:
            continue

    # Load enabled built-in plugins
    from . import _builtin_plugins

    for name in config.plugins.enable:
        if name in _builtin_plugins:
            plugin_cls = _builtin_plugins[name]
            plugins.append(plugin_cls(config))

    return plugins
