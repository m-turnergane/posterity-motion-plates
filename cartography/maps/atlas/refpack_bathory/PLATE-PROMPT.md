# PLATE PROMPT v1 - Báthory B03 map beat (Upper Hungary, Váh valley), one clean plate

Written 2026-10-31 12:05 ET. Style: Explorer's Chart (owner brief, Roanoke reference). Mood: winter, restrained historical gothic. Same format as `atlas/refpack/PLATE-PROMPTS-v2.md`.
Rules: generate at 2x (plate px = 2 x out px in `control_points_refpack_bathory_v1.json`). Attach `img_v1/bathory_b03_9x16_ref_notext.png` as the layout guide; it has no text, borders or dots. The engine adds every name, pin, marker, medallion and any realm tint, using the coarse OHM masks in `img_v1/..._realm_ids.png`. So the plate carries **no realm colours or border lines**: the 1610 borders here are coarse, and modern borders are forbidden (MAP-PLACES). A compass rose may go only inside `zones.ornament_reserved`. The `zones.medallion` box and every `label_zones` box (+10 px) must stay quiet.

## bathory_b03_9x16  (1080x1920 out, plate 2160x3840) - 118 words

Attach: `img_v1/bathory_b03_9x16_ref_notext.png`  
Ornament zone (out px): [832, 384, 1026, 578] (upper-right, below the medallion)  
Medallion zone (out px): [789, 54, 1026, 291] (upper-right corner)  
Label zones (out px, keep calm): Csejte [515,1405,614,1446] · Bytča [834,1085,925,1116] · Pozsony [374,1729,497,1759] · Vienna [92,1676,198,1708]

```
Vertical 9:16 antique chart of the Váh valley and the western Carpathians, exactly 2160x3840. Attached reference = layout guide; match its rivers, mountain ridges and lakes exactly. Explorer's-chart engraving: inked waterways, the Danube and Váh drawn strongest, fine engraved hill hachures, sparse forest stipple, tiny unlabeled settlement vignettes. Winter mood, restrained historical gothic: frost-pale parchment, cold grey-blue rivers, snow-dusted ridges, umber-black ink, aged by texture, not fading. No realm colours, no border lines. Calm margins. One small compass rose only upper-right, below the corner; upper-right corner empty. Calm ground around Csejte, Bytča, Pozsony, Vienna. Clean plate: no text, labels, routes, dotted lines, icons, banners, title, cartouche, frame border, vignette or watermark; the engine adds place names.
```
