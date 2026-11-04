# QA: Björn ROUGH v4c (Tue 2026-11-03, EST)

This rough applies editor rulings (a)–(e) on top of v4b, and nothing else changes. All work ran on the box. No external calls were made and nothing was sent. v4b, v4, v2b, v2, p05_test_v1/v2, the plates and /workspace/posterity-motion-plates are all untouched (v4b md5 re-verified: e0c31c7f…).

## Deliverable
- `rough_v4/renders/bjorn_rough_v4c.mp4`, md5 **24bb62acc5a217eca01dcd515912873f**
  - H.264 High@5.0, 1080×1920, 30 fps, **3073 frames, 102.433 s**. This matches v4b.
  - Video time_base is 1/15360 and pts/durations are identical to v4b for every frame.
- **Audio:** the v4b AAC stream was stream-copied, and all 4803 packets are bit-identical to v4b (framemd5).
  - ebur128 on the mp4: **−13.9 LUFS integrated, LRA 2.6 LU, true peak −4.2 dBFS**, the same as v4b. PASS against the −14 LUFS target and the ≤ −1 dBTP limit.
- **Unchanged from v4b:** VO ff97caaa, score, captions (`bjorn_rough_v4b_captions.ass`, md5 37310099…), all durations, the title (31 %), and every shot except P05 and P17A. There is no vignette, letterbox, watermark or LEGEND tag.
- **Builders** (new; the v4b scripts are untouched):
  - `build/p05_rough_v4c.py` (md5 b007ebaa…), a copy of p05_rough_v4b.py with the rulings applied.
  - `build/p17a_v4c.py` (md5 d62fc5b2…), the proof treatment with a zero-warp matte.
- **Clips** (made with the v4b builder's exact clip step: rgb24 → x264 medium crf14):
  - `scratch/clips_v4c/P05.mp4` (84550cae…), from `scratch/p05_rough_v4c/p05_test_v4b_silent.mp4` (0ef2e259…, 315 f).
  - `scratch/clips_v4c/P17A.mp4` (a31b4e56…), from `scratch/p17a_v4c/p17a_v4c.mp4` (1d2e33ff…, 225 f).
  - Method check: the same step rebuilt from p17a_glints_only.mp4 reproduces clips_v4b/P17A.mp4 bit-for-bit (aa6b3e68…).
  - Concat list: `scratch/concat_v4c.txt`. It matches concat_v4b.txt except for the P05 and P17A lines.

## Segment re-encode and join
- **Re-encoded ranges:** the two closed-GOP ranges between v4b IDR keyframes were re-encoded with the v4b final settings (libx264 slow, crf 16, yuv420p, -r 30, `subtitles=` the same ASS, then trim).
  - **463–777** (P05, 15.433–25.933 s)
  - **2034–2427** (P16 + P17A, 67.800–80.933 s)
- **Stream-copied ranges** (v4b packets copied unchanged): 0–462, 778–2033 and 2428–3072. The parts were joined with the concat demuxer, `-c copy`.
- Every decoded frame was checked with framemd5 against v4b (3073 vs 3073):
  - **Changed frames: exactly 463–777 and 2034–2427.** All other frames are bit-identical to v4b.
  - 2034–2202 (P16 and the end of P15's GOP) has unchanged content, but it is a re-encode because the nearest IDR before P17A (2203) is frame 2034. It measures PSNR 47.3 dB vs v4b (Y 46.3, min 45.4), which is visually lossless.
  - The decoded re-encoded segments equal the standalone segment encodes (framemd5). A full decode runs with no errors.
- IDR keyframes in v4c: 0 82 163 347 463 713 778 913 981 1127 1223 1333 1459 1576 1714 1823 1916 2034 2203 2428 2654 2780 2938.

## (a) PROVENCE: moved west, between the lower Rhône and the Alps
- **Placement:** same font (IM Fell English SC), size 33, tracking 0 and ink treatment. The centre moved from ref (728,762) rot 22° to **(668,703) rot 75°**.
  - The label now reads upward along the east bank of the Rhône, starting at the Provence coast and rising toward the Alps.
  - Bbox (ref px): v4b [636,719 – 819,808] → v4c **[634,612 – 704,798]**.
  - The east edge (ref 704) is west of the Var/Nice (≈690–710). No ink is over Liguria or the Gulf of Genoa: the gulf apex is ≈(746,758).
  - It is 103.6 px from Luna (v4b: 0).
- **Why steep:** the land between the lower Rhône (ref x ≈600) and the Var is only ≈90 × 60 ref px, and the label is ≈180 px long. An obstacle search over rotations −80…85°, with route, ship path, swords, dots, other labels, land coverage and frame edges checked at every t, found no placement west of the Var at rotations <65°.
  - Candidates with an east edge ≤705 only occur at 70–85°. 75° was chosen for the best clearance while staying distinguishable from the Rhône label's 82°.
- **Clearances:** route points inside the bbox: 0 (v4b had 21). Ink to the nearest leg is 25.2 px, ink to the nearest dot or sword is 36.4 px, and the gap to the Rhône label is ≥55 ref px (the S8 leg runs between them). The ship clearance is ≥7 px for the whole shot.
- **Flag (editor's eye):** the upper ≈⅓ of the word ("NCE") sits over the orange-tinted region north of the Alps and crosses the Alpine band. This cannot be avoided at size 33 west of the Var.
  - The alternatives are a smaller size or two lines ("PRO-/VENCE"), and both are outside the ruling.
  - Historically, Charles of Provence's kingdom (855–863) did include the Viennois and Lyonnais, so a label running up the Rhône's east bank is defensible.
- Crops:
  - `qa_v4c/p05_provence_f775_v4b_vs_v4c.png`
  - `qa_v4c/p05_italy_arrival_f730_v4b_vs_v4c.png`
  - `qa_v4c/phone_{390,540}_t{3.4,10.4}_v4b_vs_v4c.png`

## (b) Ship, last leg: arrives at the Pisa dot on "Italy", then holds
- **Retime:** the S9 leg now runs to the coast at the Pisa dot (END_GAP 0; v4b stopped short). Its cosine ramps were shortened (RAMP2 0.22 s) so the longer leg stays under the speed cap.
  - Departure is word-locked as before: the Camargue sword is on "France" at 6.779 s and departure at 7.279 s.
  - The Spain/Strait and Mediterranean legs are unchanged.
- **Arrival = P05 local 8.892 s = P05 frame 267 = timeline frame 730 (24.333 s).** "Italy" onset is 24.325 s, so arrival is +8 ms, in the same frame. No arrival shift was needed (P05C_ARR_SHIFT = 0).
  - The ship holds at the Pisa dot to the end of the shot. The Pisa sword drops on arrival, the route completes solid to Pisa (reveal 0.15 s after arrival), and no Luna mark is drawn.
- **Peak ship speed: 228.1 frame px/s** at P05 frame 253 (p95 226.0). This is ≤240, PASS. The solver's segment-2 vmax is 217.6 ref px/s.
- Crops:
  - `qa_v4c/p05_italy_arrival_f730_v4b_vs_v4c.png` (v4b ship still at sea; v4c at the Pisa coast)
  - `qa_v4c/p05_v4c_arrival_strip_f722-738.png`
  - `qa_v4c/p05_pisa_hold_f745_v4b_vs_v4c.png`
  - `qa_v4c/p05_v4c_pisa_sword_f729_733_740_777_x2.png` (sword drops at the dot beside the bow from f733, then holds)

## (c) Strait of Gibraltar: on the water
- **Placement:** two lines ("Strait of" / "Gibraltar"), same IM Fell DW Pica Italic, size 33. The centre moved from ref (232,1132) rot 0° on the Andalusian shore to **(454,1146) rot 15°**.
  - 100 % of the ink is on sea pixels, with no clipping at any t (bbox ref [397,1104 – 521,1188]).
  - The ink is 12.5 px clear of the route. The route passes the "S" corner of the padded bbox (8 route points inside the bbox+4 px pad); there is no ink overlap.
- **Note:** the label sits on the eastern approach (Alboran) just east of the narrows. The narrows themselves are too narrow at this scale for a 33 px label without touching land or the route.
  - A closer spot, (396,1176) rot 25°, was rejected: 2.7 % on land and 5.4 px from the leg.
- Crops:
  - `qa_v4c/p05_gibraltar_f565_v4b_vs_v4c.png` (t 3.4)
  - `qa_v4c/p05_gibraltar_f775_v4b_vs_v4c.png` (t 10.4)

## (d) Rhône: thicker stroke
- The glyph stroke went from 0 → **2** (PIL stroke, 2× canvas px, about +1 px at 1×). Same font (IM Fell DW Pica Italic), size, position and colour.
- **OCR target not met.** rapidocr reads the IM Fell italic "h" as "b" ("Rbone"), and thickening makes this worse, because it closes the "h" shoulder.
- Stroke sweep on rendered frames (t 6.6 and 10.4; 390/540 wide; 2 pads × 3 scales = 24 tries each), counting exact "Rhone"/"Rhône" reads:

| stroke | exact reads | typical reads |
|---|---|---|
| 0 (v4b) | 3/24 | Rbone, Rhone, Rhine |
| 1 | 1/24 | Rbone, Rhone |
| **2 (v4c)** | 0/24 | Rbone, Rbene |
| 3 | 0/24 | nothing |
| 4 | 0/24 | nothing |

- Stroke 2 was kept because the ruling asks for a thicker stroke, and it is visibly bolder at phone size. By eye it reads "Rhône" at 390 wide.
- Getting OCR to read it would need a different glyph, such as the upright IM Fell DW Pica Roman already used for Pisa, or a larger size. That needs a ruling.
- Crop: `qa_v4c/p05_rhone_f775_v4b_vs_v4c_x2.png`

## (e) P17A: full proof treatment, with figure and oars matted out of displacement
- **Proof treatment kept (proof cb67cc82 parameters):** sail ripple 0.6 px, fleet drift 1.6 px, swell bob 1.0 px, roll 0.05°, push 1.00→1.04 at (0.55,0.45), and glints (seed 617).
  - Measured peaks: sail 0.635 and fleet 1.58 plate px.
  - Plate P17A_unnamed_captain.png md5 is fa286390… before and after.
- **Matte:** captain + hand polygon, grown 8 px; oars, grown 8 px; plus the proof's nowarp mask, all grown 6 px. Displacement is forced to 0 inside the matte, with a 12 px feather outside it. See `qa_v4c/p17a_v4c_matte_overlay.jpg`.
- **Warp on figure and oars (all frames):**

| measure | figure | oars |
|---|---|---|
| analytic displacement max (plate px) | **0.0** | **0.0** |
| plate pixels changed by remap vs rigid | 0 | 0 |
| output abs-diff vs a rigid-only render (matte eroded 5 px) | 0 | 0 |
| DIS optical flow vs rigid-only (max / p99 px) | 0.0 / 0.0 | 0.0 / 0.0 |

  - **Result: max warp displacement 0.0 px (≤0.5 OK), PASS.**
- **Not warp:** the whole frame still moves rigidly with the proof's swell bob/roll and push, exactly as in the proof. Relative to the v4b glints-only clip, this rigid camera motion is at most 1.39 px (figure) and 1.42 px (oars) analytically. DIS flow measures 2.11 / 2.20 px, which includes codec and flow noise.
  - If the ruling meant ≤0.5 px of *total* motion of the figure, set bob/roll to 0; that is one parameter change.
- **Push guardrail:** pixel density 1.205 ≤ 1.5, PASS. Push ≤ 1.04 with cover slack 1.0093.
- **Face stays hidden:** the figure faces away, hooded, in every frame.
- **Decision: full motion** (no fallback was needed).
- Crops: `qa_v4c/p17a_{figure,oars}_f{2203,2315,2427}_v4b_v4c_diffx8.jpg` (v4b | v4c | |diff|×8). The diff is a uniform edge pattern from the rigid bob, with no local distortion on the hood, hand or oars.

## OCR (rapidocr) at phone widths, v4c final render
Frames are from bjorn_rough_v4c.mp4 at P05 start (frame 463) + t, with t = 3.4, 6.6, 9.4 and 10.4 s. Each frame was downscaled to 390 and 540 wide, each label was deskewed, and each crop was enlarged ×3. This harness is stricter than the v4b one: on the same v4b frames it reads Italy and Pisa less often. Use the v4b column as a reference, not a strict A/B.

| Label | v4b (QA_rough_v4b) | v4c at 390 | v4c at 540 |
|---|---|---|---|
| PROVENCE | "PROVENCE" 0.96–0.97 | "PROVENCE" 0.80–0.84 (3 of 4 t; 1× "BROVENCE") | "PROVENCE" 0.81 at t 3.4; partial ("OVENCE", "PR") later |
| Strait of Gibraltar | "Strait of" / "Gibraltar" | "Straitof" + "Gibraltar" 0.79–0.86, all 4 t | "Strait of" + "Gibraltar" 0.83–0.89, all 4 t |
| Rhône | "Rbone" 0.77–0.94 | no read | "Rbone"/"Rbere"/"Rbee" 0.54–0.58 (fails; see (d)) |
| Pisa | "Pisa" | "Pis3" 0.57–0.59 | not read (same harness on v4b: also "Pis3"/not read) |
| KINGDOM OF ITALY | "KINGDOM", "OF ITALY" | "ITAL" partial | not read (unchanged label; same harness on v4b: also partial) |
| WEST FRANCIA | "FRANCIA" | "WEST" + "FRANCIA" 0.73–0.84 | "WEST" + "FRANCIA" 0.68–0.83 |
| Mediterranean Sea | "Mediterranean Sea" | "Mediterranean"/"…ncan" + "Sea" | "Mediterranean (Sea)" 0.84–0.88 |

- **Eye check at 390:** PROVENCE, Strait of Gibraltar and Rhône are all legible (`qa_v4c/phone_390_t*.png`).
- Full frames: `qa_v4c/p05_v4c_t{3.4,6.6,9.4,10.4}.png`

## Flags for the editor
1. **PROVENCE** is necessarily steep (75°), and its top third crosses into the Alpine and orange band (see (a)).
2. **Rhône:** the thicker stroke lowers OCR; the font's "h" is the cause (see (d)).
3. **Strait** label is on the water just east of the narrows, not in the narrows.
4. **P17A** has zero warp, but rigid swell up to ≈1.4 px remains, as in the proof.
5. Frames 2034–2202 are re-encoded (content unchanged, PSNR 47 dB) because of keyframe placement.
