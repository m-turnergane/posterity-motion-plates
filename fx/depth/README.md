# depth_v1: 2.5D depth layers and restrained camera moves from one painted plate (R&D, 2026-10-30)

A plate is split into 2 rigid layers (near/subject over far). Each layer is a flat premultiplied RGBA card.

- **One warp per card per frame.** Each frame, every card is resampled exactly once with Lanczos4, using one uniform-scale + translate matrix. There is no rotation, shear, mesh, optical flow or per-pixel displacement. Faces, hands, text, water and land can only move rigidly with their layer.
- **Everything is folded into that matrix:** push 1.00→1.06, lateral drift / orbit-like pivot drift, and cover-fit framing.
- **No push on the composite.** Cards are composited far→near.

## Use
    /workspace/mpvenv/bin/python depth_v1.py render  configs/<cfg>.json out.mp4 [--size 540x960] [--seconds 6] [--crf 25]
    /workspace/mpvenv/bin/python depth_v1.py reel    configs/reel_9x16.json final/depth_v1_reel_9x16.mp4
    /workspace/mpvenv/bin/python depth_v1.py proof   configs/<cfg>.json proofs/proof_<cfg>.json
    /workspace/mpvenv/bin/python depth_v1.py stats   configs/<cfg>.json proofs/stats_<cfg>.json
    /workspace/mpvenv/bin/python depth_v1.py maxgrab configs/<cfg>.json grab.png [--size WxH]   # max offset | revealed (magenta) | fill crops
    /workspace/mpvenv/bin/python depth_v1.py layers  configs/<cfg>.json sheet.png                # plate | depth | mattes | filled far card
    /workspace/mpvenv/bin/python tests/test_depth_v1.py proofs/test_depth_v1.json

- All outputs refuse to overwrite.
- render/reel call `motion/guardrails.check_crop_zoom` in refuse mode. That call includes `check_pixel_density`: max 1.5 output px per source px at peak push × overscan.
- proof records the same check in warn mode, and the proof `pass` fails if density fails.

## Model
- **Mattes ("hybrid", default).**
  - Membership comes from a depth band (`depth_min`): Depth Anything V2 Small ONNX on CPU, about 1 s per plate, cached in `cache/`.
  - Hand fixes refine it: `region` (which blobs count), `polys` (force include), `exclude`, `seams` and `protect` (rigidity check boxes).
  - An edge-aware guided filter (guide = plate) then gives a soft alpha of 1–3 px on the painted edge.
  - `mode: "poly"` is the hand-mask baseline. See DEPTH_MODEL_EVAL.md, which keeps the model.
- **Edge un-mixing.** F = (C − (1−a)·B)/a against the farther composite, so moving edges carry no background fringe (no halo). At zero motion the composite reproduces the plate (recon PSNR 46–54 dB).
- **Disocclusion.**
  - Each card is pre-extended under nearer layers by R ≥ max relative offset + margin.
  - The extension is filled from that card's own pixels only: TELEA inpaint with every non-own pixel masked, plus matched grain. A nearer figure's colours can never leak into the fill.
  - Fill is computed once per plate before rendering, so nothing is synthesised per frame.
- **Seams.** These are cuts through continuous surfaces (floors, stairs). They get a wide alpha ramp, and the far card keeps the TRUE plate there instead of inpaint. A floor bends gently across the band instead of tearing.
- **Camera.**
  - Per layer: `z = 1 + ((z0−1) + (z1−z0)·e)·push_gain` and `tx = travel·(e−0.5)·(parallax−pivot)·dir`.
  - `pivot 1.0` holds the near layer and swings the far one, which reads as a small orbit around the subject. `pivot 0.5` splits the motion.
  - `e = smooth_progress`: 0.5 s ease-in and ease-out, then constant velocity.
  - Overscan is the smallest zoom that keeps every card covering the frame at every e (bisection over 181 samples).

## Composing with locked effects (smoke_v2, torch_v1c, water_v1, dust_v1)
`DepthShot.frame(e, size, o, plate_fx=None, layer_fx=None, screen_fx=None, t=0.0)`
- `plate_fx(t)` is a plate-space RGB float frame [0,1] of a locked effect, rendered with **its own camera disabled** (push [1,1], or call the effect's frame function rather than its render).
  - depth_v1 splits the delta (fx − plate) across the layers by their exclusive coverage. The delta rides each layer's single warp, so the effect moves with the surface it sits on. Never run the effect's own push on top.
  - Test with dust_v1: `plate_fx = lambda t: DustShot(cfg).frame(t)/255`, where cfg = `configs/compose_b01_dust_test.json`.
  - The test traps dust's `F3.push_frame`, which is called 0 times.
- `layer_fx[name](t)` is a plate-space premultiplied RGBA overlay that is added to one card before its warp. Use it for an effect that belongs to one depth, e.g. torch flames on a near wall.
- `screen_fx(img, t)` is screen-space post only: grain or grade. It must never contain a camera move or a resample.
- Water and smoke effects that animate pixels inside their own matte stay valid because the layer warp is rigid. Water still never "warps" from the depth engine itself.

## Rules (enforced or checked)
- One warp per layer per frame. Checked by WARP_LOG count in proof and test, plus a dot test: measured vs expected position err ≤0.016 px, while a double push would be 10–34 px off.
- Matrices are uniform scale + translate on all 180 frames.
- Parallax: relative far/near offset is 3.2–4.1 % of frame width. Pushes are 1.00→1.06, and the far card gets 0.3–0.4 of the push.
- Guardrails: crop zoom ≤1.5x and density ≤1.5 output px per source px. **Never upscale a plate to get an aspect.**
  - 941x1672 portrait plates pass at 9:16 (1.24–1.29) and fail as 16:9 band crops (2.2).
  - A 1280x720 plate fails at 1920x1080 (1.59–1.67).
- Rigidity: each `protect` box must be 100 % inside one layer (in_layer ≥0.97 with α=1). It must also match the plate moved by that layer's matrix (NCC ≥0.9999) at frames 0/90/179.
- Revealed areas at max offset must have 0 holes.

## Cases (current; all proofs PASS except the documented density failure)
| config | plate | aspect | density | rel. parallax | revealed@max | recon |
|---|---|---|---|---|---|---|
| b05_landing_push_v1 | standalones/edward-ii/plates-v3b/b05_landing_1326_kent_OWNER.png | 9:16 | 1.237 | 3.74 % | 0.39 %, strip 10.6 px | 45.8 dB |
| b10_corfe_letter_drift_v1 | …/b10_corfe_kent_hands_letter_OWNER.png | 9:16 | 1.244 | 3.62 % | 1.08 %, 14.6 px | 46.8 dB |
| b01_gloucester_kent_drift_v1 | …/b01_gloucester_funeral_wide_kent_OWNER.png | 9:16 | 1.286 | 4.06 % | 0.77 %, 14.3 px | 50.0 dB |
| p10_escape_drift_v1 | …/p10_escape_servant_clothes_twilight_OWNER.png | 9:16 | 1.237 | 3.65 % | 0.63 %, 9.4 px | 53.7 dB |
| hubert_fire_arch_push_v1 | day3/nero-fiddle/assets/pd_hubert_robert_fire.jpg (Hubert Robert, public domain, 1920x1543) | 16:9 | 1.100 | 3.41 % | 1.73 %, 18.4 px | 51.2 dB |
| b10_corfe_letter_drift_HANDPOLY_eval | same as b10, hand polys only | 9:16 | 1.244 | 3.63 % | 0.95 % | 48.0 dB (eval baseline) |
| nero_balcony_push_v1 | day3/nero-fiddle/assets/art_nero_lyre_balcony_fire_v2.png (1280x720) | 16:9 | **1.672 FAIL** | n/a | 2.44 % | 47.4 dB (not used) |

- **Poynter's "The Catapult" (1433x1200)** passes density (1.42) but was rejected for 16:9. It is a flat crowd with no clean depth gap, a baked inscription and a museum watermark.
- **Reels:**
  - `configs/reel_9x16.json`: b05, b10, b01, p10, 6 s each, hard cuts, crf 25.
  - `configs/reel_16x9_native.json`: Hubert Robert only, the only native-landscape plate that passes density and has a real depth gap.
- **Effects test config:** `configs/compose_b01_dust_test.json`.

## Proofs (proofs/)
- `proof_*.json`:
  - guardrail and density
  - single_transform: warp count, dot test, uniform matrices
  - disocclusion at e=0 and e=1: revealed px, strip width, holes, hf texture ratio of the fill vs its ring
  - rigidity per protect box
  - recon_native: zero-motion composite vs plate
- `stats_*.json`: phone 360x640 (or 640x360) layer travel, relative parallax in phone px total and in the first 1 s, max speed, jitter RMS, and velocity energy above 5 Hz.
- `maxgrab_*.jpg`: frame at max offset | revealed px in magenta | fill close-ups.
- `test_depth_v1.json`:
  - one warp per layer-frame with all three fx hooks active, and locked-effect camera calls = 0
  - identity plate_fx diff 0
  - fx delta rides the layer matrix (err 0.0)
  - dot test
  - push folded: far 1.0→1.024, near 1.0→1.06
- `proof_nero_balcony_push_v1_DENSITY_FAIL.json`: the documented refusal.

## Known limits / critique
- **Fill.** Fill in revealed strips (10–18 px at 1080 wide) is TELEA plus grain. Its texture ratio is 0.49–0.86 of the surrounding ring, so the fill is smoother and slightly smeared. It is visible at max offset on a still frame, but hard to spot in motion on a phone.
- **Edges.** Un-mixed edges have small reconstruction errors at a few edge pixels. Max abs is 82–212/255 on single pixels; px≥4/255 is 0.2–1.4 %. Very thin bright rims can get lost (the Hubert statue rim needed a hand poly).
- **Seams.** A seam blends two shifted copies of the floor, so floors under seams go slightly soft at max offset (b01, b10).
- **Phone read.** Total relative parallax is 13–15 phone px for 9:16 and 22 for 16:9. The first second gives only 2–3 phone px because of the 0.5 s ease-in, so depth reads at about 1–2 s, not within 1 s. A shorter ease-in would read sooner at the cost of a harder start.
- **Model failures.** Depth gets a head and body in different bands (b05) and thin bright rims or staffs against bright sky (Hubert). It cuts continuous floors. Each needed one hand fix, and the `protect` rigidity proof catches the head/body case.
- **Layers.** Only 2 layers per shot. A third (mid) layer is supported by the code path but not exercised in these cases.
- **16:9 is blocked by plate resolution.** Every Edward II plate is 941x1672 portrait. A 16:9 Edward II reel needs native landscape plates ≥1357x763, or portrait plates ≥1380x2451 for band crops.
