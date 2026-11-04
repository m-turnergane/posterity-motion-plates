# PLATE PROMPTS v3: Ugarit: The King's Warning (MA2)
Source of truth: LOCK-v3.md (script, timing, shot map). Guardrails: VERIFY.md + LOCK-v3.md. Style template: backups/INFO-PACKET.pre-v3.md §3 (v1 content dropped).
Times are LOCK-v3 estimates at 2.3 w/s; Atelier re-times to the real Oliver render.
Play order: 01 → 02 → 03 → 04 → 04b (crop) → 03b (crop) → 05 → 06 → 08 → 07 → 09 → Outro.
**Generate 02 first.** 07 is made from 02 as an image reference / edit.
**No generation needed for 04b or 03b.** Both are crops: 04b is cut from 04 (wet clay), 03b from 03 (the sea between Ugarit and Cyprus).

## Global rules (every plate)
- Vertical 9:16, full-bleed. Painterly Recovered Chronicle: aged gouache/tempera, mineral pigments, visible brushwork, paper grain.
- Clear FG/MG/BG separation. About 8% edge margin, with room for a 105-110% crop and move. No white bars or composite seams.
- Keep the lower ~25% calm for captions (except the outro, which has no captions).
- No readable text anywhere: no letters, numbers, signs or labels. Cuneiform appears only as tiny illegible wedge texture. Map labels are added in the edit.
- No gore: no bodies, wounds, fighting, captives or bones. No modern objects.
- Late Bronze Age Ugarit: dressed limestone ashlar and rubble walls with timber courses, flat roofs, upper storeys, narrow lanes, olive and fig trees, a coastal plain, the sea to the west. The capital sits INLAND. Its harbour, Minet el-Beida, is separate, about 1.5 km away on the coast. Never paint a palace over the docks.
- Dress: long dyed wool robes, wrapped fringed mantles, simple headbands, linen tunics and kilts for workers. No invented crowns or regalia.
- Ships: Late Bronze Age Levantine merchant ships (rounded hull, single square sail on a yard, high stem and stern posts, steering oars). Enemy ships are only dark, unidentified silhouettes: no bird-head prows, no figureheads, no Sea Peoples markers.
- King continuity, 01 = 04: the same original figure, never a portrait claim. Deep blue wool robe with a red hem band, simple cloth headband, short dark beard, greying temples. Seen from behind or in half-shadow, no sharp facial detail.
- Retired, never paint: a kiln or oven, a "legend vs record" look, a "last letter" or unsent-letter scene.

---

## 01 · Crisis (house intro plate)
**VO under it:** "A king's towns were burning, and his army was far away."
**Time:** 0.0-4.8s
**Suggested file:** `p01_crisis_terrace_OWNER.png`
**Motion:** the Chronicle Reveal house intro runs on this plate, then one slow push toward the ships.
**Prompt:**
> Vertical 9:16 painterly Recovered Chronicle illustration, aged gouache and mineral-pigment texture with visible brushwork and paper grain. Dusk, seen from the flat roof terrace of a Late Bronze Age limestone palace in an inland city, looking west across a wide coastal plain of olive groves and fields toward the Mediterranean. In the lower-right foreground a robed king stands seen from behind at three-quarter view, one hand on the low stone parapet: deep blue wool robe with a red woven hem band, a simple cloth headband, short dark beard and greying temples just visible in silhouette, no crown. Far off along the coastline, thin grey columns of smoke rise from two or three small coastal towns, with a faint ember glow at their bases. On the sea near the horizon, a few small dark unidentified ships with square sails appear as silhouettes only, set in the lower-left third. The top half and the centre of the frame stay clean and calm: open dusk sky in deep amber fading to bruised violet, and a smooth sea band, with no figures, smoke columns or ships there, leaving room for a title animation. Strong depth: parapet and king in the foreground, the plain in the midground, the coast, smoke and ships in the background. Quiet, ominous, not a pretty sunset. No readable text, no crown or gold regalia, no sharp face, no fighting or bodies, no fire on the palace, no harbour or docks below the palace, no bird-head prows, no Greek or Roman columns, no modern objects.

## 02 · Ugarit alive (LOCKED REFERENCE for 07)
**VO under it:** "He ruled Ugarit, a rich Syrian port, over three thousand years ago."
**Time:** 4.8-10.0s
**Suggested file:** `p02_ugarit_harbour_REFERENCE_OWNER.png`
**Motion:** hard cut from 01. Static frame with light life (birds, sail drift), no zoom. **The 07 match cut depends on this exact composition, so approve 02 before making 07.**
**Prompt:**
> Vertical 9:16 painterly Recovered Chronicle illustration, aged gouache texture, visible brushwork and paper grain. Bright late-morning view from a high vantage on the western edge of the inland city of Ugarit, looking west toward its separate harbour at Minet el-Beida, about 1.5 km away on the coast. Foreground (bottom third): flat limestone-and-timber rooftops and the top of a narrow lane in the city, with a few small figures in long dyed wool robes and linen tunics, tall two-handled storage jars stacked by a doorway. Midground: a single dirt road runs from the city gate across a green-and-ochre coastal plain of olive and fig trees, with donkeys and porters carrying jars and flat four-handled copper oxhide ingots toward the sea. Background: a small harbour town of low warehouses around a curved white-sand bay, where two or three rounded-hull Late Bronze Age merchant ships with square sails, high stem and stern posts and steering oars are moored or arriving, and more jars and stacks of copper oxhide ingots lie on the quay. Calm blue sea and a clear sky across the top quarter. The city and the harbour are clearly separate places joined by the road, with no palace above the docks. Warm ochre, sea-blue and limestone-cream palette, busy, prosperous and orderly. Faces small and soft. Simple, strong, stable composition with a clear horizon line and clear bay shape, so the same view can be repainted later. No readable text, no coins, no gold piles, no Greek or Roman ships with rams, no bird-head prows, no camels in front, no modern harbour features.

## 03 · Map (base only; labels added in the edit)
**VO under it:** "Ugarit answered to the Hittite empire, and his soldiers were in Hittite lands. His fleet was away too."
**Time:** 10.0-17.8s
**Suggested file:** `p03_map_ugarit_hatti_cyprus_OWNER.png`
**Motion:** map reveal. Opens tight on Ugarit, pulls out north as "Hittite empire" lands, and the label pops on "Hittite lands". 03b later reuses the sea between Ugarit and Cyprus.
**Prompt:**
> Vertical 9:16 painterly Recovered Chronicle antique map on aged parchment, gouache washes, visible brushwork and paper grain. The north-east corner of the Mediterranean, drawn with geographically correct coastlines. On the right, the Syrian coast runs straight north-south. At the top right it turns sharply west into the deep right-angled corner of the Gulf of Iskenderun, then the southern coast of Anatolia runs west across the upper middle of the frame. The broad Anatolian plateau, with soft Taurus and Amanus mountain shading, fills the top third, reaching central Anatolia (the Hittite heartland) near the top edge. The island of Cyprus, correctly shaped with its long narrow Karpas panhandle pointing north-east toward the Syrian coast, sits west-southwest of Ugarit across about 100 km of open sea. One small warm amber dot marks Ugarit on the Syrian coast, opposite the tip of the Karpas peninsula. One small muted dark pin sits far inland in north-central Anatolia, north and slightly west of Ugarit (Hattusa). The sea is a cool grey-blue wash with clear open water between Ugarit and Cyprus. Land is warm ochre and umber. The parchment extends above and below the map so it is not squashed. No lettering or pseudo-lettering of any kind, no labels, no arrows, no troop or route lines, no borders or empire shapes, no compass rose, no ships or soldiers, no invented islands, no Crete or Greece in frame.

## 04 · Palace writing
**VO under it:** "He wrote across the sea to the king of Cyprus:"
**Time:** 17.8-22.2s
**Suggested file:** `p04_palace_dictation_OWNER.png`
**Motion:** whip-free hard cut. Tilt down from the king to the clay. 04b (22.2-25.2s, on the quote) is cropped from this plate, so the tablet must hold up at extreme close-up.
**Prompt:**
> Vertical 9:16 painterly Recovered Chronicle illustration, aged gouache texture, warm oil-lamp light. A small stone room inside a Late Bronze Age palace in the inland city, at night. Upper half: the same king as before, standing half in shadow, deep blue wool robe with a red woven hem band, simple cloth headband, short dark beard and greying temples, one hand raised mid-dictation, face turned toward a narrow window where faint grey smoke drifts across a dim orange-tinged night sky. Lower-middle of the frame: a seated scribe in a plain linen robe bends forward and presses a reed stylus into a pillow-shaped tablet of wet grey-brown clay held in his palm. The tablet and hands are large, sharply painted and well lit by a single clay oil lamp on a low wooden table, which also holds a water bowl and a lump of spare clay. The fresh wedge marks are tiny, crisp and completely illegible, with the clay's wet sheen visible. Leave clear space around the tablet so it can be cropped to an extreme close-up. Clear vertical line from the king's head down to the clay. Close, quiet, urgent mood. No readable cuneiform or letters, no paper, scrolls, quills or ink, no crown, no sharp facial detail, no weapons, no fire inside the room, no kiln or oven.

**04b · Tablet insert (crop of 04, no generation)**
VO: "The ships of the enemy have come." (22.2-25.2s). Extreme close-up of the wet clay and fresh wedges, static. The on-screen quote is Cline's text, added in the edit.

**03b · Sea crop (crop of 03, no generation)**
VO: "He asked for word of any more ships." (25.2-28.7s). The strait between Ugarit and Cyprus, with a slow lateral drift west toward Cyprus.

## 05 · Coastal raids (plays only under the raider clause)
**VO under it:** "We don't know who the raiders were,"
**Time:** 28.7-31.7s
**Suggested file:** `p05_coastal_town_raid_dusk_OWNER.png`
**Motion:** hard cut. Slow pan along the shore. **Plays only under the raider clause.**
**Prompt:**
> Vertical 9:16 painterly Recovered Chronicle illustration, aged gouache texture. Dusk over a small coastal town on the Syrian shore (a minor village, not the city of Ugarit): a cluster of low flat-roofed mud-brick and stone houses among olive trees above a narrow beach. Thin columns of grey smoke rise from just a few of the roofs, with a faint ember glow, while most of the town is still intact. Several dark unidentified ships with square sails are drawn up on the sand or lie just offshore, painted as plain silhouettes. Far down on the beach, a handful of tiny distant figures appear as anonymous dark shapes with no visible detail, faces, weapons, helmets or headdresses, and nobody is being attacked. The shoreline runs horizontally across the frame, with enough width for a slow sideways pan. Palette: blue-violet dusk, smoke grey, small ember accents, dark sea. Subdued and uneasy, not a fire panorama. No feathered or horned headdresses, no bird-head prows or figureheads, no ethnic or Sea Peoples markers, no fighting, bodies or blood, no large city or palace, no readable text, no modern objects.

## 06 · Burnt city
**VO under it:** "or whether they destroyed Ugarit. In the end, the city burned."
**Time:** 31.7-36.5s
**Suggested file:** `p06_burnt_city_doorway_OWNER.png`
**Motion:** dissolve from 05 (time passing, a separate event). Slow push through a doorway.
**Prompt:**
> Vertical 9:16 painterly Recovered Chronicle illustration, aged gouache texture. Inside the burnt Late Bronze Age city of Ugarit, after the fire is out. The foreground is framed by a dark, scorched stone doorway with charred timber jambs, giving a strong frame to push through. Beyond it, a roofless room and lane: collapsed limestone and rubble walls, blackened and cracked plaster, deep drifts of grey ash, a fallen charred roof beam lying diagonally across the floor, broken storage jars, and a thin haze of settling smoke in cold grey light. No people anywhere and no active flames. Muted ash-grey, soot black and pale limestone, with one cool accent of sky through the open roof. Quiet, heavy, final. No fire panorama, no bodies or bones, no weapons, no gold or treasure, no clay tablets, no readable text, no modern objects.

## 07 · Abandoned match (made FROM 02)
**VO under it:** "His kingdom did not. For centuries, no city rose there again."
**Time:** 40.0-44.3s
**Suggested file:** `p07_abandoned_match02_OWNER.png`
**Motion:** match cut from 02's composition (02 flashes for 0.3s inside the cut, then snaps to 07, or a straight match dissolve). Static, to mirror 02.
**How to make it:** **Do not generate from scratch.** Load the approved `p02_ugarit_harbour_REFERENCE_OWNER.png` as the image reference / edit source (image-to-image, low-to-medium change strength, or an inpaint over the whole frame) so the camera position, horizon, road line, bay shape and building positions stay exactly where they are in 02. Then use this prompt:
> Same exact view, camera position, framing, horizon line and composition as the reference image; change only the time and condition. Vertical 9:16 painterly Recovered Chronicle illustration, aged gouache texture. Centuries later, the same city and harbour are abandoned. The foreground rooftops are now fallen: broken roofless limestone walls standing at the same positions, with collapsed timbers and rubble in the lane, and grass, weeds and wild shrubs growing over the ruins. The midground road is overgrown and fading into the plain, with olive trees gone wild. In the background the bay is the same shape but the harbour is empty: no ships, no cargo, and the warehouses are low grassy ruins. Same calm sea and sky as the reference, in a slightly paler, quieter palette. No people, animals with loads, ships, jars, copper ingots, treasure or clay tablets. No smoke or fire, no readable text, no modern objects.

## 08 · Tablet in ruins
**VO under it:** "His warning survived, on clay, in the ruins."
**Time:** 36.5-40.0s
**Suggested file:** `p08_tablet_in_rubble_OWNER.png`
**Motion:** insert cut. Static with a slight light shift.
**Prompt:**
> Vertical 9:16 painterly Recovered Chronicle illustration, aged gouache texture, close-up. A single small pillow-shaped clay tablet, fired reddish-brown and slightly chipped at one corner, lies half buried in rubble, broken mud-brick and fine grey ash. Its upper face is covered with tiny, completely illegible wedge-shaped impressions. Soft, low, warm-grey light falls across it from one side and catches the edges of the wedges. Shallow depth of field: the rubble in front and behind is soft, and the tablet in the centre-middle is sharp. Calm, still and intimate, with space above the tablet. Only one tablet: no other tablets, no valuables or jewellery, no jars, no wide view, no kiln or oven, no hands or people, no readable cuneiform or letters, no modern objects.

## 09 · Buried valuables (bronze)
**VO under it:** "The valuables its people buried were left in the ground."
**Time:** 44.3-49.1s
**Suggested file:** `p09_bronze_hoard_jar_OWNER.png`
**Motion:** insert cut. Slow tilt down into the earth, so the frame needs vertical extent.
**Prompt:**
> Vertical 9:16 painterly Recovered Chronicle illustration, aged gouache texture, close-up composed for a slow tilt down. The upper third is the ground surface: dry earth, scattered stones, a broken paving slab and a few grass roots, with soft daylight. Below it, layered brown and ochre soil runs down the frame like a gentle cutaway. In the lower-middle third a large plain clay storage jar lies on its side in the earth, half uncovered, its mouth cracked open. Spilling out and still partly embedded in the soil are BRONZE objects only: a few bronze tools (an axe-head, a chisel, a sickle blade), two small bronze bowls or vessels, and a handful of small bronze pieces and fragments, all dull green-brown with patina and only a faint warm metallic glint. Keep space below the jar so the tilt can settle on it. Quiet and mournful. No gold, silver, coins, gems or jewellery, no shiny yellow metal, no treasure chest or cartoon hoard, no clay tablets, no bones, no hands, tools or people of an excavation, no readable text, no modern objects.

## Outro · Unique dusk tell
**VO under it:** "History remembers the victors. We remember the rest."
**Time:** 49.1-~53.9s (includes about 1.3s tail)
**Suggested file:** `outro_ugarit_tell_violet_OWNER.png`
**Motion:** dissolve from 09 on "History". Static hold, with the logo and tagline added in the edit.
**Prompt:**
> Vertical 9:16 painterly Recovered Chronicle illustration, aged gouache texture. Deep dusk. The low, broad, flat-topped mound of the ruined tell of Ugarit is silhouetted in near-black across the bottom quarter of the frame, with faint low wall-stubs, long grass and one old olive tree on its crest, and a thin dark strip of distant sea to one side. Above it, a large, smooth, uncluttered violet sky fades from deep plum at the top to soft lavender and a thin warm rose glow just above the mound, with a single pale evening star near the top edge. Keep the whole middle of the frame (about 30-70% height) clean, smooth and empty for a wordmark and tagline. Calm, contemplative, final. No text, letters or logos of any kind, no people, no smoke or fire, no ruins in sharp detail, no fences, signs or modern buildings, no reuse of the composition of any earlier plate.
**Brand layer (edit):** POSTERITY wordmark + "History remembers the victors. We remember the rest." over this plate only. No second brand card.

---

## Guardrail check (VERIFY.md + LOCK-v3.md)
| Guardrail | Where it is enforced |
|---|---|
| Capital inland, harbour separate (~1.5 km), no palace over the docks | 01 (inland terrace, no docks below), 02 (road between city and harbour), 07 (same as 02) |
| Attackers unidentified, no Sea Peoples depiction | 01 and 05: dark silhouettes only, no bird-head prows, no feathered headdresses, no ethnic markers |
| Coastal raids kept separate from the capital's fall | 05 is a small town, not Ugarit. 06 follows after a dissolve, with no raiders |
| No "last letter" or final-days implication; kiln retired | 04 is a plain dictation scene; 08 is a tablet in rubble; no kiln or oven anywhere |
| No "nobody returned" overclaim | 07 shows only "no city", with ruins and grass |
| Payoff objects kept separate | 08 tablet only · 07 no treasure or tablet · 09 jar only, bronze (sourced hoards), no gold |
| No troop routes on the map | 03 has no lines, arrows or borders; labels come in the edit |
| No gore, readable text or modern objects | Global, and repeated in each prompt |
| No fire panoramas | 05 has a few roofs smoking; 06 has no flames |
| King continuity | 01 = 04: deep blue robe, red hem, headband, short dark beard, greying temples |

**Note for the shot map:** LOCK-v3 row 09 still says "bronze and gold pieces". This prompt follows the owner patch (bronze only, no gold). The LOCK row should be corrected to match.
