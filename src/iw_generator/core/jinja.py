"""Jinja2 template rendering for themes."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import Config


def get_theme_dir(config: Config) -> Path:
    """Get the path to the current theme directory."""
    theme_name = config.theme.name
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
    return env


def render_template(
    env: Environment,
    template_name: str,
    context: dict,
) -> str:
    """Render a template with the given context."""
    template = env.get_template(template_name)
    return template.render(**context)
