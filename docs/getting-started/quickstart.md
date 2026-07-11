---
title: "Quick Start"
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
