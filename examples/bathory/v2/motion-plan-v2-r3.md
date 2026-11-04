# Báthory v2: motion plan r3

r3 is r2 plus Vellum's 11:55 (Toronto time) ruling on the B20 candle, plus storyboard changes up to 11:55 (diffed against `storyboard-v2.md.pre-gate7`). r2 and the DRAFT are untouched.

**Changes from r2:**
- B20 candle runs at about half the lock (≈15% on her face). Every other candle stays at the exact lock.
- B13 is now an unlit silhouette standing clear of the lit gap, with no torch in the palette. The torch-if-painted line and the plume hand-fix flag are dropped.
- B20 face is at 70-80% of the frame width, with the candle visible.
- B03 has no inset. It uses only the Csejte and Bytča markers, registered to `MAP-PLACES-bathory-v1.md`.

The r2 text follows, with these changes applied.

**Source:** built from the latest `storyboard-v2.md` (11:52, while Scriptor was still applying fixes: depth 6 of 22, breath off, B13 as a DEPTH PLATE, B07 as Thurzó alone, B02 with no on-screen caption). Also checked against `script-v2.md`, `ARCHIVIST-CLAIMS-v2.md`, `motion/PRESETS.md` and the ledger.

**No video rendered.** The density figures below come from depth_v1's own overscan math, run on numbers only.

## Rulings applied (final)

1. **B20 is DEPTH** by the owner's direction for the closing reveal. It is logged as owner direction, not an override.
2. **B13 "doors drawn shut" is DEPTH.**
   - **Near:** the doors plus Thurzó's silhouette.
   - **Far:** the candlelit chamber.
   - **Effect:** candle; torch_v1c only if torches are painted (moot as of 11:55: no torch is painted).
3. **Short shots are accepted** for this cut.
   - The floor is about 1.5s, except deliberate hard-cut beats.
   - The arrest is not retimed past 12s.
4. **B03 is a map plate registered to our geodata** (new architecture; a separate task is building the Upper Hungary 9:16 reference). It is flat, with map-engine markers for Csejte and Bytča only.
5. **Candles use the approved lock exactly**, about 31% on faces, so there is no candle face exclusion. **Exception (11:55 ruling): B20's candle runs at about half the lock, ≈15% on her face, so the close stays uneasily still and doesn't pulse.** **Torch pulses stay off faces** (pad 6px, feather 18px).
6. **Breath smoke is off everywhere.** B10 uses dust_v1.
7. **B07** is Thurzó alone reading a folded letter by candle, flat, as a character plate. **B16** is two young noblemen and a boy of about 12, with no effect change.

**Defaults** (unless the row says otherwise):
- Flat camera is the standard restrained push 1.00→1.06, ease 0.5/0.5, on the anchor named in the row.
- Depth uses depth_v1's single 1.00→1.06 push-and-drift as the ONLY camera, with locked effects as plate_fx split by layer.
- No displacement on faces, hands, letters, archival pixels, water or land.
- No vignette, letterbox, watermark, or LEGEND/DOCUMENTED labels.

## 1. Per-beat table

D = depth_v1, F = flat push.

| Beat | t (s) | Energy | Plate | Camera | Effect stack | Mattes | Plate requirements (Scriptor) |
|---|---|---|---|---|---|---|---|
| B01a | 0.0-1.8 | INTRUSION | `b01a_bytca_led_away.png` | **D** 1.00→1.06 push with a slight drift toward the gateway, authored from frame 0. Base config: `b05_landing_push_v1`. | **dust_v1** shaft motes in the dawn wash (zone poly × luma smoothstep(20,110), n≈800, prerolled so they're visible at frame 0). No smoke, no breath, no torch. | **Near:** guards + 4 servants, rigid; `protect` heads and hands. **Far:** gateway + walls + sky. Seam on the snow gap. `depth_ok_reason` "INTRUSION: servants led away". | Clear snow gap. Nothing crosses the near outline. No faces. A painted cold wash with fine snow. No smoke anywhere. |
| B01b | 1.8-3.5 | ISOLATION | `b01b_never_tried.png` | F onto her and the candle. | **fx_candle** (house-candle-lightspill-v1, exact lock, about 31% on faces). Optional **smoke_v2** candle wisp ≤0.4. | Flame mask. Window excluded from the pulse. | One whole, sharp candle flame. |
| B02 | 3.5-5.9 | UNEASE | ARCHIVAL c.1630 portrait (HNM, PD-Art, 845x1443), composited, never regenerated | **F only**, restrained push. Standard 1.00→1.06; the storyboard's 1.04 is also within density. **No depth, no face motion.** | **None** (no dust on the archival pixels). No on-screen caption; the credit goes in the post description (storyboard). | None. | Archival. Density: 1.331 cover, 1.384 at 1.04, 1.411 at 1.06. Inscription and arms untouched. |
| B03 | 5.9-8.0 | map | `b03_atlas_upper_hungary_CLEAN.png`, registered by Atelier to Archivist's geodata (`MAP-PLACES-bathory-v1.md`); the Upper Hungary 9:16 reference is a separate task | F 1.00→1.06 toward the Váh valley, deterministic. | Map engine **house-map-inknib-dashed-v1**: ink-stamp markers for **Csejte and Bytča only** (stamp ≤0.6s). No inset, no route. Cloud shadows OFF (no motion on land). Water/river animation OFF. | Marker anchors from real coordinates. | Registered to our geodata. No baked labels, icons or routes. |
| B04 | 8.0-10.4 | INTRUSION | `b04_riders_at_the_manor.png` | **D** 1.00→1.06 push-and-drift toward the manor windows. Base config: `p10_escape_drift_v1`. | **torch_v1c** on the raised torch (near plate_fx): whole-frame 10-14%, local 20-45%, ≤3.1%/frame, ≤4.4Hz, painted tongue 0. **smoke_v2** torch emitter **0.4** on the near layer, cool grey. Manor `window` pulse ≤0.7. | **Near:** 3 hajdú + torch. **Far:** manor, unlit fortress, sky. Torch rect guardrail (Laplacian ≥100). **Torch-pulse face exclusion** 6/18. `depth_ok_reason` "INTRUSION: armed men arrive". | One whole, sharp torch wholly in the near layer. A snow band. No poles or banners across the outline. |
| B05 | 10.4-12.2 | UNEASE | `b05_supper_manor.png` | F drifting toward the doorway (upper right). | **fx_candle** on the 3-branch candlestick (lock, faces lit). **torch_v1c offscreen** at the door edge, pulse only, faces excluded 6/18. **smoke_v2** candle wisp ≤0.4. | Flame masks ×3. Doorway poly. Face masks for the torch component only. | Torch-edge glow **painted** on the doorframe (it doesn't grow). Three whole flames. |
| B06 | 12.2-17.3 | UNEASE | `b06_rumours_village.png` | F down the lane. | **dust_v1** shaft motes in the low-sun band, in the air (not ground sheets, which would mean fixed framing and motion on land). | Sun-band zone. Faces, ground and roofs at 0 px. | A raking sun band painted at head height. |
| B07 | 17.3-21.2 | INTRUSION | `b07_thurzo_ordered.png` | F onto Thurzó and the letter. **Character plate.** | **fx_candle** on the iron stand (lock, about 31% on his half-lit face). Optional **smoke_v2** wisp ≤0.4. | Flame mask. Hands and letter at 0 px displacement. | Thurzó alone, no courier. Sadeler 1607 likeness reference. Seal blank, writing unreadable. Stand whole and sharp. |
| B08 | 21.2-27.1 | UNEASE | `b08_husbands_letter.png` | F onto the hand and letter. | **fx_candle** (lock). **smoke_v2** wisp ≤0.4. | Flame mask. Hand and letter at 0 px. | Hand only, no Nádasdy face. Unreadable script. |
| B09 | 27.1-29.4 | INTRUSION | `b09_arrest.png` | **D** 1.00→1.06 push toward the doorway men. Base config: `b10_corfe_letter_drift_v1`. **Character plate.** | **fx_candle** on her candlestick (near plate_fx, lock: her face lit). **torch_v1c** on the 2 doorway torches (far plate_fx), **faces excluded 6/18**. No smoke. The "sweep" is painted. | **Near:** Báthory + candlestick (face and hands in_layer ≥0.97). **Far:** doorway, men, torches. `depth_ok_reason` "INTRUSION: the arrest". | Báthory and the candlestick at 38-62%. A floor gap. Whole, sharp far torches. No gore. |
| B10 | 29.4-33.5 | INTRUSION (transfer) | `b10_bytca_transfer.png` | **D** 1.00→1.06 push toward the shut door. **Back-to-back with B09, ruled OK** (§2). Fallback: B10 flat. | **dust_v1** snow motes in the grey courtyard wash. No breath, no smoke, no torch. | **Near:** cart, 4 servants from behind, 1 guard; `protect` heads and hands. **Far:** arcade + shut door. `depth_ok_reason` "transfer: group, not a character plate". | Atmosphere only. No faces, ropes or shackles. A cobble gap. Painted grey wash with fine snow. |
| B11 | 33.5-35.7 | ISOLATION | `b11_bytca_door_shut.png` | F onto the shut door. | **dust_v1** falling snow in the shaft. **No smoke or torch** (execution beat). | Shaft zone. | Empty courtyard, grey light, no people, no smoke or glow. |
| B12 | 35.7-39.2 | ISOLATION | `b12_taken_up_to_fortress.png` | F up the switchback. | **torch_v1c** on 4 small torches (halo and road spill only, hillside excluded, faces excluded). `window` pulse ≤0.7. **smoke_v2** torch emitters 0.4. | 4 torch rects (guardrail). Hillside mask. | Torch flames ≥ about 25px tall and sharp, or the guardrail refuses them (fallback: window pulse only). |
| B13 | 39.2-43.5 | INTRUSION | `b13_doors_drawn_shut.png` | **D** 1.00→1.06 push into the lit gap, with lateral drift. **Set near push_gain ≈ far push_gain** (config fields, not a new engine) so the doors don't scale apart and read as *opening* (R2). Parallax comes from drift travel ≈0.04. | **fx_candle** on the far candle stand (far plate_fx, exact lock). Pulse and spill on the far table, chairs and floor only. The silhouette stays unlit, and no faces are visible. No torch, no smoke. | **Near:** both doors + Thurzó silhouette + his hand on the door edge, all one layer. **Far:** the chamber seen through the gap. Seam on the door edges. The silhouette sits clear of the lit opening, so no plume hand fix is expected. Revealed strips at the door edges pre-filled. `depth_ok_reason` "INTRUSION: doors drawn shut on the trial (silhouette, no face)". | (Applied at 11:55.) Silhouette to one side, clear of the lit gap, unlit, face never shown. A clear floor gap to the chamber. Candle stand whole and sharp in the gap. Palette is candle gold and moonlight, no torch. |
| B14 | 43.5-45.0 | ISOLATION | `b14_why_window.png` | F, slow push onto the window. | **dust_v1** in the cold window shaft. | Shaft zone. Her profile at 0 px. | A clear cold shaft. No slit window. |
| B15 | 45.0-49.4 | UNEASE | `b15_thurzo_depositions.png` | F onto the sheets. | **fx_candle** (lock). No smoke. | Flame mask. | Candle whole. Sheets unreadable. No torture. |
| B16 | 49.4-55.3 | ISOLATION | `b16_family_silence.png` | F, slow, onto the hearth group. | **torch_v1c** on the hearth (**faces excluded 6/18**). **smoke_v2** low hearth column ≤0.4, clipped to the hearth opening. | Hearth flame key. Face masks ×3 (2 young noblemen + boy about 12). | Hearth flames whole and sharp. Faces turned away. No documents or seals. |
| B17 | 55.3-58.8 | UNEASE | `b17_secondhand_witnesses.png` | F along the queue to the notary. | **torch_v1c** on the brazier (faces excluded). **smoke_v2** brazier column 0.4, cool grey. | Brazier key. Face masks. | Visible brazier flame tongues, not just coals. |
| B18 | 58.8-60.4 | ISOLATION | `b18_empty_room.png` | F onto the sill. | **smoke_v2** snuffed-wick thread ≤0.4 (preroll 8s). **dust_v1** window shaft. | Wick point. Shaft zone. | Clear wick origin. A painted shaft. |
| B19a | 60.4-62.0 | ISOLATION | REUSE B11 | F, different anchor from B11. | dust_v1 snow. No smoke or torch. | Same as B11. | Same as B11. |
| B19b | 62.0-63.5 | UNEASE | REUSE archival B02 (**hard cut**) | F restrained push. | None. | None. | Same as B02. |
| B20 | 63.5-69.0 | ISOLATION | `b20_closing_eyes.png` | **D, owner direction.** 1.00→1.06 push anchored on the eyes (0.5, 0.40), little or no drift (≤0.02). Ease-out settles before "No court ever decided". **Character plate.** | **fx_candle** on the low far candle (far plate_fx) at **about half the lock: ≈15% on her face** (Vellum 11:55), so the close stays uneasily still and doesn't pulse. The flame itself sways only inside its mask. No other effect. | **Near:** face, cap, collar (whole face and hands in_layer ≥0.97, NCC ≥0.9999). **Far:** wall + candle, with dark space on both sides. Hand fix on the cap and hair edge if needed. `depth_ok_reason` "owner direction: closing reveal". | (Applied at 11:55.) Face at 70-80% of the frame width with dark space either side. Candle low at the side, whole, visible and clear of her outline. Eyes at 38-42%, centred. |
| Outro | 69.0-72.2 | outro | `outro_bathory_csejte_first_light_OWNER.png` | F 1.00→1.06 (or static OutroHold if house law requires it). | **dust_v1** motes in the first-light air band (stands in for "frost glitter"). | Baked wordmark and tagline at 0 px. Rooks and ground still. | Owner plate as supplied. Confirm its native size. |

## 2. Depth count, spacing, back-to-back and runs

**Depth: 6 of 22 slots (27%):**
- B01a (slot 1)
- B04 (slot 5)
- B09 (slot 10)
- B10 (slot 11)
- B13 (slot 14)
- B20 (slot 22)

That is under the 1-in-3 cap (7.3 slots).

**Gaps between depth slots:** 3, 4, 0, 2, 7.
- B13 has flat on both sides: B12 and B14.
- B20 follows the B19b hard cut (flat archival) and is followed by the flat outro.

**Back-to-back character rule, rechecked:**
- **B09 + B10** is the only adjacent depth pair. B09 is a character plate, but B10 is a group transfer seen from behind, not a character plate, and the cut crosses a scene change. **Ruled OK.** build_template will still WARN; log the ruling in B10's `depth_ok_reason`. Fallback: B10 flat.
- **B13** is a silhouette with no face, not a character face. Its neighbours are flat anyway. Pass.
- **B20** is a character plate. Its neighbours are flat. Pass.
- **B07** is now a character plate. It is flat. Pass.

**Pixel density at the depth push.** These figures come from depth_v1's overscan math (the same `_covers` test), assuming a native 1080x1920 plate, near push_gain 1.0, far 0.4, pivot 0.5:

| Shot | Camera | Overscan | Max output px per source px |
|---|---|---|---|
| **B20** | pure push on the eyes (0.5, 0.40); unchanged by the 70-80% face width | 1.000 | **1.060** |
| **B20** | push + drift 0.02 | 1.010 | **1.071** |
| **B13** | push into gap (0.5, 0.45) + drift 0.04 | 1.020 | **1.081** |
| Reference | Corfe-style drift 0.04 | 1.022 | 1.084 |

- All are ≤1.5 with large margin. Plates delivered larger than 1080x1920 are lower still.
- Flat plates are 1.06. The archival portrait is 1.411 at 1.06, or 1.384 at 1.04.
- The B13 recommendation (near gain ≈ far gain) lowers B13's density further.
- These need confirming with the engine's `guard()` once the plates exist.

**Short shots (ruling 3, floor about 1.5s):**
- Below 1.5s: none at storyboard times.
- At the floor: B14 is 1.5s (pause included, so keep the pause) and B19b is 1.5s (a deliberate hard cut, exempt).
- All others are ≥1.6s. At Oliver's ×1.10 read, every shot is ≥1.65s.
- The arrest is not retimed: B04 "armed men entered" runs 8.0-10.4, B05 ends at 12.2.
- **No flags.**

**Treatment runs:**
- **Flat back-half stretch:** previously 38.7s. Now B11-B12 (5.7s), B14-B19b (20.0s), the longest flat stretch, then B20 depth.
- **Firelight-pulse run:** B15, B16, B17 (candle, hearth, brazier). This is 3 flat fire beats; there is no smoke on B15, so the smoke run is only 2.
- **Identical flat candle + optional wisp:** B07 and B08, a run of 2 (wide vs hand close-up).
- **Energy runs:** none over 2.

## 3. Stacks by energy

- **INTRUSION** (B01a, B04, B07, B09, B10, B13): 5 of the 6 depth shots.
  - Torch pulse + torch smoke 0.4 on B04.
  - Candle (near) + torches (far) on B09.
  - dust_v1 on B01a and B10 (Bytča: no smoke).
  - Candle in the far gap on B13 (spill on the far chamber only).
  - B07 is flat candle.
- **UNEASE** (B02, B05, B06, B08, B15, B17, B19b):
  - Candles at lock, with candle wisps ≤0.4.
  - Offscreen torch pulse on B05; brazier pulse + smoke 0.4 on B17.
  - Sun-band motes on B06.
  - B02 and B19b are archival, push only.
- **ISOLATION** (B01b, B11, B12, B14, B16, B18, B19a, B20):
  - Cold-shaft dust on B11, B14, B18, B19a.
  - Small torches on B12, hearth on B16.
  - Candle on B01b; B20 is the depth closing reveal with a far candle at about half the lock (≈15% on the face).
- **Map** (B03): geodata-registered base, two ink-stamp markers, deterministic.
- **Outro:** dust motes, text protected.

**One-line effects summary for Pulse:** the cut uses
- **depth_v1** ×6 (B01a, B04, B09, B10, B13, B20)
- **torch_v1c** (B04, B05 offscreen, B09, B12, B16, B17)
- **fx_candle** at the exact lock (B01b, B05, B07, B08, B09, B13, B15), and at about half the lock on B20 (≈15% on the face)
- **smoke_v2** (torch 0.4 on B04 and B12, hearth on B16, brazier on B17, candle wisps on B05 and B08, optional on B01b and B07, wick thread on B18; no breath, nothing at Bytča)
- **dust_v1** (B01a, B06, B10, B11, B14, B18, B19a, Outro)
- **map engine house-map-inknib-dashed-v1** (B03)
- **water_v1 is not used.**

## 4. Remaining risks and open questions

**Closed since r2:**
- B20 prompt conflict (face now at 70-80% width, candle visible).
- B20 face pulse (now about half the lock).
- B13 plume and kalpak against the light (silhouette now clear of the gap).
- B13 torch palette mismatch.
- B03 inset (removed from the storyboard).

**Still open:**
- **R1. B20 half-lock is not a locked preset.**
  - "≈15% on the face" is a new parameter value for fx_candle: amplitude about 0.5× of house-candle-lightspill-v1. Pulse should log it as a ruled per-shot variant, not a new lock.
  - The B20 FIRE-LIT boilerplate still says the light "spills across faces… suit a gentle flicker animation". It doesn't conflict, but Scriptor could soften it to match the stillness.
- **R2. B13 can still read as doors OPENING.**
  - The default depth push scales the near layer faster than the far.
  - Keep the matched push_gain with drift-led parallax, and test it on the real plate.
  - New, minor: his one hand on the door edge sits next to the lit gap. Keep it fully inside the near layer (`protect`).
- **R3. Engine limits.** B05's approaching light, B09's torch sweep and B13's closing doors are painted states. The engines only pulse.
- **R4. B12 small torches** may fail the sharpness guardrail; the fallback is the window pulse only.
- **R5. B17 brazier** needs visible flames to key.
- **R6. B02 push value:** 1.04 (storyboard) vs 1.06 (standard). Both pass. The B19b 1.5s reuse would push fast at 1.06.
- **R7. Outro:** confirm static OutroHold or the standard push. "Frost glitter" is replaced by dust motes. Confirm the owner plate's native size.
- **R8. Short depth shots** (B01a 1.8s, B09 2.3s) move 6% quickly. Accepted under ruling 3, but watch for a punch-in feel in the edit.
- **R9. B03 geodata registration** depends on `MAP-PLACES-bathory-v1.md` and the separate Upper Hungary 9:16 reference task. Marker placement can't be verified until both land.
- **R10. Storyboard still moving** (backups `.pre-gate4` through `.pre-gate7`; latest 11:55). Re-diff before Atelier builds configs.
