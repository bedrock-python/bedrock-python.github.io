#!/usr/bin/env python3
"""Build or preview all language editions with isolated Zensical caches."""

from __future__ import annotations

import argparse
import copy
import gzip
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import tomllib
import xml.etree.ElementTree as ET
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

import yaml

from build_blog_catalog import build_catalog
from site_i18n import ROOT, language_root, messages, page_url, registry


def translated_nav(value, text):
    if isinstance(value, list):
        return [translated_nav(item, text) for item in value]
    if isinstance(value, dict):
        return {text.get(key, key): translated_nav(item, text) for key, item in value.items()}
    return value


def inventory(languages: dict) -> dict[str, set[str]]:
    return {code: {path.relative_to(ROOT / language["source"]).as_posix()
                   for path in (ROOT / language["source"]).rglob("*.md")}
            for code, language in languages.items()}


def translation_map(pages: dict, languages: dict, site_url: str) -> dict:
    origin = urlsplit(site_url)
    base_path = origin.path.rstrip("/") + "/"
    result = {}
    for code, sources in pages.items():
        root = language_root(languages[code], base_path)
        for source in sources:
            url = page_url(source)
            if url == "404.html":
                continue
            result.setdefault(url, {})[code] = {
                "path": root + url,
                "canonical": f"{origin.scheme}://{origin.netloc}{root}{url}",
            }
    return result


def rewrite_missing_links(source: str, relative: str, available: set[str], originals: set[str], base: str, text: dict) -> str:
    """Label links to untranslated Markdown/pages and point to the source edition."""
    original_urls = {page_url(path): path for path in originals}

    def fallback(value: str, markdown_link: bool = False) -> str | None:
        parts = urlsplit(html.unescape(value))
        if parts.scheme or parts.netloc or not parts.path or parts.path.startswith("/"):
            return None
        if markdown_link and parts.path.endswith(".md"):
            resolved = urljoin("/" + relative, parts.path).lstrip("/")
        else:
            resolved_url = urljoin("/" + page_url(relative), parts.path).lstrip("/")
            resolved = original_urls.get(resolved_url.removesuffix("index.html"))
        if not resolved or resolved not in originals or resolved in available:
            return None
        suffix = ("?" + parts.query if parts.query else "") + ("#" + parts.fragment if parts.fragment else "")
        return base + page_url(resolved) + suffix

    def markdown_link(match):
        destination = fallback(match[2], markdown_link=True)
        return f'[{match[1]} ({text["Read in English"]})]({destination}){{: data-language-link="" hreflang="en" }}' if destination else match[0]

    # Code is content: never rewrite example Markdown or HTML inside code fences.
    chunks = re.split(r"(^`{3,}[^\n]*\n.*?^`{3,}\s*$|^~{3,}[^\n]*\n.*?^~{3,}\s*$)", source, flags=re.M | re.S)
    for index in range(0, len(chunks), 2):
        chunk = re.sub(r"(?<!!)\[([^\]\n]+)\]\(([^\s)]+)\)", markdown_link, chunks[index])

        def html_link(match):
            destination = fallback(match[2])
            if not destination:
                return match[0]
            attributes = match[3][:-1] + ' data-language-link="" hreflang="en">'
            return f'{match[1]}{html.escape(destination, quote=True)}{attributes}{match[4]} <span class="bdr-english-label">({text["Read in English"]})</span></a>'

        chunks[index] = re.sub(r'(<a\b[^>]*\bhref=")([^"]+)("[^>]*>)(.*?)</a>', html_link, chunk, flags=re.S)
    return "".join(chunks)


def coverage(pages: dict, default: str) -> dict:
    originals = pages[default]
    return {code: {
        "translated_pages": len(sources & originals),
        "total_pages": len(originals),
        "translated_articles": len([name for name in sources & originals if name.startswith("blog/posts/")]),
        "total_articles": len([name for name in originals if name.startswith("blog/posts/")]),
        "missing": sorted(originals - sources),
    } for code, sources in pages.items()}


def prepare(work: Path, language: str, data: dict, pages: dict, config: dict, pairs: dict) -> Path:
    settings = data["languages"][language]
    text = messages(language)
    default = data["default"]
    destination = work / language
    docs = destination / "docs"
    shutil.copytree(ROOT / settings["source"], docs)
    if language != default:
        # Copy shared files, never English Markdown or the English article index.
        english = ROOT / data["languages"][default]["source"]
        for path in english.rglob("*"):
            if not path.is_file() or path.suffix == ".md" or path.name == "catalog.json":
                continue
            target = docs / path.relative_to(english)
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
        base_path = urlsplit(config["site_url"]).path.rstrip("/") + "/"
        for relative in pages[language]:
            path = docs / relative
            path.write_text(rewrite_missing_links(path.read_text(encoding="utf-8"), relative,
                            pages[language], pages[default], base_path, text), encoding="utf-8")
    shutil.copytree(ROOT / "overrides", destination / "overrides")
    project = copy.deepcopy(config)
    base_path = urlsplit(config["site_url"]).path.rstrip("/") + "/"
    locale_root = language_root(settings, base_path)
    project.update({
        "site_url": config["site_url"].rstrip("/") + "/" + (settings["prefix"] + "/" if settings["prefix"] else ""),
        "site_description": text["site_description"],
        "docs_dir": "docs", "site_dir": "site",
        "edit_uri": f'edit/master/{settings["source"]}/',
        "nav": translated_nav(config["nav"], text),
    })
    project["theme"]["language"] = language
    for palette in project["theme"].get("palette", []):
        toggle = palette.get("toggle", {})
        if "name" in toggle:
            toggle["name"] = text[toggle["name"]]
    extra = project.setdefault("extra", {})
    extra["scope"] = base_path  # Share the explicit color preference across editions.
    extra["alternate"] = [{"name": item["name"], "lang": code, "link": language_root(item, base_path)}
                          for code, item in data["languages"].items()]
    extra["i18n"] = {"default": default, "locale": settings["locale"], "root": locale_root,
                     "messages": text, "pages": pairs,
                     "partial": len(pages[language]) < len(pages[default]),
                     "original_blog": base_path + "blog/"}
    # Zensical natively accepts MkDocs YAML; generate it from the single TOML
    # configuration so each edition does not need a maintained configuration copy.
    config_path = destination / "mkdocs.yml"
    config_path.write_text(yaml.safe_dump(project, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return config_path


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        key = "href" if tag == "a" else "src" if tag in {"img", "script"} else None
        if key and attributes.get(key):
            self.links.append(attributes[key])


def validate_links(public: Path, base_path: str = "/") -> None:
    errors = []
    for path in public.rglob("*.html"):
        parser = Links()
        parser.feed(path.read_text(encoding="utf-8"))
        current = base_path + path.relative_to(public).as_posix()
        for value in parser.links:
            parts = urlsplit(value)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            url = unquote(urlsplit(urljoin(current, value)).path)
            if not url.startswith(base_path):
                continue
            target = public / url[len(base_path):]
            if not target.exists() and not (target / "index.html").exists():
                errors.append(f"{path.relative_to(public)} -> {value}")
    if errors:
        raise ValueError("Broken internal links:\n" + "\n".join(errors[:40]))


def combine_sitemaps(public: Path, language_outputs: list[Path], page_urls: list[str] | None = None) -> None:
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    result = ET.Element(f"{{{namespace}}}urlset")
    seen = set()
    for output in language_outputs:
        for entry in ET.parse(output / "sitemap.xml").getroot():
            url = entry.findtext(f"{{{namespace}}}loc")
            if url not in seen:
                result.append(entry)
                seen.add(url)
    # Zensical's sitemap omits pages outside navigation, including our articles
    # and labs. The published translation map also contains those pages.
    for url in sorted(page_urls or []):
        if url not in seen:
            entry = ET.SubElement(result, f"{{{namespace}}}url")
            ET.SubElement(entry, f"{{{namespace}}}loc").text = url
            seen.add(url)
    content = ET.tostring(result, encoding="utf-8", xml_declaration=True)
    (public / "sitemap.xml").write_bytes(content)
    (public / "sitemap.xml.gz").write_bytes(gzip.compress(content, mtime=0))


def safe_output(path: Path) -> Path:
    target = path.resolve()
    if target != ROOT / "site" and not target.is_relative_to(ROOT / "build"):
        raise ValueError("Output must be 'site' or a directory inside this repository's 'build/'")
    if target == ROOT / "build":
        raise ValueError("Choose a subdirectory of build/ for output")
    return target


def publish(public: Path, output: Path, previous: Path) -> None:
    """Swap fully built directories on the same filesystem; restore on failure."""
    output = safe_output(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.rename(previous)
    try:
        public.rename(output)
    except OSError:
        if previous.exists():
            previous.rename(output)
        raise


def build(output: Path) -> dict:
    output = safe_output(output)
    data = registry()
    for code, settings in data["languages"].items():
        build_catalog(ROOT / settings["source"] / "blog", code)
    pages = inventory(data["languages"])
    default = data["default"]
    for code in data["languages"]:
        if set(messages(code)) != set(messages(default)):
            raise ValueError(f"[{code}] Interface message keys must match {default}")
        if pages[code] - pages[default]:
            raise ValueError(f"[{code}] Pages have no source counterpart: {sorted(pages[code] - pages[default])}")
    report = coverage(pages, default)
    config = tomllib.loads((ROOT / "zensical.toml").read_text(encoding="utf-8"))["project"]
    pairs = translation_map(pages, data["languages"], config["site_url"])
    (ROOT / "build").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="editions-", dir=ROOT / "build") as temporary:
        work = Path(temporary)
        public = work / "public"
        public.mkdir()
        outputs = []
        # Default must be copied first even if the registry is reordered.
        order = [default, *(code for code in data["languages"] if code != default)]
        for code in order:
            config_path = prepare(work, code, data, pages, config, pairs)
            subprocess.run([sys.executable, "-m", "zensical", "build", "--clean", "-f", str(config_path)],
                           cwd=config_path.parent, check=True)
            built = config_path.parent / "site"
            # Instant navigation reads this edition's sitemap, not the combined
            # root sitemap. Include articles and labs before copying either one.
            combine_sitemaps(built, [built], [editions[code]["canonical"]
                                             for editions in pairs.values() if code in editions])
            outputs.append(built)
            prefix = data["languages"][code]["prefix"]
            if prefix and (public / prefix).exists():
                raise ValueError(f"Language prefix collides with default content: {prefix}")
            shutil.copytree(built, public / prefix, dirs_exist_ok=True)
        combine_sitemaps(public, outputs, [page["canonical"] for editions in pairs.values() for page in editions.values()])
        base_path = urlsplit(config["site_url"]).path.rstrip("/") + "/"
        validate_links(public, base_path)
        # All paths are on the repository filesystem. Renaming avoids serving a
        # half-copied tree and retains the previous output if publication fails.
        publish(public, output, work / "previous-output")
    (ROOT / "build/translation-coverage.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for code, item in report.items():
        print(f"[{code}] {item['translated_articles']}/{item['total_articles']} articles; {item['translated_pages']}/{item['total_pages']} pages", flush=True)
    print(f"Built all editions: {output}", flush=True)
    return report


def fingerprint() -> tuple:
    roots = [ROOT / "docs", ROOT / "translations", ROOT / "i18n", ROOT / "overrides", ROOT / "scripts"]
    paths = [ROOT / "zensical.toml"]
    for root in roots:
        paths.extend(path for path in root.rglob("*") if path.is_file() and "__pycache__" not in path.parts)
    result = []
    for path in sorted(paths):
        try:
            status = path.stat()
        except FileNotFoundError:
            continue  # Editors may atomically replace a file while scanning.
        result.append((str(path), status.st_mtime_ns, status.st_size))
    return tuple(result)


def serve(output: Path, host: str, port: int) -> None:
    server = ThreadingHTTPServer((host, port), partial(SimpleHTTPRequestHandler, directory=str(output)))
    stop = threading.Event()

    def watch():
        previous = fingerprint()
        while not stop.wait(0.6):
            current = fingerprint()
            if current == previous:
                continue
            time.sleep(0.2)
            try:
                # A fresh process also picks up changes to the Python build
                # scripts rather than reusing modules imported by this server.
                subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "scripts/build_site.py"),
                                "--output", str(output)], cwd=ROOT, check=True)
                print("Preview updated. Refresh your browser.", flush=True)
            except Exception as error:
                print(f"Build failed; the last successful preview is kept: {error}", file=sys.stderr, flush=True)
            # Edits made during the build must trigger another pass. Generated
            # catalog changes can cause one extra pass, then the inputs settle.
            previous = current

    thread = threading.Thread(target=watch, daemon=True)
    thread.start()
    print(f"Preview: http://{host}:{port}/ and http://{host}:{port}/ru/ (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        server.server_close()
        thread.join()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true", help="Watch sources and serve both languages; refresh after rebuilds.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--output", type=Path, help="Output directory: site or a subdirectory of build/.")
    args = parser.parse_args()
    output = safe_output(args.output or ROOT / ("build/preview" if args.serve else "site"))
    build(output)
    if args.serve:
        serve(output, args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
