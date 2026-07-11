"""CLI entry point for iw-generator."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from . import __version__
from .core.config import Config
from .core.engine import build

console = Console()


@click.group()
@click.version_option(__version__, prog_name="iw")
def main():
    """iw-generator: A general-purpose Markdown static site generator."""


@main.command()
@click.argument("source", default=".", type=click.Path(exists=True))
@click.option("-c", "--config", "config_path", default=None, help="Config file path")
@click.option("-o", "--output", "output_path", default=None, help="Output directory")
def build_cmd(source: str, config_path: str | None, output_path: str | None):
    """Build static site from markdown files."""
    console.print(
        Panel(f"[bold]iw-generator[/] v{__version__}", subtitle="Building site...")
    )

    # Change to source directory
    source_path = Path(source).resolve()
    import os

    os.chdir(source_path)

    # Load config
    cfg = Config.load(config_path)
    if output_path:
        cfg = cfg.model_copy(update={"paths": {"output": output_path}})

    # Build
    site = build(cfg)

    console.print(
        Panel(
            f"[green]Done![/]\n"
            f"Pages: {len(site.pages)}\n"
            f"Output: {cfg.output_dir}",
            title="Build Complete",
        )
    )


@main.command()
@click.option("-c", "--config", "config_path", default=None, help="Config file path")
@click.option("-p", "--port", default=8000, type=int, help="Port to serve on")
def serve(config_path: str | None, port: int):
    """Start development server with live reload."""
    import os
    from functools import partial
    from http.server import HTTPServer, SimpleHTTPRequestHandler

    cfg = Config.load(config_path)
    output_dir = cfg.output_dir.resolve()

    # Build first
    os.chdir(Path.cwd())
    build(cfg)

    console.print(f"[green]Serving[/] at http://localhost:{port}")
    console.print("Press Ctrl+C to stop")

    handler = partial(SimpleHTTPRequestHandler, directory=str(output_dir))
    server = HTTPServer(("", port), handler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped.[/]")


@main.command()
def init():
    """Initialize a new iw site in the current directory."""
    cwd = Path.cwd()
    config_file = cwd / "iw.config.toml"

    if config_file.exists():
        console.print("[yellow]iw.config.toml already exists, skipping.[/]")
        return

    config_file.write_text(
        """[site]
name = "My Site"
url = ""
description = ""

[paths]
content = "content"
output = "site"
static = "static"

[theme]
name = "iw"

[plugins]
enable = []
""",
        encoding="utf-8",
    )

    # Create content dir with index.md
    content_dir = cwd / "content"
    content_dir.mkdir(exist_ok=True)
    index_file = content_dir / "index.md"
    if not index_file.exists():
        index_file.write_text(
            '---\ntitle: "Home"\n---\n\n# Welcome\n\nHello world!\n',
            encoding="utf-8",
        )

    console.print("[green]Initialized![/]")
    console.print("  - iw.config.toml")
    console.print("  - content/index.md")


@main.command()
@click.argument("title")
def new(title: str):
    """Create a new markdown file."""
    slug = title.lower().replace(" ", "-")
    content_dir = Path("content")
    content_dir.mkdir(exist_ok=True)

    new_file = content_dir / f"{slug}.md"
    if new_file.exists():
        console.print(f"[yellow]{new_file} already exists[/]")
        return

    new_file.write_text(
        f'---\ntitle: "{title}"\ndate: ""\ntags: []\n---\n\n# {title}\n\nWrite here.\n',
        encoding="utf-8",
    )
    console.print(f"[green]Created[/] {new_file}")


@main.command()
@click.option("--user", prompt="GitHub username", help="GitHub username")
@click.option("--repo", prompt="Repository name", help="Repository name")
@click.option(
    "--type",
    "site_type",
    type=click.Choice(["user", "repo"]),
    default="user",
    help="Site type: user (username.github.io) or repo (username.github.io/repo)",
)
def deploy(user: str, repo: str, site_type: str):
    """Setup GitHub Pages deployment workflow."""
    from shutil import copy2

    deploy_dir = Path(".github/workflows")
    deploy_dir.mkdir(parents=True, exist_ok=True)

    # Copy workflow template
    template = Path(__file__).parent / "themes" / "iw" / "deploy" / "github-pages.yml"
    dest = deploy_dir / "github-pages.yml"
    copy2(template, dest)

    console.print(f"[green]Created[/] {dest}")
    console.print()
    console.print("Next steps:")
    console.print(f"  1. Push to [cyan]https://github.com/{user}/{repo}[/]")
    console.print("  2. Go to repo Settings -> Pages -> Source: GitHub Actions")
    console.print("  3. Push to main branch to trigger deployment")
