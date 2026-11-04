# engine-rnd/maps: MAPS v2 (stills R&D; v1 files untouched, see README.md)

No animation here. Document reveals stay paused. This folder holds still frames only.

## Files
| file | role |
|---|---|
| `map_modes_v2.py` | Terrain (land, ETOPO relief, distance fields), `realm_weights()` (the REALMS-1327 soft field), `render_mode()` |
| `map_route_v2.py` | StillShot: authority check, geographic router, spline fit + assertions, hand-ink stroke, labels, proofs |
| `build_realms_1327.py` / `verify_realms_1327.py` | Build `sources/realms/realms_1327_v1.geojson`; verify it (geometry 40/40, plus raster checks per still) |
| `configs/edward_map2a_v2.json`, `configs/edward_map2b_v2.json` | 2a: Britain to Sluis (close). 2b: full claimed route to Milan |
| `style/*.png` | four 1920x1080 stills, `style_AB_side_by_side.png`, `style_match_sheet.png` |
| `proofs/edward_map2{a,b}_v2_v2_stills.json` | every number quoted in the report (the double "v2" in the name is cosmetic) |

Run: `/workspace/mpvenv/bin/python map_route_v2.py configs/edward_map2b_v2.json --tag map2b`

## Modes (chosen per shot)
- `realms_worn` (**A, the lead**): worn painted paper and sea, subtle relief, soft realm fills with no border lines, matched to the three owner plates (see `style_match_sheet.png`).
- `campaign_atlas` (**B**): hillshade, procedural forests, rivers, translucent realm washes.
- `terrain_only`: kept in code only, with no deliverable. Parchment is dropped.
- Per shot use `"mode": "realms_worn"`, or crossfade with `"mode_from"`, `"mode_to"`, `"xfade_t"` (0..1). The basemap is static.
- House rules: no title text, place names only (IM Fell), no vignette or letterbox, density ≤ 1.5 (`guardrails.check_pixel_density`, ratio 0.99), and the MAP-PLACES-v1 authority check runs on load.

## Realms (REALMS-1327-v1, followed row by row)
- Geometry: OpenHistoricalMap relations (CC0) where they exist, plus hand-coarse shapes. Each shape cites its R-row and is listed in the geojson `provenance`. There is no aourednik/world_1300 geometry (it is GPL-3.0; the spec says reference only).
- Rendering: each feature is rasterised, given a ±4 km hand wobble, feathered (σ = feather_km/2) and normalised by land. There are no lines.
  - **New: the wobble is pinned to 0 within about 8 km of every verifier checkpoint.** This stops a wobble pushing the Duchy of Burgundy over Dole.
  - **New: core weighting.** Outside its own polygon core, a neighbour's feathered bleed is damped to 35 %. This keeps small units (Montpellier/Majorca) and border towns (Dole) showing their own realm at the 2b scale.
- Verifier facts: Avignon is in Imperial Provence (not papal, not France). Berwick is Scottish. The Dauphiné and the County of Burgundy are Imperial, not French. Montpellier is Majorca, folded into the Aragon hue.

## Route lines
- **Router**: Dijkstra on a plate/4 grid with 8 neighbours.
  - Land cost: `1 + 5(e/1000)^1.6 + 0.012·slope`, with water at 80. Mountains are avoided and the Alps are crossed by the cheapest pass.
  - Sea legs run on strict water cells only. The coast cost is `1 + 4·exp(-d_coast/6 km)`. Harbour cells and a corridor connect each port pin to open water.
  - Pin clearance and separation from legs already drawn are added as costs.
  - Cost-aware string pulling removes the 8-neighbour staircase. `snap_sea` moves sea vias onto open water.
- **Fit**: Gaussian smoothing at σ ∈ {24, 18, 14, 11, 8, 6}, otherwise per-sample adaptive σ. A reversal at a via becomes a Hermite "teardrop" that holds the via exactly.
- **Assertions** (render refuses on failure):
  - land legs have 0 water samples outside harbour discs;
  - sea legs have 0 land samples, with clearance ≥ 2.5 px away from harbours;
  - max turn < 40° per 6 px (no zigzags);
  - the line stays ≥ 3 px from other pins.
- **Stroke**: 4x supersampled stamped nib, width ±25 % slow noise, bleed and grain, tapered ends, an arrowhead on the arrival ring edge, and exact pin-edge arrival (proof `ink_vs_edge_px`).
  - Documented legs: solid iron-gall.
  - Claimed legs: dashed vermilion.
  - All of Map 2 is Fieschi's claim (MAP-PLACES §60), so every Map 2 leg is dashed. The solid style is used by Map 1.
- **Labels**: placed to avoid all ink and to stay in frame. A label must sit nearer its own pin than any other pin (this fixed the Chepstow/Berkeley swap).

## Future (not built)
- **Per-stop close-ups**: the same Terrain and realms at higher zoom (Corfe, Sluis, Avignon, Milan), with density ≤ 1.5 enforced by the guardrail. This needs a higher-resolution DEM/coast per close-up so we do not upscale ETOPO1.
- **Army/route moves**: animate the existing fitted spline by arc length (the stroke already supports partial draw). Unit tokens or arrows would ride the same path. Mode crossfades are already keyed per shot.

## Coarse / placeholder (by design or by source)
- The France outer envelope and Gascony band (hand).
- Ireland's English-lordship tint (hand, east and south-east only).
- The Avignon disc and Rhône east-bank fill.
- `empire_low` (hand plus OHM).
- The Milan Gaussian fringe (R20).
- The Duchy/County of Burgundy edge.
- Forests in B are procedural, not historical.
- Hermitages 2-16..2-18 are UNCERTAIN, so nothing is drawn.
- The Ireland via is an illustrative sea touch about 8 km off Wexford (row 2-06 is a region), snapped to open water.
