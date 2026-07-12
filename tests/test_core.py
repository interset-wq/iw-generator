"""Tests for iw_generator core modules."""

from pathlib import Path

from iw_generator.core.config import Config
from iw_generator.core.file import Page, Site
from iw_generator.core.markdown import MarkdownRenderer


def test_config_defaults():
    cfg = Config()
    assert cfg.site.name == "My Site"
    assert cfg.paths.content == "content"
    assert cfg.theme.name == "iw"


def test_config_from_dict():
    cfg = Config.model_validate({"site": {"name": "Test"}})
    assert cfg.site.name == "Test"
    assert cfg.paths.content == "content"  # default preserved


def test_page_slug():
    page = Page(
        source_path=Path("content/docs/guide.md"),
        dest_path=Path("site/docs/guide.html"),
        content_dir=Path("content"),
    )
    assert page.slug == "docs/guide"


def test_page_slug_index():
    page = Page(
        source_path=Path("content/index.md"),
        dest_path=Path("site/index.html"),
        content_dir=Path("content"),
    )
    assert page.slug == ""


def test_markdown_frontmatter_yaml():
    renderer = MarkdownRenderer()
    fm, html = renderer.render_string("---\ntitle: Hello\n---\n\n# World\n")
    assert fm["title"] == "Hello"
    assert "<h1" in html
    assert "World" in html


def test_markdown_frontmatter_toml():
    renderer = MarkdownRenderer()
    fm, html = renderer.render_string('+++\ntitle = "Hello"\n+++\n\n# World\n')
    assert fm["title"] == "Hello"
    assert "<h1" in html


def test_markdown_code_highlight():
    renderer = MarkdownRenderer()
    _, html = renderer.render_string("```python\nprint('hi')\n```\n")
    assert 'class="language-python"' in html
    assert "print" in html


def test_site_tags():
    site = Site()
    site.pages.append(
        Page(
            source_path=Path("a.md"),
            dest_path=Path("a.html"),
            content_dir=Path("."),
            tags=["python", "web"],
        )
    )
    site.pages.append(
        Page(
            source_path=Path("b.md"),
            dest_path=Path("b.html"),
            content_dir=Path("."),
            tags=["python"],
        )
    )
    tags = site.all_tags()
    assert tags["python"] == 2
    assert tags["web"] == 1


def test_page_about():
    """Test about page detection."""
    page = Page(
        source_path=Path("docs/about.md"),
        dest_path=Path("site/about/index.html"),
        content_dir=Path("docs"),
    )
    assert page.source_path.name == "about.md"
    assert "about" in str(page.dest_path)


def test_page_frontmatter_fields():
    """Test page frontmatter fields."""
    page = Page(
        source_path=Path("content/post.md"),
        dest_path=Path("site/post/index.html"),
        content_dir=Path("content"),
    )
    page.title = "Test Post"
    page.date = "2026-01-01"
    page.category = "tech"
    page.tags = ["python", "testing"]
    page.pin = 1
    page.description = "A test post"

    assert page.title == "Test Post"
    assert page.date == "2026-01-01"
    assert page.category == "tech"
    assert page.tags == ["python", "testing"]
    assert page.pin == 1
    assert page.description == "A test post"


def test_page_url_generation():
    """Test URL generation for pages."""
    page = Page(
        source_path=Path("content/docs/guide.md"),
        dest_path=Path("site/docs/guide/index.html"),
        content_dir=Path("content"),
    )
    assert page.url == "/docs/guide/"

    # Test index page
    index_page = Page(
        source_path=Path("content/index.md"),
        dest_path=Path("site/index.html"),
        content_dir=Path("content"),
    )
    assert index_page.url == "/"
