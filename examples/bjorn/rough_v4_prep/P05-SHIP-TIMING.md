# P05 ship timing at a calm pace (rough_v4_prep), for Scriptor
Written 2026-11-03, about 10:55 EST, by the rough_v4_prep run. This is timing only; nothing has been rendered yet.

## Basis
- **Path geometry:** the registered P05 plate route from `map/p05_anim/p05_transform_v2.json` (`route_qa` lengths, in ref px; 1 ref px = 1 frame px at zoom 1.00).
  - The extra legs come from `map/refpack_p05/route_places_p05.json`.
  - The v4 ink route may shift lengths by about ±3%.
- **Camera:** the house push is 1.00→1.06, so frame speed = ref speed × zoom (≤ ×1.06). The camera drift adds up to about 15 px/s of screen motion on top, which is not included below.
- **Easing:** restrained, 50% linear + 50% cosine, so peak speed = 1.285 × average.
- **Holds:** 0.5 s sword-settle holds at the arrivals.
- **Dead time:** none. The ship moves from frame 0 and never stops except on the sword holds.
- **Calm pace:**
  - RECOMMENDED: ship peak ≤ **240 px/s** at 1080×1920. That is 0.125 screen-heights/s (1/8 screen height, or 0.22 screen widths per second), half the ≤1/4-screen cap.
  - MINIMUM: peak ≤ **320 px/s** (1/6 screen height per second).
  - For reference, the v2 ship peaked at about 560 px/s (S7, cosine), which was too fast.
- **Locks:**
  - "Spain": the word onset is when the ship passes the Strait of Gibraltar.
  - "southern France": the onset of "France" is the arrival at the Rhône/Camargue ("southern" lands about 0.4 s earlier, on the approach).
  - "Italy": the onset is the arrival at Pisa.
  - The arrival frame is the word onset, plus 0 frames.
- **Swords (Annales raids only):**

  | Place | Source | When it drops |
  |---|---|---|
  | Camargue | AB 859, lines 3292–3295 | on "France" |
  | Valence | AB 860, lines 3441–3444 | 0.25 s into the Camargue hold; the ship does not go upriver |
  | Pisa | AB 860, lines 3455–3456 | on "Italy" |

  - No sword in Spain: AB 3292–3293 records only passage ("inter Hispanias videlicet et Affricam navigantes"). The Algeciras raid comes from Ibn Idhari, not the Annales.
  - Nothing at Luna.

## (a) Leg path lengths (px)

| Leg | Style | px |
|---|---|---|
| Ship start → Strait pass: S2 in-frame tail (Algarve, from x 89) + S3 (Guadalquivir → Algeciras) + Strait channel exit | solid | 56.0 + 91.9 + 19.6 = **167.6** |
| Strait pass → Camargue: S4 rest + S5 (Nekor → Orihuela) + S7 (Orihuela → Rhône/Camargue) | solid | 61.5 + 213.6 + 393.6 = **668.7** |
| Camargue → Pisa: S9 | solid | **241.0** |
| Pisa → toward Rome, short of Rome: legend tail, drawn only, the ship does not travel it | broken and lighter | **146.7** |
| Context legs: S1 Loire → Galicia (dotted) 364.8, S2 full 550.5, S2a Seville (dotted) 28, S6 Balearics (dotted) 336.1, S8 Valence (solid river, out and back) 91.2 ×2, S12 return (dotted) 840.2, S13 return (dotted) 876.0 | fade in, not ship-traced | — |

## (b) Beats: travel, hold and arrival (seconds from the start of P05)

**RECOMMENDED (peak ≤ 240 px/s)**

| Beat | Travel | Hold | Arrival |
|---|---|---|---|
| Ship starts moving at the Algarve | — | — | 0.00 |
| Passes the Spanish coast, then the Strait, on "Spain" | 3.40 (slow glide, average 49 px/s, rising to about 94 px/s at the Strait) | 0 (passes) | **3.40** |
| Rhône/Camargue on "France" | 3.57 (average 187, peak 240) | 0.50 (Camargue sword; Valence sword at +0.25) | **6.97** |
| Pisa on "Italy" | 1.37 (average 176, peak 240) | 0.50 (Pisa sword) | **8.84** |
| Legend tail Pisa → toward Rome (broken and lighter, no Luna mark) | 0.80 | — | 9.34–10.14 |
| Final hold | — | 0.40 | end **10.54** |

Gaps between arrivals: Strait → Camargue **3.57 s**; Camargue → Pisa **1.87 s** (0.5 hold + 1.37 travel).

**MINIMUM (peak ≤ 320 px/s)**

| Beat | Arrival |
|---|---|
| Strait pass on "Spain" | 3.40 (same glide) |
| Camargue | **6.07** (2.67 travel) |
| Pisa | **7.60** (0.5 + 1.03) |
| Legend tail | 8.10–8.90 |
| End | **9.30** |

Gaps between arrivals: **2.67 s** and **1.53 s**.

- At either pace, if the "Spain" lead is shorter, the whole timeline moves earlier one-for-one. For example, a 2.9 s lead gives a minimum slot of about 9.0 s.

## (c) P05 slot length

| | Slot | Frames at 30 fps | Runtime change vs the v2 slot of 6.25 s |
|---|---|---|---|
| Minimum | **9.3 s** | 279 | +3.05 s |
| Recommended | **10.5 s** | 316 | +4.29 s |

- Shorter than 9.3 s means the ship has to run faster than 1/6 screen height per second (FLAG), or the "Spain" lead has to shrink.

## (d) Target spoken windows (line starts 0.20 s after the P05 cut)

**RECOMMENDED**

| Word | Seconds from P05 start | Seconds from line start |
|---|---|---|
| "Spain" onset | 3.40 | 3.20 |
| "southern" onset | about 6.55 | about 6.35 |
| "France" onset | 6.97 | 6.77 |
| "Italy" onset | 8.84 | 8.64 |
| End of "Italy." | about 9.55 | about 9.35 |

- "Spain" → "France": **3.57 s**, about 8.6 word-slots at 2.4 words/s. With one comma pause (about 0.3 s), that is roughly **8 words counting "Spain" and "southern"**.
- "France" → "Italy": **1.87 s**, about 4.5 slots, or roughly **4 words counting "France"** with one comma.

**MINIMUM**

| Word | Seconds from P05 start | Seconds from line start |
|---|---|---|
| "Spain" | 3.40 | 3.20 |
| "France" | 6.07 | 5.87 |
| "Italy" | 7.60 | 7.40 |

- "Spain" → "France": **2.67 s**, about 6 words with one comma.
- "France" → "Italy": **1.53 s**, about 3 words with one comma.

## (e) Shortfall of the current L04 read (TEMP Oliver read, breath gaps only)

**TEMP read:** `rough_v4_prep/p05/vo_temp/TEMP_vo_oliver_L04.mp3`. Timing guide only, NEVER final. Same voice, model, settings and seed 1611 as the v3 prep read.
- Measured onsets: Spain 2.368, southern 3.587, France 3.994, Italy 5.074; the line ends 5.759.
- Spain → France = 1.63 s; France → Italy = 1.08 s.
- The current v2b audio does not contain L04: v2 L04 reads "Annals of the time record a Viking fleet raiding Italy…".

**Breath gaps allowed are 0.3–0.9 s, so the maximum is 2.53 s and 1.98 s.**

| Pace | Gap after "Spain," | Gap after "France," |
|---|---|---|
| RECOMMENDED | needs **+1.94 s**, which is **SHORT by 1.04 s** even at the 0.9 s maximum (FLAG) | **+0.79 s** (OK) |
| MINIMUM | needs **+1.04 s**, which is **SHORT by 0.14 s** (over the natural 0.9 s; FLAG) | **+0.45 s** (OK) |

## Scriptor's L04 alternates
Source: `raw/script-vo-v4-LOCKED-L04alt.txt`, md5 115f1447…

- Onsets are estimated at 2.4 words/s (0.417 s/word), plus 0.3 s per comma and 0.5 s per full stop, measured from the line start. Estimates are ±0.3 s.
- The TEMP read shows Oliver runs a little faster after "France," (almost no comma pause there).

| Line | Words | Spain | France ("southern" ≈ −0.42) | Italy | End | Spain→France / France→Italy |
|---|---|---|---|---|---|---|
| Current (measured TEMP) | 13 | 2.37 | 3.99 | 5.07 | 5.76 | 1.63 / 1.08 |
| ALT-A | 16 | 3.22 | 5.19 | 7.16 | 7.57 | 1.97 / 1.97 |
| ALT-B | 18 | 4.67 | 6.22 | 8.19 | 8.61 | 1.55 / 1.97 |
| ALT-C | 14 | 2.92 | 4.47 | 6.02 | 6.44 | 1.55 / 1.55 |

Breath gaps still needed (after "Spain," / after "France,"):

| Line | Recommended pace (3.57 / 1.87) | Minimum pace (2.67 / 1.53) |
|---|---|---|
| ALT-A | +1.60 (too long, FLAG) / 0 (0.10 s spare) | **+0.70 / 0** (both natural) |
| ALT-B | +2.02 (FLAG) / 0 | +1.12 (FLAG) / 0. The 4.67 s lead also needs the line to start about 1.3 s before P05, or a longer ship pre-roll. |
| ALT-C | +2.02 (FLAG) / +0.32 | +1.12 (FLAG) / 0 |
| Current | +1.94 (FLAG) / +0.79 | +1.04 (FLAG) / +0.45 |

**Best fit: ALT-A.**
- It is the only line with a lead that matches (Spain at about 3.2 s) and a long enough France → Italy window.
- At the minimum calm pace it needs only a natural 0.7 s breath after "Spain,".
- At the recommended pace it is still about 1.6 s short between "Spain" and "France".

## Single target for Scriptor
Recommended pace; the line starts 0.20 s after the P05 cut.

| Measure | Target |
|---|---|
| Total line length | **about 9.4 s** (to the end of "Italy.") |
| Line start → "Spain" onset | **3.2 s** (about 7 words before "Spain", as in ALT-A) |
| Line start → "southern" onset | **about 6.35 s** |
| Line start → "France" onset | **6.77 s** |
| Line start → "Italy" onset | **8.64 s** |
| P05 slot | **10.5 s** |

- In practice: ALT-A plus about 4 more words (about 1.6 s) between "Spain," and "southern France". France → Italy as in ALT-A ("France, and finally raided Italy") already fits.
- Fallback at the minimum pace: ALT-A as written, with a 0.7 s breath after "Spain,". Line start → Spain 3.2, France 5.87, Italy 7.40, end about 8.1 s; P05 slot 9.3 s.

## Re-anchoring rule for the v4 VO
- Ship arrival frame = word onset + 0 frames. The Strait pass is on the "Spain" onset, the Camargue on the "France" onset, and Pisa on the "Italy" onset.
- Each sword lands on the arrival frame with a 6-frame (0.2 s) settle, inside the 0.5 s hold.
- Re-solve the travel times from the real onsets. If any leg would then peak above 320 px/s, FLAG it and add a breath gap or extend the slot rather than speed it up.

## Addendum, 2026-11-03 (EST): P05 v4 test and rough-cut timing
- Script: `raw/script-vo-v4-LOCKED.txt`, md5 **ff97caaa20d2238fddc30c7bdb4a0c8a** (verified before voicing and in every P05 build).
- Slot: **10.5 s** (315 frames at 30 fps). Line starts 0.37 s after the P05 cut. ALT-A2 pause of 0.354 s after "Mediterranean,".
- Arrival frames (ship on the word onset + 0 frames):

| Beat | Test (TEMP read) | Rough (voiced v4 read) |
|---|---|---|
| Strait (on "Spain") | 3.400 s | 3.024 s |
| "Mediterranean" label | 4.399 s | 4.324 s |
| Camargue (on "France") | 6.970 s | 6.779 s |
| Pisa (on "Italy") | 8.839 s | 8.892 s |
| Line end | about 9.4 s | 9.473 s |

- Peak ship speed: **260.0 px/s** at frame 252 (0.241 of the screen width per second), p95 255.8 px/s. Both variants are under the 320 px/s flag line.
- Variant **b** is primary: the solid line ends at Pisa. Variant **a** keeps the faint broken tail toward Luna.
- Overlay extent: x 67–1010, y 523–1318. This is 38 px below the y 1280 safe line. Captions sit at about y 1390–1520 (MarginV 400), so they don't collide. FLAG for directive 19.
- 1/3-scale (phone) check (`test_v4/p05_test_v4_third_scale_sheet.png`):
  - WEST FRANCIA and the realm shapes read.
  - EMIRATE OF CÓRDOBA in Uncial Antiqua reads "CMIRATC". FLAG. The rough cut uses IM Fell English SC instead.
  - PROVENCE (16 px), KINGDOM OF ITALY (19), Rhône (18), Pisa (16) and Strait of Gibraltar (19) are not readable at 1/3 scale. FLAG for directive 16 (phone legibility). These labels need about 28 px or more at 1×. The rough cut keeps the tested sizes (safest option, no new collisions); the fix goes to the next P05 pass.
- Fonts (all SIL Open Font License 1.1):

| Font | Use | Author | Source |
|---|---|---|---|
| IM Fell English SC | Realms, rough cut (RECOMMENDED) | Igino Marini | https://fonts.google.com/specimen/IM+Fell+English+SC |
| Uncial Antiqua | Realms, v4 test only | Astigmatic | https://fonts.google.com/specimen/Uncial+Antiqua |
| IM Fell DW Pica (Italic / Roman) | Water names, Pisa | Igino Marini | https://fonts.google.com/specimen/IM+Fell+DW+Pica |

  Comparison only (not used): MedievalSharp (wmk69), Eagle Lake (Astigmatic), IM Fell French Canon Italic. The OFL.txt files are in `p05/fonts/*/`.
- Outputs (`rough_v4_prep/p05/test_v4/`):
  - p05_test_v4b_silent.mp4 (1428519b…) and p05_test_v4b_guide.mp4 (606b9b8e…)
  - p05_test_v4a_silent.mp4 (4e0dbe62…) and p05_test_v4a_guide.mp4 (8fcae379…)
  - Guide audio is the TEMP ALT-A2 read: 0.354 s of silence inserted at raw 4.97 s, delayed 0.37 s, padded to 10.5 s.
- Rough-cut P05 (`rough_v4/build/p05_rough_v4.py`): variant b, word-locked to the voiced v4 VO, `--offset 0.376667 --pause 0` (the pause is already in the VO retime).
