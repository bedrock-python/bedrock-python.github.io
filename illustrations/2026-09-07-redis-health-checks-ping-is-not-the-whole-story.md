# Redis health checks: PING is not the whole story

- **Post:** `docs/blog/posts/2026-09-07-redis-health-checks-ping-is-not-the-whole-story.md`
- **Category:** Design
- **Idea:** Three servers answer the same, two of them cannot take a write.

## Prompt

```text
Flat vector editorial illustration in the Bedrock Python house style. Isometric geometry built from clean straight-edged polygons and simple extruded blocks, drawn as if from the same construction as the brand mark: an isometric cube cut into flat facets separated by thin white negative-space gaps. Solid flat fills only -- no gradients, no glow, no drop shadows, no texture, no photorealistic 3D rendering. Every facet is one uniform colour: no shading, blending or vignette inside a face, tone changes only at an edge. Palette: warm off-white background #F8F6F1; forms in graphite and slate blue #1F2933, #263642, #405463, #667989, #9AAABA; exactly one accent colour, terracotta #C9572C, used sparingly and only on the single element the picture is about -- #C9572C exactly on its lit face and a darker shade of the same terracotta on its shaded faces, never a lighter orange. Small forms take their fills from the slate list and are never white or near-white: nothing in the picture may match the background. Generous negative space, calm and precise, the restraint of an engineering diagram rather than decoration. Centred composition with wide margins, 16:10 landscape.

Objects from this series' shared vocabulary appear here and must be drawn exactly as described:
- a key-value store: a rack of paired units, each a thin upright tag beside a small cube

Subject: Three identical key-value racks standing side by side on one shared base, each built of the same paired units: a thin upright tag beside a small cube. One manifold pipe runs above all three and drops an identical write arm into each rack, and each rack returns one identical plain flat disc on its front face. All three racks are shown in cutaway, and the count is the point of the picture: the LEFT rack is the only open one, its write arm reaching all the way to the bottom. The MIDDLE rack and the RIGHT rack are BOTH blocked -- each has a solid terracotta wall across its interior that stops its arm partway down. Two blocked, one open. Those two internal walls are the only terracotta in the image.

No text, no letters, no numbers, no labels, no captions, no code, no UI screenshots, no logos, no brand names, no arrows with words. No people, no faces, no hands. No robots, gears, circuit boards, server racks with blinking lights, cloud shapes or other stock technology cliches. No neon, no dark background, no glossy spheres, no light orbs, no bokeh, no lens flare, no sparkles. No soft shading or gradient across a single face, and no white or near-white fill on any object.
```
