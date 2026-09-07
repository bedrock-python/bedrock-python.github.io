# Why gRPC interceptors break on streaming RPCs

- **Post:** `docs/blog/posts/2026-09-07-why-grpc-interceptors-break-on-streaming-rpcs.md`
- **Category:** Design
- **Idea:** The wrapper closes before the stream has produced anything.

## Prompt

```text
Flat vector editorial illustration in the Bedrock Python house style. Isometric geometry built from clean straight-edged polygons and simple extruded blocks, drawn as if from the same construction as the brand mark: an isometric cube cut into flat facets separated by thin white negative-space gaps. Solid flat fills only -- no gradients, no glow, no drop shadows, no texture, no photorealistic 3D rendering. Every facet is one uniform colour: no shading, blending or vignette inside a face, tone changes only at an edge. Palette: warm off-white background #F8F6F1; forms in graphite and slate blue #1F2933, #263642, #405463, #667989, #9AAABA; exactly one accent colour, terracotta #C9572C, used sparingly and only on the single element the picture is about -- #C9572C exactly on its lit face and a darker shade of the same terracotta on its shaded faces, never a lighter orange. Small forms take their fills from the slate list and are never white or near-white: nothing in the picture may match the background. Generous negative space, calm and precise, the restraint of an engineering diagram rather than decoration. Centred composition with wide margins, 16:10 landscape.

Objects from this series' shared vocabulary appear here and must be drawn exactly as described:
- a channel: two round tubes running side by side between two housings, carrying small frames
- a stream: a long ribbon of small equal frames leaving a tube end in single file

Subject: A pair of channel tubes with a long stream ribbon of frames leaving one end in single file. Near the very start of the ribbon sits a narrow measuring ring that has already snapped shut around empty space, drawn in terracotta, while every frame is further along the ribbon, outside it. Beside the ring, a small gauge panel shows a trace pinned flat at zero while the ribbon beyond is plainly busy.

No text, no letters, no numbers, no labels, no captions, no code, no UI screenshots, no logos, no brand names, no arrows with words. No people, no faces, no hands. No robots, gears, circuit boards, server racks with blinking lights, cloud shapes or other stock technology cliches. No neon, no dark background, no glossy spheres, no light orbs, no bokeh, no lens flare, no sparkles. No soft shading or gradient across a single face, and no white or near-white fill on any object.
```
