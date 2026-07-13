"""Jinja2 template rendering for themes."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import Config


def get_theme_dir(config: Config) -> Path:
    """Get the path to the current theme directory."""
    theme_name = config.theme.name
    # iw theme shares templates with blog theme
    if theme_name == "iw":
        theme_name = "blog"
    # Built-in themes are under the package's themes directory
    builtin = Path(__file__).parent.parent / "themes" / theme_name
    if builtin.is_dir():
        return builtin
    # Fall back to user-specified custom_dir
    if config.theme.custom_dir:
        custom = Path(config.theme.custom_dir)
        if custom.is_dir():
            return custom
    return builtin


def create_jinja_env(config: Config) -> Environment:
    """Create a Jinja2 environment with the theme's templates."""
    theme_dir = get_theme_dir(config)
    templates_dir = theme_dir / "templates"

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Add icon functions to environment
    try:
        # Load icons from shared themes/icons.py
        from ..themes.icons import get_icon, get_icon_or_default

        env.globals["get_icon"] = get_icon
        env.globals["get_icon_or_default"] = get_icon_or_default
    except ImportError:
        # Icons module not available (e.g., custom theme)
        env.globals["get_icon"] = lambda name: ""
        env.globals["get_icon_or_default"] = lambda name, default="": ""

    # Add path utilities to environment
    from .paths import get_base_path, get_page_url, resolve_asset

    env.globals["get_base_path"] = get_base_path
    env.globals["resolve_asset"] = resolve_asset
    env.globals["get_page_url"] = get_page_url

    return env


def render_template(
    env: Environment,
    template_name: str,
    context: dict,
) -> str:
    """Render a template with the given context."""
    template = env.get_template(template_name)
    return template.render(**context)
