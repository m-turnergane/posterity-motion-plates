# water_v1: Light on Still Water (LOCKED 2026-10-30 4:53pm ET)

Owner verdict: "the water is good". The sea never moves: no displacement, ripple or
coastline warp. Only light changes, and only inside the water matte (plus painted flame
pixels on fire shots). This is the locked water treatment for Shorts and long-form.

**Source:** `src/motionplates/standalone/fx_water.py`

## Core Rules

1. **The sea never displaces** — no warp, flow or offsets anywhere. Only luminance and
   colour change, on fixed-point glints and a slow breathe.

2. **Glints are fixed sites** that twinkle in place. No travelling bands, no moving light
   gradients, no scrolling.

3. **Mattes only** — `out = P + (fx − P)·keep`, then `out[protect] = P`. Faces, hands,
   land, boats, coastline and text are 0 changed px (protect polys, feather 3–5 px).

4. **Protected areas 0 px** — proofs per shot: an impulse leak test (±24 on a 9-px
   lattice) must show 0 leaked px, and protect must show 0 changed px.

## Three Modes

### 1. Moon Path (nm4a_moon_path)
- `breathe` layer on the path (amp 0.07, hz 0.12–0.27, lum 70–220, cool tint 0.9/0.97/1.05)
- `glints` (≤150 fixed sites, twinkle rates 0.35–2.2 Hz, cool colour 210/228/255)

### 2. Sun Glitter (p05v2_sun_glitter)
- `breathe` layer (amp 0.06, warm tint 1.0/0.95/0.85)
- `glints` (≤160 sites, warm colour 255/232/190)

### 3. Fire Reflections (k11_fire_reflection)
- `fire_reflection` columns under each fire source, driven by torch_v1c's own per-frame
  `flick()` (same curve × pulse × gain; warm tint 1.0/0.9/0.75)
- `glints` with `clock: "fire"` (fire_k 3.0, ≤50 small sites, colour 255/196/130)
- Fire source gets torch_v1c treatment (requires fx_torch.py from PR #3)

## Layers

### `glints`
FIXED sites — the painted highlight peaks inside the eroded water matte, weighted by a
sun or moon path. Each site brightens and dims in place on its own slow twinkle clock
(two sines, 0.35–2.2 Hz, thresholded, so energy above 5 Hz stays low). Nothing travels.

Set `clock: "fire"` to make sites follow the mean torch_v1c flick.

Key parameters:
- `path`: {x, x_bot, y: [y0, y1], w: [w0, w1]} — sun/moon column
- `hp_sigma`: high-pass sigma for peak detection (default 5.0)
- `thresh`: minimum high-pass value (default 12.0)
- `n_max`: maximum number of sites (default 120)
- `sigma`, `star`, `star_len`, `halo`, `halo_sigma`: stamp shape
- `rate_lo`, `rate_hi`: twinkle frequency ranges
- `color`: glint colour [R, G, B]

### `breathe`
A static path × luminance map multiplied by one slow scalar (0.12 + 0.27 Hz). This is
the moon or sun column slowly breathing.

Key parameters:
- `path`: as above
- `lum_lo`, `lum_hi`: luminance range for the lit mask
- `amp`: breathing amplitude (default 0.08)
- `hz`: [slow_hz, fast_hz] (default [0.12, 0.27])
- `tint`: [R, G, B] multiplier

### `fire_reflection`
A static warm-reflection map (R−B × luminance × water), split into per-fire x-columns.
Each column is driven by that fire's own `flick()` value — the same per-frame curve as
the source glow (torch_v1c, LOCKED). The reflection therefore pulses with the fire.

Requires a `fire` block in the config to set up torch_v1c sources.

Key parameters:
- `warm_lo`, `warm_hi`: warmth (R-B) thresholds
- `lum_lo`, `lum_hi`: luminance thresholds
- `col_w`: column width as fraction of source width
- `gain`: flick multiplier
- `tint`: reflection tint

## Fire Block

When fire reflections are used, the config needs a `fire` block:

```json
"fire": {
  "torch": [[x0, y0, x1, y1], ...],  // fire/torch rectangles
  "spill_amp": 1.8,
  "pulse": 0.3,
  "seed": 11,
  "embers": false,
  "t0": 6.0,
  "zone_from_masks": {"thresh": 0.05, "dilate": 3}
}
```

The source fire gets LOCKED torch_v1c via fx_torch.py (PR #3). If fx_torch isn't available,
you can inject a fire renderer factory.

## Framing

STATIC (z0 = z1). A constant crop is allowed, but there is no push, so the water never
slides on screen.

## CLI

```bash
# render a single shot
python -m motionplates.standalone.fx_water render <cfg.json> <out.mp4> [--seconds S] [--size WxH] [--crf N]

# render a reel
python -m motionplates.standalone.fx_water reel <reel.json> <out.mp4>

# impulse and protect proof
python -m motionplates.standalone.fx_water proof <cfg.json> <out.json>

# phone-size stats
python -m motionplates.standalone.fx_water stats <cfg.json> <out.json> [--seconds S]

# overlay visualization
python -m motionplates.standalone.fx_water overlay <cfg.json> <out.png>
```

All outputs refuse to overwrite.

## Proofs

- **Impulse proof:** ±24 on a 9-px grid in the plate, compared with and without the
  impulses. Leaked px = 0 on all shots.
- **Protect proof:** 0 changed px in protect at all sample times.
- **Decoded reel at 360x640:** outside-allow px with a 1-s range ≥8 = 0 on every shot.

## Phone Read (360x640)

- **Moon:** ~150 fixed sparkles on the moon column twinkle in place while the column
  breathes. Boats and figures are untouched.
- **Fire:** River reflections pulse in lockstep with torch_v1c (correlation 0.97 with
  source-zone luma, 0.80 with raw flick curve). Reflection swing ~34% p-p.
- **Sun:** Warm-white sparkles on the sea. The plate's own baked glitter does most of
  the work.

**Limits:** Glints are point sparkles on fixed sites, not shimmering bands. This is
deliberate — anything wider would have to travel.

## KNOWN BAD EXAMPLE: k11_fire_reflection_v1b

Do not reuse shot 2 from the locked reel (Jianwen K11, static 2.2x crop). It was blurry
at 2.53 output px per plate px, and the fire was blotchy because the matte clipped 91%
of torch_v1c's halo and spill.

See `docs/K11-FIRE-DIAGNOSIS.md` for the full diagnosis. water_v1 now refuses any config
with zoom > 1.5x (see `docs/GUARDRAILS.md`).

## How to Apply

1. Copy the closest locked config to a NEW name.
2. Draw `water` and `protect` polys in plate coords, then set the layer paths (x, x_bot,
   y range, w range) on the light path.
3. For fire, list torch rects only on sharp native-res fire (see guardrails).
4. Run overlay (check polys), then proof (must be 0/0), render (PoC) and stats.
5. Render final at 1080x1920 crf 24–26. Never overwrite outputs.

## See Also

- `docs/GUARDRAILS.md` — Plate crop and fire sharpness guardrails
- `docs/K11-FIRE-DIAGNOSIS.md` — Why the K11 fire broke at 2.2x
- `docs/TORCH-V1C.md` — torch_v1c documentation (PR #3)
- Example configs in `examples/water_v1/`
