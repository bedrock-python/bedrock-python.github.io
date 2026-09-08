# English and Russian editions

Research and implementation proposal, 2026-09-08. Verified against the installed
Zensical 0.0.58 using an isolated two-language prototype. This document describes
the proposed implementation; translations and production integration are not yet
implemented.

## Decision

Build each language separately and publish the results as one static site.
English remains the source language and keeps every existing URL. Russian uses
the `/ru/` prefix. Further languages follow the same convention.

| Content | English | Russian |
| --- | --- | --- |
| Home | `/` | `/ru/` |
| Libraries | `/libraries/` | `/ru/libraries/` |
| Tools | `/tools/` | `/ru/tools/` |
| Blog | `/blog/` | `/ru/blog/` |
| Article | `/blog/posts/<slug>/` | `/ru/blog/posts/<slug>/` |

The approach follows [hse-doc-studio's language builds][reference-config], with
English as the default language here. Its [asset synchronization script][reference-assets]
shares styles, scripts, and images between languages; its [deployment workflow][reference-ci]
publishes the combined output.

## What Zensical provides today

- `project.theme.language` selects the language of one build. Russian theme
  translations are available.
- `project.extra.alternate` adds a language selector and alternate-language links.
- Each build produces its own search data and sitemap. Cyrillic queries work.
- Full content translation management remains on the [roadmap][roadmap]. Do not
  depend on unreleased multilingual modules or assume that the MkDocs
  `mkdocs-static-i18n` plugin is supported by Zensical.
- The new global search window still has English interface labels. This is a
  documented limitation, distinct from support for searching Russian content.

Sources: [language settings][language], [search][search], and
[supported MkDocs functionality][plugins].

## Prototype results

A minimal English site and a Russian translation each contained a homepage and
the same article path. Both were built with the installed Zensical and served
together locally. Browser checks established that:

1. English output at the root and Russian output in `site/ru` coexist when built
   sequentially, English with `--clean` and Russian without it.
2. The Russian article renders with `html lang="ru"` and its own Russian canonical
   URL. A Cyrillic query finds the Russian article and opens its `/ru/` URL.
3. The standard selector follows the configured language root, even from an
   article. It does not preserve the article path automatically.
4. The standard `hreflang` links also repeat the configured language roots on
   article pages. They need replacement with actual equivalent-page URLs.
5. The root sitemap contains English pages only; the Russian sitemap contains
   Russian pages only. Publication needs a combined sitemap or sitemap index.
6. The global search placeholder remains `Search` with the Russian theme.

The prototype was outside the repository and used a separate server; it did not
modify the running development site's output or cache.

## Source organization

Keep the English Markdown in `docs/` and add translations outside that directory:

```text
docs/                         # English sources, existing paths
  index.md
  libraries/index.md
  tools/index.md
  blog/posts/<slug>.md
  assets/
  stylesheets/
  javascripts/
translations/
  ru/                         # Translated Markdown, matching relative paths
    index.md
    libraries/index.md
    tools/index.md
    blog/posts/<slug>.md
i18n/
  locales.toml                # Enabled languages, names, prefixes, metadata
  en.json                     # Custom interface messages
  ru.json
overrides/                    # Shared templates
zensical.toml                 # Shared settings and English defaults
```

Keeping translations outside `docs/` prevents Russian sources from accidentally
appearing in the English build and search index. Existing article slugs, package
names, imports, code examples, and lab paths remain stable. Translated prose uses
normal Markdown and is rendered during the build.

Use the relative source path as the translation key. A build-generated mapping
records which languages actually contain each page. A missing translation must
not silently become an English page labelled as Russian.

## Build and local preview

Add one build command that reads the shared configuration and language registry,
then prepares an isolated input/output directory for each language. It copies
shared assets and overrides into build inputs, applies locale metadata and
navigation, builds each edition, and combines successful outputs for publication.

Generated locale configurations and copied assets are build artifacts, not
additional maintained copies. This also avoids cache conflicts with a running
English development server and avoids relying on nested output cleanup behavior.

The existing `make docs-build` and GitHub Pages workflow should call this command.
Update `make docs-serve` to preview both editions on one origin, including
translation edits and article-catalog regeneration. Retain a simple command for
previewing a single edition when useful. The build must fail before publishing if
an edition fails to build or translated links fail validation.

## Reader experience and metadata

- Show `English` and `Русский` in an accessible language selector, available on
  mobile as well as desktop. Show the selected language without using flags.
- Switch to the translation of the current page. Use a full document navigation
  across languages so the HTML language, navigation, messages, and search index
  all change together; preserve instant navigation within an edition.
- If a page lacks a translation, explain that it is available in English and
  offer a direct link to the original. Do not send readers to a nonexistent URL
  or silently replace an article with the other language's homepage.
- Preserve section anchors only where translated counterparts exist. Matching
  explicit heading IDs is preferable for sections with external links.
- Generate per-page reciprocal `hreflang` links only for existing translations,
  with English as `x-default`; each translated page has its own canonical URL.
  Replace the stock root-only alternate metadata rather than appending duplicates.
- Localize descriptions, navigation, footer, Open Graph locale, and accessible
  labels as well as visible page text.
- Publish both languages in sitemap discovery. Do not redirect visitors away
  from an explicitly selected URL based on their browser language.

## Blog and catalog changes

The current site contains 49 posts and custom JavaScript interfaces. Changing
`theme.language` alone does not translate those interfaces.

- Parameterize `scripts/build_blog_catalog.py` by language and source directory.
  Generate each language's article list and `catalog.json` from its own Markdown.
- Keep category/topic identifiers stable across languages; localize their display
  labels. Translating identifiers would break filters and category URLs.
- Localize article summaries, date formatting, reading-time labels, pagination,
  sorting, empty states, counts, and return-to-articles links. Russian counts need
  proper plural forms rather than the English singular/plural rule.
- Extract interface messages from `bedrock.js`, `blog-explorer.js`, and
  `libraries.js` into shared language dictionaries. Translate copy-button
  feedback, search-close labels, and accessibility text too.
- Generate archive/category lists from the same localized article data to keep
  counts, titles, links, and translation availability consistent.
- Keep untranslated articles discoverable through an explicit link to the
  English catalog. Do not index copied English article bodies as Russian.
- Share existing visual assets and compact/responsive styles. Check longer
  Russian labels at mobile widths before adjusting component sizing.

## Delivery and verification

First establish the complete translation workflow with the main pages, custom
interfaces, and a representative article containing links and code. Then apply
the same workflow to the article corpus. Track missing translations so partial
coverage is visible and cannot be mistaken for a fully translated site.

Required verification:

- Existing English URLs resolve unchanged, including articles and lab resources.
- Translated navigation and internal links remain in the selected edition.
- Switching language preserves the current translated article, including after
  navigating there with instant navigation; missing translations are explicit.
- Cyrillic search returns Russian pages, and English results use English URLs.
- Blog filters, pagination, return state, copy controls, and mobile search work
  in both languages and both color schemes.
- Russian layouts fit phone, tablet, and desktop widths without page overflow.
- Canonical URLs, reciprocal alternate links, HTML language, and sitemap coverage
  match actual published pages.
- Rebuilding after adding, editing, or removing a translation updates catalogs,
  language links, and output without leaving stale translated pages.

[language]: https://zensical.org/docs/setup/language/
[search]: https://zensical.org/docs/setup/search/
[plugins]: https://zensical.org/docs/compatibility/mkdocs/plugins/
[roadmap]: https://zensical.org/about/roadmap/
[reference-config]: https://github.com/AlexeyShalaev/hse-doc-studio/blob/master/docs/zensical.en.toml
[reference-assets]: https://github.com/AlexeyShalaev/hse-doc-studio/blob/master/scripts/docs/sync_shared.py
[reference-ci]: https://github.com/AlexeyShalaev/hse-doc-studio/blob/master/.github/workflows/docs.yml
