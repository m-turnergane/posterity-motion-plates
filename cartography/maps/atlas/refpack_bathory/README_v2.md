# refpack_bathory - Báthory short, B03 map beat (README v2, option (b))

Written 2026-10-31 12:20 ET. Vellum picked option (b): crop tight on the Váh valley so Upper Hungary fills the frame, and drop Vienna. Pozsony was to be kept only if it fit naturally. It does not fit (it falls at x = −488 px), so it is dropped. **v1 is kept unchanged** (README.md, PLATE-PROMPT.md, *_v1.json, img_v1/). The md5s were re-checked after this build.
Architecture as v1/Edward: the owner paints a clean plate; the engine registers it to geodata and animates the pins, labels, medallion and realm tint. Geodata is the truth.
**Authority:** `standalones/bathory/v2/MAP-PLACES-bathory-v1.md`, with 1610 names. Pins are Csejte (Q612364) and Bytča (Q1968071). The manor is a COARSE stand-in (Q337440). No pin at Sárvár or Vienna. No modern borders or names, and no dates or status words.

## Use these
- `PLATE-PROMPT_v2.md`: the single paste-ready prompt. Attach `img_v2/bathory_b03v2_9x16_ref_notext_v2.png`.
- `framing_refpack_bathory_v2.json`: frame `bathory_b03v2_9x16`. It holds:
  - proj4, projected and lon/lat bounds, km/px, pin and title safe areas;
  - a per-place check: MAP-PLACES delta, in-frame and pin-safe flags, and the realm under each pin;
  - label zones, the medallion and compass zones, realm shares, Váh stats, and the Pozsony and Danube notes.
- `control_points_refpack_bathory_v2.json`: 29 primary CPs (13 on the Váh: 6 confluences and 7 bends) and 6 secondary settlement CPs, in out px and plate px, with scaled thresholds. Same schema as v1 and Edward.
- `img_v2/bathory_b03v2_9x16_`:
  - `ref_notext_v2`: the guide. ETOPO 2022 15″ hillshade, 400/700/1000/1300 m form lines, and OSM rivers with the Váh heavy. No text, dots or borders.
  - `ref_labels_v2`: pins and the 2 labels.
  - `ref_graticule_v2`: adds a 0.25° graticule.
  - `zones_overlay_v2`: green = title-safe; orange = pin-safe; blue = label zones (+10 px); magenta = medallion; red = compass.
  - `realm_ids_v2`: COARSE OHM masks for the engine tint only.
  - `labels`, `graticule` and `zones` are 256-colour PNGs to save disk. `ref_notext` is full RGB.
- `make_refpack_bathory_v2.py`: the generator. It reuses `atlas/refpack/refpack_lib.py` and `make_refs.py` read-only. It asserts that every output path is inside this folder and refuses to overwrite.

## Frame (native 9:16, spherical LAEA, north up)
- proj4: `+proj=laea +lat_0=48.8 +lon_0=18.2 +x_0=0 +y_0=0 +R=6371000 +units=m +no_defs`.
- Size: 85.0 × 151.11 km, so **0.07870 km/px** (78.70 m/px out; 39.35 m/px on the plate 2160x3840). That is 2.35× tighter than v1 (0.18519).
- Projected bounds: x ±42 500 m, y ±75 555.6 m.
- Lon/lat envelope: 17.6117–18.7883 E × 48.1191–49.4795 N.
  - Corners: TL 17.6117/49.478; TR 18.7883/49.478; BL 17.6275/48.1191; BR 18.7725/48.1191.
- Safe areas: pin-safe [64,96,1015,1824]; title-safe [54,96,1026,1824].
- **Medallion** [789,54,1026,291], upper-right.
- **Compass** (ornament_reserved) [54,384,248,578], upper-left. It was chosen by a calm-score search (0.64) because the upper right now holds the medallion and Bytča.
- **Label zones** (bbox; +10 px pad in the overlay and the prompt):
  - Csejte [73,1000,188,1049], side N.
  - Bytča [753,320,861,356], side NW.
- **Pins:**
  - Csejte (130.7, 1065.2) and Bytča (871.4, 365.8). Both are in pin-safe and in Hungary.
  - They are 1018.7 px (80.2 km) apart, about 61 mm on a 6.1″ phone.
- Why this frame:
  - It came from a grid scan of centre and width.
  - It maximises the Hungary share with an Ottoman-envelope overlap of 0, and keeps Bytča below the medallion.
  - Both pins are in pin-safe, and the Váh is continuous from the east edge (Strečno/Zsolna) to the bottom edge (about 48.12 N, near Sered').

## Places (Wikidata P625 as v1; deltas to MAP-PLACES ≤ 3 m)
| key | on-screen (1610) | Q-id | lat, lon | out px | status |
|---|---|---|---|---|---|
| csejte (PIN) | Csejte | Q612364 | 48.72472, 17.76083 | 130.7, 1065.2 | VERIFIED; labelled |
| csejte_manor | (no label) | Q337440 | 48.71222, 17.78722 | 155.2, 1083.0 | COARSE stand-in, 2.4 km / ~30 px from the castle |
| bytca (PIN) | Bytča | Q1968071 | 49.22000, 18.55917 | 871.4, 365.8 | VERIFIED; labelled |
| pozsony | Pozsony | Q1780 | 48.15170, 17.10931 | −488.0, 1868.6 | out of frame, so dropped (allowed) |
| vagujhely | Vágújhely | Q376987 | 48.78333, 17.83333 | 198.7, 982.7 | optional, unlabelled |
| trencsen | Trencsén | Q145002 | 48.89417, 18.04056 | 391.9, 826.8 | optional, unlabelled |
| zsolna | Zsolna | Q25797 | 49.21667, 18.73333 | 1032.2, 369.6 | optional, unlabelled; in frame but outside pin-safe (x > 1015) |
Vienna (Q1741) is dropped per option (b). **On-screen labels: Csejte and Bytča only.**

## Data sources
- **Rivers:**
  - OpenStreetMap waterway=river named ways (ODbL, © OpenStreetMap contributors), from Overpass (private.coffee mirror) on 2026-10-31.
  - The Váh spine is OSM waterway relation 3509398 (Q202598), main_stream members. The plain name match left a gap at the Sĺňava/Piešťany reach.
  - Drawn: the Váh at 3.2 px plus named rivers with ≥ 12 km near the frame at 1.5 px. NE10m had only the Váh and Hron at this scale.
- **Relief:** ETOPO 2022 v1 15-arcsec (NOAA NCEI, doi:10.25921/fd45-gt74), from ERDDAP, 47.6–49.8 N × 17.0–19.5 E. In frame it runs about 100–1700 m.
- **Land:** Natural Earth 10m.
- **Realms:** OpenHistoricalMap (CC0), the same relations as v1.
- Scratch inputs are in `/tmp/bathory_scratch/` (not deliverables; re-running needs them): `etopo2022_15s_bathory.nc`, `osm_rivers_v2.json`, `osm_vah_rel.json`, `ohm_*.json`, `wd/*.json`.

## Realms: COARSE (masks only; never painted from the reference)
| colour | realm | frame share |
|---|---|---|
| 37,91,157 | Kingdom of Hungary (Upper Hungary counties: Pozsony, Nyitra, Trencsén, Bars, Turóc, …; OHM) | **77.52%** |
| 60,160,70 | Moravia (OHM 2830504) | **20.42%**, an NW wedge |
| 200,160,40 | other Bohemian Crown (Silesia/Teschen) | 0.10%, a top-edge sliver |
| 180,40,40 | Austria | 0.00% |
| 140,70,170 | Poland | 0.00% |
| 128,128,128 | unassigned: do not tint | 1.96% (SE edge; Hont/Esztergom are not in OHM) |
| (Ottoman OHM 2860343 envelope) | not masked | **0.00% overlap**: the SE Ottoman corner is avoided |

**The Moravia wedge is not thin.** It covers 770 px of the top edge and 899 px of the left edge, down to about y = 900 at the left edge. The White Carpathians/Javorníky border runs diagonally just NW of the Csejte–Bytča line, so any north-up 9:16 frame holding both pins in pin-safe includes it.
- In the scan, about 15% was the floor, and only with Bytča at about y = 225, under the medallion.
- With Bytča kept clear of the medallion, the range was 19–21%.
- Runner-up: centre (18.225, 48.775), 90 km wide, gives Moravia 19.2% but Ottoman 0.6%.
- The compass zone sits in this wedge on purpose: calm ground away from the story.

## Registration plan (Edward method, scaled)
1. Generate at 2160x3840 and downsample to out px. Crop or pad only; never stretch.
2. **Coarse fit:**
   - ORB + RANSAC affine on gradient magnitude against `ref_notext_v2`.
   - Fallback: 4-point affine from CP02 (Rajčanka–Váh), CP04 (Teplička–Váh), CP01 (Horný Dudváh–Váh) and CP08 (Malá Nitra–Nitra).
3. **Per-CP match:**
   - 56x56 gradient NCC at 2x.
   - Search radius 40 px out for river features, 60 px for settlements.
   - Accept at NCC ≥ 0.6.
4. **Warp:**
   - TPS (smoothing 5) on the accepted primaries plus the affine prior.
   - LOO rejection while the worst residual is > 12 px.
   - Fallbacks: piecewise-affine, then affine.
   - Warp limit: 2.5% of the min side = **27 px out ≈ 2.1 km**. Over that, regenerate.
5. **Gates** (inland, so there is no coast chamfer):
   - At least **12 of 29 primaries** accepted.
   - **Váh chamfer** (OSM relation centerline against the plate's river-ink ridge): median ≤ 2 px and p95 ≤ 5 px.
   - The Váh must run unbroken from the east edge to the bottom edge, passing east of Csejte and south-west of Bytča.
6. Pins always come from geodata. Settlement CPs are secondary warp checks only.
7. **Policy:**
   - Accept when the gates pass.
   - Local-correct when at most 2 CPs flag.
   - Regenerate when the warp is over the limit, fewer than 12 primaries are accepted, the chamfer fails, the Váh is broken, ink or the compass falls in the medallion or label zones, or any text appears.

### QA thresholds (per CP after warp; 0.07870 km/px)
- **pass:** ≤ 4 px **and** ≤ 0.315 km.
- **flag:** ≤ 8 px **and** ≤ 0.63 km.
- **fail:** > 8 px or > 0.63 km.
- The px gates are Edward's; the km values are px × km/px.
- The Csejte castle-to-manor offset is now about 30 px, so the two dots are visibly distinct. The inset still uses the castle point (Q612364) as the pin.

## Caveats
- **Moravia** is 20.4% (an NW wedge), not a thin edge. This is forced by the geometry; see above.
- **Danube:** out of frame (the bottom edge is 48.12 N). The Váh–Danube confluence at Komárom is out too, as is the Váh's upper course (Liptó/Turóc above Strečno). "The Váh fully visible" therefore means its whole Zsolna-to-Sered' reach, the part that links Bytča and Csejte.
- **Pozsony and Vienna:** both are off-frame, so no anchor labels. The only on-screen names are Csejte and Bytča.
- **Zsolna** is in frame but outside pin-safe (optional and unlabelled, so harmless).
- **Some primary CPs lie in Moravian ground** (CP11, CP14, CP23, CP27). They are valid geometry anchors, but the painter may render those small Czech rivers faintly. They are not needed for the 12-CP gate.
- **River list:** the generator's ≥ 12 km list is measured on a 0.1°-buffered box, so a few names (Morava, Malý Dunaj, Ipeľ, Olše) are near-frame rather than in-frame. Only their in-frame parts are drawn, if any. The framing JSON `sources.rivers` text says "Vah heavy" from the named ways; the drawn spine is relation 3509398.
- **Hungary mask:** built from OHM county relations (1050–1850, not 1610-specific). The unassigned SE edge is 2%.
- **Attribution:** OSM data is ODbL and needs "© OpenStreetMap contributors" in the credits if the shipped map uses it. ETOPO and NE are public domain; OHM is CC0.

## Files and md5 (README_v2.md cannot list its own md5; see the hand-off report)
| md5 | path |
|---|---|
| cf8a1add6950414ff8cbcde3f8232eec | PLATE-PROMPT_v2.md |
| 22e381c1c02c6de85501dc5440cf9462 | framing_refpack_bathory_v2.json |
| b473dd4b0c6aa76026d4423e93d0d93a | control_points_refpack_bathory_v2.json |
| 5ae05fb3ab37092ef1371d1688ccc7a7 | make_refpack_bathory_v2.py |
| 8c1a19112db52c41eb6344658f923cf5 | img_v2/bathory_b03v2_9x16_realm_ids_v2.png |
| 3e4b0c2df69f109377d08714b7f1d22c | img_v2/bathory_b03v2_9x16_ref_graticule_v2.png |
| eeff34b2dda64114779da9515395fb3b | img_v2/bathory_b03v2_9x16_ref_labels_v2.png |
| 1576c1ad3e7dd1734dea75d3b13640e7 | img_v2/bathory_b03v2_9x16_ref_notext_v2.png |
| 3c55f305047a29e30afb94e9504baf21 | img_v2/bathory_b03v2_9x16_zones_overlay_v2.png |
