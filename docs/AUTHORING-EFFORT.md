# Authoring effort — measured (box clock, this build) and revised estimate

All times are wall-clock minutes as measured on the box while building PoC A/B (one agent, interactive viewing of crops at full resolution). "First time" includes inventing/tuning the primitive; "repeat" is what a recipe costs once primitives and presets exist. The old 1–2 h/plate estimate is replaced by the table below.

## What each plate needed
| | PoC A `seq07b` Augustus/bier | PoC B `seq08` corridor |
|---|---|---|
| Layers (polygons) | `subject` (1 polygon, 58 vertices), `fg_left` (2), `fg_right` (2) | `mid_column` (1, GrabCut-refined), `mid_stands` (2, GrabCut-refined), `fg_rubble` (1), `fg_bottom` (1) |
| Alpha elements | 3 banners (polygon each) | 1 banner |
| Clean plate | 9 petal cuts (6 GrabCut, 3+ luma-threshold, ellipse seeds), fill of the removed petals (smooth normalised-conv base + haze noise, hand/robe excluded as sources) | none |
| Inpaints (disocclusion) | bg behind subject/FG, subject behind FG: 3 two-stage TELEA fills, ~1.3 s total | 5 fills, ~1.9 s total |
| Effects | parallax_push, petal_fall (24 extra copies), flame_flicker x2 (+local light), banner_sway x3, fabric_ripple (pall), dust_motes | parallax_push, flame_flicker x2, torch_light (+shadow field), banner_sway, dust_motes |
| Exported stack | clean plate + 7 RGBA layer PNGs (`--export-layers`) | clean-plate-less stack: bg + 5 layer PNGs |

## Measured time (first time, per task)
| Task | PoC A | PoC B |
|---|---|---|
| Read plate, grid crops, locate flames/banners/petals | ~8 min | ~6 min |
| Layer polygons + first QC | ~11 min | ~7 min |
| Petal segmentation (grabcut/luma seeds) | ~6 min | n/a |
| Clean-plate fill R&D (TELEA -> push-pull -> speck detect -> TELEA+exclude -> normalised-conv + noise) | ~25 min (one-off R&D; now a reusable `clean_plate.method`) | n/a |
| Fix artefacts found at 100% zoom (soldier edge ghost, arm edge, disocclusion smear, stands/rubble ghosting) | ~10 min | ~8 min |
| Effect placement/tuning (flames, banners, light) | ~6 min | ~4 min |
| Unattended render (8 cores) | 95 s (1.75 fps) | 150 s (1.06 fps) |
| Fast iteration (`--at t1,t2` stills) | 5 s per set | 5 s per set |
| **Plate-specific total, first time** | **~65 min** (about 40 min excluding the one-off fill R&D) | **~25 min** |
| Engine + 7 primitives + tests + docs (one-off, shared by all plates) | ~2.5 h | |

## Revised estimate per plate (with recipes + presets)
| Plate type | Authoring | Unattended render | Notes |
|---|---|---|---|
| Effects-only (dust, flame/torch light, banners with 1 polygon, gentle uniform push; no layer split, no clean plate) | **5–8 min** | 1.5–3 min | locate flame coordinates (auto-suggest from luminance blobs is a 20-line tool), copy preset, 2 stills checks |
| Layered parallax (3 depth layers, 1–2 banners) | **15–25 min** | 2–3 min | polygons dominate (8–12 min), then 1–2 artefact-fix rounds (mask grow / depth reduction fixes most ghosts) |
| Layered + removed-object animation (petals, embers) | **35–50 min first plate of a kind, 20–30 min repeat** | ~2 min | seed ellipses per object and a clean plate that looks natural at 100% zoom is the long pole |
| Reuse of an existing recipe on a near-identical composition (e.g. second Augustus beat) | **5–10 min** | 2 min | re-aim anchors/polygons only |

Daily-publishing view: at ~1 motion plate/day, budget **20–30 min of attention/day** (not 1–2 h) if most plates are effects-only or layered-parallax, with a petal-class hero shot at most weekly. Compute is not the constraint (2–3 min unattended per plate).

## What would cut it further
1. Auto-suggest tools: flame/bright-blob finder, banner/column candidate polygons from edges (mask proposals), so polygon authoring becomes "accept/adjust" (~3–5 min).
2. A segmentation model (SAM-class) for layer masks — not installed here; GrabCut inside a band is the current edge-aware step.
3. Parallax depth is intentionally small (a few %) and masks are grown generously; that policy removes most manual cleanup.
4. Speed: stack caching + ROI-only warps (banner/element warps are full-frame today) would roughly double fps; not needed for daily cadence.
