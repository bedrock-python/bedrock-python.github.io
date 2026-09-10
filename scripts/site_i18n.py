"""Shared language registry and messages for the documentation build."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path, PurePosixPath

from babel import Locale

ROOT = Path(__file__).resolve().parents[1]


def registry() -> dict:
    data = tomllib.loads((ROOT / "i18n/locales.toml").read_text(encoding="utf-8"))
    default = data["default"]
    languages = data["languages"]
    if default not in languages or languages[default]["prefix"]:
        raise ValueError("The default language must exist and use the root URL")
    prefixes = set()
    for code, language in languages.items():
        prefix = language["prefix"]
        if not re.fullmatch(r"[a-z]{2,3}(?:-[A-Za-z0-9]+)*", code):
            raise ValueError(f"Invalid language code: {code}")
        if prefix and not re.fullmatch(r"[a-zA-Z0-9-]+", prefix):
            raise ValueError(f"Invalid language prefix: {prefix}")
        if prefix in prefixes:
            raise ValueError(f"Duplicate language prefix: {prefix}")
        prefixes.add(prefix)
        source = (ROOT / language["source"]).resolve()
        if not source.is_relative_to(ROOT) or source == ROOT:
            raise ValueError(f"Language source must be inside the repository: {source}")
    return data


def messages(language: str) -> dict:
    path = ROOT / "i18n" / f"{language}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def plural_form(language: str, count: int) -> str:
    return Locale.parse(language, sep="-").plural_form(count)


def translate(catalog: dict, key: str, language: str = "en", **values) -> str:
    value = catalog[key]
    if isinstance(value, dict):
        value = value.get(plural_form(language, values["count"]), value["other"])
    return value.format(**values)


def page_url(source: str) -> str:
    path = PurePosixPath(source)
    if path.name.lower() in {"index.md", "readme.md"}:
        return "" if str(path.parent) == "." else f"{path.parent}/"
    if path.name == "404.md":
        return "404.html"
    return f"{path.with_suffix('')}/"


def language_root(language: dict, base_path: str = "/") -> str:
    return base_path.rstrip("/") + "/" + (language["prefix"] + "/" if language["prefix"] else "")
