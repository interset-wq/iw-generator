---
title: "Quick Start"
date: 2024-01-16
tags: [setup, tutorial]
category: Tutorial
pin: 2
description: "Get started with iw-generator in 3 steps"
---

# Quick Start

## 1. Initialize a site

```bash
iw init
```

This creates:

```
iw.config.toml
content/
  index.md
```

## 2. Write content

Create `.md` files in `content/`. Use frontmatter for metadata:

```markdown
---
title: "My Page"
tags: ["intro"]
---

# My Page

Content here.
```

## 3. Build

```bash
iw build
```

Output goes to `site/`.
