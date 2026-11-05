# QA: Björn ROUGH v4b (Tue 2026-11-03, EST)

This rough was requested at 12:02 EST: P07 length, P05 labels on a phone, the Luna dot check and paperwork, with nothing else changed. All work ran on the box. The user's computer was offline, no browser was used and no external calls were made. v4b needed no ElevenLabs call, because the existing v4 VO was retimed. Nothing was sent. Every v4 artefact is left intact (see the protected files below).

## Deliverable
- `rough_v4/renders/bjorn_rough_v4b.mp4`, md5 **e0c31c7fa5c12682c8a56de53971a978**
  - H.264 1080×1920 at 30 fps, 3073 frames, **102.433 s (1:42.4)**. v4 was 101.933 s (1:41.9), so v4b is +0.500 s. AAC audio.
- Loudness (ffmpeg ebur128 on the mp4): **−13.9 LUFS integrated, LRA 2.6 LU, true peak −4.2 dBFS** (v4: −13.9 / 2.6 / −4.3). The mix wav measures I −13.9 and TP −4.4, the same as v4. PASS.
- Captions: `bjorn_rough_v4b_captions.ass` (md5 37310099…). There are 49 chunks, and the text and MarginV of each match v4. Events from 32 s on are shifted +0.5 s; earlier events are unchanged.
- Contact sheet: `bjorn_rough_v4b_contact_sheet.jpg` (md5 7089707a…)
- Timing board: `rough_v4_prep/TIMING-BOARD-v4b.md` (md5 e9a7c904…). TIMING-BOARD-v4.md is unchanged.
- Builders (new copies; the v4 builders are untouched):
  - build/retime_vo_v4b.py
  - build/mix_bjorn_v4b.py
  - build/p05_rough_v4b.py
  - build/build_bjorn_rough_v4b.py
- Clips: `scratch/clips_v4b/`
  - 18 clips copied unchanged from scratch/clips/.
  - P05, P07 and P13 were re-rendered. P13 is bit-identical to v4, because its internal cut only moved with the timeline.

## 1. P07 duration (+0.5 s silence after "barred.")
- **Insert:** 24000 samples (0.500 s, 15 frames) at 32.0796 s in vo_bjorn_v4.wav, the quietest point of the "barred." → "So" gap.
  - The v4 VO gap is digital silence (floor rms ≈1e-7), so the insert is silence.
  - Samples before and after the insert are asserted bit-identical to v4.
  - Cross-correlation confirms a +0.500 s shift on "So", "leapt" and "rest.".
  - The script md5 ff97caaa was verified before the retime.
- **P07:** frames 913–966 (**1.767 s**) → frames 913–981 (**2.267 s ≥ 2.2**). It is the same push spread over 68 frames, so the end pose is identical: p07_v4_last.png and p07_v4b_last.png have the same md5.
- Every downstream cut, word and caption moves +15 frames.
- Evidence:
  - qa_v4b/p07_before_after.png (8-frame strips, v4 above v4b)
  - qa_v4b/p07_v4_last.png
  - qa_v4b/p07_v4b_last.png
- **"leapt" hit stays locked:**
  - The P14 cut is at 60.767 s (frame 1823; v4 was 60.267 s, frame 1808). "leapt" starts at 60.794 s.
  - The hit sits on the cut at track 127.0 s, the same cue point as v4. hit_under_vo is 5.95, as in v4.
  - The frame-diff spike is at frame 1823, with the same magnitude as v4 (44.1).
- **Score continuous:**
  - Segment 1 (track 60.0 s from 0 s) plays 0.5 s further into the cue across the new silence, with no edit or join added.
  - The later segments, automation and dips shift +0.5 s. Segments: [0–45.533 → track 60–105.533], [44.333–56.234 → track 5–16.901, −5 dB], [55.267–102.433 → track 121.5–168.666].
  - joins_after_hit = [].
  - From 46 s on, the mix equals v4 delayed by 0.5 s (max sample diff 0.0007).
  - Audio lag v4→v4b is 0 at 20 s and 0.5 s at 58, 59.5 and 90 s.
  - The worst VO-over-bed margins are unchanged: "the"@61.247 6.8, "Rome." 6.9, "leapt" 7.1.

## 2. P05 labels: phone legibility
The treatment and fonts are unchanged (IM Fell English SC for realms, IM Fell English for story labels, iron-gall ink, bone shadow or halo). Only sizes, positions and per-label halo gain changed. Italy's halo was raised to 0.70 over the Alps and Rhône's shadow to 0.45; the default is 0.42/0.30.

Cap heights below are measured at output 1080 wide, from appearance to the end frame. The realms (FRANCIA, Córdoba, Italy) stay the largest tier at 36–38 ref px.

| Label | v4 px | v4b px | Cap @1080, appear → end | Placement change |
|---|---|---|---|---|
| WEST FRANCIA (realm) | 24 | 38 | 26.2 → 27.8 | Moved inland: the "F" is off the coast, at bbox ref x 391–589, y 613–681 |
| EMIRATE OF CÓRDOBA (realm) | 24 | 38 | 26.2 → 27.8 | Same area, larger |
| KINGDOM OF ITALY (realm) | 24 | 36 | 24.9 → 26.3 | Stronger halo (0.70) over the Alps |
| PROVENCE | 19 | 33 (rot 22°) | 22.8 → 24.1 | Along the coast |
| Strait of Gibraltar | 16 | 33 (2 lines) | 23.0 → 24.1 | No longer clipped; moved to the Andalusian shore |
| Mediterranean Sea | 19 | 35 | 24.8 → 25.6 | Open sea |
| Rhône | 18 | 33 (rot 82°) | 23.7 → 24.1 | Along the river |
| Pisa | 16 | 33 | 24.1 | Snug to the Pisa dot (~12 px) |

All story labels reach ≥22.8 px cap when they appear and ≥24 px at the end frame.

- **Strait rationale:** the end-frame camera crops the Atlantic and the route fills the Alboran pocket, so the only clean ground that is not clipped is the Andalusian shore. The ship's mast brushes "Gi" during the wipe at about 2.9 s. This is transient and clear by 3.4 s.
- **Provence rationale:** a 22° rotation follows the coast. Its east end reaching toward Liguria is interpretation, in line with the Archivist's "boundary = interpretation" flag.

### Clearances
These are asserted in the build. Label ink must be ≥5 ref px from every route leg and ≥8 px from every dot, and it is rotation-aware.

| Label | Ink → nearest leg (ref px) | Ink → nearest dot (ref px) |
|---|---|---|
| FRANCIA | 59.0 | 58.8 |
| PROVENCE | 28.2 | 45.1 |
| Emirate | 31.3 | 276 |
| Italy | 102.6 | 102.6 |
| Strait | 9.7 | 425 |
| Mediterranean Sea | 44.9 | 280 |
| Rhône | 29.3 | 30.3 |
| Pisa | 12.5 | 12.5 |

- No label overlaps the swords or the ship at the check frames (3.4, 6.6, 9.4 and 10.4 s).
- **Caption zone:** label ink ends at output y ≤1268 and the captions sit at 1410–1525, so there is no overlap.
- The overlay-extent flag is unchanged from v4. The extent still reports y 1318 below the 1280 safe line, as in v4. It comes from 31–94 isolated route/grain specks that pass the 0.03 alpha mask threshold across x 84–998; no glyph or route stroke goes below 1280.

### OCR (rapidocr) and eye check at phone widths
Frames are taken from the final renders at P05 start 15.433 s + t. Rotated labels were OCR'd on deskewed crops.

| Label | v4 at 390/540 | v4b at 390/540 |
|---|---|---|
| WEST FRANCIA | "ERANCIA" / "RANCIA" | "FRANCIA" 0.91–0.98 |
| Strait of Gibraltar | "ioralta" (clipped) | "Strait of" / "Gibraltar" |
| Pisa | not read | "Pisa" |
| Mediterranean Sea | partial | "Mediterranean Sea" |
| PROVENCE | nothing | "PROVENCE" 0.96–0.97 (also at 1080) |
| Rhône | nothing / "R" | "Rbone" 0.77–0.94; the OCR reads the IM Fell "h" as "b", and it reads correctly by eye |
| KINGDOM OF ITALY | "Y" only | "KINGDOM" plus "OF ITALY"/"ITALY" 0.76–0.94 |

- **Eye check at 390 wide:** every v4b label is legible. Italy reads over the Alps with the stronger halo.
- Crops:
  - qa_v4b/labels_before_after_390.png and qa_v4b/labels_before_after_540.png (per-label v4 | v4b at phone scale, enlarged ×3 / ×2 nearest)
  - qa_v4b/phone_{390,540}_t{3.4,10.4}_v4_vs_v4b.png
  - qa_v4b/p05_v4_t{3.4,6.6,9.4,10.4}.png and qa_v4b/p05_v4b_t{…}.png (full frames)
- P05 clip: scratch/p05_rough_v4b/p05_test_v4b_silent.mp4 (md5 0753635f…), with its grabs and build_log.txt alongside.

## 3. Luna dot check
- **Finding:** no dot is drawn at Luna. There is no overlay dot near output (737,750) and no painted dot on the plate.
- What reads as a dot there is the Gulf of Genoa coast apex, with tiny pale plate specks of ≤4 px.
- The nearest real ink dot is the approved Pisa dot at output (812,786), now labelled snugly about 12 px away.
- The PROVENCE label in v4b now sits over the Luna area (its bbox contains the location), which further hides the specks.
- The only approved dots remain Camargue, Valence and Pisa.
- **Optional Vellum proposal (NOT applied):** a masked tone-down of the plate speck at ref ~(753,754), r≈4, in the overlay pass only, leaving the plate file untouched.

## 4. Archivist countersign (parent, 12:03 EST)
- The Archivist countersigned ff97caaa in ARCHIVIST-v4-CHECK.md §5 (md5 7946193ca492c2ca2ca819105ae5840a, verified).
- The "Pending Archivist countersign" text is in `raw/script-vo-v4-LOCKED-L04alt.txt` line 14. The older status line is in `script-final.md` line 3 and its `.pre-v2` copy.
- All of these are **Scriptor's files**, not ours, so they were **not edited**. To route: Scriptor to update the line to "Countersigned ff97caaa, ARCHIVIST-v4-CHECK.md §5".
- None of our own files carried the pending tag.

## 5. Paperwork
- `rough_v4/POST-PACK-CREDITS.md`:
  - Backed up first to POST-PACK-CREDITS.md.bak_2026-11-03_pre-v4b (md5 4b6a09c8…, the v4 version).
  - A "ROUGH v4b update" section was then appended: runtime 1:42.4 (102.433 s, 3073 frames). The credit is unchanged.
- `rough_v1/POST-PACK-CREDITS.md`:
  - Backed up first to POST-PACK-CREDITS.v1.pre-superseded-header.bak.md, a new name because POST-PACK-CREDITS.v1.bak.md already exists and is untouched.
  - A one-line "SUPERSEDED by rough_v4/" header was added at the top. Nothing else changed (verified by diff).

## Flags carried from v4 (unchanged)
- P11 is 4.200 s.
- P17A uses glints only, pending approval.
- P17B has no sky drift.
- The cover is the owner's choice.
- The P05 overlay-extent note is as above.
