# Björn Rough v4: Examiner recheck
Examiner, Tue Nov 3 2026 (ET). Standing law: `ledger/STANDING-LAW-examiner-v2-media.md`. No messages were sent.

Render: `rough_v4/renders/bjorn_rough_v4.mp4`
- md5 **1a4b5920021cdaae03876e3f69eca28c** ✓
- 1080x1920, 30 fps, 3058 frames, **101.933 s** (1:41.9)
- **I −13.9 LUFS, TP −4.3 dBFS**, LRA 2.6 ✓
- The render's audio matches `scratch/audio/mix_bjorn_v4.wav`: lag 0, residual −40.0 dB (AAC). mix − (VO stem + bed stem) gives a residual of −37.1 dB, so the stems are a valid basis for the margins.

## VERDICT: REVISION (light). Two render fixes and one paperwork fix. Audio, captions and the P13 cut pass.
The film works. Audio is the best it has been: no word is under 6.7 dB in any band. Captions are exact. The P13 cut is word-locked. The atlas ship and swords are locked to the words.

Three things need fixing:
- **P07 is under 2 s.** This is a regression.
- **P05's small labels are not phone-readable.** The directive explicitly asks for phone-readable labels.
- **The locked L04 line has no Archivist countersign.**

All three fixes are cheap. There is no recut of the story.

### FIX list
| # | t | Item | Measured | Ask |
|---|---|---|---|---|
| FIX-1 | 30.433–32.200 | P07 "gates barred" plate | **1.767 s** (53 frames). It is the only plate under 2 s; next shortest is 2.700 s. v2 had nothing under 2.367 s. | Make P07 ≥ ~2.4 s by adding a ~0.4–0.6 s VO pause after "barred." (31.927 → next word 32.31). Moving the P06→P07 cut earlier alone cannot reach 2 s: "Rome." ends at 30.127, which gives a ceiling of ≤ 1.97 s. |
| FIX-2 | 15.433–25.933 (worst at 19–25.9) | P05 atlas labels on a phone (directive: "phone-readable") | Cap height at 1080 wide: **Pisa 12 px** (x-height 7), **Provence 12**, **Strait of Gibraltar 12** (x-height 8), **Rhône ~10** (vertical italic), Kingdom of Italy 13 over busy mountain art. At 390 px wide (×0.361): Pisa cap ≈ **4.3 px**, so these four are illegible. At 540 wide (×0.5): Provence and Italy are borderline, Pisa is ~6 px (marginal), and Strait and Rhône are illegible. West Francia, Emirate of Córdoba (~18 px) and Mediterranean Sea (17) are readable at 390. | Raise the caps of the story labels (Pisa, Provence, Rhône) to ≥ 22–24 px at 1080, with a halo or plate on Kingdom of Italy. Also fix two defects: the "F" of FRANCIA sits on the Atlantic coast stroke (OCR reads "RANCIA" on 2 of 3 frames), and "Gibraltar" is clipped (faint G at x≈65; the final r runs into the Iberian coast at t19.4). See ev01, ev02. |
| FIX-3 | 15.5–24.9 (L04) | Script provenance | LOCKED md5 ff97caaa uses **L04 ALT-A2** (adds "into the Mediterranean"). `ARCHIVIST-v4-CHECK.md` passed ALT-A only, marks ALT-A2 "Pending Archivist countersign", and voids its v4c countersign if the md5 changes. | Get an Archivist countersign on LOCKED ff97caaa before fine cut. No render change is expected. |

### NOTES (no action required unless the owner wants it)
- **N1, P11 43.933–48.133 = 4.200 s** vs the owner's 3.5–4 s. That is 0.2 s over, and it is bound by the VO: "Then," starts at 44.023 and "grief." ends at 47.820. To trim, tighten the pause after "grief." (0.31 s to the cut).
- **N2, title 5.5–10.6.** It reads 6.6–10.2 (~3.6 s readable, ~5.1 s total). It has 7 words on a red brush band. The retention guide (§3) calls for 2–5 words, ≤ ~2.2 s and no banner, but the owner restored the house intro, so this stays a note. Content flags:
  - "SACKED" on screen against the Archivist's caution ("no on-screen 'sacked 860'-type text");
  - "THE KING" sits against the final reversal ("crowned the wrong Viking").
  - Placement passes: it starts after the hook (P03 cut 5.433, "Legend" 5.523), sits at y ≈ 527–600 (topPercent 31), clears Björn's face, and does not collide with captions (captions at y ≥ 1410). See ev05.
- **N3, coffin vs bier.** P11 and P13 show a **closed, cloth-draped coffin**. P17B (80.433–87.967) shows an **open bier**, with Hastein visible, a sword on his chest and hands clasped. A cold viewer may read it as a different event. It is owner-directed and the Archivist flagged it as interpretation, so it stays a note. His identity carries over: grey-streaked hair, beard, mail and red cloak match P14 (ev06).
- **N4, P13 mail already visible in the procession wide.** At f1698 (56.600) the left-foreground figure's mail shows under the cloak, so the f1699 cut is a reframe more than a reveal. It is still word-locked and reads cleanly (ev03).
- **N5, word count 244** vs the owner's 225 cap (+19). This is the owner's own text, so it is recorded only.
- **N6, P05 cut at 15.433** lands 52 ms before the json end of "there." (15.485). The waveform there is only a −30 to −35 dB tail, and small.en ends "there." at 15.30. It is effectively in the gap.
- **N7, unlabeled base-art town dot** on the Ligurian coast at ~(737,750), ~75 px (~110 km) NW of Pisa: nearer Genoa than Luna (~34 px from Luna). Nothing is drawn at Luna. It is harmless, but a sharp-eyed viewer may ask "what's that?". It could be painted out with FIX-2.
- **N8, bed swells in VO gaps after 54.77** of ~5–8 dB (gap RMS: 63.02–63.47 −23.0; 68.71–69.91 −28.4; 96.69–97.55 −25.5) vs ~−29 to −38 under the VO. This is normal 700 ms sidechain release (same chain as v2b), not word-rate pumping.
- **N9, cover.** v4 `POST-PACK-CREDITS.md` reads "Cover: owner's choice (pending)", and `rough_v1/POST-PACK-CREDITS.md` still points to v2 / "Cover: not picked". Stale but harmless; see §8.

## COLD VIEWER READ
Here is what a viewer is told, in order:
1. Legend: Björn Ironside sailed to conquer Rome. The title band arrives.
2. A real fleet sails past Spain into the Mediterranean, through southern France and into Italy (the atlas).
3. A walled city at sunset. "He had found Rome." The gates are barred.
4. Hastein fakes dying, is baptised, and stages his own funeral.
5. Mourners wear armour. He leaps from the coffin and kills the bishop.
6. After the city fell: "This wasn't Rome. It was Luna."
7. Second reversal: the annals name no captain (P17A, a faceless hooded captain at the prow, reads instantly as "unnamed"). The oldest funeral story (Dudo) credits Hastein and never mentions Björn (P17B). A monk, William, later "placed Björn aboard" (a monk painting Björn's portrait by candle, a strong image). "They conquered the wrong Rome. Perhaps history crowned the wrong Viking" plays over a half-sketched Björn above Luna.

The two-reversal structure lands; this is owner-approved and not relitigated. Björn being off screen ~63 s is also owner-approved.

Where a cold viewer may stumble:
- (a) Hastein vs Björn. The title says "THE KING WHO SACKED…" over Björn, while the VO switches to "Hastein" at ~26 s without saying who he is relative to Björn. v4 L03 ("…Björn Ironside, son of Ragnar Lothbrok, led a fleet…") followed by "Hastein believed…" leaves the viewer to infer that he is Björn's companion or co-leader. The payoff at 80–92 s explains it retroactively. It is acceptable, but it is the biggest cold-view cost.
- (b) The open bier (N3).
- (c) In P17B "gave Hastein the sword", the literal sword on his chest can read as a physical gift rather than "credited him". It is minor.

Claims check against the countersign (`claims-v2-countersign.md` / `ARCHIVIST-v4-CHECK.md`):
- L04 "into the Mediterranean" is countersign-pending (FIX-3).
- L16 "They conquered the wrong Rome" asserts the sack. The Archivist accepts it on the AB/Luna framing, provided there is no on-screen "sacked 860" text. The title's "SACKED" is borderline (N2).
- "Luna" as the sacked town is LEGEND-tier (Dudo/GND); the contemporary AB names Pisa. The VO puts it inside the funeral-story frame. The map puts swords at Pisa, not Luna, which is consistent.
- No unsupported claim was found beyond these.

## FINDINGS

### 1. Story / new VO
Script `raw/script-vo-v4-LOCKED.txt`: md5 ff97caaa, 244 words (v3: 225).

Diff vs v3-LOCKED:
- L04 is now the atlas line (ALT-A2).
- L08 is "Then, on Hastein's orders, his companions staged their grief. They said he was dead, and wished to be buried in the city."
- L11 "This was not Rome" → "This wasn't Rome".
- v3 L12–14 (Dudo / William / "legend got wrong") are replaced by L12–16: the strangest mistake, no captain in the annals, Dudo gave Hastein the sword, William placed Björn aboard, wrong Rome / wrong Viking.
- The tagline is unchanged.

The story read is covered under COLD VIEWER READ.

### 2. Captions vs script
- 49 caption lines. Their text equals the script minus the tagline: 236 = 236 words, exact.
- The tagline appears on the outro card as on-screen text, not as a caption (OCR at 99.0 and 101.5).
- OCR (rapidocr) of all 49 caption events: all correct. The only differences are ö read as o and spacing artifacts. No duplicates or missing lines.
- MarginV is 400 by default (y ≈ 1410–1525), 615 on P07 and 860 on P13.
- Directive 19 is met: on P13 the caption "Mid-funeral, Hastein" sits above the mail (mail y ≈ 1080–1360). On P05 the captions sit over North Africa, clear of every label.
- **ASR small.en:**
  - raw WER **2.04%** (5 / 245);
  - the errors are Hastein → haestain/hastain ×2 (proper noun), past → passed (homophone), baptised → baptized (spelling), and one decoder duplicate "city." at 51.42 (p = 0.0005);
  - **content WER ≈ 0.4%**.
- **ASR medium.en:**
  - Chunked run 3 gave raw 8.98%, but 10 of its 22 errors come from one chunk, 58.4–63.25, which returned nothing. Re-running that span with a 0.2 s earlier start (58.2–63.4, or 56.0–63.4) transcribes the whole line: "Mid-funeral, Hastine leapt from the coffin and struck the bishop down." (no-speech 0.01). So the drop was a chunk-boundary decoder failure, not audibility.
  - Corrected raw WER ≈ **5.3%** (13 / 245). The errors are all Hastein spellings (hastine/hastin/steinn/haszteyn/hastings), past/passed, baptized and "dudow", plus one stray "h" insertion.
  - **Content WER ≈ 0.4%**.
- "armour" is recognised by both models (p 0.48 small / 0.37 medium; the margin is high at 30 dB, so the low confidence is about pronunciation, not masking).

### 3. VO audibility over the continuous score
Margin = VO over bed, per word, in dB. Bands are house K-weighted / 1–4 kHz / phone 300–8 kHz.
- Stems: `stem_v4_voonly.wav` and `stem_v4_bedonly.wav`.
- My recomputation matches Atelier's `margins_v4.json` exactly (max diff 0.0 dB).
- A render-based bed (render − VO) agrees within ~0.3–0.9 dB.

| Worst words | house | 1–4 kHz | phone |
|---|---|---|---|
| "leapt" @60.294 | **6.7** | 7.2 | **7.4** |
| "the" (coffin) @60.747 | 17.2 | **6.8** | 10.3 |
| "Rome." @93.43 | – | 6.9 | – |
| "walled" @26.32 / "a" @26.21 | 24.8 / 20.1 | 7.8 / 7.9 | 23.0 / 21.1 |
| "and" @35.01 | 9.0 | 15.6 | 10.0 |
| "and" @61.35 | 10.4 | – | 7.9 |
| "have" @38.6 | – | – | 8.7 |

- **No word is under 3 dB in any band.** The film minima are **6.7 / 6.8 / 7.4**, up from v2's 4.1 / −5.7 / −0.1.
- **From 54.77 s to the end** the minima are leapt 6.7 (house), "the" 6.8 (1–4 kHz) and leapt 7.4 (phone).
- **81–82 s:** v4 has no "a" words here. The words are "The oldest surviving funeral story", and all are well above 10 dB.
- **"leapt" hit:**
  - the bed's 1 ms peak is at **60.285** (−11.2 dBFS), +18 ms after the P14 cut (60.267) and −9 ms before "leapt" (60.294);
  - bed RMS is −34.4 before (59.90–60.26), **−19.3 in the 200 ms hold**, −24.2 at 60.47–60.72 and −31.0 at 60.75–61.2;
  - the hit is intact (owner-approved) and re-ducks before "the coffin".
- **Duck only under VO:** the bed is −29 to −38 dB (100 ms envelope) under speech and swells 5–8 dB in gaps (N8). The release is 700 ms. There is no word-rate pumping. The P16 −6 dB plateau is present.
- **Constant level:** LRA 2.6 LU; one continuous track from the coffin attack to the end (directive met).
- **Outro:** the bed is ~−38 to −43 under the tagline and fades to digital silence at the end.
- Tagline margins:
  - We 27.8 / 11.7 / 21.4
  - remember 28.2 / 19.6 / 25.8
  - the 29.1 / 21.8 / 29.5
  - rest. 24.6 / 23.0 / 25.0
  - victors. 22.4 / 20.1 / 21.3
  - "Viking." @96.13: 12.4 / 10.0 / 11.0

### 4. P05 on a phone (15.433–25.933)
Phone simulation is in ev01 (390 vs 540 wide); label crops at 1080 are in ev02.
- **Label sizes:** see FIX-2. The **phone call is FAIL for Pisa, Provence, Strait of Gibraltar and Rhône at 390 wide; marginal at 540.**
- **Labels shown:** all are place names (West Francia, Emirate of Córdoba, Strait of Gibraltar, Mediterranean Sea, Kingdom of Italy, Provence, Pisa, Rhône). No fabricated text, and no Luna label ✓.
- **Swords:**
  - Camargue appears ~22.4, Valence by 23.0, and Pisa by 25.2 (not yet at 24.4);
  - **nothing is drawn at Luna** ✓ (the build asserts > 12 px from Luna);
  - the route **ends solid** about 27 px from the Pisa dot ✓;
  - dotted legs mark uncertain or legendary segments, and solid legs mark the documented ones.
- **Ship vs words** (template-matched):
  - enters from the Atlantic at ~17.2;
  - passes the Strait at 18.6–19.0 ("Spain," 18.457–19.119) ✓;
  - crosses the Mediterranean at 19.2–21.0 ("Mediterranean," 19.757–20.628) ✓;
  - reaches the Rhône mouth at ~21.6 ("struck" 21.353, "France," 22.212–22.770) ✓;
  - holds there while the red route traces up the Rhône;
  - crosses to Pisa at 23.4–24.2 and arrives at 24.2 ("Italy." 24.325–24.906) ✓.
- The **Pisa sword appears ~0.3–0.9 s after "Italy." ends**. That is acceptable.
- The animated map itself is owner-approved and not relitigated.

### 5. Cuts
- Scene detect (frame-diff) finds 21 cuts, all single-frame hard cuts, matching `cuts_v4.json`: 2.733, 5.433, 11.567, 15.433, 25.933, 30.433, 32.200, 37.067, 40.267, 43.933, 48.133, 52.033, 56.633 (P13 internal), 60.267, 63.367, 67.300, 72.933, 80.433, 87.967, 92.167, 97.433.
- **Every cut is in a word gap.** The one edge case is 15.433 (N6).
- **P13 cut vs "armour":**
  - the cut at **f1699 = 56.633** comes 6 ms after "wore" ends (56.627) and **41 ms before the json onset of "armour" (56.674)**;
  - in the waveform, "wore" decays to −44/−52 dB rel by 56.62–56.64 and "armour" energy returns at 56.65–56.66;
  - so the cut sits in a ~30 ms trough, **~17–27 ms before the audible onset** (ev03);
  - P13 zoom is 1.300 → 1.305 (no fast vertical move; directive item 11 met).
- **Plate durations of concern:**
  - **P07 1.767 s (FIX-1)**;
  - P11 4.200 s (N1);
  - the next shortest are 2.700 s (2.733–5.433) and 2.733 s (0–2.733); all others are ≥ 3.1 s;
  - long plates (P05 10.5 s animated, P17A 7.5 s, P17B 7.53 s) have motion and carry the VO.

### 6. Title over P03
Covered in N2. Placement and timing pass; the content and length notes are logged only.

### 7. Anatomy / fabricated text on new or changed plates
- **P03 title area:** clean; Björn's face is unobstructed.
- **P06 (t26.5–29.5):** Hastein seen from behind, braid and hood; the walled city across the water. It is water-only, with no landing (directive met).
- **P11 (t44.5/47.5):** mourners' raised hands have five fingers; hands on faces are plausible; there are torches and ships. OK.
- **P13 mail detail (t56.7/59.5):** the hand gripping the cloak is a well-formed four-finger grip, with mail under the cloak. OK.
- **P17A (t74–79):** the hooded captain's hand on the tiller is OK. Oars and rowers are OK. The fleet's sails are plausible.
- **P17B (t81/87):**
  - the carriers' hands on the poles are OK;
  - the body's clasped hands rest over the sword grip and the crossguard is plausible;
  - a city gate and Italianate tower are behind.
- **P18 monk (t90):** the brush hand is OK. The book shows a cross only.
- OCR over 20 full-res frames plus P05 found **no text other than captions, the title, map place names and the outro card**.
- **No "ILLUSTRATIVE RECONSTRUCTION" anywhere** ✓. No fabricated text ✓.

### 8. Post pack
`rough_v4/POST-PACK-CREDITS.md` has a "ROUGH v4 update" section:
- runtime 1:41.9 ✓ (matches 101.933 s);
- file `bjorn_rough_v4.mp4` ✓;
- the credit line;
- "No SFX" ✓;
- IM Fell (OFL) ✓;
- **Cover: owner's choice (pending)**.

The backup is `.bak_2026-11-03_from-rough_v2`.

Status: **current, apart from the pending cover**. `rough_v1/POST-PACK-CREDITS.md` is stale (it points to v2 and says "Cover: not picked"). It should be retired or made to point to v4.

### 9. Cold watch at 540 wide
Done on stills and downscales at every plate. Captions are fully legible at 540. The title is legible. P05 small labels fail (FIX-2). Everything else reads.

## INFORMATION BUDGET
- 244 words in 101.9 s is about 2.4 words/s, dense but steady.
- The heaviest stretch is the P05 atlas line (19 words over 10.5 s of moving map with eight labels). Because the labels can't be read on a phone, the eye has nothing to anchor on, which adds to FIX-2.
- The second reversal (72.9–97.4) introduces three new sources in 25 s (Frankish annals, Dudo, William). Each gets its own plate, so it holds.

## UNANSWERED QUESTIONS (cold viewer)
1. Who is Hastein to Björn? (Only inferred until ~80 s.)
2. Was the body on the bier the same coffin? (N3)
3. Why are there swords at Valence? (Not voiced. The map shows it silently, which is fine as texture.)

## SCORE READ
- One continuous Uprising bed runs from the coffin attack to the end, as directed.
- The "leapt" hit lands at +18 ms after the cut and holds for 200 ms, then the bed re-ducks before "the coffin".
- Under-VO ducking is clean. The gap swells act as breaths, not pumping.
- The outro bed sits under the tagline and fades to silence.
- **Audio PASS.**

## Evidence (`examiner-v4/`, 0.75 MB total)
- `ev01_P05_last_phone_390_vs_540.jpg`: P05 final frame at 390 and 540 wide.
- `ev02_P05_label_crops_fullres_Pisa_Provence_Strait_Rhone_Italy_Francia.jpg`: label crops at 1080. Shows the FRANCIA "F" on the coast and the clipped Gibraltar.
- `ev03_P13_cut_f1698_f1699_vs_armour_onset.jpg`: frames 1698 and 1699, with a 10 ms VO envelope showing the cut, "wore" and the "armour" onset.
- `ev04_P06last_P07_plate_1.767s.jpg`: the P06 last frame and the P07 plate.
- `ev05_title_over_P03_t6.0_t8.5.jpg`: title reveal and title in full.
- `ev06_P14_P17A_P17B_continuity.jpg`: Hastein at P14 vs the P17B bier, and the P17A captain.

All temp work was in `/tmp/exbj4/` and has been deleted.

---

## v4b focused recheck (Examiner, Nov 3, 2026, ~1:00 PM ET)

Scope: v4 FIX-1/2/3 only, plus regressions from the +0.5 s insert. Not a full re-prosecution.
Input: `renders/bjorn_rough_v4b.mp4`, `QA_rough_v4b.md`, `qa_v4b/`, `ARCHIVIST-v4-CHECK.md` §5.

### VERDICT: **PASS WITH NOTES**. All three v4 FIXes are closed. Nothing blocks.

### Measured
- **File:** md5 e0c31c7fa5c12682c8a56de53971a978 ✓. 1080×1920, 30 fps, 3073 frames (+15 vs v4), **102.433 s** ✓. ebur128: **I −13.9 LUFS**, LRA 2.6, **TP −4.2 dBTP** ✓.
- **FIX-1 (P07) CLOSED:** P07 now runs frames 913–981 = **2.267 s** (was 1.767).
  - Cut in at 30.433 s. "barred." ends at 31.927 (cut is +773 ms after it). The P07→P08 cut is at **32.700**, 110 ms before "So" at 32.810. The cut sits in the word gap ✓.
  - Inserted VO is silent: peak −62 dBFS over 31.95–32.75.
  - Score segment 1 plays straight through. The bed stem has 0 lag through 43 s, so there is no edit in the music.
  - Bed above 8 kHz over 31.5–33.5 s: median −73, max −61.7 dB, so **no click**. The mix in the gap is −31 to −35 dB RMS (bed only). The one HF spike is the "S" of "So".
- **Downstream offset is exactly +0.5 s:**
  - Video, v4 f967+ vs v4b f982+: lag 15 frames gives mean diff 0.010. Lag 14 or 16 gives 0.77.
  - P13 (v4 f1561–1807 shifted +15) is **bit-identical**.
  - Frames 0–462 and 778–912 are identical to v4. P05 differs only in label pixels (see below).
  - Audio xcorr lag is 0.000 for 0–31 s and 0.500 for 31–95 s. Residual after alignment: −39 dB / −37 dB.
  - VO stem matches v4 within 0.0008 after the shift. Of 244 words, 79 moved by 0 s and 165 by exactly +0.5 s.
- **All 21 cuts are single-frame and in word gaps.** The one exception is 15.433 (P05 in), which is still 52 ms into the tail of "there.", same as v4 (see N6).
  - P13 internal cut at **57.133**: +6 ms after "wore" (57.127), −41 ms before "armour" (57.174). Unchanged from v4 ✓.
- **"leapt" hit:** the bed is bit-identical to v4 shifted by +0.5 s.
  - Sample peak at **60.790 s (−12.1 dBFS)**: +23 ms after the cut (60.767) and −4 ms before "leapt" (60.794) ✓.
  - The QA's figures differ from my v4 report only in averaging method. It is the same signal.
- **Plates:** shortest is **2.267 s (P07)**. **No plate ≤ 2 s** ✓. P11 is still 4.2 s.
- **Captions:** 49 events, text identical to v4 = script minus tagline (236 words). The first 16 events are unchanged; 33 are shifted +0.5/+0.5.
  - OCR spot-check on the render: 31.0 "But the gates / were barred." · 32.4 none · 32.9 "So Hastein sent word" · 37.8 "The bishop and / count could" · 57.2 "wore armour under / their tunics." · 60.9 "leapt from / the coffin and" · 69.0 "This wasn't Rome." · 81.2 "The oldest / surviving funeral" ✓.
- **Margins** (my script reproduces Atelier's `margins_v4b.json` to 0.0 dB). **No word is under 3 dB.**
  - Worst words: house leapt@60.794 **6.7** · 1–4 kHz the@61.247 **6.8** · phone leapt **7.4**.
  - Render-based (bed = render − VO): 7.3 / 7.1 / 8.1.
  - Around the insert, every word is ≥ 11.9 dB ("So" 26.8 / 24.3 / 24.4). After 54 s the minimums are the same as the worst words above.
- **FIX-2 (P05 labels) CLOSED:**
  - Connected-component heights at 1080 (incl. serif/halo): WEST / FRANCIA / EMIRATE / CÓRDOBA caps 27–29 px · Mediterranean M ≈27 · Strait / Gibraltar caps ≈25, x-height ≈15 · Pisa P 23–25 · PROVENCE ≈24 and Rhône R ≈23–24 (deskewed 2× crops). This matches Atelier's claimed 23–28 px.
  - Phone legibility by eye: at 390 wide, WEST FRANCIA, KINGDOM OF ITALY, PROVENCE, Pisa, EMIRATE OF CÓRDOBA, Strait of Gibraltar and Mediterranean Sea are all readable. At 540 all are comfortable.
  - **Rhône** is the weakest (thin italic). It is readable by eye at 390. OCR at 1080 reads "Rbone" (circumflex present) (N2).
  - OCR at 390 also gets FRANCI(A), PROVE(NCE), Córdoba, Strait of / Gibraltar, Mediterranean Sea.
  - **No new fabricated or misspelled text.**
  - FRANCIA now sits entirely inland on the blue, clear of the coast ✓. Gibraltar is set on two lines on the Andalusian shore and is not clipped ✓.
  - Pixel-diff mask v4→v4b at f560 / 640 / 700 / 777: **only label pixels changed**. Ship path, route line, swords and their timings are unchanged from v4. P05 sits before the insert, so word-lock is unchanged: swords at Camargue / Valence / Pisa, nothing at Luna, and the route ends solid at the Pisa sword ✓.
  - The NW-of-Pisa specks I flagged in v4 are no longer visible; the PROVENCE lettering now covers that area.
- **FIX-3 (L04 countersign) CLOSED:** §5 "Countersign: v4-LOCKED with ALT-A2 (2026-11-03 12:05pm ET) … COUNTERSIGNED ff97caaa". It covers the script file md5 ff97caaa20d2238fddc30c7bdb4a0c8a (244 words; only L04 differs from v4c). The L04 text is "…past Spain, into the Mediterranean, then struck southern France, and finally raided Italy." with ruling PASS, DOCUMENTED (AB 859/860). On-disk script md5 = ff97caaa ✓. ARCHIVIST-v4-CHECK.md md5 is 7946193c.

### NOTES (non-blocking)
- **N1. PROVENCE label reaches into Italy** (end frame f777 = 25.9 s, ev07 middle).
  - The label is rotated 22°. Its "…VENCE" runs over the Ligurian Alps and the head of the Gulf of Genoa, i.e. Kingdom of Italy territory where "OF ITALY" sat in v4, and ends next to the Pisa sword.
  - At "finally raided Italy" (≈24.1–25.9 s), the ship rests directly under the word PROVENCE.
  - Fix: shift or shorten the label ~60–80 px west/south-west so its east end stops near the Var/Nice. Atelier's QA itself calls this "interpretation", so Archivist should eyeball it.
- **N2. Rhône is the thinnest label.** OCR reads "Rbone" at 1080; it reads correctly by eye at 390. Optional: semibold or +2 px.
- **N3. Ship mast brushes "Gi" of Gibraltar** at f545–f555 (18.17–18.50 s, ≈0.33 s), while the label is still revealing. The label stays readable throughout and is clear from f558 (ev07 bottom). Minor; optional fix is to nudge the label 10–15 px up.
- **N3b. "Strait of Gibraltar" is set on land** (red Córdoba, Andalusian shore) rather than on the water. It is readable, but a cartographer would put it in the strait. Optional.
- **N4. Caption gap on the P07 tail:** "But the gates were barred." ends at 32.18 and the next caption starts at 32.81. That is 0.63 s with no caption (v4: 0.13). Intentional-looking beat. Fine, just noting it.
- **N5. Paperwork:** "Pending Archivist countersign" text is still in Scriptor's `raw/script-vo-v4-LOCKED-L04alt.txt` l.14 and `script-final.md` l.3. Route to Scriptor. Not an edit for Atelier.
- **N6. Carried from v4:** P05 cut still on the tail of "there." (15.433, −52 ms) · P11 4.2 s · title / coffin vs bier / mail-in-wide / cover items (v4 N1–N9) unchanged by design.
- **N7.** Margin floor is 6.7 dB ("leapt" vs its own hit). Unchanged from v4 and acceptable.

Evidence added: `ev07_v4b_P05_390end_Liguria_Gibraltar.jpg` (304 KB). Top: f777 at 390 wide, ×2 nearest. Middle: v4 vs v4b Liguria crop ×3. Bottom: f545–f565 Gibraltar/mast strip.
