# Edward II v3b — ROUGH v1 build notes (2026-10-29)

**Master:** `/workspace/posterity/renders/posterity-edward-ii-v3b-ROUGH-v1.mp4`. 1080x1920, 30 fps, 92.033 s (2761 f). x264 High yuv420p CRF 16 medium; AAC LC 256k 48 kHz; +faststart. 76,786,790 B, md5 84d0660a56cc3d06f011ebf2ed086023.
**Preview:** `…-ROUGH-v1-preview.mp4`. 720x1280, x264 2.6 Mb/s, with the master's AAC stream copied. 32,341,510 B (32.3 MB), md5 ea4478f288677730996e9794c034221f.
**Loudness (ffmpeg ebur128 on the final files):** master and preview both read **I -14.2 LUFS, true peak -1.7 dBTP**, LRA 2.9 LU. The pre-AAC mix measured -14.1 / -1.9.
**Build script:** `edit/build_rough_edward_ii_v3b_v1.py`, run with `/workspace/mpvenv/bin/python` (needs cv2; system python3 lacks it).
- The script refuses to overwrite the master or preview; use `--tag v2` etc. for a new build.
- Other options: `--title`, `--title-top-pct`, `--test-frames` (stills to /dev/shm/e2qc), `--audio-only`, `--jobs`.
- Scratch goes to `edit/_build_v3b_<tag>/`.
- Pipeline: per-slot CRF-8 clips rendered in parallel → concat → burnt-in ASS → final encode → preview.
- Inputs are guarded by md5 checks: VO 30e67dbd…, script b30ce609…, music e25af185….
- Final script md5 is listed at the bottom of this file.

## Slot table (cut rule: word start − 0.08 s when the preceding gap ≥ 0.25 s, else the floor frame of the word start; overrides on S01/S04/S11/S12)
| slot | plate | f0 | start | end | dur s | crop (plate px l,t,r,b) | push anchor | VO under shot |
|---|---|---|---|---|---|---|---|---|
| S01 | b01_gloucester_funeral_wide_kent_OWNER.png | 0 | 0.000 | 2.333 | 2.333 | full (cover) | [0.5, 0.45] | England buried its king. |
| S02 | b02_kent_bound_dawn_close_OWNER.png | 70 | 2.333 | 4.833 | 2.500 | full (cover) | [0.5, 0.45] | Two years later, his half-brother was |
| S03 | b03_corfe_moonlit_from_below_OWNER.png | 145 | 4.833 | 7.033 | 2.200 | full (cover) | [0.62, 0.35] | executed for trying to rescue him. |
| S04 | b04_the_brothers_OWNER.png | 211 | 7.033 | 12.300 | 5.267 | full (cover) | [0.8, 0.3] | The king was Edward the Second. His half-brother, the Earl of Kent, |
| S05 | b05_landing_1326_kent_OWNER.png | 369 | 12.300 | 16.033 | 3.733 | full (cover) | [0.35, 0.45] | had helped Edward's queen and Roger Mortimer overthrow him. |
| S06 | p04_berkeley_castle_dusk_OWNER.png | 481 | 16.033 | 20.233 | 4.200 | full (cover) | [0.62, 0.4] | Months later, Edward was announced dead at Berkeley Castle. |
| S07 | b07_kent_at_funeral_close_OWNER.png | 607 | 20.233 | 23.700 | 3.467 | full (cover) | [0.45, 0.35] | Kent attended his funeral at Gloucester. Then Kent heard |
| S08 | b08_kent_hears_friars_OWNER.png | 711 | 23.700 | 27.400 | 3.700 | full (cover) | [0.4, 0.35] | his brother was alive, held at Corfe Castle. |
| S09 | b09_kent_supporters_OWNER.png | 822 | 27.400 | 31.800 | 4.400 | full (cover) | [0.5, 0.4] | Around seventy men backed his plan to free Edward. A chronicle says |
| S10 | b10_corfe_kent_hands_letter_OWNER.png | 954 | 31.800 | 35.200 | 3.400 | full (cover) | [0.45, 0.55] | Kent handed a letter for Edward to a man at Corfe who claimed to guard |
| S11 | p07_mortimer_reads_letter_OWNER.png | 1056 | 35.200 | 38.200 | 3.000 | full (cover) | [0.55, 0.55] | him. That man took it to Mortimer. |
| S12 | b12_winchester_after_OWNER.png | 1146 | 38.200 | 42.467 | 4.267 | full (cover) | [0.5, 0.5] | Kent was beheaded. Then Edward's young son, now king, |
| S13 | b13_nottingham_seizure_OWNER.png | 1274 | 42.467 | 46.667 | 4.200 | full (cover) | [0.5, 0.4] | and a few loyal men seized Mortimer at Nottingham Castle by night. |
| S14 | b14_mortimer_charged_OWNER.png | 1400 | 46.667 | 50.533 | 3.867 | full (cover) | [0.5, 0.4] | Mortimer was hanged, charged with murdering the old king. |
| S15 | b15_papal_notary_writes_OWNER.png | 1516 | 50.533 | 55.100 | 4.567 | full (cover) | [0.4, 0.5] | Years later, a papal official wrote to Edward's son. He claimed |
| S16 | p10_escape_servant_clothes_twilight_OWNER.png | 1653 | 55.100 | 59.833 | 4.733 | full (cover) | [0.55, 0.5] | Edward had escaped Berkeley in disguise, and another man lay in his tomb. |
| S17 | p14_corfe_dusk_single_light_OWNER.png | 1795 | 59.833 | 65.133 | 5.300 | full (cover) | [0.62, 0.22] | He said Edward had been hidden at Corfe, the very castle Kent wrote to. |
| S18 | b18_edward_hidden_at_corfe_OWNER.png | 1954 | 65.133 | 69.600 | 4.467 | full (cover) | [0.55, 0.3] | And according to the letter, Edward left Corfe only after learning Kent |
| S19 | b12_winchester_after_OWNER.png | 2088 | 69.600 | 72.833 | 3.233 | [190, 520, 650, 1338] | [0.45, 0.5] | had been executed for saying Edward was alive. |
| S20 | p04_berkeley_castle_dusk_OWNER.png | 2185 | 72.833 | 76.433 | 3.600 | [380, 250, 900, 1174] | [0.55, 0.3] | Most historians believe Edward died at Berkeley. But |
| S21 | b19_kent_empty_seat_OWNER.png | 2293 | 76.433 | 79.500 | 3.067 | full (cover) | [0.5, 0.45] | if that letter is true, Edward lived to hear that |
| S22 | b20_kent_seals_letter_OWNER.png | 2385 | 79.500 | 83.767 | 4.267 | full (cover) | [0.55, 0.45] | the brother who helped overthrow him died trying to free him. |
| OUTRO | outro_edward_ii_gloucester_dusk_OWNER.png | 2513 | 83.767 | 92.033 | 8.267 | full (cover) | [0.5, 0.4] | History remembers the victors. We remember the rest. |

- Opening S01–S03: 2.333 / 2.500 / 2.200 s, inside the 1.5–2.5 s window.
- **Every other shot is ≥ 3.0 s.** The shortest are S11 at 3.000 s and S21 at 3.067 s; the build asserts this rule.
- End: speech energy ends 88.05 s. The outro then holds about 4 s, with the score fading from 89.4 s to 92.0 s.

## Motion
- Every slot uses StablePush 1.00→1.06 (geometric ease), copied verbatim from Germanicus v5b: PIL affine onto a 2x grid, then cv2 INTER_AREA down. The crops get the same push.
- No warp, distortion, water animation, vignette, letterbox, TEMP mark or "ILLUSTRATIVE RECONSTRUCTION" text.
- **Glow pulse (S10, S13: the larger wall-torch fires):** the plate stays static. A luminance-only pulse of about ±4.5% peak is applied on a blurred mask of warm highlights (r>170, r−b>70), driven by two slow sines (0.83 Hz and 1.71 Hz).
- **Candle preset: NOT applied.** No house candle-flicker preset was readily available, so candle plates (S01 hearse candles, S18, S22) get the plain push only.
- **S12** is b12 as-is (full plate, including the executioner).
- **S19** is a tight b12 crop, (190,520)-(650,1338) = 460x818, about 2.35x upscale. It shows the guard's arm, Kent's bowed head, the mantle and the block, and **excludes the executioner** (plate x≈660–915). Verified on a QC still.
- **S20** is a tight p04 crop, (380,250)-(900,1174) = 520x924, about 2.08x. It shows the keep and the lit window, with the moat static.
- **Outro** is used as-is (POSTERITY and tagline baked in, no overlay).

## Title (Chronicle Reveal, house CR from Germanicus v5b)
- Text: **"THE LETTER TO / A DEAD KING"**, from script-v3.md / OWNER-DIRECTION-v3.md. ⚠ The brief named "The King Who Was Buried Twice"; re-run with `--title` if that is wanted.
- Band centre: topPercent **32.5%** (inside the brief's 25–40% band).
- Timing: stroke enters f8–26; letters manifest f14–42; letters exit f179–199; stroke clears f188–209. The title is fully gone 2 frames before the S04 cut (f211), so it spans S01–S03.
- I tested 38.5% as well. It was worse: it covered Kent's head on B01 and the lit window on B03, and B02's mouth was still under it.

## Captions
- House ASS style (DejaVu Sans 54, white, 4 px outline, MarginV 400), auto_chunks of ≤7 words with a 24-character wrap. There are 42 cues, word-synced from `final-vo…_words.json`, and the text is verbatim from the script (asserted).
- Cue timing: each cue ends at its last word end + 0.30 s, capped at the next cue start − 0.04 s and at the outro cut. None are hidden: the title wording never appears in the VO.
- **The tagline (L17, "History remembers the victors. We remember the rest.") is NOT captioned**, because it is baked into the outro plate. The VO speaks it over the outro.

## Music & audio
- Score: **"Gregorian Chant", Kevin MacLeod, CC BY 4.0** (see `edit/MUSIC-CREDIT.md`). It is a single cue, starting at track 0:00 and running the full film (excerpt 0–92 s).
- Bed processing: HPF 70 ×2, then BED_EQ (−2.5 dB @320 Hz, −2 dB @1.8 kHz), then a −3 dB speech-band dip @3 kHz and a 1.2 s fade-in.
- **Dread rise:** about +4.5 dB by the S13 cut, rising to about +6.5 dB at the end of Nottingham (pre-duck). A parallel 40–160 Hz copy of the score ramps in from S12 (38.2 s), with weight 0.7→1.0 through S13. It eases back over about 2.5 s into S14 and returns to base by L16. The score sits about −1.5 dB through the outro, then fades 89.4→92.0 s: quiet and unresolved.
- SFX: CC0 knight footsteps in a castle hall (Vrymaa, freesound 770083), under S13 only, about 4.2 s, very low (−38 dB pre-gain, about −46 LUFS in the mix).
- VO chain: HPF 80, then acompressor (thr 0.125, ratio 3), then dual-mono.
- Bed: −21 dB, then sidechain-ducked by the VO (thr 0.02, ratio 4, 25/450 ms). The ducked bed measures about −27 LUFS against VO about −15 LUFS (about 12 LU under the voice) and stays audible throughout, including the outro (outro tail about −27 LUFS).
- Mix: +15.4 dB, then 192 kHz-oversampled alimiter (0.8), then 48 kHz.

## VO
t1 (seed 11), `vo/final-vo-oliver-edward-ii-v3b.wav`, md5 30e67dbdce08242d7e8a03e89cbff23d. Words json md5 acce2b6e4065cdbd2e342195b41a40f0. Details in `vo/VO-NOTES.md`.

## Plate issues
1. **Title band vs composition:** no opening plate has a calm 25–40% band.
   - B02: Kent's face sits at about 25–42% height, so the title crosses his mouth and beard (eyes clear).
   - B03: the Corfe keep sits under the title (the lit window is just below it at 32.5%).
   - B01: the upper hearse candles are behind the title.
   - The truly calm area on all three is about 0–12% height.
   - Fix options: regenerate B02 with the face lower (42–58%, as the original prompt asked), or approve moving the title to about 16–20%.
2. The outro filename differs from the slot map: the file is `outro_edward_ii_gloucester_dusk_OWNER.png`, while the map says butrio_hills. The gloucester_dusk file was used.
3. S19 and S20 crops are about 2.1–2.35x upscales of 941x1672 plates, so they are softer than the full plates. Acceptable for a rough; consider native regens.
4. S12 (b12 as-is) shows the executioner with the axe, as briefed. S19 removes him.
5. No stray text, watermark or artefacts seen on any plate.

## md5
| file | md5 |
|---|---|
| master mp4 | 84d0660a56cc3d06f011ebf2ed086023 |
| preview mp4 | ea4478f288677730996e9794c034221f |
| VO wav | 30e67dbdce08242d7e8a03e89cbff23d |
| VO words json | acce2b6e4065cdbd2e342195b41a40f0 |
| music mp3 | e25af185c7890ba1fdef695ae9b030b8 |
| captions .ass (kept in _build_v3b_v1) | ac2db59077f1d6ad4fbe9fb95026a3f0 |
| build script build_rough_edward_ii_v3b_v1.py | d1f1370a4a4db706757720c7a3d61f9e |

---
# v1b (2026-10-29, 4:12 PM EDT): Vellum's calls, built from v1
**Master:** `/workspace/posterity/renders/posterity-edward-ii-v3b-ROUGH-v1b.mp4`. 1080x1920, 30 fps, **88.533 s** (2656 f), same house encode as v1. 74,474,119 B, md5 832e1160a3c30c9c556ad42d347a6c43.
**Preview:** `…-ROUGH-v1b-preview.mp4`. 720x1280, with the master's AAC stream copied. 31,203,887 B, md5 c361057e5707a15b2cc47820169dbf5e.
**Loudness:** master and preview both read I -14.2 LUFS, TP -1.7 dBTP. The pre-AAC mix was -14.1 / -1.9.
**Script:** `edit/build_rough_edward_ii_v3b_v1b.py` (md5 81968b014b25fd71d69cd5c10399d6a6). It is a copy of the v1 script; the v1 script is left untouched so v1 stays reproducible. Defaults are --tag v1b, --title-top-pct 16.0 and --tail 0.5. Scratch goes to `edit/_build_v3b_v1b/`.

## Changes vs v1 (nothing else changed)
1. **Title text** is unchanged: "THE LETTER TO / A DEAD KING".
2. **Title band centre moved from 32.5% to 16.0%.**
   - Measured extents: text spans y 234–376 px (12.2–19.6%) and the strike spans 236–382 px (12.3–19.9%). This is a 2-line block, about ±3.8% around the centre.
   - I tested 16, 18 and 20% on stills from the start and end of each opening plate. The push moves the plate under the title, so both ends were checked.
   - **B01:** clear at all three values. The title sits on the vault and pillars, and Kent and the hearse are far below.
   - **B02:** at 16% the title crosses only the crown of Kent's hair, and his forehead, brows, eyes and face are clear. At the end of S02 (push at 1.06) the strike's lower ragged edge just meets the hairline. At 18% and 20% it covers the forehead.
   - **B03:** at 16% the keep's top battlements sit just below the strike with a small gap, and the lit window is clear. At 20% the strike touches the tower top.
   - **16% is the best value in range.** It still touches Kent's hair and hairline (not the face) at the end of S02.
   - IG top UI: the text top is 234 px (12.2%), below the usual top-bar zone of about 150–200 px.
3. **Outro trimmed from 8.267 s to 4.767 s.** The film now ends at 88.533 s (--tail 0.5 after the speech energy ends at 88.045 s).
   - A 4.0 s outro would end at 87.77 s and clip the spoken tagline "…We remember the rest.". 4.77 s is the shortest that keeps the full VO plus a 0.5 s breath.
   - Score: it stays audible into the outro, at about -26 to -29 dBFS RMS in the 86.0–86.5 s VO gap. It fades from 87.13 s to 88.48 s (1.35 s), reaching about -62 dBFS RMS at 88.25 s and digital silence at the last sample, so there is no hard cut.
   - The fade is the only change to the bed automation. The v1 points from 0 s to the outro, the bed and SFX gains and the duck settings are all identical.

Unchanged from v1: VO t1, every cut S01–S22 and the outro start (83.767 s), the 42 caption cues, motion, crops, glow, music and SFX, the mix chain and the -14 LUFS / ≤ -1 dBTP target.
- Captions .ass md5: v1b 8707d82263b4f3d5ca1d22b32d992510; v1 ac2db59077f1d6ad4fbe9fb95026a3f0. They differ only in the Title line, which carries the tag name.
- Plate issues are as v1. The title/face conflict is now limited to the hair and hairline on B02, as described above.
- QC: 6 stills from the v1b master were read: S01, S02 start and end, S03, and the outro at 85.0 s and 88.3 s.

---

## v3b Rough v1c (tag v1c), built 2026-10-29 17:25 EDT

Script: `edit/build_rough_edward_ii_v3b_v1c.py` (a copy of v1b) and the new effects module `edit/fx_v1c.py`.
The locked engine `presets/locked/engine/animate_b3_cb9e2b88.py` and preset `house-candle-lightspill-v1.json` were not edited.
Their maths is reimplemented in ROI form in fx_v1c, for speed.

### Changes from v1b
1. **Opening.** S03 (B03 Corfe) is removed. S01 and S02 now span 0–7.033 s, split at the VO word boundary "later, | his half-brother":
   - S01 `b01` runs 0.000–3.733 s (3.733 s, f0–f111): "England buried its king. Two years later,".
   - S02 `b02` runs 3.733–7.033 s (3.300 s, f112–f210): "his half-brother was executed for trying to rescue him.".
   - S04 starts at 7.033 s (f211). Every later cut is identical to v1b. The outro runs 83.767–88.533 s.
2. **Fire and candle animation with localised light-spill** on every flame plate (see the table below).
3. **Extra motion:** soft-mask parallax, mist and haze, embers, dust motes, the moon halo and the B19 smoke.
4. **Audio** is stream-copied from the v1b master (`-map 1:a -c:a copy`), with the v1b md5 asserted before the mux. The audio stream md5 is `21c813e2a7123eed1543424fc49d72a0`, identical for v1b, the v1c master and the v1c preview.

### Spill and pulse calibration
- `LOCAL = 0.32` scales the candle and torch spill radius (×0.6 for off-screen sources). The locked 800 px radius lit the whole frame, which made it pump.
- The halo is pulse-only, because the plates already have painted glow. Pool breathing is ×0.35.
- PULSE is set per plate so the near-source swing is about 20–33% p-p, the whole-frame swing is about 15% or less (b01, b07 and b13 reach about 16–18% because their candles are spread across the frame), and the step is 6% per frame or less:
  `b01 .14, b04 .76, b07 .138, b08 .9, b09 .28, b10 .47, b13 .22, b14 .26, b15 .52, p07 .43, p10 .79, b18 .43, b19 .23, b20 .45`
- Flame shape warp affects candle-sized flames only. The maximum displacement is 1.2–2.7 px (plate space), and the warp covers 0.26–6.7% of the frame, inside the flame ROIs only.

### Per-plate effects

| Plate (slots) | Shape-animated flames | Static-shape sources (glow and spill pulse only) | Other effects | Whole / near-source swing |
|---|---|---|---|---|
| b01 (S01) | 76 of 100 candles | — | 8 spill groups, haze, 170 motes | 17.1 / 17.8% |
| b02 (S02) | — | — | static (no flame) | — |
| b04 | 2 candles | — | haze, 120 motes | 6.5 / 32.3% |
| b05 | — | — | mist (water excluded) | — |
| b07 | 23 candles | — | haze, 150 motes | 17.8 / 17.8% |
| b08 | 1 lantern candle | window, off-screen torch | haze, 160 motes | 15.0 / 26.3% |
| b09 | 11 candles | — | haze, 140 motes | 15.4 / 15.8% |
| b10 | — | torch, 2 windows | 34 embers, mist, haze | 15.5 / 21.2% |
| b12 | — | — | static (daylight) | — |
| b13 | 3 candles | 3 torches | 70 embers, haze, foreground parallax (soft mask) | 16.1 / 16.8% |
| b14 | 22 candles | — | haze, 110 motes | 15.2 / 20.4% |
| b15 | 1 candle | — | haze, 150 motes | 13.2 / 33.3% |
| p04 | — | window | 2 mist layers (water excluded) | 0.1 / 22% |
| p07 | 1 candle | torch glow, off-screen source | floor pool, haze, 90 motes | 15.3 / 19.2% |
| p10 | — | lantern (treated as torch), 3 windows, off-screen doorway | mist | 15.1 / 29.1% |
| p14 | — | window | 2 mist layers | 0.1 / 18% |
| b18 | 1 candle | — | pool, breathing moon halo, haze, 90 motes | 15.9 / 23.4% |
| b19 | 4 candles (3 sconce, 1 table) | — | pool, 2 smoke wisps from the snuffed candles by the empty seat, haze, 115 motes | 15.4 / 21.5% |
| b20 | 1 candle | — | pool, haze, 90 motes | 16.2 / 24.5% |
| OUTRO | — | — | static (baked text) | — |

### Skipped and limited effects
- b02, b12 and the outro are static: they have no flame sources, b12 is daylight, and the outro has baked text.
- Parallax is on b13 only. It is the only plate with a cleanly separable foreground, and soft masks elsewhere would have warped faces or architecture.
- Only b18 has a moon. b05 is daytime, and p04's disc is the sun.
- Embers are on b10 and b13 only (real torches).
- No water animation. No whole-frame flicker.

### QC (master)
- Full decode has no errors, 2656 frames, 88.533 s. Master and preview both measure −14.2 LUFS I and −1.7 dBTP.
- **Title.**
  - S01 clears Kent.
  - In S02 (f112–f198) the band's lower edge sits about 25 px into Kent's hair, above the forehead. The eyes and brows are clear by about 90 px.
  - The S02 framing is the same as v1b. The title has exited by f210.
- **B03** is absent from the opening (b01 → b02 → b04). Corfe appears only at S10/S17 (p14) and S20 (p04).
- **Fire pairs.** Twelve plates checked 0.5 s apart at 360x640: the pulse is local and visible, with no strobing.
- **Warp check** (high-passed tile phase correlation, v1b vs v1c):
  - p14 and b05 (mist): median 0.05–0.06 px, max 0.22 px.
  - b13 background: median 0.08 px. The foreground soldiers shift rigidly by 4–8 px (the intended parallax), with no ghosting.
- **B19 smoke:** the two wisps rise and evolve from the snuffed candles (f2300/2330/2360).

### Outputs
| File | md5 | Bytes | Format |
|---|---|---|---|
| `renders/posterity-edward-ii-v3b-ROUGH-v1c.mp4` | b4f0aa7a68619ed5928738698f6e2eaf | 82,297,024 | 1080x1920 |
| `renders/posterity-edward-ii-v3b-ROUGH-v1c-preview.mp4` | 864191d526bf6cf79de336563745428d | 31,111,557 | 720x1280 |

v1 and v1b are untouched.
