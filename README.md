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

Open `http://localhost:8000` for English or `http://localhost:8000/ru/` for Russian.
The preview watches both source trees, messages, templates, and scripts. After a
successful rebuild, refresh the browser. A failed build keeps the previous preview.

Without Make, or to use another port:

```bash
uv run --no-dev --group docs python scripts/build_site.py --serve --port 8001
```

`make docs-serve-en` runs the original Zensical live preview for English content
only; use `make docs-serve` when checking language switching.

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
commit the updated catalogs, article lists, archives, and category pages alongside
the post. These are generated for all enabled languages. `make docs-serve` and
`make docs-build` regenerate them; CI checks that the committed copies are current.

The equivalent command without Make is:

```bash
uv run --no-dev --group docs python scripts/build_blog_catalog.py
```

Check that committed catalog files are current with:

```bash
uv run --no-dev --group docs python scripts/build_blog_catalog.py --check
```

## Article diagrams

Use native Mermaid figures to explain a concrete decision, sequence or state
transition. Every article has a corresponding diagram in English and Russian,
with a visible caption and accessible SVG description. Shared styles support
both themes, a scrollable mobile viewport and an expanded dialog.

See [the diagram authoring guide](plans/article-diagrams.md) for the figure
template, supported layouts, translation rules and browser checks. Run
`make docs-catalog` after editing a diagram's caption, then `make docs-check`.

## Deployment

Any push to `master` triggers the [Docs workflow](.github/workflows/docs.yml) which builds with `zensical` and deploys to GitHub Pages automatically.

`make docs-build` prepares isolated inputs and caches for each language, builds
both editions, checks internal links, and publishes the combined output in
`site/`. The root sitemap includes both editions. Shared assets come from `docs/`
and templates from `overrides/`; generated copies are not committed.

## Translations

English is the source language and keeps the existing URLs. Russian uses `/ru/`.
The Russian edition covers all 99 source pages: 49 articles, 39 lab READMEs,
and the main pages, archive, and categories. Article links open the corresponding
Russian lab documentation; runnable examples and their output retain the original
code and identifiers. Both editions have their own complete search catalog.

To translate a page, create its counterpart under `translations/ru/` using the
same relative path as in `docs/`. For example:

```text
docs/blog/posts/2026-05-30-welcome.md
translations/ru/blog/posts/2026-05-30-welcome.md
```

Translate the title, prose, descriptions, and accessibility labels. Keep dates,
authors, category names in front matter, tags, package names, commands, and code
examples consistent with the original. Category/topic IDs stay stable; their
display labels come from `i18n/ru.json`. Preserve important heading anchors with
explicit IDs, such as `## Решение { #the-decision }`. Translate lab READMEs too;
link articles to their local `../lab/<slug>/README.md` counterpart and provide
a link from the lab to its source code on GitHub.

Run `make docs-catalog`, then `make docs-check` and `make docs-build`. Commit the
translation and regenerated files. `build/translation-coverage.json` lists the
remaining translations after a build. Tests require Russian page coverage to
match the English edition and verify section anchors and executable examples.
Revisit the corresponding translations
when editing an English source; automatic stale-translation detection is not
implemented.

Language switching goes to the corresponding page and reloads the edition's
search/messages. The selector marks unavailable translations; translated pages
that link to an untranslated article show an explicit English link. The Russian
catalog includes only translated articles. An edition with partial coverage links
to the complete English catalog. Per-page canonical and alternate links describe
only published pages.

Custom interface messages live in `i18n/en.json` and `i18n/ru.json`. Keep their keys
and format variables in sync. Babel and `Intl.PluralRules` handle language-specific
count forms. `docs/javascripts/i18n.js` also localizes the search placeholder,
filters, result-count labels, and code line-selection controls that Zensical
0.0.58 leaves in English. Check this compatibility adapter when upgrading the
theme; it only changes controls, preserving search results and code content.

To add a language, register its code, name, URL prefix, source directory and locale
in `i18n/locales.toml`, add a matching message dictionary, and create its main
pages and translated posts. The build generates navigation and language links
from this registry. Navigation pages must exist; article translations for new
languages can be added gradually. Maintain full Russian coverage when adding
English pages. Start from the existing translated page structure and retain
catalog generation markers. Do not place translated Markdown inside `docs/`.

## License

Apache 2.0 — see [LICENSE](LICENSE).
