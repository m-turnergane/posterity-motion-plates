# Current Animation System (2026-10-30)

This document describes the Posterity motion-plates animation system as of
October 30, 2026. It consolidates the production engine, locked presets,
R&D modules, and QC tooling into a single reference.

## System Overview

The animation system adds restrained, painterly motion to selected Posterity
plates. The guiding principle is **subtlety over spectacle**: motion should
enhance the painting without calling attention to itself.

### Core Components

```
motionplates/
├── core/                    # Plate loading, layers, engine, encoding
│   ├── plate.py            # Bar detection, cover-fit (matches build scripts)
│   ├── layers.py           # Layer extraction, masks, inpainting
│   ├── engine.py           # Frame loop, residual fade, metrics
│   └── encode.py           # Lossless intermediate → delivery encode
├── effects/                 # Per-effect modules with @register decorator
│   ├── smoke_v2.py         # Procedural smoke overlay (LOCKED)
│   ├── flame_flicker.py    # Flame warp, color shift, local light
│   ├── parallax_push.py    # Eased 2.5D camera push
│   └── ...                 # petal_fall, banner_sway, dust_motes, etc.
├── standalone/              # Production-ready standalone modules
│   └── fx_candle.py        # Candle/fire light spill (LOCKED params)
└── rnd/                     # Research modules (not production)
    ├── natural_fire.py     # Procedural flame tongues (R&D)
    └── flame.py            # Flame simulation primitives
```

### Production Pipeline

1. **Plate** loaded with bar detection + cover-fit (identical to build scripts)
2. **Layers** extracted via polygon masks and optional GrabCut refinement
3. **Clean plate** generated for occluded areas (TELEA inpaint + haze)
4. **Effects** applied per-layer via registered effect modules
5. **Frame loop** composites layers, applies particles, fades residual
6. **Encode** lossless intermediate → delivery H.264 with verified output

## Locked Presets

Two presets are **APPROVED-DEFAULT** for production use:

### `house-candle-lightspill-v1`

Single-source candle/torch light with:
- Flame warp (inside flame mask only, 0 px elsewhere)
- Light spill with falloff × facing heuristic
- Light pool (radial darkening that breathes with the flame)
- Flicker curve: 4 sine bands + smoothed noise, floor 0.45

**Config:** `recipes/presets/locked/house-candle-lightspill-v1.json`
**Reference md5:** `030cbcbb8bbb5977066975a5c7f5b9e7`

### `house-map-inknib-dashed-v1`

Animated map with:
- Dashed route drawn with nib-style ink (wet→dry transition)
- Cloud shadows with softness and drift
- Parchment light sweep
- Ink markers with bloom

**Config:** `recipes/presets/locked/house-map-inknib-dashed-v1.json`
**Reference md5:** `b8aa9ceb7cae2757a44d9919eb8ddd9f`

### Applying Locked Presets

```bash
# Copy the locked preset (NEVER edit the original)
cp recipes/presets/locked/house-candle-lightspill-v1.json \
   configs/myshow_myplate_candle_v1.json

# Edit the copy: set plate, name, out_dir, seed
# Draw masks: flame, relight, protect
# Tune: source.xy, flame_warp, light_spill, light_pool
# QC: --repeat-check, qc_isolation, qc_layers, qc_layermask
```

## Smoke v2 Effect

Procedural smoke overlay with painted-smoke billow. Key features:

- Curl field domain warping for natural billowing
- Periodic FFT noise for seamless fractal textures
- 8-second preroll so smoke is established at frame 0
- Zero-motion proofs for protected regions

See `docs/SMOKE-V2.md` for full documentation.

## Candle/Fire Standalone Module

Production module for single-source candle and small fire animation:

- Light spill with inverse-square-ish falloff
- Facing heuristic based on luminance × warmth + gradient toward source
- Flame warp constrained to flame mask only
- Deterministic flicker from 4 sine bands + band-limited noise

Parameters are locked to `house-candle-lightspill-v1` values:

```python
LOCK_FLICKER = {
    "amps": [0.15, 0.08, 0.035, 0.015],
    "freqs": [0.55, 1.3, 2.6, 4.4],
    "noise_amp": 0.05,
    "noise_hz": 4.0,
    "floor": 0.45,
    "smooth": True
}
```

## QC Tools

### tools/qc/

| Tool | Purpose |
|------|---------|
| `qc_isolation.py` | Each layer alone: diff outside its mask (must be 0) |
| `qc_layers.py` | Per-layer max displacement inside protect masks |
| `qc_layermask.py` | Max change outside declared mask PNG at sample times |
| `qc_spill_sync.py` | Light spill correlation with flame brightness |
| `qc_phone.py` | Judge renders at phone resolution (360x640) |
| `qc_overlay.py` | Mask overlay visualization |

### Engine QC (built-in)

Every render writes `qc/<name>.qc.json`:

- `plate_outside_max`: max |AFTER − plate| outside layer masks
- `out_outside_max`: same in output space, after camera
- Displacement max overall, outside masks, inside protect masks
- `changed_pct` and `mean_abs_diff`
- Mask overlay still, mid-clip AFTER still, diff heat map

### Zero-Motion Proofs

Protected regions (faces, hands, key subjects) must show **0 px change**:

```bash
python -m motionplates.effects.smoke_v2 \
    --plate scene.png \
    --config smoke.json \
    --proof-report qc/smoke_proof.json
```

## R&D Modules (Not Production)

### Natural Fire (`src/motionplates/rnd/natural_fire.py`)

Procedural flame tongues with:
- Stroke-textured, jagged-edge sprites
- OVER composite in linear light
- Burst dynamics tied to glow peaks
- Height-capped pillar flames

Status: R&D. Not approved for production. See `docs/NATURAL-FIRE-RND.md`.

### Archive (`archive/engine-snapshots/`)

Historical engine versions preserved for regression testing:

- `animate_b3_cb9e2b88.py` - Batch 3 (locked presets reference)
- `animate_b4_96da01a0.py` - Batch 4 (fire-light R&D)
- `animate_b5_b371d67f.py` - Batch 5 (flame_warp, light_pool)
- `animate_b6_886d34e0.py` - Batch 6 (wax stamp, soft wash)
- `animate_b7_a88fde43.py` - Batch 7 (geo_thresh)
- `animate_b9_b719e8d8.py` - Batch 9 (icon stamp, battlemap)
- `battlemap_b9_9422cc91.py` - Battlemap renderer

## Camera

**StablePush**: scale-only center zoom, no pan or rotation.

- Default: 100% → 104% over the AFTER half
- Candle preset: 100% → 104%
- Maximum allowed: 106% (configured via `camera.z1`)

The zoom is eased (smoothstep) so motion never feels mechanical.

## Determinism

All renders are deterministic:

- RNG seeded via `ctx.rng(name, idx) = default_rng([seed, crc32(name), idx])`
- No `time`, no global RNG, no network calls
- x264 with `+bitexact` and fixed threads
- `--repeat-check` verifies identical md5 on a second render

## Hard Rules (from AGENTS.md)

1. Never copy plates into this repo (read from `$MOTIONPLATES_PLATES`)
2. Frame 0 must equal the cover-fit plate (max abs diff 0)
3. Effects start from zero (`ramp_in`), clean-plate swap corrected by fading residual
4. Deterministic: pure functions of `t`, stateless frame loop
5. Restrained motion: camera push a few percent, eased; no Ken Burns
6. Original plate is always the fallback

## Examples

### Edward II Production Build

See `examples/edward-ii/` for a complete production build:

- `BUILD-NOTES-v1.md` - Detailed production notes
- `build_rough_v1c.py` - Full build script
- `fx_v1c.py` - Production effects module

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-10-18 | v0.3 | Last commit before Oct production work |
| 2026-10-22 | batch 1-4 | Engine iterations, locked presets approved |
| 2026-10-23 | naturalfire | Natural-fire R&D (P05 forge) |
| 2026-10-30 | current | Smoke v2, full system integration |

## See Also

- `AGENTS.md` - Repository conventions and hard rules
- `docs/ARCHITECTURE.md` - Detailed architecture
- `docs/SMOKE-V2.md` - Smoke v2 documentation
- `docs/NATURAL-FIRE-RND.md` - Natural fire R&D notes
- `recipes/PRESETS.md` - Full preset documentation (from production)
