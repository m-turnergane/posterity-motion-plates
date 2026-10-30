# Plate Crop and Fire Guardrails (2026-10-30)

Shared guardrails for all motion presets. These checks prevent the K11 fire-break
failure mode and ensure motion effects run only on sharp, native-resolution content.

**Source:** `src/motionplates/guardrails.py`

## Background

The K11 fire-reflection shot (water_v1 reel shot 2) broke at a 2.2x crop because:
1. The plate was upscaled to 2.53 output px per plate px, making it visibly soft
2. The fire was masked to flame-pixels only, clipping 91% of torch_v1c's halo/spill

See `docs/K11-FIRE-DIAGNOSIS.md` for the full diagnosis.

## Rules

### 1. Crop/Zoom Limit

Plates are never cropped or zoomed past **~1.5x of native fill** (1.0 = plate cover-fits
the frame). This covers push end zoom, static crops and reel reframes.

Beyond 1.5x, a 941-px-wide plate is upscaled to more than 1.7 output px per plate px
and goes visibly soft on a phone.

### 2. Fire Sharpness

torch_v1c and water fire reflections run **only on sharp, native-resolution fire**:
- The fire rect's Laplacian variance must be ≥ 100 at native plate res
- The shot zoom must be ≤ 1.5x

Locked torch plates measure 134–707 Laplacian variance. K11 fires measure 412–1790 at
native res — they're sharp, but the 2.2x zoom made them soft.

### 3. No Flame-Pixel-Only Mattes on Conflagrations

Do not clip torch_v1c to a flame-pixel-only matte on a broad painted conflagration.
Either:
- Let the halo and spill run, with land protected by `relight_poly`, OR
- Drive only the reflection from `flick()` and leave the source fire untreated

## API

### `check_crop_zoom(zoom, max_zoom=1.5, mode="refuse", plate_wh=None, out_wh=(1080,1920))`

Check that zoom does not exceed max_zoom.

```python
from motionplates.guardrails import check_crop_zoom

# Refuse mode (raises GuardrailError)
check_crop_zoom(2.2)  # raises GuardrailError

# Warn mode (prints warning, returns report)
result = check_crop_zoom(2.2, mode="warn")
# result = {"check": "crop_zoom", "zoom": 2.2, "max_zoom": 1.5, "ok": False, "msg": "..."}
```

### `check_fire_sharpness(plate, rects, zoom=1.0, min_lapvar=100, max_zoom=1.5, mode="refuse")`

Check fire/torch rects for sharpness at native resolution.

```python
from motionplates.guardrails import check_fire_sharpness
import cv2

plate = cv2.cvtColor(cv2.imread("plate.png"), cv2.COLOR_BGR2RGB)
rects = [(548, 668, 600, 700), (600, 668, 645, 700)]  # fire regions

result = check_fire_sharpness(plate, rects, zoom=1.0)
# result = {"check": "fire_sharpness", "zoom": 1.0, "lapvar": [820.8, 913.5],
#           "min_lapvar": 100, "soft_rects": [], "max_zoom": 1.5, "ok": True, "msg": "ok"}
```

### `check_shot(cfg, plate=None, mode="refuse", out_wh=(1080,1920))`

Convenience function: check crop-zoom and fire-sharpness from a shot config.

```python
from motionplates.guardrails import check_shot
import json, cv2

cfg = json.load(open("shot.json"))
plate = cv2.cvtColor(cv2.imread(cfg["plate"]), cv2.COLOR_BGR2RGB)

results = check_shot(cfg, plate, mode="warn")
# results = [crop_zoom_report, fire_sharpness_report] or just [crop_zoom_report]
```

## Waivers

One locked shot predates this guardrail and is kept bit-identical:

- **p05v2_sun_glitter_v1d**: 1.6x static crop, LOCKED by owner 2026-10-30 4:53pm ET

This shot has a named waiver in `LOCKED_WAIVERS` that downgrades the error to a warning
at exactly 1.6x. **Do not add new waivers** — reframe instead.

## Integration

### water_v1_1 Wrapper

The guarded entry point for water_v1 is via a wrapper that calls guardrails first:

```python
# water_v1_1 pattern:
from motionplates.guardrails import check_shot, GuardrailError
from motionplates.standalone.fx_water import WaterShot, render

def guarded_render(cfg, plate, mode="refuse"):
    check_shot(cfg, plate, mode=mode)  # raises or warns
    return render(cfg, ...)
```

### How to Wire into Other Modules

Call `check_shot()` from every new engine (dust_v1, etc.):

```python
from motionplates.guardrails import check_shot

def render(cfg, out, ...):
    plate = load_plate(cfg["plate"])
    check_shot(cfg, plate)  # refuse mode by default
    # ... proceed with rendering
```

## Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `MAX_ZOOM` | 1.5 | Maximum crop/zoom relative to native fill |
| `FIRE_MIN_LAPVAR` | 100.0 | Minimum Laplacian variance for fire rects |
| `FIRE_MAX_ZOOM` | 1.5 | Maximum zoom for fire effects |

## See Also

- `docs/K11-FIRE-DIAGNOSIS.md` — Why the K11 fire broke at 2.2x
- `docs/WATER-V1.md` — water_v1 documentation
- `docs/TORCH-V1C.md` — torch_v1c documentation (PR #3)
