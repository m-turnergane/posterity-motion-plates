# Báthory Rough v1: QC note (Atelier build, 2026-10-31)

**Render:** `v2/renders/bathory_rough_v1.mp4`
- md5 `e9d76b347c8a82970b290ec318630070`
- 87.000 s, 2610 frames, 1080x1920, 30 fps, H.264 yuv420p (crf16), AAC 256k 48 kHz stereo
- **Loudness:** -14.2 LUFS integrated, -1.7 dBTP, LRA 4.1 LU (measured on the final mp4)
- VO over the ducked bed: 13.0 LU (stems: VO -30.4 / bed -43.4 LUFS, before master gain)
- **Ducking:** sidechaincompress with attack 15 ms, ratio 2.5, release 700 ms, knee 4
- **Bed:** Ignosi from track 0:31.000, audible from frame 1, 20 ms de-click fade-in
- **Outro fade:** constant 16 dB/s from 83.2 s (-60 dB at 86.95 s), applied in dB space
- **Build tools:** `build_bathory_rough_v1.py` (CLI: still, clip, captions, mix, final, sheet). Per-beat config and measurements are in `bathory_rough_v1_beat_log.json`; captions are in `bathory_rough_v1_captions.ass`.
- **Contact sheet:** `bathory_rough_v1_contact_sheet.jpg`, one mid-frame per beat, 24 beats.

## House rules
- **Push:** 1.00→1.06 on every flat, map and archival beat. Depth beats push the near layer 1.00→1.06 and the far layer at gain 0.4. B13a/B13b split the push 1.0→1.035→1.06 across the cut.
- **Worst pixel density:**
  - Archival B02 and B19b: **1.410**
  - Best plate-based beat: B09 at 1.249
  - All beats ≤1.5 ✓
- **Arrest timing:** B04, "armed men entered her manor", runs 9.45–12.08 s, so the arrest lands by 12.2 s ✓. The shortest shot is B14 at 1.77 s (floor is 1.5 s ✓).
- **Captions:** 38 chunks, ≤7 words, ≤24 characters per line, two lines maximum. Breaks fall at sentences and cuts. An assert checks that the caption text equals the VO words exactly ✓. Style is the Edward ASS style: DejaVu Sans 54, MarginV 400, IG-safe.
- **Clean frame:** no vignette, letterbox, watermark, TEMP mark or LEGEND/DOCUMENTED label.
- **No motion on faces, water or land:** faces are excluded from relighting, held rigid in the depth near layer and protected from dust and snow. Snow uses `land_gain 0`.

## Per-beat effects
Flicker numbers are peak-to-peak % of mean luma, given as whole frame / near the source / maximum per-frame step.

| Beat | Treatment |
|---|---|
| B01a | **FLAT** (see the B01a choice below). torch_v1c on the left brazier (0,870)-(215,1360): pulse 0.344, 9.9 / 19.4 / 3.1. Faces excluded from relight. Cool dust motes. |
| B01b | fx_candle on the left candle (72,405)-(122,530), which sits at about 24–32% of plate height: 14.6 / 31.4 / 4.1. Wick smoke 0.35. Top-right tapestry desaturated and darkened. |
| B02 | Archival portrait (Commons), push only. |
| B03 | Map (details below). |
| B04 | depth_v1: near 27% of the frame (riders and ground), seams kept clear of the boots. Torch 8.4 / 27.4 / 3.1. Windows at amp 0.7. Grey torch smoke 0.4. |
| B05 | Auto candles 12.5 / 35.5 / 4.5. Off-screen torch spill (spill only) 1.5 / 13.8 / 3.0. Wick smoke. Tapestry painterly darkened. |
| B06 | Sun-band dust; people and roofs protected. |
| B07 | Candle 12.1 / 35.3 / 4.7, plus a wisp. |
| B08 | Candle 9.7 / 35.3 / 5.2, plus a wisp. |
| B09 | depth_v1, near 33%. Candles 6.6 / 36.8 / 4.1. Doorway torches 4.7 / 21.9 / **3.2**, just over the 3.1 limit (see failures). |
| B10 (new) | FLAT + fx_candle 14.4 / 32.0 / 3.8 + window-shaft dust; faces protected. |
| B11 (new) | depth_v1 reusing cache `da2s_32aa34…` at D≥0.18 inside the carriers-and-bier region, plus the ground below y≈1230; arcade is the far layer; near is 38%. Torch on the brazier [85,985]–[295,1262]: 12.3 / 22.6 / 3.0. snow_v1b `b11`, composited after the push using the near-layer matrix. |
| B12 | 4 path torches located automatically: (381,691), (462,664), (522,637), (590,599). Whole 1.9 (distant), local 15.6, step 3.0. Window at amp 0.7, radius_mult 0.5. Torch smoke 0.35 ×4. snow_v1b `b12`. |
| B13a | Poly depth: the wall and leaves are near, the gap is far. The chamber candle is spill-only in the gap: 14.2 / 22.4 / 3.1. |
| B13b | Hard cut, continuing B13a's final matrix (zoom 1.035→1.06, ease-out). |
| B14 | Window-shaft dust; her head is protected. |
| B15 | Candle 8.2 / 28.3 / 5.9. Tapestry desaturated and darkened. |
| B16 | Hearth torch with faces excluded: 11.8 / 22.5 / 3.1. Low hearth smoke 0.35. |
| B17 | Brazier torch 9.6 / 20.8 / 3.0. Smoke 0.4. Crest and banner desaturated and darkened. snow_v1b `b17`. |
| B18 | Wall banner desaturated and darkened. Wick smoke. Shaft dust. |
| B19a | Reuses the new B11 plate, flat, centre (0.4,0.62). Torch as in B11. Snow uses the b11 preset with seed 1912. |
| B19b | Archival portrait, push only, centre (0.5,0.36). |
| B20 | depth_v1, near 64%. Anchor (0.5,0.35), slightly higher than the plan's 0.40 so it sits on her eyes. Candle at **half** the lock pulse: 7.9 / 21.7 / 2.9. |
| Outro | Air-band dust; the rooks, the baked-in text and the castle are protected. |

## B01a choice: FLAT
I chose flat over depth for three reasons:
- the thin sword would tear at a layer boundary
- the brazier flames cross the near/far line
- the shot is only 3.0 s, so parallax adds little

## B03 map
- **Base:** the clean plate, Lanczos 2x, registered (from earlier: PASS, 29/29 control points).
- **Labels (LABEL-PLAN_v2b):**
  - "Csejte, today Čachtice, Slovakia" in IM Fell SC 51, on one line
  - "Bytča" in SC 51
  - "Váh" in IM Fell French Canon Italic 38, rotated 7° at alpha 0.60
- **Váh thinning:** 2824 river pixels inside the Csejte label zone, blended 60% toward an inpaint.
- **Ink stamps:**
  - Csejte at 0.15–0.60 s
  - Bytča at 0.55–1.00 s
  - Each scales 1.35→1.0 with a fade, under 0.6 s ✓
- **Push and route:** 1.06 push, no route.
- **Residuals:** the visual check is clean; label edges and halos are crisp at 1080 wide.

## B13 cut
- **Registration:** b→a translation (-0.423, -0.764) plate px, i.e. **0.51 / 0.93 output px** (≤2 px ✓).
- **Sign check:** I diffed the cut frames outside the door region. Mean |ΔY| was 10.41 for sign -1, 10.82 for +1 and 10.56 with no shift. Sign -1 was chosen. The margin is small because the two plates' lighting differs, but every option is under 2 px.
- **Impact:** hard cut at **46.267 s** (frame 1388) = **Ignosi 77.267 s** (window 76.9–77.3 ✓; 0.78 s clear of 76.49 ✓).
- **F7 door hit:** synthesised (pre-swing, wood-and-stone impact, short stone-room tail). It peaks about 4 dB over the VO RMS for 0.1 s.

## Heraldry
Treated with a soft, painterly blend of bilateral and Gaussian filtering at desat 0.7 and dark 0.6, feathered 26 px, on:
- B01b top-right tapestry
- B05 tapestry
- B15 tapestry
- B17 crest and banner
- B18 wall banner

Each now reads as a dim, muted cloth, not a legible coat of arms.

## Snow visibility
Visible flakes per frame (peak alpha × matte > 0.08), as min / mean / max:

| Beat | Flakes per frame | Near-tier mean |
|---|---|---|
| B11 | 180 / 192 / 208 | 26 |
| B12 | 144 / 154 / 160 | 20 |
| B17 | 87 / 104 / 117 | 16 |
| B19a | 186 / 200 / 212 | |

- I measured contrast on the output: about 100–140 flakes with ΔY > 12 per frame on B11/B12, and about 60 on B17.
- Snow is composited after the push in every case, and is visible in motion.
- **B17 is the lightest**, because the snow is against a bright wall and sky.
- I did not change the locked preset densities or opacities.

## Failures and judgment calls
1. **F7 is synthesised.** No library door SFX was available. F1–F6 and F8 from the cue sheet are omitted in this rough.
2. **B09 torch step** is 3.2%/frame, against a 3.1 limit. Its whole-frame flicker is only 4.7%. I'm flagging it rather than retuning.
3. **Low torch whole-frame flicker on some beats:**
   - B01a 9.9, B04 8.4, B17 9.6 (target 10–14)
   - B12 1.9 (distant torches) and B05 off-screen 1.5
   
   In each case the ≤3.1%/frame step is the binding limit. I kept the step limit rather than the whole-frame target.
4. **Outro:** the OWNER plate has the text "History remembers the victors. We remember the rest." baked in, so the burned caption "We remember the rest." duplicates it on screen. Captions follow VO word-for-word per the house rules. **Vellum's call** whether to drop the last two caption chunks over the outro.
5. **B13b's optional candle-line pulse** was skipped.
6. **B19a keeps the brazier torch**, so the reused plate isn't static.
7. **Plate texture:** a fine crackle/canvas texture is visible on B12 and B17 when zoomed in. It is in the source plates, not introduced by the build.
8. **B02 and B19b** use the same archival portrait. Its top-left inscription is part of the original painting.
9. **Credits** are not on screen; they go in the description per POST-PACK-v2.
