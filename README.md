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
  - Releases      # or: Design, Meta, Tutorial
tags:
  - library-name
---

# Post title

One-sentence summary shown in the post list.

<!-- more -->

Full content here.
```

## Deployment

Any push to `master` triggers the [Docs workflow](.github/workflows/docs.yml) which builds with `zensical` and deploys to GitHub Pages automatically.

## License

Apache 2.0 — see [LICENSE](LICENSE).
