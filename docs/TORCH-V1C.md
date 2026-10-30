# torch_v1c — LOCKED 2026-10-30 by owner

**HOUSE TORCH STANDARD** for torches, braziers, cressets, lanterns-as-torch, and larger fires.

**Owner verdict:** "more like a pulsing effect". The Edward II v1c torch treatment, exactly
as shipped, is the house torch standard. No tweak, no boost. The v3 flames work "was
distorting the things around it": its strong spill and heavy sky billow are REJECTED for
torch surroundings. flames_v1–v3 are R&D only.

## Reference

- **Master:** `renders/posterity-edward-ii-v3b-ROUGH-v1c.mp4` (md5 `b4f0aa7a68619ed5928738698f6e2eaf`)
- **Torch/cresset slots:** S10 b10 cresset, S13 b13 three torches (also S08 b08, S11 p07, S16 p10)
- **Source module:** `src/motionplates/standalone/fx_torch.py`
- **Audit:** `docs/AUDIT-V1C-VS-V3.md`

## Core Principles

1. **Painted flame shape holds:** no tongue, no warp, no displacement anywhere
2. **Soft local glow and spill pulse** at v1c strength
3. **Surroundings stay visually steady:** no moving or warping
4. **No strong pulsing waves or moving light gradients** on walls or faces (no v3 spill)
5. **Glow zones fixed:** the whole room brightens and dims together with one brightness value per frame

## Technical Details

### Flame Key (torch)

```
lo = (L >= max(140, 0.55*Lmax)) & (R >= 170) inside the source rect
mask = dilate 3x3 then Gaussian σ 1.6
```

### Flicker Clock

```python
amps = [0.15, 0.08, 0.035, 0.015] × 1.5  # torch/offscreen; windows × 0.8
freqs = [0.55, 1.3, 2.6, 4.4] Hz         # each × U(0.85, 1.15), random phases
noise = 0.05 at 4 Hz
f = max(0.45, 1 + Σ(amp×sin(2π×freq×t + phase)) + noise)
```

Highest component 4.4 Hz, so nothing strobes.

### Painted Flame (shape holds)

- **tongue = 0** for torches (no scrolling teardrop/tongue)
- **No warp or remap** (warp is only for candles with h ≥ 5)
- Flame pixels go toward hot (255,238,190):
  ```
  g = clip(0.6·(f−1), −0.5, 0.6)
  roi + (hot−roi)·clip(g,0,1)·0.6 + roi·g·0.2  (when g > 0)
  roi·(1+g)                                     (when g < 0)
  ```

### Glow (halo)

```
gauss_dot at (x, base − h/2)
σ = clip(0.9·h, 20, 120) px for torches
colour = (255,165,80)
gain = 0.18 × 2 × min(1, max(PULSE, 0.6)) × (f−1)
```

Painted plates already carry the static glow: animate the halo as a pulse only (no exposure lift).

### Spill (falloff, reach, pulse amplitude)

```
reach r = 800 × 1.3 × LOCAL(0.32) × clip(h/26, 0.5, 3)^0.5 × radius_mult
        ≈ 330–570 px on a 941-px plate; explicit offscreen radius × 0.6
weight = clip(h/26, 0.25, 2.5)^0.5
```

Up to 8 k-means groups. Per group:

```
fall = 1 − Π(1 − clip(w,0,1)/(1 + (d/r)^2.0))  on a 1/4-res grid
light offset (0,−14)
facing = 0.45 + 0.55·clip(0.65·lit + 0.35·grad)
map = spill_amp × fall × facing × relight-mask
```

Per frame:

```
dl = mean_group(f−1) × min(√n, 2.5) × PULSE[plate]
img *= 1 + map·dl·tint(1.0, 0.8, 0.5)
```

The map is static and the pulse is **one scalar per group**, so walls and faces breathe together
and no light gradient ever moves.

### PULSE Calibration

| Plate | PULSE |
|-------|-------|
| b08   | 0.9   |
| b10   | 0.47  |
| b13   | 0.22  |
| p07   | 0.43  |
| p10   | 0.79  |
| p05   | 0.13  |

### Embers

Per SPECS spawn ellipses:
- b10: (676,430,22,26) n 34
- b13: 3 spawns n 70

Rise 25–70 px/s, life 1.2–2.6 s, drift +6 px/s, sway 2.4–8 px at 0.4–1.4 Hz, size 0.9–1.7,
colour (255,170,80), twinkle 5–13 Hz, two gauss dots per ember.

## Measured Strength (360×640, 1 s windows, median)

| Region | Swing |
|--------|-------|
| Walls and faces near torch | 20–46 % |
| Chainmail | 10–29 % |
| Whole frame | ≈ 12–14 % (3 s p-p 15–20 %) |
| Max step | ≤ 3.1 %/frame |
| Energy above 5 Hz | < 1 % |

It is large but coherent, which is what reads as "pulsing" rather than distortion.

## Scope Note (owner, 2026-10-30, after the 4:31pm ET lock)

- Flames LOCKED on flames_v4 / torch_v1c for **torches, cressets, braziers and all larger fires**
  (burning buildings, town fires). Owner: "much better for the larger flames in our plates,
  simple and does the job."
- **Candles keep their own treatment:** the fx_candle preset (candle-sized flame shape motion,
  flicker, local spill) plus subtle smoke_v2 wisps. torch_v1c does NOT apply to candles.
- flames_v1–v3b (tongue displacement) remain R&D only; never use them in production.

## Usage

```python
from motionplates.standalone.fx_torch import TorchFX

spec = dict(
    torch=[(638, 378, 712, 528)],  # (x0, y0, x1, y1) rects for torch flames
    relight_poly=[[(0, 0), (475, 0), (560, 60), ...]],  # areas to exclude from relight
    spill_amp=1.8,
    embers=[dict(spawn=[(676, 430, 22, 26)], n=34)],
)

fx = TorchFX(plate_path, spec, pulse=0.47, seed=10)

for frame_idx in range(total_frames):
    t = frame_idx / 30.0
    out = fx.render(t)  # RGB uint8 (H, W, 3)
```

## Rules Summary

1. Painted flame shape holds (no tongue, no warp, no displacement)
2. Soft local glow and spill pulse at v1c strength
3. Surroundings stay visually steady (no moving or warping)
4. No strong pulsing waves or moving light gradients on walls or faces
5. No v3 spill (it moves gradients across walls and faces)
6. No tongue or displacement motion on torches
7. flames_v1–v3 are R&D only
8. Faces, land and water get zero warp; the sea never moves (keep protects at 0 px)

## See Also

- `docs/AUDIT-V1C-VS-V3.md` — Detailed comparison showing why v1c beat v3
- `docs/SMOKE-V2.md` — Smoke overlay documentation
- `src/motionplates/standalone/fx_candle.py` — Candle treatment (separate from torch_v1c)
