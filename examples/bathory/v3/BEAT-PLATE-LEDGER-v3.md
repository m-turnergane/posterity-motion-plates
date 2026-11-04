# Báthory v3 · BEAT-PLATE-LEDGER-v3.md (Atelier, 31 Oct 2026)

> **Rev 2 (15:50 EDT): H01/H02 on disk (KEEP); L11 is being extended again (L11b pending); B08 revival under review by the parent.** Rev 1 header follows.
>
> **VO-LOCKED, with L11 PENDING REVISION.** The VO is `raw/script-vo-v3.txt` (205 words, Archivist countersign PASS), identical to the DRAFT file at the lock. The owner has reopened **L11**. Its quote below is the pre-revision text, and **every time after V11 will shift** by the change in L11's length.
>
> - Beats follow Scriptor's updated beat sheet in `script-v3.md` (V01–V15 plus the Outro). H01 and H02 map to V01, H03 to V05, H04a to V13 and H04b to V15.
> - Times (s) come from the earlier TEMP read (84.9 s). A provisional pre-L11 read of the locked file gave identical timings.
> - The score is locked: Anabasis I, 256–344 s (see `SCORE-LOCK-v3.md`).
> - The movements follow the owner's binding structure note: **M1** Accusation · **M2** Investigation and intrusion · **M3** Reversal · **M4** Final revelation. A plate that serves no movement is CUT.
> - No plates were generated and no cut was rendered. The H-plates are owner commissions, in production at **native 1080×1920**, with no files yet.
> - The earlier `BEAT-PLATE-LEDGER-v3-skeleton.md` is kept unchanged.

> **Rev 3b — FINAL for Rough v3b (16:58 EDT).** The table directly below is the as-built `renders/bathory_rough_v3b.mp4` (101.5 s, md5 63716245…). The Rev 3 table after it remains the record of the v3 render. Backup: `BEAT-PLATE-LEDGER-v3.md.bak-1646`. QC: `build_rough_v3/QC_v3b.md`.

## Rev 3b — final in/outs (as built)

Times are cut seconds at 30 fps. Source: `build_rough_v3/logs_v3b/beat_*.json`.

| Beat | VO line(s) | Plate | In–out (s) | Len (s) | Motion | FX | Scale (out px / plate px) |
|---|---|---|---|---|---|---|---|
| h01 | Elizabeth Báthory was accused of / burning young maids with hot irons. | `h01_heated_iron_threat.png` | 0.000–3.967 | 3.967 | 1.5× face open, smoothstep tilt-down to iron | fx_candle(candle3), torch_v1c(torch1) | 1.500 |
| h02 | Of forcing others into freezing water. | `h02_freezing_water.png` | 3.967–6.333 | 2.367 | push 1.00→1.06 | snow_v1b(h02_snow_v3b, 61.9 flakes/f), smoke_v2 breath≤0.22 (right, off faces), water_v1 hem-drip glints (11781 px, 60 sites) | 1.217 |
| b06 | People said young women / were dying in her household. / The rumours reached the king. | `b06_rumours_village.png` | 6.333–11.300 | 4.967 | push 1.00→1.06 | dust_v1 | 1.217 |
| b07 | He sent Hungary's highest official, / György Thurzó, to investigate. | `b07_thurzo_ordered.png` | 11.300–15.867 | 4.567 | push 1.00→1.06 | fx_candle(candle1), smoke_v2≤0.35 | 1.217 |
| b04 | One December night, / armed men arrived at her manor. | `b04_riders_at_the_manor.png` | 15.867–19.667 | 3.800 | push 1.00→1.06 | torch_v1c(torch1,window6), smoke_v2≤0.40 | 1.217 |
| b05 | Báthory was eating supper. | `b05_supper_manor.png` | 19.667–22.200 | 2.533 | push 1.00→1.06 | fx_candle(candle3), torch_v1c(offscreen1), smoke_v2≤0.30 | 1.217 |
| h03 | Thurzó wrote that his men had found / one girl dead and another dying. | `h03_thurzo_claimed_finding.png` | 22.200–26.867 | 4.667 | push 1.00→1.06 | torch_v1c(torch1) | 1.219 |
| b12 | Báthory was taken to the / fortress above her home. | `b12_taken_up_to_fortress.png` | 26.867–30.033 | 3.167 | push 1.00→1.06 | torch_v1c(torch4,window1), smoke_v2≤0.35, snow_v1b(b12, 154.1 flakes/f) | 1.219 |
| b01a_v1 | Four servants, / three women and a young man, / were arrested as her alleged accomplices. / Under torture, they confessed / to dozens of killings. / Three were executed within days. | `b01a_bytca_led_away_v1.png` | 30.033–42.433 | 12.400 | push 1.00→1.06 | snow_v1b(snow_b01a_v1, 140.9 flakes/f) | 1.219 |
| b01b | But Báthory was never tried. | `b01b_never_tried.png` | 42.433–45.200 | 2.767 | push 1.00→1.06 | fx_candle(candle1), smoke_v2≤0.35 | 1.217 |
| b17 | Nothing was ever proven / against her in court. / The case rested on witness testimony, / and much of it was hearsay. | `b17_secondhand_witnesses.png` | 45.200–52.933 | 7.733 | push 1.00→1.06 | torch_v1c(torch1), smoke_v2≤0.40, snow_v1b(b17, 100.9 flakes/f) | 1.219 |
| b13a | The king pressed for a trial. | `b13a_doors_open.png` | 52.933–55.500 | 2.567 | flat (static) | fx_candle(candle5) | 1.189 |
| b13b | Thurzó prevented it. | `b13b_doors_shut.png` | 55.500–58.033 | 2.533 | static, registered to B13a | — | 1.218 |
| b08 | Thurzó had fought the / Ottomans beside her husband. / Ferenc's dying wish was that / his friend watch over her. | `b08_husbands_letter.png` | 58.033–65.267 | 7.233 | push 1.00→1.06 | fx_candle(candle1), smoke_v2≤0.35 | 1.219 |
| b14 | Many historians think he confined her quietly | `b14_why_window.png` | 65.267–68.300 | 3.033 | push 1.00→1.06 | dust_v1 | 1.218 |
| b16 | rather than risk her beheading / and the family's lands. | `b16_family_silence.png` | 68.300–71.967 | 3.667 | push 1.00→1.06 | torch_v1c(torch1), smoke_v2≤0.35 | 1.218 |
| b18 | She died in confinement. | `b18_empty_room.png` | 71.967–74.533 | 2.567 | push 1.00→1.06 | smoke_v2≤0.35, dust_v1 | 1.219 |
| h04a | Then someone added the detail / that would make her infamous. / A century later, / a priest wrote that she bathed / in murdered girls' blood / to keep her beauty. | `h04a_priest_writes_legend_inkgraded_v3b.png` | 74.533–84.533 | 10.000 | push 1.00→1.06 | fx_candle(candle5) | 1.217 |
| b15 | No witness against her had described that. | `b15_thurzo_depositions.png` | 84.533–87.333 | 2.800 | push 1.00→1.06 | fx_candle(candle1) | 1.219 |
| h04b | No court ever heard her. / But the legend had its monster: / the Blood Countess. / History remembers the victors. / We remember the rest. | `h04b_final_stare.png` | 87.333–101.500 | 14.167 | push 1.00→1.06 to the eyes by tagline, then hold | fx_candle(candle3) | 1.217 |

**Rev 3b decisions**
- **B01a CUT.** B01a_v1 carries the servants, confession and execution lines (12.4 s, same snow, no repaint). B17 is unchanged, on the hearsay lines. The execution line was not moved to B17 because B17 follows B01b in the locked order. Alternative: put B17 ahead of B01b.
- **Pauses reopened from the raw VO gaps.** Every plate is ≥2.53 s except H02 (2.367 s, the agreed short slot). "Never tried" gets a ~1.0 s held beat on B01b.
- **H04a** uses the second derived ink copy, `build_rough_v3/h04a_priest_writes_legend_inkgraded_v3b.png` (md5 2de02592…). The table-edge red drips are graded to ink. The source plate is untouched.
- **H02 replaced by the owner at 16:49 EDT.** The new KEEP plate is `h02_freezing_water.png`, md5 adf6966b498d4ed4fb4cb60cc4cb6e05, 3,131,033 B. The pour plate is now `_v2` and the tub plate `_v1`; neither was touched. See the updated H02 row in the Ledger below. Never the cover or thumbnail.

> **Rev 3 — FINAL for Rough v3 (16:24 EDT).** The table directly below is the as-built cut, `renders/bathory_rough_v3.mp4` (97.5 s). Everything after it is the pre-L11 planning ledger, kept for the record, and its times are **superseded**; the stale H02 row has been corrected in place. Backup: `BEAT-PLATE-LEDGER-v3.md.bak-1624`.

## Rev 3 — final in/outs (as built)

Times are cut seconds at 30 fps. Scale is output px per plate px; the house limit is ≤1.5. Source: `build_rough_v3/logs/beat_*.json` and `logs/beat_table.json`.

| Beat | VO line(s) | Plate | In–out (s) | Motion | FX | Scale (out px / plate px) |
|---|---|---|---|---|---|---|
| h01 | Elizabeth Báthory was accused of / burning young maids with hot irons. | `h01_heated_iron_threat.png` | 0.000–3.967 | 1.5× face open, smoothstep tilt-down to iron 0.6–3.4 s | fx_candle(candle3), torch_v1c(torch1) | 1.500 |
| h02 | Of forcing others into freezing water. | `h02_freezing_water.png` at the time; it is now `h02_freezing_water_v2.png` (pour, 20bfe504…) | 3.967–6.333 | full-frame push 1.00→1.06 | smoke_v2 steam≤0.30, water_v1 glints (77140 px) | 1.217 |
| b06 | People said young women / were dying in her household. / The rumours reached the king. | `b06_rumours_village.png` | 6.333–11.300 | push 1.00→1.06 | dust_v1 | 1.217 |
| b07 | He sent Hungary's highest official, / György Thurzó, to investigate. | `b07_thurzo_ordered.png` | 11.300–15.800 | push 1.00→1.06 | fx_candle(candle1), smoke_v2≤0.35 | 1.217 |
| b04 | One December night, / armed men arrived at her manor. | `b04_riders_at_the_manor.png` | 15.800–19.567 | push 1.00→1.06 | torch_v1c(torch1,window6), smoke_v2≤0.40 | 1.217 |
| b05 | Báthory was eating supper. | `b05_supper_manor.png` | 19.567–21.667 | push 1.00→1.06 | fx_candle(candle3), torch_v1c(offscreen1), smoke_v2≤0.30 | 1.217 |
| h03 | Thurzó wrote that his men had found / one girl dead and another dying. | `h03_thurzo_claimed_finding.png` | 21.667–26.233 | push 1.00→1.06 | torch_v1c(torch1) | 1.219 |
| b12 | Báthory was taken to the / fortress above her home. | `b12_taken_up_to_fortress.png` | 26.233–29.400 | push 1.00→1.06 | torch_v1c(torch4,window1), smoke_v2≤0.35, snow_v1b(b12, 154 flakes/f) | 1.219 |
| b01a_v1 | Four servants, / three women and a young man, / were arrested as her alleged accomplices. | `b01a_bytca_led_away_v1.png` | 29.400–35.200 | push 1.00→1.06 | snow_v1b(/workspace/posterity/standalones/bathory/v3/build_rough_v3/snow_b01a_v1.json, 143 flakes/f) | 1.219 |
| b01a | Under torture, they confessed / to dozens of killings. / Three were executed within days. | `b01a_bytca_led_away.png` | 35.200–41.667 | push 1.00→1.06 | torch_v1c(torch1), snow_v1b(/workspace/posterity/standalones/bathory/v3/build_rough_v3/snow_b01a.json, 100 flakes/f) | 1.217 |
| b01b | But Báthory was never tried. | `b01b_never_tried.png` | 41.667–43.767 | push 1.00→1.06 | fx_candle(candle1), smoke_v2≤0.35 | 1.217 |
| b17 | Nothing was ever proven / against her in court. / The case rested on witness testimony, / and much of it was hearsay. | `b17_secondhand_witnesses.png` | 43.767–51.300 | push 1.00→1.06 | torch_v1c(torch1), smoke_v2≤0.40, snow_v1b(b17, 101 flakes/f) | 1.219 |
| b13a | The king pressed for a trial. | `b13a_doors_open.png` | 51.300–53.400 | flat (static) | fx_candle(candle5) | 1.189 |
| b13b | Thurzó prevented it. | `b13b_doors_shut.png` | 53.400–55.300 | static, registered to B13a (sign −1) | — | 1.218 |
| b08 | Thurzó had fought the / Ottomans beside her husband. / Ferenc's dying wish was that / his friend watch over her. | `b08_husbands_letter.png` | 55.300–62.433 | push 1.00→1.06 | fx_candle(candle1), smoke_v2≤0.35 | 1.219 |
| b14 | Many historians think he confined her quietly | `b14_why_window.png` | 62.433–65.467 | push 1.00→1.06 | dust_v1 | 1.218 |
| b16 | rather than risk her beheading / and the family's lands. | `b16_family_silence.png` | 65.467–69.033 | push 1.00→1.06 | torch_v1c(torch1), smoke_v2≤0.35 | 1.218 |
| b18 | She died in confinement. | `b18_empty_room.png` | 69.033–71.067 | push 1.00→1.06 | smoke_v2≤0.35, dust_v1 | 1.219 |
| h04a | Then someone added the detail / that would make her infamous. / A century later, / a priest wrote that she bathed / in murdered girls' blood / to keep her beauty. | `h04a_priest_writes_legend_inkgraded.png` | 71.067–80.933 | push 1.00→1.06 | fx_candle(candle5) | 1.217 |
| b15 | No witness against her had described that. | `b15_thurzo_depositions.png` | 80.933–83.700 | push 1.00→1.06 | fx_candle(candle1) | 1.219 |
| h04b | No court ever heard her. / But the legend had its monster: / the Blood Countess. / History remembers the victors. / We remember the rest. | `h04b_final_stare.png` | 83.700–97.500 | push 1.00→1.06 to the eyes by 90.2 s, then hold under tagline | fx_candle(candle3) | 1.217 |

**Rev 3 decisions**
- **B10 DROPPED** (read as a victim), so V08 runs on B01a only. B10_v1 and B09 are unused.
- **B08 USED** (55.3–62.4) for the Thurzó/husband line; this revival is now built into the cut. **B16 USED** (65.5–69.0) for "rather than risk her beheading and the family's lands."
- **H04a** uses the ink-graded derived copy `build_rough_v3/h04a_priest_writes_legend_inkgraded.png` (md5 438bbd47…). The source plate is untouched.
- **H04b** is the closer: a push to the eyes, holding under the tagline. **Outro plate OMITTED**; the tagline is a standard caption on H04b.
- **depth_v1 is used nowhere.** B13a is flat (static); B13b is registered to B13a.
- Still CUT: B02, B03, B19a/b, B20, b11 (both), b13_diff.

**Motion and effect locks**, used in every row:
- **F** is a flat 2D push, 1.00→1.06. **D** is depth_v1, opt-in only, and never where it would deform anatomy.
- **torch_v1c** only on real painted torches, braziers and hearths.
- **fx_candle** for candles.
- smoke_v2 at ≤0.4 · dust_v1 · snow_v1b (frost or snow).
- **Depth-safe** means architecture or landscape only, with no figures in the parallax layers. A bare "no" means a figure's anatomy would warp.

## Ledger

| Beat · time | VO (quoted) | Mvt | Owner line | Candidate plate | Status | Why | Motion / effects | Depth-safe | Notes for NEEDS-NEW |
|---|---|---|---|---|---|---|---|---|---|
| **V01** 0.0–6.6 | "Elizabeth Báthory was accused of burning young women in her service with hot irons. Of forcing others into freezing water." | M1 | L01 | **H01** `v2/plates/h01_heated_iron_threat.png` (≈0–4.4 s; also the opening frame) · md5 `062343feeaead44464eb3d0034332ae3` · **941×1672** | **KEEP** | The allegation made visible but attributed. The maid (headscarf, red shawl) kneels by a stone wall, looking up in fear. Báthory is at right in a brocade gown, hand at her side. A two-pronged iron heats in a brazier at the bottom-left. A three-candle stand sits by the window. No contact, no injury. | **Opener:** start on the face crop (below), then a **pull-back or tilt down** to the full frame over about 2–3 s to reveal the iron. A push-*in* cannot reveal it: the iron sits at the bottom of the frame. torch_v1c on the brazier (a real fire; mask the face and hands out). fx_candle on the three candles. No smoke over her face. | **no** (close figures) | **Opener crop check: PASS with a crop.** In full-res pixels, the iron and brazier fire sit at y≈1160–1520 (x≈0–560), and flame tips at the left edge reach y≈840–1040. **The 9:16 crop box (60,120)–(611,1100), 551×980, excludes the iron and the brazier** and keeps the face (y≈300–540) and the candles. That is a 1.71× zoom, i.e. about 1.96× upscale to 1080×1920, so check for softness. A plain top-half crop also works (the iron is entirely in the bottom 30%). Flags: **(a) the plate is 941×1672, not the 1080×1920 promised;** (b) the iron is long-handled, curling-tong-like pincers. That reads as "heated iron", but it is borderline against "small handheld, not a poker". Owner eye. |
| V01 (cont.) **3.967–6.333** (final, v3 and v3b) | "Of forcing others into freezing water." | M1 | L01 | **H02 (KEEP plate, replaced again 16:49 EDT, used in v3b)** `v2/plates/h02_freezing_water.png` · md5 `adf6966b498d4ed4fb4cb60cc4cb6e05` · **3,131,033 B** · 941×1672 | **KEEP / USED in v3b** (never the opener, cover or thumbnail) | The second alleged method. She kneels alone in the snowy courtyard, soaked, in an opaque dark dress, hands clasped, eyes shut; two women stand back with buckets; the lit manor is behind. | Full-frame F push 1.00→1.06 (density 1.217). Only three things move, each matted: **snow_v1b** (`build_rough_v3/snow_h02_v3b.json`; all 3 figures are subjects, faces are masked, the ground is land with gain 0), **smoke_v2** breath steam on the right (1 haze emitter, opacity 0.22, off faces, hands and figure), and **water_v1** glints on the hem drips and their ripple pools (11,781 px allow mask). Faces, hands, figures and the dress body stay still. | **no** | Proofs PASS (`build_rough_v3/logs_v3b/h02_water_proof.json`, `h02_snow_proof.json`, `h02_combined_proof_v3b.json`): faces 0 px, outside-allow 0 px, figure body (excluding drip strands) 0 px, snow keep-out 0 px, and output-space figure matte 0 px at all sample times. Flag: 941×1672, not 1080×1920. *Previous plates, untouched:* `h02_freezing_water_v2.png` (pour, 20bfe504…, 3,027,591 B; used in the v3 render with steam and stream glints) and `h02_freezing_water_v1.png` (tub, 19c5212c…, 2,734,547 B). |
| **V02** 6.6–11.2 | "People said young women were dying in her household. The rumours reached the king." | M1 | L02 | `b06_rumours_village.png` | KEEP-candidate | Whispers spread: the hinge from allegation to the crown. | F + dust_v1 in the low-sun band | no (three women in the foreground) | Scriptor also wants "a dispatch reaching the royal court". There's no plate for it; B06 covers the beat. Optional new plate, not required. |
| **V03** 11.2–15.2 | "He sent Hungary's highest official, György Thurzó, to investigate." | M2 | L03 | `b07_thurzo_ordered.png` | KEEP-candidate | Thurzó receives the order: opens the investigation. | F + fx_candle (iron stand) | no (figure) | — |
| **V04** 15.2–19.4 | "One December night, armed men arrived at her manor." | M2 | L04 | `b04_riders_at_the_manor.png` | KEEP-candidate | The intrusion begins. | **Depth OFF** (owner). **Full-frame F push** + torch_v1c (torch) + smoke_v2 0.4 + window-glow pulse. | no (ruled off; walking retainers) | — |
| V04 (cont.) 19.4–21.6 | "Báthory was eating supper." | M2 | L04 | `b05_supper_manor.png` | KEEP-candidate | Matches the documented detail (arrest 29 Dec 1610, during supper). | F + fx_candle (three-branch candlestick) + offscreen torch pulse at the door | no | — |
| V04 (alt or insert) | (as above) | M2 | L04 | `b09_arrest.png` | KEEP-candidate | Torch-bearing armed men in her doorway: the intrusion made physical. Use it if V04 is split three ways after the lock, or as the thumbnail or opener alternate. | **F recommended.** v2 used D; depth on her figure and the doorway men warps anatomy. torch_v1c on the doorway torches + fx_candle | **no** (flag) | — |
| **V05** 21.6–26.8 | "Thurzó wrote that his men had found one girl dead and another dying of her wounds." | M2 | L05 (owner's "later claimed / gravely wounded" became L05) | **H03** manor aftermath | NEEDS-NEW | The attributed finding. No v2 plate fits (v2 avoided it). | F. torch_v1c only on torches actually painted in the men's hands. fx_candle if there's a candle. | **no** | **Inside the manor.** One girl dead (covered by a cloth) and one dying (being tended), per Thurzó's letter of 30 Dec 1610, so it is *attributed*. Ominous and non-graphic. **No dungeon, no hallway body, no rows of bodies, no clean-up.** **Native 1080×1920.** |
| **V06** 26.8–30.1 | "Báthory was taken to the fortress above her home." | M2 | L06 | `b12_taken_up_to_fortress.png` | KEEP-candidate | Torches climbing to Csejte: closes M2. | F + torch_v1c ×4 (switchback torches) + smoke_v2 ≤0.4 + snow_v1b | yes in principle (land and architecture only; the torch figures are tiny). Kept F to protect the torch flames. | — |
| **V07** 30.1–35.9 | "Four of her servants, three women and a young man, were arrested as her alleged accomplices." | M3 | L07 | `b01a_bytca_led_away_v1.png` | KEEP-candidate (primary) | Three women in headscarves and a young man, seen from behind and under guard: exactly the VO's count, in servants' dress. | F + snow_v1b | no (figures) | It is set at Bytča, not the arrest itself. Archivist C3 has them sent under guard. Acceptable as the "taken" image. Option, not required: a new plate of the arrest at the manor with distinct figures. **Differentiate them from the victims by dress, role and staging, not by age.** Scriptor's updated beat sheet agrees: "plain working dress, visibly distinct from the young maids. No age implied." |
| V07 (alt) | (as above) | M3 | L07 | `b10_bytca_transfer_v1.png` | KEEP-candidate (alt) | The covered cart and four servants under guard, from behind. | F + snow_v1b | no | Pick one of the two v1 variants for V07. |
| **V08** 35.9–39.4 | "Under torture, they confessed to dozens of killings." | M3 | L08 | `b10_bytca_transfer.png` (current, the interrogation) | KEEP-candidate (**decide at assembly**) | The interrogation (2 Jan 1611) by an official and a notary. | F + fx_candle + dust_v1 | no | **Rule:** the bound woman must read as an **accused servant, not a victim**: plain working dress, older working-servant styling, in contrast with the V01/H02 maids. Decide at assembly, side by side with H01/H02. If she still reads as a victim, drop B10 and run V08 on B01a only (≈6.5 s), or regrade or mask her. |
| V08 (cont.) 39.4–42.4 | "Three were executed within days." | M3 | L08 (ruling: "within days") | `b01a_bytca_led_away.png` (current, owner redo) | KEEP-candidate | The execution prelude at Bytča (7 Jan 1611, winter). **No burning shown.** | F + torch_v1c (brazier) + snow_v1b | **no** (kneeling figure, sword) | — |
| **V09** 42.4–44.9 (+pause) | "But Báthory was never tried." | M3 | L09 | `b01b_never_tried.png` | KEEP-candidate | The reversal's hinge: alone by candle; hold for the pause. | F + fx_candle | no (seated figure) | If B01b is used as the cold-open fallback, this becomes a reuse. Avoid that: see the cold-open row. |
| **V10** 44.9–49.3 | "The king pressed for a trial. Thurzó prevented it." | M3 | L10 (owner's wording restored) | `b13a_doors_open.png` → `b13b_doors_shut.png` | KEEP-candidate ×2 | The doors shut on the trial. | B13a: D *conditional* (the silhouette is rigid, from behind; clear it with a frame check) else F. B13b: F + fx_candle (candle line) | B13a conditional · B13b no | — |
| **V11** ≈49.3–(≈58+, re-time) (**L11b PENDING**) | **L11 owner-decided, now being extended by ≈8–12 words (L11b pending).** Current locked file (224 words): "Her dying husband had asked Thurzó to watch over her. Many historians think he confined her quietly rather than risk her beheading and the family's lands. And many witnesses could only repeat what they had heard." | M3 | L11 (owner rewrite) | (a) **Husband's request / Thurzó:** `b08_husbands_letter.png`, **UNDER REVIEW by the parent (revival of a mandatory CUT; needs the owner's explicit sign-off).** Alternate without reinstating it: `b07_thurzo_ordered.png` (Thurzó reading a letter by candle) as a reuse from V03. (b) **"confined her quietly":** `b13b_doors_shut.png` (from V10, reuse) or B14. (c) **Hearsay:** `b17_secondhand_witnesses.png`. | B17 KEEP-candidate · B08 UNDER REVIEW · B16 **at risk** | The beat is no longer the family's silence. It is Nádasdy's deathbed request and Thurzó's quiet confinement, then the hearsay. | B08: F + fx_candle (candle), with the hand and sabre kept still, depth no. B17 as before. | no | **B16 (family at the hearth) no longer matches the VO.** It becomes CUT unless L11b reintroduces the family. "Many historians think" must stay attributed on screen: never state the motive as fact. Possible NEEDS-NEW if B08 is refused: Nádasdy's deathbed with Thurzó at the bedside (the husband died in 1604). |
| **V12** 55.7–58.1 | "She died in confinement." | M3 | L12 | `b18_empty_room.png` | KEEP-candidate | The empty fortress room with a snuffed candle: ends M3. | F default. smoke_v2 wick thread ≤0.4 + dust_v1 window shaft | **yes** (architecture only) | — |
| V12 (alt) | (as above) | M3 | L12 | `b14_why_window.png` | KEEP-candidate (alt) | Báthory at the window, a cold shaft of light. Use it if V12 needs her presence before the empty room. | F + dust_v1 shaft | no (figure) | — |
| **V13** 58.1–69.4 | "Then someone added the detail that would make her infamous. More than a century after her death, a priest wrote that she bathed in murdered girls' blood to keep her beauty." | M4 | L13–L14 (owner's L13a softened) | **H04a**, Turóczi writing (a separate plate) | NEEDS-NEW | The legend's author. Opens M4. | F slow push onto the page + **fx_candle** (the priest's candle or lamp) | **no** (figure) | **Turóczi, a Jesuit in period black, writing in 1729.** A Latin page, **no readable title** on screen. "To keep her beauty" is the motive, carried in the VO. **No blood-bath image** (the updated beat sheet agrees). The priest and Báthory are never in the same room. **Native 1080×1920.** |
| **V14** 69.4–72.3 | "No witness against her had described that." | M4 | L15 | `b15_thurzo_depositions.png` | KEEP-candidate | Back to the 1610–11 testimony. | F + fx_candle | no (figure) | Notes and captions must **not** say "no bath of any kind": the 1611 transcript mentions an herbal-water bath. The updated beat sheet agrees: no visual claim that no bath of any kind was mentioned. |
| **V15** 72.3–79.9 | "No court ever heard her. But the legend had its monster: the Blood Countess." | M4 | L16 ("No court ever heard her", ruling) + L17 | **H04b**, the final stare as portrait or memory (a separate plate) | NEEDS-NEW | The closing reveal of the owner's H04 brief. | **Separate plates:** H04a (V13) → B15 (V14) → H04b (V15). F slow push onto the eyes; fx_candle only if a candle is painted. | **no** (face) | **Her stare is a portrait or memory, never her alive in the room.** Same restraint as V13. **Not exoneration:** guilt is left unresolved, and nothing implies the deaths were fabricated; only the blood bath is legend. **Native 1080×1920.** It can double as the thumbnail. |
| **Outro** 79.9–≈88 | "History remembers the victors. We remember the rest." | — | L18 (tagline) | `outro_bathory_csejte_first_light_OWNER.png` | KEEP-candidate | House outro. | F 1.00→1.06 (or a static OutroHold) + dust_v1 first-light motes | yes (ruin and land) | **Flag:** the baked wordmark and tagline would duplicate a burned-in caption of L18. Suppress the caption there. |
| — | — | none | — | `b02_bathory_erzsebet_2_commons.jpg` (archival, B02) | **CUT** | Mandatory (archival portrait). | — | — | — |
| — | — | none | — | B19b, REUSE of archival B02 | **CUT** | Mandatory (archival, and a B19 reuse). | — | — | — |
| — | — | none | — | B19a, REUSE of B11 | **CUT** | Mandatory (all B19 reuses). | — | — | — |
| — | — | none | — | `b03_atlas_upper_hungary_CLEAN.png` | **CUT** | Mandatory (the B03 map). | — | — | — |
| V11 (proposed) | L11 husband/Thurzó clause | M3 | L11 | `b08_husbands_letter.png` | **UNDER REVIEW (revival)** | It was a mandatory CUT (the Thurzó/husband backstory). The new L11 puts that backstory back in the VO, so the parent is reviving B08 for the L11 beat and is checking it personally. The ledger does **not** count it as KEEP until that check is done and the owner signs off on reversing the cut. | F + fx_candle; keep the hand and sabre static. | no | **Flag:** this reverses an earlier mandatory cut. |
| — | — | none | — | `b11_bytca_door_shut_v1.png` (empty courtyard, shut door) | **CUT** | Serves no movement. Redundant with B13b's shut doors. | — | — | — |
| — | — | (M3) | — | `b11_bytca_door_shut.png` (current: covered body on a bier, blood in the snow) | **CUT** | Made redundant by **H03**: a second covered body would blur victim and executed servant. The restrained blood in the snow is a gore risk. V08 is covered by B10 and B01a. | — | no | Fallback for "executed" only if B01a fails review. |
| — | — | (M4) | — | `b20_closing_eyes.png` | **CUT** | Made redundant by **H04b**, the owner's final stare. Keep the file as a fallback and as a source for the thumbnail or the H04b reference. | (v2: D by owner direction) | no (face) | — |
| — | — | none | — | `b13_diff.png` | **CUT** | Diagnostic difference image, not a plate. | — | — | — |

## Counts

**By status (Rev 2).** 21 KEEP-candidates, 3 NEEDS-NEW, 8 CUT and 1 UNDER REVIEW, 33 in all.
- **KEEP-candidate (21):** H01, H02 (both on disk at 941×1672/1671), B06, B07, B04, B05, B09, B12, B01a_v1, B10_v1, B10, B01a, B01b, B13a, B13b, B16 (**at risk**: no longer matches the new L11), B17, B18, B14, B15, Outro.
- **UNDER REVIEW (1):** B08 (revival for L11; the parent is checking it).
- *Rev 1 line, superseded:* 19 KEEP-candidates, 5 NEEDS-NEW and 9 CUT; KEEP-candidates: B06, B07, B04, B05, B09, B12, B01a_v1, B10_v1, B10, B01a, B01b, B13a, B13b, B16, B17, B18, B14, B15, Outro. That includes three alternates (B09, B10_v1, B14). The likely cut uses 16; it drops to 15 if B10 fails the assembly check, and L11 may remove one of B16/B17.
- **NEEDS-NEW (3):** H03, H04a, H04b. (H01 and H02 were delivered at 15:41–15:42 EDT.) H04a and H04b are separate plates. The safe opening frame is part of the H01 commission.
- **CUT (8; B08 moved to UNDER REVIEW):**
  - B02 (archival)
  - B19b (archival reuse)
  - B19a (reuse)
  - B03 (map)
  - b11_v1 (serves no movement)
  - b11 current (redundant with H03)
  - B20 (redundant with H04b)
  - b13_diff (diagnostic)

**Per movement:**

| Movement | KEEP-candidate | NEEDS-NEW | CUT | Beats |
|---|---|---|---|---|
| M1 Accusation | 3 (H01, H02, B06) | 0 | 0 | V01–V02 |
| M2 Investigation/intrusion | 5 (B07, B04, B05, B09, B12) | 1 (H03) | 0 | V03–V06 |
| M3 Reversal | 11 (B01a_v1, B10_v1, B10, B01a, B01b, B13a, B13b, B16 at risk, B17, B18, B14) + B08 under review | 0 | 1 (b11 current) | V07–V12 |
| M4 Final revelation | 1 (B15) | 2 (H04a, H04b) | 1 (B20) | V13–V15 |
| Outro | 1 | 0 | 0 | tagline |
| No movement | — | — | 6 (B02, B19b, B19a, B03, b11_v1, b13_diff) | — |

**Balance flag.** M3 is plate-rich (11 candidates for about 28 s), while M1 and M4 lean on the new H-plates. M1 is now covered (H01, H02, B06). If H04a or H04b slips, M4 has only B15. Neither can carry its movement alone.

## Opener and thumbnail

- **Opening frame:** H01's first frame, the **maid's face only**, with the iron revealed on the push. Per the updated beat sheet, there is no fallback reuse.
- **Thumbnail:** the H04b stare once made. Until then, B20 (thumbnail use only, as it is CUT from the cut) or B09. **Never H01 or H02.**

## Flags

1. **Native size.** All v2 plates are **≈941×1672**, not 1080×1920, so each needs a ~1.15× upscale. Check density, especially for the F push on B04 (full frame). The **H-plates are 1080×1920 native**, so watch for a sharpness mismatch where they cut against the v2 plates.
2. **B10 (current).** The bound woman must read as an accused servant, not a victim. **Decide at assembly** (see V08).
3. **b11 (current).** Restrained blood in the snow; it is CUT. If it's ever reinstated, it needs a gore review.
4. **L11 pending revision.** Every time from V11 on shifts by the change in L11's length. Re-time the ledger and `SCORE-LOCK-v3.md`, and re-record Oliver once L11 is relocked. Scriptor's earlier beat-sheet conflicts (V07 age, V13 bath image, V14 "no bath anywhere") are **resolved** in the updated `script-v3.md`.
5. **Sentence-level guardrails.** Never imply the deaths were fabricated. Guilt stays unresolved; only the blood bath is legend. The family motive is never stated as fact. No hallway body, dungeon clean-up, walling-up, dwarf or Darvulia. No burning shown.
6. **Outro.** The baked tagline duplicates the caption.
7. **Torch and candle masks.** In B12, B16 and B17, keep face exclusions on all torch_v1c masks, as in v2.
8. **Disk.** The volume is at **57%** (72 G used of 128 G, 56 G free), not 95%.

## Rev 2 notes (15:50 EDT)
- **Timings are still pre-L11.** The new 224-word L11 adds about 19 words, and L11b adds about 8–12 more, so ≈+27–31 words, roughly +9–11 s at Oliver's pace. That likely pushes the VO from ≈84.9 s to ≈94–96 s, **past the ≈88 s Shorts budget**. Re-time V11–V15 after the L11b read.
- **No re-voice or refit has been done.** The 224-word read was stopped before any audio was written (`vo/` holds only the render script and an empty log). `SCORE-LOCK-v3.md` is unchanged, still on pre-L11 timings.
- **The H-plate size, 941×1672, disagrees with the 1080×1920 promised in Rev 1.** Both H01 and H02 need upscaling, the same as the v2 plates.
