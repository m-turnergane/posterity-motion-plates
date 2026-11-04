# Báthory v2: SCORE CUE SHEET (DRAFT r3)

r3 (2026-10-31, Toronto time) is r2 plus the owner countersign. r2 is untouched. Narration is LOCKED; beat times stay TBD until the VO is recorded and measured.

r3 changes:
(1) **Score LOCKED: "Ignosi" (Kevin MacLeod) is the only score (owner pick), from track 0:31, audible from video frame 1.** Gagool is **dropped** as a backup; no Gagool cue, preview row, credit or listening item remains in this sheet. (Its files on disk are kept, not deleted.)
(2) **B13 is split** (storyboard/motion plan r4): B13a, doors partly open (storyboard 39.2–41.8), hard cut to B13b, doors shut (41.8–43.5). **F7's IMPACT is synced to the B13a→B13b hard cut.** Recommended impact: **video 0:46.0 (track 1:16.98)**, in the percussion gap (§4 F7, §6 #6).
(3) **Fallback:** with a single shut-doors plate there's no swing sound; an optional low thud only.

The r2 text follows, with these changes applied.

---

Status: **DRAFT** (r3: the score choice is LOCKED to Ignosi; beat times and the F7 impact remain TBD until the VO is measured). This file supersedes nothing on disk: `score-cue-sheet-DRAFT.md` (r1) is kept unchanged, and no `score-cue-sheet.md` exists or should exist until the script locks. Timings are from `storyboard-v2.md` (DRAFT/HOLD) at 2.55 w/s ×1.10. **Every beat time is TBD** until the VO is recorded and measured. Prepared 2026-10-31 at about 12:00 ET from metrics only. **Nobody has listened to this audio**; §6 is the list for a human ear check.

r2 changes:
(1) Answers the gate's "immediate unease from 0:00" question with measured options A, B and C (§1).
(2) Vellum's 11:51 ruling: two owner-package preview clips (§2; r3 keeps only the Ignosi clip).
(3) **B13** is now Scriptor's INTRUSION flat beat: a Thurzó silhouette shuts the council-chamber doors at night, with no courier and no letter. F7 is now heavy doors shutting in a stone chamber.
(4) **B07** may be swapped to "Thurzó alone reading a folded letter by candle", so its Foley is quiet: paper and candle only.
(5) Content ID findings (§5). These **correct r1 §7.3**.

## 0. Clarification for the gate
"Ignosi from 0:31" means the **start offset inside the track**. The bed is heard **from video frame 1** (00:00:00), and track 0:31 plays at video 0:00. Nothing enters late. The rendered A preview is −13.0 LUFS momentary in its first 0.5 s, the loudest moment of its opening.

## 1. 0:00 unease: options measured (first 6 s of each 15 s bed-only preview, normalised to −14 LUFS-I / ≤ −1 dBTP)
Previews are in `score/r2/previews/`. Data is in `score/r2/first6s_compare.json`, `score/r2/opening_analysis.json` and `score/r2/phone_sim_first6s.txt`. The re-fit of B is in `score/r2/B_refit.txt`.

| | A: Ignosi @ 0:31 from video 0:00 (current plan) | B: Ignosi from its own 0:00 | C: low drone 0–4.5 s → Ignosi @ 0:31 |
|---|---|---|---|
| File | `A_ignosi_off0-31_15s_-14LUFS_bedonly.wav` | `B_ignosi_off0-00_15s_-14LUFS_bedonly.wav` | `C_drone-xfade_ignosi_off0-31_15s_-14LUFS_bedonly.wav` |
| Momentary loudness 0.5–3 s (preview scale) | −13.0, −13.2, −16.7, −16.9, −17.9, −19.7 (strong at frame 1, then a phrase decay) | −29.0, −21.1, −20.1, −19.5, −17.1, −15.3 (quiet start, swells in) | −25.4, −17.2, −16.2, −15.8, −13.1, −11.1 |
| Phone-speaker sim (HP 250 Hz) 0–3 s / 3–6 s | **−18.8** / −21.7 LUFS | −30.9 / −20.6 | **−36.0** / −23.4 |
| Spectrum, first 6 s | centroid 775 Hz; 39% <120 Hz, 42% 120–500, 19% 500–2k | centroid 468 Hz; 62% <120 Hz | centroid 139 Hz; 80% <120 Hz |
| Harmony, first 6 s | Pitch classes C#, G, A#, G#. Semitone-cluster 0.58, **tritone 0.44** (C#–G). Key fit 0.48: unstable, a Neapolitan/dominant colour against the piece's C minor | C, G, B (tonic pedal). Cluster 0.25, tritone 0.06. Key fit 0.71: **tonal, settled** | Drone = B's C pedal, consonant (cluster 0.24, tritone 0.08). Tension only from the C→C# semitone shift at the crossfade (3–4.5 s) |
| Reads as (metric-based, not heard) | **Tense from frame 1**, dark and mid-low, no brightness above 2 kHz | Low, calm and consonant, rising; "suspended" rather than uneasy | Darker but **consonant** for 3 s, nearly inaudible on phones, then A |
| Beat map | Unchanged (r1 map, §3) | **Breaks it.** Re-fit correlation at ×1.1 is −0.32 (A: +0.49). B09 arrest +0.6 dB, B10 −5.4 dB. The loudest 5 s lands at video ~79 s (end card). Best case ×1.0: B09 +2.1 only. **The arrest does not land on the loud section.** | Unchanged after 4.5 s |
| Rule conflicts (edit-preferences / one-score law) | None. One offset at t=0 is not a sequence-boundary seek. | Arrest energy lost; B19b–B20 loud, against the "unresolved, withdrawn" close | It **splices two points of the same track** (0:00 → 0:34) under the hook, which is close to "chopping/restarting the bed" in the one-score law, and two sources overlap for 1.5 s. Its 0–3 s is effectively an **inaudible open on phone speakers**, against "bed audible from t=0" and phone-speaker intelligibility. A low drone reads as an "intro" texture before the story (against "no standalone intro before hook"), though it is under the VO. Built from Ignosi's own material, so it is rights-clean and the same composition. **Needs owner sign-off as a head element.** |

**Recommendation: A, unchanged (Ignosi from track 0:31 at video 0:00).**
- It is the most harmonically tense opening of the three: the tritone and semitone clusters are the strongest measured.
- It is the loudest at frame 1, including on a phone speaker.
- It keeps the arrest on the swell, and it needs no rule exceptions.

Only production note: a 20 ms de-click fade at t=0, because the cut lands mid-sustain. This is not a fade-up. Its 2–3.5 s dip under "She was never tried." (B01b ISOLATION) is wanted.

If the owner hears A and still wants "darker", the lawful lever is the **offset**, not a head drone:
- Track 0:29 (cluster 0.44) starts 2 s earlier in the same phrase.
- Track 0:35 (G minor, cluster 0.56) is darker-tonal but shifts the arrest map ~4 s late.

Do not use C unless the owner explicitly approves it.

VO preview: **not rendered.** `v2/raw/` has only `script-vo-v2-DRAFT.txt` (text) and no temp VO audio, and the box has no TTS.

## 2. Owner-package preview clips (Vellum 11:51 ruling; these replace the 30 s ear-check excerpt)
Clip spec: 30.0 s, 48 kHz/24-bit, 0.5 s equal-power fades in and out, −14.1 LUFS-I, −1.5 dBTP (ebur128 true-peak).

| File | Source window | Why this start | Swell inside the clip |
|---|---|---|---|
| `score/ignosi_preview_30s.wav` | Ignosi track **0:39.8–1:09.8** | The B04 position on the r1/r2 map (video 8.8 s at offset 0:31). The storyboard says "the arrest lands by 12 s (B04 to B05)". | Rises from clip 0:14; **peak clip 0:23–0:25 (track 1:02–1:04 = B09 "Now his men were arresting her.")** |

**Ambiguity to flag:** the ruling says "starting at the arrest swell ... the track position that lands on the B04 arrest". In Ignosi, B04 itself is flat (r1 weak spot, rel −0.2 dB) and the swell is B09. I started at B04, as literally specified, so each 30 s clip runs from the arrest's arrival through its swell. If Vellum meant to start at the swell itself, re-cut from Ignosi 1:00.8. (r3: the Gagool preview is dropped with Gagool; the file is kept on disk.)

The previews are bed-only and normalised to −14 LUFS-I. In the mix, the bed sits about 12–14 LU under the VO, so these play much louder than the bed will.

Superseded but kept (no deletions): `score/r2/previews/EARCHECK_ignosi_track0-50_to_1-20_video0-19_to_0-49_30s.wav`. It still covers listening items 6–7 below, which the owner clip does not.

## 3. Energy-keyed phase map: PRIMARY "Ignosi" @ 0:31, storyboard-v2 timings ×1.10 (all TBD)
"rel" = 1 s mean of momentary loudness minus the window median (−25.0 LUFS); values as in r1. Percussion is from `score/r2/perc_scan_ignosi_0-31_1-53.csv`.

| Beat | Energy | storyboard-v2 est. | Video ×1.1 | Track | rel dB | Notes (r2) |
|---|---|---|---|---|---|---|
| B01a | INTRUSION | 0–1.8 | 0.0–2.0 | 0:31.0–0:33.0 | −1.3 | Tense chord from frame 1 (§1) |
| B01b | ISOLATION | 1.8–3.5 | 2.0–3.9 | 0:33.0–0:34.9 | −5.2 | Mallet/percussive accent ~video 0:02 (listen #1) |
| B02 | UNEASE | 3.5–5.9 | 3.9–6.5 | 0:34.9–0:37.5 | −2.7 | No percussion |
| B03 | MAP | 5.9–8.0 | 6.5–8.8 | 0:37.5–0:39.8 | −0.2 | |
| B04 | INTRUSION | 8.0–10.4 | 8.8–11.4 | 0:39.8–0:42.4 | −0.2 | Low-drum groove enters ~video 0:09. **Owner preview clip starts here.** Foley F1/F2 |
| B05 | UNEASE | 10.4–12.2 | 11.4–13.4 | 0:42.4–0:44.4 | −0.2 | |
| B06 | UNEASE | 12.2–17.3 | 13.4–19.0 | 0:44.4–0:50.0 | −0.2 | Strongest drum hit ~video 0:14 (listen #2) |
| **B07** | INTRUSION (picture may become quiet) | 17.3–21.2 | 19.0–23.3 | 0:50.0–0:54.3 | +1.6 | **May become "Thurzó alone reading a folded letter by candle".** Foley is quiet: paper and candle only (F-B07). The bed's restrained rise and mallet figures continue (listen #3–4). |
| B08 | UNEASE | 21.2–27.1 | 23.3–29.8 | 0:54.3–1:00.8 | +2.4 | Exposed mallet (likely marimba) 0:22–0:28 (listen #4) |
| **B09** | **INTRUSION** | 27.1–29.4 | 29.8–32.3 | 1:00.8–1:03.3 | **+6.6** | Arrest = swell peak ✓ (F4) |
| **B10** | **INTRUSION** | 29.4–33.5 | 32.3–36.9 | 1:03.3–1:07.8 | +6.0 | Drum+mallet hit ~0:36 (listen #5) |
| B11 | ISOLATION | 33.5–35.7 | 36.9–39.3 | 1:07.8–1:10.3 | +3.0 | Partial thinning only |
| B12 | ISOLATION | 35.7–39.2 | 39.3–43.1 | 1:10.3–1:14.1 | +2.6 | F6 key/bolt; percussion builds from ~0:42 |
| **B13a** | **INTRUSION** | 39.2–41.8 | 43.1–46.0 | 1:14.1–1:17.0 | +5.5 | **Doors partly open, lit chamber, Thurzó silhouette (DEPTH).** Carries the strongest percussion of the window (hits at track 1:14.55, 1:15.53, 1:16.49). No Foley swing; the doors are not animated. |
| **B13b** | **INTRUSION** | 41.8–43.5 | 46.0–47.9 | 1:17.0–1:18.8 | — | **Doors shut (FLAT), hard cut on the F7 IMPACT.** The cut lands as the percussion drops out (no hit from track 1:16.49 until a weak one at 1:18.07), so the door owns the moment and B14 "Why?" inherits the withdrawal. |
| B14 | ISOLATION | 43.5–45.0 | 47.9–49.5 | 1:18.8–1:20.5 | +2.3 | Percussion drops out (video 0:46–0:51), bed −23 M, no hole (listen #7) |
| B15 | UNEASE | 45.0–49.4 | 49.5–54.3 | 1:20.5–1:25.3 | +0.3 | |
| B16 | ISOLATION | 49.4–55.3 | 54.3–60.8 | 1:25.3–1:31.8 | +1.8 | |
| B17 | UNEASE | 55.3–58.8 | 60.8–64.7 | 1:31.8–1:35.7 | −2.7 | |
| B18 | ISOLATION | 58.8–60.4 | 64.7–66.4 | 1:35.7–1:37.4 | −2.1 | |
| B19a/b | ISOLATION→UNEASE | 60.4–63.5 | 66.4–69.9 | 1:37.4–1:40.9 | ~0 | |
| B20 | ISOLATION | 63.5–69.0 | 69.9–75.9 | 1:40.9–1:46.9 | −3.9 | Drum+mallet return ~video 1:10–1:13 (listen #8) |
| Outro | card + tagline | 69.0–72.2 | 75.9–79.4 (+card) | 1:46.9–1:50.4+ | −3.4 | Constant dB/s fade, landing on a beat |

Mix spec is unchanged from r1 §3: −14 LUFS-I, TP ≤ −1 dBTP; sidechain duck 0.015 / 1.5–3 / 200–300 ms / 600–800 ms / 75 ms lookahead; VO 12–14 LU over the bed; no rides and no drops.

## 4. Foley (only what the VO or plate describes; INTRUSION-weighted; all times TBD)
F1–F6 and F8 are unchanged from r1 §4. Changes:

| # | Beat | Energy | Anchor | Sound | Notes |
|---|---|---|---|---|---|
| F-B07 (new, conditional) | B07 | INTRUSION (quiet treatment) | L05 "king orders Thurzó"; plate: Thurzó reads a folded letter by candle (if Scriptor swaps it) | **Paper**: one fold opened, one soft handling rustle. **Candle**: a faint flame flutter at most | Quiet, under the VO. No quill, seal, wax or signing. r1 listed "quill or seal" as unsupported, and the Archivist/gate rule bans king signing or a sealed agreement; a letter *being read* is a plate choice for Scriptor/Vellum, and its Foley should stay with paper only. If the swap does not happen, B07 has no Foley (r1 had none). |
| **F7 (r3)** | **B13a→B13b** | **INTRUSION** | "the king pressed for her trial, Thurzó prevented it"; plates: doors partly open (B13a), then shut (B13b) | **Heavy doors closing in a stone chamber**: a short, heavy pre-swing/air of large wooden doors under the end of B13a, then the **IMPACT (wood on wood, the bar or latch dropping) exactly on the B13a→B13b hard cut**, and a short stone-room reverb tail into B13b | No courier, no letter, no hoofbeats. Weighty but not a stinger or impact sweetener. **Impact in a gap, not on a drum hit.** Sub-second HPSS onsets (Ignosi, track 1:12–1:22) put the heavy hits at track **1:14.55, 1:15.53, 1:16.49** (≈0.97 s apart), then nothing heavy until 1:22. The storyboard cut (41.8 ×1.10 = video **0:45.98**, track **1:16.98**) lands 0.49 s after the last hit, in the drop-out: the door transient stands alone instead of being masked by or doubling a drum. **Proposed impact: video 0:46.0 / track 1:16.98** (keep it within track 1:16.9–1:17.3, ≥0.4 s clear of 1:16.49). Alternative, only if the VO fit leaves B13b ≥1.5 s: the 'missing' next beat at track 1:17.46 (video 0:46.46), so the door lands where the drum would have been. Not on 1:14.55/1:15.53/1:16.49. Re-check after the VO is timed. Different timbre from F6 (iron bolt at B12): wood and stone room for F7. **Fallback (single shut-doors plate):** no swing sound; an optional low, soft thud at the B12→B13 cut only. |

Still not supported: gavel or court sounds, crowds or executions, screams, chains, wind howl, wolves, bells, fire crackle.

## 5. Content ID: findings (sources saved under `score/licence_evidence/`, fetched 2026-10-31)
**Correction to r1 §7.3.** r1 said "MacLeod tracks are not normally in Content ID". That is **out of date**.

1. **Kevin MacLeod / incompetech: his music is now pre-registered in Content ID, and claims are expected when the description credit is missing.**
   - The official page (https://incompetech.com/music/royalty-free/youtube-contentid.html, saved as `incompetech_youtube-contentid_2026-10-31.html`) says: "having the music pre-registered, it stops the baddies and bad data from claiming my music incorrectly."
   - It names the likely cause of a claim: "someone forgot to add the credit, or the credit was placed in the video itself, and the credit could not be read automatically".
   - The fix it gives: put "SongTitle" by Kevin MacLeod in the **text description** before disputing; the claim is "released within 72 hours and likely much faster".
   - Background: incompetech blog, 13 Jan 2026, "I'm switching publishers ... close a lot of loopholes people have been using to snipe my compositions" (https://www.incompetech.com/wordpress/2025-Dec-to-2026-Feb.html, saved). False third-party claims have hit specific titles (https://incompetech.com/wordpress/2025/04/whats-going-on-with-spotify/, saved). Ignosi and Gagool are **not** on that list.
   - The FAQ (https://www.incompetech.com/music/royalty-free/faq.html) says credits may go in the description *or* in the video. For Content ID, the description is what matters.
2. **Scott Buckley: in Content ID through a "Smart Content ID" system that scans the description for a credit.**
   - Source: https://www.scottbuckley.com.au/library/copyright-claims-release/ (saved): "This system scans the description of videos using my music looking for a credit. If no credit is found, the system places a copyright claim on the video."
   - The claimant shows as "We Are Era Music BV, claimed on behalf of Scott Buckley".
   - The scan looks for "Scott Buckley", "@ScottBuckley" or "musicbyscottb".
   - Release is via his form within 1 business day; false "Sentric Music Publishing" claims are a known issue.
   - The track page (`scottbuckley_eyes_in_the_void.html`) says: "credits must appear in the video description. If you don't, you will likely get a copyright claim from me."
3. **Unverified, inference only.** Creators on Reddit report MacLeod tracks claimed by "We Are Era Music BV" in Jul–Aug 2026. Sources: https://www.reddit.com/r/SmallYoutubers/comments/1uy3qmi/ and https://www.reddit.com/r/NewTubers/comments/1vq9ug0/; seen in search results only, because the direct fetch returned 403 and the saved `reddit_*.json` files are block pages. That is the same company that administers Buckley's claims, so it may be MacLeod's new Content ID administrator. **incompetech does not name its administrator**, so treat this as unconfirmed.
4. **Why this matters more for this video.** YouTube Help (https://support.google.com/youtube/answer/6013276, saved) says: "Shorts 1-3 minutes in length: Claimed videos will be **blocked** if there is an active claim applied, regardless of policy." At 76–80 s, this Short is in that band. **Any active claim, even a valid-licence one, blocks it until it is released.** Disputes give the claimant 30 days (https://support.google.com/youtube/answer/2797454).

**What we can verify without uploading:** licence terms, the credit format each composer's system expects, the claim policy each composer publishes, and that Ignosi is not on incompetech's published false-claim list (r2 also checked Gagool, now dropped).

**What we cannot verify without uploading:**
- whether Ignosi specifically has an active Content ID reference;
- whether the description scanner will accept our exact credit text;
- whether a third party has falsely registered the track;
- whether a claim would appear on a 30–80 s excerpt.

There is no public Content ID lookup. The only real test is YouTube's own check on an upload: upload the final as **Private**, with the description credit already in place, and wait for Studio's Copyright check before scheduling or publishing. That upload is an owner action and has not been done.

**Credit lines.** These must go in the **description** at upload time, not added afterwards:
- `"Ignosi" Kevin MacLeod (incompetech.com) Licensed under Creative Commons: By Attribution 4.0 https://creativecommons.org/licenses/by/4.0/`
- `'Eyes In The Void' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au`

## 6. Ear-check listening list (for a human; nobody on our side has listened)
Heuristic from HPSS. "Mallet" = percussive energy at 400 Hz–3 kHz (where marimba sits); "drum" = percussive energy below 200 Hz. Catalogue: Ignosi uses "Marimba, Percussion" and "starts without percussion, then adds in a groove later on". Times are video time at offset 0:31 (×1.1 map).

| # | Video | Track | In which file | What to listen for |
|---|---|---|---|---|
| 1 | 0:02 | 0:33 | A preview @ 0:02 | Mallet/percussive accent under the hook ("She was never tried."). Does marimba read off-period or "adventure" in the first 3 s? |
| 2 | 0:09–0:14 | 0:40–0:45 | owner clip 0:00–0:05; A preview 0:09–0:14 | Drum groove entry; strongest drum hit at video 0:14. Gothic-thriller march, or tribal/adventure? |
| 3 | 0:17–0:21 | 0:48–0:52 | owner clip 0:08–0:12 | Drum+mallet pulse going into B07, which may now be the quiet candle/letter plate. Does the pulse fight a still image? |
| 4 | 0:22–0:28 | 0:53–0:59 | owner clip 0:13–0:19 | **Main marimba check.** Mallet-band peaks with no low drum, so the marimba is likely exposed (B07–B08). Period colour and cliché check. |
| 5 | 0:36 | 1:07 | owner clip 0:27 | Drum+mallet hit at the B10→B11 turn (into the verdicts). Too punchy for ISOLATION? |
| 6 | 0:42–0:45 | 1:13–1:16 | EARCHECK file 0:23–0:26 | **Strongest percussion in the window, under B13a** (hits at track 1:14.55, 1:15.53, 1:16.49). r3: the F7 impact is placed after it, at track 1:16.98, on the B13a→B13b cut. Confirm by ear that it lands clear. |
| 7 | 0:46–0:51 | 1:17–1:22 | EARCHECK file 0:27–0:30 | Percussion falls away for B14 "Why?". Should feel like withdrawal, not a gap. |
| 8 | 1:10–1:13 | 1:41–1:44 | (not excerpted) | Drum+mallet return in B20, the closing ISOLATION. Does it undercut the unresolved ending? |

## 7. Open / blocking
1. The script is not locked, so the offset is re-fit after the VO is timed. This file stays DRAFT.
2. No ear check has been done (§6).
3. Content ID can only be confirmed by a private upload with the credit (§5); this is the owner's step.
4. B07 swap is pending Scriptor; F-B07 is conditional. B13 is settled as B13a/B13b (r3); the F7 impact position is re-checked after the VO is timed.
6. r3: Score LOCKED to Ignosi (owner pick). Gagool dropped.
5. Option C has not been approved and is not recommended.
