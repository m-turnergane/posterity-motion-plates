# EXAMINER REPORT: Báthory, Rough v3
**Examiner** · Sat 31 Oct 2026, written about 5:10 PM ET · Judged against the STORY first and compliance second.
**File:** `renders/bathory_rough_v3.mp4`
- md5 `7efd3c476188310c3bd282d884e8498b` (verified)
- 97.5 s, 1080×1920, 30 fps, 2925 frames, AAC

**Locked VO:** `raw/script-vo-v3.txt`
- md5 `9db405e1…` (verified)
- 230 words, 19 lines

**Read before reviewing:**
- script-v3.md
- OWNER-NARRATION-v3.md
- ARCHIVIST-CLAIMS-v3.md (and the v2 rulings)
- BEAT-PLATE-LEDGER-v3.md (Rev 3)
- SCORE-LOCK-v3.md
- build_rough_v3/QC.md
- mix_v3.py
- beat_table.json
- the captions .ass file
- the tight-word JSON

**Law:** STANDING-LAW-examiner, plus the v2-media passes 2–11.

**Evidence:** `build_rough_v3/examiner-v3/`. It contains:
- `frames/`
- `crops/`
- `contact_sheet_small.jpg`
- `audio_measures.json`
- `cuts_wordgaps.txt`
- `captions_check.txt`
- `asr_diff.txt`
- `asr_words.json`
- `motion_orb.txt`

---

## VERDICT: **REVISION**

**The story lands.** The owner's bar is met: a cold viewer finishes knowing:
- what she was accused of;
- that the accomplices were tortured and executed while she was confined without trial;
- why Thurzó did it (Ferenc's dying wish);
- that the blood bath was added a century later.

The two hard story checks PASS:
- **Deaths not implied fabricated: PASS.**
- **"Nothing was ever proven against her in court" is clear: PASS.** On that line the VO beats the bed by 21.8–29.0 dB on the K-weighted measure, and the ASR is verbatim.

The cut is not shippable as-is for four reasons:
1. **An Archivist ruling was not carried over.** The B01a execution plate still has a large, live-animated flaming brazier. The ruling was embers only or paint it out, and the ledger says "No burning shown".
2. **Five plates sit at or near 2 s.** One is the film's hinge, "But Báthory was never tried." (2.10 s with no pause, where the storyboard says to "hold for the pause").
3. **The default cover frame is the H01 distressed maid with fire and irons**, and there is no POST-PACK-v3 that sets the H04b cover.
4. **B01a's who's-who.** The condemned man reads as a victim and wears a different costume from his arrest plate.

All four fixes are mechanical: one repaint or regrade, re-opened VO pauses, and a packaging file. There are no script changes.

---

## 1. FOUR-MOVEMENT TABLE (does each land?)

### M1 Accusation (0:00.0–0:11.3)
- **Beats and plates:**
  - 0:00 "accused of burning young maids with hot irons" (H01)
  - 0:04.1 "freezing water" (H02)
  - 0:06.5 rumours (B06)
  - 0:09.7 "reached the king"
- **Lands?** **YES.** "Accused" comes first and attributes every method. Both methods are shown with no injury.
- **Cold watch:** Confirmed: got the accusation. Weakness: the H02 pourers read as "villagers" (W-a).

### M2 Investigation and supper intrusion (0:11.3–0:29.4)
- **Beats and plates:**
  - 0:11.4 the king sends Thurzó (B07)
  - 0:15.9 armed men at the manor (B04)
  - 0:19.7 "eating supper" (B05, **2.10 s**)
  - 0:21.8 "Thurzó wrote that his men had found…" (H03)
  - 0:26.4 taken to the fortress (B12)
- **Lands?** **YES.** The supper intrusion is legible, but B05 is too short to register her before the cut (F2).
- **Cold watch:** Got Thurzó. H03's kneeling noble reads as Thurzó (see the invented-fact table, item 1).

### M3 Reversal (0:29.4–1:11.1)
- **Beats and plates:**
  - 0:29.5 four servants arrested (B01a_v1)
  - 0:35.3 torture and confessions; 0:39.5 "Three were executed within days" (B01a)
  - **0:41.8 "But Báthory was never tried." (B01b, 2.10 s)**
  - 0:43.9 "Nothing was ever proven against her in court…hearsay" (B17)
  - 0:51.4 king pressed, Thurzó prevented (B13a/b)
  - 0:55.4 Thurzó, Ferenc's dying wish (B08)
  - 1:02.6 "Many historians think…lands" (B14, B16)
  - 1:09.1 "She died in confinement." (B18, **2.03 s**)
- **Lands?** **YES on content, under-weighted on rhythm.**
  - The reversal's hinge ("never tried") has a 0.44 s gap before the next line, against the storyboard's "hold for the pause" (script-v3 V09).
  - "She died in confinement" is gone in 2 s.
- **Cold watch:** Confirmed: got the confinement and Ferenc's wish. Weaknesses: the B01a man reads as a victim (W-b); the B16 boy is never introduced (W-c); B13a is "empty" (W-d).

### M4 Payoff (1:11.1–1:37.5)
- **Beats and plates:**
  - 1:11.2 "Then someone added the detail…" (H04a)
  - 1:15.2 "A century later, a priest wrote…blood…beauty" (H04a, score swell)
  - 1:21.1 "No witness against her had described that." (B15)
  - 1:23.8 "No court ever heard her" (H04b)
  - 1:28.3 "the Blood Countess" (H04b)
  - 1:30.2–1:35.1 tagline (H04b)
- **Lands?** **YES.** The new information (the bath came a century later and no witness described it) arrives in the last 20 s. The ending reveals something new, as the owner required.
- **Cold watch:** Confirmed: "bath = legend" was clear. Weakness: B15 reads as "Thurzó says it?" (W-e, minor).

---

## 2. FIXES (must)

### F1 · 0:35.2–0:41.7 (B01a): the flaming brazier, an Archivist ruling not carried (CONFIRMED)
**Evidence:**
- `frames/10_b01a_mid.jpg`
- `crops/b01a_brazier.jpg`

**What is wrong:**
- The plate md5 is `e4cf0d6d…`, identical to `v2/plates/b01a_bytca_led_away.png` (mtime 1:21 PM ET), so the plate is unchanged since the ruling.
- A large open-flame brazier fills about 20% of the frame height at the lower left, right beside the kneeling condemned man. torch_v1c animates it, so the flames flicker live.
- The v2 Archivist ruling (ARCHIVIST-CLAIMS-v2.md, rulings item 4) said: "B01a: tone the brazier down to low embers or paint it out." The ledger's V08 line says "**No burning shown**."
- Two of the executed were burned alive, and Ficzkó's body was burned. A blazing fire at the execution therefore suggests exactly what the must-not forbids.

**Fix (mildest first):**
1. Regrade or paint the brazier down to low embers (no flame tongues) and drop torch_v1c on it.
2. Or crop it out. The push already ends at 1.06, so a reframe of about 1.25 that excludes x<215 would work.

Then send it to the Archivist for countersign.

### F2 · Short plates, against the house standard of no plates of about 2 s or shorter (CONFIRMED)
Measured from beat_table, with cuts checked against word gaps:

| Plate | Time | Duration | VO | Status |
|---|---|---|---|---|
| B13b doors shut | 0:53.40–0:55.30 | **1.90 s** | "Thurzó prevented it." | FIX. B13a and B13b are registered, so together they read as one 4.0 s shot that changes state. That softens this one, but it is still under the standard. |
| B18 empty room | 1:09.03–1:11.07 | **2.03 s** | "She died in confinement." | FIX. **Cold watch "cell ≈2 s": CONFIRMED.** |
| B01b Báthory alone | 0:41.67–0:43.77 | **2.10 s** | "But Báthory was never tried." | FIX. It is the hinge of the film, and the storyboard says "hold for the pause". |
| B05 supper | 0:19.57–0:21.67 | **2.10 s** | "Báthory was eating supper." | FIX |
| B13a doors open | 0:51.30–0:53.40 | **2.10 s** | "The king pressed for a trial." | FIX (see B13b) |
| H02 water | 0:03.97–0:06.33 | 2.37 s | "Of forcing others into freezing water." | NOTE, borderline. **Cold watch "H02 ≈2 s": PARTLY REFUTED** (2.37 s). |

**Fix:** re-open VO pauses. The tight read removed about 3.3 s.
- **After "tried."** (0:43.45): add about 0.9 s. This is the storyboard pause.
- **After "supper."** (0:21.31): add about 0.6 s.
- **After "trial."** (0:53.07): add about 0.5 s.
- **After "it."** (0:54.97): add about 0.6 s.
- **After "confinement."** (1:10.73): add about 0.8 s.

This brings every plate to 2.6 s or more. Runtime goes from 97.5 s to about 101 s, and nothing is re-voiced.

Re-run the mix with the same chains and re-anchor the L13 duck and the ease to the new word times.

### F3 · Opener cover and packaging: there is no POST-PACK-v3 (CONFIRMED; v1-F5 carries over)
**Evidence:** `frames/t0.0.jpg`

**The default cover:** on all three apps the default cover is frame 0 unless one is chosen. Frame 0 shows:
- H01's tearful maid looking up;
- live fire and the iron tongs in the brazier at the bottom of the frame;
- the caption "Elizabeth Báthory was accused of".

The ledger says "Thumbnail: … **Never H01 or H02**", but no v3 packaging file exists to enforce it.

**Fix:** write `POST-PACK-v3.md` with:
- a custom cover from H04b (for example the 1:31 frame, no caption) on TikTok, Reels and Shorts;
- the Anabasis I credit line (Scott Buckley, CC BY 4.0), which SCORE-LOCK says is required in the YT description;
- runtime;
- "No SFX".

See the platform section below.

### F4 · 0:29.4–0:41.7 (B01a_v1 → B01a): the condemned man reads as a victim, the B10 failure mode (CONFIRMED)
**Evidence:**
- `frames/09_b01a_v1_mid.jpg`
- `frames/10_b01a_mid.jpg`
- `crops/b01a_v1_group.jpg`

**What is wrong:**
- On the arrest plate the "young man" is seen from behind in a brown jacket and cap.
- On the execution plate the kneeling man is bareheaded and bearded, about 30, in a cream shirt. His hands are bound behind him and he looks upward, which is martyr iconography.
- Nothing ties the two plates together.
- He arrives under "Under torture, they confessed…", so for 4 s a casual viewer sees "a bound young man being tortured" before "Three were executed" re-frames him.
- He also reads older than Ficzkó's "young" (the v2 Archivist noted about 35).

**Fix:** fold this into the F1 repaint.
- Give him the B01a_v1 jacket and cap colours, a younger, lighter-bearded face and a downcast rather than heavenward gaze.
- Alternative with no repaint: open B01a 1.0 s later, on "Three were executed", and hold B01a_v1 through "confessed to dozens of killings". This needs B01a_v1 to stretch to about 6.8 s (fine).

---

## 3. NOTES (Vellum's calls)

**N1 · 0:21.7–0:26.2 (H03).**
- The plate is named `h03_thurzo_claimed_finding`. A fur-clad noble kneels at a covered body with a bloodstain.
- The face is NOT the B07/B15 Thurzó likeness: bareheaded, grey-streaked beard, different face. The costume and the VO "Thurzó wrote" make the cold viewer read him as Thurzó (**cold watch: CONFIRMED that it reads as Thurzó**).
- This is not a consequential invention. Thurzó was at Csejte for the arrest (v2 Archivist, Bledsaw), the VO attributes the claim, and C1's "many wounds and tortures" supports the blood.
- The ledger's brief ("one dying, being tended") is not painted, so "another dying" is under-served (QC flag 2).
- Options: leave it; or crop or paint toward one of "his men" (a feathered officer, no lord kneeling) and add the tended second girl.

**N2 · 0:51.3–0:53.4 (B13a).**
- The figure from behind wears Thurzó's feathered fur hat (the B07/B15 costume) under "The **king** pressed for a trial."
- **Cold watch: CONFIRMED.** The figure reads as Thurzó, the king is never shown, and the viewer found the plate "empty".
- It doesn't break the logic: VO carries the king, and the cold viewer still got king vs Thurzó.
- Options: paint the hat out or give the figure a royal attribute (crown or sceptre); or show the doors open on the empty council chamber with no figure. The second is cleaner: doors open, then doors shut.

**N3 · 1:05.5–1:09.0 (B16).**
- Two men and a boy of about 12 at the hearth, under "…rather than risk her beheading and the family's lands."
- **Cold watch: CONFIRMED that he is never introduced.** **Fact: consistent, not invented.** Her son Pál was born 1598, so he was about 12 in Dec 1610. ARCHIVIST D3 has "her son and sons-in-law were at the arrest", and the family agreement included Pál (through his guardian Megyeri) and the sons-in-law Zrinski and Drugeth.
- For a casual viewer the plate says "the family", which is exactly what the VO says.
- Options: accept; or drop the plumes and fur so it reads as "family" rather than "court".

**N4 · 1:20.9–1:23.7 (B15).**
- Thurzó reads a deposition under "No witness against her had described that."
- **Cold watch: "reuse of the 0:10 plate" is REFUTED.** B15 is a different plate from B07, with the same costume.
- **"Whose words": PARTLY CONFIRMED.** The line is the narrator's, but cutting straight from the priest to Thurzó can read as Thurzó saying it.
- No fact is misstated: he did collect the testimony.
- Options: replace with a deposition insert (stacked papers and a seal, no face), or reprise B17 (the witness queue).

**N5 · 1:11.1–1:20.9 (H04a).**
- **Cold watch "skull on the shelf": CONFIRMED** (`crops/h04a_skull.jpg`).
  - It is a full skull, lit at the top left. It survives the push, and at 0 to 2 s it is about 8% of the frame width.
  - It reads as a memento mori, not gore. It does tilt the priest toward "macabre" exactly while the VO is about murdered girls' blood.
  - Mildest option: paint it out.
- **Other drift from the brief ("a Jesuit in period black"):**
  - The man wears a brown habit with a pectoral cross and a full beard, so he reads as a friar or abbot, not an 18th-century Jesuit.
  - Csejte castle is in the window. That invents a local setting: Turóczi wrote at the Jesuit college in Trnava/Nagyszombat. This is minor and not consequential.
- **Page:** illegible pseudo-script; no readable fabricated text. PASS.

**N6 · 1:25.8 "But the legend had its monster: the Blood Countess."**
- The only line that could be heard as "she wasn't a monster at all". It is mitigated by line 16, which is scoped to "that" (the bath), and by "No court ever heard her" (not "she was innocent").
- The cold viewer did not read the deaths as fabricated. **Keep**, but don't let packaging (titles or descriptions) paraphrase it as "the monster was a legend".

**N7 · 0:00–0:06.3 (H02 pourers).**
- **Cold watch "villagers, not accomplices": CONFIRMED.**
- This is historically apt: the accomplices' confessions name the "alte Weiber" (Jó and Szentes). But nothing identifies them, and they are not linked to the B01a_v1 women 25 s later.
- It is harmless at 0:04, because the VO subject is Báthory ("accused of forcing others").
- Option: match the H02 headscarf colours to the B01a_v1 women, so a rewatch connects them.

**N8 · 0:29.4–0:35.2 (B01a_v1).**
- I count five walkers between the two guards: three headscarved women, the young man (right), and a capped figure at the back left (`crops/b01a_v1_group.jpg`).
- The VO says "Four servants." The capped figure is partly occluded and could pass for a guard.
- Option: paint the capped figure out or put it in guard livery.

**N9 · 0:55.3–1:02.4 (B08) ring hand.**
- **Cold watch "ring-hand texture": CONFIRMED but cosmetic** (`crops/b08_ring_hand.jpg`).
- Anatomy is correct: four fingers visible, thumb under, gold band on the ring finger. The skin carries the same craquelure as the whole plate, most visible at 1.06.
- The letter is illegible pseudo-cursive. PASS.

**N10 · 1:23.7–1:37.5 (H04b) end hold.**
- **Cold watch "14 s zoom": PARTLY REFUTED.**
- By ORB, the push runs 1.00→1.06 and completes at about 1:30.2 (on the eyes). The remaining **7.3 s are static**, under the tagline and a 2.4 s caption-free tail with a fade from 1:35.0.
- The ending lands, there is **no duplicated outro caption** (the tagline appears once, 1:30.2–1:35.1) and there is **no baked text** (`frames/t96.5.jpg`).
- Option: keep a very slow 1.06→1.08 push through the tagline so the last 7 s aren't a freeze.

**N11 · Caption micro-notes.**
- "Thurzó had fought the / Ottomans beside her husband." (0:55.4) breaks after "the". Re-break as "Thurzó had fought / the Ottomans beside her husband."
- Ten cards run at 17–19 cps. The fastest is "rather than risk her beheading" at 19.0 cps. They are acceptable at 4–5 words.
- After F2, re-time so that "Of forcing others…", "The rumours reached the king.", "fortress above her home." and "Many historians think…quietly" stop spilling 0.06–0.13 s past their cuts (`captions_check.txt`).

**N12 · Word "that." (1:22.96), the payoff word of line 16.**
- It has the lowest K-weighted margin in the film: 10.0 dB K-weighted, 8.6 dB in the 1–4 kHz band, 7.9 dB on the phone proxy.
- It sits on the tail of the priest-line swell, before the ease ramp (1:25.4).
- Option: start the −3 dB ease at about 1:22.5 instead of 1:25.4.

**N13 · The H-plates are 941×1672, upscaled about 1.15×** (QC flag 10). No visible artefacting in the crops. Native re-renders are preferred for final.

---

## 4. HARD CHECKS

### HC1. Deaths not implied fabricated: **PASS**
**VO, word by word:**
- Every allegation is attributed: "was accused of", "People said", "Thurzó wrote that his men had found", "confessed under torture".
- The only things called false or unproven are:
  - (a) the court case: "Nothing was ever proven against her **in court**", "much of it was hearsay";
  - (b) the bath: "added the detail", "No witness against her had described **that**".
- "much of it was hearsay" is scoped to the testimony, as the Archivist cleared.
- There is no "no bath of any kind" wording (L17 respected).

**Captions:** identical to the VO (230/230 words).

**Juxtaposition:**
- The bloodied H03 sheet (0:21–0:26) carries an attributed claim. It keeps the deaths real, not dismissed.
- The "hearsay" line plays over the witness queue (B17), not over a victim plate.
- The "legend" line plays over the portrait (H04b), not over any death plate.

**Residual risk:** N6 ("the legend had its monster"). It is acceptable as cut.

### HC2. "Nothing was ever proven against her in court" comes across: **PASS (exceedingly clear; the cold watch is CONFIRMED)**
**VO, 0:43.89–0:46.27:** "Nothing was ever proven against her in court." This is the Archivist's 4:04 PM lock.

**Per-word margins over the ducked bed:**

| Word | K-weighted (dB) | 1–4 kHz (dB) | 300 Hz–8 kHz phone (dB) |
|---|---|---|---|
| Nothing | 25.0 | 17.9 | 19.7 |
| was | 28.2 | 19.4 | 24.5 |
| ever | 29.0 | 16.3 | 24.1 |
| proven | 26.2 | 23.2 | 21.7 |
| against | 27.1 | 24.9 | 24.6 |
| her | 27.8 | 24.6 | 26.4 |
| in | 27.9 | 12.8 | 19.9 |
| court | 21.8 | 19.2 | 21.7 |

**Score:** the source track rises about 4.6 dB (unducked) across 0:44–0:46.5, but the sidechain duck (median −7.3 dB) holds it under. The margins stay at 21.8 dB or more K-weighted.

**Caption:** "Nothing was ever proven" (0:43.89) then "against her in court." (0:45.14–0:46.52). Faithful.

**ASR:** small.en and medium.en both return the sentence verbatim.

**Plate:** B17, the witness queue at the manor door with a scribe, starts 0.12 s before "Nothing". It shows testimony being taken, which supports "rested on witness testimony". It has a flaming brazier in the foreground. That is outside the Bytča ruling, but it is a second fire at a legal scene: Vellum may want it embered for consistency.

**Weak point:** the line arrives without a breath after "never tried" (0.44 s gap). F2 fixes this, and the line will hit harder for it.

### HC3. Who's who: see §6

### HC4. Fact check: see §5. No consequential invented fact. Two Archivist rulings did not carry (F1 brazier; B01a "young" Ficzkó, F4).

### HC5. Platform risk: see §7

---

## 4b. HOUSE STANDARDS

| Standard | Result | Detail |
|---|---|---|
| No plates of about 2 s or shorter | **FAIL → F2** | 1.90 / 2.03 / 2.10 / 2.10 / 2.10 s. H02 is 2.37 s (note). |
| Cuts land in word gaps | **PASS** | 19 of 20 cuts land in gaps, 0.05–0.36 s after the word end. H01→H02 at 3.967 falls 15 ms before the TTS end of "irons." (3.553–3.982), in the release, so it is inaudible. `cuts_wordgaps.txt` |
| One score at a constant level, ducked only for VO | **PASS with remark** | One cue: Anabasis I, with an internal 2.5 s crossfade at 0:37.0. Measured on stems rebuilt with the mix_v3 chains and least-squares fitted to the render decode (lag 48 smp, corr 0.989, residual −16.8 dB). Duck median −7.3 dB, p5 −8.6 dB. 3 s ST range of the ducked bed 12.5 LU (p95–p5 7.9). This is composition dynamics, not automation. Two non-VO gain moves exist, both deliberate: the L13 −3.5 dB plus 2 kHz cut at 1:08.5, and the −3 dB ease at 1:25.4–1:28.2. The priest-line swell is on the cue (SCORE-LOCK). |
| Per-word margins | **PASS** | K-weighted: median 23.6, min 10.0 ("that.", N12), 0 words under 10 dB. 1–4 kHz: median 17.9, p5 8.1. Lowest band values are all short function words: "a" −4.2 (20 ms, 0:52.48), "He" 0.8, "and" 3.0, "The" 4.7. ASR is unaffected. |
| SFX audible on a phone and only where storyboarded | **PASS (none)** | mix_v3.py has no SFX layer, and no v3 storyboard calls for SFX. Residual (render minus fitted VO+bed) in the cold watch's SFX windows: 0:00–0:02 −14.7 dB; 0:03.9–0:06.4 −15.2 dB; 0:06.3–0:08 −17.2 dB; 0:43–0:46 −18.0 dB. An SFX event would push the residual toward 0 dB. **Cold watch "fire crackle 0:00, splash 0:04, murmurs 0:06/0:44": REFUTED.** They are not in the audio. They are probably score texture plus visual suggestion (fire, water and crowd plates). |
| Captions faithful, every word, no duplicated outro | **PASS** | 48 events, joined text == script == VO (230 words). No overlaps. Tagline once. Breaks: N11. |
| No readable fabricated text; no "ILLUSTRATIVE RECONSTRUCTION" | **PASS** | B07, B08, B15 and H04a pages are pseudo-script and illegible at full-res. No overlay text besides the captions. |
| Zoom-only motion | **PASS** | ORB plus estimateAffinePartial2D, 5 samples per beat (`motion_orb.txt`). Every beat is push 1.00→1.06 with rotation ≤0.03°. H01 is a pull-back (0.90) plus tilt-down, approved in the ledger. B13a and B13b are registered with a combined ≈1.055. H04b push completes, then holds static (N10). |
| Integrated LUFS and true peak | **PASS** | −14.1 LUFS, −4.3 dBTP, LRA 3.2 LU (ffmpeg ebur128, render). |
| ASR vs the script | **PASS** | small.en WER 1.7% and medium.en WER 1.3%, spelling only: rumours→rumors; György→"Georgi"/"Jorgi"; girls'→girl's; small.en also "Ference's". No content errors. `asr_diff.txt` |
| Anatomy (full-res crops, viewed) | **PASS** | H02: both pourers' hands are correct on the pail rims; the soaked woman's arms are behind her back (bound reading), with no limb errors. B01a: bound hands are hidden behind the back, shoulders plausible; the executioner's crossed hands on the pommel are correct. B07/B15: reading hands correct, ring hand correct. B08: N9. H04a: quill hand and flat left hand correct. H03: resting hand correct. B16: the boy's clasped hands are correct. `crops/` |

### v1 fixes: confirm or refute

| v1 item | Status in v3 |
|---|---|
| F1 short plates | **NOT RESOLVED.** There is a new set of five plates at about 2 s (F2). |
| F2 inaudible F7 door impact and mid-phrase cut | **RESOLVED BY REMOVAL.** There is no SFX in v3, and B13b is a silent registered door-shut. |
| F3 Archivist countersign (B01a/B10/B11) | **PARTLY.** B10 and B11 are cut. **B01a: the countersign condition (embers) was not applied → F1.** |
| F4 duplicated outro caption | **RESOLVED.** The outro plate is omitted and the tagline is captioned once on H04b. |
| F5 POST-PACK stale | **NOT RESOLVED.** There is no POST-PACK-v3 (F3). |
| Note: B11 blood | **RESOLVED.** B11 is cut. Blood now lives only on the H03 sheet (attributed, restrained) and as faint red residue on the H04a page (QC flag). |
| Note: B01a cover risk | **RESOLVED for the cover**, since B01a is no longer the opener. The risk moved to H01 (F3). The flame brazier persists at 0:35 (F1). |

---

## 5. INVENTED-FACT TABLE (vs ARCHIVIST-CLAIMS-v3)

| # | Where | Depicted or said | Claims basis | Ruling |
|---|---|---|---|---|
| 1 | H03 0:21.7 | Fur-clad noble kneeling at the covered body (reads as Thurzó finding it personally) | C1: "his **men** found"; Thurzó at the arrest (v2, Bledsaw) | Inference, not consequential. VO attributes. N1 |
| 2 | H03 | Bloodstained sheet | C1 "many wounds and tortures" | Consistent |
| 3 | H03 | Only one body; the "dying" girl is absent | C1 | Omission (under-serves the VO). N1 |
| 4 | H01 0:00 | Báthory's lace-cuffed hand beside a maid and a heating iron | L1 transcript: "die alten Weiber und sie selbst" burned with irons | Consistent. Attributed by "accused of" |
| 5 | H02 0:04 | Older headscarved women pour water on a kneeling young woman in a snowy courtyard | L1 PASS (freezing water); accomplice confessions | Consistent. Pourers unlabelled (N7) |
| 6 | B01a_v1 0:29.4 | Prisoners led under guard | B: 3 women plus Ficzkó | Possibly 5 walkers vs 4 (N8) |
| 7 | B01a 0:35.2 | Condemned man, swordsman, **flaming brazier**, generic onlookers | B: Ficzkó beheaded, body burned; must-not "No burning shown"; v2 ruling "embers" | Male ✓, onlooker generic ✓ (not the B07 likeness), sword ✓. **Brazier ✗ → F1.** Reads older than "young" → F4 |
| 8 | B16 1:05.5 | Two men and a boy at the hearth | D3: son and sons-in-law at the arrest and in the family agreement; Pál b. 1598 (≈12) | Consistent. N3 |
| 9 | B13a 0:51.3 | Thurzó-costumed figure under "The king pressed" | — | Ambiguity, not a claim. N2 |
| 10 | B08 0:55.3 | Ringed hand, sealed letter, sabre for Ferenc's dying wish | Letter of 3 Jan 1604; Long War service | Consistent |
| 11 | B18 1:09.0 | Room with window, bed, snuffed candle | D4: house arrest, not walled up; died 21 Aug 1614 | Consistent (correctly avoids a walled-up dungeon) |
| 12 | H04a 1:11.1 | Bearded priest in a brown habit, Csejte castle in the window, skull | E1: Turóczi, Jesuit, 1729 (Trnava) | Minor drift (habit, setting); skull prop. N5 |
| 13 | B15 1:20.9 | Thurzó reading depositions | A6: ~300 witnesses | Consistent. N4 |
| 14 | VO "A century later" | Turóczi 1729 | E1 | PASS (round figure, Archivist) |
| 15 | VO "Many historians think…" | Motive | INTERPRETATION, "never most" | PASS |

**No consequential invented fact.** Two prior Archivist rulings did not carry over into the cut (#7). The rulings that did carry over:
- the B01a figure is male;
- onlookers are generic;
- B11 (with its background brazier) is cut altogether.

---

## 6. WHO'S WHO

**Cast as a cold viewer meets them:**

| Character | On screen | Cue | Clarity |
|---|---|---|---|
| Báthory | H01 (hand only); B05 supper; B01b; B14; H04b | Same pearl hood and ruff on all plates | Consistent ✓ |
| Thurzó | B07 and B15 (feathered fur hat, brown beard); H03 noble; B13a silhouette | B07 and B15 match each other | H03 is a different face that reads as him (N1). B13a's hat reads as him under "the king" (N2). |
| The king | Never shown | VO only | OK by VO. B13a mis-cues it (N2) |
| Ferenc | Hand only (B08) | VO "her husband", "Ferenc's dying wish" | ✓ |
| Accomplices | H02 pourers (unlabelled); B01a_v1 from behind; B01a kneeling man | VO "alleged accomplices", "Three were executed" | **Weakest link.** Pourers read as "villagers" (N7). The condemned man reads as a victim and doesn't match his arrest costume (F4). |
| Victims | H01 maid; H02 young woman; H03 covered body | Young women, headscarf or shift | Distinct from the accused ✓ (the must-not is met), apart from the F4 kneeling man |
| Family | B16 men and boy | VO "the family's lands" | Plausible (Pál ≈12, sons-in-law), never named (N3) |
| Priest | H04a | VO "a priest" | ✓ (habit drift, N5) |

**Cold-watch flags (verified on full-res):**

| Flag | Verdict | Where |
|---|---|---|
| (a) H02 pourers read as villagers | **CONFIRMED** (low impact) | N7 |
| (b) 0:34 bound young man reads as a victim | **CONFIRMED** | F4 |
| (c) 1:04 boy not introduced | **CONFIRMED.** The fact is consistent: Pál was ≈12 in 1610 | N3 |
| (d) 0:50 man from behind could be the king or Thurzó; plate "empty" | **CONFIRMED.** Reads as Thurzó | N2 |
| (e) 1:20 Thurzó, a reuse of 0:10, confusing whose words | Reuse: **REFUTED** (B15 ≠ B07). Confusion: **PARTLY CONFIRMED** | N4 |
| 0:21 Thurzó kneeling by a bloodied sheet, an invented fact? | **REFUTED as consequential.** Reads as Thurzó, and is a different face | N1 |
| 0:34 brazier vs the embers ruling | **CONFIRMED** | F1 |
| 1:10 skull | **CONFIRMED** | N5 |
| H02 hands on the buckets | **REFUTED** (correct) | crops |
| 0:34 bound hands | **REFUTED** (hidden, plausible) | crops |
| 0:54 ring-hand texture | **CONFIRMED, cosmetic** | N9 |
| H02 / cell ≈2 s | H02 2.37 s, **partly refuted**. Cell 2.03 s, **CONFIRMED** | F2 |
| SFX crackle, splash, murmurs | **REFUTED.** There are no SFX in the render | §4b |
| 14 s end zoom, duplicated outro? | Zoom 7 s plus 7 s static hold. No duplicate. **The end lands** | N10 |

---

## 7. PLATFORM RISK: the opener (H01, H02, H03)

This is a read of the published rules (TikTok Community Guidelines effective 24 Sep 2026: "Shocking and Graphic Content", "FYF Ineligible" and Content Levels; YouTube violent or graphic and age-restriction policy; Instagram Recommendations Guidelines and Sensitive Content Control). **It is not a live test.**

**Strictness:** TikTok > YT Shorts > IG Reels.

**Context that helps everywhere:** painted or historical art, an educational VO, no wounds, no gore, and no real footage.

**Default cover:** on TikTok, Reels and Shorts, the default is frame 0 or an auto-pick unless one is chosen. Frame 0 = `frames/t0.0.jpg`.

| Plate (time) | What's on screen | Default-cover exposure | TikTok (strictest) | YT Shorts | IG Reels | Mildest mitigation |
|---|---|---|---|---|---|---|
| **H01** 0:00–3.97 | Tearful maid looking up; fire and two-pronged iron at the bottom of frame 0; Báthory's hand at the edge. No contact, no injury. | **Yes: it is frame 0, the likely default cover** | "Focus on fear or suffering" is excluded from the **General-audience content level**, so it is likely gated to the older audience tier. It is **not** "graphic violence", so FYF-ineligible is unlikely. No warning interstitial expected. | Likely none (EDSA context, no injury) | Likely none | **Set a custom cover (H04b) on all three** (F3). There is no need to recut H01. Optional: start 1–2 frames lower in the tilt so the opening frame is the face only (the ledger's intent). |
| **H02** 0:04–6.33 | Bound young woman kneeling, mouth open in a scream, soaked semi-sheer shift, two women pouring ice water: **active abuse in progress** | No (unless auto-picked mid-video; YT may auto-pick) | **The highest risk in the film.** It is torture depicted in progress, though painted, with no wound or blood. Closest rule: "Fictional graphic incidents, violence" (FYF ineligible). Likely outcome: **FYF reduced or ineligible on a strict read, or a mature content level**, with a smaller chance of a sensitive-content warning screen. A wet, clinging shift on a restrained woman also brushes "sexualized" signals, a second vector. | Low: possible age restriction only if reviewers read it as "focus on torture"; unlikely at 2.4 s in an educational Short | Low: may be left out of non-follower recommendations (Recommendations Guidelines: violent content). No removal. | **In order of mildness:** (1) Cover rule (F3) so it can never be the thumbnail. (2) Re-grade or crop so the frame is pail, water and faces, with the shift below mid-thigh out of frame and less sheer. (3) Re-paint to a closed-mouth, gasping expression, hands not visibly bound. (4) Replace with the aftermath (the girl wrapped and shivering). Option 2 is enough for YT and IG; on TikTok option 3 lowers the risk most. |
| **H03** 0:21.7–26.2 | Covered body, bloodstain on the sheet, noblemen with a torch | No | Blood in an artistic or educational context is **Allowed**. A covered body is not a "dead body" depiction under the real-world rule, though a reviewer may still apply the FYF-ineligible "dead bodies" clause. **Likely none.** At worst, a mature content level. | None | None | Optional: reduce the bloodstain saturation by about 30% (QC flag 2 already asks). |

**Summary:**
- With a custom H04b cover, the realistic downside on TikTok is H02 only: reduced FYF reach or a mature content level. Removal is unlikely.
- YouTube and Instagram risk is low.
- Without a custom cover, H01 frame 0 becomes the face of the video in every feed and grid. That is the single cheapest risk to remove.

---

## 8. PLATE-PURPOSE TABLE

| ID | Time | Duration (s) | VO | Purpose | Verdict |
|---|---|---|---|---|---|
| h01 | 0:00.0–0:03.97 | 3.97 | "Elizabeth Báthory was accused of burning young maids with hot irons." | M1: the accusation made visible, attributed | KEEP (cover → F3) |
| h02 | 0:03.97–0:06.33 | 2.37 | "Of forcing others into freezing water." | M1: second method | KEEP. Short (note); platform risk (§7); N7 |
| b06 | 0:06.33–0:11.30 | 4.97 | "People said young women were dying… reached the king." | M1→M2: rumour to crown | KEEP |
| b07 | 0:11.30–0:15.80 | 4.50 | "He sent… György Thurzó, to investigate." | M2: introduce Thurzó (his likeness anchor) | KEEP |
| b04 | 0:15.80–0:19.57 | 3.77 | "One December night, armed men arrived at her manor." | M2: the intrusion | KEEP |
| b05 | 0:19.57–0:21.67 | **2.10** | "Báthory was eating supper." | M2: the supper detail, her first appearance | KEEP. **F2** |
| h03 | 0:21.67–0:26.23 | 4.57 | "Thurzó wrote that his men had found one girl dead and another dying." | M2: the attributed finding | KEEP. N1 |
| b12 | 0:26.23–0:29.40 | 3.17 | "Báthory was taken to the fortress above her home." | M2 close | KEEP |
| b01a_v1 | 0:29.40–0:35.20 | 5.80 | "Four servants… alleged accomplices." | M3: the accused | KEEP. N8; costume anchor for F4 |
| b01a | 0:35.20–0:41.67 | 6.47 | "Under torture… Three were executed within days." | M3: their fate | **F1 + F4** |
| b01b | 0:41.67–0:43.77 | **2.10** | "But Báthory was never tried." | M3: **the hinge** | KEEP. **F2** (pause) |
| b17 | 0:43.77–0:51.30 | 7.53 | "Nothing was ever proven against her in court… hearsay." | M3: testimony | KEEP (brazier: Vellum's call) |
| b13a | 0:51.30–0:53.40 | **2.10** | "The king pressed for a trial." | M3: the trial pressed | **F2**, N2 |
| b13b | 0:53.40–0:55.30 | **1.90** | "Thurzó prevented it." | M3: the door shut on the trial | **F2** |
| b08 | 0:55.30–1:02.43 | 7.13 | "Thurzó had fought… Ferenc's dying wish…" | M3: motive (the wish) | KEEP. N9 |
| b14 | 1:02.43–1:05.47 | 3.03 | "Many historians think he confined her quietly" | M3: confinement | KEEP |
| b16 | 1:05.47–1:09.03 | 3.57 | "rather than risk her beheading and the family's lands." | M3: stakes (family) | KEEP. N3 (ledger "at risk" resolved; it now matches the VO) |
| b18 | 1:09.03–1:11.07 | **2.03** | "She died in confinement." | M3 close | KEEP. **F2** |
| h04a | 1:11.07–1:20.93 | 9.87 | "Then someone added… a priest wrote… to keep her beauty." | M4: the legend's author | KEEP. N5 |
| b15 | 1:20.93–1:23.70 | 2.77 | "No witness against her had described that." | M4: back to the testimony | KEEP. N4 |
| h04b | 1:23.70–1:37.50 | 13.80 | "No court ever heard her… Blood Countess." plus tagline | M4 payoff, exit | KEEP. N10; cover source |

---

## 9. PASSES 2–11 (condensed)

**2. Cold viewer.**
- Got: the accusation, the king and Thurzó, the confinement, Ferenc's wish, and the bath as legend.
- Did not read the deaths as fabricated. "Never proven in court" read as "exceedingly clear".
- I agree with all of it, and verified the remaining flags (§6).

**3. Causal graph.** The chain is complete: accusation → king → Thurzó → raid → servants punished → no trial ← Thurzó ← dying wish → confinement → death → priest adds the bath → legend. There are no orphan nodes. The boy (N3) is a decorative node.

**4. Information budget.**
- 230 words in 94.8 s of VO is 2.43 wps, dense but fine.
- Proper nouns: Elizabeth Báthory, Hungary, György Thurzó, Ottomans, Ferenc, Blood Countess.
- Six is under the load ceiling. Ferenc is introduced as "her husband" one sentence earlier ✓.

**5. VO↔visual.**
- 17 of 21 plates illustrate their line directly.
- Mismatches: B13a (the king; N2), B15 (whose words; N4), B01a (victim reading; F4) and B16 (unnamed boy; N3).

**6. Visual delta.**
- Every cut changes the scene or the subject.
- B13a→B13b is a deliberate registered state change.
- B07 and B15 are distinct Thurzó plates. There are no reuses.

**7. Retention.**
- The hook is under 1 s (the accusation in the first sentence).
- Mid-film re-hooks: the raid (0:15), the executions (0:39), "never tried" (0:42), the king vs Thurzó (0:51), the reveal (1:11).
- The weak spot is 0:41–0:44, where the biggest line is rushed (F2).

**8. Score and sound.** One cue, constant apart from deliberate automation; the swell on the priest line is apt; no SFX; the mix is clean. See §4b.

**9. Proper-noun load.** OK (see 4).

**10. Serial.** N/A.

**11. Exit state.** The viewer leaves knowing guilt is unresolved, the trial never happened, and the bath is legend. The tagline lands once on her face. ✓

## SCORE READ
- Anabasis I suits the material: restrained, with a single swell that lands on the priest line.
- The bed stays well under the VO (median margin 23.6 dB K-weighted).
- The only word near the limit is "that." (N12).

## UNANSWERED QUESTIONS (for Vellum or the Archivist)
1. Should B17's foreground brazier also go to embers, for consistency with F1?
2. H03: keep the noble at the body, or switch to "his men" (N1)?
3. H02: which mitigation level suits the channel's TikTok strategy (§7)?

## FINAL EDITORIAL TEST
**Would a stranger finish this and be able to say what she was accused of, why it matters, and what changes by the end? Yes.**

The v3 story is the strongest Báthory cut yet. It needs:
- one plate repaint or regrade (B01a: embers plus Ficzkó continuity);
- about 3.4 s of restored pauses;
- a POST-PACK with an H04b cover and the score credit.

After that it should move to **PASS WITH NOTES**.
