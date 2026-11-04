# build_template_v1.py: generic box build template (Edward II long-form and Shorts)

A NEW standalone template. It does not modify any episode build script or any locked file
(smoke_v2.py, fx_v1c.py, water_v1.py, dust_v1.py, PRESETS.md). Python: `/workspace/mpvenv/bin/python`.

## Based on
* **Base:** `standalones/jianwen/build_rough_jianwen_v2.py`, the newest and cleanest. It provides smoke_v2 loaded by path,
  the zero-motion smoke proof, cut-safe captions, the loudness loop, the house `prepare_cover`/`cam`/`cam_frame`
  push, and the Chronicle Reveal title. Edward v3b v1c was read for the fx hook (`PlateFX(plate_path, seed)`), which
  is now opt-in via `--fx-module`.
* **Guards from Atahualpa v2c:** refuse to overwrite a master; refuse a smoke config that names a different plate.
  Not ported on purpose: the "non-empty build dir" refusal. The keyed cache below makes reusing a build dir safe,
  and that is the point of the cache.
* **Guardrail:** `motion/guardrails.py::check_crop_zoom(max_zoom=1.5, mode="refuse")` runs for every shot before anything renders.
* **Pixel-density guardrail:** `check_pixel_density(max_ratio=1.5)` runs for every shot too (see the section below).

## Usage
```
PY=/workspace/mpvenv/bin/python; T=/workspace/posterity/motion/templates/build_template_v1.py
$PY $T --manifest plates.json --timeline timeline.json --size 1920x1080 --build-dir /path/build --tag rough1 --check
$PY $T --manifest plates.json --timeline timeline.json --size 1920x1080 --build-dir /path/build --tag rough1
```
Always run from the file (fork Pool + `__main__` guard). Never pipe it through stdin.
* `--check` resolves the manifest, timeline and guardrails, prints the plan and FLAGS, and renders nothing.
* `--clips-only`, `--audio-only` and `--no-phone-qc` skip parts of the build.
* `--fx-module path/fx_x.py` adds an optional per-plate fx module (its file md5 and its `_ENG` md5 go into the keys).
* `--extra-key-files a,b` adds extra files whose md5 joins every shot key.
* `--smoke-engine` defaults to `engine-rnd/smoke/smoke_v2.py`. When that default is used, its md5 is asserted to be `80bb2869...`.
* Paths derive from the template's own location (`templates/ -> motion/ -> posterity/`). `POSTERITY_ROOT` overrides this. Nothing hard-codes `/workspace`.

## --size WxH (default 1080x1920; long-form 1920x1080)
Every dimension derives from W×H, with scale `U = min(W,H)/1080`:
| | portrait (H>W) | landscape |
|---|---|---|
| captions | Shorts safe zone, font 54U, MarginV 400·H/1920, 24 chars/line | EBU 10 % safe, MarginV 0.09H, MarginL/R 0.1W, 42 chars/line |
| title (Chronicle Reveal) | top 16 %, band 94 % W, line ≤ 0.92W | top 24 %, band from text, line ≤ 0.80W |
| phone QC PNG | 360 wide (360×640 at 9:16) | 360 tall (640×360) |
| preview | 720 wide | 720 tall (only written when the output's short side > 720) |
The push/crop/cover uses the house `prepare_cover(2x)` and `cam_frame` at W×H. Each shot computes
`zoom = max(push) × (1/crop.frac)` and passes it to `check_crop_zoom`. Anything over 1.5x makes the run exit with `GUARDRAIL REFUSED`.
The ASS PlayRes is W×H. The title box is checked against the safe area and FLAGged if it falls outside.

## Pixel density guardrail (EIC ruling 2026-10-30)
At planning (inside `setup()`, so also under `--check`), every shot's **output px per real source px** is computed with
`guardrails.check_pixel_density(plate file, (W, H), push, crop_zoom=1/crop.frac)`: cover-fit scale × peak push × crop zoom,
both axes, max taken, using the plate file's actual size (not `target_resolution`). Anything over **1.5** makes the run exit
non-zero with `GUARDRAIL REFUSED (pixel density > 1.5 ...)`, listing **every** offending shot (id, plate, ratio, plate size, and the
minimum native size needed). Nothing renders and no build dir is created. The plan line prints `density N.NNN` per shot.
* 941x1672 portrait plate → 1920x1080 = 2.040 (refused; 2.163 at push 1.06). Same plate on a 1080x1920 Short at 1.06 = 1.217 (ok).
* 2560x1440 → 1920x1080 at push 1.06 = 0.795 (ok). 1080x1920 Short plate at 1.06 = 1.060 (ok). 640x1138 → 1080x1920 at 1.06 = 1.789 (refused).
* The P05 water_v1 waiver does not apply here (it lives only in `check_shot` for the exact locked water shot); a P05-style 1.6x shot is refused.

## Depth layer (depth_v1, LOCKED 2026-10-30 6:16pm ET): OPT-IN per shot, OFF by default
A shot gets depth **only** if its timeline entry has a `depth` key (absent, `null`, `false` or `{"enabled": false}` = flat). With no
depth shot in the timeline, `depth_v1.py` is not even loaded. The value is one of:
* `"depth": "../../engine-rnd/depth/configs/b05_landing_push_v1.json"`: a depth_v1 config by reference;
* `"depth": {"config": "<cfg>.json", "camera": {"travel": 0.02}}`: a reference plus overrides (dicts merge one level deep);
* `"depth": {"matte": {...}, "layers": [{far}, {near, polys/region/...}], "camera": {...}, "crop": {"9x16": [x0,y0,x1,y1]}}`: inline.

Rules:
* **One camera.** A depth shot renders through `depth_v1.DepthShot.frame` (one uniform matrix per layer per frame, push + drift folded in).
  It **replaces** the template push: `cam_frame` / `prepare_cover` are never called for that shot. The depth config's `camera.push` wins.
  If it has none, the shot's `push` (default [1.0, 1.06]) is folded into the layer matrices instead. A template `crop` on a depth shot is
  refused; put the window in the depth config's `crop` per aspect.
* **Effects compose inside the layer matrix** as depth_v1 `plate_fx`. Order: the fx module (torch / candle; its own `par` parallax is
  frozen at u=0), then smoke_v2, then `"dust": "<dust_v1 cfg>"` / `"water": "<water_v1 cfg>"` (only their `.frame(t)`; their
  `F3.push_frame` camera is trapped and must be called 0 times), then grade. dust/water are accepted on depth shots only.
* **Plate-specific configs.** A depth, dust or water config whose `plate` is a different file (by md5) is refused, the same rule as smoke.
* **Density is checked per layer** at planning (`--check` too): layer scale = cover-fit × shared overscan × layer zoom × depth crop.
  The gate is the larger of the two layers; the plan line prints `DEPTH n layers (template push skipped) overscan .. gate layer .. per-layer far:x,near:y`.
  16:9 needs a native landscape plate ≥ ~1357x763 (Hubert 1920x1543 → 1.100 ok; a 941x1672 Edward plate is refused).
* **Proof per clip**: `clips/{sid}.depth_proof.json`. `warps_logged == frames × layers`, max 1 warp per (frame, layer),
  `template_cam_calls 0`, `effect_camera_calls 0`. If any fails, the shot fails and no key is written.
* **Cache key**: md5 of the resolved depth config, md5 of the referenced config file, depth_v1.py md5 + model file name/size, and the
  dust/water config + engine md5s.
* **When to use it (owner rule, motion/PRESETS.md "depth_v1"):** use it on motion/action plates (arrivals, landings, escapes, processions,
  crowds, journeys). Quiet portrait, dialogue and still character plates stay flat. Never use depth on back-to-back character plates.
  "About 1 in 3" is only a loose ceiling. Planning prints:
  * `WARN depth back-to-back on character plate(s): Sxx -> Syy`: two consecutive depth shots where either is a character plate.
    The plate counts as a character plate if the shot has `"character": true` or `"plate_type": "character"`, or the manifest row has
    `plate_type: character`. This is a warning, not a refusal.
  * `WARN depth on Sxx without scene_action / depth_ok_reason`: say why the shot gets depth.
  * `FLAG depth on n/N shots`: when depth goes well past ~1 in 3.

## Tests
`cd motion/templates && /workspace/mpvenv/bin/python -m pytest -q -p no:cacheprovider tests/` (26 tests, ~35 s; renders are tiny,
108x192 and ≤ 9 frames, in pytest tmp dirs).
* `test_build_template_v1.py` (16, all `--check`) covers the density cases above, max-push / both-axes, real-file-size, the
  check_shot / check_crop_zoom wiring, the P05 exact-shot waiver and that it is not broadened, crop counting toward density, and the
  examples' missing-plate exit 2.
* `test_build_template_depth.py` (10) covers:
  * a 9:16 depth shot rendering a tiny clip (real b05 config by reference, plus a cache hit on re-run);
  * a 16:9 depth shot on a 941x1672 plate being refused;
  * the Hubert native plate passing 16:9 at density 1.100;
  * a single transform (cam_frame / prepare_cover booby-trapped; warps == frames × layers);
  * dust_v1 composing inside the layers with 0 effect-camera calls (b01);
  * the cache key changing with an inline or referenced depth config;
  * depth off by default;
  * flat-shot pixels identical to the pre-depth template;
  * the back-to-back character WARN (manifest and timeline tags, plus negatives) and the missing-reason WARN;
  * a refused template crop and a refused foreign-plate depth config.

## Manifest (--manifest .json or .csv)
Fields (all rows): `plate_id, scene_id, shot_ids, prompt, aspect, target_resolution, expected_filename, refs, notes`, plus optional
`plate_type` (`character` feeds the back-to-back depth WARN), `scene_action` and `depth_ok_reason` (notes on why a plate gets depth).
* JSON can be a list of rows, or `{"plates_dir": "...", "plates": [...]}`.
* In CSV, `shot_ids` and `refs` are `;`- or `|`-separated.
* Plates resolve as `plates_dir/expected_filename`. `plates_dir` comes from `--plates-dir`, else the JSON key, else the manifest's folder.
* Validation rejects unknown or missing fields, path traversal, a duplicate plate_id or filename, a shot claimed by two plates, and an aspect that contradicts target_resolution.
* **Missing files:** every missing plate is listed (plate_id, shots, expected filename) and the run exits 2 before rendering.
* Soft FLAGs: the plate's real size differs from target_resolution; cover-fit shows less than 75 % of the plate; the plate is upscaled more than 1.43x; manifest plates are unused; shot_ids are not in the timeline.

## Timeline (--timeline JSON; relative paths resolve from its folder)
```
{"name": "edward-ii-lf", "fps": 30,
 "shots": [{"id": "S01", "seconds": 6.0 | "frames": 180, "plate_id": "(optional)", "anchor": [0.5,0.5],
            "push": [1.0,1.06], "crop": {"center": [0.5,0.5], "frac": 0.75}, "smoke": "smoke_S01.json", "fx": true,
            "depth": "(optional, OFF by default) depth_v1 cfg | {config, ..overrides} | {inline}", "dust": "(depth shots) dust_v1 cfg",
            "water": "(depth shots) water_v1 cfg", "character": false, "plate_type": "character|...", "scene_action": "...", "depth_ok_reason": "..."}],
 "title": {"text": "LINE1\nLINE2", "start_f": 6, "exit_f": 150, "font_px": 78, "top_pct": 24},
 "captions": [{"start": 0.2, "end": 2.5, "text": "..."}],
 "audio": {"vo": "vo.wav", "music": "bed.wav", "bed_db": -17.5, "lufs": -14, "tp_max": -1.0}}
```
Shots map to plates through the manifest `shot_ids`. A caption that straddles a cut is refused. Unknown shot keys are FLAGged (ignored).
The smoke config uses the smoke_v2 format, e.g. `{"seed":4,"protect":[],"emitters":[{"type":"candle","src":[x,y],"height":N}]}`.

## Content-hash cache (fixes the "exists -> reuse forever" bug)
Each clip `clips/{sid}.mp4` has a `{sid}.key` sidecar (JSON) holding md5s of: the template, the plate file, the shot's
segment JSON (frames, anchor, push, crop, run clock), the smoke config file, the engine files (smoke_v2, fx module and its
engine, extra key files), plus size/fps/encode settings, and the title md5 when the title overlaps the shot.
* Key matches: **CACHE HIT**, and the clip is reused.
* Key missing or different: the old clip, its key and its sidecars (smoke proof) are **renamed** to `{sid}.stale-<ts>.mp4` / `.key` / `.json`.
  Nothing is ever deleted. The shot re-renders, and the run prints which key parts changed.
* An orphan `.part.mp4` from a crashed run is also moved to stale. The key is written last (atomically), only after the clip and its smoke proof are good.
  A zero-motion smoke failure leaves no key, so the shot never counts as a hit.
* The same rule applies to `audio/mix.wav` (`mix.key` holds the VO/music md5s, duration, LUFS/TP targets, bed dB and filter chain; each key gets
  its own `work-<key>/` intermediates folder) and to the phone QC PNGs (keyed on the clip's key).
* Worker failures (a bad emitter, an encode failure, a zero-motion proof failure) are caught per shot and printed as `clip Sxx: FAILED ...`.
  The run exits with `CLIP FAILURES [...]` and writes no master. Good clips keep their keys. A foreign or missing smoke config is refused at preflight (also in `--check`).
* Each run writes `cache_report_<ts>.json` (hit or render per item, with reasons). Masters are `out/{name}-{tag}-{W}x{H}.mp4`
  and are encoded with `-n`, so an existing master is refused and you must pass a new `--tag`.

## Examples (EXAMPLE DATA, the plates do not exist)
`examples/example_manifest.json`, `examples/example_manifest.csv`, `examples/example_timeline.json`, `examples/example_smoke_S04.json`.
Running `--check` on them exits 2 and lists the 3 missing plates, which shows the missing-file failure.

## Known gaps
* Not ported: the episode-specific LEGEND overlay and the word-grid captions. Captions are plain ASS lines (cut-safe, scaled).
* `fx_v1c.PlateFX` SPECS are keyed to Edward v3b plates, so on new long-form plates it is likely inactive until a new fx module exists.
* The template md5 is in every key, so editing the template re-renders everything (deliberately conservative).
* Stale files accumulate by design (no deletes). Purge them by hand when space is needed (`--min-free-gib` guards the disk).
* The aspect cover-fit check only FLAGs, it does not refuse (a wrong-aspect plate is still refused when its pixel density exceeds 1.5). There is no `check_fire_sharpness` call. AAC true-peak after encode is not re-measured.
* The cache keys on file contents, not on the Python environment (e.g. an ffmpeg or numpy version change will not invalidate it).
* The portrait house title band at 16 % sits slightly above the Shorts top safe line. It is FLAGged, not moved, to keep the house look.
* Depth:
  * dust/water compose only on depth shots; flat shots still use the engines' own renders.
  * Only 2-layer configs are tested; 3+ layers should work through depth_v1 but are untested here.
  * The 0.5 s ease stays (owner may want snappier).
  * Depth shots render at plate resolution, so they are slower than flat shots.
  * With an fx module that has its own `par` parallax, the parallax is frozen inside depth (FLAGged).
  * A plate's first depth use runs DA2 (~1 s) and writes `engine-rnd/depth/cache/da2s_<md5>.npy`.
