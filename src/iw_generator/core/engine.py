"""Build engine: discovers files, renders markdown, writes output."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from .config import Config
from .file import Page, Site
from .jinja import create_jinja_env, render_template
from .markdown import MarkdownRenderer
from .plugin import PluginBase, discover_plugins
from .utils import clean_dir, copy_tree

console = Console()


class Engine:
    """Orchestrates the static site build process."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.renderer = MarkdownRenderer()
        self.site = Site()
        self.plugins: list[PluginBase] = []

    def build(self) -> Site:
        """Run the full build pipeline."""
        self._load_plugins()
        self._clean_output()
        self._discover_and_render_pages()
        self._copy_static_assets()
        self._write_pages()
        self._run_plugin_hook("on_site_build_done", self.site)
        return self.site

    def _load_plugins(self) -> None:
        self.plugins = discover_plugins(self.config)
        for plugin in self.plugins:
            console.print(f"  Plugin: [cyan]{plugin.name}[/]")
            plugin.on_config_loaded(self.config)

    def _clean_output(self) -> None:
        output_dir = self.config.output_dir
        console.print(f"Cleaning [cyan]{output_dir}[/]")
        clean_dir(output_dir)

    def _discover_and_render_pages(self) -> None:
        content_dir = self.config.content_dir
        if not content_dir.is_dir():
            console.print(f"[yellow]Content dir not found: {content_dir}[/]")
            return

        md_files = sorted(content_dir.rglob("*.md"))
        console.print(f"Found [cyan]{len(md_files)}[/] markdown files")

        for md_path in md_files:
            page = self._process_page(md_path, content_dir)
            self.site.pages.append(page)

    def _process_page(self, md_path: Path, content_dir: Path) -> Page:
        # Determine output path
        rel = md_path.relative_to(content_dir)
        out_rel = rel.with_suffix(".html")
        dest_path = self.config.output_dir / out_rel

        page = Page(
            source_path=md_path,
            dest_path=dest_path,
            content_dir=content_dir,
        )

        # Read and render
        page.raw_content = md_path.read_text(encoding="utf-8")
        frontmatter, html = self.renderer.render_string(page.raw_content)
        page.frontmatter = frontmatter
        page.title = frontmatter.get("title", rel.stem)
        page.date = str(frontmatter.get("date", ""))
        tags = frontmatter.get("tags", [])
        page.tags = tags if isinstance(tags, list) else []

        # Plugin hooks
        self._run_plugin_hook("on_page_read", page)
        html = self._run_render_hook(page, html)
        page.html_content = html

        return page

    def _run_render_hook(self, page: Page, html: str) -> str:
        for plugin in self.plugins:
            html = plugin.on_page_render(page, html)
        return html

    def _run_plugin_hook(self, hook_name: str, *args) -> None:
        for plugin in self.plugins:
            method = getattr(plugin, hook_name, None)
            if method:
                method(*args)

    def _copy_static_assets(self) -> None:
        # Copy user static dir
        static_dir = self.config.static_dir
        if static_dir.is_dir():
            dest = self.config.output_dir / "static"
            console.print(f"Copying static: [cyan]{static_dir}[/]")
            copy_tree(static_dir, dest)

        # Copy theme assets
        from .jinja import get_theme_dir

        theme_dir = get_theme_dir(self.config)
        assets_dir = theme_dir / "assets"
        if assets_dir.is_dir():
            dest = self.config.output_dir / "assets"
            copy_tree(assets_dir, dest)

    def _write_pages(self) -> None:
        env = create_jinja_env(self.config)
        console.print(f"Writing [cyan]{len(self.site.pages)}[/] pages")

        for page in self.site.pages:
            page.dest_path.parent.mkdir(parents=True, exist_ok=True)
            html = render_template(
                env,
                "base.html",
                {
                    "site": self.config.site,
                    "page": page,
                    "content": page.html_content,
                    "config": self.config,
                },
            )
            page.dest_path.write_text(html, encoding="utf-8")
            self._run_plugin_hook("on_page_write", page, html)


def build(config: Config) -> Site:
    """Convenience function to build a site."""
    engine = Engine(config)
    return engine.build()
