# Bedrock Python Blog

[![Site](https://img.shields.io/badge/site-bedrock--python.github.io-blue)](https://bedrock-python.github.io)
[![License](https://img.shields.io/github/license/bedrock-python/bedrock-python.github.io)](LICENSE)
[![Docs](https://github.com/bedrock-python/bedrock-python.github.io/actions/workflows/docs.yml/badge.svg?branch=master)](https://github.com/bedrock-python/bedrock-python.github.io/actions/workflows/docs.yml)

Source for [bedrock-python.github.io](https://bedrock-python.github.io) — release notes, design decisions, and deep dives for the Bedrock Python library ecosystem.

## Local development

```bash
uv sync --group dev
uv run pre-commit install --hook-type commit-msg
make docs-serve
```

Open `http://localhost:8000`.

## Adding a blog post

Create a Markdown file under `docs/blog/posts/` with a date-prefixed name:

```
docs/blog/posts/YYYY-MM-DD-your-slug.md
```

Required front matter:

```yaml
---
date: YYYY-MM-DD
authors:
  - alex
categories:
  - Tutorials     # or: Design, Libraries, Tools, Meta
tags:
  - library-name
---

# Post title

One-sentence summary shown in the post list.

<!-- more -->

Full content here.
```

The blog directory is generated from the posts: titles, summaries, dates, formats,
tags, topics, reading times, and the local search catalog. Topics are inferred from
library tags and the article's subject. Use accurate tags; there is no separate
JavaScript list to update. The first paragraph after the title and optional hero
illustration supplies the summary.

Run `make docs-catalog` after adding a post or changing its metadata/content, and
commit the updated `docs/blog/catalog.json` and generated article block in
`docs/blog/index.md` alongside the post. `make docs-serve`, `make docs-build`, and
the deployment workflow regenerate these automatically. If a development server
is already running, run `make docs-catalog` again to refresh the directory.

The equivalent command without Make is:

```bash
uv run --no-dev --group docs python scripts/build_blog_catalog.py
```

Check that committed catalog files are current with:

```bash
uv run --no-dev --group docs python scripts/build_blog_catalog.py --check
```

## Deployment

Any push to `master` triggers the [Docs workflow](.github/workflows/docs.yml) which builds with `zensical` and deploys to GitHub Pages automatically.

## License

Apache 2.0 — see [LICENSE](LICENSE).
