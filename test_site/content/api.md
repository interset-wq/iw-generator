---
title: "API Reference"
tags: ["api", "reference"]
---

# API Reference

## Config

```python
from iw_generator.core.config import Config

cfg = Config.load("iw.config.toml")
```

## Build

```python
from iw_generator.core.engine import build

site = build(cfg)
```
