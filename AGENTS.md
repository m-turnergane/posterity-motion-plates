# AGENTS.md — conventions for Codex / ChatGPT / human reviewers

Scope: experimental, **separate from the production editor**. Nothing here edits day-N build scripts or plates. The ordinary stills pipeline is unchanged; motion is only for *selected* plates.

## Hard rules
1. Never copy plates into this repo and never commit large binaries (`*.mp4`, `*.png` outside `tests/data`, `out/`, `cache/` are git-ignored). Plates are read from `$MOTIONPLATES_PLATES` (default `/workspace/posterity/day20/alexander-corpse/plates`).
2. Frame 0 must equal the cover-fit plate (max abs diff 0 in the lossless pipeline). Effects start from zero (`ramp_in`), the clean-plate swap is corrected by the fading residual (`frame0_residual_fade_s`).
3. Deterministic: all randomness comes from `ctx.rng(name, idx)` = `default_rng([seed, crc32(name), idx])`. No `time`, no global RNG. Effects are pure functions of `t`; the frame loop is stateless, so any frame can be rendered alone (`--at`).
4. Restrained motion: camera push is a few percent and eased; no generic Ken Burns; no uniform pulsing (flicker = multi-band smooth noise). Motion cap tests live in `tests/`.
5. Original plate is always the fallback; the editor integration is "if the motion mp4 is missing or fails QC use the PNG".
6. No network, no publishing, no secrets in the repo.

## Layout
- `src/motionplates/core/` plate loading (bar detect + cover-fit identical to build scripts), layers (polygon/GrabCut masks, inpaint, clean plate), engine (frame loop, residual, metrics, manifest), encode (lossless intermediate -> delivery encode), compare (side-by-side + labelled stills).
- `src/motionplates/effects/` one file per primitive, registered by `@register("type")`: `petal_fall flame_flicker banner_sway dust_motes parallax_push fabric_ripple torch_light`.
- `recipes/<plate>.yaml` authored per plate (layer polygons, petal cuts, positions); `recipes/presets/*.yaml` reusable presets (`preset:` key, override per recipe).
- `tests/` pytest on a generated synthetic plate (frame-0 equality, determinism, motion cap, safe zones, edge/white-bar scan, no plates in git).
- `docs/` architecture, authoring effort, experiment C (skipped).

## Adding an effect
Subclass `Effect`, implement any of `authoring_holes / setup / layer_stage / post`, decorate with `@register`. `layer_stage` edits per-frame layer pixels via `st.rgb(name)` / `st.alpha(name)` (copy-on-write); `post` draws screen-space sprites and must map positions through `ctx.camera_fn(depth, t)`. Add a preset and a test.

## Review checklist
Seeds fixed? Frame 0 identical? Layer masks generous (never inside the subject), disocclusions inpainted? Motion numbers in manifest within caps? No plate/binary committed?


## v0.2.1/v0.3 rules
- Never hardcode a plates path; use --plates / $MOTIONPLATES_PLATES.
- Never commit plates, MP4s or the PoC C base map (md5 in assets/basemaps/README.md).
- Motion plates are at best REVIEW_REQUIRED until an editor sets qc.playback_approved for that exact frames_sha1. Original static plates stay the fallback.
- No merge to master / production activation without owner approval.
