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
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


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
    parser.feed(markdown.markdown(source, extensions=["fenced_code", "tables"]))
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
    code_blocks = re.findall(r"^(`{3,}|~{3,})[^\n]*\n(.*?)^\1\s*$", body, flags=re.MULTILINE | re.DOTALL)
    prose = re.sub(r"^(`{3,}|~{3,})[^\n]*\n.*?^\1\s*$", "", body, flags=re.MULTILINE | re.DOTALL)
    prose_words = len(re.findall(r"\b[\w'-]+\b", plain_text(prose)))
    code_words = sum(len(re.findall(r"\b\w+\b", code)) for _, code in code_blocks)
    # Code contributes to reading time without counting punctuation as prose.
    return max(1, math.ceil((prose_words + code_words * 0.5) / 220))


def slug(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", label.casefold()).strip("-")


def read_article(path: Path) -> tuple[dict, dict[str, str]]:
    source = path.read_text(encoding="utf-8-sig")
    front_matter = re.match(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", source, flags=re.DOTALL)
    if not front_matter:
        raise ValueError(f"{path.relative_to(ROOT)}: missing YAML front matter")
    metadata = yaml.safe_load(front_matter[1])
    body = front_matter[2]
    heading = re.search(r"^#\s+(.+)$", body, flags=re.MULTILINE)
    if not heading:
        raise ValueError(f"{path.relative_to(ROOT)}: missing article title")
    title = plain_text(heading[1])
    date = metadata.get("date")
    if isinstance(date, dt.datetime):
        date = date.date()
    elif not isinstance(date, dt.date):
        date = dt.date.fromisoformat(str(date))
    labels = {slug(str(label)): str(label) for label in metadata.get("categories", [])}
    tags = [str(tag) for tag in metadata.get("tags", [])]
    description = summarize(body)
    headings = plain_text(" ".join(re.findall(r"^#{2,6}\s+(.+)$", body, flags=re.MULTILINE)))
    topics = article_topics(title, tags)
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
        "search": " ".join([title, description, *tags, *labels.values(), *(TOPICS[topic] for topic in topics), headings]),
    }, labels


def render_article(article: dict, categories: dict[str, str]) -> str:
    escaped = {key: html.escape(str(article[key]), quote=True) for key in ("id", "url", "title", "description", "date", "minutes")}
    topic = html.escape(TOPICS[article["topics"][0]])
    category = html.escape(categories[article["categories"][0]]) if article["categories"] else "Article"
    date = dt.date.fromisoformat(article["date"])
    display_date = f"{MONTHS[date.month - 1]} {date.day}, {date.year}"
    return f'''  <article class="bdr-entry" data-article-id="{escaped['id']}">
    <a class="bdr-entry__link bdr-card" href="{escaped['url']}">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">{topic} <span>·</span> {category}</div>
        <h3 class="bdr-entry__title">{escaped['title']}</h3>
        <p class="bdr-entry__description">{escaped['description']}</p>
        <div class="bdr-entry__meta"><time datetime="{escaped['date']}">{display_date}</time><span>·</span><span>{escaped['minutes']} min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated files need updating; do not write files.")
    args = parser.parse_args()
    articles = []
    categories: dict[str, str] = {}
    for path in sorted((BLOG / "posts").glob("*.md")):
        article, labels = read_article(path)
        articles.append(article)
        categories.update(labels)
    articles.sort(key=lambda article: (-dt.date.fromisoformat(article["date"]).toordinal(), article["title"].casefold()))
    catalog = {
        "articles": articles,
        "topics": [{"id": key, "label": label} for key, label in TOPICS.items()],
        "categories": [{"id": key, "label": label} for key, label in sorted(categories.items())],
    }
    index_path = BLOG / "index.md"
    index = index_path.read_text(encoding="utf-8-sig")
    if index.count(START) != 1 or index.count(END) != 1 or index.index(END) < index.index(START):
        raise ValueError("docs/blog/index.md must contain one ordered pair of catalog:articles markers")
    before, remainder = index.split(START, 1)
    _, after = remainder.split(END, 1)
    generated = "\n" + "\n".join(render_article(article, categories) for article in articles) + "\n"
    outputs = {
        BLOG / "catalog.json": json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        index_path: before + START + generated + END + after,
    }
    stale = []
    for path, content in outputs.items():
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            stale.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.write_text(content, encoding="utf-8", newline="\n")
    if args.check and stale:
        print("Blog catalog is stale: " + ", ".join(stale), file=sys.stderr)
        print("Run: uv run --no-dev --group docs python scripts/build_blog_catalog.py", file=sys.stderr)
        return 1
    print(f"Blog catalog {'checked' if args.check else 'generated'}: {len(articles)} articles, {len(TOPICS)} topics.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
