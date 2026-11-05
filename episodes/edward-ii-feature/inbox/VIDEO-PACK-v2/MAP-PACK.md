# MAP PACK v2 — Edward II / Edmund, Earl of Kent (long-form, 16:9)

Status: DRAFT. Atlas bases (AB, AE) not generated and not owner-approved. Built on sources/atlas-refpack-v2 (README-v2 45a278f5, framing_refpack_v2.json 8db7392a, control_points_refpack_v2.json 8081580a, REGISTRATION-PLAN-v2.md b8002aff) and MAP-PLACES-v1.md. v2.1: script v3.2 LOCKED line IDs (11f4e6f9); ledger CLAIM-LEDGER-v3.2 (8e824c98). Script v2/v3 and ledger v3 SUPERSEDED. v2 2026-11-04: registration authority = REGISTRATION-PLAN-v2.1.md; re-timing §4b.

Architecture (owner, 31 Oct): the owner paints one clean base per frame; the engine owns registration, routes, markers, labels, camera, effects and narration sync. Geodata is the truth, never the painting.

## 1. Frames

- **AB = britain_16x9**: out 1920x1080, plate 3840x2160 (2x); centre [-2.55, 51.95], width 705 km, 0.36719 km/px; proj4 `+proj=laea +lat_0=51.95 +lon_0=-2.55 +x_0=0 +y_0=0 +R=6371000 +units=m +no_defs`; pin-safe px [153, 129, 1766, 950]; title-safe px [96, 54, 1824, 1026]; medallion zone [54, 789, 291, 1026]; compass-rose zone [383, 54, 577, 248] (only place a rose may be painted). Labels dropped on this frame: none.
- **AE = euro_16x9**: out 1920x1080, plate 3840x2160 (2x); centre [0.5, 48.5], width 3040 km, 1.58333 km/px; proj4 `+proj=laea +lat_0=48.5 +lon_0=0.5 +x_0=0 +y_0=0 +R=6371000 +units=m +no_defs`; pin-safe px [153, 108, 1766, 972]; title-safe px [96, 54, 1824, 1026]; medallion zone [54, 54, 291, 291]; compass-rose zone [54, 443, 248, 637] (only place a rose may be painted). Labels dropped on this frame: ['Gloucester', 'Bristol', 'Winchester', 'Tyburn'].

Prompts: PLATE-PROMPTS.md §AB / §AE (verbatim refpack v2). Attach `<frame>_ref_tinted_notext.png` (present in the box pack folder sources/atlas-refpack-v2/, but NOT inside the DOCS zip; it ships in the MEDIA zip, see ASSET-TRANSFER-INDEX.md); add `_ref_bare.png` if shapes drift. Map class: Explorer's Chart proposed — OWNER DECISION.

## 2. Registration and QA (authority: REGISTRATION-PLAN-v2.1.md; sources/atlas-refpack-v2/REGISTRATION-PLAN-v2.md is SUPERSEDED on the global-transform step)

1. Generate at exactly 3840x2160 with the tinted_notext guide.
2. Register: ORB (6000 kp) + RANSAC HOMOGRAPHY (reproj 6 px) with a sanity gate, AFFINE fallback if the gate fails, MANUAL 4-point registration as the deterministic last resort (reference script registration/register_atlas_h.py) -> NCC refinement on control points (accept NCC >= 0.6) -> thin-plate spline, smoothing 5. Warp limit: 0.025 x min side = 27 px out.
3. QA thresholds per control point — britain: pass <= 4 px / <= 1.6 km, flag <= 8 px / <= 3.0 km; euro: pass <= 4 px / <= 7 km, flag <= 8 px / <= 13 km. Plate passes with >= 20 primary CPs passing and <= 3 flags; coastline chamfer median <= 2 px, p95 <= 5 px.
4. Realm fills: engine masks from `<frame>_realm_ids.png` (REALMS-1327-v1). Realm names are NOT shown on screen; colour only.
5. Clean-plate rule: any painted text, route, icon, border, cartouche or watermark = regenerate (do not paint out by hand without logging it).
6. A failed plate falls back to the refpack's own tinted render for the beat; log it in QA.

## 2c. Map motion: deterministic engine + OPTIONAL hybrid atmosphere layer (owner, 12:44pm ET)
- **Deterministic engine for:** geography, borders, realm fills, labels, pins, route drawing and pacing. **I2V never draws routes, labels or markers.**
- **NEW: optional HYBRID LAYER TEST.**
  - Atelier Jr may generate a short Higgsfield I2V atmosphere clip from the approved painted map plate:
    - ink blooming at the edges
    - drifting mist or sea shimmer
    - candle-lit parchment
  - **No camera move**, so the plate stays registrable.
  - Composite it UNDER the engine's routes, labels and markers, keeping the realm masks.
- **Invariants:**
  - Coastlines and borders must not drift.
  - Mask the land and border regions, or limit the motion to the sea, margins and vignette.
  - Check the drift: re-register sampled frames against the plate with registration/register_atlas_h.py, or track the control points.
  - If the plate drifts by more than a few px against the registration (suggested yardstick: the 4 px CP pass threshold in §2.3), fall back to engine FX (paper grain or dust_v1 on the still plate).
- **When:**
  - Run ONE map test in the sample phase.
  - The primary opening sample (S001–S010) contains no map beat. So the test runs on **ME1 (S030, AE)** if the optional Act II sample is made.
  - Otherwise it runs as a **standalone 5 s test on the Britain base (AB)**.

## 3. Stops (from framing_refpack_v2.json; out px, plate px = 2x)

### Britain (AB)
| row | name | kind | lon, lat | out px (x, y) | plate px | label side |
|---|---|---|---|---|---|---|
| 1-01 | Chepstow | pin | -2.6757, 51.6439 | 936.4, 632.7 | 1872.8, 1265.4 | W |
| 1-03 | Kenilworth | pin | -1.59111, 52.347 | 1137.4, 418.6 | 2274.8, 837.2 | W |
| 1-04 | Berkeley | pin | -2.45694, 51.68861 | 977.5, 619.1 | 1955.0, 1238.2 | E |
| 1-05 | Gloucester | pin | -2.24654, 51.8673 | 1016.7, 564.9 | 2033.4, 1129.8 | E |
| 1-06 | Bristol | pin | -2.5975, 51.45361 | 951.0, 690.3 | 1902.0, 1380.6 | E |
| 1-07 | Lincoln | pin | -0.55, 53.25 | 1322.3, 141.3 | 2644.6, 282.6 | W |
| 1-08 | Corfe | pin | -2.0589, 50.6399 | 1054.3, 936.4 | 2108.6, 1872.8 | W |
| 1-09 | Winchester | pin | -1.30861, 51.06333 | 1196.3, 806.5 | 2392.6, 1613.0 | E |
| 1-10 | Westminster | pin | -0.12417, 51.49944 | 1417.2, 668.8 | 2834.4, 1337.6 | E |
| 1-11 | Tyburn | pin | -0.164, 51.51286 | 1409.6, 665.0 | 2819.2, 1330.0 | W |
| 1-12 | Nottingham | pin | -1.15472, 52.94917 | 1214.6, 235.0 | 2429.2, 470.0 | E |
| 2-07 | Sandwich | pin | 1.33889, 51.27472 | 1696.3, 724.9 | 3392.6, 1449.8 | W |
| 1-02 | Glamorgan | region_label_only | -3.55, 51.62 | 772.0, 638.6 | 1544.0, 1277.2 | W |
| 2-06 | Ireland | region_label_only | -7.6, 53.15 | 227.2, 277.5 | 454.4, 555.0 | C |

### Europe (AE)
| row | name | kind | lon, lat | out px (x, y) | plate px | label side |
|---|---|---|---|---|---|---|
| 1-01 | Chepstow | pin | -2.6757, 51.6439 | 821.6, 316.3 | 1643.2, 632.6 | SW |
| 1-03 | Kenilworth | pin | -1.59111, 52.347 | 870.3, 268.6 | 1740.6, 537.2 | E |
| 1-04 | Berkeley | pin | -2.45694, 51.68861 | 831.3, 313.6 | 1662.6, 627.2 | NW |
| 1-05 | Gloucester | pin | -2.24654, 51.8673 | 840.9, 301.4 | 1681.8, 602.8 | dropped |
| 1-06 | Bristol | pin | -2.5975, 51.45361 | 824.4, 329.8 | 1648.8, 659.6 | dropped |
| 1-07 | Lincoln | pin | -0.55, 53.25 | 915.8, 206.2 | 1831.6, 412.4 | E |
| 1-08 | Corfe | pin | -2.0589, 50.6399 | 846.0, 387.8 | 1692.0, 775.6 | W |
| 1-09 | Winchester | pin | -1.30861, 51.06333 | 880.2, 359.0 | 1760.4, 718.0 | dropped |
| 1-10 | Westminster | pin | -0.12417, 51.49944 | 932.7, 329.3 | 1865.4, 658.6 | N |
| 1-11 | Tyburn | pin | -0.164, 51.51286 | 931.0, 328.3 | 1862.0, 656.6 | dropped |
| 1-12 | Nottingham | pin | -1.15472, 52.94917 | 889.9, 226.8 | 1779.8, 453.6 | W |
| 2-07 | Sandwich | pin | 1.33889, 51.27472 | 996.9, 345.0 | 1993.8, 690.0 | S |
| 2-08 | Sluis | pin | 3.3883, 51.3089 | 1086.8, 340.3 | 2173.6, 680.6 | W |
| 2-11 | Avignon | pin | 4.80833, 43.94861 | 1177.9, 853.5 | 2355.8, 1707.0 | W |
| 2-12 | Paris | pin | 2.35222, 48.85667 | 1045.6, 513.9 | 2091.2, 1027.8 | W |
| 2-14 | Cologne | pin | 6.95778, 50.94222 | 1245.4, 356.3 | 2490.8, 712.6 | W |
| 2-15 | Milan | pin | 9.19, 45.46694 | 1387.1, 729.0 | 2774.2, 1458.0 | W |
| 1-02 | Glamorgan | region_label_only | -3.55, 51.62 | 783.4, 316.2 | 1566.8, 632.4 | W |
| 2-06 | Ireland | region_label_only | -7.6, 53.15 | 619.4, 195.1 | 1238.8, 390.2 | C |
| 2-13 | Brabant | region_label_only | 4.75, 50.75 | 1148.8, 376.7 | 2297.6, 753.4 | S |

Pins vs regions (MAP-PLACES): Glamorgan, Ireland, Normandy, Languedoc, Brabant = region labels or tints only, never pins. Sandwich and Sluis are VERIFIED pins. Vercelli is not mapped (no year, no pin).

## 4. Beats (v2.1, script v3.2 LOCKED; TCs from SHOT-LIST v2.1)

| beat | frame | shot | line | est. TC in | est. dur s | what the engine draws | claims |
|---|---|---|---|---|---|---|---|
| MB1 | AB | S013 | L13 | 1:49.5 | 9.2 | Chepstow pin; Glamorgan as region label only (no pin, C26 disputed spot). Documented line (continuous ink) Chepstow -> Glamorgan label area. No date on screen. | C25, C26 |
| MB2 | AB | S014 | L14 (part, 11 of 17 words: "He was taken to Kenilworth Castle, in the middle of England,") | 1:58.7 | 4.6 | Documented line continues to the Kenilworth pin; arrival hold, then cut to N03 on "and there he lost his crown." | C25 |
| MB3 | AB | S019 | L18 | 2:27.5 | 5.8 | Documented line Kenilworth -> Berkeley pin; arrival hold >=1.2 s. | C06 |
| MB4 | AB | S021 | L20 | 2:39.5 | 5.4 | Lincoln pin only, no line (C20: no date on screen). | C20 |
| MB5 | AB | S053 | L51 | 6:13.3 | 5.0 | Westminster and Tyburn pins, 1330 colour, no connecting route; no gallows or execution marker. | C12, C13 |
| MB6 | AB | S091 | L92 | 12:08.9 | 9.2 | Berkeley, Gloucester and Corfe pins lit equally, no route, no arrows. v3.2 L92 ("But belief is not proof ... most historians still hold that he died at Berkeley") still fits: the pins hold the question; nothing on the map endorses either answer. | C16e-a, C16a |
| ME1 | AE | S030 | L29 (part, 22 of 34 words) | 3:37.2 | 9.2 | Camera glide from Britain to the Avignon city point; NO Kent route line. Avignon pin + ink-in label only. | C09 |
| ME2 | AE | S071 | L70 | 9:07.2 | 15.4 | Fieschi's CLAIMED route, dotted: Corfe -> Ireland (region label) -> Sandwich -> Sluis. VO: "...crossed to Ireland ... came back to England dressed as a hermit ... crossed the sea to the mainland of Europe." No dates, no durations (C03b). | C03a, C03b |
| ME3 | AE | S072 | L71 | 9:22.6 | 10.0 | Dotted route continues: Normandy (region label) -> Languedoc (region label) -> Avignon (pin). VO names only Avignon. | C03a |
| ME4 | AE | S074 | L73 | 9:32.6 | 10.0 | Dotted route continues: Paris -> Brabant (region label) -> Cologne -> Milan. Milan is the last pin; hermitages an unlabelled soft tint south of Milan or omitted (MAP-PLACES-v1 §2). L72 is cut in v3.2, so ME4 now rides L73 ("...living as a hermit in Lombardy, in the north of Italy."). N20 is not placed (RESERVE). | C03a, C03c |
| ME5 | AE | S075 | L74 | 9:42.6 | 6.2 | Slow pull-back over the whole dotted route; labels recede (fade to 40%): the claim seen whole, not endorsed. Kent stays off this map. | C03a (framing) |

Times are estimates (v3.2 word counts / 2.4 words per second; no v3.2 VO has been recorded). Re-time to the recorded VO.

**Label set (v3.2, resolved):** the on-screen labels stay the v2 set (from MAP-PLACES-v1), unchanged: the pins in the table above, with region labels only for Glamorgan, Ireland, Normandy, Languedoc and Brabant. The v3 proposal's extra labels (Lombardy, Pavia, Germany, England, the Low Countries, "south of France") are NOT added: v3.2 speaks "Lombardy, in the north of Italy" and "the mainland of Europe" in the VO, so no new label is needed, and none has Archivist or owner sign-off. Gascony (v3.2 L08) is shown on plate N21, not on a map.

### 4b. Re-timing check (v2.1, script v3.2; 90 px/s draw on AE and AB at full-frame zoom, 1.2 s hold per arrival; /workspace/tmp/vp2/retime_v21.py)

| beat | route | px | need s | allocated s | margin | fix |
|---|---|---|---|---|---|---|
| MB1 | Chepstow->Glamorgan | 164.5 | 3.03 | 9.2 | +6.17 | - |
| MB2 | Glamorgan->Kenilworth | 426.5 | 5.94 | 4.6 | -1.34 | run MB1+MB2 as one continuous draw from S013: 13.8 s available vs 8.97 s needed (+4.83) |
| MB3 | Kenilworth->Berkeley | 256.5 | 4.05 | 5.8 | +1.75 | - |
| ME2 | Corfe->Ireland->Sandwich->Sluis | 793.7 | 12.42 | 15.4 | +2.98 | - (v2 spill into S072 no longer needed) |
| ME3 | Sluis->Normandy~->Languedoc~->Avignon | 735.1 | 11.77 | 10.0 | -1.77 | STAGE (as v2): Sluis->Normandy pre-inked (212.3 px) at the cut; animate 522.8 px = 8.21 s (+1.79) |
| ME4 | Avignon->Paris->Brabant->Cologne->Milan | 1033.6 | 16.28 | 10.0 | -6.28 | STAGE (as v2, kept): Avignon->Paris->Brabant pre-inked (536.2 px); animate Brabant->Cologne->Milan 497.5 px = 7.93 s (+2.07; v2 was +0.37) |

- ME4 staging re-checked: FITS on S074/L73 with +2.07 s. Pre-inking Avignon->Paris only still fails (11.03 s needed vs 10.0 s, -1.03).
- AE run S071-S072-S074 is now 35.4 s (v2: 30.0 s), with 28.56 s of draw and holds; the rest is arrival hold. No act card falls inside a map beat. MB4-MB6, ME1 and ME5 draw no route.
- `~` = approximate region anchors chosen by the desk (Normandy 0.0E 49.2N, Languedoc 3.0E 43.5N), NOT from framing_refpack_v2.json; Atelier Jr may move them inside the region label zone.
- Every beat: RE-TIME TO THE RECORDED v3.2 VO.

## 5. Line grammar and timing

- Documented movement (Map 1, 1326–27: C25, C26, C06) = continuous ink line. Claimed (Fieschi itinerary, C03a) = dotted. Approximate = shaded area. Competing accounts = separate lines, never merged.
- The documented 1326–27 sequence and the claimed journey must never read as one route (different style; ME beats are on the other frame).
- 1330 places (Corfe, Winchester, Westminster, Tyburn, Nottingham) = separate colour, no connecting route.
- Routes oxblood with a parchment keyline. Draw speed <= ~120 px/s (britain), <= ~90 px/s (euro). Arrival holds >= 1.2 s at major stops, >= 0.6 s at waypoints.
- Labels ink in (stroke reveal) on arrival; no title card on the map itself (the intro/act cards are separate CB1 shots: LONGFORM-HOUSE-INTRO-BRIEF.md), no legend box, no dates, no durations, no status words ('claimed', 'disputed') on screen — attribution is in narration.
- Medallion (if used) parks in the medallion zone at wide zoom and never covers a label zone. Kent is never placed on the Europe route.
- Lit-plate rule does not apply to map plates; a light dust_v1 / paper grain pass is optional.

## 6. Open
- Map class (Explorer's Chart vs other) — owner.
- Atlas bases not generated; registration QA not run.
- Whether MB6 uses AB or a crop of AB — Atelier Jr (crop window must stay >= 0.53 of plate width).
