# water_v1_1 = water_v1 (LOCKED) + crop/fire guardrails

- `water_v1_1.py` imports `water_v1.py` (unchanged, md5 811734e9e3919bddbe3ef22022203d5f) by path and delegates all rendering to it. Before any render, proof, stats, overlay or reel, it runs `motion/guardrails.py`:
  - `check_crop_zoom(max_zoom=1.5)`: the push/crop zoom relative to native cover-fit.
  - `check_fire_sharpness`: for fire shots, the Laplacian variance of the torch rects at native res must be ≥ 100, and the zoom must be ≤ 1.5.
- The default is to **refuse** (GuardrailError). `--warn-only` downgrades a refusal to a warning. `water_v1_1.py check <cfg|reel>` prints the report.
- **Identity, verified 2026-10-30:** 2 s at 540x960 rendered through water_v1.py and water_v1_1.py gives byte-identical mp4s and identical decoded frames.
  - nm4a_moon_path_v1b (shot 1): mp4 36c79fcd…, frames d344fb92…
  - p05v2_sun_glitter_v1d (shot 3): mp4 d9ec9aa7…, frames 2b8584ca…
  - Files are in `scratch/v1_1/`.
- **Guardrail conflict (shown, not hidden):** locked shot 3, p05v2_sun_glitter_v1d, is a static 1.6x crop, which is above 1.5x. To keep it bit-identical, it has a named waiver in `guardrails.LOCKED_WAIVERS`. The waiver only warns, and only at exactly 1.6. New work must not add waivers.
- Locked shot 2, k11_fire_reflection_v1b (2.2x, fire), is **refused**. It is a known bad example; see K11_FIRE_DIAGNOSIS.md. As a result, `water_v1_1.py reel configs/reel_v1.json` refuses. The locked reel final/water_v1_reel.mp4 stays the record of what was locked.
