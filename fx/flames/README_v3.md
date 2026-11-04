# Posterity FLAMES — v3 (P05 sky billow + perceptible local light spill)

v3 = `flames_v3.py` (new file; v1/v2 code, configs, READMEs and reels untouched). With v2 configs it renders
bit-identically to `flames_v2.py` (scratch/v2/regress.py: max diff 0 on B13/P05/B10 v2b). Nothing under
`engine-rnd/smoke/` was edited; `smoke_v2.py` (md5 80bb28695757f7568b005e8ba8327bde) is imported by path.

Reel: `final/flames_v3_reel.mp4` from `configs/reel_v3.json`. It has the v2 structure: B13 flames + smoke (7 s), then
P05 flames + big-fire smoke + **sky billow** (7 s), then the B10 cresset holds at t=1.0 and t=2.5 (1.5 s each, no push).
Usage: `python flames_v3.py --reel configs/reel_v3.json --out <new.mp4>` (it refuses to overwrite).

## Fix 1: P05 sky billow (painted plumes)
* `configs/p05v2_sky_billow_v3.json` is a smoke_v2 config with **billows only** (no emitters or fires; asserted). It uses the
  locked P06 doorway-plumes approach: a luma/saturation key plus a `dark_rel` local-darkness key, then grow, feather and
  edge-feather to make the smoke matte, and a two-phase flow-map rise with a curl warp *strictly inside the matte*.
* The P05 plumes are red-lit (saturation about 0.5–0.65), so the key is luma [0, 0.30], sat_max 0.72, soft 0.045,
  dark_rel [-0.04, 0.0] (rel_sigma 60), grow 6, feather 6, edge_feather 12. Motion: amp 14, rise 26 px/s, period 2.4,
  scale 120. The bright orange sky ribbons fall outside the matte and stay at 0 px.
* Region: the sky above the skyline (lowest matte row y=503). Protect: the sea, ships, sun and horizon glitter, the shore
  glitter, and the land below the skyline. Matte overlap with the sea, ships, glitter, land and the flame/spill/spark
  zones is **0 px** (`proofs/v3/billow_matte_overlap_p05_v3.json`).
* Order: billow on the plate, then the flames (so tongues sit over the moving sky), then the emitter smoke on top.
* `configs/p05v2_town_flames_v3.json` is v2b plus `billow_guards_ok: ["sky"]`. The flames' "sky" guard box necessarily
  contains the plumes, so the proof checks it *outside the matte* (0) and reports the overlap (441,817 px).
* Phone visibility (`proofs/v3/billow_p05_v3.json`, 360x640): 45,277 matte px (19.7% of the frame). 89% of matte px
  change by ≥6 levels within every 1 s window (min 88.5%). Farneback flow over 1 s: median 2.6 phone px, p90 5.3.
* Not billowed: the low plume roots right above the town fires (they fall inside the flame/spill zones, which are kept
  disjoint) and the left smoke column over land and fires #3/#4 (land gets zero warp; the v2b emitter smoke rises there).

## Fix 2: local light spill (B13 torches, B10 cresset)
Gain `G = 1 + clip(amp·clock(t), ±max_gain)·fall·tint`. Falloff `fall = exp(-(d/r)^p)` with p=2 (B13) or p=3 (B10),
radius 80–175 px plate. The gain is multiplied into the plate colours, so it changes **brightness and colour only**.
`skip_flame` removes the flame body and glow from the gain, so the whole frame does not pump. `through_protect: true`
lets light reach the face protects, which still block *motion*; `spill_protect` polygons would block light as well.

### Light vs motion in the proofs (proof_v3)
* `protect_motion_max_diff` / `guards_motion_max_diff`: the frame **with the spill off** vs the plate. These must be 0
  (no displacement). All are 0.
* `protect_light_residual_max` / `guards_light_residual_max`: the full frame vs `light_only(t)` (the plate × the gain
  map alone). These must be 0, which proves that every change on a face is a pure per-pixel gain and that nothing moved.
  All are 0.
* `protect_light_change_max` / `guards_light_change_max` report how much light landed there (e.g. B13 guard_face_l 98
  levels at max, gaoler 63). That is allowed.
* `guards_shift_px_max` (phase correlation) shows ≈0.5 px on lit faces. This is an artefact of a brightness *gradient*
  across the box (phase correlation is not gain-invariant). The motion and light residuals above are exactly 0.
* All six proofs pass, with `changed_px_outside_allowed` = 0 and flames-only `outside_flame_zone` = 0:
  proof_b13_three_torches_flames_v3[_with_smoke], proof_b10_cresset_flames_v3, proof_p05v2_town_flames_v3[_with_smoke][_billow].

### Spill swing at phone scale (360x640, flames only, sparks off, 1 s windows; median %, min %)
Before = v2b, after = v3, same surfaces (configs/*_spill_surfaces_v3b.json):

| B13 surface | v2b | v3 |
|---|---|---|
| left_doorframe_wall (wall) | 3.37 / 0.79 | **18.06 / 10.94** |
| right_door_wall (wall) | 1.51 / 0.34 | **16.21 / 7.71** |
| left_stone_wall | 0.38 | 5.13 |
| stairs L / R of fore torch | 3.74 / 3.65 | **10.90 / 10.34** |
| guard_face_l (face) | 0.00 | **13.41 / 8.65** |
| guard_face_r (face) | 0.00 | **10.36 / 4.56** |
| torch_holder_l_face (face) | 0.00 | **17.33 / 10.47** |
| back_guard_r_face_mail (face+mail) | 1.96 | **18.08 / 9.49** |
| guard_l_coif_chainmail | 0.02 | 6.67 / 4.16 |
| guard_r_coif_chainmail | 0.00 | 8.99 / 3.39 |
| edward_face / guard arm chainmail / fore soldier chainmail | 0–0.3 | 0.13 / 0.4–0.55 / 0.44 (out of reach by design) |
| whole frame (flames) | 4.92 | 5.77 (max step 0.45%, >5 Hz energy 0.002) |

| B10 surface | v2b | v3 |
|---|---|---|
| wall_above_cresset | 4.67 | **17.66 / 6.16** |
| pillar_left_of_cresset | 4.91 | **18.63 / 6.90** |
| wall_right_of_cresset | 4.35 | **15.94 / 5.22** |
| pillar_below_cresset | 2.95 | **10.68 / 3.60** |
| gaoler_face | 0.00 | **12.69 / 4.34** |
| gaoler_shoulder_chainmail | 0.00 | 6.31 / 1.93 |
| gaoler_chainmail (lower) / kent_face | 0.01 / 0.00 | 0.40 / 0.08 (out of reach) |
| whole frame | 3.10 | 6.39 (max step 0.53%) |

Composite whole-frame swing: B13 + smoke 5.44% (max step 0.42%); P05 + smoke + billow 1.15%. Decoded reel at
360x640 (incl. push): B13 7.09% (max step 0.96%), P05 1.83%. v2 reel for comparison: 6.31% / 1.84%. All within ~8%.
Spectra peak at 0.14–0.29 Hz with ≈0 energy above 5 Hz, so there is no strobing.

B10 shots in the reel are **holds** (frozen frames), so the cresset flicker cannot be seen there. It is shown in
`proofs/v3/b10_cresset_v3_360.mp4` (360x640, 6 s, no push).

## Unchanged by design
Tiny far P05 fires keep their twinkle (not faked). The sea, ships, horizon, faces and land get zero warp. Tongues move
vertically only. No vignette, letterbox, watermark or text.
