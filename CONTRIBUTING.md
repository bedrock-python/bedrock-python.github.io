# Contributing to Bedrock Python Blog

Contributions are welcome — whether that's fixing a typo, improving an existing post, or suggesting new content.

## Setup

```bash
git clone https://github.com/bedrock-python/bedrock-python.github.io.git
cd bedrock-python.github.io
uv sync --group dev
uv run pre-commit install --hook-type commit-msg
```

## Preview the site locally

```bash
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

## Commit messages

[Conventional Commits](https://www.conventionalcommits.org/) are enforced by pre-commit:

| Prefix | Use for |
|--------|---------|
| `docs:` | New or updated post / page |
| `fix:` | Typo, broken link, incorrect info |
| `feat:` | New site section or feature |
| `chore:` | Config, CI, tooling |

## Pull requests

1. Fork the repository
2. Create a branch from `master`: `git checkout -b docs/my-post`
3. Add or edit content, run `make docs-serve` to preview
4. Open a PR against `master`
