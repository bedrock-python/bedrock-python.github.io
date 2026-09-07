# PgBouncer transaction mode and async SQLAlchemy: the production setup nobody documents enough

- **Post:** `docs/blog/posts/2026-09-07-pgbouncer-transaction-mode-async-sqlalchemy.md`
- **Category:** Tutorials
- **Idea:** Transaction pooling reassigns the lane on every transaction, and session state does not survive it.

## Prompt

```text
Flat vector editorial illustration in the Bedrock Python house style. Isometric geometry built from clean straight-edged polygons and simple extruded blocks, drawn as if from the same construction as the brand mark: an isometric cube cut into flat facets separated by thin white negative-space gaps. Solid flat fills only -- no gradients, no glow, no drop shadows, no texture, no photorealistic 3D rendering. Every facet is one uniform colour: no shading, blending or vignette inside a face, tone changes only at an edge. Palette: warm off-white background #F8F6F1; forms in graphite and slate blue #1F2933, #263642, #405463, #667989, #9AAABA; exactly one accent colour, terracotta #C9572C, used sparingly and only on the single element the picture is about -- #C9572C exactly on its lit face and a darker shade of the same terracotta on its shaded faces, never a lighter orange. Small forms take their fills from the slate list and are never white or near-white: nothing in the picture may match the background. Generous negative space, calm and precise, the restraint of an engineering diagram rather than decoration. Centred composition with wide margins, 16:10 landscape.

Objects from this series' shared vocabulary appear here and must be drawn exactly as described:
- a connection pool: a rack of round rods in sockets, some withdrawn and in use
- a database drum: a squat cylinder with two thin bands near its top

Subject: Application housings on the left, a narrow pooler plate across the middle with only a few lanes cut through it, and a database drum on the right. Lanes entering the plate leave it on different lanes, visibly re-routed rather than passing straight through. At the plate's surface several small state chips have fallen off the lanes and lie loose on the base plane; one is terracotta.

No text, no letters, no numbers, no labels, no captions, no code, no UI screenshots, no logos, no brand names, no arrows with words. No people, no faces, no hands. No robots, gears, circuit boards, server racks with blinking lights, cloud shapes or other stock technology cliches. No neon, no dark background, no glossy spheres, no light orbs, no bokeh, no lens flare, no sparkles. No soft shading or gradient across a single face, and no white or near-white fill on any object.
```
