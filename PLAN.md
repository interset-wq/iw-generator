# IW-Generator 实施计划

## 项目概述

将 Gmeek（GitHub Issues 博客生成器）重构为通用的 Markdown 静态网站生成器，支持文档模式和博客模式，默认主题 "iw"。

---

## 架构设计

### 目录结构

```
iw-generator/
├── pyproject.toml              # uv 项目配置
├── README.md
├── LICENSE
├── src/
│   └── iw_generator/
│       ├── __init__.py
│       ├── __main__.py         # CLI 入口
│       ├── cli.py              # Click CLI 命令
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py       # 配置加载与验证 (YAML)
│       │   ├── site.py         # 站点生成主逻辑
│       │   ├── markdown.py     # Markdown 解析器 (markdown-it-py)
│       │   ├── plugin.py       # 插件加载系统
│       │   └── utils.py        # 工具函数
│       ├── generators/
│       │   ├── __init__.py
│       │   ├── blog.py         # 博客模式生成器
│       │   └── docs.py         # 文档模式生成器
│       ├── templates/          # 内置模板
│       │   ├── iw/             # 默认 iw 主题
│       │   │   ├── base.html
│       │   │   ├── home.html
│       │   │   ├── post.html
│       │   │   ├── page.html
│       │   │   ├── tag.html
│       │   │   ├── nav.html
│       │   │   ├── footer.html
│       │   │   └── assets/
│       │   │       ├── css/
│       │   │       │   └── iw.css
│       │   │       └── js/
│       │   │           └── iw.js
│       │   └── themes/         # 其他主题目录
│       ├── plugins/
│       │   ├── __init__.py
│       │   ├── toc.py          # 目录插件
│       │   ├── search.py       # 搜索插件
│       │   ├── rss.py          # RSS 生成
│       │   ├── sitemap.py      # Sitemap 生成
│       │   └── highlight.py    # 代码高亮
│       └── static/             # 内置静态资源
├── tests/
│   ├── test_config.py
│   ├── test_markdown.py
│   ├── test_blog.py
│   └── test_docs.py
└── docs/                       # 使用文档
```

---

## 实施阶段

### 阶段 1：项目基础搭建

**目标：** 建立项目骨架，配置 uv，实现基本 CLI。

1. **初始化 uv 项目**
   - 创建 `pyproject.toml`，配置项目元数据和依赖
   - 依赖项：
     ```
     markdown-it-py >= 3.0
     jinja2 >= 3.1
     pyyaml >= 6.0
     click >= 8.0
     rich >= 13.0          # 美化 CLI 输出
     pygments >= 2.17      # 代码高亮
     python-frontmatter >= 1.0  # 解析 MD frontmatter
     ```

2. **创建 CLI 入口**
   - `iw build [source] [-o output]` — 构建站点
   - `iw serve [-p port]` — 本地开发服务器
   - `iw init` — 初始化新站点
   - `iw new <title>` — 创建新文档/文章

3. **配置系统**
   - 基于 YAML 的配置文件 (`iw.config.yaml`)
   - 默认配置与用户配置合并
   - 配置验证和错误提示

---

### 阶段 2：Markdown 解析与内容处理

**目标：** 实现本地 Markdown 解析，替代 GitHub API。

1. **Markdown 解析器**
   - 使用 `markdown-it-py` 替代 GitHub Markdown API
   - 支持 GFM（GitHub Flavored Markdown）
   - 扩展支持：
     - 代码高亮（Pygments）
     - 表格
     - 任务列表
     - 脚注
     - 数学公式（KaTeX/MathJax）
     - Mermaid 图表

2. **Frontmatter 处理**
   - 使用 `python-frontmatter` 解析 YAML frontmatter
   - 支持的元数据字段：
     ```yaml
     ---
     title: 文章标题
     date: 2024-01-15
     tags: [tag1, tag2]
     category: 技术
     draft: false
     description: 文章描述
     image: /images/cover.jpg
     layout: post  # 或 docs
     ---
     ```

3. **内容管道**
   - Frontmatter 解析 → Markdown 渲染 → HTML 后处理
   - 支持自定义渲染器（插件注入点）

---

### 阶段 3：文档模式生成器

**目标：** 实现类似 MkDocs 的文档站点生成。

1. **目录结构约定**
   ```
   content/
   ├── index.md          # 首页
   ├── getting-started/
   │   ├── index.md
   │   └── installation.md
   ├── user-guide/
   │   ├── index.md
   │   └── configuration.md
   └── api/
       ├── index.md
       └── reference.md
   ```

2. **导航生成**
   - 根据目录结构自动生成侧边栏导航
   - 支持在 frontmatter 或配置中自定义导航
   - 支持多级嵌套菜单

3. **文档模式特性**
   - 自动目录（TOC）生成
   - 上一篇/下一篇导航
   - 搜索功能（客户端）
   - 版本切换（可选）
   - 代码复制按钮

---

### 阶段 4：博客模式生成器

**目标：** 实现博客功能，支持文章列表、标签、RSS。

1. **文章发现**
   - 扫描 `content/posts/` 目录
   - 从 frontmatter 提取元数据（标题、日期、标签、分类）
   - 按日期排序

2. **文章列表页**
   - 分页显示
   - 标签筛选
   - 按分类分组
   - RSS/Atom feed 生成

3. **单篇文章页**
   - 文章标题、日期、标签展示
   - OG meta 标签（SEO）
   - 上一篇/下一篇导航
   - 评论系统接口（可选）

4. **标签系统**
   - 自动提取所有标签
   - 按标签分组显示
   - 标签云（可选）

---

### 阶段 5：主题系统

**目标：** 实现灵活的主题系统，默认 "iw" 主题。

1. **主题结构**
   ```
   themes/
   └── iw/
       ├── theme.yaml          # 主题配置
       ├── templates/
       │   ├── base.html
       │   ├── ...
       └── assets/
           ├── css/
           └── js/
   ```

2. **iw 默认主题**
   - 现代、简洁的设计风格
   - 响应式布局
   - 深色/浅色模式切换
   - 中文优化排版
   - 自定义 CSS 变量

3. **主题配置**
   ```yaml
   theme:
     name: iw
     custom_dir: overrides/    # 用户自定义覆盖
     palette:
       - media: "(prefers-color-scheme: light)"
         scheme: light
         primary: blue
       - media: "(prefers-color-scheme: dark)"
         scheme: dark
         primary: blue
     font:
       text: "Noto Sans SC"
       code: "JetBrains Mono"
   ```

4. **模板覆盖机制**
   - 用户可覆盖主题中的任何模板
   - 支持模板继承和块覆盖

---

### 阶段 6：插件系统

**目标：** 实现可扩展的插件系统。

1. **插件接口**
   ```python
   class Plugin:
       def __init__(self, config):
           pass

       def on_page_markdown(self, markdown, page):
           """处理页面 Markdown"""
           return markdown

       def on_page_html(self, html, page):
           """处理页面 HTML"""
           return html

       def on_site_build(self, site):
           """站点构建完成"""
           pass
   ```

2. **内置插件**
   - `toc` — 目录生成
   - `search` — 搜索索引
   - `rss` — RSS/Atom 生成
   - `sitemap` — Sitemap 生成
   - `highlight` — 代码高亮配置
   - `mermaid` — Mermaid 图表支持
   - `math` — 数学公式支持

3. **插件配置**
   ```yaml
   plugins:
     - toc:
         depth: 3
     - search:
         lang: zh
     - rss:
           limit: 20
     - mermaid:
         theme: default
   ```

---

### 阶段 7：静态资源处理

**目标：** 处理 CSS、JS、图片等静态资源。

1. **静态资源目录**
   - `static/` — 直接复制到输出
   - 主题资产 — 从主题目录复制
   - 用户覆盖 — 从 `overrides/` 复制

2. **资源优化（可选）**
   - CSS/JS 合并压缩
   - 图片优化
   - 缓存破坏（hash 文件名）

3. **开发服务器**
   - 热重载
   - 实时预览
   - Markdown 文件监听

---

## 配置文件示例

```yaml
# iw.config.yaml
site_name: "我的文档站点"
site_url: "https://example.com"
site_description: "一个示例站点"

# 内容目录
docs_dir: content
site_dir: site

# 主题
theme:
  name: iw
  palette:
    - scheme: light
      primary: blue
    - scheme: dark
      primary: blue

# 模式: docs 或 blog
mode: docs

# 博客模式配置（仅 mode: blog 时生效）
blog:
  posts_dir: posts
  paginate: 10
  rss: true

# 导航（文档模式）
nav:
  - 首页: index.md
  - 开始使用:
    - 安装: getting-started/installation.md
    - 配置: getting-started/configuration.md
  - 用户指南: user-guide/
  - API: api/

# 插件
plugins:
  - toc
  - search
  - rss

# Markdown 配置
markdown:
  extensions:
    - tables
    - fenced_code
    - footnotes
    - toc:
        permalink: true
  highlight:
    theme: monokai

# 额外资源
extra_css: []
extra_js: []
```

---

## 迁移步骤（从 Gmeek）

### 第一步：提取可复用组件
1. 复用 Jinja2 模板渲染逻辑
2. 复用 RSS 生成逻辑（feedgen）
3. 复用 i18n 框架
4. 复用插件脚本（lightbox、TOC 等）

### 第二步：移除 GitHub 依赖
1. 移除 PyGithub 依赖
2. 移除 GitHub API 调用
3. 移除 Issue 相关逻辑
4. 移除 utteranc.es 评论系统（改为可选配置）

### 第三步：重写核心逻辑
1. 重写 Markdown 解析（用 markdown-it-py）
2. 重写内容发现机制（本地文件扫描）
3. 重写配置系统（YAML）
4. 重写站点生成流程

### 第四步：重新设计模板
1. 设计新的 base.html 布局
2. 创建 iw 主题样式
3. 实现响应式设计
4. 支持深色/浅色模式

---

## 关键决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 配置格式 | YAML | 比 JSON 更易读，支持注释 |
| 包管理器 | uv | 快速、现代 |
| MD 解析器 | markdown-it-py | 功能丰富、可扩展 |
| 模板引擎 | Jinja2 | 与 Gmeek 一致，功能强大 |
| 默认主题 | iw | 简洁现代，中文优化 |
| CLI 框架 | Click | 成熟稳定，易于扩展 |

---

## 待实现功能清单

- [ ] 项目初始化 (`iw init`)
- [ ] 配置加载与验证
- [ ] Markdown 解析器
- [ ] Frontmatter 处理
- [ ] 文档模式生成器
- [ ] 博客模式生成器
- [ ] iw 默认主题
- [ ] 插件系统
- [ ] TOC 插件
- [ ] 搜索插件
- [ ] RSS 插件
- [ ] Sitemap 插件
- [ ] 开发服务器
- [ ] CLI 美化输出
- [ ] 测试用例
