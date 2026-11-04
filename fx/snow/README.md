# snow_v1 — subtle painterly snowfall over a still winter plate (R&D, 2026-10-31)

Variant of the locked `engine-rnd/dust/dust_v1.py`. Matte-only, screen-space flakes over the house push.
Nothing displaces; every keep-out pixel (faces, crowd heads, torches, brazier, interiors) is reset to the
pushed plate -> 0 px changed (proved). Plates: Báthory v2 **B11, B12, B17**.
B10 was on the first list, but the owner replaced its plate with an interior and ruled B10 flat + candle + dust
with **no snow**. So B10 has no preset and is not in the reel.

## Use
    P=/workspace/mpvenv/bin/python
    $P snow_v1.py presets                                   # print merged presets
    $P snow_v1.py render  b11 out.mp4 [--seconds 4] [--size 540x960] [--crf 20]
    $P snow_v1.py reel    final/snow_v1_reel.mp4 [--presets b11,b12,b17] [--seconds 4]
    $P snow_v1.py sheet   final/snow_v1_contact_sheet.png [--t 2.0]
    $P snow_v1.py proof   b11 proofs/proof_b11.json         # keep-out 0 px, outside-matte 0 px, determinism, guardrail
    $P snow_v1.py stats   b11 proofs/stats_b11.json         # flakes on screen, phone 360x640 pop/flicker numbers
    $P snow_v1.py overlay b11 proofs/overlay_b11.png        # plate | tier mattes + keep-out | depth
A preset can also be a JSON file `{"base": "b11", ...overrides}` (tier dicts merge per key).
All outputs refuse to overwrite. Every render runs motion/guardrails.py check_shot (refuse mode).
Each preset pins its plate md5; if the plate is replaced, the module refuses, because the hand masks belong to that image.

## Model
- **Camera:** the house StablePush (smoothstep 1.00->1.06, cover-fit 1080x1920, the same maths as flames_v3.push_frame).
  The snow is composited **after** the push, in screen space, so flakes never zoom. Only the static mattes and the colour map are warped with the push.
  Peak density is 1.219 output px per source px (limit 1.5).
- **Tiers** far / mid / near. Nearer flakes are bigger, softer, faster and sway more. Each flake is a Gaussian dab, slightly tall (sy = 1.12 sx).
  Defaults (output px, px/s): far sigma 1.2–1.6, speed 30–42, sway 4–8, opacity .50 | mid 1.9–2.5, 52–72, 8–14, .58 | near 3.6–5.0, 88–120, 14–24, .55.
- **Motion:** each flake falls at a constant speed, plus per-plate wind and a 2-sine lateral sway (0.07–0.22 Hz) with a small flutter.
  Positions are analytic, p(t + 60 s pre-roll), so the motion is seeded, deterministic, and already moving at frame 0. Flakes wrap only off-screen.
- **No pops:** each flake has its own life envelope, (0.5-0.5cos)^0.7 over 6–14 s, so it fades in and out in the air.
  All matte edges are feathered, and the depth gate is blurred (gate_blur 6 px), so a flake dissolves where it goes behind something.
- **Colour from the plate's light:** snow_white is the mean of the plate's bright, low-saturation pixels (times color_gain).
  A heavily blurred plate gives the local ambient light, which lifts and tints each flake (warm near fire, blue-grey in night sky).
  Far flakes are pulled further toward the ambient colour (aerial perspective).
- **Occlusion:** Depth Anything V2 Small (depth_v1's model, read-only; maps cached in cache/) gives the plate depth.
  A tier is visible only where the painted surface is farther away than the tier, so far and mid flakes pass behind figures, walls and the crag.

## Matte approach (faces / indoors / settled snow)
- **Faces:** YuNet (OpenCV zoo, `models/face_detection_yunet_2023mar.onnx`, score >= 0.6) auto-detects faces.
  Each box is padded for hats and scarves (x .6, top .9, bottom .5), and the presets add hand boxes.
  B17 also has a hand-drawn **crowd-heads band**, because YuNet misses heads seen from behind or in profile.
  These areas get a 40 px feathered fade, then a hard reset to the plate, so 0 px change.
- **Indoors no snow:** `interior` polygons (the B17 lit doorway with the clerk and candle) are reset to the plate.
  None of the three plates is an interior.
- **Light sources:** `keepout` polygons cover the B12 torch procession and the B17 brazier (flakes don't cross flames).
- **Settled snow stays still:** there is no ground or sheet layer (unlike dust_v1).
  `land` polygons fade every tier to 0 over a 60–80 px ramp *above* the ground line, so flakes "settle" and vanish.
  Nothing moves on the snow-covered ground. There is no water in these plates.

## Presets (current)
| preset | plate | seed | push centre | wind | flakes far/mid/near (n) | keep-out | on screen, mean (min–max) |
|---|---|---|---|---|---|---|---|
| b11 | b11_bytca_door_shut.png | 1111 | .60,.45 | -4 | 130/65/22 | none (no people); land y≈1035–1095 | 107 (97–118): 65/31/11 |
| b12 | b12_taken_up_to_fortress.png | 1212 | .50,.38 | +6 | 120 (depth .35)/55 (.6)/18; color_gain 1.6 (night) | torch procession box; land y≈1215–1240 | 92 (87–99): 58/26/9 |
| b17 | b17_secondhand_witnesses.png | 1717 | .40,.40 | -4 | 130/75/26 | 12 YuNet faces + crowd-heads band, brazier, lit doorway (interior); land left street | 59 (51–70): 29/21/10 |
All presets use push 1.00->1.06, 4 s, 30 fps, CRF 20 and 1080x1920.

## Proofs (proofs/)
- proof_*.json: at 6 times, 0 keep-out px and 0 outside-matte px changed. Two instances give identical frame md5s (deterministic). Guardrails ok.
- stats_*.json (phone 360x640): the per-flake visible-alpha step per frame is p99 0.015–0.029.
  The max is 0.14–0.17, and those are only flakes sliding in across the top or side frame edge over 2–3 frames.
  Interior pops were diagnosed and removed: a hard land edge and unblurred depth-gate silhouettes caused them.
  Whole-frame 1 s swing <= 0.46 %; energy above 5 Hz <= 0.03.
- overlay_*.png (540x960): plate | tier mattes (R far, G mid, B near) + keep-out (magenta) | depth.

## Outputs
final/snow_v1_reel.mp4: B11, B12, B17 at 4 s each (12 s), H.264 CRF 20, 30 fps, 1080x1920.
final/snow_v1_contact_sheet.png: one still per plate at t = 2 s.

## Known limits
- B11 already has a few painted static flakes. The moving snow sits over them, and they read as settled flakes in the air (acceptable, but noted).
- B12 is dark. Flakes are lifted with color_gain 1.6 so they read on a phone; in the torch box there are none.
- B17: the crowd fills the right half and is all keep-out, so the snow lives in the sky, the facade, the left street and the gaps.
  Its density is the lowest (about 59 on screen).
- Hand-drawn polygons are tied to the pinned plate md5. Redraw them if a plate is redone.
- Flakes slightly smaller than 1 phone pixel twinkle as they cross pixel edges (pop12 counter 13–50 px per frame). This is motion, not spawns.
