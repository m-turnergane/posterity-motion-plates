# flames_v2 — painted-fire animation, v2 (Posterity engine R&D)

v1 (`flames_v1.py`, `README.md`, v1/v1b configs, `final/flames_v1_reel.mp4`) is untouched and still works.
v2 is a new module, `flames_v2.py`, with new `*_v2b.json` configs. `../smoke/smoke_v2.py` is only imported by path, never edited.

## What changed vs v1
1. **Minimum visible lick (small fires).** A smooth, vertical-only stretch term `D_lick = lgain·s(x,t)·Hb` is added to the
   v1 tongue displacement. `s` is low-frequency smooth noise with lateral wavelength ≥ `lick_lx_min` (60 px), so no squiggles.
   Its amplitude has a floor of `lick_min_phone` px **at phone scale** (360x640) and a cap of `s_max`. Gain is limited by
   `lick_tilt_max` and by a shared slope budget (`slope_total`) with the turbulence, so shear stays controlled. `map_x = X` still holds:
   no sway, no swivel.
2. **Small-fire flicker boost + self-pulse.** `flick_amp = amp·clip(sqrt(small_ref/hc),1,small_boost)`, plus an optional
   in-flame self-pulse (`flicker.self`) that scales with `small_ref/hc`. The clock is still (0.55, 1.3, 2.9) Hz: no strobing.
3. **`dim_warm`.** Pixels the tongue motion darkens take their chroma from a per-fire LUT of the plate's own flame colours.
   This removes the grey-blue holes in white cores (they were also present in v1).
4. **Sparks scale with fire size.** `spark_k = clip(hc/220, 0.4, 1)` sets size, count and rise, and sparks are drawn 2x supersampled.
   Wall torches and small fires get finer sparks.
5. **B13 spill pulled in.** Wall torches use spill 0.6, radius_k 0.8, max 110; the foreground torch uses 0.5, 0.55, 140.
6. **P05 + smoke_v2.** `configs/p05v2_smoke_bigfires_v2b.json` uses smoke_v2's own fire detection with min_area 2500,
   which gives 7 plumes on the big fronts only. It has no billows. Sky, sea, ships and glitter are the flames protects, with a 110 px feather.
7. **Phone-scale lick report.** `--phone-report OUT.json` measures, per fire at 360x640 and per 1 s window, the light-weighted
   peak-to-peak of the tongue tip. The tip is the cumulative-light quantile (0.12), with sub-pixel interpolation, so the metric is flicker-invariant.

## Run
```
PY=/workspace/mpvenv/bin/python
$PY flames_v2.py --config configs/b13_three_torches_flames_v2b.json --smoke ../smoke/configs/b13_three_torches.json --out poc/NEW.mp4
$PY flames_v2.py --config configs/p05v2_town_flames_v2b.json --smoke configs/p05v2_smoke_bigfires_v2b.json --out poc/NEW.mp4
$PY flames_v2.py --reel configs/reel_v2.json --out final/NEW.mp4
$PY flames_v2.py --config CFG [--smoke SCFG] --proof proofs/     # 0-px zero-motion proof (refuses to overwrite)
$PY flames_v2.py --config CFG --stats | --phone-report OUT.json | --stills DIR --times 1 3
```
ffmpeg is always run with `-n`, so it never overwrites.

## Reel
`final/flames_v2_reel.mp4`: 1080x1920, 30 fps, 510 frames, crf 22. Hard cuts:
B13 flames+smoke 7 s → P05 v2 flames+smoke 7 s → B10 cresset hold @1.0 s (1.5 s) → hold @2.5 s (1.5 s).

## Proofs (proofs/, all pass: 0 px changed outside allowed zones, 0 in protects and guards; 15 frames over 7 s)
- proof_b13_three_torches_flames_v2b.json, proof_b13_three_torches_flames_v2b_with_smoke.json (edward_face, guard faces 0)
- proof_p05v2_town_flames_v2b.json, proof_p05v2_town_flames_v2b_with_smoke.json (horizon_line, sea_open, sky, shore_glitter 0)
- proof_b10_cresset_flames_v2b.json (kent_face, gaoler 0)
- stats_*_flames_v2b.json, phone_*_flames_v2b.json (+ phone_*_v1b_equiv_baseline.json = same configs with lick 0, no boost),
  reel_v2_phone_stats.json, stills_v2/

## Known limits (honest)
The tiny P05 fires (window glows and distant points ≤ ~6 phone px tall: #15, #17, #19, #22, #23, #24, plus #10/#11) read as
flicker or twinkle, not as tongues. #6 (beach fire by the ships) is ~70 % under the sea protect, so it can only flicker.
Pushing those harder would break the swing and no-squiggle rules, or move protected pixels.
