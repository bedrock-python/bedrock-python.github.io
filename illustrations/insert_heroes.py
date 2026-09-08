#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Put each post's illustration at the top of its own page, under the title.

The image is a background on a div rather than an <img> so that the light and dark renders swap
with the theme toggle: the toggle sets `data-md-color-scheme` on the root, which a stylesheet can
follow but a <picture> element's media query cannot. A background carries no alt text, so the div
declares `role="img"` and takes its accessible name from the one-line idea recorded in the post's
prompt file.

    uv run insert_heroes.py --dry-run
    uv run insert_heroes.py

Idempotent: a post that already has a hero is left alone.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
POSTS = HERE.parent / "docs/blog/posts"


def idea_for(slug: str) -> str:
    prompt = HERE / f"{slug}.md"
    match = re.search(r"^- \*\*Idea:\*\* (.+)$", prompt.read_text(encoding="utf-8"), re.M)
    if not match:
        raise SystemExit(f"no Idea line in {prompt.name}")
    return match.group(1).strip().rstrip(".")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--posts", type=Path, default=POSTS)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    done = skipped = 0
    for path in sorted(args.posts.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if "bdr-post__hero" in text:
            skipped += 1
            continue
        heading = re.search(r"^# .+$", text, re.M)
        if not heading:
            raise SystemExit(f"no H1 in {path.name}")
        alt = idea_for(path.stem).replace('"', "'")
        hero = (f'\n\n<div class="bdr-post__hero" data-bdr-post="{path.stem}" '
                f'role="img" aria-label="{alt}" markdown="0"></div>')
        text = text[: heading.end()] + hero + text[heading.end():]
        if not args.dry_run:
            path.write_text(text, encoding="utf-8")
        print(f"  {path.stem[:56]:56} {alt[:60]}")
        done += 1

    verb = "would add" if args.dry_run else "added"
    print(f"\n{verb} {done} hero(es), {skipped} already had one")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
