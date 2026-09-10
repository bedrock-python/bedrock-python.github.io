"""Keep article diagrams translated, accessible, and compatible with Markdown."""

import html
import re
import unittest
import sys
import gzip
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import markdown
from pymdownx.superfences import fence_code_format

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_blog_catalog import reading_minutes
from build_site import combine_sitemaps
FIGURE = re.compile(r'<figure class="bdr-diagram"[^>]*>.*?</figure>', re.S)
MERMAID = re.compile(r'(?ms)^```mermaid\n(.*?)^```')


class ArticleDiagrams(unittest.TestCase):
    def test_edition_sitemap_includes_articles_for_instant_navigation(self):
        with tempfile.TemporaryDirectory() as temporary:
            edition = Path(temporary)
            namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
            (edition / "sitemap.xml").write_text(
                f'<urlset xmlns="{namespace}"><url><loc>https://example.org/ru/</loc></url></urlset>',
                encoding="utf-8",
            )
            urls = ["https://example.org/ru/", "https://example.org/ru/blog/posts/example/",
                    "https://example.org/ru/blog/lab/example/"]
            combine_sitemaps(edition, [edition], urls)
            content = (edition / "sitemap.xml").read_bytes()
            actual = [entry.findtext(f"{{{namespace}}}loc") for entry in ET.fromstring(content)]
            self.assertCountEqual(actual, urls)
            self.assertEqual(gzip.decompress((edition / "sitemap.xml.gz").read_bytes()), content)

    def test_diagram_syntax_does_not_inflate_reading_time(self):
        prose = "Explanation " * 250 + "\n\n"
        source = "node --> next\n" * 500
        self.assertEqual(reading_minutes(prose), reading_minutes(prose + "```mermaid\n" + source + "```\n"))
        self.assertGreater(reading_minutes(prose + "```python\n" + source + "```\n"), reading_minutes(prose))

    def test_every_article_has_diagrams_in_both_editions(self):
        for source in sorted((ROOT / "docs/blog/posts").glob("*.md")):
            translated = ROOT / "translations/ru/blog/posts" / source.name
            with self.subTest(article=source.name):
                english = MERMAID.findall(source.read_text(encoding="utf-8"))
                russian = MERMAID.findall(translated.read_text(encoding="utf-8"))
                self.assertTrue(english, "Explain at least one concept visually")
                self.assertEqual(len(english), len(russian))

    def test_diagrams_have_localized_descriptions_and_render_as_native_fences(self):
        for tree in ("docs", "translations/ru"):
            for path in (ROOT / tree / "blog/posts").glob("*.md"):
                source = path.read_text(encoding="utf-8")
                figures = FIGURE.findall(source)
                self.assertEqual(len(figures), len(MERMAID.findall(source)), path.name)
                for figure in figures:
                    with self.subTest(language=tree, article=path.name):
                        diagram = MERMAID.search(figure).group(1)
                        title = re.search(r"(?m)^\s*accTitle: (.+)$", diagram)
                        description = re.search(r"(?m)^\s*accDescr: (.+)$", diagram)
                        self.assertIsNotNone(title)
                        self.assertIsNotNone(description)
                        self.assertIn(f"<strong>{html.escape(title[1])}</strong>", figure)
                        self.assertIn(f'>{html.escape(description[1])}</p>', figure)
                        if tree == "translations/ru":
                            self.assertRegex(title[1], r"[А-Яа-яЁё]")
                            self.assertRegex(description[1], r"[А-Яа-яЁё]")
                        rendered = markdown.markdown(
                            figure,
                            extensions=["md_in_html", "pymdownx.superfences"],
                            extension_configs={"pymdownx.superfences": {
                                "custom_fences": [{"name": "mermaid", "class": "mermaid",
                                                   "format": fence_code_format}],
                            }},
                        )
                        self.assertIn('<pre class="mermaid">', rendered)
                        self.assertIn('class="bdr-diagram__caption"', rendered)
                        self.assertNotIn("```", rendered)
