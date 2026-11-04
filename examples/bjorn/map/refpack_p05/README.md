# Björn Ironside P05 refpack: animated atlas, 17.50-23.75 s, native 9:16 (2026-11-03)

Built by Atelier from `../../map-reference-data.md` (Archivist; md5 62c4384a3ce5ce1575f940f032143b83, mtime 2026-11-03 06:42:45 EST).
Generator: `make_refpack_p05.py` (deterministic). It refuses to overwrite without `--force` and writes only inside this folder.

## Storyboard version
v2 (P05 is **CUT**, P05-ALT runs) is superseded by `STORYBOARD-v3.md`. v3's header reads "OWNER-APPROVED, VO v3 LOCKED" and "Supersedes: STORYBOARD-v2.md", and P05 **RUNS** in it. This pack follows v3: one native 9:16 frame running from Scandinavia and the Frankish coast down to Iberia and North Africa.
- The solid ink AB route runs Spain-Africa, Rhône, Italy, and ends at an unlabelled coastal end-mark.
- The broken, paler legendary leg points toward Rome.
- The fleet marker is nameless (sails only, no medallion).
- No Luna label or mark. MapTrace about 4.5 s, no hold.

The changes from v2 that matter here are CUT→RUNS, Scandinavia in the framing, the fleet marker and no hold. OWNER-REVISION-2026-11-03 item 6 also applies: a few key locations, with documented and legendary geography kept distinct.

## Use these
| file | what |
|---|---|
| `img/bjorn_p05_9x16_ref_clean.png` | **image-model input**: 1080x1920 RGB. Coast, c. 860 realm tints, inked borders, rivers. No route, dots, labels or zones |
| `img/bjorn_p05_9x16_ref_annotated.png` | registered reference: clean + P05 route (solid documented, broken legendary), other legs dotted, place dots + P-codes, no-data hatch, safe/label/compass zones, caption band, legend |
| `img/bjorn_p05_9x16_zones_overlay.png` | transparent zones overlay (v2b colours) |
| `img/bjorn_p05_9x16_realm_ids.png` | realm-id raster (index = `realms[].index` in the JSON, 0 = sea/no data) for registration QA |
| `img/bjorn_p05_contact.png` | clean \| annotated side by side, 1092x1000 |
| `route_places_p05.json` | frame, zones, all 23 places (out + plate px), all legs (polylines, type, P05 order, QA), end-mark, allow-list, realms, build log |
| `PLATE-PROMPT_p05.md` | owner plate prompt (Báthory v2 format) |

## Frame (native 9:16, spherical LAEA, north up)
- proj4: `+proj=laea +lat_0=40.7 +lon_0=3.0 +x_0=0 +y_0=0 +R=6371000 +units=m +no_defs`
- Size: out 1080x1920, plate 2160x3840 (plate px = 2 x out px). At 2.09259 km/out px, the frame is 2260 x 4017.78 km.
- px: `x = X/2092.59 + 540`, `y = 960 - Y/2092.59`
- Corners (lon, lat): TL (-16.011, 57.622), TR (22.011, 57.622), BL (-7.843, 21.982), BR (13.843, 21.982). Centre (3.0, 40.7). Top centre is about 58.8N.
- Push 1.06 (centred assumed). The crop in source px is [30.6, 54.3, 1049.4, 1865.7]. With a 1080x1920 source, the push renders 1.06 output px per source px, within the 1.5 limit. Paint the plate at 2160x3840 and it is 0.53.
- Safe areas (v2b): title_safe [54,96,1026,1824] (green); pin_safe [64,96,1015,1824] (orange).
- Push-adjusted title-safe in source px: [81.5,144.9,998.5,1775.1].
- Caption third: nothing at or below out y 1280 after the push = **source y 1261.9** (magenta band).
- Label zones: blue, bbox + 10 px pad. Compass: red (ornament_reserved) [89,576,279,766]. Medallion: none (v3).
- Every place sits inside the push title-safe and above source y 1261.9. The lowest is Nekor at y 1246.8, which is the binding constraint on the frame.

Why one frame and not the Archivist's pan plus Luna-Rome inset (§5): v3 specifies a single native 9:16 frame. The width needed (Galicia to Rome) gives a frame tall enough to reach southern Scandinavia while keeping the route band above the caption line.

Scandinavia only shows as Jutland, the Danish isles, and the tips of southern Norway and Scania, mostly in the top push margin (y < 145). Moving the frame further north would push Nekor below the caption line.

## Places (map-reference-data.md §1, coordinates verbatim)
| code | place | out px | P05 role | overlay label |
|---|---|---|---|---|
| P7 | Algeciras | 177.6, 1185.8 | stop (start of S4) | **allowed** |
| P8 | Strait of Gibraltar | 174.2, 1193.7 | waypoint | no |
| P9 | Nekor | 244.0, 1246.8 | stop | **allowed** |
| P10 | Orihuela | 375.1, 1095.3 | stop | **allowed** |
| P14 | Camargue | 597.8, 809.0 | stop (overwinter) | **allowed** |
| P15 | Rhône (mouth) | 611.3, 819.3 | waypoint | **allowed** |
| P17 | Pisa | 823.8, 787.6 | **unlabelled end-mark** (AB 860 Italian raid) | no (v3) |
| P18 | Luna | 807.6, 770.4 | none: no mark, no label | **never** |
| P19 | Rome | 914.1, 876.2 | legendary target, not touched | no |

The JSON also holds off-P05 places, with dots in the annotated image only: P1 Loire 352.9,605.4; P2 Galicia 116.4,821.8; P3 Asturias 198.9,801.2; P4 Beja 86.5,1074.8; P5 Guadalquivir 142.6,1146.9; P6 Seville 160.9,1116.8; P11 Mallorca 539.3,1017.6; P12 Menorca 584.1,998.7; P13 Formentera 475.7,1065.7; P16 Valence 611.2,734.4; P20 Medina Sidonia 159.0,1166.4; P21 Pamplona 358.8,842.7; P22 Nîmes 592.1,792.8; P23 Arles 602.6,801.2.

## Legs (map-reference-data.md §2)
P05 draw order:
| order | leg | from→to | type | style | length |
|---|---|---|---|---|---|
| 1 | S4 | Algeciras → Strait → Nekor | documented | solid ink | 108.6 px / 227 km |
| 2 | S5 | Nekor → Orihuela | documented | solid ink | 236.2 px / 494 km |
| 3 | S7 | Orihuela → Rhône mouth → Camargue | documented | solid ink | 425.9 px / 891 km |
| 4 | S9 | Camargue → Pisa (end-mark) | documented | solid ink | 261.9 px / 548 km |
| 5 | P05-LEG | Pisa → toward Rome, stops at sea 12.4 px (~26 km) short | legendary | broken, paler | 172.8 px / 362 km |

Solid total: 1032.6 px. Every P05 leg has 0 land px outside the inland spurs.

Not drawn in P05 (polylines in the JSON):
- documented: S2, S3, S8 (Rhône river to Valence)
- legendary: S10 (to Luna), S11
- uncertain: S1, S2a, S6 (Balearics), S12, S13

**Routing method:** sea legs use Dijkstra on a 540x960 sea grid from NE 10m land, keeping about 17 km offshore. Inland places take a straight spur from the nearest sea cell. Lines are simplified with Douglas-Peucker at 1.5 px, then Chaikin x3. River legs follow NE 10m river centrelines. These routes are schematic: no source gives a track.

## Label allow-list (overlay only, never on the plate)
**Algeciras, Nekor, Orihuela, Camargue, Rhône.** These are documented P05 stops or waypoints from the §6 list. The allow-list is a ceiling; v3 may use none ("no readable text").
- Excluded: Pisa (v3 says the end-mark is unlabelled); Rome (legend-only in P05); Luna (never).
- Also excluded: the Balearics and Loire (uncertain legs), Galicia, Guadalquivir and Valence (off-P05 legs), Seville, Pamplona and the Strait (optional or disputed in §6).
- Data line 5: names only, with no dates, captions or claims.
- Label font in the reference: IM Fell English SC 40 px. The zones in the JSON (`zones.label_zones_bbox_nopad`) exclude the pad.

## Data sources
- `map-reference-data.md` §1 places, §2 legs and types, §4 realm OHM relation IDs, §5 framing bbox (W-11 E15.5 S34.5 N48, all inside this frame), §6 labels.
- OpenHistoricalMap (CC0) geometry: `../sources/ohm_860_geom.json` (md5 5f87248e82c328f35bb51d3bf5665829), fetched by the Archivist. It contains 14 relations.
- Natural Earth 10m (public domain): land, lakes, rivers_lake_centerlines, from `engine-rnd/maps/sources/naturalearth`.
- No relief is used. ETOPO1 on the box ends at 34N and 60N and would leave a seam.

## Realms (OHM c. 860, suggested pigments only; the owner style governs)
| index | realm | pigment | land share of frame |
|---|---|---|---|
| 1 | West Francia | weathered royal blue | 6.7% |
| 2 | Emirate of Córdoba | crimson | 6.0% |
| 3 | Papal lands | deep antique gold | 0.7% |
| 4 | Lotharingia | ochre | 2.8% |
| 5 | Brittany | slate | 0.6% |
| 6 | Asturias | sage | 2.1% |
| 7 | Pamplona | umber | 0.1% |
| 8 | Aghlabids | sienna | 4.1% |
| 9 | Eastern Roman Empire | muted purple | 0.3% |
| 10–14 | Benevento, Naples, Sorrento, Bari, Venice | olive, teal, light teal, rose madder, grey-blue | ≤0.1% each |

## Data gaps and conflicts (flagged, not guessed)
1. **No border data** for Provence, the Kingdom of Italy, East Francia, Nekor/Idrisids, Britain, Scandinavia, Corsica or Sardinia (§4 says these are not in OHM). They are hatched in the annotated image and plain in the clean one. The P05 stops at Camargue, the Rhône mouth, Pisa and Nekor all sit in no-data land. Shepherd pl. 56 in `../sources` is a possible trace source if the Archivist verifies it.
2. **Scandinavia** has no points, realms or legs in the data; it appears only as NE coastline.
3. **OHM overlaps:**
   - West Francia and the Eastern Roman Empire both claim the Balearics. Both claims are dropped (lon 1.0–4.6, lat 38.5–40.2): 3 WF parts and 4 ERE parts.
   - Pamplona sits inside West Francia, and a West Francia/Lotharingia strip on the Meuse/Scheldt overlaps. Both are resolved **smaller realm wins** (1961 out px).
   - Capua (2888915) and 2740130 are absent from the geometry file.
4. **Strait** (P8) is 2.1 km outside the Córdoba polygon edge, and **Camargue** is 8.2 km outside West Francia. Both sit in no-realm land, which is consistent with §4's Provence note.
5. **Pisa:** §6 lists it as a label, but v3 makes the P17 end-mark unlabelled. v3 wins.
6. **Legendary leg:** v3 says "to Rome", but §2 S11 says stop short and do not touch Rome. The leg stops short.
   - It starts at Pisa, not Luna (S10), because v3 forbids any Luna mark.
   - The documented S9 arc passes Luna's coast unmarked.
7. **Realm fills:** §4 suggests "loose, low-contrast fills", but the owner's style calls for strong pigments. Strong pigments are used (owner rule); flag for Vellum.
8. **S7** is drawn from Orihuela, as §2 allows ("Balearics or Orihuela"). The Balearics leg S6 is uncertain and off.
9. **Off-P05 documented legs:** S2, S3 and S8 are documented but off, because v3's route starts "between Spain and Africa".
10. **Dense Provence cluster:**
    - Camargue to the Rhône mouth is 16 px, and Pisa to Luna is 24 px.
    - Nekor's label zone had to sit raised and to the west.
    - The S4 path makes a small hook west to the P8 Strait waypoint.
    - Orihuela's inland spur doubles back.
11. **Guadalquivir/Rhône** river snap errors are 10.7 and 7.6 px, which is fine for off-P05 legs.
12. `raw/geo/ohm3.json` (cited by the data) contains tags only; the geometry came from `ohm_860_geom.json`.

## Files and md5
```
b5b2f01db1078c3f892fc4b891319a6d  img/bjorn_p05_9x16_realm_ids.png
4f9b79c29696b217a5286004dc84de7a  img/bjorn_p05_9x16_ref_annotated.png
dc6d40b8595fa2d6902b9a56d3012ff9  img/bjorn_p05_9x16_ref_clean.png
12cd28a87cd498aa641819205682d8a1  img/bjorn_p05_9x16_zones_overlay.png
214931e57c5c18e9abf4976014ba1d1c  img/bjorn_p05_contact.png
ec022f640832d88b5ab055e874be6be6  route_places_p05.json
a133e74c4854b5ed0bc79c7c5b9f0950  PLATE-PROMPT_p05.md
715a12b88ae59245f4bade6575103ec7  make_refpack_p05.py
```
