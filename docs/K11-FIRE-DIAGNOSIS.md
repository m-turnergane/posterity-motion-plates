# K11 Fire Diagnosis: Why It Broke at 2.2x (2026-10-30)

Owner note (4:53pm ET lock): on shot 2 (Jianwen K11) "the fire looked messed up and the
image was blurry; the water itself is good."

Shot: `k11_fire_reflection_v1b.json`, rendered in the locked reel at 6–12 s.

## Verdict

Two separate faults stacked on top of each other. Both come from how the shot was set
up, not from torch_v1c or the water layers.

### Fault 1: Blur from Excessive Crop

The plate is 941×1672 pixels. Cover-fit to 1080×1920 is already 1.148×, and the static
zoom of 2.2 brings it to **2.53 output px per plate px**.

Only 428 plate px span the full 1080 output width. Every pixel is a cubic (`INTER_CUBIC`)
interpolation of a much smaller source, so edges smear over about 2.5 px. Cubic
overshoot also clips 2.9% of the pixels in the fire crop to 0 or 255, showing as
ringing on flame edges.

**The painting is not unusually soft.** The Laplacian variance of the K11 fire rects at
native res is 412–1790. Locked Edward II torch rects measure 134–707 (b13) and 599 (b10).
At native fill, K11 would be as sharp as the locked torch plates.

### Fault 2: Fire Masked into Blotches

torch_v1c is designed as painted flame + soft halo + broad spill. The spill and halo
are what read as a "pulse".

To keep land at 0 px, `zone_from_masks` allowed only the keyed flame pixels plus 3 px
of dilation and a 3 px feather (**7.6 output px** after the zoom).

The numbers:
- Only **9.2%** of torch_v1c's change energy survived the matte
- Raw fx changed 901,770 px; after the matte 23,406 px
- What survived is the painted-flame "toward hot (255,238,190)" push alone, on a patchy key

The torch key (L ≥ max(140, 0.55·Lmax) & R ≥ 170) fills only **14–55%** of each fire
rect, in **1–5 separate blobs** per source (median 46–673 px each).

K11 is a broad painted conflagration, not a torch. The result: a few patches inside one
continuous painted fire turning yellow-white (mean lift +35 levels at peak, 3.4% of
fire-zone px pushed near white) while the painted flame around them stays frozen.

This is the "messed up" look.

### Fault 3: Glow Sigma Mismatch

`σ = clip(0.9·h, 20, 120)` is in plate px. For K11 sources h = 5–54 px, so σ is 20–49
plate px, which becomes **50–123 output px** at 2.53×.

Two sources (h 5 and 14) sit at the 20 px floor — 4× and 1.4× their own flame height.
That glow was mostly cut by the matte. Where it survived, it lifted whole flame blobs
uniformly instead of reading as a soft glow around a torch.

### The Water Was Fine

The reflection columns are driven by the same `flick()` (correlation 0.97 with source
luma, 0.80 with the flick curve) and sit entirely in water. Only the fire source and
the crop were wrong.

## Numbers

From `k11_diag.py`:

| Metric | Value |
|--------|-------|
| Native plate size | 941×1672 |
| Cover-fit scale | 1.148× |
| Config zoom | 2.2× |
| Output px per plate px | 2.53 |
| Plate px visible in width | 428 |
| K11 fire rect Laplacian variance | 412–1790 |
| Reference torch Laplacian variance | 134–707 (b13), 599 (b10) |
| fx change energy kept after matte | 9.2% |
| Raw fx changed px | 901,770 |
| After matte changed px | 23,406 |
| Cubic overshoot (clip to 0/255) | 2.86% |

### Source Details

| Source | bb | h (px) | Glow σ (plate/out) | Mask px | Mask fill % |
|--------|-----|--------|-------------------|---------|-------------|
| 1 | [548,668,600,700] | 14 | 20 / 50 | 425 | 26% |
| 2 | [600,668,645,700] | 27 | 24 / 61 | 664 | 46% |
| 3 | [690,686,740,712] | 26 | 23 / 59 | 710 | 55% |
| 4 | [725,630,790,700] | 47 | 42 / 107 | 1347 | 30% |
| 5 | [790,610,860,700] | 54 | 49 / 123 | 1703 | 27% |
| 6 | [860,640,941,700] | 39 | 35 / 89 | 1004 | 21% |
| 7 | [760,690,820,712] | 5 | 20 / 50 | 185 | 14% |

## Fix / Rules

Now in `docs/GUARDRAILS.md` and `src/motionplates/guardrails.py`:

1. **Never crop/zoom past 1.5× of native fill.** K11 at 2.2 is refused. At 1.5 it would
   be 1.72 output px per plate px.

2. **Run torch_v1c / water fire reflections only on sharp, native-resolution fire:**
   Laplacian variance of the fire rect ≥ 100 at native res.

3. **Do not clip torch_v1c to a flame-pixel matte on a broad painted conflagration.**
   Either let the halo and spill run with land protected by `relight_poly`, or drive
   only the reflection from `flick()` and leave the source fire untreated.

4. **Known bad example:** `k11_fire_reflection_v1b.json` (zoom 2.2, flame-pixel matte).
   Do not reuse it.

## See Also

- `docs/GUARDRAILS.md` — The guardrails that prevent this failure
- `docs/WATER-V1.md` — water_v1 documentation
- `examples/water_v1/k11_fire_reflection_v1b.json` — The bad example config (kept for documentation)
