"""Contracts that keep translated URLs, catalogs, and code examples consistent."""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
import markdown
from unittest.mock import patch
from pathlib import Path
from string import Formatter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_blog_catalog import read_article
from build_site import build, combine_sitemaps, publish, rewrite_missing_links, safe_output, translation_map, validate_links
from site_i18n import messages, page_url, registry, translate


class Translations(unittest.TestCase):
    def test_russian_edition_covers_all_source_pages(self):
        original = {path.relative_to(ROOT / "docs") for path in (ROOT / "docs").rglob("*.md")}
        translated = {path.relative_to(ROOT / "translations/ru") for path in (ROOT / "translations/ru").rglob("*.md")}
        self.assertEqual(original, translated)

    def test_translated_sections_keep_original_anchors_and_code(self):
        for translated in (ROOT / "translations/ru/blog").rglob("*.md"):
            if "posts" not in translated.parts and "lab" not in translated.parts:
                continue
            original = ROOT / "docs" / translated.relative_to(ROOT / "translations/ru")
            sources = [path.read_text(encoding="utf-8-sig") for path in (original, translated)]
            headings = []
            for source in sources:
                body = re.sub(r"\A---\n.*?\n---\n", "", source, flags=re.S)
                rendered = markdown.markdown(body, extensions=["toc", "attr_list", "tables", "pymdownx.superfences"])
                headings.append(re.findall(r'<h[1-6] id="([^"]+)"', rendered))
            self.assertEqual(headings[0], headings[1], translated.name)
            pattern = r"(?ms)^```(python|bash|sh|shell|sql|yaml|toml|json|dockerfile)\n(.*?)^```"
            self.assertEqual(re.findall(pattern, sources[0]), re.findall(pattern, sources[1]), translated.name)

    def test_language_pairs_only_include_published_translations(self):
        languages = registry()["languages"]
        sources = {"en": {"index.md", "blog/posts/example.md", "blog/posts/pending.md"},
                   "ru": {"index.md", "blog/posts/example.md"}}
        pairs = translation_map(sources, languages, "https://example.org/project/")
        self.assertEqual(pairs[""]["en"]["path"], "/project/")
        self.assertEqual(pairs["blog/posts/example/"]["ru"]["canonical"],
                         "https://example.org/project/ru/blog/posts/example/")
        self.assertEqual(set(pairs["blog/posts/pending/"]), {"en"})
        self.assertEqual(page_url("blog/lab/example/README.md"), "blog/lab/example/")
        self.assertEqual(page_url("blog/category/design.md"), "blog/category/design/")

    def test_missing_links_are_explicit_and_code_is_untouched(self):
        original = {"index.md", "blog/posts/missing.md", "blog/posts/present.md"}
        available = {"index.md", "blog/posts/present.md"}
        source = ('[Missing](missing.md#example)\n\n[Present](present.md)\n\n'
                  '```markdown\n[Example](missing.md)\n```\n\n'
                  '<a href="../missing/">Missing HTML</a>\n')
        result = rewrite_missing_links(source, "blog/posts/present.md", available, original, "/", messages("ru"))
        self.assertIn('[Missing (Читать на английском)](/blog/posts/missing/#example)', result)
        self.assertIn('[Present](present.md)', result)
        self.assertIn('```markdown\n[Example](missing.md)\n```', result)
        self.assertIn('href="/blog/posts/missing/"', result)
        self.assertIn('(Читать на английском)</span>', result)
        self.assertIn('data-language-link="" hreflang="en"', result)

    def test_message_keys_and_format_variables_match(self):
        english = messages("en")
        formatter = Formatter()
        for language in registry()["languages"]:
            localized = messages(language)
            self.assertEqual(set(english), set(localized), language)
            for key, value in english.items():
                baseline = value["other"] if isinstance(value, dict) else value
                if not isinstance(baseline, str):
                    continue
                fields = {field for _, field, _, _ in formatter.parse(baseline) if field}
                values = localized[key].values() if isinstance(localized[key], dict) else [localized[key]]
                for candidate in values:
                    self.assertEqual(fields, {field for _, field, _, _ in formatter.parse(candidate) if field}, (language, key))

    def test_russian_plural_forms(self):
        expected = {0: "0 статей", 1: "1 статья", 2: "2 статьи", 5: "5 статей",
                    11: "11 статей", 12: "12 статей", 21: "21 статья", 22: "22 статьи", 111: "111 статей"}
        for count, label in expected.items():
            self.assertEqual(translate(messages("ru"), "{count} articles", "ru", count=count), label)

    def test_article_identity_and_executable_examples_match(self):
        posts = list((ROOT / "translations/ru/blog/posts").glob("*.md"))
        self.assertGreater(len(posts), 0)
        for translated in posts:
            original = ROOT / "docs/blog/posts" / translated.name
            english, _ = read_article(original)
            russian, _ = read_article(translated, "ru")
            for key in ("id", "url", "date", "categories", "topics", "tags"):
                self.assertEqual(english[key], russian[key], (translated.name, key))
            pattern = r"(?m)^```python\n(.*?)^```"
            self.assertEqual(re.findall(pattern, original.read_text(encoding="utf-8"), re.S),
                             re.findall(pattern, translated.read_text(encoding="utf-8"), re.S), translated.name)
            self.assertRegex(russian["title"], r"[А-Яа-я]")
            self.assertNotIn("{#", russian["title"], translated.name)
            self.assertNotIn("{#", russian["search"], translated.name)

    def test_install_commands_are_not_translated_or_truncated(self):
        for relative in ("libraries/index.md", "tools/index.md"):
            original = (ROOT / "docs" / relative).read_text(encoding="utf-8")
            translated = (ROOT / "translations/ru" / relative).read_text(encoding="utf-8")
            pattern = r"<code>((?:uv |pip ).*?)</code>"
            self.assertEqual(re.findall(pattern, original), re.findall(pattern, translated))

    def test_catalog_is_language_specific(self):
        catalog = json.loads((ROOT / "translations/ru/blog/catalog.json").read_text(encoding="utf-8"))
        translated = {path.stem for path in (ROOT / "translations/ru/blog/posts").glob("*.md")}
        self.assertEqual({article["id"] for article in catalog["articles"]}, translated)
        self.assertEqual(catalog["language"], "ru")
        self.assertEqual({item["id"] for item in catalog["categories"]}, {"design", "libraries", "tools", "tutorials", "meta"})

    def test_output_cannot_replace_source_directories(self):
        for directory in (ROOT, ROOT / "docs", ROOT / "translations", ROOT / "build", ROOT / "build/../docs"):
            with self.assertRaises(ValueError):
                safe_output(directory)
        self.assertEqual(safe_output(ROOT / "build/verification"), ROOT / "build/verification")

    def test_validation_catches_cross_language_404s(self):
        with tempfile.TemporaryDirectory() as temporary:
            public = Path(temporary)
            (public / "index.html").write_text('<a href="/ru/">Русский</a>', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Broken internal links"):
                validate_links(public)
            (public / "ru").mkdir()
            (public / "ru/index.html").write_text('<a href="/">English</a>', encoding="utf-8")
            validate_links(public)

    def test_failed_build_keeps_the_last_successful_site(self):
        (ROOT / "build").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as temporary:
            output = Path(temporary) / "preview"
            output.mkdir()
            sentinel = output / "index.html"
            sentinel.write_text("last successful build", encoding="utf-8")
            with patch("build_site.build_catalog"), patch("build_site.prepare", side_effect=RuntimeError("Invalid source")):
                with self.assertRaisesRegex(RuntimeError, "Invalid source"):
                    build(output)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "last successful build")

    def test_sitemap_contains_both_languages_without_duplicates(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sites = [root / "en", root / "ru"]
            for site in sites:
                site.mkdir()
                (site / "sitemap.xml").write_text(
                    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                    '<url><loc>https://example.org/</loc></url>'
                    + ('<url><loc>https://example.org/ru/</loc></url>' if site.name == 'ru' else '')
                    + '</urlset>', encoding="utf-8")
            articles = ["https://example.org/blog/posts/article/", "https://example.org/ru/blog/posts/article/"]
            combine_sitemaps(root, sites, ["https://example.org/", *articles])
            xml = (root / "sitemap.xml").read_text(encoding="utf-8")
            self.assertEqual(xml.count('<loc>https://example.org/</loc>'), 1)
            self.assertEqual(xml.count('<loc>https://example.org/ru/</loc>'), 1)
            for url in articles:
                self.assertEqual(xml.count(f'<loc>{url}</loc>'), 1)

    def test_publishing_removes_deleted_translations(self):
        (ROOT / "build").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as temporary:
            root = Path(temporary)
            output, prepared, previous = root / "output", root / "prepared", root / "previous"
            (output / "ru/deleted-article").mkdir(parents=True)
            (output / "ru/deleted-article/index.html").write_text("removed translation", encoding="utf-8")
            prepared.mkdir()
            (prepared / "index.html").write_text("new edition", encoding="utf-8")
            publish(prepared, output, previous)
            self.assertFalse((output / "ru/deleted-article/index.html").exists())
            self.assertEqual((output / "index.html").read_text(encoding="utf-8"), "new edition")

    def test_failed_directory_swap_restores_previous_output(self):
        (ROOT / "build").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as temporary:
            root = Path(temporary)
            output, prepared, previous = root / "output", root / "prepared", root / "previous"
            output.mkdir()
            prepared.mkdir()
            (output / "index.html").write_text("previous edition", encoding="utf-8")
            rename = Path.rename

            def fail_new_output(path, target):
                if path == prepared:
                    raise PermissionError("Directory is locked")
                return rename(path, target)

            with patch.object(Path, "rename", fail_new_output):
                with self.assertRaises(PermissionError):
                    publish(prepared, output, previous)
            self.assertEqual((output / "index.html").read_text(encoding="utf-8"), "previous edition")


if __name__ == "__main__":
    unittest.main()
