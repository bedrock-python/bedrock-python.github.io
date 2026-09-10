"""Optional Playwright check against a running bilingual preview."""

import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = {
    "2026-05-15-transactional-outbox-with-omni-box",
    "2026-09-07-circuit-breakers-should-be-per-origin",
    "2026-09-07-unit-of-work-in-sqlalchemy-2",
    "2026-09-07-when-should-redis-fail-open",
    "2026-09-07-the-anatomy-of-a-production-grpc-server",
    "2026-09-07-warmup-readiness-and-liveness-are-three-different-things",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--browser", choices=["chromium", "webkit"], default="chromium")
    parser.add_argument("--channel", help="Optional installed Chromium channel, e.g. chrome")
    parser.add_argument("--sample", action="store_true", help="Check six representative articles")
    args = parser.parse_args()
    output = ROOT / "build/diagrams/browser"
    output.mkdir(parents=True, exist_ok=True)
    posts = sorted((ROOT / "docs/blog/posts").glob("*.md"))
    if args.sample:
        posts = [post for post in posts if post.stem in SAMPLES]
    checks = []
    errors = []
    with sync_playwright() as p:
        options = {"channel": args.channel} if args.channel else {}
        browser = getattr(p, args.browser).launch(headless=True, **options)
        context = browser.new_context(viewport={"width": 1440, "height": 1100})
        # Inspect native closed roots without changing their mode or behavior.
        context.add_init_script('''
            window.__diagramRoots = new WeakMap();
            const attach = Element.prototype.attachShadow;
            Element.prototype.attachShadow = function(options) {
                const root = attach.call(this, options);
                window.__diagramRoots.set(this, root);
                return root;
            };
        ''')
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        for lang, prefix in [("en", ""), ("ru", "/ru")]:
            for post in posts:
                url = args.base_url.rstrip("/") + prefix + "/blog/posts/" + post.stem + "/"
                page.goto(url)
                figure = page.locator("figure.bdr-diagram").first
                button = figure.locator(".bdr-diagram__expand")
                expect(button).to_be_visible(timeout=60000)
                viewport = figure.locator(".bdr-diagram__viewport")
                host = viewport.locator("div.mermaid")
                info = host.evaluate('''host => {
                    const svg = window.__diagramRoots.get(host).querySelector('svg');
                    return {width: svg.getBoundingClientRect().width,
                            title: svg.querySelector('title')?.textContent,
                            description: svg.querySelector('desc')?.textContent,
                            labelled: svg.getAttribute('aria-labelledby'),
                            described: svg.getAttribute('aria-describedby')};
                }''')
                assert all(info.values()), (url, info)
                widths = [320, 390, 768, 1440] if post.stem in SAMPLES else [390, 1440]
                for width in widths:
                    page.set_viewport_size({"width": width, "height": 1100 if width > 600 else 844})
                    for theme in ("default", "slate"):
                        page.evaluate("theme => document.body.setAttribute('data-md-color-scheme', theme)", theme)
                        page.wait_for_function("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1", timeout=5000)
                        figure.scroll_into_view_if_needed()
                        overflowing = viewport.evaluate("e => e.scrollWidth > e.clientWidth + 1")
                        expect(figure.locator(".bdr-diagram__hint")).to_be_visible() if overflowing else expect(figure.locator(".bdr-diagram__hint")).to_be_hidden()
                        if overflowing:
                            viewport.focus()
                            page.keyboard.press("ArrowRight")
                            page.wait_for_function("document.querySelector('.bdr-diagram__viewport').scrollLeft > 0")
                            viewport.evaluate("e => e.scrollLeft = 0")
                        button.click()
                        dialog = page.locator(".bdr-diagram-dialog")
                        expect(dialog).to_be_visible()
                        expect(dialog.locator("div.mermaid")).to_be_attached()
                        page.keyboard.press("Escape")
                        expect(dialog).not_to_be_visible()
                        expect(host).to_be_attached()
                        expect(button).to_be_focused()
                        checks.append({"language": lang, "post": post.stem, "width": width, "theme": theme})
                    if post.stem in SAMPLES and width in (390, 1440):
                        # Let responsive drawer transitions settle before taking a screenshot.
                        page.wait_for_timeout(250)
                        figure.screenshot(path=str(output / f"{args.browser}-{lang}-{post.stem}-{width}.png"))
                print(f"{args.browser}: {lang}/{post.stem}", flush=True)

        # Same-edition links should retain the document and reinitialize controls.
        page.goto(args.base_url.rstrip("/") + "/ru/blog/posts/2026-09-07-safe-grpc-retries/")
        expect(page.locator(".bdr-diagram__expand")).to_be_visible(timeout=60000)
        original_url = page.url
        original_path = urlsplit(original_url).path
        target = page.evaluate('''() => [...document.querySelectorAll('.md-content a[href]')]
            .find(a => a.origin === location.origin && a.pathname.includes('/blog/posts/') && a.pathname !== location.pathname)
            ?.getAttribute('href')''')
        assert target, "The navigation fixture needs an internal article link"
        page.evaluate("window.__diagramNavigationSentinel = true")
        page.locator(f'.md-content a[href="{target}"]').first.click()
        page.wait_for_url(lambda url: urlsplit(str(url)).path != original_path)
        expect(page.locator(".bdr-diagram__expand")).to_be_visible(timeout=60000)
        assert page.evaluate("window.__diagramNavigationSentinel === true")
        page.locator(".bdr-diagram__expand").click()
        page.locator(".bdr-diagram-dialog__header button").click()
        expect(page.locator(".bdr-diagram__expand")).to_be_focused()
        page.locator(".bdr-diagram__expand").click()
        page.evaluate("history.back()")
        page.wait_for_url(lambda url: urlsplit(str(url)).path == original_path)
        expect(page.locator(".bdr-diagram-dialog")).not_to_be_visible()
        expect(page.locator(".bdr-diagram__expand")).to_be_visible(timeout=60000)
        expect(page.locator(".bdr-diagram-dialog__body")).to_be_empty()
        assert not errors, errors

        # If the CDN is unavailable, the article and visible explanation survive.
        fallback = browser.new_context()
        fallback.route("**/*mermaid*.js*", lambda route: route.abort())
        offline = fallback.new_page()
        offline.goto(args.base_url.rstrip("/") + "/blog/posts/2026-05-15-transactional-outbox-with-omni-box/")
        expect(offline.locator(".bdr-diagram__caption")).to_be_visible()
        expect(offline.locator(".bdr-diagram__expand")).to_be_hidden()
        fallback.close()
        browser.close()
    (output / f"{args.browser}-checks.json").write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {len(checks)} layout/theme/dialog checks, instant navigation and CDN fallback", flush=True)


if __name__ == "__main__":
    main()
