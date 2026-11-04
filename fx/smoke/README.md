# smoke — procedural smoke overlay for still painted plates (PoC)

Posterity engine R&D, module `smoke_v1.py`. Status: **proof of concept** (2026-10-30).

## What it does
It composites animated smoke over a 1080x1920 (or any size) painted still plate. **The plate never moves.**
- **Density:** multi-octave periodic FFT noise, scrolled upward and domain-warped by a slowly evolving
  curl (swirl) field. Shapes billow and morph instead of sliding rigidly.
- **Per-emitter plume envelope:** narrow at the source, then widening, thinning and fading as it rises. The centre
  line wanders and leans.
- **Depth layers** for distant columns (`layers: 2-3`). Back layers are larger, slower and fainter.
- **Fire glow:** the smoke is lit from below with a smooth, non-repeating flicker.
- **Billow relief:** the noise is embossed so puffs read as rounded volumes.
- **No visible loop:** the textures are far taller than the distance scrolled in a shot, and the octaves scroll at
  incommensurate speeds.
- **Global ease-in** of opacity (no pop-in). There is also an optional slow 1.00→1.06 StablePush.
- **Zero motion outside the smoke:** pixels outside each emitter's footprint, and inside the `protect` polygons, are
  bit-exact copies of the plate. `--proof` prints a frame diff against the still to verify this.

It does not import any locked-engine, Edward II or Jianwen code.

## Install / run
Requirements: Python 3.9+, `numpy`, `opencv-python`, and `ffmpeg` on PATH.
```
pip install numpy opencv-python        # (in this repo: /workspace/mpvenv already has them)
/workspace/mpvenv/bin/python smoke_v1.py --config configs/b19_candle_wisps.json \
    --out out.mp4 --seconds 8 --proof --grab grab_360x640.png --grab-t 3.5
```
CLI flags:
| flag | meaning |
|---|---|
| `--config CFG.json` | emitter config (required) |
| `--plate PLATE.png` | plate image; defaults to the config's `"plate"` |
| `--out OUT.mp4` | output (H.264 CRF17 yuv420p, no audio) |
| `--seconds 8 --fps 30` | duration / frame rate |
| `--preview 360` | low-res output width for quick checks (height = 16:9) |
| `--no-push` | disable the 1.00→1.06 push |
| `--proof` | print the zero-motion report (max diff / changed pixels outside the smoke footprint; must be 0) |
| `--grab G.png --grab-t 3` | also save a 360x640 PNG frame grab |

Library use:
```python
import smoke_v1 as S, json
scene = S.SmokeScene(S.load_plate(path), json.load(open(cfg)))
rgb = scene.frame(t)                 # HxWx3 uint8, plate coordinates
S.zero_motion_report(scene, [0, 1, 2])
```

## Config format
```json
{
  "plate": "/abs/path/plate.png",
  "seed": 19,                 // master seed (everything is deterministic)
  "ease_in": 0.7,             // seconds of global opacity ease-in
  "push": [1.0, 1.06],        // StablePush start/end zoom
  "protect": [[[x,y],...]],   // polygons (plate px) where smoke is NEVER drawn (sea, faces, ...)
  "emitters": [ { "type": "candle|torch|column|haze", ... } ]
}
```
Each emitter starts from the `PRESETS[type]` values in `smoke_v1.py`. Any field can be overridden:

| field | plume types (candle/torch/column) |
|---|---|
| `src` [x,y] | source point in plate pixels (the wick / fire top) |
| `height` | rise height in px before it fully fades |
| `w0`, `w1` | plume width at the source / at the top (px) |
| `lean` | horizontal drift of the top in px (wind); + = right |
| `rise` | upward speed in px/s |
| `opacity` | peak alpha (0-1) |
| `lo`, `hi` | noise feature scale: coarse wavelength px / fine detail factor |
| `swirl` | curl-warp amplitude in px (grows with height) |
| `meander` | centre-line wander, as a fraction of `w1` |
| `thin` | how fast density thins with height |
| `color_dark`, `color_light` | RGB at the source / higher up |
| `detail` | weight of the second noise octave |
| `relief` | billow emboss strength (default 0.22) |
| `layers` | depth layers (1-3) |
| `glow` | `{color, strength, reach (fraction of height), flicker}` or `null` |
| `seed`, `name` | per-emitter variation / label |

`haze` uses `rect` [x0,y0,x1,y1], `drift` (px/s sideways), `opacity`, `lo`, `hi`, `feather`, and `color_light`.

Example configs: `configs/b19_candle_wisps.json` (Edward II b19 candles) and
`configs/p05v2_burning_town.json` (Ugarit p05 v2: 3-layer column, town fires, headland plume, ground haze, with
the sea and beach protected).

## Files
- `smoke_v1.py`: the whole module (noise, flicker, emitters, scene, push, writer, proof, CLI)
- `configs/*.json`: example emitter configs
- `poc/`: PoC clips and 360x640 grabs
- `NOTES.md`: state / next steps
- `scratch/`: dev contact sheets (disposable)

## Known limits (PoC)
- Overlay only. **Painted-plume matte billow (spec part b) is not built yet**, so existing painted smoke stays still.
- The smoke is clipped hard by `protect` polygons (feathered ~4 px). Place emitters so plumes don't cross them, or
  you get a visible cut edge.
- Candle wisps can look slightly "wormy" or contour-banded up close.
- Big columns read as smoke, but they are softer and flatter than painted billows. Glow is a simple vertical falloff.
- Speed: ~0.25 s/frame for the candle plate and ~1.7 s/frame for the p05 5-emitter scene at full res (single
  thread). Use `--preview 360` while tuning.
- Emitter positions are hand-placed in plate pixels. There is no auto-detection of fires.

---
# v2 — `smoke_v2.py` (current; `smoke_v1.py` is the frozen PoC above and still reproduces poc/)

Same dependencies (numpy, opencv, ffmpeg only; nothing imported from the locked engine, Edward or Jianwen).

## Run
```
P=/workspace/mpvenv/bin/python
$P smoke_v2.py --config configs/p05v2_every_fire.json --out x.mp4 --seconds 6 [--preview 360] [--proof] [--grab g.png --grab-t 1]
$P smoke_v2.py --reel configs/reel_final.json --out final/smoke_v2_final_reel.mp4 --jobs 5     # 1080x1920, ~2 min
$P proofs_v2.py configs/reel_final.json final/ --reel-mp4 final/smoke_v2_final_reel.mp4         # proofs.json, diff_*.png, contact_sheet.png
```
Reel JSON: `{"shots":[{"config":"configs/x.json","seconds":5}, ...]}` (paths relative to the package root); hard cuts,
each shot gets its own push 1.00->1.06. `--jobs N` renders shots in parallel and joins them with a lossless concat.

## New config fields (v2)
Scene: `preroll` (s, default 8 — sim runs before frame 0 so smoke is established; no global fade-in, `ease_in` default 0),
`protect` polygons + `protect_feather` (soft smoothstep keep-out, no hard cut), `flame_keepout` (0..1, smoke thins over
fire-coloured pixels so flames read through; use 0 + a protect polygon when a lit wall is itself fire-coloured),
`push_center` [fx,fy] (fixed point of the push), `guards` {name: polygon} (extra regions the proof must report as 0),
`billows` (painted-plume billow in a matte), `fires` (auto emitters).
Emitter: `type` candle|torch|column|haze, `src`, `height`, `w0`, `w1`, `lean`, `rise`, `opacity`, `layers` (depth 1-3:
back layers bigger/slower/fainter/cooler), `lo`/`hi` (noise band px), `swirl`, `laminar`, `meander`, `thin`, `detail`,
`breakup`, `edge`, `relief`, `puffs`, `body`, `res` (sim grid scale), `color_dark`/`color_light`, `glow`
{color,strength,reach,flicker,patch} (flicker clock), `start`/`end` (shot seconds: a plume grows up from the source / its tail
leaves the source and rises away — never fades in; `front_speed`), haze: `rect`, `drift`, `feather`, `spread`, `beta`.
`fires`: {ymin,ymax,exclude[polys],r_min,rb_min,min_area,split,skip_radius,wind,big,mid,column{},torch{},ember{},drop[[x,y]]} —
every fire component gets one emitter sized to its flame area (>=big column, >=mid torch, else ember wisp) at its flame tips.
`billows[]`: {region[polys], luma[a,b], sat_max, soft, dark_rel[a,b], rel_sigma, grow, feather, edge_feather, amp, rise,
period, scale, seed} — only matte pixels move (two-phase flow-map + curl warp, displacement clamped).

## Proofs
`--proof` / proofs_v2.py diff every sampled frame against the still plate: `max_diff_outside` (outside emitter
footprints + matte), `max_diff_in_protect`, `billow_max_diff_outside_matte` (emitters off), `guards_max_diff` — all must be 0.

## Shot configs
b19_candle_wisps_v2 (3 wicks), b10_wall_torch, b13_three_torches, p05v2_every_fire (46 auto plumes + hero column + haze),
p01v2_city_plumes (billow + distant coast fires), p06_doorway_plumes (billow + base columns), p06_street_haze (haze-led),
reel_final (p05, b13, p06 haze, b19, p01 — 26 s).
