# Báthory v2: motion plan (DRAFT)

DRAFT for Vellum's gate. Nothing has been rendered. This plan is built on `storyboard-v2.md` (the LOCKED version, 11:47, with rulings applied), which supersedes `storyboard-v2-SKELETON.md`. It is checked against `script-v2.md`, `ARCHIVIST-CLAIMS-v2.md` (including the answers at the bottom), the desk rulings of 2026-10-31, `motion/PRESETS.md` and `ledger/edit-preferences.md`.

**Beat times** come from storyboard-v2 at 2.55 w/s, before pauses. Atelier re-times them to Oliver. The score cue sheet's ×1.10 times are noted wherever they change a check.

**Locked engines only:**
- **depth_v1:** two rigid layers, one push-and-drift from 1.00 to 1.06. When depth is on, it is the only camera.
- **torch_v1c / flames_v4:** the glow pulses and the flame shape holds. It runs as plate_fx under depth.
- **fx_candle:** candles only.
- **smoke_v2:** small torch smoke rides the near layer at about 0.4.
- **dust_v1:** motes in light shafts.
- **water_v1:** NOT USED. There is no water anywhere, per the desk ruling.

**Defaults on every beat unless the row says otherwise:**
- **Flat camera** is the standard restrained push from 1.00 to 1.06, ease 0.5/0.5, on the anchor named in the row.
- **Face exclusion:** faces are masked out of every light pulse and every flame warp, torch and candle alike, with pad 6px and feather 18px.
- **Hands, letters and archival pixels** take no displacement.
- **No motion on faces, water or land.**
- **No vignette, letterbox or watermark.** No LEGEND or DOCUMENTED labels.
- **Pixel density:** native 1080x1920 plates sit at 1.06 flat, and at about 1.06 plus overscan under depth (about 1.08 to 1.10, measured per config). All are at or below 1.5.

## 1. Per-beat plan

D = depth_v1. F = flat push. "near" and "far" are the depth layers.

| Beat | t (s) | Energy | Plate | Camera | Effect stack (engine: params/preset) | Matte needs | Plate requirements Scriptor must honour |
|---|---|---|---|---|---|---|---|
| B01a | 0.0-1.8 | INTRUSION | `b01a_bytca_led_away.png` | **D**: 1.00→1.06 push with a slight drift up toward the gateway. Authored from frame 0 (STANDING-LAW). Base it on `b05_landing_push_v1`. | **dust_v1** shaft motes in the dawn wash over the snow gap and gateway: zone poly × luma smoothstep(20,110), n≈800, preroll so motes are on screen at frame 0, as plate_fx split by layer. **NO smoke_v2.** The storyboard's "breath" is dropped (see Risk R3) and there is no chimney. No torch. | **Near:** the group of 2 guards and 4 servants, rigid. **Far:** the gateway and walls, plus sky. Seam on the snow gap. `protect` on all heads and hands (in_layer ≥0.97). `depth_ok_reason`: "INTRUSION: servants led away (action)". | Clear snow gap between the group and the gateway. Nothing crosses the near outline (no poles, sabres or reins). Faces never seen. A readable cold wash with painted fine snow or dust in it. No smoke anywhere. Group at 50-72% height, gateway at 25-45%. |
| B01b | 1.8-3.5 | ISOLATION | `b01b_never_tried.png` | **F** 1.00→1.06 onto her silhouette and the candle. | **fx_candle** (kind candle, house-candle-lightspill-v1): sway only inside the flame mask, 0 px elsewhere; pulse on the wall and table only. Optional **smoke_v2** candle wisp at ≤0.4. | Flame mask. Face/profile exclusion (6/18). Window or sky excluded from the pulse. | One whole, sharp candle flame fully in frame, not tight-cropped. Her face turned from the light, so no lit face is needed. Solid wall behind the flame so the spill reads. |
| B02 | 3.5-5.9 | UNEASE | ARCHIVAL c.1630 portrait (HNM, PD-Art, 845x1443), composited, **never regenerated** | **F only:** restrained push 1.00→1.06 on the face and upper body, centred. **No depth, no face motion.** The storyboard's StablePush 1.04 also passes; the owner picks. | **None.** The storyboard's dust_v1 is dropped under the desk ruling "flat restrained push only". There are no effects on the archival pixels, and the real inscription and arms stay untouched. Edit caption: "c.1630, posthumous, artist unknown" (Vellum ruling), set as a credit line, not a LEGEND or DOCUMENTED label. | None. | n/a (archival). **Density:** cover 1.331, 1.384 at 1.04, 1.411 at 1.06, all ≤1.5. No extra crop or zoom is allowed beyond 1.127× cover. Do not upscale-regenerate. Do not crop or alter the inscription or arms. |
| B03 | 5.9-8.0 | map | `b03_atlas_upper_hungary_CLEAN.png` plus the Atelier map engine | **F** 1.00→1.06 toward the Váh valley (Csejte). Deterministic. | Map engine, **house-map-inknib-dashed-v1**: ink-stamp markers for Csejte and Bytča (stamp lands at ≤0.6s), plus the manor/fortress inset. **Cloud shadows OFF** (no motion on land). **Water/river layer OFF** (no water). No route line, because transport is not recorded. | Marker anchor points from real coordinates. | **See R6:** the house rule says maps are deterministic graphics from real geo data, never AI-painted geography. The atlas base has to be georeferenced, or replaced with a deterministic base. The base carries no baked text, routes or markers. Drop the boilerplate "cold shaft/snow" light line from this prompt. |
| B04 | 8.0-10.4 | INTRUSION | `b04_riders_at_the_manor.png` | **D**: 1.00→1.06 push-and-drift toward the manor windows. Base it on `p10_escape_drift_v1`. | **torch_v1c** on the raised torch, as plate_fx in the near layer: whole-frame swing 10-14%, near-torch surfaces 20-45%, ≤3.1%/frame, ≤4.4Hz, painted tongue 0. Plus **smoke_v2** torch emitter at **0.4** on the near layer: cool grey, low detail, flame_keepout. The manor windows get a slow `window` pulse (window_amp ≤0.7). | **Near:** the 3 hajdú plus the torch. **Far:** the manor, the unlit fortress and the sky. Seam on the snow band. Torch rect for the guardrail (Laplacian var ≥100). Face exclusion on all three men. `depth_ok_reason`: "INTRUSION: armed men arrive". | One torch, whole and sharp, fully inside the near layer, not crossing the seam. A clear snow band. Fortress unlit. No banners, spears or poles across the near outline. |
| B05 | 10.4-12.2 | UNEASE | `b05_supper_manor.png` | **F** 1.00→1.06 drifting toward the dark doorway (upper right). | **fx_candle** on the three-branched candlestick. **torch_v1c offscreen** source at the doorway edge (explicit radius, scaled ×0.6 by the engine): **pulse only**. The light does not grow or approach (see R7). **smoke_v2** candle wisp ≤0.4. | Flame masks ×3. Face exclusion. Doorway poly for the offscreen spill. | The torch-edge glow must already be **painted** on the doorframe. Three whole flames. Doorway at 20-40% from the right edge. |
| B06 | 12.2-17.3 | UNEASE | `b06_rumours_village.png` | **F** 1.00→1.06 down the lane. | **dust_v1 in shaft-motes mode** in the low-sun band in the AIR above the lane, not ground-dust sheets (see R8). Feathered zone × luma; 0 px outside the zone. | Sun-band zone poly. Faces excluded. Ground, roofs and figures held still. | A low raking sun band clearly painted crossing the lane at head height, with motes. Figures small, faces averted or in shadow. |
| B07 | 17.3-21.2 | INTRUSION | `b07_thurzo_ordered.png` | **F** 1.00→1.06 toward the kneeling courier and doorway. It stays flat because this is a two-character plate, and B08/B09 come next. | **fx_candle** on the iron candle stand. Optional **smoke_v2** candle wisp ≤0.4. | Flame mask(s). Face exclusion on Thurzó and the courier (6/18). | Thurzó's likeness follows the 1607 Sadeler engraving. The candle stand is whole and sharp. Letters and seals are unreadable scribble. No king and no signing scene. |
| B08 | 21.2-27.1 | UNEASE | `b08_husbands_letter.png` | **F** 1.00→1.06 onto the hand and the letter. | **fx_candle** single candle. **smoke_v2** candle wisp ≤0.4 (storyboard). | Flame mask. Hand and letter zero displacement (spill only). | **Hand only, no face, no Nádasdy likeness** (desk ruling). Script unreadable. Sabre whole. |
| B09 | 27.1-29.4 | INTRUSION | `b09_arrest.png` | **D**: 1.00→1.06 push toward the doorway men with a slight drift. Base it on `b10_corfe_letter_drift_v1`. | **fx_candle** on her candlestick (near, plate_fx). **torch_v1c** on the 2 doorway torches (far, plate_fx). The "sweep" must be painted; the engine only pulses. No smoke (storyboard). Optional far-layer torch wisps at 0.4 if Vellum wants them. | **Near:** Báthory plus the candlestick, rigid. Her face and hands sit wholly in near (in_layer ≥0.97); face excluded from the pulse. **Far:** doorway, silhouetted men and torches. Seam in the gap. `depth_ok_reason`: "INTRUSION: the arrest". | Báthory and the candlestick at 38-62%. A clear floor gap to the doorway. Torches whole and sharp in the far layer. Men in silhouette, faces not needed. No gore: Thurzó's claimed girl at the manor stays OUT. |
| B10 | 29.4-33.5 | INTRUSION (transfer) | `b10_bytca_transfer.png` | **D**: 1.00→1.06 push toward the shut door. **Back-to-back with B09, kept per the desk ruling** (see §2). **Fallback: B10 flat** if Vellum wants a buffer. | **smoke_v2 "breath"** (storyboard) on the near layer at ≤0.25: tiny, short-lived, low detail, above heads seen from behind. **Gated:** there is no locked breath config (see R3). If it reads as smoke at 360x640, swap to **dust_v1** snow motes in the grey wash. No torch, no fire. | **Near:** the cart, 4 servants from behind and 1 guard. **Far:** the arcade and shut door. `protect` on heads and hands. `depth_ok_reason`: "transfer (group transfer, not a character plate)". | Atmosphere only: transport isn't recorded. No ropes, shackles or interrogation, and no faces. A clear cobble gap. Nothing crosses the near outline. No smoke anywhere else. |
| B11 | 33.5-35.7 | ISOLATION | `b11_bytca_door_shut.png` | **F** 1.00→1.06 onto the shut door. | **dust_v1** shaft motes as the fine falling snow in the cold shaft. **NO smoke_v2, NO torch** (execution beat: empty courtyard, grey light). | Shaft zone poly. | Empty, no people, no execution site. A single cold shaft. Painted falling snow. No smoke, pyre or glow. |
| B12 | 35.7-39.2 | ISOLATION | `b12_taken_up_to_fortress.png` | **F** 1.00→1.06 up the switchback toward the high window. | **torch_v1c** on 4 small torches (halo and local spill only; spill kept off open hillside). A `window` pulse on the high window (≤0.7). **smoke_v2** torch emitters at **0.4**, cool grey. | 4 torch rects (guardrail). Hillside excluded from spill. | **Each torch flame needs to be big and sharp enough to pass the guardrail** (Laplacian var ≥100; roughly ≥25px tall). Otherwise the engine refuses and the beat falls back to the window pulse only. Figures tiny. |
| B13 | 39.2-43.5 | INTRUSION | `b13_courier_turned_away.png` | **F** 1.00→1.06 into the gap of the closing gate. (Optional depth: see R10.) | **torch_v1c** on the gatekeeper's torch, pulse only. The gate does not move; the "closing" is painted. | Torch rect. Face exclusion on the courier and gatekeeper. | Torch whole and sharp in the gap. Gate painted mid-close. Courier's face averted. |
| B14 | 43.5-45.0 | ISOLATION | `b14_why_window.png` | **F**: slow push 1.00→1.06 onto the window. | **dust_v1** shaft motes in the cold window shaft. | Shaft zone. Her profile excluded. | A three-quarter back view. A clear cold shaft with painted motes. No slit window or bricked cell (confinement = castle rooms). |
| B15 | 45.0-49.4 | UNEASE | `b15_thurzo_depositions.png` | **F** 1.00→1.06 onto the deposition sheets. | **fx_candle.** No smoke (storyboard), to keep B15-B17 from being three smoke shots in a row. | Flame mask. Face exclusion on Thurzó and the clerk. | Candle whole. Sheets unreadable. Commission, not torture: no witnesses being tortured. |
| B16 | 49.4-55.3 | ISOLATION | `b16_family_silence.png` | **F** 1.00→1.06, slow, onto the hearth group. | **torch_v1c** on the hearth fire. **smoke_v2** low column inside the hearth opening at ≤0.4, clipped to the hearth. | Hearth flame key. Face exclusion on all 3 men (faces turned away anyway). | Hearth flames visible and sharp (bright tongues key at L≥140/R≥170). Faces turned away. No Nádasdy likeness. |
| B17 | 55.3-58.8 | UNEASE | `b17_secondhand_witnesses.png` | **F** 1.00→1.06 along the queue toward the notary. | **torch_v1c** on the brazier. **smoke_v2** brazier column at 0.4, cool grey. | Brazier flame key. Face exclusion on the queue and notary. | **The brazier needs visible flame tongues**, not just glowing coals, or it won't key. No torture implied (commission witnesses). |
| B18 | 58.8-60.4 | ISOLATION | `b18_empty_room.png` | **F** 1.00→1.06 onto the sill. | **smoke_v2** single candle-type thread from the snuffed wick (≤0.4, preroll 8s). **dust_v1** cold window shaft. | Wick point plus shaft zone. | Thread origin is clear on the snuffed wick. Shaft painted. No bed, no body. |
| B19a | 60.4-62.0 | ISOLATION | REUSE `b11_bytca_door_shut.png` | **F** 1.00→1.06. Use a different anchor or crop from B11 so it doesn't read as a repeat. | dust_v1 snow, same as B11. **No smoke or torch.** | Same as B11. | Same as B11. |
| B19b | 62.0-63.5 | UNEASE | REUSE archival B02 | **F** restrained push only. | None (archival). | None. | Same as B02. |
| B20 | 63.5-69.0 | ISOLATION | `b20_closing_eyes.png` | **F: RULE-FORCED CHANGE** from the storyboard's depth (see §2 and R1). Push 1.00→1.06 anchored on the eyes, landing on "No court ever decided". **Owner-override option:** depth_v1 with face = near, wall and candle = far. | **fx_candle** on the low background candle; spill on the far wall only. Face excluded (so the face never flickers). | Flame mask. Full face and hair exclusion. | Eyes at 38-42%. For flat, consider a face at 50-60% of frame width so the dark wall and candle read. Whole sharp candle. |
| Outro | 69.0-72.2 | outro | `outro_bathory_csejte_first_light_OWNER.png` | **F** 1.00→1.06 (or OutroHold static if house law requires it). | **dust_v1** shaft motes in the first-light air band. Not "frost glitter": there's no locked glitter engine, and water_v1 glints are water-only. | **Protect the baked wordmark and tagline** (0 px). Rooks still. Ground and vines still. | Owner plate as supplied. Check its native size for density. |

## 2. Depth count, spacing and runs

**Depth count: 4 of 22 slots (18%):**
- B01a at slot 1
- B04 at slot 5
- B09 at slot 10
- B10 at slot 11

That is under the 1-in-3 cap (7.3). If the owner overrides B20 back to depth, it becomes 5 of 22 (23%), still under the cap.

**Gaps:**
- B01a→B04: 3 slots
- B04→B09: 4 slots
- B09→B10: 0 slots, kept per the desk ruling

**B09 + B10 back-to-back, kept by desk ruling.**
- **Reason:** B10 is a group transfer, not a character plate, so the back-to-back character-plate rule isn't broken. It also crosses a scene change, from the Csejte manor at night to the Bytča courtyard by day.
- **Note:** build_template will WARN because B09 is a character plate. Log the ruling as B10's `depth_ok_reason`.
- **Fallback:** B10 flat (depth count 3 of 22), if Vellum wants a buffer.

**B20 changed from depth to flat (rule-forced), so this differs from the storyboard's "Depth 5 of 22".** Rules that force it:
- The brief allows depth only on action, INTRUSION or transfer beats, and B20 is ISOLATION, a quiet portrait.
- PRESETS says quiet portraits stay flat.
- A frame-wide face leaves almost no far layer, and with face exclusion the candle pulse reaches only the background.

I disagree with the storyboard here, so it's flagged and not hidden. Depth remains the owner-override option.

**Every depth beat carries an action reason:**
- B01a: led away
- B04: arrival
- B09: arrest
- B10: transfer

No depth beat is adjacent to the archival portrait or the map.

**Treatment runs:**

| Run | Slots | Notes |
|---|---|---|
| Identical: flat + candle + smoke wisp | B07, B08 | 2 in a row, OK. Different scale: wide room vs hand close-up. |
| Identical: flat + small-fire pulse | B12, B13 | 2, OK |
| Firelight-pulse family | B15, B16, B17 | 3 in a row (candle, hearth, brazier). B15 smoke removed to break the smoke run to 2 (B16, B17). Mitigation option: B16 cold shaft and dust instead of the hearth, to match ISOLATION guidance. |
| Dust motes | B11, B14, B18, B19a, Outro | Never adjacent except B18 to B19a (different plates, both ISOLATION). OK. |
| **Flat stretch** | **B11 → Outro, 12 slots, about 38.7s (33.5-72.2)** | **Flagged.** The whole back half has no depth. With the storyboard's B20 depth it would still be 30s (B11-B19b). See R10 for the B13 option. |
| Energy runs | none over 2 | Same as storyboard |

**Effect read at 360x640 within 1s:**
- Torch and candle pulses read at once.
- Depth ease lands at about 1-2s, so B04 and B09 lean on the torch pulse for the first second.
- B01a leans on the prerolled dust motes.
- B10 is 4.1s long, so depth lands fine.
- Nothing strobes: ≤3.1%/frame and ≤4.4Hz.

**Shots under 3s (outside the opening):**

| Shot | Storyboard (s) | ×1.10 (s) |
|---|---|---|
| B02 | 2.4 | 2.6 |
| B03 | 2.1 | 2.3 |
| B04 | 2.4 | 2.6 |
| B05 | 1.8 | 2.0 |
| B09 | 2.3 | 2.5 |
| B11 | 2.2 | 2.4 |
| B14 | 1.5 | 1.7 |
| B18 | 1.6 | 1.8 |
| B19a | 1.6 | 1.8 |
| B19b | 1.5 | 1.7 |

The shortfall is about 10.6s at storyboard times, or about 8.7s at ×1.10. See R2.

## 3. Stacks by energy

- **INTRUSION** (B01a, B04, B07, B09, B10, B13): concentrated motion.
  - All 4 depth shots live here.
  - Depth with torch_v1c as plate_fx on B04 and B09, torch smoke at 0.4 on B04.
  - B01a and B10 have no fire. Bytča gets motes, and breath only if it doesn't read as smoke.
  - B07 and B13 are flat, with a pulse toward the threshold.
- **UNEASE** (B02, B05, B06, B08, B15, B17, B19b): candle and torch pulse, candle wisps at ≤0.4, brazier smoke at 0.4.
  - B02 and B19b are archival: push only.
  - B06 is daylight, so motes go in the raking sun band.
- **ISOLATION** (B01b, B11, B12, B14, B16, B18, B19a, B20): stillness plus dust_v1 in cold shafts (B11, B14, B18, B19a).
  - Small distant torches on B12, the hearth on B16, a single background candle on B01b and B20.
  - No depth (B20 rule-forced flat).
- **Map** (B03): deterministic map engine, markers and inset. Cloud shadows and water off.
- **Outro:** dust motes in first light, baked text protected.

## 4. Risks and open questions

- **R1. B20 depth vs. rules (owner decision).**
  - Flat is the rule-compliant default.
  - The gate notes want a strong closing reveal; the flat push to the eyes gives that without depth.
  - Inconsistency: the ledger says Seq12b SURVIVE, but the storyboard prompts a new painting. Confirm which plate.
- **R2. Ten shots under 3s.**
  - Options with no VO change:
    - (a) Planned pauses after L02, L13 and each verdict line (L15-L17). This covers B02, B14 and B18-B19b at Oliver pace plus 1.0-1.4s pauses.
    - (b) Let B03 carry into the first words of L03, and let B04 run into the start of B05's line.
    - (c) Merge B19a and B19b into one 3.1s shot: the B11 reuse under L16, with a hard cut to B02 only if a pause lengthens L17.
  - Cost: about 8-10s of runtime, and the arrest lands at about 13s, not 12s. Vellum/Atelier decide.
  - Is B01b exempt as part of the opening, or only B01a? Not clear.
- **R3. Breath smoke at Bytča (B01a, B10).**
  - smoke_v2 has no locked "breath" config. The emitter types are candle, torch, column and haze.
  - At 360x640, breath above heads can read as smoke near Bytča, which is exactly what the Archivist banned (it signals the burning method).
  - Plan: dropped on B01a, kept as a gated option on B10 at ≤0.25. Fallback is dust_v1 snow. This needs a test frame before lock.
- **R4. Face exclusion on candles.**
  - The candle lock lit faces at about 31%, and the FIRE-LIT boilerplate says light "spills across faces".
  - The brief's exclusion is written for torch flicker. I've applied it to candles too, to be safe.
  - Confirm, or allow candle spill on faces as a static light change with no pulse.
- **R5. Short depth shots.**
  - B01a (1.8s) and B09 (2.3s) push 6% fast. That risks reading as a punch-in and goes against the no-random-zoom rule.
  - Option: depth amount 1.00→1.04 on B01a only. That isn't the locked move, so it needs owner OK.
- **R6. B03 atlas is AI-painted geography.** This conflicts with the house map rule (deterministic, real geo data). Markers will sit on invented terrain. Use a georeferenced or deterministic base, or verify the painted one.
- **R7. Engine limits vs. storyboard wording.**
  - B05's "approaching" torchlight, B09's torch "sweep" and B13's "closing" gate are painted states. The engines only pulse; nothing moves or grows.
  - The F4 "torch flutter sweeping" is sound only.
- **R8. B06 dust mode.**
  - Ground-dust sheets were locked with fixed framing, and they put motion on land.
  - The plan uses shaft motes in the sun band so the push is kept. Confirm.
- **R9. B12 small torches** may fail the sharpness guardrail, so the plate needs flames of about 25px or more. Their smoke at 0.4 may not read at phone size; it's optional.
- **R10. Long flat back half (about 38.7s).**
  - Option: make **B13 a depth shot.** It's an INTRUSION arrival (courier near, gate and torch far, gap between).
  - Its prompt would need to change from FLAT PLATE to DEPTH PLATE.
  - Count would be 5 of 22, B10→B13 gap 2.
  - Not in the plan unless Vellum/owner OK it.
- **R11. B02 push amount:** the storyboard says 1.04 and the brief's standard is 1.06. Both pass density. B19b's 1.5s reuse would push fast at 1.06.
- **R12. Outro.**
  - "Frost glitter" isn't a locked effect, so dust motes are substituted.
  - Is OutroHold static or the standard push?
  - Verify the owner plate's native size (≤1.5 density).
- **R13. Storyboard housekeeping.**
  - The table rows are out of order (B03 before B02, B19 before B17).
  - The "full set" still lists water_v1 (unused).
  - B03's prompt carries a cold-shaft or snow light line meant for interiors.
- **Not used / banned, confirmed:**
  - water_v1
  - vignette, letterbox, watermarks
  - LEGEND/DOCUMENTED labels (B02's caption is a credit line)
  - gore, the supernatural
  - pyre, smoke column or fire glow at Bytča
  - a Nádasdy likeness
