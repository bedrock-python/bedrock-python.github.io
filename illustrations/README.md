# Article image prompts

One prompt per blog post, named after the post file:
`2026-09-07-zero-dependency-cores.md` -> `docs/blog/posts/2026-09-07-zero-dependency-cores.md`.

Each file holds the post title, its category, the one-line idea the picture has to carry, and a
single self-contained prompt block to paste into an image model. The style paragraph is repeated
verbatim in every file on purpose, so no file needs any other file to work.

## Where the style comes from

**The mark.** `docs/assets/logo.svg` is an isometric cube cut into five flat polygons —
`#1F2933`, `#263642`, `#405463`, `#667989`, `#9AAABA` — separated by thin white gaps that read as a
chevron in the negative space. Flat fills, straight edges, no gradient, no shading, no outline.

**The site.** `docs/stylesheets/bedrock.css`: warm off-white page (`#F8F6F1`), near-black ink
(`#1A1815`), one accent — terracotta `#C9572C`. Inter and JetBrains Mono. Magazine restraint,
hairline borders, a lot of empty space.

So the illustrations are: **flat isometric geometry in the logo's slate-blue family, on the site's
warm off-white, with exactly one terracotta element per image** — and that element is always the
thing the post is about (the bug, the leak, the multiplier, the lever that was pushed). Read the
grid of cards top to bottom and the terracotta is the only colour that moves.

## Rules the prompts already encode

- **No text of any kind.** Every prompt says so four ways; image models still try. If a render
  comes back with glyphs, re-run adding: `absolutely no glyphs, no writing, no symbols resembling
  letters or digits anywhere in the image`.
- **No orbs.** The current card visuals are CSS radial gradients — the light blobs these replace.
  Nothing round, glowing, glossy or blurred.
- **One accent.** If the model spreads terracotta over several forms, re-run adding: `exactly one
  terracotta element in the entire image, everything else in slate blue and graphite`.
- **Objects, not diagrams of objects.** The subjects are physical: slabs, rails, gates, plates,
  clamps, sockets. That is what keeps 49 images from turning into 49 flowcharts.

## Output

- **Aspect ratio 16:10** — `.bdr-card__visual` and `.bdr-featured__visual` are both `16 / 10`.
  If the model only offers 3:2 or 1:1, generate wide and crop to 16:10 from the centre.
- **Size:** 1536x1024 or larger, then downscale. Cards render at roughly 400x250 on a 2x display.
- **Background must be the flat `#F8F6F1`**, edge to edge — the image is a light tile in both the
  light and the dark theme, so it must not rely on the page colour behind it.
- Save as `docs/assets/blog/<post-slug>.webp` (or `.png`) to keep the post-to-image mapping obvious.

## Wiring an image into the site

The card visual is currently a category gradient:

```html
<div class="bdr-card__visual bdr-card__visual--design"></div>
```

Once an image exists, the same div takes it as a background — one extra inline style per card, or a
small CSS rule per slug. The five listings that carry a card are the ones in
`EDITORIAL-BACKLOG.md`: `docs/blog/index.md`, `docs/index.md`, the category page, and the
category-count and archive lines (those last two carry no visual).

## Generating them

`generate_images.py` renders every prompt in this directory through the OpenAI images API. It is a
PEP 723 script, so it carries its own dependencies and needs no virtualenv:

```bash
export OPENAI_API_KEY=...
uv run generate_images.py --dry-run                  # what would be sent, no API calls
uv run generate_images.py --only 2026-05-30-welcome  # one post
uv run generate_images.py --only '*kafka*' --variants 3
uv run generate_images.py                            # all 49
```

Output lands in `images/` as `<post-slug>.png`, beside a `<post-slug>.json` sidecar holding the
prompt, every request parameter and the token usage — enough to reproduce or diff a render later.

**Defaults and why.** `--size 1536x1024` is the API's landscape canvas (3:2); the script
centre-crops it to **16:10** because that is what `.bdr-card__visual` is. `--quality high` for flat
vector geometry, where banding and soft edges show. `--background opaque` because the tile has to
carry its own `#F8F6F1` on both the cream and the near-black theme. `--format png` keeps the crop
lossless; `--also-webp` writes a compressed copy beside it for the site.

Everything is overridable: `--model`, `--quality`, `--background`, `--format`, `--compression`,
`--moderation`, `--ratio`, `--no-crop`, `--workers`, `--retries`, `--limit`.

Existing files are never overwritten, so an interrupted run resumes by re-running it; pass
`--force` to redo a post. Variants are separate API calls rather than `n>1`, so one failure costs
one image instead of the batch. Rate limits and 5xx are retried with backoff; a content-policy
refusal is reported and skipped rather than retried.

## The shared vocabulary

The first full set was legible as *style* and illegible as *subject*: 49 arrangements of the same
anonymous cubes, where nothing told a post about partitions from a post about Kafka. The fix was a
vocabulary of domain objects, listed inside each prompt that uses one, drawn the same way in every
image of the series:

| object | drawn as |
|---|---|
| database | a squat drum with two bands near its top |
| table | a flat slab whose top face is ruled into rows |
| partitions | narrow ruled slabs of equal width under one long parent bar |
| append-only log | a trough of equal cells, filled from the left, a pointer at the boundary |
| topic | three log troughs running parallel |
| key-value store | a rack of paired units: a thin tag beside a small cube |
| channel | two round tubes between two housings, carrying frames |
| stream | a ribbon of equal frames leaving a tube in single file |
| migration history | offset thin plates joined by a ladder up one side |
| connection pool | a rack of round rods in sockets, some withdrawn |
| status codes | a flat strip of sixteen equal cells |
| transaction | one slab that carries everything on it as a single piece |
| effect | a disc stamped into the base plane; empty depressions for effects that did not happen |
| package, service, queue, code, container, HTTP port, schedule | see `MOTIFS` in the generator |

Two rules were added to the style block at the same time, both from defects seen in the renders:
**one connected arrangement**, never several props scattered across the frame, and **exactly one
terracotta object** in the whole image.

What the model still gets wrong, so check for it: it reads role words as people (`worker` became a
human figure twice), abstractions as interface icons (`marker pin` became a map pin, `echo` became
a speech bubble, a seal became a checkmark), and `arrow` as a flat 2D arrow laid over the scene.
Name a physical object instead and it complies. It also cannot reliably count: "the second and
third are blocked" produced one blocked rack in three separate attempts.

## Layout

- `images/` — the first set, house style without the vocabulary.
- `images/v2/` — the current set, with the vocabulary.
- `images/<set>/normalized/` — the same images with the background balanced onto `#F8F6F1`.
  This is the one to publish; see `normalize.py`.

## Dark theme

The tiles are opaque, so they do not inherit the page colour: a cream tile glares on the near-black
card. The brand already answers this for the mark -- `logo.svg` and `logo-dark.svg` are the same
five polygons with the lightness ramp turned over -- so the dark variant is that operation applied
to the render, not a second generation. Same composition, same accent object, no API call:

```bash
uv run dark_variant.py        # images/v2/normalized -> images/v2/dark
```

Hue is preserved, lightness inverted and anchored so the ground lands on the card colour, and the
terracotta object keeps its hue and takes `#E8825A` -- the accent the stylesheet already switches to
under `[data-md-color-scheme="slate"]`. Chroma, not HSL saturation, decides what counts as neutral:
near-white scores a high saturation because its denominator collapses, and inverting that paints
the whole page brown.

Wiring both into a card:

```css
.bdr-card__visual { background-image: url("../assets/blog/<slug>.webp"); background-size: cover; }
[data-md-color-scheme="slate"] .bdr-card__visual {
  background-image: url("../assets/blog/<slug>-dark.webp");
}
```
