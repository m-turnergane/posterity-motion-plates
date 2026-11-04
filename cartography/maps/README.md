# engine-rnd/maps: Edward II long-form maps (v1, native 16:9)

Self-drawing ink-nib routes on a painted basemap built from real geodata, in the locked house look
`house-map-inknib-dashed-v1`. The locked nib engine (`motion/presets/locked/engine/animate_b3_cb9e2b88.py`, `MapLight`)
and `motion/guardrails.py` are imported read-only by path. Nothing locked is edited.

## Authority for places
`longform/edward-ii-feature/MAP-PLACES-v1.md` (Archivist, 30 Oct 2026). Every pin, via and tint in `configs/` names its
row id (`1-01`, `2-08`, ...) and Q-ID. On load, `check_against_authority()` refuses to render if:
- a pin is not a VERIFIED row, or a via/tint is not an OMIT (region) row;
- a Q-ID differs from the list;
- a label is not the row's allowed on-screen text;
- rows in a chain are out of list order.

Map 2 therefore follows the C03a order: Chepstow, Glamorgan, Kenilworth, Berkeley, Corfe, Ireland, Sandwich, Sluis, Normandy,
Languedoc, Avignon, Paris, Brabant, Cologne, Milan.

Coordinates come ONLY from the Archivist's saved Wikidata entity JSON (`raw/wikidata/<QID>.json`, P625, CC0).
`sources/waypoint_coords_wikidata_2026-10-30.json` is used only for the coastline control-point headlands. Its stop entries
(for example Sluis Q10080) are older and are NOT used.

## Shots
| config | content | line style |
|---|---|---|
| `edward_map1_stations.json` | Chepstow → (Glamorgan, region) → Kenilworth → Berkeley → Gloucester; then Corfe, Winchester, Westminster as separate slate-ink pins with no route | solid house nib, filled stamps |
| `edward_map2a_fieschi_claimed_britain.json` | the letter's route, Chepstow → … → Sluis | claimed: short dash, fainter, open-ring stamps |
| `edward_map2b_fieschi_claimed_continent.json` | Britain leg already inked; Sluis → … → Milan (last pin) | claimed |

Regions (Glamorgan, Ireland, Normandy, Languedoc, Brabant) are never pins:
- each one is a soft wash painted into the STATIC basemap, centred on its P625 point;
- the line sweeps through the wash on a rounded corner, so no turning point reads as a located spot;
- only Map 1 labels its region, with the italic letter-spaced "Glamorgan" that row 1-02 allows.

Left out on purpose:
- Map 1: Nottingham, Tyburn, Bristol, Lincoln;
- Map 2: Gloucester and Kent;
- hermitages (2-16..2-18): no pin, text or tint;
- no title, dates, durations, LEGEND/DOCUMENTED tags, vignette or letterbox. The title option "The letter's route" is left to the parent.

## Method
1. **Basemap.** Natural Earth 10m land, lakes and rivers (v5.1.1, public domain, `sources/naturalearth/`).
   - Projected with spherical Lambert azimuthal equal-area, centred per map.
   - Rasterised with 4× supersampling at the 2048×1152 plate size.
   - Painted in the house palette: teal wash sea, ochre parchment, ink coast, paper grain.
   - Static; never upscaled.
2. **Placement.** About 5–8 headlands per map (Wikidata P625) are found on the rendered coast as the extreme land pixel
   in a given direction. A least-squares affine is fitted to them, and the RMS is reported in `proofs/`.
3. **Ink.** The locked `MapLight` nib draws one chain per layer. Pin groups use `MapLight` markers only.
   - Labels use IM Fell English SC (italic: IM Fell French Canon; SIL OFL, installed system fonts). They are rendered at plate
     size and fade in over 0.4 s as each stamp lands, then stay static.
4. **Camera.** One transform: a smoothstep push from 1.00 to 1.06 drifting toward the pins' centroid, as a single
   `warpAffine` with INTER_AREA. A scale of ≤1 is asserted. `guardrails.check_pixel_density` runs in refuse mode:
   2048×1152 → 1920×1080 at a 1.06 push gives a ratio of about 0.99.
5. **Proofs** (`proofs/<shot>.json`):
   - changed pixels outside the ink/stamp/label allow-mask, every frame in plate space, split by land/water/coast;
   - control-point error;
   - phone stats at 640×360 (first-second visibility, share of energy above 5 Hz, 1-second luma swing);
   - the authority rows used.

## Run
```
/workspace/mpvenv/bin/python map_route_v1.py [--reel final/out.mp4] [--still-only] configs/*.json
```
The command writes `final/<shot>_final_16x9.png`, `proofs/<shot>.json` and `poc/<shot>_540p.mp4`. It refuses to overwrite an
existing reel.

To change places, edit the config rows. The authority check will refuse anything MAP-PLACES-v1 does not allow.
