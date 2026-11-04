# Báthory · Rough v3b QC (Atelier, 31 Oct 2026, 16:58 EDT)

**Render:** `v3/renders/bathory_rough_v3b.mp4`, md5 `63716245833810335c30e382c5503baf`, 109,165,509 B.
H.264 1080×1920 at 30 fps (3045 frames) with AAC audio, **101.500 s**.
**Loudness (render AAC, ebur128):** **−14.1 LUFS** integrated, **−4.2 dBTP**, LRA 3.5 LU. The mix wav measures −14.1 / −4.4 and `vo/mix_v3b_final.mp3` (md5 05effc0d…) measures −14.1 / −4.3.
The v3 render is kept unchanged (`renders/bathory_rough_v3.mp4`). There is only one v3b render.

## Inputs
- **Script:** `raw/script-vo-v3.txt`, md5 9db405e1fe6a02f5ec12626dd541db41 (unchanged). No new ElevenLabs takes were made.
- **VO:** `vo/vo_oliver_v3b.mp3` (md5 4e876418…, 98.854 s). It was retimed from the raw `vo_oliver_v3_final.mp3` (98.128 s) by `vo/retime_v3b.py` (log `vo/retime_v3b_log.json`). The words are sample-identical to the raw read: all 230 words, min corr 0.99999, lag ≤2 samples. Only the gaps changed:

| Gap after | Raw (s) | v3b (s) | Purpose |
|---|---|---|---|
| supper. | 0.603 | 0.93 | open (B05) |
| tried. | 0.441 | 1.12 | ~1.0 s held beat on B01b ("never tried" ends 44.21, cut at 45.20) |
| trial. | 0.603 | 0.90 | open (B13a) |
| it. | 0.511 | 1.12 | open (B13b) |
| confinement. | 0.697 | 0.97 | open (B18) |
| investigate. / dying. / court. | ~0.70 | 0.55 | tighten |
| hearsay. / infamous. / victors. | 0.95 / 1.12 / 1.12 | 0.60 / 0.85 / 0.80 | tighten |

- **ASR check** (`vo/asr_check_v3b.json`, faster-whisper medium.en): 235/235. The only diffs are rumours/rumors, girls'/girl's and detail→"tale". The "detail" word is waveform-identical to the raw (corr 1.0), so that diff is ASR variance, not a VO change.
- **Captions:** `bathory_rough_v3b_captions.ass` (md5 4e29352708…), 48 chunks, none overlong (≤7 words, ≤24 chars per line). The text is asserted equal to the VO words and is identical to v3; only the timings moved.

## Changes vs v3
1. **B01a CUT.** B01a_v1 now carries all three lines: servants, then confession, then executions (30.033–42.433 s, 12.4 s, snow_v1b unchanged, no repaint). B17 is unchanged in content and still carries "Nothing was ever proven… hearsay" (7.733 s). *Why:* B17 sits after B01b in the locked order. Putting the execution line on B17 would mean moving B17 ahead of B01b ("never tried"). That option is listed below as an alternative, but it was not built.
2. **Pauses reopened from the raw gaps.** Every plate is ≥2.53 s except **H02 (2.367 s, the agreed short-slot exception)**. Runtime is 101.5 s (VO 98.854 plus the 2.65 s H04b hold).
3. **H04a ink pass 2.** The derived copy `h04a_priest_writes_legend_inkgraded_v3b.png` (md5 2de025922ede31def045c411fe1c3a1a) is made from the v3 ink copy (438bbd47…) by `h04a_ink_v3b.py` (log `logs_v3b_h04a_inkgrade.json`). Inside the feathered table-edge box (305,1360)–(520,1455), crimson hue <17° with sat >0.25 is tinted to ink at the same luma. Result: 5,967 px changed, 0 outside the box, crimson px 1776→452. The source plate d34476996b… is untouched. In the render frame at 76 s, the table-edge drips now read as dark ink.
4. **H02 rebuilt on the owner's replacement plate (16:49 EDT).** See the H02 section. The h02 clip I had already rendered on the pour plate was discarded and re-rendered before the final, so the v3b render contains only the new plate.
5. **H02 is never the cover or thumbnail.** No cover or thumbnail is attached to the mp4. Frame 0 is H01. H02 appears only as tile 2 of the QC contact sheet.

## H02 (new KEEP plate)
- **Plate:** `v2/plates/h02_freezing_water.png`, md5 **adf6966b498d4ed4fb4cb60cc4cb6e05**, **3,131,033 B**, 941×1672. Content: she kneels alone, soaked, in an opaque dark dress, hands clasped, eyes shut; two women with buckets stand behind. `_v1` (tub, 19c5212c…, 2,734,547 B) and `_v2` (pour, 20bfe504…, 3,027,591 B) were not touched.
- **Framing:** full frame, push 1.00→1.06, centre (0.5, 0.42), 1.217 output px per plate px (≤1.5). The slot length is unchanged at 3.967–6.333 s (2.367 s).
- **Only three things move, each matted:**
  - **snow_v1b**: cfg `snow_h02_v3b.json` (md5 8cdbe77b…, base b12, seed 1202, wind −2, about 62 flakes per frame). All three figures are subjects (girl's shawl and dress; each woman with her bucket), faces are listed by hand and auto-detected, and the ground below the y≈880–1060 line is land with gain 0. So snow falls only over the sky and buildings.
  - **smoke_v2 breath**: one haze emitter at (700,590)–(880,725) on the right, drift +5, **opacity 0.22**, protected off all faces, the hands and the girl's figure (feather 36).
  - **water_v1 hem drips**: glints on 5 painted drip strands below the hem and 3 ripple pools (11,781 px allow mask, 60 glint sites). Faces and hands are protected. `WG.guard('refuse')` passed: 1.217 ≤1.5.
- **Leak proofs (logs_v3b):**
  - `h02_water_proof.json`: pass. protect_changed_px 0 at all 7 times, leaked impulses 0.
  - `h02_snow_proof.json`: pass. keep-out changed 0, outside matte changed 0, deterministic, guardrails ok.
  - `h02_combined_proof_v3b.json`: pass.
    - face_changed_px [0,0,0,0]
    - outside_allow_changed_px [0,0,0,0]
    - figure body changed px, excluding drip strands, [0,0,0,0]
    - output-space full frame (snow + steam + drips, pushed) vs the pushed static plate, inside the figure matte: [0,0,0,0]
- **Visual:** I made a lossless motion map over 15 frames. Changes appear only in the snow in the sky and buildings, the breath plume on the right, and the hem drips and pools. The faces, hands, figures, dress body and ground do not move. In the encoded clip, some h264 chroma noise shows on the bright window reflections; this is encode noise, not motion.

## Score (Anabasis I) — `mix_v3b.py`, log `logs_v3b/mix_log.json`
- Cut t maps to track t+256 for t<38.5, and to t+242.4 after. One 2.5 s qsin crossfade at cut 37.25–39.75: track A 293.25–295.75 × B 279.65–282.15, both inside the flat 275–300 s stretch (chroma sim 0.598, level diff 0.54 dB). The plateau repeats for 13.6 s.
- **Priest line** at cut 78.813 lands on track **321.213**, on the swell (v3 was 321.20).
- **L13 fix** ("She died in confinement.", script line 13; "She" at 72.098): extra −3.5 dB duck plus a 2 kHz −3 dB bell on the bed, ramp 71.498–72.498, then held.
- **Blood Countess ease:** −3 dB ramp 89.041–92.026. "The Blood Countess" at cut 92.176 lands on track 334.576.
- Bed fade 99.0–101.5. Bed at VO −12 LU (−16.5 dB), master +11.4 dB, limiter 0.85.

## Per-beat table (as built; times are cut seconds at 30 fps)

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

Removed vs v3: **b01a**. Still CUT: B02, B03, B19a/b, B20, b11, b13_diff; B10 dropped. depth_v1 is used nowhere. There is no vignette, letterbox, watermark or label.

## Integrity
- All 20 plate md5s in `logs_v3b/beat_*.json` were re-hashed and match. Each equals its v3 md5 except H02 (owner replacement, expected) and H04a (the new v3b derived copy).
- The `.216-alt/.alt216` files were not used. `/workspace/posterity-motion-plates` was not touched.

## Flags
1. **B01a/B17 split:** all three lines are on B01a_v1 (12.4 s), as explained above. Alternative: move B17 ahead of B01b so B17 takes the execution line.
2. **H02 plate swapped by the owner at 16:49 EDT, mid-build.** The H02 clip and proofs were rebuilt on the new plate, then the final was rendered once.
3. **SCORE-LOCK Rev 3 label error:** it says L13 is "Then someone added the detail" at 69.14. In v3, 69.14 was actually "She died in confinement" (script line 13), and the fix sat there. Corrected in the Rev 3b note.
4. **ASR "tale"** for "detail" is ASR variance; the waveform is identical.
5. **H01 density is 1.500**, exactly at the limit (unchanged from v3).
6. `ARCHIVIST-CLAIMS-v3.md` was modified by another agent (mtime 16:43:43 EDT). I did not touch it.
7. True peak is −4.2 dBTP, well under −1. Loudness is on target at −14.1.
