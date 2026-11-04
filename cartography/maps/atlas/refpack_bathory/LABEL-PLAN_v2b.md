# Báthory B03: label plan v2b (engine overlays only)

Supersedes `LABEL-PLAN_v2.md` for the label text and layout; v2 and `label_plan_v2/` are kept unchanged. B03 itself stays on **HOLD** until Archivist verifies the geodata. No label or text is baked into the plate.

## 1. Ruling
**Archivist's final label ruling via `MAP-PLACES-bathory-v1.md`, approved by Vellum, 12:27 pm Toronto time, 2026-10-31.** This replaces the v2 two-line ruling. Labels, all engine overlays, nothing else:
- **"Csejte, today Čachtice, Slovakia"**: one label unit in one uniform style. There is no separate, smaller modern-name line.
- **"Bytča"**: plain, with no Slovakia line.
- **"Váh"**: faint river label.

Still applies: no Bratislava or Pozsony (Pozsony is off-frame at x ≈ −488); the Moravia wedge is quiet ground; the manor stays unlabelled; the "© OpenStreetMap contributors" credit applies if OSM river linework ships.

## 2. Style
- **Csejte and Bytča:** IM Fell English SC, **51 px** at 1080x1920, LABEL_INK [52,30,20]. Csejte is a single line.
- **Váh:** IM Fell French Canon Italic, 38 px, alpha 0.60, rotated 7.0° along the river.
- **Halo:** house parchment [238,226,194] on all labels (dilate ≈5 px, blur 2.0, ×1.4, opacity 0.80).
- **At 360x640:** cap height 11.7 px and small-cap x-height 7.7 px for the names; Váh x-height 6.0 px.

## 3. Boxes (frame px, [x0,y0,x1,y1]; zone = box +10 px)
| Label | 1080x1920 box | Zone | 360x640 box | Placement |
|---|---|---|---|---|
| Csejte, today Čachtice, Slovakia | [115,1086,832,1153] | [105,1076,842,1163] | [38,362,277,384] | one line, S of the pin (130.7,1065.2), left-aligned, 21 px below the pin centre |
| Bytča | [717,303,851,345] | [707,293,861,355] | [239,101,284,115] | **NW of the pin (871.4,365.8): fits again** |
| Váh | [506,709,575,749], 7.0° | [496,699,585,759] | [169,236,192,250] | beside the river at (536,694) |

**Checks:**
- Every label is inside title_safe [54,96,1026,1824] and above y 1280 (the caption third).
- Every label is clear of its pin, the other pin, the compass [54,384,248,578] (Csejte ≈605 px away) and the Moravia wedge.
- Bytča NW clears the medallion [789,54,1026,291] by 2 px beyond the 10 px pad (12 px raw). That passes, but it's tight.
- The Váh label is clear of both place labels.

**Not possible: Csejte clear of the Váh.** The castle pin sits just west of the river, and there's no room to its west before the frame edge. Every Csejte placement and wrap crosses the river:
- one line: S 491 river px, E 525, N 563
- two-line wrap: about 950–1200
- at 46 or 42 px it is still 419–456 px

I chose the one-line 51 px label south of the pin, which has the least crossing at full size; the halo masks the river under the text. Atelier could also thin the river under the halo.

## 4. Conflicts (carried over from v2, updated)
1. MAP-PLACES' 1610-only naming is now amended by Archivist's own ruling, so the modern name has a source.
2. `framing_refpack_bathory_v2.json` label_text_rule, `README_v2.md` ("Csejte and Bytča only") and the label zones in `PLATE-PROMPT_v2.md` are out of date. Atelier needs to update them to the zones above. They weren't edited here.
3. The Csejte label crosses the Váh, as explained in §3.
4. The proof is over the no-text guide, not a painted plate, so contrast must be re-checked on the real plate.

## 5. Files (`label_plan_v2b/`)
- `layout_labels_v2b.py` is the layout script.
- `label_layout_v2b.json` holds the boxes and metrics.
- **Proof:** `b03v2_labels_v2b_proof_1080x1920.png`.
- Supporting images:
  - `b03v2_labels_v2b_zones_1080x1920.png`
  - `b03v2_labels_v2b_phone_360x640.png`
  - `b03v2b_phone_crop_csejte_x3.png`
  - `b03v2b_phone_crop_bytca_x4.png`
