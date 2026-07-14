# CSS Convention

## Naming Convention

All shared CSS classes use `iw-` prefix with BEM methodology:

```
.iw-block__element--modifier
```

Examples:
- `.iw-code` - block
- `.iw-code__header` - element
- `.iw-code__copy` - element
- `.iw-nav__item--prev` - modifier

## Directory Structure

```
themes/shared/
  css/
    normalize.css    # CSS reset (v8.0.1) - always required
    variables.css    # Design tokens - always required
    base.css         # Base layout - always required
    code.css         # Code highlighting - load on pages with code
    nav.css          # Prev/next navigation - load on post pages
    footer.css       # Footer - always required
  js/
    theme.js         # Theme toggle - always required
    copy.js          # Copy button - load on pages with code
  components/
    base.html        # Base template for all themes
    footer.html      # Footer (plain)
    nav-footer.html  # Footer with navigation
    giscus.html      # Comments
```

## Base Template Placeholders

All themes must inherit from `shared/base.html`:

```jinja2
{% extends "shared/base.html" %}
```

| Placeholder | Location | Description |
|-------------|----------|-------------|
| `title` | `<title>` | Page title |
| `meta` | `<head>` | Meta tags (description, viewport, etc.) |
| `og` | `<head>` | Open Graph tags (og:title, og:description, etc.) |
| `css` | `<head>` | Page-specific CSS |
| `head_js` | `<head>` | JavaScript in head |
| `header` | `<body>` | Page header |
| `content` | `<body>` | Main content |
| `footer` | `<body>` | Page footer (default: shared footer) |
| `body_js` | `<body>` | JavaScript at end of body |

## CSS Loading Strategy

### Always Required (in base.html)
```html
<link rel="stylesheet" href=".../normalize.css">
<link rel="stylesheet" href=".../variables.css">
<link rel="stylesheet" href=".../base.css">
```

### Load on Demand (in theme's `{% block css %}`)
```jinja2
{% block css %}
<link rel="stylesheet" href="{{ base_path }}assets/shared/css/code.css">
<link rel="stylesheet" href="{{ base_path }}assets/shared/css/nav.css">
{% endblock %}
```

### When to Load

| CSS File | When to Load |
|----------|--------------|
| `normalize.css` | Always (in base) |
| `variables.css` | Always (in base) |
| `base.css` | Always (in base) |
| `code.css` | Pages with code blocks |
| `nav.css` | Post pages with prev/next |
| `footer.css` | Always (footer present on all pages) |

## CSS Variables

All variables use `--iw-` prefix:

```css
--iw-color-{property}      /* Colors */
--iw-font-{property}       /* Typography */
--iw-space-{size}          /* Spacing (0-12) */
--iw-radius-{size}         /* Border radius */
--iw-shadow-{size}         /* Box shadows */
--iw-transition-{speed}    /* Transitions */
```

### Color Variables

```css
/* Background */
--iw-color-bg
--iw-color-bg-subtle
--iw-color-bg-muted

/* Foreground */
--iw-color-fg
--iw-color-fg-subtle
--iw-color-fg-muted

/* Border */
--iw-color-border
--iw-color-border-muted

/* Accent */
--iw-color-accent
--iw-color-accent-fg
--iw-color-accent-subtle
```

## Color Scheme Switching

Use `data-color-mode` attribute on `<html>`:

```html
<html data-color-mode="light">
<html data-color-mode="dark">
<html data-color-mode="auto">
```

## File Naming

- Use lowercase with hyphens: `code.css`, `nav-footer.html`
- Components: `components/{name}.html`
- CSS: `css/{name}.css`
- JS: `js/{name}.js`
