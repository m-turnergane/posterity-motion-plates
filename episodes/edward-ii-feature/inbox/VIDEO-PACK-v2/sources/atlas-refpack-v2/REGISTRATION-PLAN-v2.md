# REGISTRATION PLAN v2 - owner plate -> geodata frame

Written 2026-10-31 11:31 ET. Inputs: `framing_refpack_v2.json` (frames, projection, zones), `control_points_refpack_v2.json` (control points + prototype numbers), `img_v2/` (references, realm-id rasters, prototype overlays). Script: `make_regplan.py` (read-only use of engine loaders; NE10m coast/rivers; GAZ headlands; pins from MAP-PLACES-v1 via the authority check).

**Principle.** The geodata is the truth; the painting is a texture. We never move a route, marker, label or realm mask to follow the painting. We warp the PAINTING onto the frame's LAEA pixel grid, and if the painting can't be warped within limits it is corrected or regenerated.

## 1. Spaces
- Frame out px: the `size_px` grid of each frame (1920x1080 or 1080x1920), spherical LAEA R=6371 km, `proj4` per frame in the framing JSON. Every engine overlay is drawn here.
- Plate px: the owner's image, expected at 2x (3840x2160 / 2160x3840). Any size is accepted: it is first scaled by the aspect-preserving factor to 2x, then registered. Control-point `plate_px` = 2 x `px` is only the *expected* location before matching.

## 2. Control points (20-30 primary per frame)
Types, in order of trust:
1. **headland** - GAZ headlands (engine gazetteer) plus extra named headlands snapped to the nearest NE10m coastline vertex (stored lon/lat is the NE vertex, so geodata is the source; the name is a handle only).
2. **river_mouth** - NE10m river centreline end nearest the coast (kept if within 0.35 deg).
3. **confluence** - closest approach of two NE10m rivers (kept if < 0.03 deg, about 3 km).
4. **settlement** (secondary) - MAP-PLACES-v1 pins. Used in the fit only if the plate actually paints a vignette there; otherwise they are QA check points after the fit.
Selection: inside a 5% margin, greedy typed minimum separation 0.045 x min side, at most 28 primary. Search radius in the plate: 40 out px (60 for settlements) around the affine prediction.

## 3. Method
1. **Global**: ORB (6000 kp) on reference vs plate (grey), cross-checked Hamming matches, RANSAC affine (reproj 6 px). Gives scale/rotation/shift and the search prediction.
2. **Per point**: 56x56 px template of the reference gradient magnitude around the CP, normalised cross-correlation in the plate gradient inside the search box, sub-pixel parabolic peak; accept ncc >= 0.6. (Gradient matching ignores the colour difference between the flat reference and the painted plate; a tiny dither prevents flat-sea false 1.0 peaks.)
3. **Robust fit**: thin-plate spline (scipy RBFInterpolator, smoothing 5.0) through the accepted points; leave-one-out residuals; while the worst LOO residual > 12.0 px and > 12 points remain, drop it from the fit and record it as **rejected** (= a place where the painting disagrees with the geodata).
4. **Fallbacks**: fewer than 12 accepted points, or LOO rms above the flag threshold -> piecewise-affine on a Delaunay mesh of the accepted points; if that also flags -> global affine only (from ORB, refined on the accepted points) and the plate is treated as 'needs regen' for anything beyond a wide shot.
5. **Warp limit**: the non-affine part of the displacement at any point must stay <= 2.5% of min(W,H) (27 out px at 1080). Beyond that the painting's geometry is wrong there, and a TPS would visibly smear the art.
6. **Resample**: inverse map out px -> plate px on an 8 px grid, bilinear upsample, cv2.remap (Lanczos for final). Output: the plate in frame space, then the engine draws on top.

## 4. QA
Thresholds (residual = LOO for fitted points, residual vs the final fit for rejected/check points):

| frame kind | pass | flag | fail |
|---|---|---|---|
| euro (about 1.5 km/px) | <= 4 px and <= 7 km | <= 8 px and <= 13 km | above |
| britain (0.37-0.65 km/px) | <= 4 px and <= 1.6 km | <= 8 px and <= 3.0 km | above |

Plate-level gates: pass = >= 20 fitted primary points, no fail, <= 3 flags, no warp-limit breach, coastline chamfer median <= 2 px and p95 <= 5 px; flag = any of: 1-3 fails/rejections, a warp-limit breach, chamfer p95 <= 8 px; fail = otherwise.
- **Coastline chamfer**: segment the registered plate's sea (blue-green wash: k-means on Lab, the cluster covering the reference sea mask) and take the distance transform of the NE10m coast edge; report median/p95 over the plate's coast pixels.
- **Stop check**: every MAP-PLACES-v1 pin and region anchor: is the painted vignette (if any) within flag distance; is the stop on the correct realm in `realm_ids.png` (always true by construction, since masks come from geodata).
- **Overlay image**: registered plate at 75% + NE10m coast in red + CP circles coloured pass/flag/fail with LOO px + non-affine arrows x4 + magenta X for rejected points (`img_v2/<frame>_regproto_qa_overlay.png` is the template).

## 5. Realm masks
Realm fills used by the engine (highlights, pulses, mask-ins) come from `img_v2/<frame>_realm_ids.png` (legend in `framing_refpack_v2.json` -> `realm_id_legend`) or straight from the realm geodata via `realm_masks`, **never** from segmenting the painting. If the painted border is off by more than the flag threshold from the geodata border, the mask wins; the deviation is listed for a local correction.

## 6. Deviation policy
- **Regenerate** (new seed / stronger reference weighting, note what went wrong in the prompt) when: fewer than 15 primary points match, or > 5 fail/rejected, or a warp-limit breach near a stop (within 120 px), or the Alps/Pyrenees/coast of the route corridor (Severn, Dorset, Kent, Flanders, Seine, Rhône, Rhine, Po) is wrong.
- **Local correction** when only 1-3 points fail or are rejected away from stops: (a) let the TPS take it if under the warp limit; (b) else inpaint/paint-over the small region (clone from the plate itself, or a masked img2img pass with the reference crop) and re-run registration; (c) the engine's labels/markers never move.
- **Accept with note** when only flags remain and none is within 120 px of a stop.

## 7. Synthetic-warp prototype (done)
Each frame's `ref_tinted_notext` was warped by a known map: affine (scale 1.025, rotation 0.9 deg, shift 14,-9 px) + smooth random field (max 1.2% of min side) + one local bulge (24,13 px) at a headland (a stand-in for "the generator drew this headland too far out"). Then registered blind with the method above; truth is known, so the real error is measured on every 7th NE coastline pixel.

| frame | primary CPs | fitted | LOO rms / max px | affine-only rms px | match vs truth rms px | coast true err TPS median / p95 px | affine-only median / p95 px | pass/flag/fail | rejected | warp-limit |
|---|---|---|---|---|---|---|---|---|---|---|
| euro_16x9 | 28 | 27 | 1.11 / 2.37 | 3.87 | 0.38 | 0.61 / 3.65 | 3.39 / 7.0 | 27/0/0 | - | - |
| britain_16x9 | 25 | 24 | 1.76 / 3.66 | 5.21 | 0.55 | 0.72 / 5.37 | 3.14 / 10.62 | 24/0/0 | CP02 Portland Bill (25.27 px) | CP02 |
| euro_9x16 | 28 | 27 | 3.16 / 11.76 | 3.92 | 0.49 | 1.18 / 8.04 | 3.28 / 10.28 | 25/1/1 | CP05 Dunnet Head (27.08 px) | - |
| britain_9x16 | 28 | 27 | 2.42 / 7.11 | 4.78 | 0.55 | 0.75 / 7.94 | 3.0 / 7.79 | 19/7/1 | CP02 Flamborough Head (23.88 px) | CP02 |

Reading: per-point matching is sub-pixel against truth (0.4-0.6 px rms); the TPS halves the coastline error of affine-only at the median and roughly halves p95. The local bulge was caught as a rejected point + warp-limit breach in britain_16x9 (Portland Bill), euro_9x16 (Dunnet Head) and britain_9x16 (Flamborough Head) - exactly the 'local correction' trigger. In euro_16x9 the bulge sat at Land's End, whose CP did not match (outside the accepted set), so it was absorbed silently: the coast p95 there is fine but the max (26 px) sits at that bulge -> the chamfer check, not CPs alone, must gate. Max coast errors (25-30 px) are at the bulge or at frame edges away from CPs; the plate-level chamfer gate covers those.

## 8. Control-point tables
`px` = frame out px; plate px = 2 x px. Role: primary (fit) / secondary (settlement; fit only if painted).

### euro_16x9

| id | type | name | role | lon | lat | px | plate px |
|---|---|---|---|---|---|---|---|
| CP01 | headland | Land's End | primary | -5.71522 | 50.0677 | 680.2, 418.5 | 1360.4, 837.0 |
| CP02 | river_mouth | Po mouth | primary | 12.5338 | 44.97 | 1555.3, 741.5 | 3110.6, 1483.0 |
| CP03 | river_mouth | Elbe mouth | primary | 9.819 | 53.5404 | 1348.1, 162.0 | 2696.2, 324.0 |
| CP04 | headland | Cape Finisterre | primary | -9.27222 | 42.8825 | 458.1, 902.9 | 916.2, 1805.8 |
| CP05 | headland | Cap de Creus | primary | 3.3171 | 42.322 | 1106.5, 971.0 | 2213.0, 1942.0 |
| CP06 | confluence | Seine-Marne (Charenton) | primary | 2.4069 | 48.8143 | 1048.2, 516.8 | 2096.4, 1033.6 |
| CP07 | headland | Spurn | primary | 0.13981 | 53.59383 | 945.0, 182.4 | 1890.0, 364.8 |
| CP08 | headland | Pointe de Grave | primary | -1.06 | 45.5701 | 883.3, 745.0 | 1766.6, 1490.0 |
| CP09 | confluence | Rhine-Mosel (Koblenz) | primary | 7.6057 | 50.364 | 1277.8, 394.2 | 2555.6, 788.4 |
| CP10 | river_mouth | Shannon mouth | primary | -8.7385 | 52.6728 | 567.5, 222.9 | 1135.0, 445.8 |
| CP11 | headland | Cap Corse | primary | 9.41666 | 42.83398 | 1418.6, 911.6 | 2837.2, 1823.2 |
| CP12 | headland | Mull of Galloway | primary | -4.8629 | 54.6377 | 741.9, 101.3 | 1483.8, 202.6 |
| CP13 | headland | Den Helder | primary | 4.75889 | 52.95833 | 1140.2, 221.9 | 2280.4, 443.8 |
| CP14 | headland | Selsey Bill | primary | -0.78799 | 50.7227 | 902.7, 383.4 | 1805.4, 766.8 |
| CP15 | headland | Cabo de Penas | primary | -5.8499 | 43.6628 | 637.5, 866.5 | 1275.0, 1733.0 |
| CP16 | confluence | Po-Ticino (Pavia) | primary | 9.2241 | 45.1405 | 1391.3, 751.6 | 2782.6, 1503.2 |
| CP17 | headland | Cap Frehel | primary | -2.3265 | 48.685 | 829.0, 524.6 | 1658.0, 1049.2 |
| CP18 | headland | Cap Sicie | primary | 5.8604 | 43.0497 | 1235.2, 913.2 | 2470.4, 1826.4 |
| CP19 | headland | Braich y Pwll (Lleyn tip) | primary | -4.7616 | 52.7906 | 736.6, 230.9 | 1473.2, 461.8 |
| CP20 | confluence | Loire-Vienne (Candes) | primary | 0.0754 | 47.2182 | 939.7, 630.0 | 1879.4, 1260.0 |
| CP21 | headland | Orford Ness | primary | 1.5798 | 52.0808 | 1006.6, 288.2 | 2013.2, 576.4 |
| CP22 | headland | Pointe du Raz | primary | -4.74111 | 48.04028 | 714.1, 563.9 | 1428.2, 1127.8 |
| CP23 | river_mouth | Schelde mouth | primary | 4.3083 | 51.2686 | 1127.3, 341.4 | 2254.6, 682.8 |
| CP24 | headland | Brean Down | primary | -3.029 | 51.3256 | 805.1, 338.0 | 1610.2, 676.0 |
| CP25 | river_mouth | Seine mouth | primary | 0.4932 | 49.4936 | 959.7, 470.2 | 1919.4, 940.4 |
| CP26 | headland | Mizen Head | primary | -9.81944 | 51.45028 | 509.9, 302.0 | 1019.8, 604.0 |
| CP27 | headland | Cabo Ortegal | primary | -7.8798 | 43.762 | 535.6, 849.8 | 1071.2, 1699.6 |
| CP28 | river_mouth | Loire mouth | primary | -1.7345 | 47.2108 | 853.4, 629.0 | 1706.8, 1258.0 |
| CP29 | settlement | Chepstow | secondary | -2.6757 | 51.6439 | 821.6, 316.3 | 1643.2, 632.6 |
| CP30 | settlement | Kenilworth | secondary | -1.59111 | 52.347 | 870.3, 268.6 | 1740.6, 537.2 |
| CP31 | settlement | Berkeley | secondary | -2.4569444444444444 | 51.68861111111111 | 831.3, 313.6 | 1662.6, 627.2 |
| CP32 | settlement | Gloucester | secondary | -2.24654 | 51.8673 | 840.9, 301.4 | 1681.8, 602.8 |
| CP33 | settlement | Bristol | secondary | -2.5975 | 51.45361111111111 | 824.4, 329.8 | 1648.8, 659.6 |
| CP34 | settlement | Lincoln | secondary | -0.55 | 53.25 | 915.8, 206.2 | 1831.6, 412.4 |
| CP35 | settlement | Corfe | secondary | -2.0589 | 50.6399 | 846.0, 387.8 | 1692.0, 775.6 |
| CP36 | settlement | Winchester | secondary | -1.3086111111111 | 51.063333333333 | 880.2, 359.0 | 1760.4, 718.0 |
| CP37 | settlement | Westminster | secondary | -0.12416666666667 | 51.499444444444 | 932.7, 329.3 | 1865.4, 658.6 |
| CP38 | settlement | Tyburn | secondary | -0.164 | 51.512861111111 | 931.0, 328.3 | 1862.0, 656.6 |
| CP39 | settlement | Nottingham | secondary | -1.1547222222222222 | 52.94916666666667 | 889.9, 226.8 | 1779.8, 453.6 |
| CP40 | settlement | Sandwich | secondary | 1.3388888888889 | 51.274722222222 | 996.9, 345.0 | 1993.8, 690.0 |
| CP41 | settlement | Sluis | secondary | 3.3883 | 51.3089 | 1086.8, 340.3 | 2173.6, 680.6 |
| CP42 | settlement | Avignon | secondary | 4.8083333333333 | 43.948611111111 | 1177.9, 853.5 | 2355.8, 1707.0 |
| CP43 | settlement | Paris | secondary | 2.352222222222222 | 48.85666666666667 | 1045.6, 513.9 | 2091.2, 1027.8 |
| CP44 | settlement | Cologne | secondary | 6.9577777777778 | 50.942222222222 | 1245.4, 356.3 | 2490.8, 712.6 |
| CP45 | settlement | Milan | secondary | 9.19 | 45.466944444444 | 1387.1, 729.0 | 2774.2, 1458.0 |

### britain_16x9

| id | type | name | role | lon | lat | px | plate px |
|---|---|---|---|---|---|---|---|
| CP01 | headland | Cap Gris-Nez | primary | 1.58361 | 50.87083 | 1749.5, 844.4 | 3499.0, 1688.8 |
| CP02 | headland | Portland Bill | primary | -2.45722 | 50.51444 | 977.9, 974.7 | 1955.8, 1949.4 |
| CP03 | headland | Great Orme | primary | -3.85556 | 53.33333 | 723.9, 119.0 | 1447.8, 238.0 |
| CP04 | headland | Hartland Point | primary | -4.52528 | 51.0219 | 583.8, 816.0 | 1167.6, 1632.0 |
| CP05 | headland | Selsey Bill | primary | -0.78799 | 50.7227 | 1297.8, 907.6 | 2595.6, 1815.2 |
| CP06 | headland | The Needles | primary | -1.58933 | 50.6627 | 1144.4, 928.6 | 2288.8, 1857.2 |
| CP07 | headland | Brean Down | primary | -3.029 | 51.3256 | 869.4, 728.8 | 1738.8, 1457.6 |
| CP08 | headland | St David's Head | primary | -5.3002 | 51.8883 | 446.1, 549.0 | 892.2, 1098.0 |
| CP09 | headland | Strumble Head | primary | -5.0695 | 52.0264 | 490.6, 508.7 | 981.2, 1017.4 |
| CP10 | headland | Braich y Pwll (Lleyn tip) | primary | -4.7616 | 52.7906 | 555.1, 279.3 | 1110.2, 558.6 |
| CP11 | headland | Holy Head (Anglesey) | primary | -4.6907 | 53.3114 | 572.7, 122.0 | 1145.4, 244.0 |
| CP12 | headland | Worms Head (Gower) | primary | -4.2974 | 51.5692 | 631.1, 651.4 | 1262.2, 1302.8 |
| CP13 | headland | North Foreland | primary | 1.4476 | 51.3807 | 1715.2, 691.7 | 3430.4, 1383.4 |
| CP14 | headland | South Foreland | primary | 1.3697 | 51.1405 | 1704.3, 765.1 | 3408.6, 1530.2 |
| CP15 | headland | Dungeness | primary | 0.9687 | 50.9153 | 1631.5, 837.1 | 3263.0, 1674.2 |
| CP16 | headland | Beachy Head | primary | 0.2399 | 50.7471 | 1494.5, 894.1 | 2989.0, 1788.2 |
| CP17 | headland | Orford Ness | primary | 1.5798 | 52.0808 | 1728.1, 478.6 | 3456.2, 957.2 |
| CP18 | headland | Lowestoft Ness | primary | 1.764 | 52.4746 | 1755.2, 357.5 | 3510.4, 715.0 |
| CP19 | headland | Carnsore Point | primary | -6.3672 | 52.1816 | 251.6, 451.3 | 503.2, 902.6 |
| CP20 | headland | Wicklow Head | primary | -5.9939 | 52.9584 | 332.0, 219.7 | 664.0, 439.4 |
| CP21 | headland | Howth Head | primary | -6.0575 | 53.3746 | 326.6, 93.3 | 653.2, 186.6 |
| CP22 | headland | Hook Head | primary | -6.9321 | 52.1247 | 145.8, 462.6 | 291.6, 925.2 |
| CP23 | headland | St Ann's Head | primary | -5.1698 | 51.6889 | 468.3, 610.2 | 936.6, 1220.4 |
| CP24 | river_mouth | Thames mouth | primary | 0.3845 | 51.4531 | 1513.6, 679.3 | 3027.2, 1358.6 |
| CP25 | river_mouth | Severn mouth | primary | -2.3914 | 51.7778 | 989.7, 592.1 | 1979.4, 1184.2 |
| CP26 | settlement | Chepstow | secondary | -2.6757 | 51.6439 | 936.4, 632.7 | 1872.8, 1265.4 |
| CP27 | settlement | Kenilworth | secondary | -1.59111 | 52.347 | 1137.4, 418.6 | 2274.8, 837.2 |
| CP28 | settlement | Berkeley | secondary | -2.4569444444444444 | 51.68861111111111 | 977.5, 619.1 | 1955.0, 1238.2 |
| CP29 | settlement | Gloucester | secondary | -2.24654 | 51.8673 | 1016.7, 564.9 | 2033.4, 1129.8 |
| CP30 | settlement | Bristol | secondary | -2.5975 | 51.45361111111111 | 951.0, 690.3 | 1902.0, 1380.6 |
| CP31 | settlement | Lincoln | secondary | -0.55 | 53.25 | 1322.3, 141.3 | 2644.6, 282.6 |
| CP32 | settlement | Corfe | secondary | -2.0589 | 50.6399 | 1054.3, 936.4 | 2108.6, 1872.8 |
| CP33 | settlement | Winchester | secondary | -1.3086111111111 | 51.063333333333 | 1196.3, 806.5 | 2392.6, 1613.0 |
| CP34 | settlement | Westminster | secondary | -0.12416666666667 | 51.499444444444 | 1417.2, 668.8 | 2834.4, 1337.6 |
| CP35 | settlement | Tyburn | secondary | -0.164 | 51.512861111111 | 1409.6, 665.0 | 2819.2, 1330.0 |
| CP36 | settlement | Nottingham | secondary | -1.1547222222222222 | 52.94916666666667 | 1214.6, 235.0 | 2429.2, 470.0 |
| CP37 | settlement | Sandwich | secondary | 1.3388888888889 | 51.274722222222 | 1696.3, 724.9 | 3392.6, 1449.8 |

### euro_9x16

| id | type | name | role | lon | lat | px | plate px |
|---|---|---|---|---|---|---|---|
| CP01 | headland | Land's End | primary | -5.71522 | 50.0677 | 181.8, 782.9 | 363.6, 1565.8 |
| CP02 | headland | Cap Corse | primary | 9.41666 | 42.83398 | 989.3, 1337.5 | 1978.6, 2675.0 |
| CP03 | headland | Grenen | primary | 10.6469 | 57.7456 | 918.4, 182.5 | 1836.8, 365.0 |
| CP04 | confluence | Rhine-Mosel (Koblenz) | primary | 7.6057 | 50.364 | 841.4, 764.8 | 1682.8, 1529.6 |
| CP05 | headland | Dunnet Head | primary | -3.37565 | 58.64475 | 342.8, 130.0 | 685.6, 260.0 |
| CP06 | river_mouth | Ebro mouth | primary | 0.8972 | 40.7252 | 504.5, 1523.1 | 1009.0, 3046.2 |
| CP07 | headland | Cabo de Penas | primary | -5.8499 | 43.6628 | 128.5, 1276.6 | 257.0, 2553.2 |
| CP08 | headland | Spurn | primary | 0.13981 | 53.59383 | 477.4, 526.2 | 954.8, 1052.4 |
| CP09 | confluence | Loire-Vienne (Candes) | primary | 0.0754 | 47.2182 | 465.0, 1019.9 | 930.0, 2039.8 |
| CP10 | river_mouth | Rhône mouth | primary | 4.6946 | 43.5791 | 719.4, 1298.8 | 1438.8, 2597.6 |
| CP11 | river_mouth | Elbe mouth | primary | 9.819 | 53.5404 | 922.5, 509.8 | 1845.0, 1019.6 |
| CP12 | river_mouth | Shannon mouth | primary | -8.7385 | 52.6728 | 60.4, 565.5 | 120.8, 1131.0 |
| CP13 | headland | Mull of Galloway | primary | -4.8629 | 54.6377 | 254.6, 433.9 | 509.2, 867.8 |
| CP14 | headland | Selsey Bill | primary | -0.78799 | 50.7227 | 427.8, 747.4 | 855.6, 1494.8 |
| CP15 | headland | Den Helder | primary | 4.75889 | 52.95833 | 692.2, 572.7 | 1384.4, 1145.4 |
| CP16 | river_mouth | Garonne mouth | primary | -0.5417 | 44.898 | 427.9, 1198.8 | 855.8, 2397.6 |
| CP17 | confluence | Po-Ticino (Pavia) | primary | 9.2241 | 45.1405 | 961.4, 1160.6 | 1922.8, 2321.2 |
| CP18 | confluence | Seine-Marne (Charenton) | primary | 2.4069 | 48.8143 | 586.3, 896.6 | 1172.6, 1793.2 |
| CP19 | headland | Cap Frehel | primary | -2.3265 | 48.685 | 344.4, 902.1 | 688.8, 1804.2 |
| CP20 | headland | Braich y Pwll (Lleyn tip) | primary | -4.7616 | 52.7906 | 246.8, 576.8 | 493.6, 1153.6 |
| CP21 | headland | Orford Ness | primary | 1.5798 | 52.0808 | 543.8, 643.9 | 1087.6, 1287.8 |
| CP22 | headland | Pointe du Raz | primary | -4.74111 | 48.04028 | 217.1, 943.8 | 434.2, 1887.6 |
| CP23 | river_mouth | Schelde mouth | primary | 4.3083 | 51.2686 | 676.2, 704.3 | 1352.4, 1408.6 |
| CP24 | headland | Cap de Creus | primary | 3.3171 | 42.322 | 644.2, 1398.5 | 1288.4, 2797.0 |
| CP25 | headland | Brean Down | primary | -3.029 | 51.3256 | 320.8, 695.9 | 641.6, 1391.8 |
| CP26 | headland | Ile de Re west tip | primary | -1.5558 | 46.2456 | 376.3, 1092.7 | 752.6, 2185.4 |
| CP27 | river_mouth | Seine mouth | primary | 0.4932 | 49.4936 | 489.3, 843.9 | 978.6, 1687.8 |
| CP28 | headland | Cap Gris-Nez | primary | 1.58361 | 50.87083 | 544.1, 737.6 | 1088.2, 1475.2 |
| CP29 | settlement | Chepstow | secondary | -2.6757 | 51.6439 | 339.3, 672.2 | 678.6, 1344.4 |
| CP30 | settlement | Kenilworth | secondary | -1.59111 | 52.347 | 393.6, 620.3 | 787.2, 1240.6 |
| CP31 | settlement | Berkeley | secondary | -2.4569444444444444 | 51.68861111111111 | 349.9, 669.3 | 699.8, 1338.6 |
| CP32 | settlement | Gloucester | secondary | -2.24654 | 51.8673 | 360.7, 656.0 | 721.4, 1312.0 |
| CP33 | settlement | Bristol | secondary | -2.5975 | 51.45361111111111 | 342.2, 687.1 | 684.4, 1374.2 |
| CP34 | settlement | Lincoln | secondary | -0.55 | 53.25 | 444.9, 552.1 | 889.8, 1104.2 |
| CP35 | settlement | Corfe | secondary | -2.0589 | 50.6399 | 365.2, 751.4 | 730.4, 1502.8 |
| CP36 | settlement | Winchester | secondary | -1.3086111111111 | 51.063333333333 | 403.2, 720.2 | 806.4, 1440.4 |
| CP37 | settlement | Westminster | secondary | -0.12416666666667 | 51.499444444444 | 461.6, 688.1 | 923.2, 1376.2 |
| CP38 | settlement | Tyburn | secondary | -0.164 | 51.512861111111 | 459.7, 687.0 | 919.4, 1374.0 |
| CP39 | settlement | Nottingham | secondary | -1.1547222222222222 | 52.94916666666667 | 416.0, 574.5 | 832.0, 1149.0 |
| CP40 | settlement | Sandwich | secondary | 1.3388888888889 | 51.274722222222 | 532.2, 706.3 | 1064.4, 1412.6 |
| CP41 | settlement | Sluis | secondary | 3.3883 | 51.3089 | 631.5, 702.5 | 1263.0, 1405.0 |
| CP42 | settlement | Avignon | secondary | 4.8083333333333 | 43.948611111111 | 724.6, 1269.9 | 1449.2, 2539.8 |
| CP43 | settlement | Paris | secondary | 2.352222222222222 | 48.85666666666667 | 583.4, 893.4 | 1166.8, 1786.8 |
| CP44 | settlement | Cologne | secondary | 6.9577777777778 | 50.942222222222 | 806.3, 722.5 | 1612.6, 1445.0 |
| CP45 | settlement | Milan | secondary | 9.19 | 45.466944444444 | 957.1, 1135.6 | 1914.2, 2271.2 |

### britain_9x16

| id | type | name | role | lon | lat | px | plate px |
|---|---|---|---|---|---|---|---|
| CP01 | headland | Land's End | primary | -5.71522 | 50.0677 | 197.0, 1275.6 | 394.0, 2551.2 |
| CP02 | headland | Flamborough Head | primary | -0.0823 | 54.1158 | 793.2, 584.0 | 1586.4, 1168.0 |
| CP03 | confluence | Loire-Vienne (Candes) | primary | 0.0754 | 47.2182 | 851.9, 1765.9 | 1703.8, 3531.8 |
| CP04 | headland | Cap Gris-Nez | primary | 1.58361 | 50.87083 | 992.7, 1132.2 | 1985.4, 2264.4 |
| CP05 | headland | Howth Head | primary | -6.0575 | 53.3746 | 186.3, 707.2 | 372.6, 1414.4 |
| CP06 | river_mouth | Severn mouth | primary | -2.3914 | 51.7778 | 562.1, 989.5 | 1124.2, 1979.0 |
| CP07 | headland | Pointe de Penmarch | primary | -4.3698 | 47.8071 | 336.0, 1668.1 | 672.0, 3336.2 |
| CP08 | headland | Pointe de Barfleur | primary | -1.2706 | 49.6982 | 687.5, 1345.0 | 1375.0, 2690.0 |
| CP09 | headland | St Bees Head | primary | -3.6342 | 54.5129 | 437.0, 519.6 | 874.0, 1039.2 |
| CP10 | headland | Lowestoft Ness | primary | 1.764 | 52.4746 | 995.7, 856.3 | 1991.4, 1712.6 |
| CP11 | headland | St David's Head | primary | -5.3002 | 51.8883 | 254.2, 965.3 | 508.4, 1930.6 |
| CP12 | headland | Start Point | primary | -3.6456 | 50.226 | 425.2, 1254.9 | 850.4, 2509.8 |
| CP13 | river_mouth | Loire mouth | primary | -1.7345 | 47.2108 | 640.9, 1772.2 | 1281.8, 3544.4 |
| CP14 | headland | Cap Frehel | primary | -2.3265 | 48.685 | 571.0, 1520.0 | 1142.0, 3040.0 |
| CP15 | headland | Great Orme | primary | -3.85556 | 53.33333 | 411.4, 721.6 | 822.8, 1443.2 |
| CP16 | river_mouth | Seine mouth | primary | 0.4932 | 49.4936 | 884.6, 1374.1 | 1769.2, 2748.2 |
| CP17 | headland | Selsey Bill | primary | -0.78799 | 50.7227 | 736.8, 1168.1 | 1473.6, 2336.2 |
| CP18 | headland | Hook Head | primary | -6.9321 | 52.1247 | 84.0, 916.4 | 168.0, 1832.8 |
| CP19 | headland | Hartland Point | primary | -4.52528 | 51.0219 | 332.3, 1116.5 | 664.6, 2233.0 |
| CP20 | river_mouth | Thames mouth | primary | 0.3845 | 51.4531 | 859.0, 1038.7 | 1718.0, 2077.4 |
| CP21 | headland | Portland Bill | primary | -2.45722 | 50.51444 | 555.6, 1206.3 | 1111.2, 2412.6 |
| CP22 | headland | Braich y Pwll (Lleyn tip) | primary | -4.7616 | 52.7906 | 315.8, 812.4 | 631.6, 1624.8 |
| CP23 | headland | Mull of Galloway | primary | -4.8629 | 54.6377 | 315.3, 495.4 | 630.6, 990.8 |
| CP24 | headland | Beachy Head | primary | 0.2399 | 50.7471 | 848.2, 1160.4 | 1696.4, 2320.8 |
| CP25 | headland | Brean Down | primary | -3.029 | 51.3256 | 494.0, 1067.0 | 988.0, 2134.0 |
| CP26 | headland | Worms Head (Gower) | primary | -4.2974 | 51.5692 | 359.0, 1023.2 | 718.0, 2046.4 |
| CP27 | headland | Spurn | primary | 0.13981 | 53.59383 | 818.9, 672.7 | 1637.8, 1345.4 |
| CP28 | headland | North Foreland | primary | 1.4476 | 51.3807 | 973.2, 1045.6 | 1946.4, 2091.2 |
| CP29 | settlement | Chepstow | secondary | -2.6757 | 51.6439 | 531.9, 1012.5 | 1063.8, 2025.0 |
| CP30 | settlement | Kenilworth | secondary | -1.59111 | 52.347 | 645.7, 891.2 | 1291.4, 1782.4 |
| CP31 | settlement | Berkeley | secondary | -2.4569444444444444 | 51.68861111111111 | 555.2, 1004.8 | 1110.4, 2009.6 |
| CP32 | settlement | Gloucester | secondary | -2.24654 | 51.8673 | 577.4, 974.1 | 1154.8, 1948.2 |
| CP33 | settlement | Bristol | secondary | -2.5975 | 51.45361111111111 | 540.3, 1045.2 | 1080.6, 2090.4 |
| CP34 | settlement | Lincoln | secondary | -0.55 | 53.25 | 750.4, 734.0 | 1500.8, 1468.0 |
| CP35 | settlement | Corfe | secondary | -2.0589 | 50.6399 | 598.9, 1184.5 | 1197.8, 2369.0 |
| CP36 | settlement | Winchester | secondary | -1.3086111111111 | 51.063333333333 | 679.2, 1110.9 | 1358.4, 2221.8 |
| CP37 | settlement | Westminster | secondary | -0.12416666666667 | 51.499444444444 | 804.4, 1032.8 | 1608.8, 2065.6 |
| CP38 | settlement | Tyburn | secondary | -0.164 | 51.512861111111 | 800.0, 1030.6 | 1600.0, 2061.2 |
| CP39 | settlement | Nottingham | secondary | -1.1547222222222222 | 52.94916666666667 | 689.4, 787.1 | 1378.8, 1574.2 |
| CP40 | settlement | Sandwich | secondary | 1.3388888888889 | 51.274722222222 | 962.5, 1064.4 | 1925.0, 2128.8 |
