# water_v1: painted light on STILL water (2026-10-30)

The sea never moves: no displacement, ripple or coastline warp. Only light changes, and only inside the water matte (plus the painted flame pixels on fire shots). It uses the torch_v1c lesson: static spatial maps, each driven by one scalar per frame, read as light, while light that travels reads as warping.

## Layers (water_v1.py)
- **glints**: FIXED sites, the painted highlight peaks inside the eroded water matte, weighted by a sun or moon path. Each site brightens and dims in place on its own slow twinkle clock (two sines, 0.35–2.2 Hz, thresholded, so energy above 5 Hz stays low). Nothing travels. `clock: "fire"` makes the sites follow the mean torch_v1c flick.
- **breathe**: a static path × luminance map multiplied by one slow scalar (0.12 + 0.27 Hz). This is the moon or sun column slowly breathing.
- **fire_reflection**: a static warm-reflection map (R−B × luminance × water), split into per-fire x-columns. Each column is driven by that fire's own `fx_v1c.flick()` value, the same per-frame curve as the source glow (torch_v1c, LOCKED). The reflection therefore pulses with the fire.
- **fire**: the source fire gets the LOCKED torch_v1c via `fx_v1c.PlateFX`, imported by path and not edited. It uses flames_v4 disabling (no warp, smoke, layers, motes or embers). `fire.zone_from_masks` limits the allowed fire zone to the painted flame pixels (fx source masks, dilated 3 px), so roofs and walls stay at 0.
- **Mattes**: `out = P + (img−P)·keepout_fade(protect)`, then `out[protect] = P`. Here protect = NOT(water ∪ fire zone). Ships, boats, people and paddles are explicit protect polygons cut out of the water.
- **Framing**: STATIC (z0 = z1). A constant crop is allowed, but there is no push, so the water never slides on screen.

## CLI
`render <cfg> <out.mp4> [--seconds --size WxH --crf]`, `reel <reel.json> <out.mp4>`, `proof <cfg> <out.json>`, `stats <cfg> <out.json> [--seconds]`, `overlay <cfg> <out.png>`. All outputs refuse to overwrite.

## Cases (reel order = best-reading first)
| case | plate | config |
|---|---|---|
| moonlight path | day7/nan-madol-saudeleur/assets/owner/seq4a_oral_floating_stones_canal.png | configs/nm4a_moon_path_v1b.json |
| torch/fire reflections | standalones/jianwen/plates-v1/k11_LEGEND_monk_leaves_burning_city.png (static crop z 2.2) | configs/k11_fire_reflection_v1b.json |
| sun glitter | micro-anomaly/ugarit/plates/p05_coastal_town_raid_v2_OWNER.png (static crop z 1.6) | configs/p05v2_sun_glitter_v1d.json |

Reel: `final/water_v1_reel.mp4` (configs/reel_v1.json): 18 s, 1080x1920, 30 fps, crf 26, 1.36 MB, hard cuts.

## Proofs (proofs/)
- Impulse proof: ±24 on a 9-px grid in the plate the renderer reads, 7 times, compared with and without the impulses. Leaked px = 0 on all three shots; 89–98% of live impulses pass through unchanged in scale.
- Protect proof: 0 changed px in protect at all 7 times on all three shots.
- Decoded reel at 360x640 (`proofs/decoded_reel_phone_stats_v1c.json`): outside-allow px with a 1-s range ≥8 = 0 on every shot (codec p99 ≤1.7 levels). Whole-frame 1-s swing max: moon 0.27%, fire 5.87%, sun 0.20%.
- `decoded_reel_phone_stats_v1.json` and `_v1b.json` are TRUNCATED, invalid files from a JSON float32 bug. Use v1c.

## Honest phone read (360x640)
- **Moon**: reads. About 150 fixed sparkles on the moon column twinkle in place while the column breathes. It looks like moonlight glittering on a still canal, and the boats and men are untouched.
- **Fire**: reads strongest. The river reflections pulse in lockstep with the torch_v1c fire: correlation 0.97 with the source-zone luma and 0.80 with the raw flick curve. Reflection swing is about 34% p-p, matching the torch_v1c near-source level. The K11 plate is soft at a z 2.2 crop, and the reflections are a small band at phone size.
- **Sun**: reads, but it is the subtlest. The P05 sea is only about a third of the frame, even cropped. The glints are visible as warm-white sparkles, and the plate's own baked glitter does most of the work.
- **Limits**: glints are point sparkles on fixed sites, not shimmering bands. That is deliberate, because anything wider would have to travel.
