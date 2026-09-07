#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["openai>=1.100", "pillow>=11.0"]
# ///
"""Generate one illustration per blog post from the prompt files in this directory.

Each `<post-slug>.md` here holds exactly one fenced ```text block: the prompt. This script
sends each of them to the OpenAI images API, crops the result to the 16:10 the blog cards
use, and writes `<post-slug>.png` plus a `<post-slug>.json` sidecar recording every
parameter the image was made with, so a regeneration is reproducible.

    export OPENAI_API_KEY=...
    uv run generate_images.py --dry-run          # what would be sent, no API calls
    uv run generate_images.py --only 2026-05-30-welcome
    uv run generate_images.py                    # all of them
    uv run generate_images.py --only '*kafka*' --variants 3 --force

Nothing is overwritten without --force, so an interrupted run resumes by re-running it.
"""

from __future__ import annotations

import argparse
import base64
import concurrent.futures
import dataclasses
import fnmatch
import json
import random
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROMPT_BLOCK = re.compile(r"^```text\n(.*?)^```", re.S | re.M)

# The API renders 3:2 (1536x1024); the blog cards are 16:10 (.bdr-card__visual).
CARD_RATIO = 16 / 10


@dataclasses.dataclass(frozen=True)
class Job:
    slug: str
    prompt: str
    title: str
    out: Path


@dataclasses.dataclass
class Outcome:
    slug: str
    status: str            # "ok" | "skipped" | "failed"
    detail: str = ""
    tokens: int = 0
    seconds: float = 0.0


def read_prompts(directory: Path, patterns: list[str]) -> list[tuple[str, str, str]]:
    """Return (slug, title, prompt) for every prompt file matching the patterns."""
    found = []
    for path in sorted(directory.glob("*.md")):
        if path.name == "README.md":
            continue
        if patterns and not any(
            fnmatch.fnmatch(path.stem, p) or p == path.stem for p in patterns
        ):
            continue
        text = path.read_text(encoding="utf-8")
        match = PROMPT_BLOCK.search(text)
        if not match:
            print(f"  ! {path.name}: no ```text prompt block, skipped", file=sys.stderr)
            continue
        title_match = re.search(r"^# (.+)$", text, re.M)
        title = title_match.group(1).strip() if title_match else path.stem
        found.append((path.stem, title, match.group(1).strip()))
    return found


def center_crop(data: bytes, ratio: float, fmt: str, also_webp: Path | None) -> bytes:
    """Crop bytes to `ratio` around the centre. Returns the original on any failure."""
    try:
        import io

        from PIL import Image
    except ImportError:
        print("  ! Pillow not available, image left at the API's aspect ratio", file=sys.stderr)
        return data

    with Image.open(io.BytesIO(data)) as im:
        w, h = im.size
        if abs(w / h - ratio) < 0.005:
            cropped = im.copy()
        elif w / h > ratio:                      # too wide -> trim left and right
            new_w = round(h * ratio)
            left = (w - new_w) // 2
            cropped = im.crop((left, 0, left + new_w, h))
        else:                                     # too tall -> trim top and bottom
            new_h = round(w / ratio)
            top = (h - new_h) // 2
            cropped = im.crop((0, top, w, top + new_h))

        if also_webp is not None:
            cropped.save(also_webp, format="WEBP", quality=92, method=6)

        buf = io.BytesIO()
        save_fmt = {"png": "PNG", "jpeg": "JPEG", "webp": "WEBP"}[fmt]
        kwargs = {"quality": 92, "method": 6} if save_fmt == "WEBP" else {}
        if save_fmt == "JPEG":
            kwargs = {"quality": 92, "subsampling": 0}
        cropped.save(buf, format=save_fmt, **kwargs)
        return buf.getvalue()


def generate(client, job: Job, args, attempt_log: list[str]) -> Outcome:
    import openai

    params = {
        "model": args.model,
        "prompt": job.prompt,
        "size": args.size,
        "quality": args.quality,
        "background": args.background,
        "output_format": args.format,
        "n": 1,                       # variants are separate calls: one failure is one image
    }
    if args.moderation:
        params["moderation"] = args.moderation
    if args.compression is not None and args.format in {"webp", "jpeg"}:
        params["output_compression"] = args.compression

    started = time.monotonic()
    tokens = 0
    for variant in range(1, args.variants + 1):
        suffix = "" if variant == 1 else f"-{variant}"
        target = job.out.with_name(f"{job.slug}{suffix}.{args.format}")
        if target.exists() and not args.force:
            attempt_log.append(f"{target.name} exists")
            continue

        last_error: Exception | None = None
        for attempt in range(1, args.retries + 1):
            try:
                result = client.images.generate(**params)
                break
            except (openai.RateLimitError, openai.APIConnectionError, openai.InternalServerError) as exc:
                last_error = exc
                delay = min(60.0, 2.0 ** attempt) + random.uniform(0, 1.5)
                attempt_log.append(f"{type(exc).__name__}, retry in {delay:.1f}s")
                time.sleep(delay)
            except openai.BadRequestError as exc:          # policy refusal, bad params
                return Outcome(job.slug, "failed", f"rejected: {exc}", tokens,
                               time.monotonic() - started)
        else:
            return Outcome(job.slug, "failed", f"gave up after {args.retries}: {last_error}",
                           tokens, time.monotonic() - started)

        payload = base64.b64decode(result.data[0].b64_json)
        webp_copy = target.with_suffix(".webp") if args.also_webp and args.format != "webp" else None
        if not args.no_crop:
            payload = center_crop(payload, args.ratio, args.format, webp_copy)
        target.write_bytes(payload)

        usage = getattr(result, "usage", None)
        if usage is not None:
            tokens += getattr(usage, "total_tokens", 0) or 0

        target.with_suffix(".json").write_text(
            json.dumps(
                {
                    "slug": job.slug,
                    "title": job.title,
                    "generated_at": datetime.now(UTC).isoformat(),
                    "request": {k: v for k, v in params.items() if k != "prompt"},
                    "cropped_to": None if args.no_crop else round(args.ratio, 4),
                    "usage": None if usage is None else usage.model_dump(),
                    "revised_prompt": getattr(result.data[0], "revised_prompt", None),
                    "prompt": job.prompt,
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        attempt_log.append(f"wrote {target.name}")

    if not any(line.startswith("wrote") for line in attempt_log):
        return Outcome(job.slug, "skipped", "already generated (use --force)", 0,
                       time.monotonic() - started)
    return Outcome(job.slug, "ok", "; ".join(attempt_log), tokens, time.monotonic() - started)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Render the blog article illustrations with the OpenAI images API.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--prompts", type=Path, default=HERE, help="directory holding the prompt .md files")
    p.add_argument("--out", type=Path, default=HERE / "images", help="where to write the images")
    p.add_argument("--only", action="append", default=[], metavar="SLUG|GLOB",
                   help="generate just these (repeatable, fnmatch patterns allowed)")
    p.add_argument("--base-url", default=None, metavar="URL",
                   help="an OpenAI-compatible endpoint to use instead of api.openai.com; "
                        "authenticates with $OPENAI_API_KEY as a bearer token")
    p.add_argument("--model", default="gpt-image-1")
    p.add_argument("--size", default="1536x1024",
                   choices=["1536x1024", "1024x1024", "1024x1536", "auto"],
                   help="API canvas; 1536x1024 is the landscape one, cropped to 16:10 after")
    p.add_argument("--quality", default="high", choices=["low", "medium", "high", "auto"])
    p.add_argument("--background", default="opaque", choices=["opaque", "transparent", "auto"],
                   help="the cards need an opaque tile: it sits on cream and on near-black")
    p.add_argument("--format", default="png", choices=["png", "webp", "jpeg"], dest="format")
    p.add_argument("--compression", type=int, default=None, metavar="0-100",
                   help="webp/jpeg compression level")
    p.add_argument("--moderation", default=None, choices=["auto", "low"])
    p.add_argument("--variants", type=int, default=1, help="images per post, as separate calls")
    p.add_argument("--ratio", type=float, default=CARD_RATIO, help="crop ratio (16/10 = 1.6)")
    p.add_argument("--no-crop", action="store_true", help="keep the API's own aspect ratio")
    p.add_argument("--also-webp", action="store_true", help="write a .webp copy beside the image")
    p.add_argument("--workers", type=int, default=3, help="parallel requests")
    p.add_argument("--retries", type=int, default=5)
    p.add_argument("--force", action="store_true", help="overwrite images that already exist")
    p.add_argument("--limit", type=int, default=None, help="stop after N posts (a cheap trial run)")
    p.add_argument("--dry-run", action="store_true", help="print what would be sent, call nothing")
    p.add_argument("--append", default=None, metavar="TEXT",
                   help="extra clause appended to every prompt in this run, for corrective re-renders")
    args = p.parse_args()

    prompts = read_prompts(args.prompts, args.only)
    if args.limit:
        prompts = prompts[: args.limit]
    if not prompts:
        print("no prompt files matched", file=sys.stderr)
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    jobs = [Job(slug, prompt, title, args.out / slug) for slug, title, prompt in prompts]
    if args.append:
        jobs = [dataclasses.replace(job, prompt=f"{job.prompt}\n\n{args.append}") for job in jobs]
        print(f"appended to every prompt: {args.append}")

    where = args.base_url or "api.openai.com"
    print(f"{len(jobs)} post(s) -> {args.out}   via {where}")
    print(f"model={args.model} size={args.size} quality={args.quality} "
          f"background={args.background} format={args.format} variants={args.variants} "
          f"crop={'off' if args.no_crop else f'{args.ratio:.3f}'}")

    if args.dry_run:
        for job in jobs:
            first = job.prompt.split("\n", 1)[0]
            print(f"\n--- {job.slug}  ({len(job.prompt)} chars)\n    {first[:110]}...")
        print(f"\ndry run: {len(jobs)} request(s) would be sent, nothing written")
        return 0

    import openai

    client_kwargs = {"base_url": args.base_url} if args.base_url else {}

    try:
        client = openai.OpenAI(**client_kwargs)
    except openai.OpenAIError as exc:
        print(f"cannot build a client: {exc}", file=sys.stderr)
        return 1

    outcomes: list[Outcome] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(generate, client, job, args, []): job for job in jobs}
        for done in concurrent.futures.as_completed(futures):
            job = futures[done]
            try:
                outcome = done.result()
            except Exception as exc:                        # noqa: BLE001 - one bad job, keep going
                outcome = Outcome(job.slug, "failed", repr(exc))
            outcomes.append(outcome)
            mark = {"ok": "+", "skipped": ".", "failed": "!"}[outcome.status]
            print(f" {mark} {outcome.slug:58} {outcome.detail[:70]}")

    ok = [o for o in outcomes if o.status == "ok"]
    failed = [o for o in outcomes if o.status == "failed"]
    skipped = [o for o in outcomes if o.status == "skipped"]
    total_tokens = sum(o.tokens for o in outcomes)
    print(f"\n{len(ok)} generated, {len(skipped)} already there, {len(failed)} failed")
    if total_tokens:
        print(f"{total_tokens} image tokens billed (multiply by your gpt-image output rate)")
    for o in failed:
        print(f"  ! {o.slug}: {o.detail}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
