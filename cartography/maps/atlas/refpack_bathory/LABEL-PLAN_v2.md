# Báthory B03: label plan v2 (engine overlays only)

Status: written 2026-10-31 (Toronto time) after the owner countersign. **B03 itself is on HOLD: no plate is generated until Archivist verifies the geodata.** This plan covers only the editorial overlay labels the engine draws on top of the plate. No label or text is ever baked into the plate.

## 1. Ruling (Vellum, FINAL; it replaces the earlier parenthetical version)
Exactly these labels and nothing else, all engine overlays:

| Label | Line 1 | Line 2 (smaller) |
|---|---|---|
| Csejte | **Csejte** | *today Čachtice, Slovakia* |
| Bytča | **Bytča** | *Slovakia* |
| River | *Váh* (faint) | — |

- **Override recorded:** the second lines override MAP-PLACES' 1610-only naming, at the owner's request (via Vellum). Line 1 still uses the 1610 names.
- No Bratislava and no Pozsony (Pozsony sits at x ≈ −488, outside the frame anyway).
- No other place, region, realm, range, date or status text. The manor stays an unlabelled point.
- The **Moravia wedge** (lower right, top y 770, left x 899, ≈20% of the frame) is approved as quiet ground: no label, no ornament.

## 2. Style (house map style, as in `map_route_v1.py` / `map_route_v2_r2.py`)
- **Line 1 (places):** IM Fell English SC (`IMFellEnglishSC-Regular.ttf`), **51 px** at 1080x1920.
- **Line 2 and Váh:** IM Fell French Canon Italic, **38 px**, leading 4 px under line 1. Line 2 is left-aligned with line 1.
- **Ink:** LABEL_INK [52,30,20]. Line 2 at the same ink (smaller and italic does the hierarchy). **Váh at alpha 0.60**, rotated **6.9°** to follow the river.
- **Halo:** the house parchment halo LABEL_HALO_COL [238,226,194]: dilate about 5 px, blur 2.0, ×1.4, opacity 0.80, on all three labels.
- Glyphs Č, č and á are present in both fonts (checked).
- Sizes are larger than v1's 30 px (Edward r2 used 45; refpack v2 used 40) so line 2 holds a 6 px x-height on a 360x640 phone.

## 3. Boxes (frame px; origin top-left)
Pins from `framing_refpack_bathory_v2.json`: Csejte (130.7, 1065.2), Bytča (871.4, 365.8), manor COARSE (155.2, 1083.0, not drawn). Reserved: compass/ornament [54,384,248,578]; medallion [789,54,1026,291]; title_safe [54,96,1026,1824]; pin_safe [64,96,1015,1824].

| Label | Ink bbox 1080x1920 [x0,y0,x1,y1] | Zone (+10 pad) | 360x640 bbox | Placement |
|---|---|---|---|---|
| Csejte (2 lines) | [114,1086,493,1197] | [104,1076,503,1207] | [38,362,164,399] | **S of the pin**, left-aligned, top 21 px below the pin centre |
| Bytča (2 lines) | [854,381,996,465] | [844,371,1006,475] | [285,127,332,155] | **S of the pin**, left-aligned, top 15 px below the pin centre |
| Váh | [505,709,574,749], 6.9° | [495,699,584,759] | [168,236,191,250] | beside the river at (535,694), alpha 0.60 |

**Checks (all pass):** every box is inside title_safe, above y 1280 (clear of the caption third), clear of the compass (Csejte ≈605 px from its centre), clear of the medallion (Bytča top 381 vs medallion bottom 291), clear of the other pin, and outside the Moravia wedge. At 360x640, line 1 is an 11.7 px cap height and line 2 / Váh a 6.0 px x-height (9.0 px cap); both two-line labels read clearly in the phone crops.

**Zones moved:** the old zones in `framing_refpack_bathory_v2.json` (Csejte [73,1000,188,1049] N; Bytča [753,320,861,356] NW) are too small for two lines. Bytča NW would hit the medallion, and Csejte N is crowded by the castle hill. Both move **south of their pins** to the boxes above.

## 4. Credit
If OSM river linework ships in the plate or overlay (the Váh spine here is OSM relation 3509398), the edit must carry **"© OpenStreetMap contributors"** (ODbL) in the description/credits, plus a small on-screen credit if the house map style uses one.

## 5. Conflicts found (for the owner, Archivist and Atelier)
1. `MAP-PLACES-bathory-v1.md` says 1610 names only and "No modern borders or names (Slovakia, Bratislava)". The second lines ("today Čachtice, Slovakia"; "Slovakia") break this **by owner override via Vellum** (recorded in §1). MAP-PLACES itself is not edited.
2. House rule "place names only" vs the **Váh** river label: also covered by the ruling.
3. `framing_refpack_bathory_v2.json` label_text_rule ("1610 names only. No river, range, realm, date or status text.") and `README_v2.md` ("On-screen labels: Csejte and Bytča only") are now out of date. **Atelier must update** them and the label-zone reservations in `PLATE-PROMPT_v2.md` to the §3 zones (not edited here).
4. **The Csejte label crosses the Váh** (≈833 river px under the block). The river runs just east of the castle, so every Csejte placement crosses it; the halo masks it. Accept, or Atelier thins the river under the halo.
5. Pozsony is at x ≈ −488 (off frame): the "no Pozsony" ruling needs no layout change.
6. The proof is laid over the no-text reference guide, not a painted plate. Re-check contrast on the real plate after Archivist clears the geodata.

## 6. Files (`label_plan_v2/`)
- `layout_labels_v2.py`: layout script (spherical LAEA +lat_0=48.8 +lon_0=18.2, 78.704 m/px; checked against the Csejte pin).
- `label_layout_v2.json`: boxes and metrics.
- `b03v2_labels_v2_proof_1080x1920.png`, `b03v2_labels_v2_zones_1080x1920.png`, `b03v2_labels_v2_phone_360x640.png`, `b03v2_phone_crop_csejte_x3.png`, `b03v2_phone_crop_bytca_x4.png`: the proofs.
