---
title: "Writing Plugins"
---

# Writing Plugins

Subclass `PluginBase`:

```python
from iw_generator.core.plugin import PluginBase

class MyPlugin(PluginBase):
    name = "my_plugin"

    def on_config_loaded(self, config):
        pass

    def on_page_render(self, page, html):
        return html

    def on_site_build_done(self, site):
        pass
```

## Hooks

- `on_config_loaded(config)` — after config is loaded
- `on_page_read(page)` — after markdown is read
- `on_page_render(page, html)` — after rendering (return modified HTML)
- `on_page_write(page, html)` — before writing to disk
- `on_site_build_done(site)` — after full site build
