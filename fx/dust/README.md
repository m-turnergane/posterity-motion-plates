# dust_v1 — motes/haze in light shafts + ground dust (R&D, 2026-10-30)

Matte-only, additive/alpha dust over a still plate. Nothing displaces; every pixel outside the dust zones
(faces, hands, text, land/coast, lanterns, walls) is reset to the plate -> 0 px changed (proved).

## Use
    /workspace/mpvenv/bin/python dust_v1.py render  configs/<cfg>.json out.mp4 [--size 540x960] [--seconds 6]
    /workspace/mpvenv/bin/python dust_v1.py proof   configs/<cfg>.json proofs/proof_<cfg>.json
    /workspace/mpvenv/bin/python dust_v1.py stats   configs/<cfg>.json proofs/stats_<cfg>.json
    /workspace/mpvenv/bin/python dust_v1.py grab    configs/<cfg>.json grab.png --t 3     # phone before|after|diff x4
    /workspace/mpvenv/bin/python dust_v1.py reel    configs/reel_v1.json final/dust_v1_reel.mp4
All outputs refuse to overwrite. render/reel call motion/guardrails.py (refuse mode: zoom <= 1.5x).

## Model
- Zone matte M = poly(feathered) x smoothstep(lum_lo, lum_hi, blurred plate luma)^gamma x keepout — light shafts key themselves on brightness, so motes are brighter where the light is.
- motes: analytic drift p0 + v(t + 40 s pre-roll) + slow 2-sine turbulence, depth sets size/speed/brightness, each mote has a smooth (0.5-0.5cos)^0.8 life of 5–12 s (no pops), wrap only in a zero-M margin (no visible loop).
- haze: fixed-position soft blobs inside M breathing at <= 0.15 Hz (no moving light gradients).
- sheets (ground): two large periodic noise textures advected by wind, alpha-blended toward a dust colour inside M; periods >> drift distance over a shot.
- compose: sheets alpha -> motes/haze screen -> matte -> protect reset to plate.

## Cases (current)
| config | plate | camera |
|---|---|---|
| t1a_tomb_shaft_v1c | micro-anomaly/tamerlane/plates/seq1a.png | push 1.00->1.06 |
| c6_citadel_ground_dust_v1b | day8/chan-chan-chimu/assets/owner/seq6_emptied_citadel_OWNER.png | fixed |
| t6_oculus_stair_shaft_v1c | micro-anomaly/tamerlane/plates/seq6.png | push 1.00->1.06 |
Older configs (t1a v1/v1b, t6 v1/v1b, c6 v1) are kept as history; poc/ has 540x960 renders of each.

## Proofs (proofs/)
proof_*.json: ±24 impulse lattice -> leaked 0 px; protect_changed_px 0 at 7 times; guardrail ok. stats_*.json: phone 360x640 numbers.
decoded_reel_phone_stats_v1b.json is valid; decoded_reel_phone_stats_v1.json is a truncated failed write (float32 json error) — ignore.

## Known limits
- t6: motes over bright, busy stone barely read on a phone; weakest case.
- c6: the ground dust is subtle in a still frame and reads mainly as motion (drift); it changes ground pixels inside the matte by design (no displacement).
- Small sharp motes are sub-pixel at phone size; the "pop" counter (28–51 phone px per frame jumping >=12) is motes crossing pixel edges, not spawns — it shows as a faint twinkle.
- Hard-edged polys: matte edges are feathered but the zone shape is hand-drawn.
