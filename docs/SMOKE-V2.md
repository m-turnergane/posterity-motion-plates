# Smoke v2 Effect Module

**Status:** Locked 2026-10-30. Production-ready procedural smoke overlay.

## Overview

The smoke v2 module generates realistic procedural smoke overlays for painted
plates. It creates billowing smoke columns that rise from emitter sources,
with natural turbulence, density variations, and proper atmospheric integration.

The module is designed around these core principles:

1. **Frame-0 equality**: The smoke overlay at t=0 exactly matches the clean plate
   (smoke fades in from zero)
2. **Deterministic rendering**: All randomness via seeded RNG; any frame can be
   rendered in isolation with `--at`
3. **Zero-motion protection**: Protected regions (faces, hands, key subjects)
   must have exactly 0 pixel change verified via proof reports

## Architecture

```
SmokeScene
├── Emitter[]           # Source locations for smoke columns
│   ├── position        # Base xy coordinates
│   ├── width           # Emitter mouth width
│   └── rise_speed      # Vertical velocity in px/s
├── Billow              # Turbulence/displacement engine
│   ├── curl_field      # Curl-noise domain warping
│   └── density_field   # Periodic FFT noise for density
└── render()            # Frame loop with preroll
```

### Key Components

**Emitter**: Defines where smoke originates. Each emitter has:
- Position and width at the smoke source
- Rise speed and spread angle
- Color gradient from base to top
- Opacity and density parameters

**Billow**: The turbulence simulation using:
- Curl field domain warping for natural billowing motion
- Periodic FFT noise that tiles seamlessly
- Height-dependent turbulence scaling

**Preroll**: 8 seconds of simulation before frame 0 so smoke is
already established (not appearing from nothing) when rendering starts.

## Usage

### As a registered effect

```yaml
# In a recipe YAML
layers:
  - type: smoke_v2
    emitters:
      - position: [540, 1200]
        width: 80
        rise_speed: 45
        color_base: [60, 50, 40]
        color_top: [180, 175, 170]
    preroll_s: 8.0
    mask: masks/smoke_region.png
    protect: masks/faces_hands.png
```

### Command-line interface

```bash
# Render a smoke scene
python -m motionplates.effects.smoke_v2 \
    --plate plates/scene.png \
    --config smoke_config.json \
    --out out/smoke_test \
    --duration 6.0 \
    --fps 30

# Check a specific frame
python -m motionplates.effects.smoke_v2 \
    --plate plates/scene.png \
    --config smoke_config.json \
    --at 2.5

# Generate zero-motion proof report
python -m motionplates.effects.smoke_v2 \
    --plate plates/scene.png \
    --config smoke_config.json \
    --proof-report qc/smoke_proof.json
```

## Configuration

### Emitter Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `position` | [x,y] | required | Emitter center in plate pixels |
| `width` | float | 60 | Emitter mouth width in pixels |
| `rise_speed` | float | 40 | Vertical velocity in px/s |
| `spread` | float | 0.3 | Lateral spread factor |
| `color_base` | [r,g,b] | [50,45,40] | Smoke color at base |
| `color_top` | [r,g,b] | [170,165,160] | Smoke color at top |
| `opacity` | float | 0.7 | Maximum smoke opacity |
| `density` | float | 1.0 | Density multiplier |

### Billow Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `curl_scale` | float | 0.003 | Curl field scale |
| `curl_strength` | float | 25 | Curl displacement strength |
| `noise_lo` | float | 120 | Low frequency noise scale |
| `noise_hi` | float | 8 | High frequency noise scale |
| `evolution_rate` | float | 0.4 | Noise evolution speed |

### Scene Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `preroll_s` | float | 8.0 | Preroll time in seconds |
| `seed` | int | 0 | RNG seed for determinism |
| `fps` | float | 30 | Frame rate |
| `ramp_in_s` | float | 0.5 | Fade-in duration from frame 0 |

## QC and Proofs

### Zero-Motion Reports

The `zero_motion_report()` function generates proof that protected regions
have exactly zero pixel change:

```python
from motionplates.effects.smoke_v2 import SmokeScene, zero_motion_report

scene = SmokeScene.from_config(config)
report = zero_motion_report(scene, plate, protect_mask, frames=[0, 30, 60, 90])

# report contains:
# - max_diff: maximum absolute difference (must be 0)
# - changed_px: count of changed pixels (must be 0)
# - frames_checked: list of frame indices
# - status: "PASS" or "FAIL"
```

### Integration with Engine QC

The smoke v2 module integrates with the main engine's QC system:

```yaml
# In recipe YAML
qc:
  protect_masks:
    - masks/faces.png
    - masks/hands.png
  max_motion_px: 0  # Zero tolerance for protected regions
```

## Implementation Notes

### Periodic FFT Noise

The density field uses periodic FFT noise for seamless tiling:

```
noise(x, y, t) = Σ IFFT(band_k * exp(i·φ(t)))
```

where each frequency band has its own phase evolution rate,
creating multi-scale turbulence without visible seams.

### Curl Field Domain Warping

The curl field provides divergence-free displacement:

```
curl(x, y) = [∂ψ/∂y, -∂ψ/∂x]
```

where ψ is a potential field derived from layered Perlin noise.
This ensures smoke moves in natural, swirling patterns without
artificial compression or expansion artifacts.

### Preroll System

To ensure smoke appears established at frame 0:

1. Simulation runs from t = -preroll_s to t = duration
2. Smoke state at t = 0 already has 8+ seconds of evolution
3. Frame 0 uses `ramp_in` opacity fade so the delta from plate is 0
4. The `frame0_residual_fade_s` parameter controls the fade duration

## Constraints and Limitations

1. **No plate displacement**: Smoke is an overlay only; the underlying
   plate pixels are never warped
2. **Mask-bounded**: Smoke is clipped to the smoke mask; it cannot
   extend beyond the designated region
3. **Memory**: Full-resolution noise fields can be large; consider
   proxy mode for iteration
4. **Speed**: ~2-3 fps at 1080x1920 without optimization

## See Also

- `AGENTS.md` - Repository conventions and hard rules
- `docs/ARCHITECTURE.md` - Overall system architecture
- `docs/CURRENT-SYSTEM.md` - Current animation system overview
- `src/motionplates/effects/smoke_drift.py` - Earlier smoke implementation
