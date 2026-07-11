---
title: "Plugins"
---

# Plugins

## Built-in

| Plugin | Description |
|--------|-------------|
| `toc` | Table of contents |
| `search` | Client-side search index |
| `rss` | RSS feed |
| `sitemap` | Sitemap.xml |
| `highlight` | Code highlighting |

## Enable

```toml
[plugins]
enable = ["toc", "search", "rss"]
```

## Third-party

Plugins are discovered via Python entry_points. Install a package that registers `iw_generator.plugins`:

```toml
# In the plugin package's pyproject.toml
[project.entry-points."iw_generator.plugins"]
my_plugin = "my_package:MyPlugin"
```
