# Motion iterations, 2026-10-22: element-motion engine, batch 1

**Brief:** this follows the owner's final brief for the day. It is an R&D day with no hard rules: water is allowed, effects can be bold, and the scope is maps and environments only, with no figures. Warping is measured and reported, but it does not gate a clip. The end goal is a reusable, stable, seeded preset system.
**Engine and code:** everything is in `motion/iterations-2026-10-22/`:
* `animate.py` is the single CLI.
* `make_masks_batch1.py` builds masks from thresholds plus polygons.
* `qc_layers.py` reports per-layer displacement.
* `qc_isolation.py` checks each layer alone against its own mask.
* `qc_overlay.py` makes a readable mask-overlay still.
* `configs/*.json` holds the per-plate configs.

Presets are documented in `motion/PRESETS.md`.
**Clip format:** 8.0 s, 240 frames, 720x1280, 30 fps, H.264 yuv420p, no audio. BEFORE (0–4 s) is the plate with the standard 100→104 % centre zoom only. AFTER (4–8 s) uses the identical zoom, restarted, plus the preset layers. Each half carries a 'BEFORE' or 'AFTER' corner label and a one-line note.
**Determinism:** every final clip was rendered twice with `--repeat-check`, and the MP4 md5 and raw-frame SHA-256 matched both times. Map and light were rendered a third time after the last code edit (the foliage bound) and matched again (c63bbe60… / 1fb0d7e9…).
**Existing files:** none deleted, moved or overwritten. Everything new is under `motion/iterations-2026-10-22/`, plus this log and `motion/PRESETS.md`. Previews went to `/tmp/pv`, outside the project. The total new footprint is about 175 MB.

## QC columns, explained
* **out-of-mask (union):** plate-space and output-space max |AFTER−BEFORE| outside the union of all layer masks.
* **isolation:** each layer rendered alone, with its max diff outside that layer's own mask. This is the meaningful check when a layer covers the full frame.
* **disp:** max displacement of plate pixels: overall, per layer, and inside the protect mask.

---

## Clip 1 — MAP: `batch1/b1_map_seq09a_roanoke_croatoan_final.mp4`
* **md5:** c63bbe60bb50accd94b8e3b2e05127ab
* **Duration:** 8.000 s
* **Config:** `configs/b1_map_seq09a.json` (seed 9091)
* **Plate:** `serials/croatoan/ch2/plates/seq09a_map_roanoke_croatoan_UNLABELED_OWNER.png`, 941x1672.
* **Element types and presets:**
  * **map-light**, mask `seq09a_full`:
    * parchment light sweep: strength .07, 32°
    * cloud shadows: strength .21, lo 440, hi 120, beta 3, coverage .36, velocity [26, 9] px/s
    * oxblood ink route: Catmull-Rom from Roanoke Island (520,322) down Pamlico Sound to the Croatoan cape (686,1398); draws over 0.35–3.1 s; width 4.6, dash 18/9, halo .4, glowing head
    * markers: Roanoke glows from t=0; Croatoan ignites with a flash and ring at 3.1 s, when the line arrives
  * **water**, mask `seq09a_sea`: amp 0.9 px, speed 10, stretch 3.5, shimmer .05, no glints. The protect mask is `seq09a_protect_land_coast` (land + ink coastline dilated by 3 px, plus the ship box).
* **Method:** displacement only on the sea, tapered to 0 px a margin away from the coast. Everything else is luminance or overlay.
* **QC:**
  * Out-of-mask (union) is 0 / 0, but trivially so, because the union covers 100 % of the frame.
  * Isolation: water 0, map-light 0.
  * Displacement: max 0.98 px (sea), and **0 px on land, coastline and ship**, so the coast geometry stays pixel-static.
  * Changed pixels (|Δ|>2): mean 84 %, mostly from the full-frame light. Mean |Δ| 8.9/255.
  * Render time 41 s.
* **Note (on clip):** "Map-light: route draws Roanoke to Croatoan, cloud shadows, sea shimmer; coast static"
* **QC stills:**
  * `batch1/qc/b1_map_seq09a_roanoke_croatoan_final_mask_overlay_readable.png` (also `_mask_overlay.png`)
  * `..._after_mid.png`, `..._after_mid_platefull.png`, `..._diff_heat_mid.png`
  * `.qc.json`, `.layers.json`, `.isolation.json`
* **Improvement over `ugarit_fire_v2.py`:** fire_v2 could only modulate fire pixels on one plate type, and its SPECS were hard-coded in Python. This clip adds a narrative map device: a timed, eased ink route that ends on a marker ignition, so the motion carries information. Light passes over the land without moving a single coastline pixel. It all runs from a JSON config with an automatic protect-zone displacement check.
* **Iteration history:**
  * v1 `batch1/b1_map_seq09a_roanoke_croatoan.mp4` (md5 eb6c70d4ce1bbfacc3d16c43c0bf67c5) was superseded and kept as a record. Its cloud shadows were too high-frequency and blotchy ("camouflage", hi 40, beta 2), its route was too thin to read at 720p (3.2 px, no halo), its markers were weak, and its sea displacement was unbounded (peak 4.3 px).
  * The fixes were softer, larger shadows (hi 120, beta 3), route width 4.6 with a warm halo, bigger markers, and tanh-bounded water displacement.

## Clip 2 — ENVIRONMENT (water allowed): `batch1/b1_env_p07_ugarit_coast_final_v2.mp4`
* **md5:** 02d0742133b1c24c00639568b6cdfa9c
* **Duration:** 8.000 s
* **Config:** `configs/b1_env_p07.json` (seed 7071)
* **Plate:** `micro-anomaly/ugarit/plates/p07_abandoned_match02_OWNER.png`
* **Element types and presets:**
  * **sky**, cloud drift: velocity 9 px/s, parallax .9, billow .8 px, skyline taper 10 px
  * **water**: amp 1.4 px, speed 16, stretch 4, shimmer .08, sun glints 1.2 (threshold 2.7, favouring bright water)
  * **foliage**: amp 1.2 px, gusts 110 px/s with a 460 px wavelength, sway .6 Hz, flutter .4, dapple .06
  * **map-light**: cloud shadows only, on the land mask; strength .2, velocity [34, 12] px/s
* **Protect mask:** `p07_protect_stone` (walls, paths, ground and stone that are not foliage).
* **QC:**
  * Out-of-mask (union) 0 / 0, again trivially, since the union covers the full frame.
  * Isolation: sky 0, water 0, foliage 0, map-light 0.
  * **Displacement:**
    * sky drift: max 48.2 px. This is a deliberate translation of the cloud content at the top of frame by 4 s, not a warp.
    * water: 1.52 px.
    * foliage: 1.49 px (tanh-bounded).
    * inside the stone/wall protect mask: 0 px.
  * Changed pixels mean 52 %. Mean |Δ| 8.1. Render time 40 s.
* **Note (on clip):** "Sky drift + sea ripple & sun glints + foliage sway in gusts + cloud shadows on land"
* **QC stills:** `batch1/qc/b1_env_p07_ugarit_coast_final_v2_mask_overlay_readable.png`, `..._after_mid.png`, `..._diff_heat_mid.png`, plus the json files.
* **Improvement over fire_v2:** fire_v2 had one element class (fire, smoke and embers) and used zero motion of plate structure. This clip combines four coordinated, physically plausible systems:
  * The sky drifts with parallax.
  * The sea gets ripple and glints.
  * Foliage moves in travelling gust fronts, so neighbouring bushes sway together, not as independent jelly.
  * Cloud shadows cross the land.

  Every displacement is bounded and tapered, and measured at 0 px on stone.
* **Honest caveats:**
  1. The sky drift has no off-plate sky to draw on, so the trailing (left) edge strip is filled with a mirror of the adjacent cloud. That is up to about 48 plate px (about 37 output px) at the top-left by the end of AFTER.
  2. At foliage edges, the up-to-1.5 px displacement can drag in a pixel of neighbouring wall or ground. That is a small warp, and isolation shows it stays inside the foliage mask dilated by 2·amp.
  3. The clip is 21 MB at crf 17, because the glinting sea is high-entropy.
* **Iteration history:**
  * Preview v1 was rejected: the anisotropy was inverted, so the sea showed vertical streaks, and the glints were too dense and noisy.
  * `batch1/b1_env_p07_ugarit_coast_final.mp4` (md5 755ece930397b65293067b239e3f7efc; rerun identical) was superseded and kept. Its foliage flutter was unbounded, peaking at 4.0 px. v2 bounds it with tanh to 1.49 px.

## Clip 3 — LIGHTING / ATMOSPHERE SHOWPIECE: `batch1/b1_light_p06_ugarit_burning_dusk_final.mp4`
* **md5:** 1fb0d7e9661658313918aa42740d21d5
* **Duration:** 8.000 s
* **Config:** `configs/b1_light_p06.json` (seed 6061)
* **Plate:** `micro-anomaly/ugarit/plates/p06_burnt_city_doorway_OWNER.png` (burnt city seen through a charred doorway).
* **Element types and presets:**
  * **smoke**: 4 advected plumes rising from the existing painted plume bases, widening (w1 60–120 px), meandering and boiling, rise 18–26 px/s, clipped to the doorway opening. Plus 170 ash flakes falling in front of everything, with wind and sway.
  * **atmos**:
    * drifting haze sheets through the distant ruins (band y 600–860)
    * soft crepuscular rays screen-blended from off-frame top-right (900,110): strength .16, n_scale 55, no visible star point
  * **light-shift**: day→dusk between 0.3 and 3.6 s; gain [1.05,.82,.66], ev −0.5, extra sky warmth, low sun/fire glow at (720,560).
  * **fire-torchlight**:
    * 3 small flickering fires at the plume bases, each throwing light onto the nearby ruins
    * smoulder hotspots on the char mask (8 % coverage, breathing and bloom, lighting the surrounding ground)
    * 80 embers rising from 4 spawn zones

  Because fire is emitted after the grade, the glow takes over as the light falls. The protect mask is `p06_protect_frame` (the doorway frame).
* **QC:**
  * Out-of-mask (union) 0 / 0, trivially (light-shift, ash and embers are full-frame).
  * Isolation: smoke 0, atmos 0, light-shift 0, fire-torchlight 0.
  * **Displacement: 0 px everywhere.** No pixel is ever moved; everything is light or overlay.
  * Changed pixels mean 84 % (max 99.9 % once dusk is fully in). Mean |Δ| 22.9, which is high by design: it is a grade.
  * Render time 85 s.
* **Note (on clip):** "Day-to-dusk shift, smoke columns + light rays, smoulder glow, embers and ash"
* **QC stills:** `batch1/qc/b1_light_p06_ugarit_burning_dusk_final_mask_overlay_readable.png`, `..._after_mid.png`, `..._diff_heat_mid.png`, plus the json files.
* **Improvement over fire_v2:**
  * fire_v2 only re-lit fire pixels that already existed and boiled smoke in place, on one hard-coded plate.
  * This clip changes the lighting of the whole scene over time (day to dusk), adds new volumetric-looking smoke columns that actually rise and widen, and adds light rays.
  * Fire light is thrown onto surrounding surfaces through their own albedo, so stone warms and char stays black.
  * Foreground ash and embers sit in front of the doorway for real depth.
  * It still uses zero displacement, and the result is seeded and byte-reproducible.
* **Iteration history:**
  * Preview v1 was rejected: the rays were thin hard laser lines (6x angular multiplier), the sky was over-saturated flat orange, and there were too many hotspots, so the rubble read as lava.
  * Preview v3 was rejected: the rays formed a visible starburst, with the origin inside the frame.
  * Preview v4 became the final: origin off-frame, near-fade, broader shafts, sky_gain toned to [1.1,.86,.74], hotspots at 8 % coverage, and smoke opacity raised 1.35x.

---

## Open issues and next steps (batch 2)
* **fire-torchlight** has not yet been shown in its classic form, a candle or torch on interior walls. Candidate: a day19/rome69 torchlit interior.
* **sky** drift needs an edge strategy for long holds: cap the speed at about 4 px/s, or pre-extend the sky.
* **Speed:** about 40–85 s per 8 s clip on 4 threads, fine for R&D. Bounding-box optimisation and caching static layers would roughly halve it.
* The union-mask stability number is vacuous whenever a full-frame preset is present. Read the isolation numbers instead, or add an optional `static_regions` mask that must stay bit-exact.
* Not yet reviewed by Vellum or the owner. All three clips are REVIEW_REQUIRED.

---

# Batch 2 (afternoon): editorial notes on batch 1, plus the light-spill exception

**Order:** (1) the candle light-spill clip (new; a figure is allowed here as pure relighting), (2) P06 burning dusk v2 (real flames), (3) the Croatoan map v2 (ink nib). P07 was skipped, as instructed.
**Code:** `animate.py` gained the fire-torchlight blocks `light_spill`, `plate_flame`, `halo`, configurable `flicker`, `flame_tongues`, `shimmer` and `sparks`, and the map-light nib `route` and `ink` markers. New scripts:
* `make_masks_batch2.py` → `batch2/masks/`
* `qc_spill_sync.py`

Configs: `configs/b2_candle_seq14.json`, `configs/b2_light_p06_v2.json`, `configs/b2_map_seq09a_solid.json`, `configs/b2_map_seq09a_dashed.json`.
**Regression:** the batch-1 map and light configs and the candle config were re-rendered with the final engine. All reproduce their original md5s. Batch-1 files are untouched.
**Determinism:** every batch-2 clip was rendered twice with `--repeat-check`. The MP4 md5 and frame SHA-256 are identical; reruns are in `batch2/determinism/`.
**Footprint:** the iterations folder is now about 266 MB in total. Nothing existing was deleted, moved or overwritten.

## B2-1 — CANDLE LIGHT-SPILL: `batch2/b2_candle_seq14_lightspill_v1.mp4`
* **md5:** 2962e4acba43d411d443adfd35728159
* **Format:** 8.0 s, 240 frames, 720x1280, 30 fps, H.264, no audio
* **Plate:** `serials/croatoan/ch2/plates/seq14_white_ireland_letter_candle_OWNER.png`
* **Preset:** fire-torchlight, layer mask `batch2/masks/seq14_relight.png` (the whole room minus the night window).
  * **Source:** candle at (59,1001); procedural flame gain .22; halo σ20, gain .07.
  * **Flicker** (shared by everything): amps [.09,.05,.025,.01] at [0.8,1.9,3.7,7.9] Hz, noise .06 @ 7 Hz, floor .6, smooth.
  * **plate_flame:** the painted flame pixels (`seq14_flame.png`) breathe with gain .6, tongue .25, rise 70.
  * **light_spill:** radius 450, power 2, amp 1.0, tint [1,.84,.58], optical centre offset [0,−14], facing floor .3, warm .65, grad .35.
* **QC:**
  * **Displacement 0.0 px everywhere** (protect = full frame).
  * Union out-of-mask: 0 / 0. Isolation diff outside the relight mask: 0. The window changes by ≤ 0.01 %, only in the feathered edge band.
  * Changed pixels mean 9.3 %; mean |Δ| 0.92.
  * Spill sync (`qc/b2_candle_seq14.spill_sync.json`), all correlating 0.965–0.968 with the flame's own brightness:

    | region | swing | std | max per-frame step |
    |---|---|---|---|
    | face | −5.2…+3.8 % | 2.0 % | 2.8 % |
    | left hand | −12.6…+8.4 % | 4.7 % | 6.6 % |
    | right hand | −5.0…+3.6 % | – | – |
    | paper | −6.7…+4.8 % | – | – |
    | far wall | ±1.8 % | – | – |
* **Note (on clip):** "Light-spill: candle flicker relights face, hands, paper and room in sync with the flame"
* **Stills:** `batch2/qc/b2_candle_seq14_lightspill_v1_after_mid.png` (mid-frame), `_mask_overlay_readable.png`, `_diff_heat_mid.png`, `_after_mid_platefull.png`.
* **Iteration:**
  * The first preview had amp .62 / radius 380, so the face swung only about ±2.4 % (too subtle).
  * The final raised this to amp 1.0 / radius 450 and softened the 3.7 and 7.9 Hz bands, reducing per-frame steps.

## B2-2 — P06 BURNING DUSK v2: `batch2/b2_light_p06_ugarit_burning_dusk_flames_v2.mp4`
* **md5:** 759ccaa16690f6a51bbf18518c816c04
* **Duration:** 8.0 s
* **Changes vs batch 1** (dusk grade, rays, haze, embers and ash kept):
  * **flame_tongues:** 9 fire beds.
    * 4 on the skyline at the painted plume bases: heights 14–30 px, thickness 3–4.
    * 5 on charred timbers in the street: heights 55–85 px, thickness 7–8.
    * Settings: rise 95, sway 5, tongue_lo 24, tongue_hi 6, sharp 1.5, body .8, clump .9, cover .6, bloom .3, light .38 at radius 110.
    * Per-bed flicker curves drive both the flame height and the firelight thrown on the stone.
  * **shimmer:** amp 1.2 px, band .45–2.4 × flame height. It is applied to the plate ONLY on `p06_sky_strict_v2` (the batch-1 sky minus every skyline silhouette and spire, and nothing below y 586), eroded 3 px. Over ground fires it refracts only the flame layer.
  * **sparks:** 260, rising 90–230 px/s, life .35–1 s, gravity 60, turbulence 25.
  * **Smoulder hotspots:** cut from 8 % to 5 % coverage and from gain .5 to .35. They are now ember beds under the flames, no longer the "static orange patches".
  * **Smoke:** 4 extra thin plumes rising from the ground fires.
  * The batch-1 teardrop sources were removed (replaced by the skyline beds).
* **QC:**
  * Union out-of-mask 0 / 0.
  * Isolation: smoke 0, atmos 0, light-shift 0, fire-torchlight 0.
  * **Displacement:** max 1.40 px (heat shimmer, in the sky at about x 799, y 573). **0.0 px on every non-sky pixel** (`batch2/masks/p06_protect_nonsky_v2.png`: stone, walls, rubble, frame).
  * Changed pixels mean 87 %; mean |Δ| 29.6 (a grade plus fire, by design). Render time 125 s.
* **Note (on clip):** "v2: licking flames + sparks, heat shimmer in sky only, firelight on stone; dusk, smoke, rays"
* **Stills:** `batch2/qc/b2_light_p06_ugarit_burning_dusk_flames_v2_after_mid.png` (mid-frame), `_mask_overlay_readable.png`, `_diff_heat_mid.png`.
* **Iteration:**
  * Preview a was rejected: the flames read as a uniform fuzzy "flame grass" strip, with no distinct tongues, and the firelight washed the whole street yellow.
  * The final has per-column tongue peaks (vertical-elongated texture, sharpened), stronger clumping (gaps along the beds), smoother tongue texture, bloom .3, and light .38.
* **Honest view:** a clear step up from 7.5. The flames now lick, split and rise, sparks fly, and stone takes flickering light. However:
  1. The street flames still read as long, thin ribbons along the timbers, not big volumes. At 720p the 55–85 px beds are modest, so "a city being consumed" is only partly there.
  2. A few isolated tall thin tongues look like wisps.
  3. The shimmer is real but subtle, since it is limited to small sky areas above the skyline fires.

  **Next (v3):** taller, wider beds (×1.5–2) on the two or three biggest timbers; volumetric flame bodies (a second, lower, wider tongue octave); dark soot at the tongue tips. **Estimate: about 8/10 now.**

## B2-3 — CROATOAN MAP v2 (ink nib), rendered both ways
* **Solid:** `batch2/b2_map_seq09a_inknib_solid_v2.mp4`, md5 00620860b44a585ea0940106bd6b2c5a, 8.0 s
* **Dashed:** `batch2/b2_map_seq09a_inknib_dashed_v2.mp4`, md5 6b2d06d34a3f47f460bda18fb68807c0, 8.0 s
* **Changes vs batch 1:**
  * The glowing route head and the marker glow, ring and bloom are **removed**.
  * The route is a hand-inked nib: width 2.7 ±22 % (variation over ~70 px), a pressure ramp at the start, and a wet ink bead at the tip.
  * Ink age per pixel: wet [40,8,8] at opacity .97, drying over 0.8 s to iron-gall/oxblood brown [128,56,40] at opacity .85.
  * Fibre feathering .45 (1.4 px), wicking in over 1.2 s; paper-tooth density; pigment mix .5.
  * Dashed version: 13/7 px with ±25 % hand jitter.
  * Markers are inked circles drawn as a pen stroke (Roanoke at 0–0.18 s; Croatoan at 1.85–2.0 s), each with a centre dot.
  * **The endpoint moved onto the Croatoan cape**, on land: (668,1405), inside the wooded cape at the barrier-island elbow. The path now runs (704,1300) → (690,1365) → (668,1405), down the sound side of the banks and onto the cape's north shore.
  * The route draws over 0.2–1.85 s, so the mid-frame still (t = 2.0 s into AFTER) shows the completed route and the Croatoan circle. **Verified on both mid stills.**
  * Cloud shadows, parchment light, sea shimmer and a static coast are unchanged.
* **QC (both):**
  * Union out-of-mask 0 / 0. Isolation: water 0, map-light 0.
  * Displacement max 0.98 px (sea only); **0 px on land, coast and ship**.
  * Changed pixels mean 84 %; mean |Δ| 8.7–8.75.
* **Note (on clip):** "v2: hand-inked nib route Roanoke to Croatoan cape, ink drying; cloud shadows, coast static"
* **Mid stills:** `batch2/qc/b2_map_seq09a_inknib_dashed_v2_after_mid.png`, `batch2/qc/b2_map_seq09a_inknib_solid_v2_after_mid.png`, plus `_mask_overlay_readable.png` for each.
* **Preference: dashed.** It reads as a voyage track in the chart convention of the period (dotted or pecked tracks), and its hand-jittered dashes sell the nib better. The solid line reads more like a modern annotation.
* **Honest view:** this fixes the lens-flare problem and reads as ink. The weak point is that the line is thin at 720p on a phone, and over the blue sea the wet-to-dry tone shift is subtle; it is clearly visible only where the line crosses land. If editorial wants it bolder, try width 3.2 and dry_color a touch redder.

---
# BATCH 3 — 2026-10-22 (after editorial HELD batch 2: "doesn't read on a phone")
**Order (per steering):** candle v2 → map v3 → P06 v3 → water-glint (parked, finished last).
**Every clip is judged at phone size:** the mid-frame stills are downscaled to 360x640 (`*_after_mid_phone360.png`).
All clips are 8.0 s, 720x1280, 30 fps, H.264, no audio, with BEFORE/AFTER halves each using the 100→104 % centre zoom.
Every clip passed `--repeat-check` (md5 and frames_sha256 identical on rerun; reruns are in `batch3/determinism/`).

**New QC tool, `qc_layermask.py`:** a strict check of each layer's change outside its *declared mask PNG*, at t = 0.5/1.3/2.0/2.7/3.5 s.
It was added because the older allow-region isolation QC missed a flame leak in P06 v3 (see B3-3).

## B3-1 — CANDLE v2: `batch3/b3_candle_seq14_lightspill_v2.mp4`
* **md5** 030cbcbb8bbb5977066975a5c7f5b9e7. Config `configs/b3_candle_seq14_v2.json`, seed 1415.
* **New:** `flame_warp`, which sways and stretches the painted flame inside the flame mask only (zone 6 px).
  The flame brightness pulses. `light_pool` adds a dark falloff that breathes with the same flicker curve (dark .22, breathe .7).
  Spill amp is 1.35 with a warm amber tint. A 4-sine flicker gives the pool a slow breath with no strobe.
* **Swing** (/255 and %):

  | Region | Base | Swing | Half-swing |
  |---|---|---|---|
  | Face | 67.0 | −17.4/+9.5 (−26.0/+14.2 %) | 21.3 % |
  | Near hand | 86.8 | ±23 (−26.3/+26.7 %) | 26.5 % |
  | Paper | 113.1 | −28.9/+15.8 (−25.6/+13.9 %) | 21.0 % |
  | Whole frame | 31.0 | −6.9/+3.85 (−22.3/+12.4 %) | 18.3 % |

  Far hand −24.9/+11.2 %; flame −24.9/+32.5 %.
  Peak-to-peak on the face within the first 1 s is 31 %. Max step is 3.4–5.1 %/frame in the regions (flame 8.35 %), so there is no strobing.
  Each region correlates with the flame at 0.96–0.97.
* **QC:**
  * Isolation 0 outside the mask; layermask 0.
  * disp_max 4.32 px (flame zone only); **displacement on face, hands and paper is 0 px** (disp_protect 0).
* **Not done:** the optional quill shadow was skipped.
  The near-hand swing is about 26 %, slightly above the 20–25 % target.
* **Stills:** `batch3/qc/b3_candle_seq14_lightspill_v2_after_mid_phone360.png`, `…_phone360_plate_dim_bright.jpg`, `…_mask_overlay_readable.png`.
* **Verdict:** SHOW. The pool visibly breathes on a phone, with no strobing.

## B3-2 — MAP v3: `batch3/b3_map_seq09a_inknib_dashed_v3.mp4`
* **md5** b8aa9ceb7cae2757a44d9919eb8ddd9f. Config `configs/b3_map_seq09a_dashed_v3.json`, seed 9093.
* **Stroke:** width 2.7→7.2 (2.7x), dash 24/11, in a redder iron-gall ink (wet [62,10,6], dry [142,46,26]).
* **Nib bead (.85):** wobbles 1.2 px at 5 Hz with pressure (`speed_var` .45) and stays visible in dash gaps (`tip_always`).
* **Wet sheen and bloom:** a wet sheen (.4) dries over 0.9 s. Each dash blooms as it is laid (.55).
* **Markers:** the Roanoke start mark (t 0, bloom .75) and the Croatoan arrival stamp (t 2.6, r14, bloom .9, fibrous blot).
  **There is no glow anywhere.**
* **Cloud shadows:** raised to 0.32 (from .21). They are larger and softer (lo 700, softness 2.3) to avoid blotches.
* **Endpoint:** (668,1405) on the cape. The sea mask is 0 there and in a 5 px ring, so it is on land.
* **QC:**
  * Out of mask 0/0; isolation 0/0; layermask 0/0.
  * disp_max 0.974 px (sea water only); **coast and land at 0 px**.
  * changed_pct 85.3; render 41.7 s.
* **Stills:** `batch3/qc/b3_map_seq09a_inknib_dashed_v3_after_mid_phone360.png`, `…_after_end_t3.6_{platefull,phone360,endpoint_crop}.png`, `…_mask_overlay_readable.png`.
* **Verdict:** SHOW (moderate). The route, tip and stamps now read on a phone. The cloud shadows are still subtle.

## B3-3 — P06 v3: `batch3/b3_light_p06_ugarit_burning_dusk_flames_v3b.mp4` (v3 superseded)
* **v3** (`…_flames_v3.mp4`, md5 b3203c196bddd2f74057fcb5f3b6fd71) is **KEPT BUT SUPERSEDED**.
  Its widened bed started at x 92, and flames painted over the **foreground left door jamb** (x 55–145, y ~1250–1350).
  The old allow-region QC passed it because the whole bed bounding box was "allowed".
  Evidence is in `batch3/qc/b3_light_p06_v3_vs_v3b_jamb_crop.png` (left v3, right v3b).
  Batch-2 v2 may carry a slight leak of the same kind.
* **v3b** (md5 8116061e0901fb15f65c42a8bdce6bd2, config `configs/b3_light_p06_v3b.json`, seed 6063) adds `clip_to_mask`.
  Flame, hotspot glow, sparks and embers are all multiplied by `p06_opening.png`. **The jamb is clean.**
* **Fires:**
  * The big beds are 1.45–1.5x wider and 1.75–1.8x taller, with two new skyline beds.
  * Full bodies (`body_mix` .6, `despeckle` .07, `pad_mult` 3.6). The earlier despeckle .18 flattened the tops.
  * Soot haze above the tips feeds into the smoke.
  * The shimmer is wider (`spread_px` 40, amp 1.8), on the sky only. Sparks 320.
* **QC (v3b):**
  * out_outside 0; isolation 0 on all 4 layers.
  * disp_max 2.09 px at (769,515), sky; **stone 0 px** (disp_protect 0).
  * changed_pct 87.5; mean |Δ| 37.6; render 194 s.
  * **Layermask:** fire 0, atmos 0, light-shift 0.
    Smoke shows 107.9 at (855,1329), from foreground ash drifting over the frame. This is **intentional** (same as b1/b2) and the smoke allow-region is the full frame.
* **Stills:** `batch3/qc/b3_light_p06_ugarit_burning_dusk_flames_v3b_after_mid_phone360.png`, `…_mask_overlay_readable.png`.
* **Verdict:** SHOW (v3b). On a phone the city reads as being consumed, with the fire inside the doorway only.
  Remaining weakness: the soot reads as subtle haze, not strong black plumes.

## B3-4 — WATER-GLINT (parked, finished last), light only, 0 px
* **Ugarit p07 sun path:** `batch3/b3_glint_p07_ugarit_sunpath_v2.mp4`
  * md5 ca5048b8c0f9770cd2e82352294b983d; config `configs/b3_glint_p07_v2.json`.
  * Mask p07_sea (8.4 %). changed_pct 3.4; mean |Δ| 0.81.
* **Croatoan dusk:** `batch3/b3_glint_croatoan_outro_duskpath_v2.mp4`
  * md5 1e202e9f6f17f5771ad89303ad2e87bf; config `configs/b3_glint_croatoan_outro_v2.json`.
  * Mask outro_ch1_water (42 %). changed_pct 8.7; mean |Δ| 1.03.
  * The plate carries baked "POSTERITY" branding text, which is masked out (static).
* **QC (both):** out-of-mask 0; isolation 0; disp 0.0 px everywhere (no displacement used); coast static.
* **Fixes:** the earlier b3_glint_* previews read as single-pixel dust spread off the path.
  v2 uses lower-frequency glint textures (`glint_lo`/`glint_hi`), near-zero off-path glints and a high `lum_follow`.
  The v1 configs are kept, not overwritten.
* **Stills:** `batch3/qc/b3_glint_p07_ugarit_sunpath_v2_after_mid_phone360.png`, `batch3/qc/b3_glint_croatoan_outro_duskpath_v2_after_mid_phone360.png`.
* **Verdict:** BORDERLINE / HOLD as a standalone effect. At 360 px the sparkle is small; it reads in motion as gentle twinkle on the path, not a hero effect. Use it only as a layer under other motion.

## B3 regression check (after all batch-3 engine edits)
* Every shipped b1/b2/b3 config was re-rendered with the final `animate.py` into `/tmp/regress/` (nothing in the project was touched).
* **All 8 are bit-identical** (mp4 md5 and frames_sha256):
  * b1 map final c63bbe60…, b1 env v2 02d07421…, b1 P06 final 1fb0d7e9…
  * b2 candle 2962e4ac…, b2 map dashed 6b2d06d3…, b2 P06 v2 759ccaa1…
  * b3 candle v2 030cbcbb…, b3 map v3 b8aa9ceb…
* The new features are therefore strictly opt-in.
* Layermask QC: candle v2 0; map v3 0/0; P06 v3b fire/atmos/light 0 (smoke = intentional ash); glint p07 0; glint Croatoan 0.

---
## Batch 4 (2026-10-22, from 2:48 PM)
### Task 1: house presets locked
* `house-candle-lightspill-v1` = `presets/locked/house-candle-lightspill-v1.json` (byte copy of `b3_candle_seq14_v2.json`, md5 0591d4c7…).
  The `--repeat-check` render and rerun both give md5 **030cbcbb8bbb5977066975a5c7f5b9e7** (identical; frames sha256 identical).
* `house-map-inknib-dashed-v1` = `presets/locked/house-map-inknib-dashed-v1.json` (byte copy of `b3_map_seq09a_dashed_v3.json`, md5 d0ad9016…).
  Render and rerun both give md5 **b8aa9ceb7cae2757a44d9919eb8ddd9f** (identical).
* Verify renders: `presets/locked/verify/` (41 MB). Frozen engine: `presets/locked/engine/animate_b3_cb9e2b88.py`.
* **Owner production rule logged** (see PRESETS.md):
  * Candles and small fires get `house-candle-lightspill-v1` by default, starting with Atahualpa 10/23.
  * Mask the source plus the lit surfaces. Flame sway, 0 px displacement elsewhere, and the 100→104 % zoom with house cuts.
  * Large fires and burning cities stay R&D.
  * The "applying to a new plate" recipe was added.
* **Motion roadmap (owner-approved 2026-10-22) logged in PRESETS.md:**
  * Order: maps → fire & night light → sea & coast → sky & weather → smoke & dust → documents & objects, with characters later.
  * Approved presets are auto-applied defaults with per-plate masks; only approved presets ship.
  * Status tags: APPROVED-DEFAULT vs R&D.
### Engine
* animate.py was replaced in place (old version backed up at `/tmp/animate_pre_b4.py` and frozen in `presets/locked/engine/`). New md5 6d49aeb4….
* Opt-in additions only, with no new rng draws: per-bed `flicker` override and `rate`, per-bed `taper` mound envelope, and `flame_tongues.bed_spill`
  (the candle light-spill model applied per fire clump, with per-bed `spill_gain` / `spill_radius`, exclude masks, and an optional `dark`).
* Second in-place engine edit (stage-1 backup at `/tmp/animate_b4_stage1.py`): water-glint `grow_px` / `star` / `halo`, opt-in only. Final animate.py md5 96da01a0….
* **Regression check** (12 old configs re-rendered to `/tmp/regress_b4`, compared with the delivered batch outputs or the pre-b4 regress renders):
  every one is **bit-identical**, including the locked presets (030cbcbb, b8aa9ceb), P06 v3b 8116061e, and glint v2 ca5048b8 / 1e202e9f.
  The b1 configs reproduce the delivered `_final` files.
### Task 2: Ugarit P06 v4 (`configs/b4_light_p06_v4r3.json`)
* `configs/b4_light_p06_v4.json` is a first draft (spill amp 1.1). It measured ±10 % half-swing, too timid. **It was not rendered; it is superseded by v4r3.**
* r2 (amp 1.4, original flicker): ±13.8 %, but the step was 5.65 %/frame, over the limit.
* **r3 shipped:** amp 1.35 with calmer high-frequency flicker. 25 clumps: 16 street clumps (h 60–232, rate .8–1.4) and 9 skyline clumps.
* Output: `batch4/b4_light_p06_ugarit_burning_dusk_fires_v4.mp4`, md5 **aa7862de41a3907e8c37d6460377c11d** (repeat-check identical).
  Changed 87.6 %, mean |Δ| 47.7.
* **QC:**
  * isolation 0 outside own mask on all layers
  * displacement: stone 0 (fire layer max 2.10 px = sky shimmer, 0 in protect)
  * **layermask: fire-torchlight 0.0 outside p06_opening, so no jamb leak**
    (jamb mean |Δ| vs plate is the same as v3b, 7.94 at t=2; that change comes from the smoke/ash and light-shift layers)
  * smoke 102.7 = intentional foreground ash, as in b2/b3
* Spill swing: strong-spill ±13 % (26 % p2p), ground ±13 %, step ≤ 4.7 %/frame, lift +58–80 %.
### Task 3: water glint v3
* **p07:** `batch4/b4_glint_p07_ugarit_sunpath_v3.mp4`, md5 **1062f73a04ff856622dcc6b29b936783**.
  Changed 4.5 % (v2 3.4 %), mean |Δ| 3.10 (v2 0.81). disp 0, layermask 0, isolation 0.
* **Croatoan outro:** `batch4/b4_glint_croatoan_outro_duskpath_v3.mp4`, md5 **adb5242dc5403178e4653ed8de70901d**.
  Changed 13.7 % (v2 8.7 %), mean |Δ| 4.43 (v2 1.03). disp 0, layermask 0. POSTERITY glyph max |Δ| = 0.

# Batch 5 (engine md5 b371d67f54a0844a25a1ee2b19baf216; backups presets/locked/engine/animate_b4_96da01a0.py, animate_b5_b371d67f.py)
**Regression:** 15 old configs (b1–b4) re-rendered: 14 IDENTICAL.
b1_map_seq09a gives c63bbe60, which is identical to the b4-engine render. Its eb6c70d4 file is the superseded v1 (a known, pre-existing difference).
The shipped aa7862de, 1062f73a and adb5242d are all identical. Summary: `batch5/qc/regress/regress_b5_summary.txt`.

## P06 v5: `batch5/b5_light_p06_ugarit_burning_dusk_fires_v5.mp4`, md5 c216ae74903efbea0a4fb93dd51e8a04 (config `configs/b5_light_p06_v5.json`)
* **Sky above skyline, mean B−R / hue** (`batch5/qc/b5_light_p06_v5.sky_hue.json`, v4 in `b4_light_p06_v4r3.sky_hue.json`):
  * Plate: +10.6 / 245°
  * v5: t.1 −1.6 / 312°, t2 +8.2 / 264°, t3.9 **+15.9 / 252°** (stays blue)
  * v4: t3.9 **−79.9 / 18°** (it went orange)
* **v4 defect found:** pale rectangles in the sky above the skyline, from the rectangular cut-outs in its spill exclude mask. Fixed by the new `p06_sky_v5` mask. See `batch5/qc/p06_v4_top_vs_v5_bottom_skyline_crop_t6.jpg`.
* **Spill swing** (`b5_light_p06_v5.spill_swing.json`):

  | Region | Lift | p2p | Max step |
  |---|---|---|---|
  | Strong spill | +38.6 % (v4 +57.8) | 43.9 % | 2.83 %/frame |
  | Ground below clumps | +64.9 % (v4 +80.3) | 39.1 % | 3.09 %/frame |
  | Whole frame | +20.7 % (v4 +32.9) | | |

* **QC:** repeat-check identical. Isolation 0 on all layers. Layermask: fire 0 outside p06_opening (jamb clean; jamb mean |Δ| 4.44, same as v4r3); smoke 102.7 = intentional ash, as before. Displacement 0 in protect, fire layer max 2.09 px (sky shimmer).
* **Phone stills:** `b5_light_p06_v5_phone360_early_mid_late.png`, compared with `b4_light_p06_v4_phone360_early_mid_late_for_compare.png`.

## Map R&D (new preset map-ink)
* **Stamps:** `batch5/b5_map_seq09a_stamps_landing_v1.mp4`, md5 557fe5a1e3f5cad71414a62c68fc98cd (`configs/b5_map_seq09a_stamps_v1.json`).
  * Roanoke seal lands at 0.45 s and Croatoan at 1.55 s (R 80).
  * Repeat-check identical. Isolation and layermask 0. Land/protect displacement 0 (sea water 0.98 px, from the locked look).
* **Wash:** `batch5/b5_map_p03_hatti_wash_fill_v1.mp4`, md5 26fb298df817a9d1ca10d6e97d2c03ab (`configs/b5_map_p03_hatti_wash_v1.json`).
  * Hattusa seal lands at 0.3 s. Wash bleeds over Anatolia and down to Ugarit from 0.32 s, about half covered by 1 s.
  * Masks: `batch5/masks/p03_*`. Same QC results.
* **Phone strips:** `batch5/qc/*_phone360_strip.png`.

# Batch 6 (map R&D v2 + P06 v6)
Engine: `animate.py` md5 886d34e09df4d15a8561064f41609671. Backup: `presets/locked/engine/animate_b6_886d34e0.py`. Pre-b6 engine: `animate_b5_b371d67f.py`.

Regression (`/tmp/regress_b6/summary.txt`): all old configs plus the 3 b5 configs IDENTICAL, except `b1_map_seq09a` (c63bbe60 vs eb6c70d4). That difference is pre-existing and also appeared in the b5 regression, so it is not caused by b6.

## Stamps v2: `batch6/b6_map_seq09a_stamps_landing_v2.mp4`, md5 ca7712e6404a9e3245f9702f005a835a
* Config `configs/b6_map_seq09a_stamps_v2.json`. Wax seals with a Tudor rose, no letters (Elizabethan, 1585).
* Roanoke lands at .45 s and Croatoan at 1.55 s (R 60), descending from 1.3× with blur and a converging shadow. No bounce.
* Impact ROI mean Y: one step 128.9→121.6 (Roanoke) and 109.6→102.7 (Croatoan), then a monotone recovery. That is one pulse, no strobe.
* QC: repeat-check identical. Isolation 0, layermask 0. Land displacement 0 px (sea .98 px).
* Strip: `batch6/qc/b6_map_seq09a_stamps_landing_v2_phone360_strip.png`.

## Wash v2: `batch6/b6_map_p03_hatti_wash_fill_v2.mp4`, md5 dd351b4c5724a417662efaeabe2a656a
* Config `configs/b6_map_p03_hatti_wash_v2.json`. Soft feathered Hatti influence. **No border line** (eastern border removed per Vellum). The extent is an approximation, not a sourced boundary.
* Coverage of the final change:

  | t (s) | .5 | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 3.97 |
  |---|---|---|---|---|---|---|---|---|
  | coverage | .07 | .39 | .60 | .73 | .83 | .91 | .97 | 1.0 |

  Half coverage is at ~1.2 s, slightly late versus the 1 s target. Ugarit arrives at ~2.0 s (Sa .92).
* Changed area is 42.8 % of the frame. Colour is carmine/magenta. Mean LAB before [142.6,135,158.3], after [121,148.4,143.4]. Ugarit dE(a,b) 43.5.
* QC: repeat-check identical. Isolation and layermask 0. Land displacement 0.
* Strip: `batch6/qc/b6_map_p03_hatti_wash_fill_v2_phone360_strip.png`.

## P06 v6: `batch6/b6_light_p06_ugarit_burning_dusk_fires_v6.mp4`, md5 797f1d7ffb0d3d09bb104dd4289027da
* Config `configs/b6_light_p06_v6.json`, from v5. Changes:
  * ft `opaque {"alpha":1.0}`.
  * Plumes 2 and 3 get `cool` amt .8, dark [40,42,52], light [108,112,126], opacity ×1.15.
* Plume-base B−R at t .5 / 2 / 3.5:

  | Plume | v5 | v6 |
  |---|---|---|
  | idx2 | −33.8 / −21.1 / −8.3 | −3.5 / +5.9 / +13.9 |
  | idx3 | −54.4 / −45.1 / −37.2 | −11.0 / −4.9 / −3.8 |

* Sky hue matches v5: upper-sky B−R 34.7 at t4 (v5 34.4 at 3.9).
* Spill swing ≈ v5:

  | Region | Lift | p2p | max step |
  |---|---|---|---|
  | Strong | +39.0 % | 43.7 % | 2.83 %/frame |
  | Ground | +65.4 % | 39.1 % | 3.14 %/frame |

* QC: repeat-check identical. Isolation 0. Layermask: fire 0 outside p06_opening (jamb clean); smoke 102.7 = intentional ash, as in v5. Displacement 0 in protect, max 2.09 px.
* Jamb crop v6 vs v5: `batch6/qc/b6_light_p06_v6_vs_v5_jamb_crop_t7.5.png`. The flames clip cleanly at the jamb edge. Small differences near the edge come from spill/edge rounding.
* Stills: `batch6/qc/b6_light_p06_ugarit_burning_dusk_fires_v6_phone360_early_mid_late.png`. JSON: `batch6/qc/b6_light_p06_v6.{sky_hue,spill_swing}.json`.

## Batch 7: Hatti wash v3, sourced extent (17:00–17:15 EDT)
* Output: `iterations-2026-10-22/batch7/b7_map_p03_hatti_wash_fill_v3.mp4`, md5 50520427f94ffde568625afc7c752f1f. Config `configs/b7_map_p03_hatti_wash_v3s.json` (the `_v3` and `_v3_t1` configs and masks `p03_hatti_influence_v3{,b}.png` are unrendered heartland-corridor drafts superseded by the sourced brief; kept).
* Engine a88fde43 (opt-in `geo_thresh`), backup `presets/locked/engine/animate_b7_a88fde43.py`. Regression: b6 wash v2, b6 stamps v2, b5 wash v1, b5 stamps v1, b3 dashed v3, b2 solid all IDENTICAL.
* QC: repeat render md5 identical; isolation 0; layermask 0 outside declared masks; disp_protect_max 0 (land 0 px).
* Coverage (zoom-compensated, chroma Δab>15): v3 31.3 % of frame vs v2 31.2 % (Δab>8: 37.2 vs 35.4). The old 42.8 % figure was inflated by the 1.0→1.04 camera zoom; the uncompensated metric gives v3 43.9 %. Mask itself: 26.3 % of frame ≥.5, 32.7 % ≥.2. **The sourced extent is not smaller than v2**: it adds the east edge/north Syria and the pale west.
* Timing (share of final wash ≥50 % developed): 0.5 s .25 · 1.0 s .56 · 1.5 s .70 · 2.0 s .79 · 2.5 s .87 · 3.0 s .93 · 3.5 s .98 · 3.97 s 1.00 (v2: .03/.36/.57/.70/.81/.89/.97).
* Ugarit Δab at end 43.4. Thin darker wet line at the front, dries lighter; relief reads through; no residual border after drying.
* **Sources note (extent, late 13th–early 12th c BC, brief from Archivist):**
  * World History Encyclopedia, "Ugarit" (L. King, 2012): Ugarit a Hittite vassal from the mid-14th c BC, alongside Amurru to its south; destroyed c. 1190 BC.
  * Wikipedia, "Carchemish": Hittite viceroyalty from Šuppiluliuma I (c. 1321 BC); site on the WEST bank of the Euphrates; cites Bryce, *The Kingdom of the Hittites*; Kitchen.
  * Wikipedia, "Alashiya": Cyprus; Tudhaliya IV and Šuppiluliuma II campaigned there c. 1200 BC and imposed a submission treaty, but direct control is doubted. Cites Beckman, Bryce & Cline 2012 (*The Ahhiyawa Texts*), Beal 2011 (*Oxford Handbook of Ancient Anatolia*). Hence Cyprus unwashed (optional hatch not done).
  * Wikipedia, "Arzawa": Mira, Hapalla, Seha River Land, Wilusa made vassals by Mursili II (c. 1300 BC); Millawanda/Miletus under Ahhiyawa (Mycenaean) control. Cites Bryce 2011 (Oxford Handbook), Beckman, Bryce & Cline 2012.
* **Off-frame/approximation on p03:** the Euphrates bend and Carchemish lie east of the plate's right edge (x 941; no Euphrates painted), so the solid wash runs to the frame edge there and "stop at the river" can't be shown. Miletus and the Aegean coast (also Wilusa/Troy) lie west of the left edge, so the Miletus exclusion isn't visible; the pale west fades off-frame. Kadesh line estimated at plate y ≈1012–1025 (lat scale ~187 px/deg). Hand-built polygons on a painterly map: positions approximate.
* Regression addendum (17:23 EDT): b6_light_p06_v6 also IDENTICAL (797f1d7f…). All 7 targeted configs identical.

## b9 — Agincourt battle-map PoC v1
- Out: iterations-2026-10-22/batch9/b9_battlemap_agincourt_poc_v1.mp4 (md5 50c85313e38eaa461c0f3984c06bdd95; 720x1280, 30 fps, 300 f, 10.0 s, no audio). Config md5 732bd2551b69d4f0cf0372c33acb7e66. Deterministic (2 renders, frames sha c14b2956…). Phone strip: batch9/qc/b9_battlemap_agincourt_poc_v1_phone360.png.
- Passes: wip1 (edge fur → 2D noise; missile strips colour), wip2 (time warp to kill empty first second; hide_zoom labels), wip3 (French cavalry gold so horns/recoil read; funnel arrows moved outside the vanguard along the woods; clash camera cy 1310), final (marker 60 px r at 540,1388 so it sits on the contact line, less over Henry).
- Plate is AI-generated (GenerateImage) at parent's explicit instruction — conflicts with standing "no AI images" rule; flagged.

## b8 — Sword map marker (Ocracoke) + icon contact sheet
- batch8/b8_map_marker_sword_ocracoke_v1.mp4 (md5 71acf1bc6162a21efea68a6f2283e257): sword r64 at plate (648,1108). Reads, but it's thin and sits off to the NE of the ship.
- batch8/b8_map_marker_sword_ocracoke_v2.mp4 (md5 964b98660ed1970a65727ad1309219e1): r86 at (572,1072), rot -22, blade points down onto Teach's sloop. Recommended.
- Configs configs/b8_map_marker_sword_ocracoke_v1/v2.json: `icon`, `t_on`, `xy`, `radius`, `rot_deg` are the knobs.
- Contact sheet batch8/qc/b8_map_marker_icons_contact_v1.png (md5 02d73c90…): sword / crossed_swords / anchor / skull at t = .25/.42/.55/2.5 s (crown also available).
