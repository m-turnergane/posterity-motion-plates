# K11 fire on water_v1 reel shot 2: why it broke (diagnosis, 2026-10-30)

Owner note (4:53pm ET lock): on shot 2 (Jianwen K11) "the fire looked messed up and the image was blurry; the water itself is good."
Shot: `configs/k11_fire_reflection_v1b.json`, rendered in `final/water_v1_reel.mp4` at 6–12 s. Evidence is in `diag/`: `k11_diag.py` → `k11_diag_numbers.json`, `k11_mask_patchiness.json`, and the crops listed below.

## Verdict
Two separate faults stacked on top of each other. Both come from how the shot was set up, not from torch_v1c or the water layers.

1. **Blur is the crop, not the painting.** The plate is 941x1672. Cover-fit to 1080x1920 is already 1.148x, and the static zoom of 2.2 brings it to **2.53 output px per plate px**. Only 428 plate px span the full 1080 output width. Every pixel is a cubic (`INTER_CUBIC`, push_frame) interpolation of a much smaller source, so edges smear over about 2.5 px. Cubic overshoot also clips 2.9% of the pixels in the fire crop to 0 or 255, which shows as ringing on the flame edges.
   - The painting is not unusually soft. The Laplacian variance of the K11 fire rects at native res is **412–1790**. The locked Edward II torch rects measure **134–707** (b13) and **599** (b10). At native fill, K11 would be as sharp as the locked torch plates.
2. **The fire was masked into blotches.** torch_v1c is designed as painted flame + soft halo + broad spill, and the spill and halo are what read as a "pulse". To keep land at 0 px, `zone_from_masks` allowed only the keyed flame pixels plus 3 px of dilation and a 3 px feather (**7.6 output px** after the zoom). The numbers:
   - Only **9.2%** of torch_v1c's change energy survived the matte. Raw fx changed 901,770 px; after the matte 23,406 px.
   - What survived is the painted-flame "toward hot (255,238,190)" push alone, on a patchy key. The torch key (L ≥ max(140, 0.55·Lmax) & R ≥ 170) fills only **14–55%** of each fire rect, in **1–5 separate blobs** per source (median 46–673 px).
   - K11 is a broad painted conflagration, not a torch. The result is a few patches inside one continuous painted fire turning yellow-white (mean lift **+35 levels** at the peak, 3.4% of fire-zone px pushed near white) while the painted flame around them stays frozen. This is the "messed up" look. `diag/k11_fire_native_plate_fxraw_wv1_diff_x2.png` shows plate, raw fx, the water_v1 frame and |diff|x4. The diff panel shows the blotches, mostly a G-channel (yellowing) shift.
   - The 2.53x zoom then magnified each blotch and its 7.6 px matte edge.
3. **Glow sigma is sized for torches, in source px.** `σ = clip(0.9·h, 20, 120)` is in plate px. For K11 sources h = 5–54 px, so σ is 20–49 plate px, which is **50–123 output px** at 2.53x. Two sources (h 5 and 14) sit at the 20 px floor, 4x and 1.4x their own flame height. That glow was mostly cut by the matte (point 2). Where it survived, it lifted whole flame blobs uniformly instead of reading as a soft glow around a torch.
4. **The water was fine.** The reflection columns are driven by the same flick() (correlation 0.97 with source luma, 0.80 with the flick curve) and sit entirely in water. Only the fire source and the crop were wrong.

## Fix / rule (now in PRESETS.md "Plate crop and fire guardrails" and `motion/guardrails.py`)
- Never crop or zoom a plate past **1.5x of native fill**. K11 at 2.2 is refused by `water_v1_1.py`. At 1.5 it is 1.72 output px per plate px.
- Run torch_v1c / water fire reflections only on sharp, native-resolution fire: Laplacian variance of the fire rect ≥ 150 at native res (guardrails.check_fire_sharpness).
- Do not clip torch_v1c to a flame-pixel matte on a broad painted conflagration. Either let the v1c halo and spill run with land protected by relight_poly (as on P05 in flames_v4), or, if land must stay 0 px, drive only the reflection from flick() and leave the source fire untreated.
- Known bad example: `configs/k11_fire_reflection_v1b.json` (zoom 2.2, flame-pixel matte). Do not reuse it.

## Crops
- `diag/k11_fire_native_plate_fxraw_wv1_diff_x2.png`: native crop (700–941, 600–720) x2 of plate | fx raw | water_v1 frame | |diff|x4.
- `diag/k11_output_1080_z2.2_firecrop.png`: the 1080x1920 output at z 2.2 (fire band).
- `diag/k11_phone_z2.2_vs_z1.0.png`: 360x640 phone, z 2.2 vs native fill.

## Addendum (implementation)
- The fire sharpness threshold is **100**, not the 150 mentioned above. The locked b13 third torch measures 133.7 and is shipped, so 150 would have refused a locked plate. See `FIRE_MIN_LAPVAR` in `motion/guardrails.py`.
- `water_v1_1.py render configs/k11_fire_reflection_v1b.json ...` now raises `GuardrailError: zoom 2.200x of native fill exceeds 1.5x`.
