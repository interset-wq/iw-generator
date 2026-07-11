---
title: "Configuration"
---

# Configuration

`iw.config.toml` in the project root:

```toml
[site]
name = "My Site"
url = "https://example.com"

[paths]
content = "content"
output = "site"

[theme]
name = "iw"

[plugins]
enable = ["toc", "search"]

[markdown]
highlight_theme = "monokai"
```
