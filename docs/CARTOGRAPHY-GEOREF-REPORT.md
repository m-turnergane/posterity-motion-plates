# Georeferencing the painted Eurasia map (explicit projection + control points)

Map: `tamerlane_eurasia_painted.png`, 941x1672, md5 `1004379863d6234fce808a05654cd055`. Reference geography: Natural Earth 50m coastline / lakes / rivers (public domain). Code: `src/motionplates/cartography/georef.py`; tools: `tools/georef_fit_report.py`, `tools/georef_overlay.py` (extra `[geo]` = pyshp). Data: `assets/georef/`.

## Model
`pixel = warp( project(lon, lat) )`, project = explicit `equirect | mercator | lcc` (Lambert conformal conic, std. parallels 30/55, origin 40N 60E), warp = `affine | poly2 | poly3 | tps`. Everything is plain numpy/scipy, deterministic, and invertible (`to_lonlat`). Recipes then use `{lonlat: [lon, lat]}`; no hand-placed city pixels.

## Control points
9 physical **landmarks** (Cape Comorin, Sri Lanka centre, Cyprus centre, Aral Sea centre, Suez tip, Bab-el-Mandeb, Cape Guardafui, head of Persian Gulf, Crimea centre) with lon/lat from Natural Earth and pixel positions read off the painting by eye on 100 % crops with the overlay. Four **pins** the painter baked in (Samarkand, Baghdad, Delhi, Constantinople) were deliberately *not* used for the fit and serve as independent tests. Caveat: pixel positions are my reading of a painting (+/-5-10 px each); the Aral centre is the most uncertain.

## Results (9 landmarks; `diagnostics/georef/fit_report.json`)
| projection | warp | fit RMS px | leave-one-out RMS px | baked pins RMS px (~km) |
|---|---|---|---|---|
| equirect | poly2 | 13.3 | 49.8 | 46.9 (~288) |
| **lcc** | **poly2** | 14.6 | 54.0 | **28.7 (~182)** |
| mercator | poly2 | 13.4 | 54.5 | 47.0 (~289) |
| mercator / equirect | affine | 34.6-34.7 | 57 | 51-57 (~310-340) |
| lcc | affine | 40.2 | 61.7 | 39.6 (~279) |
| lcc / mercator / equirect | tps | 34-40 | 57-61 | 39-57 |

Chosen: **lcc + poly2** - best independent pin accuracy (Samarkand pin lands 17 px = ~100 km from the painter's pin), not the lowest LOO (differences between poly2 models are within noise for 9 points).

## How far does the painting deviate from real geography?
- Under a plain affine map of any standard projection the painting is off by **~35-40 px RMS at control points and ~280-340 km at the painter's own city pins**: the artist distorts (Arabia and India enlarged, Central Asia compressed).
- The best smooth warp still leaves **~15 px (~90 km) fit error and ~50 px (~300 km) predictive error**; individual places can be 100-200 km off. Rivers, seas and borders in the painting are stylised and will not match Natural Earth line-for-line (see `overlay_lcc_poly2.png`).
- Consequence: lon/lat-driven placement is good for "roughly here" (markers, labels, route directions) but **not** for anything implying exact position, borders or distances. Distances in text come from great-circle math on lon/lat (e.g. Samarkand-Berlin 4,260 km, Archivist-computed), never from pixels. Anything map-positional should carry `approximate: true`.
- To improve: add 8-12 more landmarks picked by a second person, or use poly3/tps with >= 20 points; expect ~20 px LOO.

Berlin (13.4E) falls **west of the painted map edge**: it is shown as a geodesic direction line stopping `edge_margin` px before the edge with an "off the map" label, never a fake marker.

Reproduce: `python tools/georef_fit_report.py assets/georef/tamerlane_eurasia.control_points.json OUT_DIR`; `python tools/georef_overlay.py assets/georef/tamerlane_eurasia.georef.json assets/basemaps/tamerlane_eurasia_painted.png OUT.png`.
