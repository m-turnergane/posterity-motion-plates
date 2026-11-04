# Báthory · Rough v3 · QC (16:26 EDT, 31 Oct 2026)

## Deliverable
- **Render:** `v3/renders/bathory_rough_v3.mp4`, md5 `7efd3c476188310c3bd282d884e8498b`, 101.3 MB
- **Probe:** H.264 High, 1080×1920, yuv420p, 30 fps, 2,925 frames; AAC-LC 48 kHz stereo; **97.500 s**
- **Loudness (render AAC):** **-14.1 LUFS integrated, -4.3 dBTP**, LRA 3.2 LU. Spec: −14 LUFS, ≤−1 dBTP. **PASS**
- **Mix:** `v3/vo/mix_v3_final.mp3`, md5 `7d519a99a194913ebe78ea76cd885c78`: -14.1 LUFS / -4.3 dBTP (wav -14.1 / -4.4). Master iterations: 0.0 dB → -24.7, 10.7 dB → -14.5, 11.2 dB → -14.2, 11.4 dB → -14.1
- **Black or freeze:** blackdetect (≥0.1 s) found nothing; freezedetect (≥2.5 s) found nothing.
- **Captions:** `bathory_rough_v3_captions.ass`, burned in, 48 events. The joined text equals the VO script (asserted at build). Every line is ≤7 words and ≤24 characters, 1–2 lines; overlong list empty. Plain white house style.
- **Contact sheet:** `bathory_rough_v3_contact_sheet.jpg` (21 beats, one frame each, with the burned caption)

## VO
- **Script:** `raw/script-vo-v3.txt`, md5 9db405e1fe6a02f5ec12626dd541db41, 230 words (verified before the read)
- **Raw:** `vo/vo_oliver_v3_final.mp3`, 98.13 s, md5 e98f76b4ef019b99ea15a8cdb0e01a11
- **Tight:** `vo/vo_oliver_v3_final_tight.mp3`, 94.85 s, md5 838e07d45efb06298df929a3718c9691. 3.28 s was removed over 18 gaps, with a 0.47 s cap.
- **ASR check of the tight read:** ratio 0.9915. The only differences are the spellings rumours→rumors and girls'→girl's, so no words are missing or added.

## Score and mix (detail in `SCORE-LOCK-v3.md`, Rev 3)
- **Bed:** Anabasis I, track 256.0–294.25 crossfaded (2.5 s qsin at cut 37.0) into 281.75–343.5, so 10 s of the flat plateau repeats.
- **Priest line** at track 321.2–326.6, on the swell. **"Blood Countess"** at track 334.3, with a −3 dB ease from 85.38 to 88.19.
- **L13 fix:** extra −3.5 dB duck plus a 2 kHz −3 dB Q1 dip, with the ramp at 68.54–69.54.
- **Ducking:** bed calibrated to VO −12 LU, sidechain duck 0.035/2.5/15/700/4.

## Per-beat table
| Beat | VO line(s) | Plate | In–out (s) | Motion | FX | Scale (out px / plate px) |
|---|---|---|---|---|---|---|
| h01 | Elizabeth Báthory was accused of / burning young maids with hot irons. | `h01_heated_iron_threat.png` | 0.000–3.967 | 1.5× face open, smoothstep tilt-down to iron 0.6–3.4 s | fx_candle(candle3), torch_v1c(torch1) | 1.500 |
| h02 | Of forcing others into freezing water. | `h02_freezing_water.png` | 3.967–6.333 | full-frame push 1.00→1.06 | smoke_v2 steam≤0.30, water_v1 glints (77140 px) | 1.217 |
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

## Proofs
- **H02 water_v1:** 19530 impulses, leaked px total **0**, protect changed px [0, 0, 0, 0, 0, 0, 0]. allow changed px [20215, 20079, 19500, 21613, 19212, 24040, 22076] (≈1.2–1.5% of the frame). pass_impulse_0px=True, pass_protect_0px=True
- **H02 combined (glints plus steam):** face changed px [0, 0, 0, 0], outside-allow changed px [0, 0, 0, 0]. **PASS**
- **H04a ink grade:** derived copy, md5 438bbd47c2653fea63c685f8453a3907, from source d34476996b65667e75f308d01a4ecffe. 16257 px changed inside box (300,1240,540,1410), 0 outside.
- **Guardrails:** pixel density passes on every beat. The maximum is 1.500 on H01, at the limit; all others are 1.189–1.219. H01 fire sharpness lapvar is 119.1, a PASS.

## No-touch verification (md5 against baselines taken before the build)
- **Plates:** 31 files, **all unchanged**. `/workspace/posterity-motion-plates` was not touched.
- **Engines and docs:** 35 files; 34 unchanged. **`v3/ARCHIVIST-CLAIMS-v3.md` changed at 16:03:57 EDT. I did not edit it;** that is the time the corrected script landed, so another agent likely edited it. Flagged.
- **Docs I edited, with backups first:** `SCORE-LOCK-v3.md` → `.bak-1624`, and `BEAT-PLATE-LEDGER-v3.md` → `.bak-1624`.
- The `.216-alt` / `.alt216` files were not used.

## Flags
1. **H01 density is 1.5**, at the house limit (face open at 1.306× crop on a 941×1672 plate).
2. **H03 shows blood on the sheet**, and no visibly "dying" second girl is painted, so the image under-serves "another dying."
3. **H02:** the soaked dress is a platform-sensitivity risk. The water effect is light-only (glints); the water itself does not move. H02 is not the opener or the thumbnail.
4. **H04a** uses the ink-graded derived copy (owner repaint decision). A faint red residue remains on the drips at the table edge (minor).
5. **B10 dropped** (victim-read); V08 runs on B01a.
6. **Second hot area at "Blood Countess"** (bed ≈ −16 short-term); handled by the automated −3 dB ease.
7. **Outro plate omitted.** The tagline is captioned on H04b.
8. **Captions are plain white** house style, with no emphasis styling.
9. **No pause after "tried"** (the tight read keeps a normal gap of about 0.2 s).
10. **All H-plates are 941×1672**, not 1080×1920; each is upscaled about 1.15× on cover.
11. **B13b has no FX.** It is a static, registered door-shut.
12. **True peak is −4.3 dBTP**, well inside spec. The limiter at 0.85 plus the peak compressor leave about 3 dB unused, so loudness could be held with less limiting if wanted.
13. **ARCHIVIST-CLAIMS-v3.md changed during the session**, not by me (see no-touch above).
14. **Length:** 97.5 s total and 94.85 s of VO, over the earlier ≈88 s Shorts budget note but under 3 minutes.
