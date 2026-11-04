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

- **Strait:** it is painted very narrow (nearly pinched), but there is an open sea channel. S4 threads it at ≥2 px from both shores.
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
- **Strait of Gibraltar is painted nearly closed.** The route threads a 2 px+ channel. At thumbnail size the S4 line looks like it touches the Spanish tip.
- **Orihuela landfall** sits at the Segura-mouth coast, 16 px from Orihuela (which is inland). The S5/S7 junction makes a small V there.
- **The plate has painted aged edges and a painted compass rose.** Neither is my vignette or overlay; both are untouched.
- **The Rome glyph is included because the handoff asks for it.** Vellum's "no labels" default is honoured: the glyph has no text. Drop it if the rough cut wants Pisa-only.
