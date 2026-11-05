# PLATE PROMPTS v2 - Edward II atlas plates (clean, engine-registered)

Written 2026-10-31 11:31 ET. Style: EXPLORER'S CHART ref (Roanoke) for engraving/stipple/coast detail + Imperial Atlas realm fill and inked borders for political clarity (owner brief: strong pigments, ~75% political / 25% terrain, age by texture not desaturation).
Rules for every plate: generate at 2x frame size (the plate px = 2 x out px in `control_points_refpack_v2.json`), attach `img_v2/<frame>_ref_tinted_notext.png` as the layout guide (no text on it). If the generator drifts on shape, also attach `<frame>_ref_bare.png`. The engine adds every name, route, marker and medallion; the plate must be CLEAN. The compass rose is allowed only inside the frame's `zones.ornament` box; the `zones.medallion` box and every `label_zones` box must stay quiet.
Reference colours are a layout code only; the prompt pigments below are the art direction (England/Gascony crimson, France royal blue, Empire antique gold, Brittany+Burgundy slate blue, Scotland heather violet, Castile terracotta, Aragon saffron, Portugal sage, Flanders grey-teal; Gaelic Ireland and Italy unpainted parchment).

## euro_16x9  (1920x1080 out, plate 3840x2160) - 127 words

Attach: `img_v2/euro_16x9_ref_tinted_notext.png`  
Ornament zone (out px): [54, 443, 248, 637] (middle-left)  
Medallion zone (out px): [54, 54, 291, 291] (upper-left)

```
Horizontal 16:9 antique chart of western Europe, exactly 3840x2160. Attached reference = layout guide; match its coasts, rivers, Alps, Pyrenees and realm shapes. Explorer's-chart engraving: inked waterways, forest stipple, coastal detail, painted relief, tiny settlement vignettes, parchment aged by texture, not fading; blue-green sea. Strong realm pigments, decisive inked borders: England and Gascony crimson, France royal blue, Brittany and Burgundy slate blue, Flanders grey-teal, Empire antique gold, Scotland heather violet, Castile terracotta, Aragon saffron, Portugal sage; Italy, Gaelic Ireland bare parchment. Calm margins. One small compass rose only middle-left, open Atlantic west of Brittany; upper-left corner empty. Calm ground around Paris, Avignon, Cologne, Milan, Sluis. Clean plate: no text, labels, routes, dotted lines, icons, banners, title, cartouche, frame border, vignette or watermark; the engine adds place names.
```

## britain_16x9  (1920x1080 out, plate 3840x2160) - 122 words

Attach: `img_v2/britain_16x9_ref_tinted_notext.png`  
Ornament zone (out px): [383, 54, 577, 248] (upper-left)  
Medallion zone (out px): [54, 789, 291, 1026] (lower-left)

```
Horizontal 16:9 antique chart of southern Britain and the Irish Sea, exactly 3840x2160. Attached reference = layout guide; match its coasts, rivers and realm shapes. Explorer's-chart engraving: inked waterways, forest stipple, coastal detail, painted relief, tiny settlement vignettes, parchment aged by texture, not fading; blue-green sea. Strong realm pigments, decisive inked borders: England and Wales crimson, English Ireland pale crimson, Gaelic Ireland bare parchment, France royal blue, Flanders grey-teal. Calm margins. One small compass rose only at the top edge, in the Irish Sea west of Anglesey; lower-left Celtic Sea empty. Calm ground around Berkeley, Gloucester, Corfe, Kenilworth, London, Sandwich. Clean plate: no text, labels, routes, dotted lines, icons, banners, title, cartouche, frame border, vignette or watermark; the engine adds place names.
```

## euro_9x16  (1080x1920 out, plate 2160x3840) - 127 words

Attach: `img_v2/euro_9x16_ref_tinted_notext.png`  
Ornament zone (out px): [54, 863, 248, 1057] (middle-left)  
Medallion zone (out px): [421, 54, 658, 291] (upper-centre)

```
Vertical 9:16 antique chart of western Europe, exactly 2160x3840. Attached reference = layout guide; match its coasts, rivers, Alps, Pyrenees and realm shapes. Explorer's-chart engraving: inked waterways, forest stipple, coastal detail, painted relief, tiny settlement vignettes, parchment aged by texture, not fading; blue-green sea. Strong realm pigments, decisive inked borders: England and Gascony crimson, Scotland heather violet, France royal blue, Brittany and Burgundy slate blue, Empire antique gold, Flanders grey-teal, Castile terracotta, Aragon saffron, Portugal sage; Italy, Gaelic Ireland bare parchment. Calm margins. One small compass rose only middle-left, Atlantic west of Brittany; upper-centre North Sea empty. Calm ground around Paris, Avignon, Cologne, Milan, Sluis. Clean plate: no text, labels, routes, dotted lines, icons, banners, title, cartouche, frame border, vignette or watermark; the engine adds place names.
```

## britain_9x16  (1080x1920 out, plate 2160x3840) - 116 words

Attach: `img_v2/britain_9x16_ref_tinted_notext.png`  
Ornament zone (out px): [54, 1305, 248, 1499] (lower-left)  
Medallion zone (out px): [54, 1629, 291, 1866] (lower-left)

```
Vertical 9:16 antique chart of Britain, Ireland and northern France, exactly 2160x3840. Attached reference = layout guide; match its coasts, rivers and realm shapes. Explorer's-chart engraving: inked waterways, forest stipple, coastal detail, painted relief, tiny settlement vignettes, parchment aged by texture, not fading; blue-green sea. Strong realm pigments, decisive inked borders: England and Wales crimson, English Ireland pale crimson, Gaelic Ireland bare parchment, Scotland heather violet, France royal blue, Brittany slate blue. Calm margins. One small compass rose only lower-left, Western Approaches; bottom-left Biscay corner empty. Calm ground around Berkeley, Corfe, Kenilworth, London, Sandwich. Clean plate: no text, labels, routes, dotted lines, icons, banners, title, cartouche, frame border, vignette or watermark; the engine adds place names.
```
