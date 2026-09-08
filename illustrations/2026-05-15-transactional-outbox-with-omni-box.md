# The Transactional Outbox pattern in Python: omni-box

- **Post:** `docs/blog/posts/2026-05-15-transactional-outbox-with-omni-box.md`
- **Category:** Libraries
- **Idea:** One transaction holds both the row and the event; a separate relay carries the event onward.

## Prompt

```text
Flat vector editorial illustration in the Bedrock Python house style. Isometric geometry built from clean straight-edged polygons and simple extruded blocks, drawn as if from the same construction as the brand mark: an isometric cube cut into flat facets separated by thin white negative-space gaps. Solid flat fills only -- no gradients, no glow, no drop shadows, no texture, no photorealistic 3D rendering. Every facet is one uniform colour: no shading, blending or vignette inside a face, tone changes only at an edge. Palette: warm off-white background #F8F6F1; forms in graphite and slate blue #1F2933, #263642, #405463, #667989, #9AAABA; exactly one accent colour, terracotta #C9572C, used sparingly and only on the single element the picture is about -- #C9572C exactly on its lit face and a darker shade of the same terracotta on its shaded faces, never a lighter orange. Small forms take their fills from the slate list and are never white or near-white: nothing in the picture may match the background. Generous negative space, calm and precise, the restraint of an engineering diagram rather than decoration. Centred composition with wide margins, 16:10 landscape.

Objects from this series' shared vocabulary appear here and must be drawn exactly as described:
- a transaction: one flat slab that visibly carries everything resting on it as a single piece
- a table slab: a flat rectangular plate whose top face is ruled into even rows by thin white lines
- an append-only log: a long straight trough divided into equal cells, filled solid from the left and empty to the right, with one upright pointer standing at the boundary

Subject: One transaction slab carrying two things at once: a table slab with a single row filled solid, and beside it a small upright envelope wedge, both resting on the slab as one piece. To the right, across a clear gap of empty background, an append-only log trough. A single relay arm lifts a copy of the wedge across the gap into the log's first empty cell. The wedge is the terracotta object, and nothing else crosses the gap.

No text, no letters, no numbers, no labels, no captions, no code, no UI screenshots, no logos, no brand names, no arrows with words. No people, no faces, no hands. No robots, gears, circuit boards, server racks with blinking lights, cloud shapes or other stock technology cliches. No neon, no dark background, no glossy spheres, no light orbs, no bokeh, no lens flare, no sparkles. No soft shading or gradient across a single face, and no white or near-white fill on any object.
```
