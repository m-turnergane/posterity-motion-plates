# Posterity motion presets (element-motion engine)

**Status:** R&D, batch 1 (2026-10-22). Presets marked **KNOWN-GOOD (b1)** have rendered through the config path, passed the determinism and isolation checks, and are waiting for editorial review. Nothing here is owner-approved yet.
**Engine:** `motion/iterations-2026-10-22/animate.py` (one CLI). Masks: `make_masks_batch1.py`, built from colour/luminance thresholds plus polygons (no AI imagery).
**Iteration log:** `motion/ITERATIONS-2026-10-22.md`.

## How to run
```
/workspace/mpvenv/bin/python animate.py --config configs/<plate>.json [--repeat-check] [--suffix _vN] [--out-dir /tmp/preview]
/workspace/mpvenv/bin/python qc_layers.py    configs/<plate>.json   # per-layer max displacement (px), inside protect mask
/workspace/mpvenv/bin/python qc_isolation.py configs/<plate>.json   # each layer alone: diff outside its own mask (must be 0)
```
* The output is a BEFORE|AFTER review clip: 720x1280, 30 fps, H.264 yuv420p, no audio, default 2 x 4.0 s. Each half gets the standard StablePush, a scale-only centre zoom from 100 to 104 %. Labels and the one-line note come from `labels`.
* The engine refuses to overwrite an existing MP4. To version a render, use `--suffix`.
* **Stability QC on every render** (`<out>/qc/<name>.qc.json`):
  * `plate_outside_max`: plate-space max |AFTER − plate| outside the union of layer masks, as float and as u8.
  * `out_outside_max`: the same check in output space, after the identical zoom, outside the warped mask dilated by 2 px.
  * Displacement max overall, outside the masks, and inside `protect` masks, each with the location.
  * `changed_pct` and `mean_abs_diff`.
  * Every render also writes a mask-overlay still (each layer tinted; white hatch = protect), a mid-clip AFTER still, a full-resolution plate-space AFTER still and a diff heat map.
* **Determinism:** the engine seeds a numpy Generator with `[seed, layer_index]` and uses periodic FFT noise. It runs x264 with fixed threads and `+bitexact`, with no metadata. `--repeat-check` renders a second time into `determinism/` and compares the MP4 md5 and a SHA-256 over the raw labelled frames. All batch-1 clips came out byte-identical. Map and light were also re-rendered a third time after a later code edit and matched again.
* The union-mask check proves nothing when a layer covers the full frame (cloud shadows, light-shift, full-frame ash/embers). In that case, read `qc_isolation.py`, which renders each layer alone and checks the area outside that layer's own mask.

## Common config fields
```json
{ "name": "...", "plate": "<path under /workspace/posterity or absolute>", "out_dir": "batch1", "seed": 1234,
  "fps": 30, "size": [720, 1280], "half_seconds": 4.0, "camera": {"z0": 1.0, "z1": 1.04},
  "protect": ["masks/..png"],          // displacement is measured here (should be 0); light may still change
  "labels": {"before_note": "...", "after_note": "..."},
  "layers": [ {"preset": "<name>", "mask": "masks/..png", "strength": 1.0, "params": {...}} ] }
```
* A mask is an 8-bit PNG at plate resolution: 0 = untouched, 255 = full effect, values in between = soft.
* `strength` scales the whole layer.
* Stage order inside the engine:
  1. displacement (water, sky, foliage), applied as one remap; pixels with zero displacement are copied exactly
  2. shade (water shimmer, cloud shadows, parchment, foliage dapple)
  3. overlay (smoke, ash, haze, route ink)
  4. grade (light-shift)
  5. emit (fire, hotspots, embers, rays, route head, markers)

  Emissive light comes after the grade, so fires take over as dusk falls.

---

## map-light — KNOWN-GOOD (b1)
**Purpose:** bring a painted map to life without touching its geometry: parchment light sweep, drifting cloud shadows, an ink route that draws itself on, and glowing place markers. It uses no displacement.
**Fields** (each sub-block is optional; leave a block out to disable it):
| block | fields (defaults) |
|---|---|
| `parchment` | `strength` 0.06, `angle_deg` 30, `width_frac` 0.45, `x_from` −0.4, `x_to` 0.9 (band position over the AFTER half), `warm` [1, .88, .66] |
| `cloud_shadows` | `strength` 0.16, `lo` 420 (largest cloud, px), `hi` 110 (smallest detail, px), `beta` 3.0 (higher = softer), `coverage` 0.35, `softness` 1.2, `velocity` [px/s x, y], `tint` per-channel darkening [1, .93, .80] (blue darkens least, so shadows read cool) |
| `route` | `points` [[x,y],...] in plate px (Catmull-Rom smoothed), `t0`/`t1` draw window (s, eased), `width` 3.2, `color` [112,26,20] oxblood ink, `opacity` .88, `dash` [on, off] px, `halo` .35 (warm under-glow), `halo_sigma` 3, `head_glow` 1, `head_color`, `head_sigma` 5, `supersample` 4. The ink is modulated by a paper-grain noise. |
| `markers` | list of `{xy, t_on, radius 9, color, pulse_hz .55, gain 1, ring true}`. A marker with `t_on` > 0 ignites with a flash. Set `t_on` = route `t1` to light the destination as the line arrives. |

**Mask:** the area where cloud shadows and parchment light apply (full map, or land only). The route swath and marker discs are added to the allow mask automatically.
**QC (b1, seq09a map):** isolation diff outside own mask 0; displacement 0. With water on the sea in the same clip, sea displacement max 0.98 px and 0 px on land and coast.
**Known-good example:** `configs/b1_map_seq09a.json` → `batch1/b1_map_seq09a_roanoke_croatoan_final.mp4`.
The same preset also ran with only `cloud_shadows` on the land mask of an environment plate (`configs/b1_env_p07.json`).
**Tuning notes:**
* v1 used `hi` 40 and `beta` 2, which gave blotchy "camouflage" shadows. Keep `hi` ≥ 100 and `beta` ≥ 3.
* At 720p, use a route `width` ≥ 4.5 px (plate px) and `halo` around 0.4, or the line disappears on a phone.

## water — KNOWN-GOOD (b1)
**Purpose:** sea, bay or river motion: a travelling ripple displacement tapered to 0 px at the shore, a luminance shimmer, and optional sun glints.
**Fields:**
* `amp_px` 1.2: maximum displacement. It is bounded with tanh, so the measured max is ≤ amp × 1.0 horizontally.
* `dir_deg` 0 and `speed` 14 px/s.
* `lo` 140 / `hi` 6: ripple scale.
* `stretch` 3: ripples elongated along x (horizontal swells).
* `shimmer` 0.07.
* `glint` 0 (0–1.5), `glint_thresh` 2.4 (higher = sparser), `glint_color`, `glint_lum_power` 2 (glints favour already-bright water).
* `coast_margin_px` 3 and `coast_blur_px` 4: the displacement mask is eroded by margin + amp, so no land pixel is ever sampled into the water.

**QC (b1):** map sea 0.98 px max, 0 px inside the land/coast protect mask. Ugarit coast sea 1.52 px max, 0 px on stone/land. Isolation diff outside own mask 0 on both.
**Examples:** `b1_map_seq09a` (subtle painted sea, glint 0) and `b1_env_p07` (bright Mediterranean, glint 1.2).
**Tuning note:** an early build had the anisotropy inverted, which produced vertical streaks; this is fixed (`ax=stretch`). Use a glint threshold of at least 2.6, or the sea looks like static.

## sky — KNOWN-GOOD (b1), with a caveat
**Purpose:** cloud drift. The painted sky content slides with height parallax (faster near the top of frame) plus a slow 0.8 px billow. The motion tapers to 0 at the skyline.
**Fields:** `velocity` [7, 0] px/s, `parallax` 0.8, `billow_px` 0.8, `billow_lo` 120, `edge_erode_px` 2, `edge_blur_px` 10.
**QC (b1, p07):**
* This is a deliberate translation of sky content: up to 48 px at the top of frame by the end of 4 s at 9 px/s with parallax 0.9.
* Displacement into land/stone: 0 px. Isolation diff outside the sky mask: 0.
* **Caveat:** the plate has no sky beyond its own edge, so the strip within the drift distance of the trailing (left) edge is filled with mirrored cloud. In the zoomed frame this is about 30 px at the top-left corner by the end of the clip. It looks like cloud, but it is synthesized.
* In the 10 px taper band at the skyline the sky stretches slightly, because the plain horizon haze compresses there.

**Next:** for long holds, cap the drift at about 4 px/s, or extend the sky with a mirrored pre-pad in the mask tool.

## foliage — KNOWN-GOOD (b1)
**Purpose:** grass, shrubs and tree canopies swaying in wind. Travelling gust fronts (`gust_speed`, `gust_len`) modulate a coherent sway with a per-clump phase, plus fine leaf flutter and a leaf-light dapple in luminance.
**Fields:** `amp_px` 1.1, `dir_deg` 0, `gust_speed` 90 px/s, `gust_len` 420 px, `sway_hz` 0.7, `flutter` 0.35, `flutter_lo` 14, `dapple` 0.05, `edge_erode_px` 0, `edge_blur_px` 1.5, `vertical` 0.3.
**QC (b1, p07):**
* Max displacement 1.49 px, bounded since `_final_v2`; the first final render had unbounded flutter peaking at 4.0 px.
* 0 px inside the stone/wall protect mask. Isolation diff outside own mask (dilated by 2·amp) is 0.
* At the foliage edge, displaced samples can pull in up to about 1.5 px of the neighbouring wall or ground. This is a measured warp, kept small by the taper.

## smoke — KNOWN-GOOD (b1)
**Purpose:** rising smoke columns over painted plumes or chimneys, plus optional falling ash. Each plume is an advected noise column that widens with height, has a travelling meander, boils through two textures moving at different rise speeds, and shades from dark at the base to light at the top. It uses no displacement.
**Fields:**
* `plumes[]`: `{src [x,y], top [x,y], w0 10, w1 90, opacity .55, rise 22 px/s, color_dark, color_light, meander .18, meander_len 180, lo 60, hi 4}`
* `ash`: `{count, size [.6,1.8], big_frac .08, big_size [2.5,4.5], fall [8,26] px/s, wind [10,2], sway 6, color, opacity .55, mask (none = full frame, i.e. in front of everything)}`

**Mask:** clips the plumes (for example, the doorway opening, so smoke stays behind the frame).
**QC (b1, p06):**
* Displacement 0. Isolation diff outside own mask 0.
* Own-mask coverage is 100 % because the ash has no mask and falls in front of the doorway frame on purpose, for depth.

## atmos — KNOWN-GOOD (b1)
**Purpose:** haze and mist sheets drifting through a height band, plus crepuscular light rays.
**Fields:**
* `haze`: `{color, opacity .22, lo 260, hi 30, velocity [12,-1], band [y0,y1] or null, band_soft 120, contrast 1.3}`. The noise is horizontally stretched, so the haze forms sheets.
* `rays`: `{origin [x,y] (put it off-frame or behind smoke), strength .16, color, n_scale 40 (angular shaft width in samples per 4096 per turn), speed .002 (turns/s), falloff 900, near_fade [40,260] (no visible star point), luma_gate .35 (rays read more on bright, smoky areas)}`. Rays are screen-blended.

**QC (b1, p06):** displacement 0; isolation diff outside the opening mask 0.
**Tuning notes:**
* An `n_scale` below about 30, or an origin inside the frame, gives a hard starburst. v1 and v3 previews were rejected for this.

## light-shift — KNOWN-GOOD (b1)
**Purpose:** a time-of-day grade (day to dusk by default), eased between `t0` and `t1`.
**Fields:**
* `t0` .3, `t1` 3.7
* `gain` [1.06,.84,.66], `ev` −0.45
* `shadow_color` [40,30,70], `shadow_amt` .22 (cool lifted shadows)
* `sky_mask` + `sky_gain` (extra warmth in the sky only)
* `sun` [x,y] or null, `sun_radius` 260, `sun_color`, `sun_strength` .35 (low sun or fire glow on the horizon, screen-blended)

**QC (b1, p06):** displacement 0. It covers the full frame by design (mask `p06_full.png`).
**Tuning note:** a v1 `sky_gain` of [1.18,.8,.66] over-saturated the sky into flat orange. [1.1,.86,.74] with `sun_strength` .3 holds the painted smoke.

## fire-torchlight — KNOWN-GOOD (b1)
**Purpose:** fire and torchlight with light thrown onto surfaces:
* Each source flickers deterministically, from four sine bands plus smoothed noise.
* Small procedural flames (teardrop shape with rising tongues, additive).
* Light is thrown onto surfaces by multiplying the surface's own albedo, limited to the layer mask, so stone takes warm light and black char stays dark.
* Smoulder hotspots on a char mask breathe and bloom, and light the ground around them.
* Embers rise with sway and flicker.

**Fields:**
* `sources[]`: `{xy, flame [w,h] (0 = light only), light_radius 120, intensity .5, color [255,150,70], flame_gain 1}`
* `hotspots`: `{mask, coverage .18, lo 70, hi 6, gain .9, color, breathe .35, bloom 6, light .25, light_radius 40}`
* `embers`: `{count, spawn [[x,y,rx,ry],...], rise [25,70], life [1.2,2.6], drift, sway 8, size, color, gain, mask}`

**QC (b1, p06):**
* Displacement 0. Isolation diff outside own mask 0.
* Coverage is 100 % because the embers are unmasked and may cross the doorway.

**Not yet tested:** candle or torch on interior walls, the classic use. That is the planned batch-2 lighting test on a day19/rome69 interior.

---

# Batch 2 additions (2026-10-22, afternoon)

**Engine regression check:** after every batch-2 edit, the batch-1 configs (map, light) and the batch-2 candle config were re-rendered with the current engine. They reproduce their original md5s exactly (c63bbe60…, 1fb0d7e9…, 2962e4ac…). New parameters are opt-in and draw from the RNG only when enabled, so old configs are stable.
**New QC helper:** `qc_spill_sync.py configs/x.json '{"region":[x0,y0,x1,y1],...}' '[flame box]'`. For each region it reports the relative luminance swing over the AFTER half, the largest per-frame step, and the correlation with the flame's own brightness, which is the sync proof.

## fire-torchlight → `light_spill` — KNOWN-GOOD (b2, candle)
**Purpose:** relight a still plate around a light source with no geometry change. The candle glow breathes across faces, hands, paper and walls in exact sync with the flame.
**How it works:**
* Each source has ONE deterministic flicker curve, `_flick`.
* The spill reads that same curve, as do the painted-flame modulation, the procedural flame and the halo. Flame and light therefore cannot drift apart.
* The spill is a zero-mean modulation around the painted lighting: `img *= 1 + amp·falloff·facing·mask·(flick−1)·tint`. It brightens and dims around the plate's existing candle-light instead of adding an extra lamp. Because it multiplies surface albedo, dark cloth stays dark and the paper and skin respond most.
* **Falloff:** `1/(1+(d/radius)^power)`, inverse-square-ish with a soft core. The distance is measured from the flame's optical centre (`source.xy + offset`).
* **Facing heuristic** (no AI depth): `facing = floor + (1−floor)·clip(warm_weight·lit + grad_weight·gterm)`.
  * `lit` = surfaces the painting already shows candle-lit (luminance × warmth).
  * `gterm` = the local luminance gradient pointing toward the flame. Brightness rising toward the light means the surface faces it.

**Fields:**
* `light_spill[]`: `{source 0, mask (relight mask; exclude windows/exteriors), radius 300, power 2, amp 0.5, tint [1,.85,.6], offset [0,0], facing_floor .25, warm_weight .6, grad_weight .4, grad_sigma 6, lum_lo .02, lum_hi .35}`
* `sources[].flicker`: `{amps[4], freqs[4] Hz, noise, noise_hz, floor, smooth}`. Use `smooth: true` (smoothstep noise interpolation) for candles, which avoids kinks and flash-pulsing.
* `sources[].cast_light`: false = light only via the spill. `sources[].halo`: `{sigma, gain}` for a small warm halo.
* `plate_flame`: `{source, mask (flame pixels), gain .35, tongue .18, rise 60, hot}`. The painted flame's own pixels breathe with the curve, plus a rising tongue texture. This is luminance and tint only.

**QC (b2 candle, `configs/b2_candle_seq14.json`):**
* Displacement 0 px everywhere (protect = full frame). Isolation diff outside the relight mask: 0. The window/night exterior is excluded and does not change.
* Luminance swing, relative to the plate:

  | region | swing | std | max per-frame step | correlation with flame |
  |---|---|---|---|---|
  | face | −5.2…+3.8 % | 2.0 % | 2.8 % | 0.965 |
  | left hand (nearest) | −12.6…+8.4 % | 4.7 % | 6.6 % | 0.968 |
  | paper | −6.7…+4.8 % | 2.6 % | 3.5 % | 0.966 |
  | far wall | ±1.8 % | 0.7 % | – | 0.965 |
* Known-good params: radius 450, power 2, amp 1.0, flicker amps [.09,.05,.025,.01] at [0.8,1.9,3.7,7.9] Hz, noise .06 @ 7 Hz, floor .6, smooth.

**Later targets (planned):**
1. Firelight on stone for Ugarit P06. The same falloff × facing idea is already reused in P06 v2: each flame bed throws its own flickering light onto nearby rubble.
2. Gold glints in Atahualpa's room. Proposed approach: the spill map × a specular mask of the gold objects (high-luminance, warm-hue threshold), with a sharper response (gain applied to `flick^3`), so the gold catches each flicker peak.

## fire-torchlight → `flame_tongues`, `shimmer`, `sparks` — b2, REVIEW (P06)
**`flame_tongues`:** procedural licking flames rising from hand-placed fire beds (base polylines laid on charred timbers and on the skyline plume bases).
* **Field:** for each bed, a precomputed distance-above-base field. Per frame, it is warped by rising noise: tongue sway grows with height, and a per-column tongue-height texture scrolls upward, so tongues rise, split and reshape. There is also a clump noise along the bed and a per-bed flicker curve.
* **Colour:** a blackbody-ish LUT (deep red → orange → yellow → warm cream, never white).
* **Compositing:** opaque-ish core (`cover`) plus screened luminous edges, plus a warm bloom. It is emissive, after the dusk grade.
* **Firelight:** each bed throws flickering light (falloff × painted-lit facing) onto surfaces inside the layer mask.
* **No plate displacement:** the noise displaces only the generated flame field.
* **Fields:** `{rise 95, sway_px 5, tongue_lo 20, tongue_hi 6, tongue_sharp 1.5, body .8, clump_gain .8, cover .55, bloom .45, bloom_sigma 7, light .55, light_radius 120, light_color, lut, flicker{…}, beds[{points, thickness 6, height 50, intensity 1, clump .55, light_scale 1}]}`

**`shimmer`** (heat haze):
* The air column is computed from each bed's distance field, `band` × flame height above the base.
* **Plate displacement is applied ONLY to that column ∩ a strict sky mask**, eroded by `sky_erode_px + amp`, so no stone pixel can ever be sampled or moved.
* Over ground fires, where the air column is backed by stone, the shimmer refracts only the generated flame layer and never the plate.
* Fields: `{amp_px 1.2, lo 10, rise 70, band [.45, 2.4], sky_mask, sky_erode_px 3}`.

**`sparks`:** fast short-lived streaks spawned along the beds and weighted by flame size, with gravity and turbulence, cooling hot→orange.
* Fields: `{count 200, rise [90,230], life [.35,1], spread 35, gravity 60, turb 25, size [.5,1], gain 1.2, hot, cool, streak .8, mask}`.

**QC (b2 P06, `configs/b2_light_p06_v2.json`):** see ITERATIONS-2026-10-22.md for the numbers. The key results are plate displacement ≤ 1.4 px on sky only, and **0 px on every non-sky pixel** (`p06_protect_nonsky_v2.png`).

## map-light → nib `route` + ink `markers` — b2, REVIEW (map)
**Route `style: "nib"`** (hand-inked):
* The path is resampled at 1 px. Width varies along its length (`width_var`, `width_var_len`), with a pressure ramp where the nib lands.
* Dashes are optional, with ±`dash_jitter` hand irregularity.
* A per-pixel draw-time map gives each ink pixel its age. Wet ink near the tip is dark and dense (`wet_color`, `wet_opacity`). Behind the tip it dries over `dry_time` toward `dry_color`/`dry_opacity`, a visible tone shift.
* Ink wicks into the paper fibres after it is laid: anisotropic fibre-noise feathering outside the stroke, growing over `wick_time`.
* Ink density varies with the paper tooth.
* An ink bead pools at the nib while drawing. It is dark, never a glow.
* Blend: multiply/pigment mix (`pigment` 0 = transparent multiply, 1 = opaque).

**Ink markers** (`style: "ink"`): a circle drawn as a quick pen stroke over `draw_s`, then a centre dot. They use the same wet→dry ink, with no glow and no bloom. The glow markers and the route `head_glow` remain available for old configs only.
**Fields (`ink` block):** `{wet_color [40,8,8], dry_color [128,56,40], wet_opacity .97, dry_opacity .85, dry_time .8, wick_time 1.2, width_var .22, width_var_len 70, feather .45, feather_px 1.4, fibre_lo 7, bead .75, dash_jitter .25, density .14, pigment .5}`; route `{style "nib", points, t0, t1, width 2.7, dash null | [on, off]}`.
**QC:** see the log. Displacement is 0 on land and coast; the only displacement is the existing sea water (≤ 0.98 px).

---
# BATCH 3 additions (2026-10-22)
All new parameters are **opt-in**. Their code defaults reproduce the old output exactly; the regression check is in ITERATIONS.
**Raised "recommended strengths" (batch 2 was too weak on a phone):** use these values for new work.
The code defaults were deliberately NOT changed, so b1/b2 configs still re-render bit-identically.

| Preset / field | b2 value | **b3 recommended** |
|---|---|---|
| map-light cloud-shadow strength | .21 | **.32** (lo 700, softness 2.3, to stay non-blotchy) |
| nib route width | 2.7 | **7.2** (dash [24,11]) |
| nib ink wet / dry | [40,8,8] / [128,56,40] | **[62,10,6] / [142,46,26]** (redder) |
| light_spill amp | ~1.0 | **1.35**, plus `light_pool` dark .22 / breathe .7 |
| candle flicker amps | small | **[.15,.08,.035,.015]** @ [.55,1.3,2.6,4.4] Hz, floor .45 |
| P06 flame beds | 55–85 px | **×1.45–1.5 wide, ×1.75–1.8 tall**, `clip_to_mask` ON |
| shimmer | amp 1.2, band [.45,2.4] | **amp 1.8, band [.35,4], spread_px 40** |

## fire-torchlight → `flame_warp` + `light_pool` — b3 (candle), SHOW
* **`flame_warp`** `{source, mask, base, height 40, sway_px 3, sway_hz [.9,2.3], stretch .35, zone_px 5, lean_px 0}`:
  sways and stretches the painted flame along the flicker curve.
  The displacement is confined to the flame mask plus `zone_px`; protect masks stay at 0 px.
* **`light_pool`** `{source, mask, center, r0 500, power 2, dark .35, breathe .6, tint}`:
  a radial dark falloff around the light source that breathes with the same flicker curve.
  This makes the pool of light read on a phone without strobing.

## map-light ink: bloom / sheen / wobble / tip_always / speed_var; marker bloom — b3 (map), SHOW
* **`ink` block, new fields:**
  * `bloom 0` (.55 recommended), `bloom_px 3`, `bloom_s .25`, `bloom_settle .35`: each dash spreads slightly as it is laid, then settles.
  * `sheen 0` (.4), `sheen_px 1`: a thin wet highlight offset up-left that fades as the ink dries. Above .5 it reads as a pale rim.
  * `wobble_px 0` (1.2), `wobble_hz 6` (5): the bead wobbles perpendicular to the stroke and pulses in size.
  * `tip_always false` (true): the bead shows in dash gaps at 0.7 size.
  * `speed_var 0` (.45): sinusoidal variation in draw speed.
* **Markers:** `bloom` (+ `bloom_r`, `bloom_s`, `bloom_settle`) adds a fibrous ink blot that spreads, then settles.
  The fibre texture is seeded from the marker coordinates. Use it for the start mark and the arrival stamp. There is no glow.

## fire-torchlight → `flame_tongues`: body_mix / despeckle / pad_mult / soot / clip_to_mask — b3 (P06), SHOW
* `body_mix 0` (.6), `body_scale .35`: a broad low-frequency flame body, giving full volumes instead of wisps.
* `despeckle 0` (.07): blurs the height map along x. **Values ≥ .15 flatten the flame tops.**
* `pad_mult 2.6` (3.6): bounding-box headroom so tall flames aren't clipped.
* `soot null` → `{gain .6, lo .9, hi 2.8, ramp .5, smooth .35, fade [.4,.95], color [26,21,20]}`:
  a dark haze above the tongue tips that feeds into the smoke.
* **`clip_to_mask false` → ALWAYS true for new work.**
  The flame, hotspot glow and (via their own `mask`) sparks and embers are multiplied by the layer mask.
  Without it, a bed near a foreground frame can paint over it; the allow-region QC does not catch this (P06 v3 jamb leak).
* `shimmer.spread_px 0` (40): widens the heat-haze column horizontally. It is still sky-only for the plate.

## water-glint — b3, BORDERLINE (light only, 0 px displacement)
* A sun or moon path drawn by light only: a broken column toward the source, plus perspective glints from two scrolled noise textures.
  Their threshold is lower inside the path.
* **Fields:** `{light_x, horizon_y, path_w0 20, path_w1 220, path_power .9, along [1,.55], path_gain .18, broken .7, su .9, sv 40, wave_speed .035, cross_speed .004, thresh_in 1.6, thresh_out 3, glint_gain 1.3, glint_gamma 1.6, twinkle .6, outside .15, color, bloom .35, bloom_sigma 1.6, lum_follow .5, glint_lo [18,12], glint_hi [1.2,1]}`.
* **Recommended for phone:** `glint_lo [30,22]`, `glint_hi [5,4]` (larger glints), `outside 0–.03`, `lum_follow .7–.85`, `glint_gain 6`, `thresh_in .45–.5`, `gamma .7`, `path_gain .35–.4`, `bloom .6`.
* Coast and land are untouched (mask-only, no remap).

## QC: `qc_layermask.py <config>`
* Reports each layer's max change outside its **declared mask PNG** at 5 sample times.
* Run it alongside `qc_isolation.py`. Expected non-zero values: smoke with foreground ash (P06), which is intentional.

---
# LOCKED HOUSE PRESETS (batch 4, 2026-10-22) — APPROVED-DEFAULT
Owner-approved in batch-3 review. These are **frozen**: never edit the locked JSONs. To change one, make a `-v2` and get it approved.
* Frozen engine copy: `presets/locked/engine/animate_b3_cb9e2b88.py` (animate.py md5 at lock time `cb9e2b880ab7b6940043ce3723de590a`).
  Later engine versions add opt-in fields only, so the locked JSONs still render bit-identically (see the batch-4 regression check in ITERATIONS).
* Verification: `--repeat-check` reproduces both md5s (`presets/locked/verify/<preset>/`, render plus determinism rerun, md5 and frame-sha256 identical).

## `house-candle-lightspill-v1` — APPROVED-DEFAULT (owner: "phenomenal")
* Locked JSON: `presets/locked/house-candle-lightspill-v1.json`, a byte copy of `iterations-2026-10-22/configs/b3_candle_seq14_v2.json` (md5 `0591d4c770c5363f1ca6135a5d961d17`).
* Reference render: `batch3/b3_candle_seq14_lightspill_v2.mp4`, md5 **`030cbcbb8bbb5977066975a5c7f5b9e7`** (frames sha256 `e2ceba2c…`).
* **Plate and model:** plate `serials/croatoan/ch2/plates/seq14_white_ireland_letter_candle_OWNER.png`, seed 1415.
  Protect `batch3/masks/seq14_protect_nonflame_v2b.png`. One `fire-torchlight` layer, mask `batch2/masks/seq14_relight.png`.
* **Source:** xy [59,1001], flame [4,26], flame_gain .3, cast_light false, colour [255,165,80], halo sigma 34 / gain .22.
* **Flicker:** amps [.15,.08,.035,.015], freqs [.55,1.3,2.6,4.4], noise .05 @ 4 Hz, floor .45, smooth.
* **flame_warp:** mask `batch2/masks/seq14_flame.png`, base [59,1001], height 36, sway_px 3, sway_hz [.8,2.1], stretch .45, zone_px 6.
  This is the **only** displacement in the clip: inside the flame mask. Everywhere else is 0 px.
* **plate_flame:** gain .6, tongue .08, rise 70.
* **light_pool:** center [300,950], r0 520, power 2.2, dark .22, breathe .7, tint [1,.95,.9].
* **light_spill:** radius 800, power 2, amp 1.35, tint [1,.8,.5], offset [0,-14], facing_floor .45, warm_weight .65, grad_weight .35.
  Amber falloff with distance from the flame.
* **Measured light swing** (luma, AFTER):

  | Region | Swing |
  |---|---|
  | Face | ~31 % peak-to-peak |
  | Hand | ±26.5 % |
  | Paper | ~±21 % |
  | Frame | ~±18 % |
  | Max step | ≤ 5 %/frame (no strobe) |

* Clip: BEFORE 4 s / AFTER 4 s, 100→104 % centre zoom, labels, 720x1280 / 30 fps / H.264 crf 17 bitexact, no audio.

## `house-map-inknib-dashed-v1` — APPROVED-DEFAULT (owner: "great too")
* Locked JSON: `presets/locked/house-map-inknib-dashed-v1.json`, a byte copy of `configs/b3_map_seq09a_dashed_v3.json` (md5 `d0ad9016f8aad5bc06f1d20317a372b5`).
* Reference render: `batch3/b3_map_seq09a_inknib_dashed_v3.mp4`, md5 **`b8aa9ceb7cae2757a44d9919eb8ddd9f`** (frames sha256 `dc6c079d…`).
* **Seed and clouds:** seed 9093. Cloud shadow strength **.32** (lo 700, hi 160, beta 3.2, coverage .45, softness 2.3, velocity [30,10]). Parchment .09.
* **Route:** t0 .25 → t1 2.6, **width 7.2 px**, dash [24,11].
* **Ink:** redder wet ink [62,10,6] drying to [142,46,26] (dry_time .9). **Nib bead** .85, **dash bloom** .55, **wet sheen** .4.
  Wobble 1.2 px @ 5 Hz, tip_always, speed_var .45.
* **Markers:**
  * **Roanoke start mark** [520,322] at t0, r11, bloom .75.
  * **Croatoan stamp** at endpoint **(668,1405)** at t 2.6, r14, bloom .9, bloom_r 1.45.
* Layers: `water` (sea only, disp ≤ 0.974 px, inside the sea mask) and `map-light`. Land and coastline are static.

## OWNER PRODUCTION RULE — candles and small fires (2026-10-22)
* **By default, every production plate containing candles or small fires** (candles, torches, oil and flame-lit lamps, braziers, hearth-size fires) **gets `house-candle-lightspill-v1`**, starting with **Atahualpa (10/23)**.
* Mask each light source **and** the surfaces it would light.
* **Keep:**
  * flame sway (inside the flame mask only)
  * **0 px displacement** everywhere else
  * the slow **100→104 %** zoom, with the house cuts underneath
* **Large fires and burning cities stay R&D** (the P06 fire-light work below) until the owner approves a version.

### Applying the candle preset to a new plate (recipe, ~20–30 min per plate)
1. **Copy** `presets/locked/house-candle-lightspill-v1.json` to `configs/<show>_<plate>_candle_v1.json` (a new file; never edit the locked one).
   Set `plate`, `name`, `out_dir`, and a new `seed`.
2. **Draw three masks.** Use colour/luminance threshold plus polygons, with no AI generation.
   * **Flame mask:** the visible flame(s) only, feathered 2–3 px. This is the sole region allowed to move (`flame_warp.mask`).
   * **Relight mask:** the light source plus every surface it would light (faces, hands, paper, table, nearby wall), feathered 20–40 px.
     Leave out sky and windows, and anything behind an occluder (this is the `fire-torchlight` layer `mask`).
   * **Protect mask:** everything except the flame zone (`protect`). It keeps the rest of the plate pixel-exact except for light.
3. **Tune, in this order:**
   1. `source.xy` (the flame base), `flame` [w,h] to the drawn flame size, and `halo.sigma` (≈ 1.3 × flame height).
   2. `flame_warp.base` = flame base, `height` ≈ flame height × 1.4, `sway_px` 2–4 (scale with flame size).
   3. `light_spill.radius` ≈ the distance to the furthest lit surface × 1.2, `offset` toward the wick (about −0.5 × flame height in y), and `amp` 1.0–1.5.
      Target face/paper swing of ±20–30 %, max step ≤ 5 %/frame.
   4. `light_pool.center` = the centroid of the lit surfaces, `r0` ≈ the pool radius, `dark` .15–.25 (darker room = higher).
   5. Flicker `amps`. Keep the freqs. For several candles, give each source a different seed/phase.
   * Multiple sources: one `fire-torchlight` layer per source, or a per-source mask. Torches: raise `flame` and `sway_px` about 1.5×, and drop `light_spill.radius` to the torch's reach.
4. **QC:** `--repeat-check`, then `qc_isolation`, `qc_layers` (disp 0 outside the flame mask), `qc_layermask`, and `qc_phone` (judge at 360x640).

---
# MOTION ROADMAP (owner-approved 2026-10-22)
**Policy:**
* Each owner-approved preset is a **default** in this file. It is auto-applied in builds whenever a plate contains that element, with a per-plate mask.
* **Only owner-approved presets ship in production.** Everything else stays R&D.
* Status tags: **APPROVED-DEFAULT** (ships, auto-applied) vs **R&D** (not for production).

Order, after the current batch-4 P06 fire and water-glint work:

| # | Area | Element | Status |
|---|---|---|---|
| 1 | Maps | Ink routes (`house-map-inknib-dashed-v1`) | **APPROVED-DEFAULT** |
| 1 | Maps | Markers/stamps landing (part of the locked map preset: Roanoke mark, Croatoan stamp; standalone use is R&D) | APPROVED-DEFAULT within the map preset; R&D standalone |
| 1 | Maps | Borders spreading | R&D (not started) |
| 2 | Fire & night light | Candles/small flames (`house-candle-lightspill-v1`) | **APPROVED-DEFAULT** |
| 2 | Fire & night light | Big fires / burning cities (P06 fire-light, v4 in progress) | R&D |
| 2 | Fire & night light | Torchlit crowds | R&D (not started) |
| 3 | Sea & coast | Glints on still water (water-glint, v3 in progress) | R&D |
| 3 | Sea & coast | Mist/fog over shore | R&D (not started) |
| 3 | Sea & coast | **Rule: never move water or warp the coastline** (light-only) | standing rule |
| 4 | Sky & weather | Slow clouds, shifting sunset light (light-shift is known-good in R&D), falling snow/ash, rain | R&D |
| 5 | Smoke & dust | Battlefield haze, embers, dust in a light beam (smoke/atmos/sparks exist as R&D) | R&D |
| 6 | Documents & objects | Writing appearing in sync with narration (**exact-quote rule**: only the exact quoted words), gold/coin glints | R&D (not started) |
| later | Characters | Cloth, flags, breath, blinks: only after environments are reliable | R&D (deferred) |

**Status of the existing preset sections above:**
* `house-candle-lightspill-v1` and `house-map-inknib-dashed-v1` are APPROVED-DEFAULT.
* Every other section (smoke, atmos, light-shift, fire-torchlight beds/flame_tongues/shimmer/sparks, water-glint, water) is **R&D**.
  The "KNOWN-GOOD", "SHOW", "REVIEW" and "BORDERLINE" tags are internal R&D quality notes, not production approval.

---
# Batch 4 R&D presets (2026-10-22)

## fire-light (burning city / campfires / torches) → `flame_tongues` clumps + `bed_spill` — b4 (P06 v4), R&D (awaiting owner)
This is the candle light-spill model generalised to many fire sources. Each fire **clump** is its own light source with its own flicker,
throwing light-only spill on nearby walls and ground. 0 px displacement on stone; the only displacement is the shimmer, sky-only.
* **Reference:** `configs/b4_light_p06_v4r3.json` → `batch4/b4_light_p06_ugarit_burning_dusk_fires_v4.mp4` (md5 `aa7862de41a3907e8c37d6460377c11d`).
* **Per-bed (clump) fields, all opt-in:**
  * `rate` (flicker speed multiplier, 0.75–1.45 in P06)
  * `flicker` (an override dict merged over the layer's flicker)
  * `taper {floor .3, power .8, pad .15}` (mound profile, tallest mid-clump)
  * `spill_gain` (≤ 0 means no spill; P06 uses height/170 clipped to .5–1.25), `spill_radius` (overrides the default)
* **Build clumps, not strips.** Split each fire line into 2–5 clumps of different widths (30–120 px) and heights (60–230 px on a 941x1672 plate).
  Use thickness 9–15 and per-clump intensity .85–1.0. Distant skyline fires: thickness 5, height 25–65, light_scale .5, spill_gain .35.
* **`flame_tongues.bed_spill`** (P06 values):
  * radius_mult 1.1, radius_add 30 (R = 1.1·h + 30 px), power 2, base .3 (steady warm lift), **amp 1.35** (flicker swing), tint [1,.6,.3]
  * lift .35 (the light line sits 0.35·h above the bed), facing_floor .3, exclude [sky mask], **dark .18** (darkens away from all fires so the pools read), dark_radius_mult 1.6
  * Code defaults: warm_weight .6, grad_weight .4, grad_sigma 6, lum_lo .04, lum_hi .45, cut .03
* **Flicker (layer):** amps [.21,.12,.04,.015], freqs [.7,1.6,3.1,5.2], noise .04 @ 5 Hz, floor .45, smooth.
  Keep the top two amps small: amps [.2,.11,.05,.025] with noise .06 gave a 5.5–5.7 %/frame step (over the 5 % limit).
* **Keep:** `ft.light` low (.12; the bed's own additive glow), clip_to_mask true, shimmer sky-only, sparks/soot/smoke as in v3b.
* **Measured** (`batch4/qc/b4_light_p06_v4r3.spill_swing.json`, luma, frames 0–1.47 s @ 30 fps; script `qc_spill_regions_b4.py`):

  | Region | Lift vs plate | Peak-to-peak (half-swing) | Max step |
  |---|---|---|---|
  | Strong-spill walls/ground (266k px, flame zones excluded) | +58 % | 26 % p2p (±13 %) | 4.5 %/frame |
  | Ground below clumps | +80 % | 25 % (±13 %) | 4.7 %/frame |
  | Whole frame | +33 % | 14 % | 2.0 %/frame |

  The full swing is reached within the first second of AFTER.
* **Applying to torches/campfires:** one bed per fire (2–4 points along the fuel). Height = flame height, spill_gain 1.
  `spill_radius` = reach of the light. Mask = fire plus lit surfaces, excluding sky and occluders. Check `qc_layermask` for a 0 leak onto frames/jambs.

## water-glint v3: bigger clusters + streak + soft halo — b4, R&D (awaiting owner)
New opt-in fields (default off, so the b3 configs render identically):
* `grow_px` / `grow_gain` (dilated sparkle clusters)
* `star` / `star_len` (horizontal specular streak)
* `halo` / `halo_sigma` (soft wide bloom)
All are re-masked to the water.

**Phone-readable settings:**
* glint_lo [44,34], glint_hi [8,6], grow_px 2 / .75, star .5 / 17, halo .25 / σ9, bloom .6 / σ3
* thresh_in .55, glint_gain 2.2 (p07) – 2.6 (dusk), path_gain .2 (bright sun) – .3 (dusk), broken .85
* Sun path: path_w1 330. Dusk path: 260 with a warm colour [255,220,170].

**Too hot:** glint_gain 7.5 / thresh .42 / halo .45 blows the path into a solid white column.

## fire-torchlight: per-bed `seat` + bed_spill `dark_exact` (b5, opt-in)
* `beds[i].seat = {dark .45, dark_w 7, dark_up .35, glow .55, glow_w 3.5, glow_up .5, color [255,170,80], pad .2, tex .5}`.
  It adds a darker contact band under the flame base and a thin textured glow line where the flame meets the fuel, so street clumps sit on the timbers and rubble.
  It is confined to the layer mask and adds no rng draws, so old configs render identically.
* `bed_spill.dark_exact: true` computes the spill darkening from a full-frame distance transform, removing faint bbox-edge seams. The old path is unchanged when it is off.
* **P06 v5 settings:** bed_spill base .32 / amp .70 / dark .20, exclude `batch5/masks/p06_sky_v5.png` (which follows the real skyline).
  Light-shift: sky_gain [1.06,1.36,1.8], sun [720,650] r230 s.18. Rays neutral [236,226,214] s.13.
  14 small skyline blazes (w 9–26, h 16–62, independent rates .75–1.45) sit 2 px under the skyline.

## map-ink (b5, NEW preset, R&D)
Ink events on map plates. It reuses the locked ink (wet [62,10,6] → dry [142,46,26], opacity .97→.88, dry_time .9, pigment .55). It is colour-only (0 px).
* **stamps[]:** `xy, t_on, radius, ring_w, inner, inner_w, dots, emblem "star8", rot_deg`.
  * Drop: `drop_s`, a converging soft `shadow` plus a defocused `ghost` scaling 1.25→1. It accelerates, so there is no bounce.
  * Contact: ink squashes .965→1 (monotonic). Splat: `splat` droplets, `streaks` on the heavy-pressure side.
  * Afterwards: `press` paper darkening settles to `press_settle`, deboss `emboss`, wicking bloom, wet→dry.
  * Uneven rubber-stamp coverage (`cover`, `pressure`).
* **washes[]:** `mask, seed, t0, t1, power`.
  * Arrival time = geodesic distance from the seed inside the mask over a fingered speed field (`finger`, `finger_lo`; scipy dijkstra at 1/`step` res).
  * Look: dark wet `edge` front (`edge_s`), granulation `gran`, edge-pooling `rim`.
  * Optional `land` mask: draws an inked border only where the region meets other land (not along the coast).
* **Phone-readable:** stamp radius ≥ 80 px on a 941-wide plate (ring_w 8, inner_w 3); a 44 px seal for secondary marks. Wash opacity .36 dry / .55 wet, front power 1.5.

## map-ink b6 additions (opt-in; engine animate_b6_886d34e0.py; old configs render identically)
* **Stamp `style:"wax"`** (defaults in `MapInk.WX`, merged as `{**SD, **WX, **q}`): an irregular wax blob with a pressure-side bulge and a height map (dome, recessed field, lip).
  * Raised **Tudor rose** (5+5 petals, sepals, centre dots), a beaded ring at .89R and an inner ring at .8R. No letters. Lambert plus Blinn specular shading.
  * Descent: scale `ghost_scale`→1 with height 1−u², blur ∝ height, a converging `shadow`, fade-in. No bounce.
  * Impact: contact shadow, press ring (`ring_press`→`ring_settle`, width `press_w`), shock ring, relief/spec flash with exponential decay (a single pulse, no strobe), drops plus `spatter` in 3 delay bins.
  * **Phone settings (seq09a v2):** R 60, drop_s .42, ghost_scale 1.3, ghost_blur 5, shadow .5 off [26,34] σ[20,3.5], wax [136,28,22] (brick red, close to the house ink), contact .32, drop_px [3.4,8], spatter 9 (px 1.2–3), drops 6.
* **Soft wash (`reach_frac`)** (defaults in `MapInk.SW`): a feathered area of influence with **no border**.
  * Geodesic reach over the land mask with `aniso=[deg,k_fwd,k_back]` (back slowdown /(1+kb·clip(−cos)²)). `reach_at` sets the point that defines reach 1.0; `reach_frac` and `feather_frac` set the extent and falloff.
  * Arrival time comes from a weighted area quantile through the coverage curve. The front is a dark crest in `wet_color`, lighter while wet and darker when dry, with granulation. "Tint" blend col·(Y/yref) keeps relief visible.
  * **p03 v2 settings:** seed [436,192], reach_at [775,822] (Ugarit), reach_frac 1.25, feather .3, aniso [70,8,2], color [150,34,112], wet [96,14,64], opacity .56 / wet .34.
  * The extent is an **approximation, not a sourced boundary**.
* **Smoke per-plume `cool`:** `{"amt":.8,"tint":[.9,.97,1.16],"base":[0,.6]}` applies a luma×tint lerp at the plume base before the blend. Use it to turn warm-lit bases grey/blue.
* **FireTorch `opaque`:** must be a truthy dict, e.g. `{"alpha":1.0}` (an empty `{}` is ignored).
  * Gives alpha = smoothstep(.03,.2)×tip ramp, a hot LUT, gamma .75 and rim .35, so solid flames have yellow-white cores and orange/red tips.

## Batch 7 (2026-10-22): soft wash `geo_thresh` (engine a88fde43)
* **`geo_thresh`** (soft wash only, opt-in; default .35 = old behaviour, old configs byte-identical): threshold for the geodesic-distance domain `Ms = resize(M) > geo_thresh`. Use .02 with a pre-feathered mask so the mask's own soft falloff defines the edge (no truncation edge, no border line). Mask value 0.5 → half-strength ("pale") wash.
* **p03 Hatti wash v3 (sourced extent) settings** (`configs/b7_map_p03_hatti_wash_v3s.json`): mask `batch7/masks/p03_hatti_extent_sourced_v3.png` (solid S + 0.5 pale west, blur σ26, × p03_land), geo_thresh .02, reach_frac 4.0, feather_frac .05, aniso [62,2,1.5], opacity .54 / wet_opacity .66 (dries lighter), front_s .18, wet_time .45, edge .7, edge_px 3.0, cov [[.2,0],[.7,.5],[1.4,.72],[2.3,.88],[3.0,.95],[3.5,1.0]], colour [150,34,112], wet [96,14,64], seed 9707.

## b9 — MapInk icon stamp + battlemap renderer (2026-10-22)
- **Icon stamp** (animate.py, opt-in `stamps[].style="icon"`; icons: sword, crossed_swords, anchor, crown, skull; `palette` overridable). Engraved 4x parts, v2 landing (drop .42 s from 1.3x, premult ghost blur 5, shadow .5, press ring .34→.07, no bounce). Old stamp configs b5/b6 re-render IDENTICAL. Engine backup: presets/locked/engine/animate_b9_b719e8d8.py.
- **battlemap.py** (new, separate renderer; backup battlemap_b9_9422cc91.py). Plate never remapped (land 0 px); overlays labels→stakes→units→arrows→volleys→marker; camera pchip keys [t,cx,cy,z] rendered 2x→INTER_AREA; units keyed [t,x,y,w,d,ang,alpha] with painterly wash/marks/banners (en_george, fr_lis, fr_pennon); stakes, volley arcs, nib arrows, period-font labels with hide_zoom.
- **Preset b9_battlemap_agincourt_poc_v1**: config generated by iterations-2026-10-22/gen_b9_battlemap_agincourt_cfg.py (edit unit keys / TW time-warp / camera there; it refuses to overwrite). Colour language: English red/white, French infantry blue, French cavalry gold, missile troops pale stipple.

---
## [SUPERSEDED 2026-10-27, owner: no IR tag] `house-ir-tag-standalone-v1` (ILLUSTRATIVE RECONSTRUCTION tag) — PROPOSAL — not owner-approved
[SUPERSEDED 2026-10-27] **Status:** PROPOSAL only; the owner has not approved it as a house default. Treat as R&D under the policy above until approved. Appended 2026-10-27 with Germanicus ROUGH v1c.
[SUPERSEDED 2026-10-27] **Reference:** `standalones/germanicus/edit/build_rough_germanicus_v1c.py`: `IR` dict, `IR_SEGS`, `IR_Y`, `ir_png(sid)` / `ir_layer()` (lines ~476–500). Render: `renders/posterity-germanicus-ROUGH-v1c.mp4`.
[SUPERSEDED 2026-10-27] * **Text:** `ILLUSTRATIVE RECONSTRUCTION`, all caps, one line.
[SUPERSEDED 2026-10-27] * **Font and size:** Source Serif Pro **Bold** (`SourceSerifPro-Bold.ttf`), **34 px** on 1080x1920; tracking **0.20 em** (6.8 px after each glyph, laid out per character); line ≈ 731 px wide.
[SUPERSEDED 2026-10-27] * **Colour/opacity:** ivory **(243,237,224)** at **0.92**. Keyline: 1 px black offset copy in ±x/±y at 0.45 × opacity. Shadows: blur 10 px α 0.60 × opacity offset (0,+3) and blur 6 px α 0.45 × opacity offset (0,+2), under the text.
[SUPERSEDED 2026-10-27] * **Scrim:** rounded rectangle padded 34 px left/right, 14 px above the text top, 12 px below the 1.2 × fs line box; radius 30, fill α **0.40**, Gaussian blur 22, colour **(14,11,9)**.
[SUPERSEDED 2026-10-27] * **Position:** centred horizontally; text-box top at **y 296 px** by default (text ≈ 296–337 px). **Per-plate override `IR_Y`:** on a plate that also carries a source credit, put the tag below the credit — Germanicus 1B uses **y 384** (credit "Tacitus, Annals 2.69" text ≈ x 343–736, y 313–353). Screen-space: it does not ride the camera push; composited with the other overlays, under burnt-in captions.
[SUPERSEDED 2026-10-27] * **Timing (30 fps):** whole on-screen duration of each tagged plate; fade in = smoothstep 10 frames after a 4-frame delay from the cut; fade out = smoothstep over the plate's last 8 frames.
[SUPERSEDED 2026-10-27] * **Which plates (Germanicus v1c, owner list):** **1B, 2, 3, 4, 6, 7A, 7B, 8, 9B**. No tag on 1A (title card), 5, 9A, 10 (inscription close-up) or the outro. General rule (proposal): tag every generated scene that depicts people, places or events as they might have looked; leave title cards, artefact/document close-ups and the outro untagged. The rule is the owner's to decide.
[SUPERSEDED 2026-10-27] * **QC:** check at 360x640 — no collision with the title, the credit or the captions; static (no motion, no displacement).
[SUPERSEDED 2026-10-27] * **To apply on a new standalone:** copy `IR`, `IR_SEGS`, `IR_Y`, `ir_png(sid)`/`ir_layer()` into the build; set `IR_SEGS` to the reconstructed-scene plates; if a plate's top band is busy or carries a credit, set an `IR_Y` override (keep y ≥ 270 px).

## 2026-10-27 — No "ILLUSTRATIVE RECONSTRUCTION" text (OWNER standing rule, via Vellum)
- **No IR text in plate prompts:** never write "ILLUSTRATIVE RECONSTRUCTION" in any plate prompt body or Flags line.
- **No on-screen IR tag overlay in any cut:** no "ILLUSTRATIVE RECONSTRUCTION" tag (or `house-ir-tag-standalone-v1`) on any plate, title, credit or outro.
- **Supersedes** the earlier IR-tag rule/proposal (`house-ir-tag-standalone-v1`, Germanicus v1c–v1f tag lists); those lines are kept and marked SUPERSEDED.

---
## torch_v1c (LOCKED 2026-10-30 by owner) — HOUSE TORCH STANDARD (torches, braziers, cressets, lanterns-as-torch, big fires)
**Owner:** "more like a pulsing effect". The Edward II v1c torch treatment, exactly as shipped, is the house torch standard. No tweak, no boost. The v3 flames work "was distorting the things around it": its strong spill and heavy sky billow are REJECTED for torch surroundings. `engine-rnd/flames/flames_v1–v3` are R&D only. Audit: `engine-rnd/flames/AUDIT_v1c_vs_v3.md`.
**Reference shipped:** `renders/posterity-edward-ii-v3b-ROUGH-v1c.mp4` (md5 b4f0aa7a68619ed5928738698f6e2eaf), slots S10 b10 cresset and S13 b13 three torches (also S08 b08, S11 p07, S16 p10).
**Source:** `standalones/edward-ii/edit/fx_v1c.py`, md5 **f31394f82a890b94d7670b009e984ce8** (do not edit; import by path). It reads the LOCK `presets/locked/house-candle-lightspill-v1.json` (md5 0591d4c770c5363f1ca6135a5d961d17) and helpers from `presets/locked/engine/animate_b3_cb9e2b88.py` (md5 cb9e2b880ab7b6940043ce3723de590a).
* **Functions:** `PlateFX(plate, seed)` → `.render(t, u)`. `blob(P, rect, "torch")` keys the flame. `mk_flick` / `flick` is the clock. `_prep_spill` precomputes the grouped spill maps. Inside `render`: plate_flame, halo, spill and embers. Per-plate `SPECS[key]` (torch / window / offscreen / relight_* / spill_amp / embers) and `PULSE[key]`.
* **Flame key (torch):** lo = (L ≥ max(140, 0.55·Lmax)) & (R ≥ 170) inside the source rect; mask = dilate 3x3 then Gaussian σ 1.6.
* **Flicker clock:** amps [0.15, 0.08, 0.035, 0.015] × **1.5** (torch, offscreen; windows 0.8 × window_amp). Freqs [0.55, 1.3, 2.6, 4.4] Hz, each × U(0.85, 1.15), random phases. Noise 0.05 at 4 Hz. f = max(0.45, 1 + Σ…). Highest component 4.4 Hz, so nothing strobes.
* **Painted flame (shape holds):** tongue = **0** for torches, and no warp or remap. g = clip(0.6·(f−1), −0.5, 0.6). Flame pixels go toward hot (255,238,190): roi + (hot−roi)·clip(g,0,1)·0.6 + roi·g·0.2 (roi·(1+g) when g < 0).
* **Glow (halo):** gauss_dot at (x, base − h/2), radius **σ = clip(0.9·h, 20, 120) px**, colour (255,165,80). Gain **0.18 × 2 × min(1, max(PULSE, 0.6)) × (f−1)**, so it is a pulse only, with no static exposure lift. Windows: σ = clip(1.6·h, 8, 40), gain 0.12.
* **Spill (falloff, reach, pulse amplitude):** reach r = 800 × 1.3 × LOCAL 0.32 × clip(h/26, 0.5, 3)^0.5 × radius_mult (≈ 330–570 px on a 941-px plate; explicit offscreen radius × 0.6). Weight = clip(h/26, 0.25, 2.5)^0.5. Up to 8 k-means groups. Per group, fall = 1 − Π(1 − clip(w,0,1)/(1 + (d/r)^2.0)) on a 1/4-res grid, light offset (0,−14). facing = 0.45 + 0.55·clip(0.65·lit + 0.35·grad). map = spill_amp (b10/b13 **1.8**, others 1.5–1.7; lock default 1.35) × fall × facing × relight-mask (relight_exclude / relight_poly, blur 14 then 6). Per frame: **dl = mean_group(f−1) × min(√n, 2.5) × PULSE[plate]**, then img *= 1 + map·dl·tint(1.0, 0.8, 0.5). The map is static and the pulse is one scalar per group, so walls and faces breathe together and no light gradient ever moves. **PULSE:** b08 .9, b10 .47, b13 .22, p07 .43, p10 .79 (candle plates .14–.76).
* **Embers:** per SPECS spawn ellipses (b10: (676,430,22,26) n 34; b13: 3 spawns n 70). Rise 25–70 px/s, life 1.2–2.6 s, drift +6 px/s, sway 2.4–8 px at 0.4–1.4 Hz, size 0.9–1.7, colour (255,170,80), twinkle 5–13 Hz, two gauss dots per ember.
* **Strength (measured at 360x640, 1 s windows, median):** walls and faces near a torch **20–46 %**, chainmail 10–29 %, whole frame **≈ 12–14 %** (3 s p-p 15–20 %), max step ≤ 3.1 %/frame, energy above 5 Hz < 1 %. It is large but coherent, which is what reads as "pulsing" rather than distortion.
* **Rules:** (1) the painted flame shape holds; (2) a soft local glow and spill pulse at v1c strength; (3) the surroundings stay visually steady, with nothing moving or warping; (4) no strong pulsing waves or moving light gradients on walls or faces (no v3 spill); (5) no tongue or displacement motion on torches (no warp, flow or parallax near them); (6) flames_v1–v3 are R&D only; (7) faces, land and water get zero warp, and the sea never moves (keep protects at 0 px).
* **To apply in a new build:** import fx_v1c by path (`importlib`, never copy-edit). Add the plate's `SPECS[key]` at runtime (torch rects, relight_exclude/relight_poly for sky, sea or other no-light zones, spill_amp 1.8, optional embers). Set `PULSE[key]` so the 360x640 whole-frame 1 s swing lands in about 10–14 % and near-torch walls in the 20–45 % band. Render `PlateFX(plate, seed).render(t, u)` **before** the camera push. For a pure-torch shot, also set `fx.par = None` and pop any candle `warp`. Verify with the impulse test (`engine-rnd/flames/scratch/v4/impulse_v4.py`: plate impulses must not leak, so 0 px displacement), a protect 0-px check, and the phone swing table. Worked example: `engine-rnd/flames/flames_v4.py` + `configs/reel_v4.json` (P05 PULSE 0.13).

### torch_v1c — scope note (owner, 2026-10-30, after the 4:31pm ET lock)
- Flames LOCKED on flames_v4 / torch_v1c for torches, cressets, braziers and all larger fires (burning buildings, town fires). Owner: "much better for the larger flames in our plates, simple and does the job."
- CANDLES keep their own treatment: the fx_candle preset (candle-sized flame shape motion, flicker, local spill) plus subtle smoke_v2 wisps, as on Edward II. torch_v1c does NOT apply to candles.
- flames_v1–v3b (tongue displacement) remain R&D only; never use them in production.

## water_v1 (LOCKED 2026-10-30 4:53pm ET by owner)
Locked for Shorts and long-form. Owner: the water is good. His one note was on shot 2 (K11): "fire looked messed up and the image was blurry". That shot is a KNOWN BAD EXAMPLE (see below).
- **Source:** `engine-rnd/water/water_v1.py` md5 `811734e9e3919bddbe3ef22022203d5f`, with README.md `bf22bab5b2c512a7b759f74aa7be9ffe`. The guarded entry point for all new work is `engine-rnd/water/water_v1_1.py` (`0afcfc06d49d2a26ce520a2314df9bfb`). It delegates unchanged to water_v1.py and calls `motion/guardrails.py` first.
- **Locked reel:** `engine-rnd/water/final/water_v1_reel.mp4` md5 `7e3d3292de7f529667d181f99194da09`, 18 s 1080x1920 30fps (moon 6 s, K11 6 s, sun 6 s). Reel config `configs/reel_v1.json` (`a154ffc8af9f5a7f8ca7d45fa288252d`).
- **Three modes (layers per shot config):**
  1. **Moon path** (`configs/nm4a_moon_path_v1b.json`, `a8c825eb…`, Nan Madol seq4a, push 1.0). A `breathe` layer on the path (amp 0.07, hz 0.12–0.27, lum 70–220, cool tint 0.9/0.97/1.05) and `glints` (≤150 fixed sites from a high-pass σ 4 / thresh 10, min_dist 8, sigma 2.0, star 0.55 / len 9, halo 0.12 σ 6, add 0.7, color 210/228/255, twinkle rates 0.35–0.9 / 0.9–2.2 Hz, thresh_t 0.45, power 1.6).
  2. **Sun glitter** (`configs/p05v2_sun_glitter_v1d.json`, `380ed751…`, Ugarit P05 v2, static 1.6x crop, center 0.97/0.30). Same layers: breathe amp 0.06, warm tint 1.0/0.95/0.85; glints ≤160, star 0.6, add 0.75, color 255/232/190.
  3. **Fire reflections** (`configs/k11_fire_reflection_v1b.json`, `06d183b6…`). `fire_reflection` columns under each fire source, driven by torch_v1c's own per-frame `fx_v1c.flick()` (same curve × pulse × gain 1.4; warm 25–80, lum 55–160, col_w 0.6, tint 1.0/0.9/0.75), plus `glints` with `clock: "fire"` (fire_k 3.0, ≤50 small sites, color 255/196/130). The fire source itself is torch_v1c (`fx_v1c.PlateFX`; fire.torch rects, spill_amp, pulse).
- **Rules:**
  - The sea never displaces: no warp, flow or offsets anywhere. Only luminance and colour change, on fixed-point glints and a slow breathe.
  - Glints are fixed sites that twinkle in place. No travelling bands, no moving light gradients, no scrolling.
  - Mattes only: `out = P + (fx − P)·keep`, then `out[protect] = P`. Faces, hands, land, boats, coastline and text are 0 changed px (protect polys, feather 3–5 px).
  - Proofs per shot: an impulse leak test (±24 on a 9-px lattice) must show 0 leaked px, and protect must show 0 changed px. Decoded phone stats: 0 px outside allow with a 1 s range ≥ 8, whole-frame swing < 8%, no energy > 5 Hz.
- **How to apply:**
  1. Copy the closest locked config to a NEW name.
  2. Draw `water` and `protect` polys in plate coords, then set the layer paths (x, x_bot, y range, w range) on the light path.
  3. For fire, list torch rects only on sharp native-res fire (see guardrails below).
  4. Run `python water_v1_1.py overlay` (check polys), then `proof` (must be 0/0), `render --size 540x960` (poc) and `stats`.
  5. Render final at 1080x1920 crf 24–26. Never overwrite outputs (writer uses `-n`).
- **KNOWN BAD EXAMPLE:** do not reuse shot 2, the K11 crop (`k11_fire_reflection_v1b`: Jianwen K11 burning city, static 2.2x crop at 1.0/0.362 with a fire-pixel-only matte). It was blurry because of 2.53 output px per plate px with a cubic upscale. The fire was blotchy because the matte clipped 91% of torch_v1c's halo and spill and pulsed only patchy keyed flame blobs. See `engine-rnd/water/K11_FIRE_DIAGNOSIS.md`. water_v1_1 refuses this config.

## Plate crop and fire guardrails (2026-10-30, applies to ALL motion presets)
- Plates are never cropped or zoomed past **~1.5x of native fill** (1.0 = plate cover-fits the frame). This covers push end zoom, static crops and reel reframes. Beyond 1.5x a 941-px-wide plate is upscaled to more than 1.7 output px per plate px and goes visibly soft on a phone.
- torch_v1c and water fire reflections run **only on sharp, native-resolution fire**. The fire rect's Laplacian variance must be ≥ 100 at native plate res (locked torches measure 134–707), and the shot zoom must be ≤ 1.5x.
- Do not clip torch_v1c to a flame-pixel-only matte on a broad painted conflagration. Either let its halo and spill run, with land protected by relight_poly, or drive only the reflection from flick() and leave the source fire untreated.
- Code: `motion/guardrails.py` provides `check_crop_zoom(zoom, max_zoom=1.5)`, `check_fire_sharpness(plate, rects, zoom)` and `check_shot(cfg, plate)`. The default is refuse; `mode="warn"` only warns. Call it from every new engine (water_v1_1, dust_v1, …).
- The one waiver is locked water_v1 shot 3 (`p05v2_sun_glitter_v1d`, 1.6x). It is waived to warn-only at exactly 1.6 so the locked output stays bit-identical. Add no new waivers; reframe instead.
- P05 1.6x exemption accepted by EIC 2026-10-30, warn-only, this shot only (`p05v2_sun_glitter_v1d`; guardrails.py matches exact name + plate path/md5 + push [1.6,1.6], crop_zoom check only).

## dust_v1 (LOCKED 2026-10-30 5:16pm ET by owner)
- Source: `engine-rnd/dust/dust_v1.py` (md5 9ea7ab68e3f64ebd25dbd3e82da6e00b), README `engine-rnd/dust/README.md`. Locked reel: `engine-rnd/dust/final/dust_v1_reel.mp4` (md5 acc858d393bcf785363a52e466aceed3) from `configs/reel_v1.json` (df68d55d1491e1555ad566b416b9a137). Reference shot configs: `t1a_tomb_shaft_v1c.json` (28769839…), `c6_citadel_ground_dust_v1b.json` (e03081ea…).
- Mode **shaft motes** (painted light shafts in dim interiors): zone matte = feathered poly (feather 50) × smoothstep(lum_lo 20, lum_hi 110) of the plate luma (blur 8) ^0.7, so motes are brightest where the painted light is. Motes n 800, sigma 0.9–3.4 px, speed 5–22 px/s along the shaft (dir [-0.22, 1], jitter 35°), turbulence 7 px at 0.07–0.3 Hz, life 5–12 s with a smooth fade, amp 200, near_gain 1.8, warm colour [255,226,180], screen blend. Haze: 6 fixed soft blobs (sigma 80) breathing at 0.05–0.14 Hz, amp 10. Camera push 1.00→1.06 allowed.
- Mode **ground-dust sheets** (sunlit dusty ground): zone matte = ground poly (feather 30) × smoothstep(40, 170). Two wind-advected noise sheets (scales 260×20 and 120×10 px, wind [26,-3] and [15,1] px/s, squash_y 2.6), alpha amp 0.36 toward [250,228,192]; plus 420 low motes, speed 12–40 px/s along the wind, life 4–9 s, amp 150. Fixed framing.
- Rules: matte-only additive/alpha dust; NOTHING displaces. Everything outside the dust zones (faces, hands, text, land/coast, lanterns, walls) is reset to the plate: 0 px changed, proved per shot (`proof`: ±24 impulse lattice leaks 0 px, protect_changed_px 0). Motes are pre-rolled 40 s, wrap only in a zero-matte margin and fade in/out (no loop, no pop). Haze is fixed-position (no moving light gradients). The guardrail is refuse at >1.5x (`motion/guardrails.py`, called by render/reel). Phone check (`stats`): whole-frame 1 s swing < 8%, low energy above 5 Hz.
- Apply: copy the closest reference config to a NEW file, set plate, zone poly (light shaft or ground only), protect polys (people, lanterns, text), and lum_lo/hi to the shaft's brightness; then `grab` (phone before|after|diff), `proof`, `stats`, a 540x960 `render` PoC, and `reel`. Best on a DARK interior with a painted beam; motes over bright, busy stone barely read on a phone (t6 oculus was the weak case).
- **Size-density fix (2026-10-30, EIC-approved):** `guard()` now passes the actual output size to `check_shot` (`out_wh=out_size(cfg, size)`): `render` uses its `--size`, `reel` uses the reel's `size`. Before, it always checked at 1080x1920, so a `--size 1920x1080` render of a 941x1672 plate slipped past the density check. Only the guard calls changed (3 lines); visual math untouched. New source md5 **c0ad4ef55357ddd47ca73b9a93ffc760** (was 9ea7ab68e3f64ebd25dbd3e82da6e00b, backup `engine-rnd/dust/superseded/dust_v1.py.pre-size-density-2026-10-30`). Proof: both locked reels re-rendered with the new file are BYTE-IDENTICAL by md5 (reel_v1 → acc858d393bcf785363a52e466aceed3, reel_ref_v1 → 74744cd11f6c37452e9568081f3179e1, matching `final/dust_v1_reel.mp4` and `final/dust_v1_ref_reel.mp4`). Tests on `t1a_tomb_shaft_v1c` (941x1672, push 1.06): `--size 1920x1080` REFUSES (2.163 > 1.5; a reel at 1920x1080 refuses too), `--size 1080x1920` renders (1.217). Record: `engine-rnd/dust/proofs/size_fix/PROOF_size_fix_2026-10-30.md`.

## depth_v1 (LOCKED 2026-10-30 6:16pm ET by owner)
- Source: `engine-rnd/depth/depth_v1.py` (md5 **dd5cd5011c88b3b56528b96fedae5494**), README `engine-rnd/depth/README.md` (6c54fd2e…), model eval `engine-rnd/depth/DEPTH_MODEL_EVAL.md` (8f4bc96d…). Locked reels: `engine-rnd/depth/final/depth_v1_reel_9x16.mp4` (md5 **629db9a3bb6d1f9b525a49d8913f81a1**; `configs/reel_9x16.json`: b05, b10, b01, p10, 6 s each, 1080x1920, crf 25) and `engine-rnd/depth/final/depth_v1_reel_16x9.mp4` (md5 **d1953b4ad47f2f4e9794f76b105552bf**; `configs/reel_16x9_native.json`: Hubert Robert fire arch only, 1920x1080).
- Method: **two rigid premultiplied layers** (far, then near). Each layer gets **one uniform transform per frame** (cover-fit × shared overscan × layer zoom about the anchor, plus a layer shift) that folds in the 1.00→1.06 push and the drift. There is **no global push** on top. Effects (dust, water, smoke, fx candle/torch) compose **inside the layer matrix** as `plate_fx`: the effect's plate-space delta is split across layers by exclusive coverage and rides each layer's single warp. The effect's own camera is **never called**. Proof: `WARP_LOG` holds exactly layers × frames warps, max 1 per (frame, layer); the compose test traps `dust.F3.push_frame` (0 calls).
- Matte workflow (`matte.mode: "hybrid"`): a Depth Anything V2 **Small** threshold (`depth_min` / `depth_max`), then hand fixes per layer (`region`, `polys`, `exclude`, `seams`, `protect`), then a guided filter (`guided_r`, `guided_eps`). Model: `engine-rnd/depth/models/da2_small.onnx` (onnx-community DA2 Small fp32, Apache-2.0, ~99 MB). Cache: `engine-rnd/depth/cache/da2s_<plate md5>.npy` (float16, ~3 MB per plate; 5.9 MB for the larger Hubert plate). Inference takes ~0.9 s and the build ~4 s. Setup is **~3 min per plate** (vs ~15 min for pure hand polys; see DEPTH_MODEL_EVAL.md).
- Fill: revealed areas are **pre-filled** (inpaint + grain, `reveal_px`). The motion uses a **0.5 s ease in and out** (`smooth_progress`, ramp 0.5/0.5). This **stays for now**; the owner may want it snappier later (it is a config value, `camera.ease`).
- Guardrails: the pixel-density rule applies (≤ 1.5 output px per real source px), measured per layer at the larger layer scale (zoom × overscan × crop). 16:9 needs **native landscape plates ≥ ~1357x763**, never upscaled (portrait band crops need ≥ 1380x2451). The 941x1672 Edward plates are refused at 16:9 (intended); `nero_balcony_push_v1` (1280x720) is refused at both sizes. Reel densities: b05 1.237, b10 1.244, b01 1.286, p10 1.237 (9:16); Hubert 1.100 (16:9).
- Rigidity rule: **faces, hands and letters must sit wholly inside one layer** (`protect` boxes; proof needs in_layer ≥ 0.97 and NCC ≥ 0.9999). They move only rigidly and are never warped or split by a seam.
- Weak spots: revealed strips (10–18 px) read slightly smeared (hf texture ratio 0.49–0.86). Seam floors (b01, b10) go soft at max offset. On a phone the move lands at ~1–2 s because of the ease-in. Relative parallax is 3.2–4.1 % of width.
- **When to use depth (owner rule 2026-10-30):**
  - **Primary test: motion or action.** Use depth on plates whose scene moves: arrivals, landings, escapes, processions, crowds, journeys.
  - **Quiet portrait, dialogue and still character plates stay flat.** They use the other locked effects: candle (fx_candle flicker + spill), smoke_v2, dust_v1, torch_v1c, water_v1.
  - **Secondary guard: never use depth on back-to-back character plates.**
  - The old "about 1 in 3 shots" figure is only a **loose ceiling**, not a target. The motion/action test decides.
  - In `build_template_v1.py`, depth is **opt-in per shot and OFF by default**. Planning WARNs (does not refuse) on two consecutive depth shots where either is a character plate. It also asks for a `scene_action` / `depth_ok_reason` note on every depth shot.
- **Owner calibration example (when to use depth).** The locked 9:16 reel is the reference for deciding which shots get depth:
  - **b05 landing** → WOULD get depth.
  - **b10 Corfe letter** → WOULD get depth.
  - **p10 escape** → WOULD get depth.
  - **b01 Gloucester funeral** → would **STAY FLAT** and get the **candle treatment**: fx_candle flicker + spill plus smoke_v2 wisps. b01 is in the demo reel **only as a technical showcase**, not as a model for real cuts.
- Apply: copy the closest reference config (`b05_landing_push_v1`, `p10_escape_drift_v1`, `b10_corfe_letter_drift_v1`, or `hubert_fire_arch_push_v1` for 16:9) to a NEW file. Set the plate, then tune `depth_min` and the hand fixes until `layers` (sheet) looks clean and every face, hand and letter is inside one layer. Then run `proof` (single transform, rigidity, disocclusion), `stats` (phone jitter), and a small `render`. In a template build, put `"depth": "<config>.json"` (or inline mattes/layers) on that shot only (see `motion/templates/README_build_template.md`).

## Stacking: depth_v1 + torch_v1c + smoke_v2 (LOCKED 2026-10-30 7:11pm ET by owner: "THIS CAME OUT SO FREAKING WELL")
- Reference: `engine-rnd/hero/final/b10_corfe_fullstack_v1_restrained.mp4` (md5 3ae1ae4d60b43f86e062cc8c44632a3f), Edward II b10 Corfe handover, 7s, 9:16. Code: `engine-rnd/hero/fullstack_v1.py` + README.
- depth_v1 provides the ONLY camera (one uniform transform per layer per frame). torch_v1c composes as `plate_fx` inside the layer matrix; smoke_v2 plumes ride the layer they rise from (here the near arch layer) using that layer's single warp; smoke_v2's own camera is never called (0 calls).
- smoke_v2 from small wall torches: alpha x0.4 (about 0.4 opacity) when stacked with torch_v1c and depth_v1. Full strength (~0.86 base, near-black) reads as soot on the flame tip and eats the torchlight.
- Faces are kept OUT of the torch flicker: torch delta zeroed on face masks, padded 6px, feathered 18px. Faces then change 0.0 levels in plate space; the effects add 0 px on faces beyond depth alone.
- Proofs in that reference: density 1.22, 0 holes, torch impulse leak 0px, energy above 5Hz with all on = torch only (no stacked pumping), local excess at most 0.27 pts.
- No dust_v1 on b10 (owner). No body motion (body motion waits for its own roadmap stage).

## Pixel density guardrail (EIC ruling 2026-10-30, applies to ALL motion presets, long-form 16:9 AND Shorts 9:16)
- Refuse any shot that puts more than **1.5 output px on one real source px**. `ratio = max over the push/zoom range, max over both axes, of output dimension / visible source-crop dimension` = cover-fit scale × peak push × crop zoom, measured on the **actual plate file size** (never the nominal / manifest size). A push 1.00→1.06 uses 1.06.
- Why: `check_crop_zoom` measures zoom relative to cover-fit, so a 941x1672 portrait plate cover-fit into 1920x1080 passed at 1.00x even though it is **2.04** px/px (2.16 at push 1.06). That plate is fine for Shorts (1.148 static, 1.217 at 1.06) but not for long-form.
- Reference numbers: 941x1672 → 1920x1080 = 2.040 (refuse); 2560x1440 → 1920x1080 @1.06 = 0.795 (pass); 1080x1920 → 1080x1920 @1.06 = 1.060 (pass); 640x1138 → 1080x1920 @1.06 = 1.789 (refuse). For long-form at push 1.06 a 16:9 plate needs ≥ 1357x763 (house target 2560x1440).
- Code: `motion/guardrails.py::check_pixel_density(plate_path | array | (w,h), out_wh, push_range, max_ratio=1.5, mode="refuse", crop_zoom=1.0)` returns `ratio, ratio_x, ratio_y, pass, msg` (msg names the plate and numbers). It runs inside `check_shot` (water_v1_1, dust_v1) and inside `check_crop_zoom` whenever `plate_wh` is given (depth_v1). `build_template_v1.py` runs it per shot at planning and lists every offending shot before rendering. Default is refuse (raise / non-zero exit); the guardrails CLI now refuses by default too (`--warn-only` for a report).
- P05 exemption (exact shot only): `p05v2_sun_glitter_v1d` measures **1.600** (1080x1920 OWNER plate, static 1.6x, 1080x1920 Short). The existing tightly-scoped waiver (exact name + plate path + md5 41025b96 + push [1.6,1.6], no crop_zoom, no fire) is extended to density as **warn-only**, additionally requiring output exactly 1080x1920 and measured density 1.6. EIC-accepted for that shot only. The same shot at 1920x1080, under another name or plate copy, or in build_template_v1 (no waiver path) is refused. Add no new waivers; regenerate a higher-res / native-aspect plate instead.
- Known gaps (locked files, not edited): (`dust_v1.guard()` used to check at 1080x1920 regardless of `--size`; FIXED 2026-10-30, see the dust_v1 entry) `depth_v1` now refuses its 16:9 renders of the 941x1672 Edward plates (2.20–2.29) and `nero_balcony_push_v1` (1280x720) at both sizes.
