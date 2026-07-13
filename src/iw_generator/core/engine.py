"""Build engine: discovers files, renders markdown, writes output."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from .config import Config
from .file import Page, Site
from .jinja import create_jinja_env, get_theme_dir, render_template
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
        # Determine output path - generate directory-based URLs
        rel = md_path.relative_to(content_dir)
        stem = rel.stem
        parent = rel.parent

        # Read and render first to get frontmatter
        raw_content = md_path.read_text(encoding="utf-8")
        frontmatter, html, toc_items = self.renderer.render_string(raw_content)

        # Check for custom slug in frontmatter
        custom_slug = frontmatter.get("slug")
        if custom_slug:
            # Use custom slug from frontmatter
            slug = custom_slug.strip("/")
            dest_path = self.config.output_dir / slug / "index.html"
        elif stem == "index":
            # index.md -> dir/index.html
            dest_path = self.config.output_dir / parent / "index.html"
        else:
            # page.md -> page/index.html (use slugify for safe URLs)
            from .markdown import slugify

            safe_stem = slugify(stem)
            dest_path = self.config.output_dir / parent / safe_stem / "index.html"

        page = Page(
            source_path=md_path,
            dest_path=dest_path,
            content_dir=content_dir,
        )

        # Set page data
        page.raw_content = raw_content
        page.frontmatter = frontmatter
        page.title = frontmatter.get("title", rel.stem)
        page.date = str(frontmatter.get("date", ""))
        page.description = frontmatter.get("description", "")
        page.image = frontmatter.get("image", "")
        page.category = frontmatter.get("category", "")
        page.pin = int(frontmatter.get("pin", 0))
        tags = frontmatter.get("tags", [])
        page.tags = tags if isinstance(tags, list) else []
        page.toc_items = toc_items

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
        theme_dir = get_theme_dir(self.config)
        assets_dir = theme_dir / "assets"
        if assets_dir.is_dir():
            dest = self.config.output_dir / "assets"
            copy_tree(assets_dir, dest)

    def _write_pages(self) -> None:
        env = create_jinja_env(self.config)
        theme_dir = get_theme_dir(self.config)

        # Check for custom theme hooks
        hooks_file = theme_dir / "hooks.py"
        hooks = self._load_theme_hooks(hooks_file) if hooks_file.exists() else {}

        # Let theme hooks handle page writing, or use default
        if "write_pages" in hooks:
            hooks["write_pages"](self, env, theme_dir)
        else:
            self._default_write_pages(env)

    def _default_write_pages(self, env) -> None:
        """Default page writing logic."""
        nav = self._build_nav()
        theme_name = self.config.theme.name
        console.print(
            f"Writing [cyan]{len(self.site.pages)}[/] pages (theme: {theme_name})"
        )

        # Load theme context
        theme_context = self._get_theme_context()

        for page in self.site.pages:
            page.dest_path.parent.mkdir(parents=True, exist_ok=True)
            html = render_template(
                env,
                "base.html",
                {
                    "site": self.config.site,
                    "page": page,
                    "content": page.html_content,
                    "nav": nav,
                    "config": self.config,
                    **theme_context,
                },
            )
            page.dest_path.write_text(html, encoding="utf-8")
            self._run_plugin_hook("on_page_write", page, html)

    def _get_theme_context(self) -> dict:
        """Get theme-specific context variables."""
        context = {}

        # Load icons if available
        try:
            from ..themes.icons import _load_icons

            context["icons"] = _load_icons()
        except ImportError:
            context["icons"] = {}

        # Pass theme_config (loaded from theme.toml in config)
        context["theme_config"] = self.config.theme_config
        context["theme"] = self.config.theme
        return context

    def _load_theme_hooks(self, hooks_file: Path) -> dict:
        """Load theme hooks from hooks.py."""
        import importlib.util

        spec = importlib.util.spec_from_file_location("theme_hooks", hooks_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return {
                name: getattr(module, name)
                for name in dir(module)
                if callable(getattr(module, name)) and not name.startswith("_")
            }
        return {}

    def _build_nav(self) -> list[dict]:
        """Build hierarchical navigation tree from pages sorted by path."""
        nav: list[dict] = []
        sorted_pages = sorted(self.site.pages, key=lambda p: p.source_path.parts)

        for page in sorted_pages:
            rel = page.source_path.relative_to(self.config.content_dir)
            parts = rel.parts[:-1]  # directory parts (excluding filename)

            # Build nested structure
            current_level = nav
            for i, part in enumerate(parts):
                # Find or create section
                section = None
                for item in current_level:
                    if item.get("section") == part:
                        section = item
                        break

                if section is None:
                    section = {
                        "title": part.replace("-", " ").replace("_", " ").title(),
                        "section": part,
                        "children": [],
                        "level": i + 1,
                    }
                    current_level.append(section)

                current_level = section["children"]

            # Add page to current level
            current_level.append(
                {
                    "title": page.title,
                    "url": page.url,
                    "active": False,
                }
            )

        return nav


def build(config: Config) -> Site:
    """Convenience function to build a site."""
    engine = Engine(config)
    return engine.build()
