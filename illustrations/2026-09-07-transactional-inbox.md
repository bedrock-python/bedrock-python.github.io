# Transactional inbox: the other half of the outbox pattern

- **Post:** `docs/blog/posts/2026-09-07-transactional-inbox.md`
- **Category:** Design
- **Idea:** The arriving message becomes a row in the same transaction as the effect.

## Prompt

```text
Flat vector editorial illustration in the Bedrock Python house style. Isometric geometry built from clean straight-edged polygons and simple extruded blocks, drawn as if from the same construction as the brand mark: an isometric cube cut into flat facets separated by thin white negative-space gaps. Solid flat fills only -- no gradients, no glow, no drop shadows, no texture, no photorealistic 3D rendering. Every facet is one uniform colour: no shading, blending or vignette inside a face, tone changes only at an edge. Palette: warm off-white background #F8F6F1; forms in graphite and slate blue #1F2933, #263642, #405463, #667989, #9AAABA; exactly one accent colour, terracotta #C9572C, used sparingly and only on the single element the picture is about -- #C9572C exactly on its lit face and a darker shade of the same terracotta on its shaded faces, never a lighter orange. Small forms take their fills from the slate list and are never white or near-white: nothing in the picture may match the background. Generous negative space, calm and precise, the restraint of an engineering diagram rather than decoration. Centred composition with wide margins, 16:10 landscape.

Objects from this series' shared vocabulary appear here and must be drawn exactly as described:
- an append-only log: a long straight trough divided into equal cells, filled solid from the left and empty to the right, with one upright pointer standing at the boundary
- a transaction: one flat slab that visibly carries everything resting on it as a single piece
- a table slab: a flat rectangular plate whose top face is ruled into even rows by thin white lines
- an effect: a solid disc stamped into the base plane, with empty depressions of the same size for effects that did not happen

Subject: An append-only log trough on the left delivering one frame to a transaction slab on the right. The slab carries two things as a single piece: a table slab with one row filled, and an effect disc stamped beside it. A second identical frame arrives, meets the slab's raised edge and is deflected away -- that deflected frame is terracotta. Nothing inside the slab is duplicated.

No text, no letters, no numbers, no labels, no captions, no code, no UI screenshots, no logos, no brand names, no arrows with words. No people, no faces, no hands. No robots, gears, circuit boards, server racks with blinking lights, cloud shapes or other stock technology cliches. No neon, no dark background, no glossy spheres, no light orbs, no bokeh, no lens flare, no sparkles. No soft shading or gradient across a single face, and no white or near-white fill on any object.
```
