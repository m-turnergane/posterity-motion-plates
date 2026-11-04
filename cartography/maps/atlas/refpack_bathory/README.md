# refpack_bathory - Báthory short, B03 map beat (README v1)

Written 2026-10-31 12:07 ET. Architecture (same as the Edward pack, `atlas/refpack/`): the owner paints a clean plate (no labels, routes or icons); the engine registers it to geodata and animates the pins, labels, medallion and any realm tint on top. Geodata is the truth, never the painting.
**Authority:** `standalones/bathory/v2/MAP-PLACES-bathory-v1.md` (Archivist). Pins, names, anchors, rivers and realms follow it exactly. This pack is **not PENDING**.

## Use these
- `PLATE-PROMPT.md`: the single paste-ready prompt. Attach `img_v1/bathory_b03_9x16_ref_notext.png`.
- `framing_refpack_bathory_v1.json`: frame `bathory_b03_9x16` (1080x1920, plate 2160x3840). It holds the proj4, projected and lon/lat bounds, km/px, pin/title safe areas, a per-place safe-area check (with the Wikidata-vs-MAP-PLACES delta and the realm under each pin), label zones, the medallion zone, the ornament_reserved (compass) zone, and the realm legend and coverage.
- `control_points_refpack_bathory_v1.json`: 17 primary CPs (confluences and Váh/Danube/Oder/Morava/Dyje bends) and 8 secondary settlement CPs, all in out px and plate px, with scaled thresholds. Same schema as `control_points_refpack_v2.json`.
- `img_v1/bathory_b03_9x16_`:
  - `ref_notext`: the guide. Relief, hillshade, 500/1000/1500 m form lines, rivers and lakes. No text, dots or borders, so it is period-neutral.
  - `ref_labels`: the same with pins and the four MAP-PLACES labels.
  - `ref_graticule`: the labels image plus a 0.5° graticule.
  - `zones_overlay`: green = title-safe; orange = pin-safe; blue = label zones (+10 px); magenta = medallion; red = compass.
  - `realm_ids`: COARSE OHM realm masks, for engine pigment only.
- `make_refpack_bathory.py`: the generator. It reuses `atlas/refpack/refpack_lib.py` and `make_refs.py` read-only, and refuses to overwrite.

## Frame (native 9:16, spherical LAEA)
- proj4 `+proj=laea +lat_0=49.5 +lon_0=17.55 +x_0=0 +y_0=0 +R=6371000 +units=m +no_defs`. The engine forward is `map_route_v1.LAEA` and the inverse is `map_modes_v2.inverse_laea`.
- 200.0 x 355.56 km, so **0.18519 km/px** (185.185 m/px out; 92.6 m/px on the plate).
- Projected bounds: x ±100 000 m, y ±177 777.8 m.
- Lon/lat envelope: 16.118–18.982 E × 47.893–51.099 N.
  - Corners: TL 16.118E 51.090N; TR 18.982E 51.090N; BL 16.209E 47.893N; BR 18.891E 47.893N.
- Pin-safe area [64,96,1015,1824]; title-safe area [54,96,1026,1824].
- Medallion zone [789,54,1026,291] (upper-right). Compass zone [832,384,1026,578].
- Why this frame:
  - The width follows the MAP-PLACES suggested span (Vienna at the west edge; Bytča and Zsolna inside).
  - The south edge is held at about 47.89 N, just north of the Danube's Komárom–Esztergom reach. This keeps Ottoman Esztergom/Párkány out of frame, per MAP-PLACES.
  - The suggested 47.9–49.5 N × 16.3–19.0 E crop is landscape-shaped (about 200 × 178 km). A native 9:16 frame of that width needs about 356 km of height, so the frame extends **north to about 51.1 N**: White Carpathians, Javorníky/Beskids, the Moravian Gate and the upper Oder. That ground is calm and gives the medallion and label margins.

## Places (all inside the pin-safe area). Source: Wikidata P625, read live 2026-10-31 (entity JSON, lastrevid given); identical to MAP-PLACES (delta ≤ 5 m)
| key | on-screen name (MAP-PLACES 1610) | Q-id (rev) | lat, lon | out px | band |
|---|---|---|---|---|---|
| csejte (PIN) | Csejte | Q612364 Čachtice Castle / Csejtei vár (2512685565) | 48.72472, 17.76083 | 623.5, 1425.4 | VERIFIED |
| csejte_manor | (no label; inset split only) | Q337440 Čachtice village / Csejte (2535936920) | 48.71222, 17.78722 | 634.0, 1432.9 | COARSE stand-in, 2.4 km / ~12 px from the castle |
| bytca (PIN) | Bytča | Q1968071 Bytča Castle (2478934103) | 49.22000, 18.55917 | 935.8, 1125.5 | VERIFIED (town Q27907 49.22278, 18.55806, rev 2563023334) |
| vienna | Vienna (anchor; on screen only if the owner wants) | Q1741 (2553605752) | 48.20833, 16.37250 | 68.8, 1731.9 | anchor |
| pozsony | Pozsony (never "Bratislava"; anchor) | Q1780, hu label "Pozsony" (2562607249) | 48.15170, 17.10931 | 363.4, 1769.1 | anchor |
| vagujhely | Vágújhely (optional; unlabelled) | Q376987 (2532117524) | 48.78333, 17.83333 | 652.1, 1390.1 | optional |
| trencsen | Trencsén (optional; unlabelled) | Q145002 (2530368079) | 48.89417, 18.04056 | 733.7, 1323.1 | optional |
| zsolna | Zsolna (optional; unlabelled) | Q25797 (2530368296) | 49.21667, 18.73333 | 1004.1, 1126.5 | optional |

Cross-checks:
- Wikipedia (en): Čachtice Castle 48.725, 17.7608; Čachtice 48.72, 17.78; Bytča 49.22, 18.56.
- Natural Earth 50m populated places: Bratislava 48.150, 17.117; Vienna 48.202, 16.365. Each is within 1 km of Wikidata.
- No pin at Sárvár or Vienna. Vienna and Pozsony are drawn only as small anchor dots on the reference.

## Data sources
- **Land and lakes:** Natural Earth 10m (engine `sources/naturalearth`).
- **Rivers:**
  - NE10m `rivers_lake_centerlines`: Danube, Morava, Oder, Vistula.
  - NE10m `rivers_europe` supplement (naciscdn.org): Váh, Dyje, Svitava, Nysa Kłodzka and others. The core file has no Váh.
  - Danube and Váh are drawn heavy.
- **Relief:** ETOPO1 (NOAA NCEI), via the ERDDAP `etopo180` subset 45–52 N, 13–23 E. The engine's `etopo1_eu.nc` stops at 20 E.
- **Realms:** OpenHistoricalMap (CC0) relations, fetched via the OHM Overpass API.
- The scratch inputs are in `/tmp/bathory_scratch/`, outside the pack and not deliverables. Re-running needs them.

## Realms: COARSE (masks only; never painted from the reference)
| colour (realm_ids) | realm | OHM source | frame share |
|---|---|---|---|
| 37,91,157 | Kingdom of Hungary (Royal Hungary) | union of county relations 2830015 Pozsony, 2830018 Nyitra, 2829775 Trencsén, 2829772 Bars, 2829771 Turóc, 2829458 Árva, 2829427 Zólyom, 2829455 Liptó, 2829043 Sopron, 2829044 Moson (dated 1050/1350–1850) | 25.2% |
| 180,40,40 | Archduchy of Austria | 2830626 Austrian Circle 1565–1618 | 6.9% |
| 60,160,70 | Moravia | 2830504 Moravia 1182–1742 | 25.3% |
| 200,160,40 | other Bohemian Crown lands (Silesian duchies) | 2830430 Lands of the Bohemian Crown 1557–1635, minus Moravia | 38.8% |
| 140,70,170 | Poland (Kraków Voivodeship) | 2696433, 1400–1773 | 1.4% |
| 128,128,128 | unassigned: do not tint | none | 2.4% (SE corner; Komárom/Esztergom/Hont/Győr counties are not in OHM) |

Every pin falls in the right realm: Csejte, Bytča, Pozsony, Vágújhely, Trencsén and Zsolna are in Hungary; Vienna is in Austria.

## Registration plan (Edward method, `atlas/refpack/REGISTRATION-PLAN-v2.md`, scaled to this frame)
1. **Generate:**
   - Generate the plate at 2160x3840 and downsample to out px for the QA numbers.
   - If the aspect or size is wrong, centre-crop or pad only. Never stretch.
2. **Coarse fit:**
   - Run ORB + RANSAC affine between the plate and `ref_notext`, after converting both to gradient magnitude.
   - Fallback: 4-point affine from the Danube–Morava, Dyje–Morava, Nysa–Oder and Váh-elbow CPs.
3. **Per-CP match:**
   - Use a 56x56 gradient-template NCC on the plate at 2x scale.
   - Search radius: 40 px out (80 on the plate) for river features, 60 px out for settlements.
   - Accept a match at NCC ≥ 0.6.
4. **Warp:**
   - Fit a TPS (RBF, smoothing 5) on the accepted primaries plus the coarse-affine prior.
   - Leave-one-out: while the worst LOO residual is > 12 px out, drop that CP and refit.
   - Fallbacks: piecewise-affine, then affine-only.
   - Warp limit: 2.5% of the min side = **27 px out (≈ 5.0 km)**. If the warp needs more, regenerate.
5. **Plate gates** (inland frame, so there is no coast chamfer):
   - At least **12 of 17 primary CPs** must be accepted.
   - **River chamfer:** rasterise the Danube and Váh as NE centerlines and compare them with the plate's river-ink ridge. Pass at median ≤ 2 px and p95 ≤ 5 px out.
   - Coverage gap: east of the Váh below Bytča (the Strážov/Tribeč hills) has no primary CP. The Váh chamfer and the Csejte/Bytča settlement CPs carry that region.
6. **Pins:**
   - Pins are always drawn from geodata, never from a painted vignette.
   - Settlement CPs are secondary checks of the warp only.
7. **Policy:**
   - Accept when the gates pass and no CP fails.
   - Local-correct (one TPS refit with the flagged CPs dropped) when at most 2 CPs flag.
   - Regenerate the plate when the warp is over the limit, fewer than 12 primaries are accepted, the chamfer fails, the Váh doesn't run east of Csejte to Bytča, a compass or ink sits in the medallion or label zones, or any text appears.

### QA thresholds (per CP, after warp; out px with km at 0.18519 km/px)
- The px gates are the same as Edward's. The km values are scaled from the Edward Britain row (4/8 px ≈ 1.6/3.0 km at 0.37–0.65 km/px) to this frame.
- **pass:** ≤ 4 px **and** ≤ 0.74 km.
- **flag:** ≤ 8 px **and** ≤ 1.48 km.
- **fail:** > 8 px or > 1.48 km.
- Story pins get a tighter check. Csejte's castle-to-manor offset is only about 12 px, so the inset must use the castle point (Q612364). On a flag at Csejte, use a local correction, never a moved pin.

## Caveats
- **9:16 vs the suggested crop:** see the "Why this frame" notes above. The frame runs north to 51.1 N, so Moravia and Silesia take about 64% of the area. Hungary is *not* the whole frame east of the Morava. It is the southern and eastern band, roughly the Váh valley and south of the Javorníky/Beskid line.
- **Ottoman conflict in OHM:** the single OHM Ottoman relation 2860343 (1540–1669) reaches into the SE of the frame: 18 940 px, about 18.32–19.03 E, 47.84–48.27 N. That is a whole-period envelope. In 1610 Érsekújvár was Habsburg, and MAP-PLACES says the frontier is out of frame. So it is **not** masked or tinted, and it is flagged to the Archivist.
- **No geometry for Hungary in OHM:** OHM "Kingdom of Hungary" (rel 2750054) has no geometry, so the Hungary mask is built from county relations. Those are dated 1050–1850, not 1610-specific, and some southern counties are missing, which leaves the grey SE corner.
- **Váh–Danube confluence:** it lies at Komárom (about 47.76 N) and is out of frame. The Váh leaves the frame bottom near 17.9 E.
- **Moravia/Silesia boundaries** are OHM-coarse; there are enclave islands of Moravia inside Silesia.
- **Labels:** Vienna and Pozsony labels are reference-only; they appear on screen only if the owner wants them. No river, range, realm, date or status labels anywhere (MAP-PLACES must-nots).
- **Build note:** during a first test run, a variable-shadowing bug wrote the two JSONs into `atlas/refpack/` as *new* files (`*_bathory_v1.json`). They were removed within a minute, the script was fixed, and no existing file there was touched. The `atlas/refpack/` listing is unchanged.

## Files and md5 (README.md cannot list its own md5; it is given in the hand-off report)
| md5 | path |
|---|---|
| c6137503ddb80e193843b34e2c98c5bd | PLATE-PROMPT.md |
| c34e5867ebd8dc82a544290e394e6ab3 | control_points_refpack_bathory_v1.json |
| 9d9737e8dc02e53a9713ff023be0d9bd | framing_refpack_bathory_v1.json |
| 8b595b978ee9d955d1088d9dfef16e10 | img_v1/bathory_b03_9x16_realm_ids.png |
| defe59f4bf1159c728d60280f1119d95 | img_v1/bathory_b03_9x16_ref_graticule.png |
| d50d3a288f5fe1dd40e75364d28a7075 | img_v1/bathory_b03_9x16_ref_labels.png |
| f013d525f7252a9487469ce4d519430f | img_v1/bathory_b03_9x16_ref_notext.png |
| 37569554010651e4f7346aec14e02f56 | img_v1/bathory_b03_9x16_zones_overlay.png |
| 08c1af99451eb5ea1b1d33e24925f4f6 | make_refpack_bathory.py |
