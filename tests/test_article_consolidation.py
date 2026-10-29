"""Retired article URLs and lab links remain usable after consolidation."""

import json
import re
import unittest
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
GROUPS = json.loads((ROOT / "plans/article-consolidation.json").read_text(encoding="utf-8"))["groups"]


class ArticleConsolidation(unittest.TestCase):
    def test_retired_urls_have_localized_redirects_and_fragment_targets(self):
        for language, tree, prefix in [("en", "docs", ""), ("ru", "translations/ru", "/ru")]:
            posts = ROOT / tree / "blog/posts"
            for group in GROUPS:
                source = (posts / (group["slug"] + ".md")).read_text(encoding="utf-8")
                rendered = markdown.markdown(source, extensions=["toc", "attr_list", "tables", "pymdownx.superfences"])
                ids = re.findall(r'\bid="([^"]+)"', rendered)
                self.assertEqual(len(ids), len(set(ids)), (language, group["slug"]))
                for old in group["sources"]:
                    with self.subTest(language=language, retired=old):
                        self.assertFalse((posts / (old + ".md")).exists())
                        redirect = (posts / old / "index.html").read_text(encoding="utf-8")
                        self.assertIn(f'<html lang="{language}">', redirect)
                        self.assertIn('name="robots" content="noindex"', redirect)
                        self.assertIn(f'rel="canonical" href="https://bedrock-python.github.io{prefix}/blog/posts/{group["slug"]}/"', redirect)
                        self.assertIn(f'href="../{group["slug"]}/"', redirect)
                        self.assertIn("location.search + location.hash", redirect)
                        self.assertTrue(set(group["legacy_anchors"][old]).issubset(ids), old)

    def test_combined_articles_keep_links_to_their_original_labs(self):
        for tree in ("docs", "translations/ru"):
            for group in GROUPS:
                source = (ROOT / tree / "blog/posts" / (group["slug"] + ".md")).read_text(encoding="utf-8")
                for lab in group["labs"]:
                    self.assertTrue((ROOT / tree / "blog/lab" / lab / "README.md").is_file(), lab)
                    self.assertIn(f"(../lab/{lab}/README.md)", source)
                self.assertNotIn("{{diagram}}", source)
                self.assertNotIn("{{code}}", source)


if __name__ == "__main__":
    unittest.main()
