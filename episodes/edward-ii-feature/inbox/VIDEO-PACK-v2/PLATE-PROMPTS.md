# PLATE PROMPTS v2 — Edward II / Edmund, Earl of Kent (long-form, 16:9)

Status: DRAFT for Atelier Jr. v2.1: repinned to script v3.2 LOCKED (sources/raw/script-vo-v3.2-LOCKED.txt md5 11f4e6f9ac7d640d006dac33533472f6; owner-approved 12:50pm ET 2026-11-04; Archivist countersign ARCHIVIST-SCRIPT-v3.2-CHECK.md) and CLAIM-LEDGER-v3.2 (md 8e824c980c2f2d3c289a20ae5447e7a9). Script v2 and v3 are SUPERSEDED. Shot, line and VO fields regenerated from SHOT-LIST v2.1; image prompts unchanged except the new plates N21, N22 (optional), N23 (optional). No plate here has been generated. Format: PLATE-PROMPT-TEMPLATE-v2 (sources/PLATE-PROMPT-TEMPLATE-v2.md, B09 example).

How to use: paste ONLY the IMAGE GENERATION block into the image model, with the listed reference image(s) attached. Each plate has a ready-to-paste Nano Banana Pro IMAGE GENERATION block. The SHOT INTENT block (v2) governs motion; Atelier Jr writes the Higgsfield I2V prompt from it. The MOTION HANDOFF block is a v1 suggestion for the engine / Atelier Jr. Sourcing per shot (engine preset on a plate, existing Short plate, or Higgsfield) is Atelier Jr's call (sample phase has no budget constraint; see PILOT-OVERRIDE-v1 §4); these prompts work for any route. Hero plates (H01–H06) may be outpainted from the Short 9:16 plate (to 2976x1674) or regenerated native 16:9 (>=2560x1440); the route is not prescribed. Generate other plates native 16:9 at >=2560x1440 (atlas plates exactly 3840x2160). Crop rule: a crop window must be >=0.53 of plate width and never upscale more than 1.5 output px per plate px (law §6).

VO quoted below is verbatim script v3.2; any edit voids the countersign. L65 is a translation and is never shown in quotes on screen. No prompt asks the image model for on-screen text, status labels or chapter cards. The title card and the act cards (owner note 11:49am ET 2026-11-04) are engine-typed on the CB1 base; their words are OWNER SIGN-OFF (00-README.md).

## 1. Character anchors (paste verbatim where a prompt names the figure)

### KENT
Edmund, Earl of Kent — verbatim from standalones/edward-ii/plate-prompts-v3b.md §3 (KENT CHARACTER BLOCK). Short refs: b20, b04, b07, b09, b10.

```
Edmund, Earl of Kent, the same man in every image: an English royal nobleman in his late twenties, lean and upright, medium height, pale skin, short dark auburn hair cut level just below the ears with a soft centre parting, a short neatly trimmed dark auburn beard and moustache, a straight narrow nose, steady grey-blue eyes under straight dark brows. Early fourteenth-century English noble dress: a knee-length oxblood-red wool cote with a round neck and close-fitting sleeves buttoned from elbow to wrist with small gilt buttons, a narrow dark leather belt, dark hose, plain black leather shoes, and over it a long deep midnight-blue wool mantle lined with grey-and-white squirrel fur, fastened at the right shoulder by a round gold ring brooch; a heavy gold signet ring on the forefinger of his right hand. Bareheaded, no crown, no coronet, no armour. An original painted face, not a portrait of any real person or actor.
```

### EDW_ROYAL
Edward II as king — from the B04 prompt (v3b). Short ref: b04.

```
King Edward the Second: a tall, broad-shouldered man of about forty with fair hair to the jaw and a short fair beard, in a royal blue and gold robe and a simple gold crown, calm and regal.
```

### EDW_HIDDEN
Edward of Caernarfon in hiding (Fieschi claim scenes only: N18, N19, N20) — verbatim from v3b §3 / B18. Short refs: b18, p10. Each use is a claim attributed in narration, never shown as proof.

```
Edward of Caernarfon in hiding, a former king now living as a hidden man: a tall, broad-shouldered Englishman of about forty-five, worn and weathered, fair hair going grey and grown to the collar, a full untrimmed fair-grey beard, tired deep-set eyes; plain dark brown and charcoal wool clothes and a plain hooded wool cloak, no crown, no jewels, no royal insignia. An original painted face, not a portrait of any real person or actor.
```

### ISA
Queen Isabella — from the B05 prompt (v3b). Short ref: b05.

```
Queen Isabella: an elegant, composed woman of about thirty in a rich dark crimson gown and white veil with a slim gold circlet, a dark travelling cloak over it
```

### MORT
Roger Mortimer — from B05/B13/B14 (v3b). Short refs: b05, p07, b13.

```
Roger Mortimer: a hard-faced English baron around forty, dark-haired with a short dark beard and heavy brows, in a dark green surcoat over mail
```

### E3
Edward III — age set per plate: fourteen at the coronation (N04, NR-4), about eighteen in November 1330 (N16). Kept OUT of H03 (Nottingham).

```
the young king Edward the Third: a tall slender youth, beardless, fair-haired, crowned
```

### FIESCHI
Manuel Fieschi — from the B15 prompt (v3b), with the papal-court setting removed (C14b-b BLOCKED: no named city, palace or Avignon). Short ref: b15.

```
a middle-aged cleric, a notary of the pope, in a black clerical gown and close black cap
```

### BERK
Thomas, Lord Berkeley — an original painted characterization (no Short plate); fixed here for N17 and reuse.

```
Thomas, Lord Berkeley: an English baron in his thirties, broad and square-faced, clean-shaven with close-cropped brown hair, in a plain dark russet gown with a black belt and no armour, holding himself stiffly. An original painted face, not a portrait of any real person or actor.
```

Visual identity line (opens every IMAGE GENERATION block):

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language.
```

## 2. Location anchors

### Corfe Castle (Dorset)
Intact and royal (no ruin): tall square stone keep on a steep green hill in a gap between the Purbeck ridges, curtain walls stepping down, gatehouse below, one lit window high in the keep. Anchor: Short plate b03 (b03_corfe_moonlit_from_below_OWNER.png) -> N10; must match in H02, H04, N19 (interior), E01. C32 (Murimuth on Corfe) and C03 (Fieschi on Corfe) stay separate: the plate is a place, not evidence.

### Berkeley Castle (Gloucestershire)
Red-sandstone walls and keep at dusk, moat mist. Anchor: Short plate p04 (p04_berkeley_castle_dusk_OWNER.png) -> N05; N18 postern must match. Never show or narrate a method of death (C33).

### Gloucester (abbey church, now cathedral)
Romanesque nave, candlelit hearse, closed coffin under a wooden effigy ("probably" Edward per C04, attributed in VO). Anchor: Short plate b01 (b01_gloucester_funeral_wide_kent_OWNER.png) -> H01; N07 matches. Tomb photography for T01 = CC0 Poliphilo (rights-risks §1).

### Winchester
Grey castle wall, cold March morning, empty straw-strewn platform with Kent's mantle on the steps; nothing graphic. Anchor: Short plate b12 (b12_winchester_after_OWNER.png) -> N14. The parliament hall in N13 is "a great hall at Winchester" (exact building not asserted).

## 3. Plates (play order of first use)

### H06 — Kent seals letter

Class HERO · batch 3 · expected file `h06_kent_seals_letter_16x9_OWNER.png` · shots S001, S002, S052, S098b · lines L01, L02, L50, L97a · claims C09, C05c

VO (anchor shot S001, L01): "The king's own brother sealed a letter for a king that England had already buried."

VO on this plate, script v3.2 verbatim (every shot):
- S001 (L01): "The king's own brother sealed a letter for a king that England had already buried."
- S002 (L02): "The brother was Edmund, Earl of Kent. The buried king was his half-brother, Edward the Second."
- S052 (L50): "And it said Kent had been fooled about a man who had been dead for a long time."
- S098b (L97a (part, 11 of 40 words)): "Kent's letter was meant for a brother England had already buried."

Narrative purpose: Open the film on one private act: the king's brother sealing a letter by candlelight.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Candle gold, oxblood, midnight blue, wax red and old parchment against warm darkness.

Scene: England, 1330, a small private chamber at night. Edmund, Earl of Kent, the same man in every image: an English royal nobleman in his late twenties, lean and upright, medium height, pale skin, short dark auburn hair cut level just below the ears with a soft centre parting, a short neatly trimmed dark auburn beard and moustache, a straight narrow nose, steady grey-blue eyes under straight dark brows. Early fourteenth-century English noble dress: a knee-length oxblood-red wool cote with a round neck and close-fitting sleeves buttoned from elbow to wrist with small gilt buttons, a narrow dark leather belt, dark hose, plain black leather shoes, and over it a long deep midnight-blue wool mantle lined with grey-and-white squirrel fur, fastened at the right shoulder by a round gold ring brooch; a heavy gold signet ring on the forefinger of his right hand. Bareheaded, no crown, no coronet, no armour. An original painted face, not a portrait of any real person or actor. He sits at a heavy oak table and presses his signet ring into a pool of red wax on a folded parchment letter, his left hand flattening the fold. His face is intent and resolved, eyes on the seal. A single tall candle burns on the table; a stick of red wax, a small knife and a second folded sheet lie beside it. Behind him, plain plastered stone and a shuttered window.

Continuity: Attach the Short plate b20 (b20_kent_seals_letter_OWNER.png) as the hero reference: keep Kent's face, hair, cote, mantle, brooch and ring exactly, and the room's candle-gold light; recompose for a wide frame.

Composition: Medium-wide, eye level. Kent left of centre, face at about a third of frame height; the letter, seal and both hands clearly separated from the candle in the centre foreground so a close framing on the hands alone reads cleanly. Open dark wall to the right. Leave space at all edges for a slow push of about 106%.

Lighting and animation readiness: One candle is the only light, painted whole with a crisp bright core; its warm light falls on his face, hands and the wet wax. A thin thread of smoke rises from the wick. The image is one frozen instant.

Shot-specific constraints: The letter is folded and sealed; no writing shows.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5) · **I2V TEST CANDIDATE**

- Dramatic intent: Cold open: a brother seals a letter for a king already buried.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; letter folded and sealed, no writing visible; signet on right forefinger; single candle
- Permitted action: Kent presses the signet into the wax and lifts his hand; the wax settles; candle flame breathes; smoke thread rises.
- Preferred method (suggestion): HIGGSFIELD_I2V
- Fallback: STILL+ENGINE (plate + locked engine preset push/fx) if the I2V test breaks an invariant
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: slow push 1.00->1.04 toward the seal (S001); hands crop S052; bookend wide S098 as a slow pull-back.
- Effects: fx_candle on the table candle with spill on face and hands; smoke_v2 wisp off the wick.
- Masks / protection: face, both hands and the seal rigid; spill excluded from the wax pool highlight.
- Title: none over H06 (v2). The house title now lives on the LONGFORM-HOUSE-INTRO leaf (SC01), not over S001-S002.

### CB1 — Chronicle card base

Class CARD · batch 2 · expected file `cb1_chronicle_card_base_16x9_OWNER.png` · shots SC01, SC02, SC03, SC04 · lines L05, L07, L28, L29, L58, L59 · claims none (silent card)

VO: none (silent cards SC01-SC04).

Narrative purpose: One reusable base for the title card (SC01) and every act card (SC02-SC04, plus SC05 if the 4-act option is taken): an aged chronicle leaf whose empty field receives engine-rendered engraved type.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Old parchment cream and umber, faded oxblood and midnight-blue ink, candle gold spill, warm darkness at the edges.

Scene: A single large leaf of aged vellum lying flat on a dark oak writing desk, seen from directly above, filling almost the whole frame. The leaf is stained, softly cockled and darkened at the edges, with a few small worm holes and a faint fold crease. Ruled in faded brown ink: a simple double-line border with small penwork corner flourishes in faded oxblood and midnight blue, and a broad, empty central field of bare vellum inside it, with faint pricking and dry-point ruling lines. A little dark oak shows at the outer edges.

Continuity: Same desk and parchment world as DK1, DR1, DF2 and DM1 (house desk); grade matches the Recovered Chronicle plates.

Composition: Flat, top-down, the leaf centred and square to the frame. The empty central field covers the middle half of the frame width and about a third of its height, perfectly clear, for engine type at centre; nothing important within 6% of any edge.

Lighting and animation readiness: Warm candlelight falling from off-frame left, soft falloff to warm darkness at the right and lower edges; a faint sheen on the vellum. The image is one frozen instant.

Shot-specific constraints: The central field is bare vellum: no writing, letters, numerals, initials, seals or marks in it (the engine inks the act titles into this field; a functional requirement, like the atlas clean plate). No candle or hand in frame.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: Title card: the film names itself after the cold open.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; central field bare until the engine inks the type; border rigid; no generated letters
- Permitted action: none (engine type ink-in on a static leaf; candle-spill flicker only)
- Preferred method (suggestion): ENGINE_CARD (LONGFORM-HOUSE-INTRO)
- Fallback: Chronicle Reveal v3.2b (9:16-only composition; 16:9 needs a new comp) on static CB1
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: SC01+SC02 = ONE LONGFORM-HOUSE-INTRO move (7.5 s: ink bloom, pen-stroke wordmark + title, leaf settles, 'ACT I' writes in; LONGFORM-HOUSE-INTRO-BRIEF.md Part 1). SC03/SC04 = standalone ~3.5 s cards on the same leaf: 'ACT II' / 'ACT III' pen-stroke write-in, slow push 1.00->1.02, act crossfade across the card.
- Effects: fx_candle spill flicker on the vellum from off-frame left; ink bloom only in the margins (never over the type field).
- Type (engine, never generated): stroke-reveal along the letter paths (not a fade, wipe or slide), multiply blend, paper-texture displacement, fibre feathering, uneven pressure, no glow/drop shadow; iron-gall brown. Face: proposed Source Serif Pro Semibold (house Shorts title face) or IM Fell (repo fonts/ofl); Atelier Jr records the licence. Wordmark from the locked master only (MISSING; see ASSET-TRANSFER-INDEX).
- Text rules (owner DECIDED/APPROVED 12:41pm ET): act cards carry ONLY 'ACT I' / 'ACT II' / 'ACT III' centred: no subtitles, no ornaments, no extra text; no quotation marks, no dates, no status labels.
- Masks / protection: the type layer sits above the candle flicker so letters never shimmer; border rigid; no ink blot over any letter.

### N01 — The brothers

Class NEW · batch 3 · expected file `n01_the_brothers_16x9_OWNER.png` · shots S007, S007a, S008, S018 · lines L07, L07a, L08, L17 · claims NR-1, NR-2

VO (anchor shot S008, L08 (part, 26 of 38 words)): "Kent stayed loyal to him. Edward made him Earl of Kent, and for years Kent served him as one of the great lords of the realm,"

VO on this plate, script v3.2 verbatim (every shot):
- S007 (L07): "Edmund of Kent was the youngest son of King Edward the First, born to the old king's second wife, and he came into the world when his half-brother Edward was already seventeen."
- S007a (L07a): "By the time Kent was a grown man, that half-brother was king, as Edward the Second."
- S008 (L08 (part, 26 of 38 words)): "Kent stayed loyal to him. Edward made him Earl of Kent, and for years Kent served him as one of the great lords of the realm,"
- S018 (L17): "So the Earl of Kent had helped to bring down his own brother. Everything he did later runs against that fact."

Narrative purpose: Show the two brothers of one royal house, the king and the loyal younger half-brother at his shoulder.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Cool window daylight, royal blue and gold, red cloth of estate, oxblood and midnight blue.

Scene: England, the 1320s, a royal chamber in cool daylight from a tall window, a red cloth of estate behind the throne. Seated on a carved oak throne: King Edward the Second: a tall, broad-shouldered man of about forty with fair hair to the jaw and a short fair beard, in a royal blue and gold robe and a simple gold crown, calm and regal. Standing at his right shoulder, one step lower, half-turned toward the viewer: Edmund, Earl of Kent, the same man in every image: an English royal nobleman in his late twenties, lean and upright, medium height, pale skin, short dark auburn hair cut level just below the ears with a soft centre parting, a short neatly trimmed dark auburn beard and moustache, a straight narrow nose, steady grey-blue eyes under straight dark brows. Early fourteenth-century English noble dress: a knee-length oxblood-red wool cote with a round neck and close-fitting sleeves buttoned from elbow to wrist with small gilt buttons, a narrow dark leather belt, dark hose, plain black leather shoes, and over it a long deep midnight-blue wool mantle lined with grey-and-white squirrel fur, fastened at the right shoulder by a round gold ring brooch; a heavy gold signet ring on the forefinger of his right hand. Bareheaded, no crown, no coronet, no armour. An original painted face, not a portrait of any real person or actor. Both are formal and composed; no one else is in the room.

Continuity: Attach the Short plate b04 (b04_the_brothers_OWNER.png) as the reference for both faces, costume and the room.

Composition: Wide, eye level. The king seated left of centre, Kent standing right of centre, with a clear gap of tapestry between their heads so each can be framed alone: Kent at medium, and the king alone on his throne. Throne steps and rush-strewn floor across the foreground.

Lighting and animation readiness: Daylight from the tall window at left; two iron cressets on the wall behind burn with small whole flames. Dust hangs in the window shaft. The image is one frozen instant.

Shot-specific constraints: No heraldry beyond the gold lions on red cloth.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: Introduce Kent as the younger brother.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; king and Kent distinct and consistent with their refs; no crown on Kent; no added figures
- Permitted action: Kent turns his head toward the king; a slight shift of weight at the king's shoulder; cloth and banner stir.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S007 Kent medium -> S008 pull-back to wide (matched reframe) -> S009 the king alone, slow push; S018 Kent close as a callback.
- Effects: fx_candle on the two cressets; dust_v1 in the window shaft.
- Masks / protection: both faces and hands rigid.
- Special: S009 grade cools about 5% across the shot; S018 grades warm.

### N02 — Landing 1326

Class NEW · batch 3 · expected file `n02_landing_1326_16x9_OWNER.png` · shots S010, S011, S012 · lines L10, L11, L12 · claims NR-3, C11-a (actions only; C11-b motive BLOCKED)

VO (anchor shot S011, L11): "In the autumn, Isabella and Roger Mortimer landed in England with an invading force. The Earl of Kent landed with them."

VO on this plate, script v3.2 verbatim (every shot):
- S010 (L10): "And in the end his own wife, Queen Isabella, turned against him too, alongside her ally, a lord of the Welsh borderlands named Roger Mortimer."
- S011 (L11): "In the autumn, Isabella and Roger Mortimer landed in England with an invading force. The Earl of Kent landed with them."
- S012 (L12): "The records tell us what Kent did. They do not tell us why he did it."

Narrative purpose: Isabella returns with Mortimer and an army, and Kent is one of them.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Grey-green sea light, wet sand, crimson, dark green and midnight blue, pale sky.

Scene: England, autumn 1326, an English shore under a pale overcast sky. Ships ride at anchor offshore and small boats are drawn up on the sand; armed men in mail and surcoats wade and climb ashore with banners furled. In the middle ground stand side by side Queen Isabella: an elegant, composed woman of about thirty in a rich dark crimson gown and white veil with a slim gold circlet, a dark travelling cloak over it, and Roger Mortimer: a hard-faced English baron around forty, dark-haired with a short dark beard and heavy brows, in a dark green surcoat over mail. One step behind them, stepping onto the sand from a boat: Edmund, Earl of Kent, the same man in every image: an English royal nobleman in his late twenties, lean and upright, medium height, pale skin, short dark auburn hair cut level just below the ears with a soft centre parting, a short neatly trimmed dark auburn beard and moustache, a straight narrow nose, steady grey-blue eyes under straight dark brows. Early fourteenth-century English noble dress: a knee-length oxblood-red wool cote with a round neck and close-fitting sleeves buttoned from elbow to wrist with small gilt buttons, a narrow dark leather belt, dark hose, plain black leather shoes, and over it a long deep midnight-blue wool mantle lined with grey-and-white squirrel fur, fastened at the right shoulder by a round gold ring brooch; a heavy gold signet ring on the forefinger of his right hand. Bareheaded, no crown, no coronet, no armour. An original painted face, not a portrait of any real person or actor. His face is calm and unreadable.

Continuity: Attach the Short plate b05 as the reference for Isabella, Mortimer, Kent and the landing.

Composition: Wide, slightly low angle along the shoreline. Isabella and Mortimer in the left-centre middle ground; Kent at right with open sand around him so he can be framed alone; ships far back. A clear band of shallow water across the foreground.

Lighting and animation readiness: Soft overcast light from the left; a bright edge on the wet sand. Shallow waves painted clearly along the shoreline; light sea haze over the far ships. The image is one frozen instant.

Shot-specific constraints: Mortimer stands as an ally beside the queen, with no intimacy between them.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: Isabella turns against him, with Mortimer.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; non-graphic; no battle; one landing, no fleet invented beyond the plate
- Permitted action: Landing party moves up the shore; banners stir in wind; surf runs in.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S010 Isabella and Mortimer crop, drift left 2% -> S011 pull-back revealing Kent -> S012 Kent close, micro push.
- Effects: water_v1 on the foreground shallows (masked); smoke_v2 sea haze on the far ships.
- Masks / protection: faces and hands rigid; banners rigid.

### N03 — Kenilworth the crown

Class NEW · batch 3 · expected file `n03_kenilworth_the_crown_16x9_OWNER.png` · shots S015, S092 · lines L14, L93 · claims C25

VO (anchor shot S015, L14 (part, ~55% of line)): "He was taken to Kenilworth Castle, in the middle of England, and there he lost his crown."

Narrative purpose: At Kenilworth the deposed king gives up his crown.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Cold stone grey, candle gold, faded royal blue, black.

Scene: England, 1327, a stone chamber in Kenilworth Castle. A tall, fair-bearded man of about forty-three in a plain dark gown, the deposed King Edward the Second (the same face as King Edward the Second in the brothers image, now uncrowned and drawn), sits slumped on a plain chair, looking away. On a table before him rests the gold crown on a dark cushion, no longer on his head. A group of lords in furred gowns waits by the door, watching him.

Continuity: Attach N01 (once approved) for Edward's face; same man, older and stripped of royal robes.

Composition: Medium-wide. Edward left, the crown on its cushion in the centre, sharply lit and clear of hands and faces so a close framing on the crown alone reads; the lords at right in shade.

Lighting and animation readiness: Two candles on a ledge, whole and crisp; grey window light from behind the lords. The image is one frozen instant.

Shot-specific constraints: A quiet moment, not a ceremony: the crown rests on the table, and no one holds it.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: There he lost his crown.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; no violence; Edward's face stays consistent; no added witnesses
- Permitted action: The crown is set down / held still in a cold room; light shifts across the stone.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S015 slow push 1.00->1.04 on the crown; S092 crown close, micro push.
- Effects: fx_candle on the ledge candles.
- Masks / protection: faces and the crown rigid.

### N04 — The boy king crowned

Class NEW · batch 3 · expected file `n04_the_boy_king_crowned_16x9_OWNER.png` · shots S016, S017 · lines L15, L16 · claims NR-4

VO (anchor shot S016, L15): "His teenage son, also named Edward, was crowned Edward the Third. Kent's own nephew was now king."

VO on this plate, script v3.2 verbatim (every shot):
- S016 (L15): "His teenage son, also named Edward, was crowned Edward the Third. Kent's own nephew was now king."
- S017 (L16): "But the real power belonged to the boy's mother, Isabella, and to Roger Mortimer."

Narrative purpose: The boy king is crowned while real power stands behind him.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Candle gold, incense haze, white and gold vestments, crimson, dark green.

Scene: England, 1 February 1327, the choir of a great abbey church during a coronation. Seated on the coronation chair, small inside his robes: the boy king Edward the Third, fourteen, fair-haired, beardless, a crown just set on his head. Bishops in white and gold vestments stand around him. Behind the chair, a step back in rich dress: Queen Isabella: an elegant, composed woman of about thirty in a rich dark crimson gown and white veil with a slim gold circlet, a dark travelling cloak over it, without the travelling cloak, and Roger Mortimer: a hard-faced English baron around forty, dark-haired with a short dark beard and heavy brows, in a dark green surcoat over mail, now in a dark green furred gown. Lords crowd the stalls.

Continuity: Attach b05 for Isabella and Mortimer; Edward III's face here becomes the anchor for N16.

Composition: Wide, looking up the choir. The boy central and slightly low; Isabella and Mortimer behind him to the right, framed together with clear space around them for a medium crop. Candles and stalls lead the eye in.

Lighting and animation readiness: Tall candles on stands either side of the chair, whole and sharp; incense haze in the candlelight. The image is one frozen instant.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: The boy king is crowned; Kent's nephew.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; the boy king's age reads ~14; no added text or heraldry
- Permitted action: The young king is crowned: crown lowered, onlookers still; incense drifts.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S016 slow push up the choir; S017 Isabella and Mortimer crop, drift right 2%.
- Effects: fx_candle on the candle stands; smoke_v2 incense haze.
- Masks / protection: faces, crown and hands rigid.

### N05 — Berkeley at dusk

Class NEW · batch 4 · expected file `n05_berkeley_at_dusk_16x9_OWNER.png` · shots S020, S022, S057, S060, S077, S089 · lines L19, L21, L55, L58, L76, L89, L90 · claims C25, C20

VO (anchor shot S020, L19): "In late September, word went out that Edward of Caernarfon, the former king, was dead."

VO on this plate, script v3.2 verbatim (every shot):
- S020 (L19): "In late September, word went out that Edward of Caernarfon, the former king, was dead."
- S022 (L21): "No surviving official record says how he had died."
- S057 (L55): "Thomas, Lord Berkeley, held the castle where Edward was said to have died, and he had to answer for the death."
- S060 (L58): "So the record itself treats the death as a murder. Some historians still read Berkeley's first words as a denial that the king had died at all. Others read them as a lord denying any part in a killing."
- S077 (L76): "Most historians hold that Edward the Second died at Berkeley."
- S089 (L89; L90): "So what can the evidence establish? It can establish that no surviving official record of the time said how he died, and that the new government later called it murder."

Narrative purpose: Berkeley Castle at dusk: the place where the former king was held, and where the evidence keeps returning.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Red sandstone, dusk violet, Severn silver, a single warm window.

Scene: England, Gloucestershire, dusk. Berkeley Castle seen across water meadows and its moat: a low, massive red-sandstone shell keep and curtain wall, the gatehouse, a church tower beyond. The wide grey Severn estuary glimmers in the far distance. One small window high in the keep is lit. The meadows are empty.

Continuity: Attach the Short plate p04 (or b06) as the reference for Berkeley's architecture and light.

Composition: Wide, eye level from across the moat. Keep and gate in the centre-right; the lit window clearly isolated against dark stone so it can be framed alone; moat across the foreground.

Lighting and animation readiness: Last violet light in the sky; the lit window glows warm with a crisp interior flame shape. Still water in the moat with a faint reflection; low mist over the meadows. The image is one frozen instant.

Shot-specific constraints: No figure in the window or on the walls.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: Word goes out that the former king is dead.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; no figures implying the manner of death; no interior view of the death; Berkeley geometry fixed
- Permitted action: Dusk light fades over Berkeley; a window light comes on; birds or smoke move.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S020 very slow push; S022/S089 window crop holds; S057 keep and gate crop; S060/S077 wide.
- Effects: water_v1 on the moat (masked); fx_candle spill in the window; smoke_v2 low mist.
- Masks / protection: architecture rigid; the window glow must not bleed into the sky.

### N06 — The viewing

Class NEW · batch 4 · expected file `n06_the_viewing_16x9_OWNER.png` · shots S023, S024, S086 · lines L22, L23, L86 · claims C04

VO (anchor shot S023, L22): "A chronicler of the time, Adam Murimuth, says that local notables were called to see the body: abbots, priors, knights, and leading townsmen of Bristol and Gloucester."

VO on this plate, script v3.2 verbatim (every shot):
- S023 (L22): "A chronicler of the time, Adam Murimuth, says that local notables were called to see the body: abbots, priors, knights, and leading townsmen of Bristol and Gloucester."
- S024 (L23): "But Murimuth adds a strange detail. He says they looked at it only superficially."
- S086 (L86): "There was a body. Local notables were called to view it, even if one chronicler says they looked only superficially."

Narrative purpose: Local notables are brought to view the body, and look only from a distance.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Candle gold, black, cold stone, dull wool browns.

Scene: England, 1327, a dim stone chamber. A bier stands in the middle ground covered entirely by a heavy dark pall, candles at its corners. At the doorway, abbots and priors in black and white habits, knights in surcoats and burgesses in plain wool gowns stand back, a few steps from the bier, looking toward it but keeping their distance.

Continuity: None; no named characters.

Composition: Wide, from inside the chamber toward the doorway. The covered bier in the left-centre middle ground; the onlookers grouped at right by the door so they can be framed alone.

Lighting and animation readiness: Four candles at the bier corners, whole and sharp; a faint grey light in the doorway. The image is one frozen instant.

Shot-specific constraints: The pall covers everything: no face, hands or form of a body shown.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: Notables are called to see the body.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; body covered, face not graphic; no wounds; witnesses per C-ledger wording only
- Permitted action: Notables step forward to view the body under the cloth; a candle gutters.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S023 lateral drift 3%; S024 onlookers crop, slow push; S086 reuse.
- Effects: fx_candle on bier candles; smoke_v2 wisps.
- Masks / protection: the pall and faces rigid.

### H01 — Gloucester funeral wide with Kent

Class HERO · batch 1 · expected file `h01_gloucester_funeral_wide_kent_16x9_OWNER.png` · shots S003, S025, S026, S028, S087, S093 · lines L03, L24, L25, L27, L87, L94 · claims C04, C06, C10

VO (anchor shot S003, L03): "Kent had stood at Edward's funeral at Gloucester."

VO on this plate, script v3.2 verbatim (every shot):
- S003 (L03): "Kent had stood at Edward's funeral at Gloucester."
- S025 (L24): "Historians think that at the funeral itself, a wooden effigy of the king was probably displayed."
- S026 (L25): "Edward was buried at Gloucester just before Christmas, about three months after his death was announced."
- S028 (L27): "England moved on under its new rulers."
- S087 (L87): "There was a royal funeral, with Kent himself in attendance."
- S093 (L94): "He stood at his brother's funeral."

Narrative purpose: The royal funeral at Gloucester, and Kent among the mourners.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Deep candle gold, black velvet, cold stone grey, faded heraldic red and blue, wax white.

Scene: England, December 1327, the dim stone choir of Gloucester Abbey at night, tall round Norman columns rising into darkness. Right of centre: a royal hearse, a tall wooden frame draped in black and crowded with burning candles, holding a closed coffin under black cloth; lying on top, a carved and painted wooden effigy of a crowned king, hands folded, a copper-gilt crown on its head. Monks in black habits stand with heads bowed along it; richly dressed mourners stand back in shadow. Left third, standing a little apart and looking toward the effigy: Edmund, Earl of Kent, the same man in every image: an English royal nobleman in his late twenties, lean and upright, medium height, pale skin, short dark auburn hair cut level just below the ears with a soft centre parting, a short neatly trimmed dark auburn beard and moustache, a straight narrow nose, steady grey-blue eyes under straight dark brows. Early fourteenth-century English noble dress: a knee-length oxblood-red wool cote with a round neck and close-fitting sleeves buttoned from elbow to wrist with small gilt buttons, a narrow dark leather belt, dark hose, plain black leather shoes, and over it a long deep midnight-blue wool mantle lined with grey-and-white squirrel fur, fastened at the right shoulder by a round gold ring brooch; a heavy gold signet ring on the forefinger of his right hand. Bareheaded, no crown, no coronet, no armour. An original painted face, not a portrait of any real person or actor.

Continuity: Attach the Short plate b01 (b01_gloucester_funeral_wide_kent_OWNER.png) as the hero reference for Kent, the hearse and the choir.

Composition: Wide, eye level. Kent left with clear space around him; the effigy and crown right of centre, clearly framed so each can be cropped alone; a high corner of the choir with candles above the mourners for a third framing.

Lighting and animation readiness: The hearse candles are the main light, each flame whole and crisp; incense haze lies in their glow. The image is one frozen instant.

Shot-specific constraints: Closed coffin under the effigy; Kent looks toward the effigy, not at a body.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: Preview: the kingdom buried Edward, and Kent was there.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; Kent consistent; coffin/effigy covered; Gloucester geometry fixed
- Permitted action: Procession moves slowly; mourners shift; incense rises; Kent turns his head.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S003 drift toward Kent; S025 effigy crop push; S026 wide pull-back; S028 upper-choir crop; S087 wide; S093 Kent crop.
- Effects: fx_candle on hearse candles; smoke_v2 wisps.
- Masks / protection: Kent's face and the effigy rigid.

### N07 — Kent at the funeral, close

Class NEW · batch 1 · expected file `n07_kent_at_the_funeral_close_16x9_OWNER.png` · shots S027, S081, S097 · lines L26, L80, L96a · claims C10

VO (anchor shot S027, L26): "The Earl of Kent was there. No record says whether he ever saw his brother's body."

VO on this plate, script v3.2 verbatim (every shot):
- S027 (L26): "The Earl of Kent was there. No record says whether he ever saw his brother's body."
- S081 (L80): "First, Kent's own belief. He was the king's brother, he had been at the funeral, and he still staked his life on the reports."
- S097 (L96a (part, 10 of 34 words)): "What they do show is what his choice cost him."

Narrative purpose: Kent, close, at his brother's funeral: present, but no record says he saw the body.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Candle gold, midnight blue, oxblood, warm shadow.

Scene: England, December 1327, Gloucester Abbey choir at night. Close portrait of Edmund, Earl of Kent, the same man in every image: an English royal nobleman in his late twenties, lean and upright, medium height, pale skin, short dark auburn hair cut level just below the ears with a soft centre parting, a short neatly trimmed dark auburn beard and moustache, a straight narrow nose, steady grey-blue eyes under straight dark brows. Early fourteenth-century English noble dress: a knee-length oxblood-red wool cote with a round neck and close-fitting sleeves buttoned from elbow to wrist with small gilt buttons, a narrow dark leather belt, dark hose, plain black leather shoes, and over it a long deep midnight-blue wool mantle lined with grey-and-white squirrel fur, fastened at the right shoulder by a round gold ring brooch; a heavy gold signet ring on the forefinger of his right hand. Bareheaded, no crown, no coronet, no armour. An original painted face, not a portrait of any real person or actor. He stands among shadowed mourners, looking off to the right toward unseen candlelight, his face still and grave.

Continuity: Attach the Short plate b07 and H01 (once approved): same face, mantle and brooch; the same choir behind.

Composition: Close, head and shoulders, Kent left of centre, looking right into open space; soft Norman columns and candle points behind.

Lighting and animation readiness: Warm candlelight from the right on his face; a few small candle flames, whole and sharp, in the soft background. The image is one frozen instant.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: Kent was there; no record says he saw the body.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; Kent identity; no tears exaggerated; no added figures
- Permitted action: Kent's eyes lift from the coffin; candlelight trembles.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S027 micro push 1.00->1.02; S081 reuse.
- Effects: fx_candle spill on the face (from the right).
- Masks / protection: face rigid; spill padding around the eyes.

### N08 — Reports reach Kent

Class NEW · batch 1 · expected file `n08_reports_reach_kent_16x9_OWNER.png` · shots S029, S033 · lines L28, L31 · claims C09, C09b

VO (anchor shot S029, L28): "Then reports began to reach Kent that his brother was still alive."

VO on this plate, script v3.2 verbatim (every shot):
- S029 (L28): "Then reports began to reach Kent that his brother was still alive."
- S033 (L31): "According to Kent's own confession, a friar had assured him that Edward was alive, claiming that the devil had told him so."

Narrative purpose: Reports reach Kent in the quiet of a cloister: men of the church telling him something.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Lantern gold, black friars' habits, cold stone blue, midnight blue.

Scene: England, a cloister walk at night. Two friars in black mantles over white habits stand close with Edmund, Earl of Kent, the same man in every image: an English royal nobleman in his late twenties, lean and upright, medium height, pale skin, short dark auburn hair cut level just below the ears with a soft centre parting, a short neatly trimmed dark auburn beard and moustache, a straight narrow nose, steady grey-blue eyes under straight dark brows. Early fourteenth-century English noble dress: a knee-length oxblood-red wool cote with a round neck and close-fitting sleeves buttoned from elbow to wrist with small gilt buttons, a narrow dark leather belt, dark hose, plain black leather shoes, and over it a long deep midnight-blue wool mantle lined with grey-and-white squirrel fur, fastened at the right shoulder by a round gold ring brooch; a heavy gold signet ring on the forefinger of his right hand. Bareheaded, no crown, no coronet, no armour. An original painted face, not a portrait of any real person or actor.; one leans in and speaks low, the other holds a lantern. Kent listens intently.

Continuity: Attach b08 for Kent and the cloister.

Composition: Medium-wide along the cloister arcade. Kent centre-left; the speaking friar clearly separated at right so a close framing on him alone works; arcade receding behind.

Lighting and animation readiness: The lantern is the only light, flame whole and crisp; moonlight touches the arches. The image is one frozen instant.

Shot-specific constraints: Ordinary men in an ordinary cloister, nothing supernatural.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: Reports begin to reach Kent.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; letter not legible; Kent identity
- Permitted action: A messenger hands over a report; Kent reads, hands tighten.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S029 slow push; S033 friar crop, micro push.
- Effects: fx_candle on the lantern flame.
- Masks / protection: faces and hands rigid.

### N09 — Kent before the pope

Class NEW · batch 1 · expected file `n09_kent_before_the_pope_16x9_OWNER.png` · shots S031, S032 · lines L29, L30 · claims C09

VO (anchor shot S031, L29 (part, ~50% of line)): "According to an English chronicle called the Brut, Kent went to see the pope at Avignon, where the pope held his court, and spoke of a common report in England that Edward was alive."

Narrative purpose: Kent goes to the pope and speaks of a common report that his brother lives.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Deep crimson, white silk, gold, candle gold, warm stone.

Scene: A papal audience chamber with painted walls in deep red and gold, lit by candles. Seated on a raised chair under a canopy: an aged, slight pope in a white cassock, a red mozzetta and a red cap, his right hand raised in blessing. Kneeling before him on the lowest step: Edmund, Earl of Kent, the same man in every image: an English royal nobleman in his late twenties, lean and upright, medium height, pale skin, short dark auburn hair cut level just below the ears with a soft centre parting, a short neatly trimmed dark auburn beard and moustache, a straight narrow nose, steady grey-blue eyes under straight dark brows. Early fourteenth-century English noble dress: a knee-length oxblood-red wool cote with a round neck and close-fitting sleeves buttoned from elbow to wrist with small gilt buttons, a narrow dark leather belt, dark hose, plain black leather shoes, and over it a long deep midnight-blue wool mantle lined with grey-and-white squirrel fur, fastened at the right shoulder by a round gold ring brooch; a heavy gold signet ring on the forefinger of his right hand. Bareheaded, no crown, no coronet, no armour. An original painted face, not a portrait of any real person or actor. His face is lifted, earnest, speaking. Two clerics stand to one side.

Continuity: Attach b07 (b07_kent_at_funeral_close_OWNER.png) or H01 (once approved) for Kent's face and dress. The pope is an original painted face, not a portrait.

Composition: Wide, a little low. The pope upper right, Kent kneeling lower left, a clear diagonal of floor between them for depth; the pope's raised hand and Kent's face both readable in one medium framing.

Lighting and animation readiness: Tall candlesticks either side of the chair, flames whole and sharp; incense haze under the canopy. The image is one frozen instant.

Shot-specific constraints: Interior only: no exterior view.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: Kent speaks of the common report before the pope.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; pope generic (no named portrait); no text on screen
- Permitted action: Kent kneels or bows before the pope; the pope raises a hand; cloth settles.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S031 slow push; S032 blessing-and-kneeling crop, slow push.
- Effects: fx_candle on candlesticks; smoke_v2 incense.
- Masks / protection: both faces and the blessing hand rigid.

### N10 — Corfe by moonlight

Class NEW · batch 1 · expected file `n10_corfe_by_moonlight_16x9_OWNER.png` · shots S034 · lines L32 · claims C09

VO (anchor shot S034, L32): "And the Brut says that friars told him where. Edward, they said, was being held in Corfe Castle, in Dorset."

VO on this plate, script v3.2 verbatim (every shot):
- S034 (L32): "And the Brut says that friars told him where. Edward, they said, was being held in Corfe Castle, in Dorset."

Narrative purpose: Corfe Castle by moonlight: the place the friars named.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Moon silver, slate blue, chalk grey, one warm window.

Scene: England, Dorset, night. Corfe Castle stands whole and royal on its steep green hill in a gap between the Purbeck ridges: a tall square stone keep, curtain walls stepping down the slope, the gatehouse below. A full moon sits low over the ridge. One window high in the keep is lit. Mist lies in the valley around the hill.

Continuity: Attach the Short plate b03 (b03_corfe_moonlit_from_below_OWNER.png) as the reference for Corfe's architecture; H02, H04, N19 and E01 must match it.

Composition: Wide, from the valley floor. The castle and hill centre, the lit window clearly isolated against dark stone; open moonlit sky above; mist across the foreground.

Lighting and animation readiness: Cold moonlight from the upper left; the single window glows warm with a crisp flame shape inside. The image is one frozen instant.

Shot-specific constraints: Corfe is intact: no ruin.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: The friars name the place: Corfe.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; Corfe geometry fixed; no figures implying a captive seen
- Permitted action: Moonlit cloud passes over Corfe; a single window glows; wind in grass.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S034 slow push 1.00->1.04 toward the lit window.
- Effects: fx_candle spill in the window; smoke_v2 low valley mist.
- Masks / protection: architecture rigid; window glow kept inside the frame of the window.

### N11 — The supporters

Class NEW · batch 2 · expected file `n11_the_supporters_16x9_OWNER.png` · shots S035, S036, S037, S082 · lines L33, L34, L35, L81 · claims C08, C07

VO (anchor shot S035, L33): "Kent was not acting alone. His confession names powerful backers, among them an archbishop, a bishop and several knights."

VO on this plate, script v3.2 verbatim (every shot):
- S035 (L33): "Kent was not acting alone. His confession names powerful backers, among them an archbishop, a bishop and several knights."
- S036 (L34): "The archbishop was William Melton of York. The confession says he promised Kent five thousand pounds."
- S037 (L35): "One modern historian, Kathryn Warner, has traced around seventy men who supported him."
- S082 (L81): "Second, he was not alone. Kathryn Warner argues that his supporters were many, and often close to Edward."

Narrative purpose: Kent was not alone: powerful men gathered around his cause.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Candle gold, oxblood, dark greens and browns, black shadow.

Scene: England, a manor hall at night. Around a long oak table lit by candles sit and stand a group of English lords and knights in furred gowns and surcoats, leaning in toward one another. At the head of the table: Edmund, Earl of Kent, the same man in every image: an English royal nobleman in his late twenties, lean and upright, medium height, pale skin, short dark auburn hair cut level just below the ears with a soft centre parting, a short neatly trimmed dark auburn beard and moustache, a straight narrow nose, steady grey-blue eyes under straight dark brows. Early fourteenth-century English noble dress: a knee-length oxblood-red wool cote with a round neck and close-fitting sleeves buttoned from elbow to wrist with small gilt buttons, a narrow dark leather belt, dark hose, plain black leather shoes, and over it a long deep midnight-blue wool mantle lined with grey-and-white squirrel fur, fastened at the right shoulder by a round gold ring brooch; a heavy gold signet ring on the forefinger of his right hand. Bareheaded, no crown, no coronet, no armour. An original painted face, not a portrait of any real person or actor. Behind them, in shadow, more men stand along the wall. On the table: candles, pewter cups, a jug, hands resting on the wood.

Continuity: Attach the Short plate b09 (b09_kent_supporters_OWNER.png) for Kent and the hall.

Composition: Wide, eye level down the table. Kent at the far end, centre; the candles, cups and hands in the near foreground clear of faces so they can be framed alone; the standing men in shadow at right as a third framing.

Lighting and animation readiness: Five or six candles down the table, whole and crisp, the only light; faces lit warm from below; smoke from the wicks. The image is one frozen instant.

Shot-specific constraints: No one dressed as an archbishop or bishop; no coins on the table.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: Kent was not alone.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; no new named faces beyond ledger; no plotting text
- Permitted action: Supporters lean in, one nods, a cup is set down.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S035 lateral drift 3%; S036 table crop, slow push; S037 shadowed men crop; S082 reuse.
- Effects: fx_candle on table candles; smoke_v2 wisps.
- Masks / protection: faces and hands rigid.

### H02 — Corfe gate handover

Class HERO · batch 2 · expected file `h02_corfe_kent_hands_letter_16x9_OWNER.png` · shots S038, S039, S094 · lines L36, L37, L95 · claims C09

VO (anchor shot S038, L36): "Then, as the Brut tells it, Kent came to Corfe himself, with a letter for his brother, closed and sealed with his own seal."

VO on this plate, script v3.2 verbatim (every shot):
- S038 (L36): "Then, as the Brut tells it, Kent came to Corfe himself, with a letter for his brother, closed and sealed with his own seal."
- S039 (L37): "At Corfe he gave it to a man named John Deveril."
- S094 (L95): "Then, just over two years later, he gave his life trying to set that same brother free."

Narrative purpose: As the Brut tells it, Kent comes to Corfe himself and hands over a sealed letter.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Chalk grey, mist white, dull green, umber, midnight blue, torch orange and wax red.

Scene: England, 1330, dusk at the gatehouse arch of Corfe Castle in Dorset, intact and royal, the tall stone keep rising on its steep green hill above, the curtain wall running across the frame, ground mist below. Left of centre, in three-quarter view, holding out a folded parchment letter sealed with red wax: Edmund, Earl of Kent, the same man in every image: an English royal nobleman in his late twenties, lean and upright, medium height, pale skin, short dark auburn hair cut level just below the ears with a soft centre parting, a short neatly trimmed dark auburn beard and moustache, a straight narrow nose, steady grey-blue eyes under straight dark brows. Early fourteenth-century English noble dress: a knee-length oxblood-red wool cote with a round neck and close-fitting sleeves buttoned from elbow to wrist with small gilt buttons, a narrow dark leather belt, dark hose, plain black leather shoes, and over it a long deep midnight-blue wool mantle lined with grey-and-white squirrel fur, fastened at the right shoulder by a round gold ring brooch; a heavy gold signet ring on the forefinger of his right hand. Bareheaded, no crown, no coronet, no armour. An original painted face, not a portrait of any real person or actor. Facing him in the arch, taking the letter: a heavy-set man in a mail coat and a plain dark surcoat. Behind Kent a groom holds his saddled horse.

Continuity: Attach the Short plate b10 (b10_corfe_kent_hands_letter_OWNER.png) as the hero reference for Kent, the man and the gate; match Corfe to N10.

Composition: Medium-wide. Kent left, the man right, the letter between their hands in the centre and clear of both faces so a close framing on the hands reads; the keep above the arch; the lane falling away left.

Lighting and animation readiness: One iron torch in a bracket beside the arch, its flame whole and sharp; cool dusk light elsewhere. The image is one frozen instant.

Shot-specific constraints: The man carries nothing that marks an office.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5) · **I2V TEST CANDIDATE**

- Dramatic intent: Kent comes to Corfe with a sealed letter, as the Brut tells it.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; letter sealed; Corfe gate geometry; no proof that the king is inside shown
- Permitted action: A gatekeeper/agent at the Corfe gate receives a sealed letter from a messenger; the gate stays shut behind.
- Preferred method (suggestion): HIGGSFIELD_I2V
- Fallback: STILL+ENGINE (plate + locked engine preset push/fx) if the I2V test breaks an invariant
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S038 slow push; S039 hands crop; S094 wide reuse.
- Effects: torch_v1c on the gate torch.
- Masks / protection: faces, hands and the letter rigid; torch spill excluded from faces.

### N12 — Mortimer reads the letter

Class NEW · batch 2 · expected file `n12_mortimer_reads_the_letter_16x9_OWNER.png` · shots S040, S098a · lines L38, L97 · claims C09

VO (anchor shot S040, L38): "The Brut says the letter never reached Edward. Deveril took it to Roger Mortimer instead."

VO on this plate, script v3.2 verbatim (every shot):
- S040 (L38): "The Brut says the letter never reached Edward. Deveril took it to Roger Mortimer instead."
- S098a (L97 (part, 6 of 21 words)): "It went to Roger Mortimer instead."

Narrative purpose: The letter goes to Mortimer instead.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Candle gold, black, dark green, oxblood and old parchment.

Scene: England, 1330, a private chamber at night. Roger Mortimer: a hard-faced English baron around forty, dark-haired with a short dark beard and heavy brows, in a dark green surcoat over mail. He sits at a heavy oak table by a single candle, holding an opened letter with a broken red wax seal, reading it with a slow, satisfied, dangerous expression. Behind him, half in shadow, a guard waits by the door.

Continuity: Attach the Short plate p07 (p07_mortimer_reads_letter_OWNER.png) as the reference for Mortimer and the room; Mortimer matches N02, N04 and H03.

Composition: Medium, eye level. Mortimer left of centre, the letter in both hands at chest height facing him; the guard small in the right background with dark wall between them.

Lighting and animation readiness: One candle, whole and crisp, lights his face and the sheet from below. The image is one frozen instant.

Shot-specific constraints: The letter's writing is not visible to us.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5) · **I2V TEST CANDIDATE**

- Dramatic intent: The letter goes to Mortimer instead.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; Mortimer identity; letter not legible; no devil or supernatural visual
- Permitted action: Mortimer breaks the seal and reads; his eyes narrow; candle flame moves.
- Preferred method (suggestion): HIGGSFIELD_I2V
- Fallback: STILL+ENGINE (plate + locked engine preset push/fx) if the I2V test breaks an invariant
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S040 slow push 1.00->1.04.
- Effects: fx_candle.
- Masks / protection: face, hands and letter rigid.

### DK1 — Kent's sealed letter

Class DOC · batch 2 · expected file `dk1_kents_sealed_letter_16x9_OWNER.png` · shots S005, S041, S080, S098 · lines L05, L39, L79, L97 · claims C09, C05c

VO (anchor shot S005, L05): "Why would a king's brother risk his life to rescue a man the whole kingdom had mourned?"

VO on this plate, script v3.2 verbatim (every shot):
- S005 (L05): "Why would a king's brother risk his life to rescue a man the whole kingdom had mourned?"
- S041 (L39): "One chronicle claims to quote its opening words. The letter itself has never been found."
- S080 (L79): "So what is the strongest case that Edward survived?"
- S098 (L97 (part, 15 of 21 words)): "As the Brut tells it, the letter he sealed for his brother never reached him."

Narrative purpose: Kent's letter as an object: closed, sealed, and never seen again.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Old parchment, red wax, candle gold, dark oak.

Scene: A folded parchment letter lies on a dark oak table, tied with a thin cord and closed with a round seal of red wax. Its surface shows folds, a faint stain and soft wear. Warm light from an unseen candle falls across it from the left; the rest of the table falls into darkness.

Continuity: None. This is Kent's letter, and it must look nothing like the Fieschi register (DF2) or the archbishop's letter (DM1).

Composition: Close, slightly above. The seal in the centre right, the folded letter filling the middle of the frame, dark table beyond.

Lighting and animation readiness: A warm candle glow from off-frame left, with a soft moving-light quality the engine can enhance. The image is one frozen instant.

Shot-specific constraints: Closed and sealed: no writing visible; the seal impression soft and indistinct.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: The central question sits on the sealed letter.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; no legible text beyond what the ledger allows; seal intact
- Permitted action: candle spill flicker; slight paper settle; macro push only.
- Preferred method (suggestion): ENGINE_PRESET
- Fallback: static plate + house push and dust_v1
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S005 push 1.00->1.05 to the seal; S041 tighter push; S080 hold.
- Effects: fx_candle spill only (no flame in frame).
- Masks / protection: seal rigid.

### N13 — Winchester: the confession read

Class NEW · batch 4 · expected file `n13_winchester:_the_confession_read_16x9_OWNER.png` · shots S042, S043, S044 · lines L40, L41, L42 · claims C05f, C28

VO (anchor shot S042, L40): "At the parliament held at Winchester, Kent's confession was put before the lords."

VO on this plate, script v3.2 verbatim (every shot):
- S042 (L40): "At the parliament held at Winchester, Kent's confession was put before the lords."
- S043 (L41): "A copy of that confession still survives, written into a chronicle manuscript about seventy years later."
- S044 (L42): "The official record of his trial is lost."

Narrative purpose: At Winchester, Kent's confession is put before the lords.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Cold grey daylight, candle gold, rich robes, dark timber.

Scene: England, March 1330, a great hall at Winchester during parliament: tall arcades, high windows, benches of lords and bishops in robes. In the centre a royal clerk in a dark gown stands and reads from a parchment held in both hands. The lords listen, grave and still.

Continuity: None for faces; the clerk is an original figure.

Composition: Wide, from the end of the hall. The clerk centre, clearly separated from the benches so a medium framing on him works; deep shadow at the far right of the hall for a drift into darkness.

Lighting and animation readiness: Grey daylight through the high windows with dust in the shafts; candles on stands along the benches, flames whole and sharp. The image is one frozen instant.

Shot-specific constraints: Kent is not in the hall. The parchment shows no readable writing.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: At Winchester the confession is put before the lords.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; Kent present per plate; no quoted text on screen; non-graphic
- Permitted action: A clerk reads the confession aloud; listeners still; one turns away.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S042 slow push; S043 clerk crop; S044 drift into the dark of the hall.
- Effects: fx_candle on stand candles; dust_v1 in window shafts.
- Masks / protection: faces rigid.

### N14 — Winchester, the morning after

Class NEW · batch 4 · expected file `n14_winchester_the_morning_after_16x9_OWNER.png` · shots S004, S045, S046, S090, S095 · lines L04, L43, L44, L91, L96 · claims C28

VO (anchor shot S004, L04): "Just over two years later, Kent was beheaded for plotting to set his brother free."

VO on this plate, script v3.2 verbatim (every shot):
- S004 (L04): "Just over two years later, Kent was beheaded for plotting to set his brother free."
- S045 (L43): "The Earl of Kent was condemned for plotting to free a man the government said was dead, and in March he was beheaded at Winchester."
- S046 (L44): "Adam Murimuth called the whole story false. But he also thought Kent's death was unjust."
- S090 (L91): "It can establish what Kent did, and that he and others believed the reports that his brother was alive."
- S095 (L96): "Kent made his choice, and he paid for it with his head."

Narrative purpose: The morning after at Winchester: the cost, shown only as an absence.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Cold grey morning light, pale straw, weathered timber, midnight blue, oxblood and soot black.

Scene: England, March 1330, outside the walls of Winchester Castle on a cold grey morning. In the middle ground a low, empty timber platform strewn with clean pale straw. On its wooden steps lies a long deep midnight-blue wool mantle lined with grey-and-white squirrel fur, a round gold ring brooch still pinned at its shoulder, folded as if just set down. Townsfolk in plain wool hoods and a grey friar stand back with heads bowed, some turning away, seen mostly from behind. The castle wall rises grey behind.

Continuity: Attach the Short plate b12 (b12_winchester_after_OWNER.png) as the reference and keep its arrangement; the mantle and brooch match Kent's character block.

Composition: Wide, eye level. Platform centre, the mantle on the steps lit and clear so it can be framed alone; the townsfolk in the left foreground as a separate medium framing.

Lighting and animation readiness: Flat grey dawn light; low mist hanging along the wall; a little dust in the air. The image is one frozen instant.

Shot-specific constraints: No one on the platform; nothing that shows a death.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: Preview: the cost, condemned and beheaded, shown only as aftermath.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; non-graphic: no execution, no blood, no body
- Permitted action: Morning light grows over the Winchester yard; wind moves straw; an empty block area seen from a distance.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S004 very slow push; S045 slow push; S046 townsfolk crop; S090 empty platform crop; S097 mantle close.
- Effects: smoke_v2 low mist; dust_v1.
- Masks / protection: mantle and brooch rigid.

### N15 — Margaret and the children

Class NEW · batch 4 · expected file `n15_margaret_and_the_children_16x9_OWNER.png` · shots S047, S054, S098c · lines L45, L52, L97a · claims C13

VO (anchor shot S047, L45): "Kent left behind a widow, Margaret, and their children."

VO on this plate, script v3.2 verbatim (every shot):
- S047 (L45): "Kent left behind a widow, Margaret, and their children."
- S054 (L52): "Within weeks of Mortimer's fall, Kent's widow asked parliament to reopen his case."
- S098c (L97a (part, 13 of 40 words)): "And within the year, according to the petition Kent's widow put before parliament,"

Narrative purpose: Kent left a widow and children.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Candle gold, mourning black, white linen, oak brown.

Scene: England, 1330, a quiet chamber. Margaret, Countess of Kent, a young noblewoman in a black gown and white wimple, sits by a window holding the youngest of her small children in her lap; the others are close at her side. Her face is composed but grieving, eyes lowered.

Continuity: None. Margaret is an original painted face; she becomes the anchor for her close framing.

Composition: Medium-wide. Margaret centre-left, her face clear of the children's heads so a close framing on her alone reads; the window right.

Lighting and animation readiness: Soft window light, and one candle on a stand beside her, its flame whole and crisp. The image is one frozen instant.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: He left a widow and children.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; children's ages consistent; no added text
- Permitted action: Margaret holds the children close; a child looks up; candle light moves.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S047 slow push; S054 Margaret close, slow push.
- Effects: fx_candle on the stand candle.
- Masks / protection: faces and hands rigid.

### H03 — Nottingham seizure

Class HERO · batch 5 · expected file `h03_nottingham_seizure_16x9_OWNER.png` · shots S048 · lines L46 · claims C27

VO (anchor shot S048, L46): "That autumn, the young king struck back. At Nottingham Castle, Edward the Third's party seized Roger Mortimer."

VO on this plate, script v3.2 verbatim (every shot):
- S048 (L46): "That autumn, the young king struck back. At Nottingham Castle, Edward the Third's party seized Roger Mortimer."

Narrative purpose: The young king strikes back: Mortimer is seized at Nottingham.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Torch orange, soot black, soft sandstone, dark green, steel grey.

Scene: England, October 1330, Nottingham Castle at night, the doorway of a private chamber at the head of a rough stone stair. Four young knights in mail and surcoats, torches raised, have burst through the heavy door and taken hold of Roger Mortimer: a hard-faced English baron around forty, dark-haired with a short dark beard and heavy brows, in a dark green surcoat over mail, caught half-risen from a bench, his face set in fury and shock.

Continuity: Attach the Short plate b13 (b13_nottingham_seizure_OWNER.png) as the hero reference; Mortimer matches N12.

Composition: Medium-wide. Mortimer centre-right, the knights left and in the doorway, the stair falling away at left; clear air between the near knights and the far wall.

Lighting and animation readiness: Two torches in the knights' hands and torchlight from the stair below, flames whole and sharp; one candle in the chamber. The image is one frozen instant.

Shot-specific constraints: A seizure, not a fight: weapons sheathed, no wounds. The young king is not in the scene.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5) · **I2V TEST CANDIDATE**

- Dramatic intent: The young king strikes back: Mortimer seized at Nottingham.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; non-graphic: no blood, no strike landing; Mortimer and Edward III identities fixed; Nottingham interior consistent
- Permitted action: Armed men step into the chamber and Mortimer is seized by the arms; he turns; torchlight sways.
- Preferred method (suggestion): HIGGSFIELD_I2V
- Fallback: STILL+ENGINE (plate + locked engine preset push/fx) if the I2V test breaks an invariant
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S048 slow push 1.00->1.04.
- Effects: torch_v1c on the two torches; fx_candle on the chamber candle.
- Masks / protection: faces and hands rigid; torch spill kept off faces.

### N16 — Westminster: the charges

Class NEW · batch 5 · expected file `n16_westminster:_the_charges_16x9_OWNER.png` · shots S049, S051, S055, S098d · lines L47, L49, L53, L97a · claims C12, C05e

VO (anchor shot S049, L47): "In November, parliament met, and Mortimer was charged."

VO on this plate, script v3.2 verbatim (every shot):
- S049 (L47): "In November, parliament met, and Mortimer was charged."
- S051 (L49): "The same parliament turned to the Earl of Kent. It said Mortimer's circle had tricked Kent into believing that his brother was alive."
- S055 (L53): "So the new government now had a clear story. The old king had been murdered, and Kent had been the victim of a cruel trick."
- S098d (L97a (part, 16 of 40 words)): "Roger Mortimer himself, at his own death, admitted before the people that Kent had died wrongfully."

Narrative purpose: Parliament at Westminster: the charges are read, and the new government tells its story.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Candle gold, cold window light, blue and gold canopy, dark robes.

Scene: England, November 1330, a crowded stone hall at Westminster during parliament, high windows and candles. On a raised dais under a blue and gold canopy sits the young king Edward the Third: a tall slender youth, beardless, fair-haired, crowned, about eighteen, watching. In the foreground, back half-turned to the viewer, a royal clerk in a dark gown reads aloud from a long parchment roll. On benches on both sides, lords and bishops in robes turn to one another.

Continuity: Attach b14 (b14_mortimer_charged_OWNER.png) for the hall and the young king; his face matches N04, older.

Composition: Wide, from behind the clerk. The young king high centre, clear of the canopy posts for a medium framing; lords at left turning to each other as a separate medium framing.

Lighting and animation readiness: Grey light from the high windows with dust in the shafts; candle stands along the benches, flames whole and sharp. The image is one frozen instant.

Shot-specific constraints: Mortimer is not in the hall. The roll shows no readable writing.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: Parliament meets; Mortimer is charged.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; no legible charges on screen; no quoted text
- Permitted action: Lords listen as charges are read; a hand raises a document.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S049 slow push to the dais; S051 lords crop; S055 king crop.
- Effects: fx_candle; dust_v1.
- Masks / protection: faces rigid.

### DR1 — The November 1330 roll

Class DOC · batch 5 · expected file `dr1_the_november_1330_roll_16x9_OWNER.png` · shots S050, S056, S059a, S085, S086a · lines L48, L54, L57a, L84, L85, L86a · claims C12, C01a, C05e

VO (anchor shot S050, L48): "The charges said Mortimer had Edward sent to Berkeley, and had him murdered there."

VO on this plate, script v3.2 verbatim (every shot):
- S050 (L48): "The charges said Mortimer had Edward sent to Berkeley, and had him murdered there."
- S056 (L54): "But one statement in that same parliament roll has been read in two very different ways."
- S059a (L57a): "The same parliament condemned two of Edward's keepers, Thomas Gurney and William Ockley, for his murder."
- S085 (L84; L85): "Now the strongest reply. Kent could have been deceived. The new government's own record says he was, and the modern editor of the archbishop's letter thinks the archbishop was misled."
- S086a (L86a): "And the same record that holds Berkeley's words also condemns Edward's keepers for his murder."

Narrative purpose: The November 1330 roll as an object: the record that tells the official story.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Pale parchment, brown ink texture, cold daylight, dust.

Scene: A long parliament roll of stitched parchment membranes lies partly unrolled across a dark table, its lower end curling off the edge. Dense lines of brown medieval script run across it, worn soft and faded so no word can be read. Cold daylight falls across it from a high window; dust floats in the light.

Continuity: None. Must not resemble DK1 (a small sealed letter) or DF2 (a bound register).

Composition: Close, three-quarter from above. The roll runs diagonally from upper left to lower right; a lower stretch near the bottom edge is clear for a separate close framing.

Lighting and animation readiness: Cold daylight from upper right; a fine dust shaft across the parchment. The image is one frozen instant.

Shot-specific constraints: Script is texture only, never legible.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: The charges: sent to Berkeley and murdered.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; roll text not legible; no dates rendered
- Permitted action: candle spill; slight page settle; macro push.
- Preferred method (suggestion): ENGINE_PRESET
- Fallback: static plate + house push and dust_v1
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S050 slow push; S056 lower stretch crop, drift down 2%; S085 reuse.
- Effects: dust_v1 in the light shaft.
- Masks / protection: parchment rigid.

### N17 — Lord Berkeley answers

Class NEW · batch 5 · expected file `n17_lord_berkeley_answers_16x9_OWNER.png` · shots S058, S059, S084 · lines L56, L57, L83 · claims C01a, C01b, C31

VO (anchor shot S058, L56): "The parliament roll records Lord Berkeley saying he never consented to the death, and never knew of it until that parliament."

VO on this plate, script v3.2 verbatim (every shot):
- S058 (L56): "The parliament roll records Lord Berkeley saying he never consented to the death, and never knew of it until that parliament."
- S059 (L57): "He also said that at the time he had been ill, away from the castle."
- S084 (L83): "And fourth, Lord Berkeley's words in parliament, which can be read as a denial that the king had died at all."

Narrative purpose: Lord Berkeley answers for the death before parliament.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Candle gold, cold window light, russet, dark robes.

Scene: England, November 1330, the same Westminster hall as N16. Standing before the benches, alone on the open floor, unbound: Thomas, Lord Berkeley: an English baron in his thirties, broad and square-faced, clean-shaven with close-cropped brown hair, in a plain dark russet gown with a black belt and no armour, holding himself stiffly. An original painted face, not a portrait of any real person or actor. He speaks with one hand pressed to his chest, his face guarded. Lords and bishops watch from the benches.

Continuity: Use N16 (once approved) for the hall, light and robes.

Composition: Wide, eye level. Berkeley centre-left on open floor, clear of other figures so a close framing on him reads; benches rising right.

Lighting and animation readiness: Window light and candle stands as in N16, flames whole and sharp; dust in the shafts. The image is one frozen instant.

Shot-specific constraints: He is free and unbound, a lord answering, not a prisoner.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: Berkeley says he never consented and never knew.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; Berkeley identity; no text
- Permitted action: Lord Berkeley speaks before lords; gestures once; lords' heads turn.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S058 slow push; S059 Berkeley close; S084 reuse.
- Effects: fx_candle; dust_v1.
- Masks / protection: face and hands rigid.

### H05 — Papal notary writes

Class HERO · batch 6 · expected file `h05_papal_notary_writes_16x9_OWNER.png` · shots S061, S062, S063, S066, S076 · lines L59, L60, L62, L65, L75 · claims C14, C14b-a; C14b-b BLOCKED (no place shown), C17-a

VO (anchor shot S061, L59): "Years after Kent's death, a very different letter was written."

VO on this plate, script v3.2 verbatim (every shot):
- S061 (L59): "Years after Kent's death, a very different letter was written."
- S062 (L60): "It was written by Manuel Fieschi, an Italian churchman who served the pope as a notary, and it was addressed to the young king, Edward the Third."
- S063 (L62): "His letter has no date, and it does not say where it was written. Historians think it was written roughly a decade after the funeral."
- S066 (L65): "Fieschi tells Edward the Third that he is setting down, in his own hand, what he heard in his father's confession."
- S076 (L75): "Here is the hard part. A letter can be genuinely old, and genuinely written by the man who signed it, and still tell a story that is not true."

Narrative purpose: A papal notary writes a private letter to the young king.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Candle gold, black cloth, old parchment, narrow window grey.

Scene: The 1330s, a churchman's small writing room lit by a narrow window and one candle. a middle-aged cleric, a notary of the pope, in a black clerical gown and close black cap sits at a slanted desk writing a letter on a single sheet of parchment, quill mid-stroke, face intent and private. Beside the sheet: a stick of red sealing wax, a small brass seal, an inkhorn and the candle.

Continuity: Attach the Short plate b15 (b15_papal_notary_writes_OWNER.png) as the hero reference for the cleric, desk and light.

Composition: Medium-wide. Fieschi left of centre; his face, the sheet and the hand with the quill each clear of the others so each can be framed alone.

Lighting and animation readiness: One candle, whole and crisp, and grey light from a narrow window; a thread of smoke from the wick. The image is one frozen instant.

Shot-specific constraints: An ordinary room with no view outside and no marks of a city or palace. The sheet shows no readable writing. No bishop's insignia.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: Years later, a very different document.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; no legible letters; no archive name (C14b); no Hérault/Montpellier as an archive
- Permitted action: The notary dips the pen and writes; hand moves along the line; candle flame moves; he pauses and looks up.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S061 slow push; S062 face crop; S063 sheet crop; S066 hand-and-quill crop; S076 wide pull-back.
- Effects: fx_candle; smoke_v2 wisp.
- Masks / protection: face, hand and quill rigid.
- Special: keep at least one shot away from any DK1/H02/H06 shot (C17-b BLOCKED); never intercut.

### DF2 — The register copy

Class DOC · batch 6 · expected file `df2_the_register_copy_16x9_OWNER.png` · shots S064, S065, S088 · lines L63, L64, L88 · claims C14, C03d

VO (anchor shot S064, L63): "It survives only as a copy, made decades later, in a register of the bishops of Maguelone, near Montpellier, in the south of France."

VO on this plate, script v3.2 verbatim (every shot):
- S064 (L63): "It survives only as a copy, made decades later, in a register of the bishops of Maguelone, near Montpellier, in the south of France."
- S065 (L64): "To be clear, this is not the letter Kent carried to Corfe. It has a different writer and a different reader, and nothing in the record connects the two."
- S088 (L88): "And Fieschi's letter is undated, written years later, and survives only as a copy. Older historians found it remarkable, but could not believe it."

Narrative purpose: Fieschi's letter survives only as a later copy in a register.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Brown leather, pale vellum, faded brown ink texture, cool daylight.

Scene: A thick bound medieval register lies open on a reading slope, its worn brown leather binding and raised bands visible at the spine. Two columns of small, dense, faded script run down the open pages, softened by age into texture. The page edges are cockled and darkened; a ribbon marker hangs from the binding. Cool daylight falls from above.

Continuity: None. Must not resemble DK1, DR1 or DM1.

Composition: Close, three-quarter view. The open pages fill the centre; the worn edge and binding at the right are clear for a separate close framing.

Lighting and animation readiness: Cool, even daylight with fine dust in the air. The image is one frozen instant.

Shot-specific constraints: Script is texture only, never legible.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: It survives only as a later copy in a register.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; no legible text; no archive name; no Hérault/Montpellier
- Permitted action: pen-stroke ink line appears across a blank-looking area (no legible words); page turned once.
- Preferred method (suggestion): ENGINE_PRESET
- Fallback: static plate + house push and dust_v1
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S064 slow push; S065 binding crop, drift; S088 reuse.
- Effects: dust_v1.
- Masks / protection: pages rigid.

### N18 — Escape in servant's clothes

Class NEW · batch 6 · expected file `n18_escape_in_servants_clothes_16x9_OWNER.png` · shots S067 · lines L66 · claims C03a

VO (anchor shot S067, L66): "The letter claims that the former king escaped from Berkeley Castle in a servant's clothes."

VO on this plate, script v3.2 verbatim (every shot):
- S067 (L66): "The letter claims that the former king escaped from Berkeley Castle in a servant's clothes."

Narrative purpose: The letter's claim: the former king escapes Berkeley in a servant's clothes.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Night blue, red sandstone, mist, one distant torch.

Scene: England, night at Berkeley Castle. At a small postern door in the red-sandstone wall, a tall man slips out into the mist, hood drawn over his head, in a servant's rough undyed tunic and hood: Edward of Caernarfon in hiding, a former king now living as a hidden man: a tall, broad-shouldered Englishman of about forty-five, worn and weathered, fair hair going grey and grown to the collar, a full untrimmed fair-grey beard, tired deep-set eyes; a servant’s rough undyed tunic and hood, no crown, no jewels, no royal insignia. An original painted face, not a portrait of any real person or actor. He glances back once.

Continuity: Attach the Short plate p10 (p10_escape_servant_clothes_twilight_OWNER.png) as the reference; his face matches N19 and N20; Berkeley's stone matches N05.

Composition: Medium-wide. The man centre-left, the postern behind him; a distant torch on the wall walk far upper right, separated by open dark stone.

Lighting and animation readiness: Cold night light; one distant torch, whole and sharp; mist rising from the moat. The image is one frozen instant.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: The letter claims an escape in a servant's clothes.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; claimed escape (C03a) – framed as narrative of the letter; face partially obscured; non-graphic
- Permitted action: A figure in servant's clothes slips past a doorway; a lantern swings.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S067 slow push.
- Effects: torch_v1c on the distant torch; smoke_v2 mist.
- Masks / protection: face and hands rigid.

### H04 — Corfe dusk single light

Class HERO · batch 5 · expected file `h04_corfe_dusk_single_light_16x9_OWNER.png` · shots S068, S079, S096 · lines L67, L78, L96a · claims C03a (letter claim), C32

VO (anchor shot S068, L67): "It claims he was hidden at Corfe Castle for a year and a half."

VO on this plate, script v3.2 verbatim (every shot):
- S068 (L67): "It claims he was hidden at Corfe Castle for a year and a half."
- S079 (L78): "On the other side, the historian Ian Mortimer, a modern writer not to be confused with Roger, argues that the death was faked, and that Edward was still alive when Kent made his move."
- S096 (L96a (part, 24 of 34 words)): "At the start of this story, the records could tell us what Kent did, but not why. That is still true at the end."

Narrative purpose: Corfe at dusk, one light still burning: a question kept open.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Dusk violet, chalk grey, dull green, a single warm window.

Scene: England, Dorset, dusk. Corfe Castle on its steep hill between the Purbeck ridges, intact and royal, the tall square keep dark against a fading sky. One window high in the keep is lit. Mist gathers in the valley below.

Continuity: Attach the Short plate p14 (p14_corfe_dusk_single_light_OWNER.png) as the hero reference; architecture matches N10.

Composition: Wide, from the valley. Castle centre-right on its hill; the lit window clearly isolated against dark stone for a medium framing.

Lighting and animation readiness: Last violet dusk light; the window glows warm with a crisp flame shape inside; low mist. The image is one frozen instant.

Shot-specific constraints: No figure in the window.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: Second question: what the evidence can prove; one light left burning.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; Corfe geometry fixed
- Permitted action: A single window light at Corfe flickers at dusk; cloud drifts.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S006 hold then slow push; S068 reuse; S079 keep crop; S095 window crop.
- Effects: fx_candle spill in the window; smoke_v2 low mist.
- Masks / protection: architecture rigid; the window glow stays inside the window.

### N19 — Hidden at Corfe

Class NEW · batch 6 · expected file `n19_hidden_at_corfe_16x9_OWNER.png` · shots S069, S070 · lines L68, L69 · claims C03a, C17-a

VO (anchor shot S069, L68): "Then, it says, he heard that the Earl of Kent had been beheaded for saying that he was alive."

VO on this plate, script v3.2 verbatim (every shot):
- S069 (L68): "Then, it says, he heard that the Earl of Kent had been beheaded for saying that he was alive."
- S070 (L69): "That is the only place where Fieschi's letter touches Kent's story, and it is the letter's own claim."

Narrative purpose: The letter's claim: a hidden man at Corfe hears that Kent has died.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Candle gold, cold stone, charcoal and brown wool.

Scene: England, a small bare stone room high in a castle at night. Edward of Caernarfon in hiding, a former king now living as a hidden man: a tall, broad-shouldered Englishman of about forty-five, worn and weathered, fair hair going grey and grown to the collar, a full untrimmed fair-grey beard, tired deep-set eyes; plain dark brown and charcoal wool clothes and a plain hooded wool cloak, no crown, no jewels, no royal insignia. An original painted face, not a portrait of any real person or actor. He sits on a low bench by a single candle, head bowed into one hand, the other hand limp on his knee. A narrow window shows only night.

Continuity: Attach the Short plate b18 (b18_edward_hidden_at_corfe_OWNER.png) as the reference; same face as N18 and N20.

Composition: Medium-wide. He sits centre-left, his bowed head clear of the candle so a close framing on it reads; bare stone around him.

Lighting and animation readiness: One candle, whole and crisp, the only warm light. The image is one frozen instant.

Shot-specific constraints: He is alone; no one brings the news into the room.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: He hears that Kent has been beheaded.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; identity ambiguous (claim); no confirmation of identity
- Permitted action: A cloaked man waits in a dim corner at Corfe; breath, small movement.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S069 slow push; S070 bowed head close.
- Effects: fx_candle.
- Masks / protection: face and hands rigid.

### N20 — The hermit road

Class NEW · batch 6 · expected file `n20_the_hermit_road_16x9_OWNER.png` · shots S074 · lines L73 · claims C03a, C03c · **RESERVE in v2.1: not placed in the v3.2 shot list** (L73 now carries map beat ME4 on AE; N20 may be used as a cutaway if the recorded VO leaves room)

VO (anchor shot S074, L73): "And it leaves him living as a hermit in Lombardy, in remote hermitages near Milan and in the diocese of Pavia."

Narrative purpose: The letter's claim leaves him a hermit in the hills of Lombardy.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Soft morning gold, blue-grey hills, valley mist, undyed wool.

Scene: Northern Italy, the hills of Lombardy in early morning. On a stony footpath high above misty valleys walks a lone hermit with a staff, in a rough undyed wool robe and hood: Edward of Caernarfon in hiding, a former king now living as a hidden man: a tall, broad-shouldered Englishman of about forty-five, worn and weathered, fair hair going grey and grown to the collar, a full untrimmed fair-grey beard, tired deep-set eyes; a rough undyed hermit’s robe and hood, no crown, no jewels, no royal insignia. An original painted face, not a portrait of any real person or actor. Layers of blue hills fall away behind him.

Continuity: Same face as N18 and N19.

Composition: Wide. The hermit small in the left third on the path; layered hills and open valley at right, with clear space between near ridge and far hills for parallax.

Lighting and animation readiness: Low morning sun from the right; mist lying in the valleys. The image is one frozen instant.

Shot-specific constraints: No buildings that could be read as a known hermitage, church or tomb.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: It leaves him a hermit in Lombardy.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; hermit face unseen; no landmark naming Milasci/Cecinie
- Permitted action: A hermit walks a road away from camera; dust and wind.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S074 slow drift 3% right.
- Effects: smoke_v2 valley mist; dust_v1 in the sunlight.
- Masks / protection: figure rigid.

### DM1 — The archbishop's letter

Class DOC · batch 7 · expected file `dm1_the_archbishops_letter_16x9_OWNER.png` · shots S083 · lines L82 · claims C02a, C02b

VO (anchor shot S083, L82): "Third, a letter from the archbishop of York, which still survives, reported news that the former king was alive. Its modern editor dates it to about two months before Kent's death."

VO on this plate, script v3.2 verbatim (every shot):
- S083 (L82): "Third, a letter from the archbishop of York, which still survives, reported news that the former king was alive. Its modern editor dates it to about two months before Kent's death."

Narrative purpose: The archbishop's surviving letter: news that the former king was alive.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Cool grey daylight, pale parchment, a dark green seal fragment, oak.

Scene: A small single sheet of parchment lies opened flat on a slanted oak lectern, its folds still showing and a broken fragment of dark green wax clinging to one edge. A few lines of faded brown script cross the sheet, worn into texture. Cool grey daylight falls on it from a window at left.

Continuity: None. Must not resemble DK1 (Kent's closed red-sealed letter), DR1 or DF2.

Composition: Close, slightly above. The sheet centre, the broken seal lower right, dark wood around.

Lighting and animation readiness: Cool, even daylight with fine dust in the air. The image is one frozen instant.

Shot-specific constraints: Script is texture only, never legible.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: Third: the archbishop's surviving letter.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; no legible text
- Permitted action: candle spill, page settle, macro push.
- Preferred method (suggestion): ENGINE_PRESET
- Fallback: static plate + house push and dust_v1
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S083 slow push.
- Effects: dust_v1.
- Masks / protection: sheet rigid.

### E01 — Corfe lane at first light

Class OUTRO · batch 7 · expected file `e01_corfe_lane_at_first_light_16x9_OWNER.png` · shots S099 · lines L98 · claims none (outro)

VO (anchor shot S099, L98): "History remembers the victors. We remember the rest."

VO on this plate, script v3.2 verbatim (every shot):
- S099 (L98): "History remembers the victors. We remember the rest."

Narrative purpose: A quiet, unique close: the lane to Corfe at first light, empty.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Pale gold dawn, mist white, chalk grey, soft green.

Scene: England, Dorset, first light. An empty, muddy lane climbs toward the closed gatehouse of Corfe Castle, the tall keep rising above on its hill. Mist is lifting off the slope; the sky behind is pale gold. No one is on the lane.

Continuity: Corfe's architecture matches N10, H02 and H04.

Composition: Wide, from low on the lane. The gatehouse and keep in the upper centre; a broad, calm band of pale sky and mist across the middle of the frame, open and uncluttered.

Lighting and animation readiness: Soft dawn light from behind the castle; mist painted in distinct soft banks on the slope and across the middle band so it can be lifted and drifted; the castle silhouette crisp against the pale sky. The image is one frozen instant.

Shot-specific constraints: No lettering, wordmark or text anywhere (the wordmark is written in later); the middle band of sky and mist stays calm and uncluttered.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: House outro: wordmark and narrated tagline over this episode's own background.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; protected tagline/wordmark area per house outro; no captions
- Permitted action: Mist lifts along the Corfe lane at first light; house outro push per Bathory v3c.
- Preferred method (suggestion): STILL+ENGINE (LONGFORM-HOUSE-OUTRO)
- Fallback: static house outro: plate push + dust_v1 + wordmark ink-in (Bathory v3c builder pattern) + narrated tagline
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: LONGFORM-HOUSE-OUTRO (LONGFORM-HOUSE-INTRO-BRIEF.md Part 2), ~9.5 s: house push 1.00->1.03; mist lifts and dissolves into ink-wash wisps at its edges; ink feathers in from the frame edges; POSTERITY wordmark + rule/diamond pen-stroke write into the middle band (bookend of the intro).
- Effects: mist alpha layer advected upward with ink-edge feathering; dawn light slowly grows; dust_v1 optional.
- Masks / protection: castle silhouette and wordmark field never touched by ink; wordmark from the locked master only.
- Special: tagline L98 "History remembers the victors. We remember the rest." narrated after the house 0.8 s break, not on screen unless the owner picks it; A3 to a final fade with the picture; background unique to this episode.

### AB — Atlas: southern Britain

Class ATLAS · batch 7 · expected file `atlas_britain_16x9_OWNER.png` · shots S013, S014, S019, S021, S053, S091 · lines L13, L14, L18, L20, L51, L92 · claims C25, C26, C27, C28, C12, C20

VO (anchor shot S013, L13): "Edward fled west to Chepstow, on the border with Wales, and sailed from there. Soon afterwards he was captured in South Wales."

VO on this plate, script v3.2 verbatim (every shot):
- S013 (L13): "Edward fled west to Chepstow, on the border with Wales, and sailed from there. Soon afterwards he was captured in South Wales."
- S014 (L14 (part, 11 of 17 words)): "He was taken to Kenilworth Castle, in the middle of England,"
- S019 (L18): "In the spring, the deposed king was moved again, to Berkeley Castle, in Gloucestershire."
- S021 (L20): "The news reached the young king at Lincoln a couple of days later."
- S053 (L51): "Mortimer was hanged at Tyburn, outside London, at the end of November."
- S091 (L92): "But belief is not proof. None of it shows that Edward survived, and most historians still hold that he died at Berkeley."

Narrative purpose: The single owner-painted base for every Britain map beat (MB1–MB6).

IMAGE GENERATION (verbatim from sources/atlas-refpack-v2/PLATE-PROMPTS-v2.md §britain_16x9; generate exactly 3840x2160 with `britain_16x9_ref_tinted_notext.png` attached, add `britain_16x9_ref_bare.png` if shapes drift)

```
Horizontal 16:9 antique chart of southern Britain and the Irish Sea, exactly 3840x2160. Attached reference = layout guide; match its coasts, rivers and realm shapes. Explorer's-chart engraving: inked waterways, forest stipple, coastal detail, painted relief, tiny settlement vignettes, parchment aged by texture, not fading; blue-green sea. Strong realm pigments, decisive inked borders: England and Wales crimson, English Ireland pale crimson, Gaelic Ireland bare parchment, France royal blue, Flanders grey-teal. Calm margins. One small compass rose only at the top edge, in the Irish Sea west of Anglesey; lower-left Celtic Sea empty. Calm ground around Berkeley, Gloucester, Corfe, Kenilworth, London, Sandwich. Clean plate: no text, labels, routes, dotted lines, icons, banners, title, cartouche, frame border, vignette or watermark; the engine adds place names.
```

Note: the 'Clean plate' sentence is kept because the engine adds every name, route and marker and registers the plate to control points; it is a functional registration requirement, not a style avoid list. Map class (Explorer's Chart) is an owner decision; see MAP-PACK.md.

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: Edward flees west and is captured in South Wales.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; geodata is truth; no I2V
- Permitted action: deterministic engine only: route ink, pins, labels, camera.
- Preferred method (suggestion): ENGINE_ATLAS
- Fallback: refpack tinted render for the beat (MAP-PACK §2.6); manual 4-point registration if homography fails QA
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Engine: ENGINE_ATLAS; registration ORB+RANSAC -> NCC>=0.6 -> TPS (smoothing 5), warp limit 27 px; QA per MAP-PACK.md before any beat is cut.
- Beats: see MAP-PACK.md (routes oxblood with parchment keyline; documented = continuous ink, claimed = dotted; labels ink in; no title card).

### AE — Atlas: western Europe

Class ATLAS · batch 2 · expected file `atlas_euro_16x9_OWNER.png` · shots S030, S071, S072, S074, S075 · lines L29, L70, L71, L73, L74 · claims C09, C03a

VO (anchor shot S030, L29 (part, ~50% of line)): "According to an English chronicle called the Brut, Kent went to see the pope at Avignon, where the pope held his court, and spoke of a common report in England that Edward was alive."

Narrative purpose: The single owner-painted base for every Europe map beat (ME1–ME5).

IMAGE GENERATION (verbatim from sources/atlas-refpack-v2/PLATE-PROMPTS-v2.md §euro_16x9; generate exactly 3840x2160 with `euro_16x9_ref_tinted_notext.png` attached, add `euro_16x9_ref_bare.png` if shapes drift)

```
Horizontal 16:9 antique chart of western Europe, exactly 3840x2160. Attached reference = layout guide; match its coasts, rivers, Alps, Pyrenees and realm shapes. Explorer's-chart engraving: inked waterways, forest stipple, coastal detail, painted relief, tiny settlement vignettes, parchment aged by texture, not fading; blue-green sea. Strong realm pigments, decisive inked borders: England and Gascony crimson, France royal blue, Brittany and Burgundy slate blue, Flanders grey-teal, Empire antique gold, Scotland heather violet, Castile terracotta, Aragon saffron, Portugal sage; Italy, Gaelic Ireland bare parchment. Calm margins. One small compass rose only middle-left, open Atlantic west of Brittany; upper-left corner empty. Calm ground around Paris, Avignon, Cologne, Milan, Sluis. Clean plate: no text, labels, routes, dotted lines, icons, banners, title, cartouche, frame border, vignette or watermark; the engine adds place names.
```

Note: the 'Clean plate' sentence is kept because the engine adds every name, route and marker and registers the plate to control points; it is a functional registration requirement, not a style avoid list. Map class (Explorer's Chart) is an owner decision; see MAP-PACK.md.

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: Kent goes to the pope at Avignon (as the Brut tells it).
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; geodata is truth; no I2V; Kent never on Europe route; Vercelli not mapped
- Permitted action: deterministic engine only: route ink, pins, labels, camera.
- Preferred method (suggestion): ENGINE_ATLAS
- Fallback: refpack tinted render for the beat (MAP-PACK §2.6); manual 4-point registration if homography fails QA
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Engine: ENGINE_ATLAS; registration ORB+RANSAC -> NCC>=0.6 -> TPS (smoothing 5), warp limit 27 px; QA per MAP-PACK.md before any beat is cut.
- Beats: see MAP-PACK.md (routes oxblood with parchment keyline; documented = continuous ink, claimed = dotted; labels ink in; no title card).

### N21 — Kent in Gascony

Class NEW · batch 3 · expected file `n21_kent_in_gascony_16x9_OWNER.png` · shots S008a · lines L08 · claims NR-2 · NEW in v2.1 (script v3.2 L08)

VO (anchor shot S008a, L08 part): "even in Gascony, the English crown's lands in the south-west of France."

Narrative purpose: Kent at work for his brother as one of the realm's great lords, far from England, in the crown's lands in south-west France.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Hot southern afternoon light, ochre stone, vine green, oxblood and midnight blue.

Scene: Gascony, the 1320s, the English crown's lands in the south-west of France. On a terrace of pale ochre stone above a broad river valley of vineyards and red-tiled roofs stands Edmund, Earl of Kent, the same man in every image: an English royal nobleman in his late twenties, lean and upright, medium height, pale skin, short dark auburn hair cut level just below the ears with a soft centre parting, a short neatly trimmed dark auburn beard and moustache, a straight narrow nose, steady grey-blue eyes under straight dark brows. Early fourteenth-century English noble dress: a knee-length oxblood-red wool cote with a round neck and close-fitting sleeves buttoned from elbow to wrist with small gilt buttons, a narrow dark leather belt, dark hose, plain black leather shoes, and over it a long deep midnight-blue wool mantle lined with grey-and-white squirrel fur, fastened at the right shoulder by a round gold ring brooch; a heavy gold signet ring on the forefinger of his right hand. Bareheaded, no crown, no coronet, no armour. An original painted face, not a portrait of any real person or actor. He studies an unrolled sheet held by a kneeling clerk while two of his household men wait a pace behind with their horses. He is a lord in command, composed and watchful.

Continuity: Attach the Short plate b04 (b04_the_brothers_OWNER.png) for Kent's face and costume. The town and valley are an original painted place, not a portrait of a named town.

Composition: Wide, slightly low. Kent right of centre against the open sky, his head clear of the clerk and the horses so a medium framing on him alone reads; the river valley falls away to the left for a slow drift.

Lighting and animation readiness: Low western sun from frame left, long shadows on the stone; a light warm haze over the valley; a pennon on a lance stirs. The image is one frozen instant.

Shot-specific constraints: The sheet carries only unreadable ink lines. Arms on pennons stay plain red and gold, no readable heraldry.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: Kent the loyal great lord, trusted with the king's far-off lands.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; Kent bareheaded, no armour; no named town on screen
- Permitted action: Kent lifts his eyes from the sheet to the valley; the pennon and the haze move; a horse shifts its weight.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: ENGINE_PRESET on the still; HIGGSFIELD_I2V allowed at Atelier Jr discretion
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S008a slow drift right to left across the valley, ending on Kent at medium.
- Effects: dust_v1 in the low sun; light haze.
- Masks / protection: Kent's face and hands rigid.

### N22 — The quarrel reaches the king's family (OPTIONAL)

Class NEW · batch 3 · OPTIONAL · expected file `n22_the_quarrel_16x9_OWNER.png` · shots S009 · lines L09 · claims NR-3 · NEW in v2.1 (script v3.2 L09). Fallback if not made: N01 DERIVED_CROP (the king alone, cooled grade), as in v2.

VO (anchor shot S009, L09): "But the reign Kent served was turning bitter. Edward's favourites had turned England's barons against him, and soon the quarrel reached into the king's own family."

Narrative purpose: The reign sours: the king's favourites against his barons, and the quarrel coming home to the royal family.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Grey storm light, royal blue and gold, cold stone, oxblood.

Scene: England, the 1320s, the same royal chamber as N01 under a darker sky. King Edward the Second: a tall, broad-shouldered man of about forty with fair hair to the jaw and a short fair beard, in a royal blue and gold robe and a simple gold crown, calm and regal, sits on the carved oak throne while two richly dressed courtiers lean close at his side, one speaking low at his ear. Across the floor stand a group of barons in mail coifs and travelling cloaks, faces hard, one with his hand on his sword belt. At the far edge of the room, half in shadow by a doorway, a young queen in a deep blue gown and white veil watches the scene, still and unreadable.

Continuity: Use N01 (once approved) for the room, the throne and the king's face and costume. The courtiers, barons and queen are original painted faces.

Composition: Wide, eye level. The king and his courtiers left of centre, the barons right, an open gap of floor between them; the queen small at the far right edge, clear enough for a close framing on her to read.

Lighting and animation readiness: Grey light from the tall window; the cressets on the wall burn low with whole flames; rain streaks on the window glass. The image is one frozen instant.

Shot-specific constraints: The barons' swords stay sheathed at their belts; the only heraldry is the gold lions on the red cloth of estate.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: The kingdom divides, and the division reaches the king's own house.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; favourites and barons unnamed; king consistent with N01
- Permitted action: the courtier keeps whispering; a baron's jaw sets; the queen turns her head toward the throne; the cresset flames move.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: N01 DERIVED_CROP with the v2 cooled grade
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S009 slow push across the gap of floor, ending on the queen in the doorway at "the king's own family".
- Effects: fx_candle on the cressets; rain on the glass.
- Masks / protection: faces and hands rigid.

### N23 — The jury of knights (OPTIONAL)

Class NEW · batch 5 · OPTIONAL · expected file `n23_the_jury_of_knights_16x9_OWNER.png` · shots S059b · lines L57b · claims C31 · NEW in v2.1 (script v3.2 L57b). Fallback if not made: DR1 DERIVED_CROP, names unreadable.

VO (anchor shot S059b, L57b): "Early the next year, a jury of knights cleared Lord Berkeley of the king's death. Yet the same record says the king was murdered by keepers Berkeley had appointed."

Narrative purpose: The acquittal: Lord Berkeley cleared by a jury of knights, in a record that still calls the death a murder.

IMAGE GENERATION

```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure, early fourteenth-century English visual language. Pale winter window light, candle gold, russet, dark wool.

Scene: England, early 1331, the same Westminster hall as N16 and N17 in winter. A row of twelve knights in plain dark wool gowns and belts, bareheaded, no armour, stands together before the benches; their foreman, a grey-bearded knight, speaks with one hand raised in assent. A few paces apart, alone and unbound, stands Thomas, Lord Berkeley: an English baron in his thirties, broad and square-faced, clean-shaven with close-cropped brown hair, in a plain dark russet gown with a black belt and no armour, holding himself stiffly. An original painted face, not a portrait of any real person or actor. His shoulders have just loosened. At a desk to one side a clerk writes on a long parchment roll.

Continuity: Use N16 and N17 (once approved) for the hall, the light and Berkeley's face and gown.

Composition: Wide, eye level. The knights in a line across the centre, Berkeley left with clear space around his head for a close framing, the clerk and his roll at the right edge so a crop on the writing hand reads.

Lighting and animation readiness: Cold low window light with breath faintly visible; candle stands with whole, sharp flames; dust in the shafts. The image is one frozen instant.

Shot-specific constraints: The roll shows only unreadable ink lines. Berkeley stays free and unbound.
```

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: Berkeley is cleared, but the same record keeps the word murder.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; Berkeley identity consistent with N17; no method of death shown or implied (C33)
- Permitted action: the foreman lowers his hand; Berkeley lets out a breath; the clerk's pen moves along the roll.
- Preferred method (suggestion): STILL+ENGINE
- Fallback: DR1 DERIVED_CROP (names unreadable)
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S059b slow push from the knights to Berkeley, then a cut-in on the clerk's pen at "the same record says".
- Effects: fx_candle; dust_v1.
- Masks / protection: faces and hands rigid.

### T01 — Gloucester tomb (desk)

Class DESK · batch 0 · expected file `t01_gloucester_tomb_desk_16x9.png` · shots S078 · lines L77 · claims C16a (framing only)

VO (anchor shot S078, L77): "The medieval historian David Carpenter argues that Edward almost certainly died there."

VO on this plate, script v3.2 verbatim (every shot):
- S078 (L77): "The medieval historian David Carpenter argues that Edward almost certainly died there."

Narrative purpose: The tomb at Gloucester as present-day evidence: the place where, Carpenter argues, Edward lies; and, in the close, the open alternative.

DESK COMPOSITION SPEC (not an image-model prompt)

- Source photos: Wikimedia Commons 'Tomb of Edward II, Gloucester Cathedral 01.jpg' to '04.jpg', CC0, Poliphilo (own work, 23 Jan 2020), per standalones/edward-ii/rights-risks.md §1. Not downloaded; URLs and pixel sizes UNKNOWN in our files — Atelier Jr fetches them and records the licence page in the rights record. Credit optional (CC0); a courtesy credit is fine.
- Layout: 1920x1080 house desk scene — one photo (prefer the effigy view) as a print on dark oak beside folded parchment, candle off-frame left; no captions, labels, arrows or status text.
- Resolution: the photo print must respect <=1.5 output px per source px at the final push (law §6); if the chosen photo is too small, use it smaller in frame.
- Overlay: none. C04: the effigy is 'probably' Edward's; nothing on screen asserts whose body lies there.
- Rendered name: t01_gloucester_tomb_desk_16x9.png.

SHOT INTENT (v2, governs; PILOT-OVERRIDE-v1 §5)

- Dramatic intent: Carpenter: almost certainly died there.
- Required invariants: identity, face, costume and props per refs; location geometry fixed; non-graphic; OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) never as fact; no devil visual; no on-screen text except engine place-name labels; photo licence recorded; no generated tomb face
- Permitted action: engine push over desk composition; candle spill.
- Preferred method (suggestion): ENGINE_PRESET
- Fallback: static plate + house push and dust_v1
- I2V prompt: written by Atelier Jr from the three lines above (not supplied here).

MOTION HANDOFF (v1 suggestion; intent above governs)

- Motion: S078 slow push 1.00->1.04 onto the effigy; S096 slow drift (hold the tomb as one of the two answers in L96).
- Effects: fx_candle spill from off-frame left only; dust_v1.
- Special: the photo is real; keep the house grade light so it is not mistaken for a painting.
