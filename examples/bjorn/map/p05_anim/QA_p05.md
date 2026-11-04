# P05 — registration, distortion QA, MapTrace test v1
Atelier, 2026-11-03 (EST). Build: `p05_build.py` (it refuses to overwrite without `--force`). The full run takes about 53 s and renders 188 frames in about 51 s.
Source plate `plates/P05_KEEP.png` is 941×1672, md5 4ef7ca5fdd0010a3f0825ae3eacb68b6. It is opened read-only, and its md5 is checked again at the end: unchanged.
`map/make_p05_reference.py` and the other half-built files in map/ were not touched.

## 1. Registration (plate px → refpack_p05 px = 1080×1920 output space at push 1.00)
- **Model: similarity.** Scale 1.14833 (the cover-fit is 1.14833, so they match), rotation −0.0116°, shift (+0.26, +0.42) px. No TPS and no shear.
  - An affine fit was also computed for comparison and was no better: inlier mean 1.89 vs 1.92 px. The similarity was kept.
- **Control points: automatic coastline ICP. No hand-picked points.**
  - Ref coast: the boundary of the refpack clean-plate sea colour, every 3rd pixel, 10,271 samples.
  - Plate coast: the boundary of the colour-segmented painted sea, 26,752 px. The sea is slate-teal (B−G about 10–16). West Francia's royal blue (B−G about 40) is excluded because it otherwise leaks into the mask. Speckle components under 4000 px are dropped.
  - Excluded areas: the 16 px plate / 24 px ref borders (painted aged edge) and the compass zone +20 px.
  - Fit: trimmed nearest-neighbour ICP with an LMedS fit. The trim radius is annealed from 12 px to 4 px over 30 iterations.
- **Residuals (output px at push 1.00; multiply by ≤1.06 during the push):**
  - All coast samples: median 1.53, p90 6.94.
  - Inliers (<8 px, 91.7% of samples; 79.7% are <4 px): mean 1.92, median 1.32, p95 5.79.
  - Per landmark (within 45 px):

| Landmark | Mean (px) | Max (px) |
|---|---|---|
| Algeciras | 1.34 | 5.5 |
| Strait | 1.22 | 4.1 |
| Nekor | 0.92 | 3.3 |
| Orihuela | 0.92 | 3.9 |
| Mallorca | 1.37 | 4.1 |
| Loire | 2.36 | 9.6 |
| Rhône | 2.58 | 7.7 |
| Camargue | 3.09 | 8.7 |
| Rome | 5.89 | 9.9 |
| Galicia | 5.87 | 14.5 |
| **Tuscany/Pisa** | **10.66** | **13.0** |

  - Tuscany/Pisa is the worst region: the painter put the Tuscan coast about 8 px W and 6 px S of the data coast.
  - These are local painting differences, not a misfit. I did not bend the plate to fix them. The route was adapted to the painted sea instead (§3).
- **Resampling:** OpenCV Lanczos-4 (INTER_LANCZOS4). No ML upscaler (Real-ESRGAN etc.) is installed on the box.
  - Each video frame is ONE Lanczos resample from the ORIGINAL plate, using the composed camera∘registration affine. Frames are not resampled from the registered PNG.
  - `P05_KEEP_registered_1080x1920.png` is the push-1.00 registered reference.
- **Guardrail** (`motion/guardrails.py`, refuse mode): checked against the original 941×1672 plate, push 1.00→1.06.
  - check_pixel_density: **1.217 output px per source px (x 1.217, y 1.217), limit 1.5, PASS.** Visible source at peak is 887×1577 px.
  - check_crop_zoom(1.06): PASS.
  - The actual peak scale of the composed transform is 1.14833 × 1.06 = 1.2172.
  - The drift is a translation only, so it does not change the density.

## 2. Distortion QA
- **Local Jacobian** on a 40×70 grid: local scale is 1.14833 everywhere, so the max scale deviation is **0.000%**. Max shear is **0.000°** and anisotropy is 1.000. The map is a pure similarity, so geography is not warped anywhere.
- **Before/after crops:** `qa/p05_registration_crops.png` covers the Strait, the Rhône/Camargue and Tuscany→Rome.
  - Each row shows the original plate (nearest-neighbour ×2), then registered (×2), then registered with the ref coast in magenta and the route in green/cyan.
  - The coastline shapes and brush texture are unchanged apart from the uniform scale.
- **Texture:** Laplacian variance of the registered crop vs the original crop is 0.63 (Strait), 0.63 (Rhône) and 0.63 (Tuscany).
  - This is uniform across regions and sits between 1/s² (0.76) and 1/s⁴ (0.57), as expected for an honest ×1.148 Lanczos upscale.
  - There is no regional smearing and no sharpening halo.

## 3. Route on the painted plate (all in ref px)
- **Method:**
  - Start from the refpack `polyline_out_px` per leg.
  - Trim the inland spurs at each end to the painted coast.
  - Join each leg to a shared coast junction: the nearest painted-sea point that is ≥2 px offshore of the place.
  - Push interior samples seaward along the painted-land distance field. The margin is 4 px offshore, ramping to 1 px at landfall. Then a Chaikin smooth and a final no-smoothing on-sea pass.
- **Every sample of every leg lies on painted sea: 0 land samples.**

| Leg | Length (px) | Min dist to land (px) | Max shift from refpack line (px) |
|---|---|---|---|
| S4 Algeciras→Strait→Nekor | 83.5 | 2.0 | 1.24 |
| S5 Nekor→Orihuela | 209.3 | 2.8 | 0.78 |
| S7 Orihuela→Rhône→Camargue | 389.1 | 2.0 | 1.03 |
| S9 Camargue→Pisa | 230.3 | 2.0 | 0.97 |
| P05-LEG legendary | 140.8 | 2.0 | 3.6 |

- **Strait:** ~~it is painted very narrow (nearly pinched), but there is an open sea channel. S4 threads it at ≥2 px from both shores.~~ **Corrected in v2:** the painted Strait is closed (sea mask has no sea at x 174–176 ref px; Atlantic and Mediterranean are separate sea components). S4 starts at the Algeciras landfall (179,1191), just east of the pinch, so it never passes through the strait.
- **Junctions (coast points; distance from the data point):**

| Place | Junction (px) | Offset |
|---|---|---|
| Algeciras | (179, 1191) | 5.4 px |
| Nekor | (244, 1236) | 10.8 px |
| Orihuela / Segura mouth | (388, 1105) | 16.1 px. Orihuela is inland, so the leg ends at the coast. |
| Camargue | (593, 821) | 12.9 px. This is on the painted delta shore. |

- **Pisa end-mark (unlabelled):** at (806, 801), 2.0 px offshore on the painted Tuscan coast.
  - It is 22.3 px (about 47 km) from the Pisa data point (823.8, 787.6). Pisa sits on painted land because of the coast offset above.
  - It was constrained to be ≥8 px nearer Pisa than Luna: it is 30.6 px from Luna (807.6, 770.4).
  - There is no Luna mark.
- **Legendary leg:** it runs from the end-mark south along the coast and **stops at sea** at (884, 881), 3.2 px off the painted coast.
  - That is **30.5 px (about 64 km) short of Rome**.
  - The Rome glyph (small pale ring, no text) is at the Rome data point (914.1, 876.2), which is on painted land.
- **Frame safety:** across the whole move, all overlay geometry stays in x 128–923 and y 791–1261 output px. That is inside pin_safe and above the caption line at y 1280.

## 4. Animation (`p05_test_v1.mp4`)
- **Format:** 1080×1920, 30 fps, 188 frames = 6.267 s. That is 6.25 s rounded up to whole frames; the cut uses the first 6.25 s.
  - Encoded as H.264 yuv420p, crf 19, **silent (no audio track)**, 6.3 MB.
- **Camera:** push 1.00→1.06 with a cosine ease over the full shot, plus a slack-limited translational drift.
  - It leans south-west toward the strait early, then pans east toward the Rhône and Italy by 4.6 s.
  - The window never leaves the plate (asserted every frame).
  - Nothing else moves the painted pixels.
- **Route styling:** house oxblood (112, 26, 20) ink, 5.0 px × zoom, at α 0.92.
  - It has a wet dark tip (62, 10, 6) over the last 26 px, which dries in 0.5 s, and a parchment keyline 8.4 px at α 0.55.
  - Drawn at 3× supersample with AA, downsampled with INTER_AREA.
- **Beat timings** (shot seconds → cut seconds):

| Beat | Shot (s) | Cut (s) | Notes |
|---|---|---|---|
| Fleet marker fades in at Algeciras | 0.00–0.25 | 17.50–17.75 | |
| S4 Algeciras→Strait→Nekor | 0.25–1.30 | 17.75–18.80 | |
| S5 Nekor→Orihuela | 1.30–2.35 | 18.80–19.85 | |
| S7 Orihuela→Rhône→Camargue | 2.35–3.45 | 19.85–20.95 | |
| S9 Camargue→Pisa | 3.45–4.55 | 20.95–22.05 | Solid ink is complete at 4.55 s, which matches the handoff's "~4.5 s". |
| Pisa end-mark stamps | 4.55–4.77 | 22.05–22.27 | Ink ring + dot; settles from 1.35× scale. |
| Hold at Pisa | 4.55–4.85 | 22.05–22.35 | |
| Legendary leg | 4.85–5.90 | 22.35–23.40 | Broken dashes 13 on / 9 off px, paler (176, 120, 100), 3.6 px wide; on "never name its leader". |
| Pale Rome glyph | 5.55–5.90 | 23.05–23.40 | Peaks at α 0.8. |
| Rest on the empty end-mark | 5.90–6.25 | 23.40–23.75 | |

  - Each leg is eased (cosine) within its beat.
  - Completed legs fade to α 0.72 over 0.6 s.
- **Fleet marker:** a small square-sailed ship glyph (oxblood hull and mast, parchment sail, soft shadow, parchment keyline). No text and no portrait.
  - It rides the drawing head and always faces east.
  - It parks 46 px before the Pisa end on S9, so the end-mark stays clear.
  - It does not travel the legendary leg.
- **Not included:** labels, text, Luna mark, vignette, letterbox, watermark, dust or other FX. The handoff lists no FX besides the route overlay.
- **Contact sheet:** `p05_contact_sheet.png` shows frames 0, 30, 52, 85, 118, 140, 160 and 187. Those are 0.00, 1.00, 1.73, 2.83, 3.93, 4.67, 5.33 and 6.23 s.
  - The frame/time captions are burned into the sheet only, not the video.
  - Full-res route crops: `qa/p05_frame140_routecrop.png` and `qa/p05_frame187_routecrop.png`.

## 5. Deviations from the handoff
1. **Camera:** the handoff allows 1.00–1.25 with a "slow drift down the Iberian coast to the strait, then east to the Rhône and along Italy". I used the brief's 1.00→1.06 push. The drift is limited to the slack that a 1.06 push gives (≤ ±31 px x, ±54 px y), so it is a lean, not a travel. A larger travel would need more zoom (it would still pass at ≤1.30 density) and owner sign-off on the brief's 1.06.
2. **VO timing:** no locked VO audio exists for Björn; only `raw/script-vo-v3-LOCKED.txt` is present. The timing follows the handoff/storyboard structure (solid by about 4.5 s, legendary leg after it on "never name its leader"). It is not cued to audio, and the video is silent.
3. **Frame count:** 188 frames (6.267 s), not the 187.5 that 6.25 s implies.
4. **Short rest at the end:** the storyboard says "ends on the empty end-mark within the slot (no added hold)". The leg finishes 0.35 s before the slot end, so the rest is inside the slot.

## 6. Flags
- **Painted coast offsets:** Tuscany/Pisa is about 10–13 px from the data coast, Rome about 6–10 px and Galicia about 6–14 px. I adapted the route to the painting rather than warping it.
  - The Pisa end-mark is about 47 km offshore-west of real Pisa.
  - The legendary leg stops about 64 km short of Rome.
  - Both read correctly on the painting, but they are not data-exact.
- **Strait of Gibraltar is painted closed** (corrected in v2; see section 7). S4 starts east of the pinch. In v1 the S4 line looked like it touched the Spanish tip at thumbnail size; v2 fixes this.
- **Orihuela landfall** sits at the Segura-mouth coast, 16 px from Orihuela (which is inland). The S5/S7 junction makes a small V there.
- **The plate has painted aged edges and a painted compass rose.** Neither is my vignette or overlay; both are untouched.
- **The Rome glyph is included because the handoff asks for it.** Vellum's "no labels" default is honoured: the glyph has no text. Drop it if the rough cut wants Pisa-only.


---

## 7. v2 (p05_test_v2.mp4), 2026-11-03 EST: legibility pass on Vellum's notes
v1 structure and timing were approved and are unchanged. v1 files are untouched, and this file's v1 text is backed up as `QA_p05_v1_backup.md`.
- **Build:** `p05_build_v2.py`, a patched copy of `p05_build.py`. It uses the same registration. The regenerated warp equals `P05_KEEP_registered_1080x1920.png` bit for bit, so that file was not rewritten. The transform is in `p05_transform_v2.json` and the log in `qa/build_log_v2.json`.

### Stroke spec (ref px at push 1.00; multiply by z, up to 1.06, in frame)
| Element | Colour | Width | Opacity |
|---|---|---|---|
| Solid legs, ink | house oxblood **#701A14** (112,26,20), from `motion/PRESETS.md` `route.color`; the same value v1 used | **11 px** (v1: 5 px, so 2.2×) | 1.0 while drawing, settles to **0.85** (v1: 0.72) |
| Solid legs, parchment keyline | **#EEE2C6** (238,226,198) | **16 px** (4 px each side of the ink) | 0.92 |
| Legendary leg, ink | pale oxblood **#B86050** (184,96,80), dashed 20 on / 13 off | **6.5 px** (v1: 3.6) | 0.92 |
| Legendary leg, keyline | #EEE2C6 | **10.5 px** | 0.80 |
| Fleet glyph and Pisa end-mark | as v1 | **1.5×** v1 | as v1 |
- The fleet glyph parks 64 px before the S9 end so it does not cover the end-mark.
- The Rome ring is kept, faint and unlabelled.
- The camera is unchanged: a 1.00→1.06 lean, no travel.

### S4 through the Strait mouth
- S4 leaves the Algeciras landfall heading **south-east at 25°**. It reaches open water at (196.7,1199.3), where the whole keyline fits, then rejoins the refpack curve to Nekor.
- **Offset vs v1** (ref px, south +): +1.1 at x186, +1.7 at x190, **+5.1 at x195, +5.9 at x200, +5.8 at x205**, +5.3 at x210, +4.4 at x215, +3.2 at x220, +0.8 at x230. The maximum shift from the refpack line is 5.6 px.
- **Clearance from the Spanish tip:** the centre line is 8.7 px from Spain 10 px along S4, 13.5 px at 15 px and 18.1 px at 20 px. Past the channel spur (19.6 px), the minimum is **18.35 px**, so the keyline edge is ≥ **10.35 px** clear (v1 with the same keyline: 8.69). The keyline edge is clear of Spain from about 9 px along S4.
- **The Algeciras spur is longer than the others:** 19.6 px, vs 12 px everywhere else. The landfall sits in the closed-off end of the channel, which is about 6–9 px wide. A 16 px keyline cannot fit there without touching both banks, so the first 19.6 px of S4 count as the landfall spur. The centre line stays ≥1.94 px from land even there.

### QA (re-run)
- **Guardrail:** `check_pixel_density(P05_KEEP, (1080,1920), (1.0,1.06), mode="refuse")` gives **1.217 PASS** (max 1.5). `check_crop_zoom(1.06)` also passes. The actual peak plate→frame scale is 1.2172.
- **Footprint on sea.** D is the distance to painted land, sampled bilinearly. Footprints are rastered at 4×, and the land figures are in ref px².

| Leg | Length | Centre samples on land | Min centre distance to land | Keyline on land outside spurs | Min keyline clearance outside spurs | Keyline / ink on land inside spurs | Spurs (start/end) |
|---|---|---|---|---|---|---|---|
| S4 | 81.1 | 0 | 1.94 | **0** | 4.35 | 232 / 104 | 19.6 / 12 |
| S5 | 213.6 | 0 | 2.62 | **0** | 1.25 | 177 / 75 | 12 / 12 |
| S7 | 393.6 | 0 | 2.06 | **0** | 1.25 | 179 / 77 | 12 / 12 |
| S9 | 241.0 | 0 | 2.65 | **0** | 1.25 | 150 / 60 | 12 / 12 |
| P05-LEG (legendary, keyline half 5.25) | 146.7 | 0 | 2.11 | **0** | 1.14 | 26 / 6 | 12 / – (ends at sea) |

- **Coastal legs move slightly seaward:** to keep the wider keyline off the coast, they sit a few px further out than v1 (maximum shift from the refpack line: S7 7.8, S9 7.8, legendary 7.0 px).
- **Legendary leg end:** (883,884), 6.39 px offshore and 32.1 px (about 67 km) short of Rome (v1: about 64 km).
- **pin_safe and caption line:** the rendered-alpha bbox over all 188 frames is x 119–915, y 765–1269 frame px. That is inside pin_safe [64,96,1015,1824], and every pixel is above the caption line y 1280 (11 px margin). This is asserted per frame.
- **Nothing added beyond the route:** no labels, text, Luna mark, vignette or watermark. The added elements are the route, its keyline, the end-mark, the fleet glyph and the unlabelled Rome ring.
- **Plate:** `plates/P05_KEEP.png` md5 is `4ef7ca5fdd0010a3f0825ae3eacb68b6`, unchanged before and after the build.
- **Video:** 1080×1920, h264 yuv420p, 30 fps, 188 frames, 6.267 s, silent.

### Legibility at phone size
- `qa/p05_v2_last_360x640.png` is the last frame downscaled to 360×640 (INTER_AREA). `qa/p05_v1_vs_v2_last_360x640.png` puts v1 and v2 side by side.
- At thumbnail size the ink is about 3.9 px and the keyline about 5.7 px wide. The ink core is LAB (32.1,30.8,21.0) against the sea ring at (36.9,0.5,−0.7): **ΔE 37.6**.
- The route reads clearly as a red-brown line with a light edge from the Strait to Pisa. The pale dashed legendary leg also reads, and stays lighter.
- Full-res crops: `qa/p05_v2_frame140_routecrop.png` and `qa/p05_v2_frame187_routecrop.png`. Contact sheet: `p05_contact_sheet_v2.png`.

### v2 flags
- **The Pisa end-mark is a coastal mark by design.** It is 2 px offshore, and at 1.5× its ring and keyline overlap the painted Tuscan coast. It sits in the Pisa landfall spur.
- **Wider S4 spur at Algeciras** (19.6 px vs 12 px), forced by the painted closed Strait (see above).
- **v1 Strait statement corrected:** the strait is painted closed, and S4 does not pass through it.
- The S5/S7 V at Orihuela is unchanged (approved).
