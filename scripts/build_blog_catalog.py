#!/usr/bin/env python3
"""Build the blog directory and its search data from post Markdown front matter."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import math
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

import markdown
import yaml

from site_i18n import messages, registry, translate

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "docs" / "blog"
START = "<!-- catalog:articles:start -->"
END = "<!-- catalog:articles:end -->"
TOPICS = {
    "postgres": "PostgreSQL & SQLAlchemy",
    "reliability": "HTTP & resilience",
    "grpc": "gRPC",
    "messaging": "Kafka & messaging",
    "lifecycle": "Service lifecycle",
    "redis": "Redis & idempotency",
    "engineering": "Python & tooling",
}
LIBRARY_TOPICS = {
    "pg-partsmith": "postgres",
    "alembic-gauntlet": "postgres",
    "sqlalchemy-foundation-kit": "postgres",
    "clientwright": "reliability",
    "deadline-budget": "reliability",
    "grpc-client-kit": "grpc",
    "grpc-server-kit": "grpc",
    "omni-box": "messaging",
    "aiokafka-foundation-kit": "messaging",
    "servicewright": "lifecycle",
    "redis-client-kit": "redis",
    "idempotency-kit": "redis",
    "mr-review": "engineering",
    "python-library-template": "engineering",
}
TECHNOLOGY_TOPICS = {
    "postgresql": "postgres",
    "sqlalchemy": "postgres",
    "alembic": "postgres",
    "pgbouncer": "postgres",
    "http": "reliability",
    "httpx": "reliability",
    "reliability": "reliability",
    "grpc": "grpc",
    "kafka": "messaging",
    "aiokafka": "messaging",
    "outbox": "messaging",
    "inbox": "messaging",
    "lifecycle": "lifecycle",
    "redis": "redis",
    "idempotency": "redis",
}


class PlainText(HTMLParser):
    """Extract visible text without carrying Markdown or embedded HTML into search."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.hidden += 1
        if tag in {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th"}:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"}:
            self.hidden = max(0, self.hidden - 1)
        if tag in {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th"}:
            self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.parts.append(data)


def plain_text(source: str) -> str:
    parser = PlainText()
    parser.feed(markdown.markdown(source, extensions=["fenced_code", "tables", "attr_list"]))
    return " ".join("".join(parser.parts).split())


def summarize(body: str, limit: int = 180) -> str:
    intro = body.split("<!-- more -->", 1)[0]
    intro = re.sub(r"^#\s+.+$", "", intro, flags=re.MULTILINE)
    intro = re.sub(r"<div\b[^>]*class=[\"'][^\"']*bdr-post__hero[^\"']*[\"'][^>]*>.*?</div>", "", intro, flags=re.DOTALL)
    paragraphs = [plain_text(part) for part in re.split(r"\n\s*\n", intro)]
    summary = next((part for part in paragraphs if part), "")
    if len(summary) <= limit:
        return summary
    sentences = list(re.finditer(r"[.!?](?=\s)", summary[: limit + 1]))
    if sentences and sentences[-1].end() >= limit // 2:
        return summary[: sentences[-1].end()]
    return summary[: limit - 1].rsplit(" ", 1)[0].rstrip(",;:") + "…"


def article_topics(title: str, tags: list[str]) -> list[str]:
    normalized = [tag.casefold() for tag in tags]
    # Ecosystem and packaging pieces mention many dependencies as examples.
    if (normalized and normalized[0] in {"bedrock-python", "python-library-template", "mr-review"}) or "packaging" in normalized:
        return ["engineering"]
    topics = list(dict.fromkeys(LIBRARY_TOPICS[tag] for tag in normalized if tag in LIBRARY_TOPICS))
    # Explicit title subjects are useful secondary topics; incidental body tags are not.
    title_words = set(re.findall(r"[\w-]+", title.casefold()))
    for tag, topic in TECHNOLOGY_TOPICS.items():
        if tag in normalized and (not topics or tag in title_words) and topic not in topics:
            topics.append(topic)
    return topics or ["engineering"]


def reading_minutes(body: str) -> int:
    code_blocks = re.findall(r"^(`{3,}|~{3,})([^\n]*)\n(.*?)^\1\s*$", body, flags=re.MULTILINE | re.DOTALL)
    prose = re.sub(r"^(`{3,}|~{3,})[^\n]*\n.*?^\1\s*$", "", body, flags=re.MULTILINE | re.DOTALL)
    prose_words = len(re.findall(r"\b[\w'-]+\b", plain_text(prose)))
    code_words = sum(len(re.findall(r"\b\w+\b", code)) for _, language, code in code_blocks
                     if language.strip() != "mermaid")
    # Code contributes to reading time without counting punctuation as prose.
    # Diagram source is rendered visually; its visible caption is counted above.
    return max(1, math.ceil((prose_words + code_words * 0.5) / 220))


def slug(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", label.casefold()).strip("-")


def read_article(path: Path, language: str = "en") -> tuple[dict, dict[str, str]]:
    text = messages(language)
    source = path.read_text(encoding="utf-8-sig")
    front_matter = re.match(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", source, flags=re.DOTALL)
    if not front_matter:
        raise ValueError(f"{path}: missing YAML front matter")
    metadata = yaml.safe_load(front_matter[1])
    body = front_matter[2]
    heading = re.search(r"^#\s+(.+)$", body, flags=re.MULTILINE)
    if not heading:
        raise ValueError(f"{path}: missing article title")
    title = plain_text(heading[0])
    date = metadata.get("date")
    if isinstance(date, dt.datetime):
        date = date.date()
    elif not isinstance(date, dt.date):
        date = dt.date.fromisoformat(str(date))
    labels = {slug(str(label)): text.get(str(label), str(label)) for label in metadata.get("categories", [])}
    tags = [str(tag) for tag in metadata.get("tags", [])]
    description = summarize(body)
    headings = plain_text("\n\n".join(re.findall(r"^#{2,6}\s+.+$", body, flags=re.MULTILINE)))
    topics = article_topics(title, tags)
    # Topic IDs follow the source article even when translated title words differ.
    original = BLOG / "posts" / path.name
    if language != "en" and original.exists():
        topics = read_article(original)[0]["topics"]
    return {
        "id": path.stem,
        "title": title,
        "description": description,
        "url": f"posts/{path.stem}/",
        "date": date.isoformat(),
        "categories": list(labels),
        "tags": tags,
        "topics": topics,
        "minutes": reading_minutes(body),
        "search": " ".join([title, description, *tags, *labels.values(), *(text[TOPICS[topic]] for topic in topics), headings]),
    }, labels


def render_article(article: dict, categories: dict[str, str], language: str = "en") -> str:
    text = messages(language)
    escaped = {key: html.escape(str(article[key]), quote=True) for key in ("id", "url", "title", "description", "date", "minutes")}
    topic = html.escape(text[TOPICS[article["topics"][0]]])
    category = html.escape(categories[article["categories"][0]]) if article["categories"] else text["Article"]
    date = dt.date.fromisoformat(article["date"])
    display_date = text["date_format"].format(month=text["months"][date.month - 1], day=date.day, year=date.year)
    reading_time = translate(text, "{minutes} min read", minutes=article["minutes"])
    return f'''  <article class="bdr-entry" data-article-id="{escaped['id']}">
    <a class="bdr-entry__link bdr-card" href="{escaped['url']}">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">{topic} <span>·</span> {category}</div>
        <h3 class="bdr-entry__title">{escaped['title']}</h3>
        <p class="bdr-entry__description">{escaped['description']}</p>
        <div class="bdr-entry__meta"><time datetime="{escaped['date']}">{display_date}</time><span>·</span><span>{reading_time}</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>'''


def directory_pages(blog: Path, articles: list[dict], language: str) -> dict[Path, str]:
    text = messages(language)
    labels = {slug(label): text[label] for label in ("Libraries", "Tools", "Design", "Tutorials", "Meta")}
    archive = [f"# {text['Archive']}", "", text["archive_intro"], ""]
    last_year = None
    for article in articles:
        year = article["date"][:4]
        if year != last_year:
            archive.extend([f"## {year}", ""])
            last_year = year
        title = html.escape(article['title'])
        archive.append(f"- **{article['date']}** — [{title}](../posts/{article['id']}.md)")
    overview = [f"# {text['Categories']}", "", text["categories_intro"], "",
                f'<nav class="bdr-category-grid" aria-label="{text["Blog categories"]}" markdown="0">']
    outputs = {blog / "archive/index.md": "\n".join(archive) + "\n"}
    for key, label in labels.items():
        matching = [article for article in articles if key in article["categories"]]
        count = translate(text, "{count} articles", language, count=len(matching))
        description = text[f"category_{key}"]
        overview.append(f'  <a class="bdr-category-card" href="{key}/"><span><strong>{label}</strong><small>{count}</small></span><p>{description}</p><span class="bdr-category-card__arrow" aria-hidden="true">↗</span></a>')
        content = [f"# {label}", "", description, ""]
        content.extend(f"- **{article['date']}** — [{html.escape(article['title'])}](../posts/{article['id']}.md)" for article in matching)
        if not matching:
            content.extend([text["category_empty"], "", f'[{text["All articles"]}](../index.md)'])
        outputs[blog / "category" / f"{key}.md"] = "\n".join(content) + "\n"
    outputs[blog / "category/index.md"] = "\n".join([*overview, "</nav>", ""])
    return outputs


def build_catalog(blog: Path, language: str = "en", check: bool = False) -> list[str]:
    text = messages(language)
    articles = []
    categories = {slug(label): text[label] for label in ("Libraries", "Tools", "Design", "Tutorials", "Meta")}
    for path in sorted((blog / "posts").glob("*.md")):
        article, labels = read_article(path, language)
        articles.append(article)
        categories.update(labels)
    articles.sort(key=lambda article: (-dt.date.fromisoformat(article["date"]).toordinal(), article["title"].casefold()))
    catalog = {
        "articles": articles,
        "language": language,
        "topics": [{"id": key, "label": text[label]} for key, label in TOPICS.items()],
        "categories": [{"id": key, "label": label} for key, label in sorted(categories.items())],
    }
    index_path = blog / "index.md"
    index = index_path.read_text(encoding="utf-8-sig")
    if index.count(START) != 1 or index.count(END) != 1 or index.index(END) < index.index(START):
        raise ValueError("docs/blog/index.md must contain one ordered pair of catalog:articles markers")
    before, remainder = index.split(START, 1)
    _, after = remainder.split(END, 1)
    generated = "\n" + "\n".join(render_article(article, categories, language) for article in articles) + "\n"
    outputs = {
        blog / "catalog.json": json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        index_path: before + START + generated + END + after,
        **directory_pages(blog, articles, language),
    }
    stale = []
    home = blog.parent / "index.md"
    home_source = home.read_text(encoding="utf-8")
    home_start, home_end = "<!-- catalog:home:start -->", "<!-- catalog:home:end -->"
    if home_start in home_source and home_end in home_source:
        cards = []
        for article in articles[:3]:
            cards.append(f'''<a class="bdr-card" href="blog/{html.escape(article['url'])}">
  <div class="bdr-card__visual" aria-hidden="true"></div>
  <div class="bdr-card__eyebrow">{html.escape(categories[article['categories'][0]])}</div>
  <h3 class="bdr-card__title">{html.escape(article['title'])}</h3>
  <p class="bdr-card__lede">{html.escape(article['description'])}</p>
  <div class="bdr-card__meta">{article['date']}</div>
</a>''')
        before, remainder = home_source.split(home_start, 1)
        _, after = remainder.split(home_end, 1)
        outputs[home] = before + home_start + "\n" + "\n".join(cards) + "\n" + home_end + after
    for path, content in outputs.items():
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            stale.append(str(path))
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8", newline="\n")
    print(f"[{language}] Blog catalog {'checked' if check else 'generated'}: {len(articles)} articles, {len(TOPICS)} topics.")
    return stale


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated files need updating; do not write files.")
    parser.add_argument("--language", help="Generate one language; by default generate all enabled editions.")
    args = parser.parse_args()
    languages = registry()["languages"]
    if args.language and args.language not in languages:
        parser.error(f"Unknown language: {args.language}")
    stale = []
    for code, language in languages.items():
        if args.language and args.language != code:
            continue
        stale.extend(build_catalog(ROOT / language["source"] / "blog", code, args.check))
    if args.check and stale:
        print("Blog catalog is stale: " + ", ".join(stale), file=sys.stderr)
        print("Run: uv run --no-dev --group docs python scripts/build_blog_catalog.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
