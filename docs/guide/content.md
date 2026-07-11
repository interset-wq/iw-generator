---
title: "Writing Content"
---

# Writing Content

## Directory Structure

Place `.md` files under `content/`. Nested directories are preserved in output.

```
content/
  index.md              -> site/index.md
  getting-started/
    quickstart.md       -> site/getting-started/quickstart.md
```

## Frontmatter

### YAML

```markdown
---
title: "Page Title"
tags: ["tag1", "tag2"]
---
```

### TOML

```markdown
+++
title = "Page Title"
tags = ["tag1", "tag2"]
+++
```
