# The Unit of Work pattern in SQLAlchemy 2

- **Post:** `docs/blog/posts/2026-09-07-unit-of-work-in-sqlalchemy-2.md`
- **Category:** Tutorials
- **Idea:** One transaction boundary owned by the use case, one commit at its edge.

## Prompt

```text
Flat vector editorial illustration in the Bedrock Python house style. Isometric geometry built from clean straight-edged polygons and simple extruded blocks, drawn as if from the same construction as the brand mark: an isometric cube cut into flat facets separated by thin white negative-space gaps. Solid flat fills only -- no gradients, no glow, no drop shadows, no texture, no photorealistic 3D rendering. Every facet is one uniform colour: no shading, blending or vignette inside a face, tone changes only at an edge. Palette: warm off-white background #F8F6F1; forms in graphite and slate blue #1F2933, #263642, #405463, #667989, #9AAABA; exactly one accent colour, terracotta #C9572C, used sparingly and only on the single element the picture is about -- #C9572C exactly on its lit face and a darker shade of the same terracotta on its shaded faces, never a lighter orange. Small forms take their fills from the slate list and are never white or near-white: nothing in the picture may match the background. Generous negative space, calm and precise, the restraint of an engineering diagram rather than decoration. Centred composition with wide margins, 16:10 landscape.

Objects from this series' shared vocabulary appear here and must be drawn exactly as described:
- a transaction: one flat slab that visibly carries everything resting on it as a single piece
- a table slab: a flat rectangular plate whose top face is ruled into even rows by thin white lines

Subject: One transaction slab raised as a low walled tray with four table slabs resting inside it, none touching the wall. Seated in a socket on the outer edge of the wall, at one corner, is a single solid plug: a plain cylindrical stopper with no marking of any kind on it, terracotta. Discarded on the base plane beside the tray lie four identical slate plugs, the ones the table slabs used to carry.

No text, no letters, no numbers, no labels, no captions, no code, no UI screenshots, no logos, no brand names, no arrows with words. No people, no faces, no hands. No robots, gears, circuit boards, server racks with blinking lights, cloud shapes or other stock technology cliches. No neon, no dark background, no glossy spheres, no light orbs, no bokeh, no lens flare, no sparkles. No soft shading or gradient across a single face, and no white or near-white fill on any object.
```
