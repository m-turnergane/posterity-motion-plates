# EXAMINER REPORT: Báthory Rough v1

- **File:** `v2/renders/bathory_rough_v1.mp4`
  - md5 e9d76b347c8a82970b290ec318630070 (verified)
  - 87.0 s, 1080x1920, 30 fps, 2610 frames
- **Reviewed:** Sat 31 Oct 2026, 2:26 to 2:40 PM ET.
- **Law applied:**
  - STANDING-LAW-examiner-v2-media (Passes 1 to 11)
  - Owner violence direction (31 Oct)
  - ARCHIVIST-CLAIMS-v2, GATE-NOTES, storyboard-v2, motion-plan r4, POST-PACK-v2
- **Evidence folder:** `v2/build_rough_v1/examiner-v1/`
  - `frames/`: 24 beat mid-frames, plus t0.5, t2.0, t80.5, t84.0, and the b03 start and end frames
  - `crops/`: 12 full-res crops
  - `contact_sheet_small.jpg`
  - `cuts_wordgaps.txt`
  - `asr_diff.txt`
  - `motion_per_beat.json`
  - `audio_measures.json`
- **Messages sent:** none. Nothing was deleted except my own /tmp scratch.

---

## VERDICT: **REVISION**

There is no binding factual error in the VO: all 18 lines trace to ARCHIVIST-CLAIMS-v2, and the captions match the VO word for word. The cut still fails three house standards:
- three plates of 2 s or shorter, including the map and the "Why?" hinge
- a designed sync cut whose door impact does not read on a phone (the cut also falls inside a phrase)
- the known outro duplicate

Three owner-redo plates (B01a, B10, B11/B19a) now carry imagery that ARCHIVIST-CLAIMS-v2 still forbids in writing:
- execution and interrogation imagery
- fire glow at Bytča
- servants' faces

The owner's violence direction plausibly licenses this imagery, but it has **no Archivist countersign**. The Bytča brazier is the one item the Archivist banned *for a factual reason* ("signals the burning method"). Until it is countersigned this is a process gap, not a FAIL. If the Archivist upholds the ban, it becomes a compliance fix.

Distribution risk is **low to moderate and fixable cheaply**. No plate is expected to draw an age gate. The main exposure is the opening frame: a kneeling bound man and a drawn sword at 0:00, which may also end up as the default cover.

---

## FIXES (must)

| # | Video time | Finding | Evidence | Smallest repair |
|---|---|---|---|---|
| F1 | 0:03.03–0:04.99 (B01b, 1.96 s); 0:07.60–0:09.45 (B03 map, 1.85 s); 0:49.00–0:50.77 (B14 "Why?", 1.77 s) | Three plates are at or under 2 s, against the house standard. The map shows a 6-word label ("Csejte, today Čachtice, Slovakia") plus "Bytča" and "Váh" for 1.85 s, too short for a cold viewer to read. B14 is the question hinge and is gone in 1.77 s. (The storyboard header says "Short shots: accepted for this cut (about 1.5s floor)". If the owner confirms that waiver overrides the house standard, downgrade to NOTE.) | `cuts_wordgaps.txt`; `frames/04_b03_mid.jpg`, `frames/b03_start_7.65.jpg`, `frames/b03_end_9.3.jpg`, `crops/b03_csejte_label.jpg`; `frames/16_b14_mid.jpg`, `frames/02_b01b_mid.jpg` | The VO words stay locked; only **line-gap silences** get longer. (a) Cut B01a→B01b at about 2.75 (gap 2.67–3.11) and add about 0.3 s to the "tried. / History" pause → B01b about 2.5 s. (b) Add about 0.8 s to the "Countess. / One" pause (7.50–8.31) and start B03 at about 7.52 → map about 2.7 s. (c) Add about 0.6 s after "Why?" (gap 50.25–50.85) and cut B14 in at about 48.86 → B14 about 2.6 s; the longer silence also strengthens the hinge. Net runtime is about +1.7 s. |
| F2 | 0:46.267 (B13a→B13b, F7 door impact) | **(a)** The F7 impact does not read on a phone. 94%+ of its energy is below 300 Hz (energy above 300 Hz is 17.7 dB below its full band). In the >300 Hz phone proxy it sits **5.1 dB under the VO**. Full band it is +3.3 dB over the VO (K-weighted, 100 ms) and +24.7 dB over the bed, which is audible only on headphones or a full-range system. This **confirms** the cold watch's "no SFX". **(b)** The hard cut was placed for that impact, inside a 23 ms gap in the phrase "the king pressed \| for her trial". medium.en puts the boundary inside "for" (46.22–46.42). So the cut breaks the "cuts land in word gaps" standard in spirit, for a sync the phone audience cannot hear. The F7 tail also drops the K-weighted margin on "for" to −3.9 dB (both ASR models still recovered it). | `audio_measures.json` → `f7`, rows for "for" 46.29 and "her" 46.44; `cuts_wordgaps.txt` (b13b IN-WORD per medium.en) | Do one of these, in this order: (1) give F7 a 1–4 kHz layer (wood knock or latch transient) so it reads at about 0 to +3 dB over the VO in the >300 Hz proxy, and keep the cut; or (2) move the B13b cut and the impact to the "trial, / Thurzó" gap (47.24–47.45), where the slam lands on the verdict and not mid-phrase. Option (2) also lifts B13a to about 2.8 s (B13b becomes about 1.6 s, so extend that pause by about 0.5 s). |
| F3 | 0:00–0:03.03 (B01a); 0:31.89–0:37.21 (B10); 0:37.21–0:41.12 and 1:08.58–1:10.89 (B11 and its reuse B19a) | **Owner-redo plates have no Archivist countersign.** ARCHIVIST-CLAIMS-v2 still reads: "Bytča group … shown only from behind", "No interrogation or execution imagery; methods of execution stay out of … plates", and "Do NOT use a smoke column, pyre or fire glow: it signals the burning method and reads as spectacle. No blocks, axes or crowds." The rough breaks all of these. B01a: kneeling servant with face shown, executioner's drawn longsword (shows the beheading method), a **lit brazier in the foreground**, a small crowd. B10: bound, tearful servant with face shown, being interrogated. B11: brazier with flame **and smoke** at Bytča, a small **blood** patch, a covered body. The owner direction covers "the execution, the interrogation, the carried body", but the brazier is a factual-signal ban, not taste. The B01a swap (plate file 1:21 PM ET) is also **not logged** in the motion-plan changelog; B10 and B11 are logged. | `crops/b01a_kneeling_sword.jpg`, `frames/01_b01a_mid.jpg`, `crops/b10_interrogation.jpg`, `crops/b11_carried_body_blood.jpg`, `frames/12_b11_mid.jpg`, `frames/21_b19a_mid.jpg` | Send the three plates to Archivist for a countersign under the new direction. Mildest edit if the fire-glow ban stands: paint the flame out of the B01a and B11 braziers (leave cold iron or remove them). This touches no story beat. Also log B01a in the motion-plan changelog, and update the stale B10/B11 table rows. |
| F4 | 1:19.60–1:27.00 (outro) | **Known issue, confirmed only (not re-prosecuted):** the baked "POSTERITY / History remembers the victors. We remember the rest." is duplicated by the burned captions "History remembers the victors." (79.68–81.95) and "We remember the rest." (82.77–85.61). | `frames/24_outro_mid.jpg`, `frames/t80.5.jpg`, `frames/t84.0.jpg`, `crops/outro_half.jpg` | Already queued: drop the two outro caption events. |
| F5 | POST-PACK-v2.md | The packaging is stale against this cut: it says "about 76-80 s" (actual 87.0 s, and about 88.7 s after F1), "fill in the exact file name", and "No SFX" (F7 is in the mix and storyboarded). Its guardrail "No … blood … talk" is fine for the text, but the plates now show blood. | POST-PACK-v2.md lines 2, 105, 111 | Update the runtime, master filename and SFX line before posting. No copy changes are needed for risk (see Distribution). |

## NOTES (Vellum's calls)

| # | Time | Note | Evidence |
|---|---|---|---|
| N1 | 0:37–0:41, 1:08–1:10 | **B11 blood.** It is restrained and non-graphic: a scatter of dark-red spots, no pool, no wound. It sits at about **82–86% frame height**, below the caption, inside the TikTok and Reels bottom-UI zone, so on those platforms it is mostly covered. Under the owner test ("only when it strengthens the scene") it adds little: the covered body already carries "executed". It adds a small distribution signal and conflicts with the storyboard palette line ("crimson … never as blood"). Recommend painting it out or desaturating it to mud. Keeping it is defensible. | `crops/b11_carried_body_blood.jpg` |
| N2 | 0:00–0:03 | **B01a as the opening frame.** Restrained, no blood, supported by the record (Ficzkó was beheaded). But it is the first image and the likely auto-cover. See Distribution. Also, Ficzkó is described in the record as "ifjú legény" (a young manservant), while the plate shows a bearded man of about 30. Minor. | `crops/b01a_kneeling_sword.jpg` |
| N3 | 0:37–0:41; 1:01.6–1:06.3 | **Invented heraldry:** a small carved eagle device on the B11 arcade and over the B17 door. The storyboard avoid-list bans invented heraldry; it is small and unreadable at phone size. The B01a gate cartouche is **blank** (OK). | `crops/b11_crest_topright.jpg`, `frames/19_b17_mid.jpg` |
| N4 | 0:56.15–1:01.63 | **B16: the three men at the hearth go unidentified** (CONFIRMED). The VO says only "her family"; the plate shows two young men and a boy, matching the Archivist's Pál (about 12) and the sons-in-law. A cold viewer sees "three nobles". The no-labels rule blocks a caption. Mildest fix: none needed for comprehension, because "her family feared a trial" lands without names. Optional: have the boy turn toward a portrait of her to tie the family to her. | `frames/18_b16_mid.jpg` |
| N5 | 0:23.7–0:31.9 and 0:44–0:49 | **Thurzó's allegiance.** The cold watch called it confusing (PARTLY CONFIRMED). The sequence "asked him to protect the family" → "his men were arresting her" → "Thurzó prevented [a trial]" is the designed ambiguity that "Why?" then splits into two readings. It works as a question, not as confusion, once B14 has time (F1c). No other change. | — |
| N6 | 1:01.6–1:06.3 | **Evidence balance** (cold watch: evidence "entirely dubious"). PARTLY CONFIRMED. The torture and hearsay are correctly kept apart: B10 tortured servants versus B17 free witnesses, as the Gate requires. But every evidential line in the VO is a doubt ("questioned under torture", "but many accounts were secondhand"), and the guilt reading gets only a motive (the family "feared a trial would reveal her guilt"). That leans toward "framed". The VO is locked and Archivist-passed, so this is a balance flag for Vellum and the owner only. An attributed counterweight would need Archivist sourcing first; do not improvise one. | — |
| N7 | 0:29.77–0:31.89 (B09, 2.12 s); 0:12.08–0:14.28 (B05, 2.20 s) | Borderline-short, above 2.0 s. B09 is the arrest payoff. | `cuts_wordgaps.txt` |
| N8 | whole | **House intro absent** on the opening plate. The storyboard deliberately chose a cold open ("There's no long title sequence"); if the house intro rule applies to standalones, it is a NOTE for the owner. | storyboard-v2 Shape |
| N9 | 0:05–0:07.75, 0:09.5–0:12.16, 0:42.8–0:44.5, 0:46.3–0:49.1 | Captions overrun the next cut by 0.08–0.15 s in five places (the tail fade). "Even when the king pressed" runs at 20 cps. Cosmetic. | caption check below |
| N10 | 0:43.3–0:43.8 | "above her" has the lowest margin of the watch words (K-weighted 9.6 / 8.9 dB, 1–4 kHz band 10.3 / 9.2 dB). small.en heard "manner" for "above her manor"; medium.en got it right. Nothing else crowds this phrase, so no action is needed unless the phone check shows a problem. | `audio_measures.json` → `watch` |
| N11 | docs | storyboard-v2 still tells every prompt to avoid "faces of the servants … fire glow … invented heraldry", and its palette line forbids blood. motion-plan r4 rows for B10/B11 describe the old plates. Bring the docs in line with the owner direction so the next examiner is not checking against dead rules. | storyboard-v2.md lines 75, 124 |

---

## STEERING FLAGS: confirmed or refuted

| Cold-watch flag | Result | Measurement |
|---|---|---|
| 1. Short plates ("0–2 execution", "0:02–4 portrait", 0:30–31, "Why?" ~1 s) | **MIXED.** "0–2 execution" REFUTED: B01a is 3.03 s. "0:02–4 portrait" is really B01b (seated Báthory), 1.96 s, CONFIRMED short; the archival portrait B02 is 2.61 s. 0:30 B09 is 2.12 s (borderline). "Why?" B14 is CONFIRMED short at 1.77 s, not about 1 s. Also short and not flagged: B03 map 1.85 s, B13a 1.87 s. | Cut list from the build CUTS and the render; `cuts_wordgaps.txt` |
| 2a. B08 ringed hand "knuckle-less, thumb merging" | **Largely REFUTED.** Four fingers with knuckle creases; the thumb is tucked under the hand. The lowest finger is slightly long. A mild artistic note at most. | `crops/b08_hand_letter.jpg`, `crops/b08_hand_zoom.jpg` (full-res) |
| 2b. B10 quill hand "blob" | **Mostly REFUTED.** A closed fist gripping the quill, soft but readable. The interrogator's left hand on the table, partly behind the caption, is the weaker one (lumpy); minor. | `crops/b10_scribe_quill_hand.jpg`, `crops/b10_interrogation.jpg` |
| 3a. Portrait "fabricated cursive" | **REFUTED.** The top-left inscription and arms belong to the **real c.1630 painting** (Commons file, Hungarian National Museum), unaltered. They are not generated text. | `crops/b02_topleft_inscription.jpg`; asset `assets/b02_bathory_erzsebet_2_commons.jpg` |
| 3b. Map labels | **REFUTED as a text violation.** Place names only ("Csejte, today Čachtice, Slovakia", "Bytča", faint "Váh"), correct diacritics and geography (Csejte SW, Bytča NE on the Váh). The real problem is the 1.85 s read time (F1). | `crops/b03_map_labels.jpg`, `crops/b03_csejte_label.jpg` |
| 4. Blood on B11/B19a | **CONFIRMED present.** Restrained and non-graphic; in the bottom UI zone (N1). | `crops/b11_carried_body_blood.jpg` |
| 5. Motion "zoom or pan" | **Pan REFUTED; zoom only**, plus the approved depth drift. ORB plus RANSAC similarity on every beat (360x640, caption band masked): 21/24 beats are a 1.059–1.061 push about a fixed point stable to ≤0.03 frame-width between halves (no travelling pan); rotation ≤0.11°. The depth plates B04 (1.024), B09 (1.022) and B13a (1.033) show a lateral component of ≤22 px (0.02 width), within the motion plan's depth_v1 drift (B13a about 0.04 approved). B13b at 1.023 is registered to B13a. The centre shifts of up to 23 px are the off-centre zoom anchor, not a pan. | `motion_per_beat.json` |
| 6. Reused plates | Thurzó 0:18/0:50 **REFUTED**: B07 (standing, reading a sealed letter) and B15 (seated with depositions) are two different plates of the same character. Body 0:36/1:08 (B11→B19a) and painting 0:04/1:10 (B02→B19b) **CONFIRMED**, and intentional per the storyboard's B19 "two halves" (verdicts versus legend). That reuse earns itself. | `frames/08_b07_mid.jpg`, `frames/17_b15_mid.jpg`, `frames/12/21`, `frames/03/22` |
| 7a. Thurzó's allegiance confusing | PARTLY CONFIRMED; it is by design (N5). | — |
| 7b. Three men at the fireplace unidentified | CONFIRMED (N4). | `frames/18_b16_mid.jpg` |
| 7c. Evidence looks "entirely dubious" | PARTLY CONFIRMED as a balance lean (N6); no factual error. | — |
| 7d. "No SFX" | **CONFIRMED in effect.** F7 exists but is inaudible on phone speakers (F2). It is the only SFX: rebuilding VO + bed + F7 explains the mix to −15.9 dB residual, and no residual 100 ms window comes within 6.6 dB of the mix. | `audio_measures.json` |
| 7e. "Steady strings" | **CONSISTENT.** Ignosi's instrumentation includes violins and violas, alongside low brass, marimba and percussion (cue sheet). The bed gain is static; its 3 s short-term LUFS moves are the composition's own, and ducking adds only a median 3.4 dB. | below |

---

## MEASUREMENTS

### Cut list and word gaps
Durations (s): b01a 3.03 · b01b **1.96** · b02 2.61 · b03 **1.85** · b04 2.63 · b05 2.20 · b06 4.66 · b07 4.79 · b08 6.04 · b09 2.12 · b10 5.32 · b11 3.91 · b12 3.28 · b13a **1.87** · b13b 2.73 · b14 **1.77** · b15 5.38 · b16 5.48 · b17 4.65 · b18 2.30 · b19a 2.31 · b19b 2.54 · b20 6.17 · outro 7.40.

- All 23 cuts fall in TTS word gaps, with an 80 ms pre-roll into the next word.
- The exception is **b13b at 46.267**, inside a 23 ms gap mid-phrase (F2).
- medium.en also reports "IN-WORD" at b05 (12.08) and b20 (73.43). These are whisper boundary smear: the TTS gaps are 11.95–12.16 and 72.60–73.51, so they are **not** findings.
- The B13a→B13b hard cut is the only "slam" and is storyboarded.

### ASR versus the script (184 words)
- **medium.en (no prompt): WER 2.7%.** Errors are name spellings (Elisabeth, "Cite" for Csejte, "Bicha" for Bytča) plus **dropped "no" in "no stranger"**. small.en heard it, and the word has a 14.2 dB K-weighted margin, so it is an ASR artifact.
- **small.en (no prompt): WER 5.4%.** "armed men"→"Arne" (margins 16.9 / 19.1 dB, so an ASR artifact), "Csejte as"→"Siete and", "above her manor"→"manner" (N10), "Georgi", "bitcher", "Thurzul".
- The prompted runs lost about 40 words (small) and 8 words (medium) to whisper prompt dropout. They are discounted. `asr_diff.txt`

### Captions versus VO
- 38 chunks, 184 words, **identical word for word** to the VO words JSON and to `script-vo-v2-DRAFT.txt`.
- No overlaps. Each chunk starts exactly on its first word; the tail runs 0.02–0.25 s past the last word. At most 7 words per chunk.
- One chunk is at 20 cps; five chunks overrun a cut by ≤0.15 s (N9).
- The outro duplicate is confirmed (F4). No "ILLUSTRATIVE RECONSTRUCTION" text. No trackers anywhere: no progress bar, date bug or marker animation in the 24 mid-frames or the contact sheet.

### Loudness (render)
- **Integrated −14.2 LUFS; true peak −1.7 dBTP; LRA 4.1 LU.** On target (−14 ±0.3, TP ≤ −1).

### Mix rebuild
- VO, bed and F7 were rebuilt with the build script's own filter chains (bed −17.2 dB from Ignosi at 31.0 s, sidechain duck; F7 seed 77, −4 dB; master +17.2 dB, limiter 0.74).
- Aligned at 95 samples (AAC delay). Correlation 0.987; least-squares residual **−15.9 dB**, so the rebuild is valid for stem-level measures.
- The fit shows the VO 1.5 dB and F7 6.0 dB lower relative to the bed than the nominal chain, from the mono→stereo pan and the limiter on the impact. Margins below use the fitted gains.

### Score (bed)
- **3 s short-term LUFS range: 13.7 LU** in the mix (p95−p5 10.0), against 14.6 LU (p95−p5 11.3) for the un-ducked source.
- The bed gain is constant; ducking takes off a median 3.4 dB, p5 5.9 dB, max 6.7 dB, only under speech.
- Every >3 dB move within 3 s is present in the **un-ducked source**: 1.5–8.5, 27.7–33.4, 39.8–45.5, 43.8–48.8, 48.2–56.7, 55.9–62.0 and 67.3–75.8 s, at 4.1–6.3 dB. These are the composition's own swells, not mix rides. None are unexplained by ducking.
- The whole mix holds a 6.7 LU short-term range.
- PASS on one primary score at constant level.

### Per-word VO margin (VO minus bed+F7, per TTS word span)
- **House (K-weighted):** median 15.0 dB; p5 5.7; 11 words under 6 dB.
- **1–4 kHz band:** median 16.6 dB; p5 −0.6.
- **Phone proxy 300 Hz–8 kHz:** median 15.4 dB; p5 3.6.
- The lowest words are "it." 48.55 (−8.6), "for" 46.29 (−3.9, F7 tail), "a" 57.90 (−1.1; band −34), "in" 42.60 (band −16) and "and" 35.85 (phone −4.8). On inspection these are **TTS timing artifacts**: the word span falls mostly in silence or on a 20 ms function word. For example, "it." has VO RMS −49 dBFS in its listed span. **Every one was recovered by both no-prompt ASR models.**
- Watch words: "armed" 16.9, "men" 19.1, "no" 14.2, "above" 9.6, "her" 8.9, Thurzó (47.45, after F7) 17.4 dB K-weighted.
- No intelligibility FIX beyond F2.

### SFX
- F7 only, storyboarded (B13b "Foley door IMPACT"). The pre-swing overlaps "pressed"; the tail overlaps "for her trial". Phone audibility fails (F2).
- POST-PACK still says "No SFX" (F5).

---

## INVENTED-FACT TABLE (every VO line and every plate against ARCHIVIST-CLAIMS-v2)

**VO:** L01–L18 are all PASS per the Archivist (11:50 ET countersign of script-v2: 184 words, L02 and L12 rulings applied). The spoken text equals `script-vo-v2-DRAFT.txt` word for word (ASR and caption check). None of the DO-NOT-SAY items appear: no victim counts, "walled up", bloody discovery, "Thurzó stood to gain", or son's guardian.

| Plate | Time | What it asserts | Archivist status | Verdict |
|---|---|---|---|---|
| B01a | 0:00–3.03 | Bytča execution: a kneeling young male servant (Ficzkó), sword executioner, onlookers, a lit brazier, snow | Beheading of Ficzkó is documented (S2). Archivist bans execution imagery, servants' faces, fire glow and crowds. The owner direction now allows the execution. | Supported event. **Brazier = conflicts with a factual-signal ban** (F3). Age of the man (N2). |
| B01b | 3.03–4.99 | Báthory alone, candle, untouched | Atmospheric; original painted face | OK |
| B02 / B19b | 4.99–7.60 / 70.89–73.43 | Real c.1630 portrait with its real inscription and arms | Archivist: do not alter. It is the unaltered Commons asset. | OK (authentic) |
| B03 | 7.60–9.45 | Csejte (Čachtice) SW and Bytča NE on the Váh | MAP-PLACES geodata | OK (place names only) |
| B04 | 9.45–12.08 | Armed retainers walking to the village manor at night | Manor arrest at supper (S2, S3) | OK |
| B05 | 12.08–14.28 | Báthory at supper, torchlight at the door | Documented (S2) | OK |
| B06 | 14.28–18.94 | Village women whispering at a well | "rumours … for months" (S11), atmospheric | OK |
| B07 | 18.94–23.73 | Thurzó alone reading a letter (no courier) | Archivist REVISE applied | OK |
| B08 | 23.73–29.77 | A nobleman's ringed hand on a letter; no face, no bed | 1604 letter (S1); no Nádasdy likeness | OK |
| B09 | 29.77–31.89 | Arrest at the manor; plumed noble with torchbearers in the corridor | Thurzó present per Bledsaw (S1); "his men" | OK. Her ringed hand on the chair reads correctly; the silver cup shows no red (`crops/b09_arrest_hands.jpg`). |
| B10 | 31.89–37.21 | Bound female servant questioned by an official with notary and guard; no instruments | Torture 2 Jan 1611 at Bytča (S3). Archivist bans interrogation imagery and faces. The owner redo (1:23 PM changelog) allows it. | Supported; restrained; needs countersign (F3) |
| B11 / B19a | 37.21–41.12 / 68.58–70.89 | Covered body carried across the Bytča courtyard; brazier with smoke; blood spots in the snow; eagle crest | Executions "at once" (S3). How bodies were handled is **not recorded**. Blood is not in the claims. Brazier/smoke conflicts with the fire-glow ban. Heraldry is banned by the storyboard. | Body: plausible reconstruction. **Blood and brazier: unsourced visual detail.** Small, but consequential in tone (F3, N1, N3). |
| B12 | 41.12–44.40 | Torches climbing to the fortress, night | "taken up into the castle" (S2) | OK |
| B13a / B13b | 44.40–49.00 | Thurzó silhouette; council doors open, then shut | Outcome-image replacement for the old courier beat (Archivist REVISE) | OK (symbolic, no invented event) |
| B14 | 49.00–50.77 | Báthory at the castle window | Confinement in rooms, no cell (S5) | OK |
| B15 | 50.77–56.15 | Thurzó reading depositions | Symbolic | OK |
| B16 | 56.15–61.63 | Two young nobles and a boy at a hearth | Pál (about 12) and the sons-in-law (S1) | OK |
| B17 | 61.63–66.28 | Free witnesses queue; notary; brazier; crest | Inquest witnesses, hearsay, not tortured (S1) | OK. Crest (N3); a brazier here is not at Bytča, so no conflict. |
| B18 | 66.28–68.58 | Empty room, snuffed candle | Died in confinement (S5) | OK (no deathbed) |
| B20 | 73.43–79.60 | Close neutral portrait | Original face | OK |
| Outro | 79.60–87.00 | Čachtice ruin today, wordmark | — | OK, apart from the duplicate captions (F4) |

**No invented consequential *claim* is made.** The only unsourced *visual* details with weight are the Bytča blood and the brazier (B01a, B11).

---

## VIOLENCE / EXPLOITATION READ

- **Within the owner direction:**
  - B01a: the execution moment is shown before the blow; no blood, no blade contact.
  - B10: interrogation without instruments or wounds; a bruise and tears.
  - B11/B19a: the carried body is fully covered, with a few blood spots.
- **What is held back:** nothing is lingered on. The longest violent plate is B10 at 5.3 s, over the line that names the torture. There is no gore, no exposed injury, no nudity and no sexualisation. The young female victims (the alleged crimes) are **never depicted**, which is the right line.
- **Disputed events stay attributed:** the alleged murders are never shown or narrated as fact. Only the documented state actions (execution, torture, confinement) are illustrated.
- **Exploitation: none found.**
- **Two tone risks:**
  - Opening on an imminent beheading sells the violence before the question. It is defensible, because L01 *is* "servants were executed", but it is the strongest image in the film and it sits at frame 0.
  - The B11 blood adds signal without meaning (N1).
- **The Halloween framing** lives only in the title and captions, as the guardrail requires.

---

## DISTRIBUTION-RISK READ

This is a policy read against the platforms' published rules (YouTube Community Guidelines on violent or graphic content, advertiser-friendly guidelines on violence; TikTok Community Guidelines on violent and graphic content, violent extremism, and For You feed eligibility; Instagram Recommendations Guidelines). It is not a live platform test, and enforcement is probabilistic.

| Plate | YouTube (Shorts + ads) | TikTok | Instagram Reels | Mildest mitigation |
|---|---|---|---|---|
| **B01a** 0:00–3.03 (imminent execution, sword, bound kneeling man, fire) | Age gate: **not expected** (non-graphic, historical/educational). Ads: low to moderate chance of "limited ads" because a dramatized execution is the opening subject. | No graphic-content removal expected. **Moderate risk of reduced For You reach** if it becomes the cover or the first-second signal; executions are a sensitive category even when non-graphic. Violent extremism: not applicable (historical state punishment, no glorification). | Not "graphic". Possible "violent" recommendation demotion if used as the cover. | **Set a custom cover/thumbnail** (B02 portrait or B05 supper) on all three platforms. If more is needed, open on B01b for 0.3 s first or soften the sword (sheathed or out of frame). |
| **B10** 0:31.9–37.2 (bound, tearful woman interrogated) | No age gate. Ads: low. | Low; no torture instrument, injury or suffering lingered on. | Low. | None required. Optionally soften the bruise and tears. |
| **B11/B19a** 0:37–0:41, 1:08–1:10 (covered body, blood spots) | No age gate. Ads: low (minor non-graphic blood, educational). | Low. A covered body is allowed; the blood sits under the UI. | Low. | Paint out the blood (N1). This also removes the only "blood" signal for classifiers. |
| B09, B17 (torches, crowd) | Negligible | Negligible | Negligible | — |
| **Wording** (POST-PACK-v2) | Title "The Countess Who Was Never Tried \| A Posterity Halloween Special": benign. Description: "executed", "questioned under torture", "Blood Countess" in factual context are advertiser-safe for education. Tags OK. | Caption: "Blood Countess", "questioned under torture", "executed" in narrative; `#fyp #halloween #darkhistory`: low risk. The pinned comment is a neutral question. | Caption "Monster, or a woman framed?" is fine; "torture" is factual. | No wording changes needed. Keep the AI-content labels (already in the pack). Update the runtime, filename and SFX line (F5). |

**Net:** no age gate is expected anywhere. The only meaningful reach risk is B01a acting as the first impression or cover, and a custom cover removes most of it.

---

## COLD-VIEWER RECONSTRUCTION (one watch, no Bible)

A Hungarian noblewoman, Elizabeth Báthory, "the Blood Countess", was arrested at supper one winter night after rumours that young women in her service were disappearing. The man who sent the soldiers, Thurzó, had been asked by her dead husband to protect the family. Her servants were tortured, tried and mostly executed within days, but she was locked in her castle and never tried, because Thurzó blocked a trial even when the king pushed. Historians split on why: a frame-up kept out of court, or a family hiding her guilt. Much of the testimony was hearsay. She died confined; the servants got verdicts and she got a legend.

**Gaps against the spine:**
- Who the three men at the hearth are (N4, benign).
- Whether Thurzó is ally or enemy (designed; it is the question).
- The map names flash by too fast to place Csejte and Bytča (F1b, a current-chapter gap: Bytča is otherwise only a word).
- The evidence leans toward "framed" (N6).
- The door-slam punctuation is unheard on phone (F2).

---

## PASSES 1–11

1. **Hard compliance.**
   - VO and captions: clean.
   - House standards: short plates (F1), mid-phrase sync cut (F2), outro duplicate (F4).
   - Archivist plate bans vs the owner redo: needs countersign (F3).
   - Invented heraldry (N3).
   - House intro absent, by storyboard choice (N8).
   - No readable fabricated text; no "ILLUSTRATIVE RECONSTRUCTION"; no trackers.
   - Motion is zoom-only plus approved drift.
   - Loudness on target.
2. **Cold viewer:** above. The story functions; one current-chapter gap (the map).
3. **Causal graph:** rumours → king orders Thurzó → Thurzó (family protector) arrests her → servants tortured, tried, executed → she is confined and the trial blocked → why? two readings → died confined; servants got verdicts, she got a legend. Every arrow is spoken; no jumps.
4. **Information budget:**
   - hook 0–5 s
   - identity and map 5–9.5 s (**map under-budgeted**)
   - arrest 9.5–31.9 s (22 s)
   - Bytča 31.9–41 s
   - confinement and blocked trial 41–50.8 s
   - why 50.8–66.3 s
   - coda 66.3–79.6 s
   - outro 7.4 s (8.5% of runtime; acceptable)
   
   B08 at 6.0 s on a hand is long for one idea but carries the hinge line. The only imbalance is that the map and "Why?" are rushed.
5. **VO ↔ visual:** each turn gets its own plate. "Within days, most were executed" lands on B11 at its first word, and the doors shut on "pressed for her trial". B18's empty room on "She died in confinement" is good. No end-state-before-reveal problems.
6. **Visual delta:** strong alternation of cold exterior and warm interior; no slideshow stretch. The B13a/B13b registered pair is a deliberate non-delta.
7. **Retention:**
   - 0–3 s: execution plus the "never tried" contradiction.
   - 3–10 s: identity and map.
   - 10–20 s: arrest.
   - Midpoint: Bytča violence.
   - Turn: doors shut / "Why?" (rushed, F1c).
   - Final hinge: "No court ever decided".
   
   The questions form early and are paid off.
8. **Score:** Ignosi is dark, somber and unnerving, with low brass, strings, marimba and percussion. It fits dread and unresolved judgement. Constant level, duck-only. The F7 sound-design moment fails on phone (F2). Silence is used well before "Why?", and would work better with F1c.
9. **Proper-noun load:**
   - Báthory, Csejte, Thurzó, Bytča, "the king", "Blood Countess".
   - Thurzó is well oriented ("Hungary's highest official", the family protector).
   - Bytča is oriented only by the map (F1b).
   - The king is unnamed (fine).
10. **Serial function:** N/A (standalone). Entry is the cold open; closure is "No court ever decided".
11. **Exit state:**
    - Final image: the ruin at dawn plus the wordmark.
    - Final thought: "she was never judged".
    - Emotion: unease, unresolved.
    
    The outro is a new plate, not a repeat. The duplicate captions (F4) are the only blemish.

## SCORE READ
- **Music says:** dark, somber, slowly menacing historical drama.
- **Story needs:** unresolved dread and judgement withheld.
- **Match:** yes; no finding beyond F2.

## UNANSWERED VIEWER QUESTIONS
- What did she supposedly do? BENIGN, and deliberately left out (no victim counts).
- Who are the men at the fire? BENIGN (N4).
- Where is Bytča? CURRENT-CHAPTER GAP (F1b).
- Was Thurzó friend or foe? INTENTIONALLY OPEN (the thesis).
- Was she guilty? INTENTIONALLY OPEN.

## FINAL EDITORIAL TEST
Not yet finished: the map and "Why?" are rushed, the designed slam is unheard on phone, and the outro text is doubled. After F1, F2 and F4, plus an Archivist countersign (F3), this is PASS WITH NOTES material.

## Filing
- Report: `v2/EXAMINER-REPORT-rough-v1.md`
- Evidence: `v2/build_rough_v1/examiner-v1/` (frames 31, crops 12, `motion_per_beat.json`, `audio_measures.json`, `asr_diff.txt`, `cuts_wordgaps.txt`, `contact_sheet_small.jpg`)
- My scratch (/tmp/exb, including rebuilt stems) was deleted after measurement.
