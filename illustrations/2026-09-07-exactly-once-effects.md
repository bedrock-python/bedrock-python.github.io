# Exactly-once is a lie; exactly-once effects are not

- **Post:** `docs/blog/posts/2026-09-07-exactly-once-effects.md`
- **Category:** Design
- **Idea:** Two systems, two commits, no shared transaction: close each window one at a time.

## Prompt

```text
Flat vector editorial illustration in the Bedrock Python house style. Isometric geometry built from clean straight-edged polygons and simple extruded blocks, drawn as if from the same construction as the brand mark: an isometric cube cut into flat facets separated by thin white negative-space gaps. Solid flat fills only -- no gradients, no glow, no drop shadows, no texture, no photorealistic 3D rendering. Every facet is one uniform colour: no shading, blending or vignette inside a face, tone changes only at an edge. Palette: warm off-white background #F8F6F1; forms in graphite and slate blue #1F2933, #263642, #405463, #667989, #9AAABA; exactly one accent colour, terracotta #C9572C, used sparingly and only on the single element the picture is about -- #C9572C exactly on its lit face and a darker shade of the same terracotta on its shaded faces, never a lighter orange. Small forms take their fills from the slate list and are never white or near-white: nothing in the picture may match the background. Generous negative space, calm and precise, the restraint of an engineering diagram rather than decoration. Centred composition with wide margins, 16:10 landscape.

Objects from this series' shared vocabulary appear here and must be drawn exactly as described:
- a database drum: a squat cylinder with two thin bands near its top
- an append-only log: a long straight trough divided into equal cells, filled solid from the left and empty to the right, with one upright pointer standing at the boundary
- an effect: a solid disc stamped into the base plane, with empty depressions of the same size for effects that did not happen

Subject: A database drum and an append-only log trough standing apart on a base plane with a visible gap of empty background between them. Spanning the gap, four small upright guard plates: three seated and closing their section, the fourth mid-descent into its slot. Beyond the log, exactly one effect disc is stamped into the plane. The descending guard plate is terracotta.

No text, no letters, no numbers, no labels, no captions, no code, no UI screenshots, no logos, no brand names, no arrows with words. No people, no faces, no hands. No robots, gears, circuit boards, server racks with blinking lights, cloud shapes or other stock technology cliches. No neon, no dark background, no glossy spheres, no light orbs, no bokeh, no lens flare, no sparkles. No soft shading or gradient across a single face, and no white or near-white fill on any object.
```
