# flames_v1 — painted-fire animation for Posterity plates

Self-contained R&D engine that animates the **fires already painted on a still plate**: licking tongues,
flicker with a colour-temperature shift, light spill synced to that flicker, and rising sparks.
Everything that is not fire light stays exactly the plate. It composes with `../smoke/smoke_v2.py`,
which is imported read-only and never edited.

## The rules it's built for
- Must read on a phone (360x640) within 1 s. No strobing. Plate-level brightness swing stays well under 10 %.
- **Zero warp** of faces, land, water or sky. The sea never moves. The only moving content is the flames'
  own emitted light, displaced **vertically only** (`map_x` is exactly the pixel column), so there is no sway or swivel.
- No vignette, letterbox, watermark or text. The only camera move is the same 1.00→1.06 StablePush as smoke_v2.

## How it works
1. **Matte.** A per-flame key (high value plus a large R−B difference, or a yellow-white core) is limited to that flame's `region`
   polygons. `add` polygons are unioned in and `protect` polygons are cut out. The result is split into connected components,
   and each component gets its own ROI, noise mapping, clock and seed. Blobs smaller than `min_area` or `min_h` are dropped,
   which removes glints and lit rims.
2. **Emissive model.** `bg = min(plate, inpaint-fill)` over the dilated matte, and `E = plate − bg ≥ 0`. The light that moves
   is `E_move = E · key · edge-feather · protect-keepout`. Output = `plate + (W(E_move)·F^temp − E_move)`, so wherever
   nothing moves the pixel is the plate, bit for bit.
3. **Tongues** (`W`). Vertical-only remap by `D = amp·gain·L(y)·N(x, y + rise·t)`:
   - `L` ramps from 0 at the base to 1 near the tips, so the base is anchored.
   - `N` is smooth noise with a long vertical wavelength (`scale_y·hc`) that travels **upward**. Whole tongues stretch
     and retract (`lick_hz`) instead of folding.
   - `gain` is auto-set so the 99.5th-percentile vertical stretch `|dD/dy| ≤ slope_max` and the column shear
     `|dD/dx| ≤ shear_max`. Shear is what reads as squiggles.
   - Rising soft gaps (`breakup`) cut into the tips, and body turbulence (`flow`) adds variation. A thinned flame goes
     redder, not grey.
   - Warm-order caps stop moved light from ever making a pixel bluer than the plate's own fire.
4. **Flicker.** A sum of smoothstep random walks at 0.55, 1.3 and 2.9 Hz, all below 5 Hz. Amplitude is `amp`, stronger at the tips.
   Channel exponents `temp = [1, 1.35, 1.9]`: brighter reads whiter, dimmer reads redder.
5. **Spill.** Multiplicative warm light, `exp(−(d/r)²)` away from the flame key, `r = radius_k·hc`, clipped to
   [`radius_min`, `radius_max`]. It's driven by the **same clock** as its flame and zeroed in protects.
6. **Sparks.** Deterministic Poisson particles born at the tops of the keyed columns. They rise with deceleration,
   drift and wobble, cool from yellow to red, and get a motion-blur streak plus glow. They're confined to a soft column
   above the flame, minus protects. Births start 10 s before t=0, and the global `preroll` means frame 0 is mid-life.
7. **Pre-roll.** Everything is evaluated at `t + preroll`, so nothing fades in.

## Run
```
PY=/workspace/mpvenv/bin/python
$PY flames_v1.py --config configs/b13_three_torches_flames_v1b.json --seconds 7 --out poc/NEW.mp4
$PY flames_v1.py --config CFG --preview 360 --seconds 4 --out scratch/NEW_prev.mp4     # quick look
$PY flames_v1.py --config CFG --proof proofs --stats                                  # zero-motion proof + swing/flicker numbers
$PY flames_v1.py --config CFG --stills proofs/stills_NEW --times 1 2.5 4             # 360x640 before/after + full-res
$PY flames_v1.py --config CFG --smoke ../smoke/configs/b13_three_torches.json --out poc/NEW.mp4   # flames + smoke_v2
$PY flames_v1.py --reel configs/reel_v1.json --out final/NEW_reel.mp4               # hard-cut reel
```
The writer is libx264 (preset slow, crf 21; reels crf 22, yuv420p, faststart) and is called with `-n`, so it **never overwrites**.
PNG writers refuse to overwrite too. Always give a new output name.
Render speed is about 0.07 s per frame for B13 and 0.12 s per frame for P05 (28 fires) at 1080x1920. A 7 s clip takes about 20–30 s.

## Config (JSON)
Top level:
- `plate`, `seed`, `preroll` (s), `push` [1.0, 1.06], `push_center`, `protect_feather` (px)
- `protect`: polygons, never touched (0 px)
- `guards`: named boxes that the proof checks are 0
- `flames`: a list of flame entries; each overrides any of `FLAME_DEFAULTS` in `flames_v1.py`

Main per-flame keys:

| key | default | meaning |
|---|---|---|
| `region` / `add` / `protect` | – | polygons that limit, force or exclude the matte |
| `key` | v_min .70, rb_min 70, core_v .92 | fire key thresholds (raise them on sun-lit plates) |
| `min_area`, `min_h`, `grow` | 60, 12, 7 | component filters; matte dilation, which is the bg-fill zone |
| `tongue`, `tongue_px_max` | 0.12, 38 | tongue amplitude as a fraction of the component height, plus a px cap |
| `scale_x`, `scale_y`, `lick_hz` | 0.6, 2.5, 1.8 | finger width (fraction of width), vertical wavelength (fraction of height), lick rate |
| `base`, `free` | 0.10, 0.75 | height fractions: anchored below `base`, full motion above `free` |
| `slope_max`, `shear_max` | 0.7, 0.6 | auto-gain limits (no folding, no squiggle) |
| `breakup`, `flow`, `fringe`, `soften` | .45, .10, 1.0, 0 | tip gaps, body turbulence, reach above the matte, blur of moved light (use ~2 for defocused fires) |
| `flicker` | amp .10, tip .8, temp [1,1.35,1.9], rates [.55,1.3,2.9] | – |
| `spill` | strength .55, radius_k 1.4, radius 40–260, tint [1,.82,.6] | `region` limits it |
| `sparks` | rate 5 per 100 px of height per s, min_h 40, life 1.2–2.6 s, v0 90–200 px/s, size 1–2.2 | `zone` limits it |

## Shipped configs
- `configs/b13_three_torches_flames_v1b.json`: Edward II B13, two wall torches plus the defocused foreground torch
  (`soften 2`), with the four faces protected.
- `configs/p05v2_town_flames_v1b.json`: Ugarit P05 v2, the whole town below the horizon, auto-split into 28 fires.
  Sky, sea, ships, sun glitter and shore glitter are protected. The key is raised so sun-lit walls don't key.
- `configs/b10_cresset_flames_v1b.json`: Edward II B10 gate cresset, with Kent and the gaoler protected. Used for stills.
- `configs/reel_v1.json` → `final/flames_v1_reel.mp4`.
- `*_flames.json` (no `_v1b`) are the first drafts that made the `poc/*_v1.mp4` clips. They have smaller tongues and bigger sparks.

## Proofs
`--proof` renders 15 frames (every 0.5 s, push off) and writes `proofs/proof_<name>.json` and `diff_<name>.png`.
The diff image shows plate | frame | |diff|×6, with the flame zone in green, protects in blue and guards in red. It checks four things:
- full effect vs plate outside (flame zone ∪ spill ∪ sparks) is 0
- flames-only (spill and sparks off) outside the flame zone is 0
- max diff inside protects is 0
- every guard is 0

`--stats` reports:
- plate swing: (max − min) / mean of the whole-frame mean luma
- flame-zone swing and its spectrum (peak, f95, energy above 5 Hz)
- clock spectrum
- flicker rms
- tongue amplitudes in px


## LOCKED 2026-10-30 (owner): flames = flames_v4 / torch_v1c, all fire sizes
* The owner locked flames on **flames_v4 / torch_v1c** for every fire size, from candles and torches up to the large plate fires. Owner's words: "much better for the larger flames in our plates, simple and does the job".
* What it is: the painted flame shape holds, with a coherent glow and a local spill pulse at v1c strength, each on ONE scalar per frame per static map. There's no tongue, warp, displacement or moving light gradient. Protects stay at 0 px (verified by the impulse test).
* Reference: `final/flames_v4_reel.mp4` (md5 e22c080aef829f6ad0984da3df4f4eb4). Code: `flames_v4.py` + `configs/reel_v4.json`. Preset: `motion/PRESETS.md` section "torch_v1c (LOCKED 2026-10-30 by owner)".
* flames_v1–v3 / v3b are R&D only. Don't use them for new shots.
