# Báthory v2: SCORE CUE SHEET (DRAFT)
Status: **DRAFT, not locked.** script-v2.md and storyboard-v2.md are both DRAFT/HOLD for Vellum's gate and owner approval. All times are estimates at 2.55 w/s scaled ×1.10 for pauses and Oliver's read (the script estimates 76–80 s). **Every beat time is TBD** until Atelier measures the real VO. Pre-screened 2026-10-31 by the executor from metrics only: **no ear check yet.**
Inputs: OWNER-PROPOSED-VO-2026-10-31.md, script-v2.md (L02/L12 fixes), ARCHIVIST-CLAIMS-v2.md, storyboard-v2.md (11:43 ET; it supersedes the SKELETON's energy tags: B07 is now INTRUSION, B16 ISOLATION, B19 split ISOLATION→UNEASE, B14 carries the "Why?" pause), GATE-NOTES-2026-10-31.md, ledger/STANDING-LAW-one-primary-score.md, ledger/STANDING-LAW-retention-motion-score.md §5, ledger/edit-preferences.md.

## 0. How this map is meant to be used (one-primary-score law)
ONE composition plays continuously at constant gain from video t=0 (a single start offset into the track) through the end card. There are no cue changes, no per-beat offsets, no gain rides and no near-silence drops; the only dynamic processing is a sidechain duck under VO. The phase map below is therefore **the composition's own natural shape laid against the storyboard**. It was used to choose the track and its one start offset. It is **not** a set of edit instructions. Any second cue needs owner approval.

## 1. Selection

| Role | Track | Start offset | Why |
|---|---|---|---|
| **PRIMARY** | **"Ignosi", Kevin MacLeod**, ISRC USUAN1100450, 3:04, 79 bpm (catalogue). Feel: Dark, Epic, Intense, Somber, Unnerving. Trombones, basses, flutes, clarinet, marimba, percussion, horn, violins, violas. | **0:31** (×1.10 read). Use 0:29 if the read lands nearer ×1.15 and 0:35 if nearer ×1.0; re-fit once the VO is timed. | Best energy fit across read speeds (r = 0.57–0.61 against the storyboard-v2 energy curve). The **strongest passage of the window lands on the arrest**: B09 +6.6 dB and B10 +6.0 dB over the window median. It **alternates more than once**: dip at B01b (-5.2), rise at B07/B08, peak at B09–B10, ease at B11–B12, second rise at B13 (+5.5, the blocked trial), then UNEASE/ISOLATION settling to a low B20 (-3.9) and outro (-3.4). Real pulse through most of the window (onset autocorr. 0.33–0.48 per 10 s; one 0.18 window at track 1:30–1:40, i.e. B16–B19, where thinning is wanted). LRA 10.5 LU over the window. No silent head at the offset (-21 to -25 LUFS M at 0:28–0:31). Never used on the channel. Native 3:04 ≥ 0:31 + ~80 s + 10 s, so no loop and no stretch. |
| BACKUP 1 | **"Gagool", Kevin MacLeod**, ISRC USUAN1100443, 5:45. Feel: Dark, Eerie, Mysterious, Suspenseful, Unnerving. Contrabassoon, oboe, violins, percussion. | **1:20** (×1.10); fit-optimal 1:31 at ×1.15 (r 0.66), but that shifts the peak off B09. | Biggest contrast: B09 +8.6, B13 +9.5, B20 -9.5. **Weaknesses:** ISOLATION at B11–B12 stays loud (+4.8/+7.4), so there is no withdrawal at the verdicts; pulse is lower (0.15–0.42); and a natural **near-silence hole at track 2:33–2:34 (-42/-47 LUFS M)** falls in B20 and would break the no-drop law unless the offset moves. Long native (5:45) gives room to re-fit. |
| BACKUP 2 | **"Eyes In The Void", Scott Buckley**, 4:24, CC BY 4.0. Composer's description: "dark, chaotic orchestral... glitchy, high-suspense... gothic orchestral march". | **2:42** (the gothic-march half; avoids the quiet head and the glitch section). | **Strongest pulse** of the set (0.5–0.7): the fallback if the owner hears Ignosi as too soft. **Weaknesses:** nearly flat (±2 dB) from B02 to B19, so little withdrawal and the energy switches must come from the picture; withdrawal only at B20 (-5.4) and outro (-8.9). The page markets it as "cosmic horror", so check it for horror cliché by ear. Hot master (window -11.6 LUFS-I) needs about -13 dB static trim. Buckley's **Smart Content ID** claims unless the credit is in the description. Native 4:24 ≥ 2:42 + 80 + 10 s (only about 12 s spare; does not fit a ×1.25 read). Also screened (not chosen) for Atahualpa. |

## 2. Energy-keyed phase map: PRIMARY "Ignosi" @ 0:31 (draft; all beat times TBD)
"rel" = 1 s-mean momentary loudness (ebur128 M) over that span minus the window median (-25.0 LUFS). Arc names come from the gate notes: unease → restrained escalation → arrest pressure → withdrawal (verdicts, blocked trial) → unresolved final motif.

| Beat | Energy (storyboard-v2) | Arc phase | Video est. (TBD) | Track time | Native M LUFS | rel dB | Read |
|---|---|---|---|---|---|---|---|
| B01a | INTRUSION | hook | 0.0–2.0 | 0:31.0–0:33.0 | -26.3 | -1.3 | Audible from frame 1 (no silent head); the opening phrase is falling away. |
| B01b | ISOLATION | hook contrast | 2.0–3.9 | 0:33.0–0:34.9 | -30.2 | -5.2 | Natural thinning on "She was never tried." ✓ |
| B02 | UNEASE | unease | 3.9–6.5 | 0:34.9–0:37.5 | -27.7 | -2.7 | Low, suspended ✓ |
| B03 | (map) | unease | 6.5–8.8 | 0:37.5–0:39.8 | -25.2 | -0.2 | |
| B04 | INTRUSION | escalation | 8.8–11.4 | 0:39.8–0:42.4 | -25.2 | -0.2 | Weak spot: no lift. Foley carries this intrusion (§4). |
| B05 | UNEASE | unease | 11.4–13.4 | 0:42.4–0:44.4 | -25.2 | -0.2 | |
| B06 | UNEASE | unease | 13.4–19.0 | 0:44.4–0:50.0 | -25.2 | -0.2 | |
| B07 | INTRUSION | escalation | 19.0–23.3 | 0:50.0–0:54.3 | -23.4 | +1.6 | Restrained rise ✓ |
| B08 | UNEASE | escalation | 23.3–29.8 | 0:54.3–1:00.8 | -22.6 | +2.4 | Builds into the arrest |
| **B09** | **INTRUSION** | **arrest pressure (peak)** | 29.8–32.3 | 1:00.8–1:03.3 | **-18.4** | **+6.6** | Strongest section ✓ |
| **B10** | **INTRUSION** | arrest pressure | 32.3–36.9 | 1:03.3–1:07.8 | -19.0 | +6.0 | ✓ |
| B11 | ISOLATION | withdrawal (verdicts) | 36.9–39.3 | 1:07.8–1:10.3 | -22.0 | +3.0 | Pulls back ~3.5 dB from the peak, but it is a partial thinning, not a true withdrawal. Ear check needed. |
| B12 | ISOLATION | withdrawal | 39.3–43.1 | 1:10.3–1:14.1 | -22.4 | +2.6 | Same |
| B13 | INTRUSION | blocked trial (pressure) | 43.1–47.9 | 1:14.1–1:18.8 | -19.5 | +5.5 | Second rise ✓ |
| B14 | ISOLATION | "Why?" + pause | 47.9–49.5 | 1:18.8–1:20.5 | -22.7 | +2.3 | Eases. The pause sits in an un-ducked gap, so the bed swells back by release time. |
| B15 | UNEASE | withdrawal | 49.5–54.3 | 1:20.5–1:25.3 | -24.7 | +0.3 | |
| B16 | ISOLATION | withdrawal | 54.3–60.8 | 1:25.3–1:31.8 | -23.2 | +1.8 | |
| B17 | UNEASE | withdrawal | 60.8–64.7 | 1:31.8–1:35.7 | -27.7 | -2.7 | Thins ✓ (lowest-pulse window) |
| B18 | ISOLATION | "She died in confinement." | 64.7–66.4 | 1:35.7–1:37.4 | -27.1 | -2.1 | ✓ |
| B19a / B19b | ISOLATION → UNEASE | verdicts / legend | 66.4–69.9 | 1:37.4–1:40.9 | -24.9 / -24.6 | ~0 | |
| B20 | ISOLATION | **unresolved final motif** | 69.9–75.9 | 1:40.9–1:46.9 | -28.9 | -3.9 | Lowest stretch (min -35.8 M at 1:43, not a hole). The music continues past here, so it does not resolve. Whether the harmony is open needs an ear check. |
| Outro | card + narrated tagline | tail fade | 75.9–79.4 (+3–4 s card, TBD) | 1:46.9–1:50.4 (+) | -28.4 | -3.4 | Constant dB/s fade under the card, landing on a beat (79 bpm ≈ 0.76 s grid; fade start TBD). |

Alternations: INTRUSION→ISOLATION→UNEASE at 0–6 s; then UNEASE→INTRUSION→withdraw→INTRUSION→withdraw from 19 to 50 s. That is two full pressure/withdraw cycles plus the hook contrast ✓.
Backup maps (same columns): `score/analysis/phasemap_sbv2_macleod_gagool_off80_x1.1.csv` and `score/analysis/phasemap_sbv2_sb_eyes_in_the_void_off162_x1.1.csv`.

## 3. Mix: house spec
- **Master:** -14 LUFS integrated, **true peak ≤ -1.0 dBTP** (past masters: limiter at -3.5 dBFS, about -14.1 LUFS, -1.7 to -3.4 dBTP; both satisfy this spec). VO forward.
- **Static bed trim (constant, set once):** Ignosi window is -23.2 LUFS-I, native TP -0.2. Start at about -1 dB so the un-ducked bed sits around -24 LUFS-I, then adjust by ear ("substantially louder" but ducked, 2026-09-19). Gagool window -18.4 → start about -6 dB. Eyes window -11.6 → start about -13 dB. Final values TBD.
- **Sidechain duck under VO only** (house settings): threshold 0.015, ratio 1.5–3, attack 200–300 ms, release 600–800 ms, lookahead 75 ms. Target **VO 12–14 LU above the bed** under speech and **key words ≥ 9 dB over bed peak**. Watch B09–B10 and B13, where the bed is +5 to +7 dB hotter: the duck must still hold 12 LU there. If it can't at ratio 3, lower the *static* trim; don't ride the gain.
- **No gain rides, no near-silence drops, no per-beat offsets.** The pauses ("Why?", the verdict lines) are un-ducked gaps, and the bed returns by release time.
- **Tail:** fade at constant dB/s under the closing brand card (about 3–4 s) and land on a beat. Native length is ≥ package + 10 s for all three, so no stretch or loop is needed.

## 4. Foley: only what the VO describes, weighted to INTRUSION
Precise and sparse, placed under VO or in its gaps, never louder than the key words. No screams, no gore, no stingers or impacts, nothing supernatural, no fire or pyre crackle (Archivist: no smoke column or pyre), no heartbeat, no whooshes. **All times TBD.**

| # | Beat | Energy | VO anchor | Sound | Notes |
|---|---|---|---|---|---|
| F1 | B04 | **INTRUSION** | "armed men entered her manor" | Horses slowing on frozen ground, then **approaching torches** (low flame flutter) and tack | Fills the music's flat spot at B04. Winter: frost and crunch, not mud. |
| F2 | B04→B05 | **INTRUSION** | "entered her manor" | **Manor door**: heavy latch, then the door swinging inward | One door only. It opens; nothing slams. |
| F3 | B05 | UNEASE | "as she sat down to supper" | **Supper table**: chair settling on stone, a single pewter cup or cutlery set down | Quiet and domestic; establishes the room that B09 breaks. |
| F4 | B09 | **INTRUSION** | "Now his men were arresting her." | **Boots** on stone, several men closing in, plus torch flutter sweeping the room; a chair pushed back as she rises | No struggle, no blade draw (storyboard: no drawn blade on her). This is the densest Foley beat. |
| F5 | B10 | **INTRUSION** | "taken to Bytča" | Cart wheels on frozen ground, guards' boots, one door closing at distance (the closed Bytča door) | Nothing beyond the door. No torture sounds. |
| F6 | B12 | ISOLATION | "confined in the fortress above her manor" | **Key turning in a lock** / iron bolt sliding home, once | The single confinement sound. Not a "walled-up" brick sound. |
| F7 | B13 | **INTRUSION** (blocked) | "the king pressed for her trial, Thurzó prevented it" | Courier's horse at the gate; **gate shut** (one heavy wooden closure) | Matches the plate (gate shut on the courier, torchlight cut). |
| F8 | B18 | ISOLATION | "She died in confinement." | Optional: a candle snuff (a near-silent breath of the wick) | Only if it doesn't read as a cliché; drop if in doubt. |

**Not supported, do not add:** quill or seal (the VO describes no letter, seal or signing; Archivist and gate rule: no king signing, no sealed agreement); a gavel or court sounds ("verdicts" is abstract, and the trial never happened); crowd or execution sounds at B01a/B11 (empty square, no method); screams, chains parade, wind howl, wolves, bells as stingers.

## 5. Licences and credits (description; Buckley requires the description)
- **Primary:**
  "Ignosi" Kevin MacLeod (incompetech.com)
  Licensed under Creative Commons: By Attribution 4.0 License
  http://creativecommons.org/licenses/by/4.0/
  Changes: excerpted, EQ, level-shaped, faded, mixed under narration.
  Short form: `Music: "Ignosi" by Kevin MacLeod (incompetech.com), CC BY 4.0, http://creativecommons.org/licenses/by/4.0/`
- **Backup 1:** same format with "Gagool".
- **Backup 2:** `'Eyes In The Void' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au` (page states: "For YouTube videos, credits must appear in the video description. If you don't, you will likely get a copyright claim from me.")
- Evidence: `score/licence_evidence/incompetech_faq.html` (credit format), `incompetech_pieces_2026-10-31.json` and `incompetech_excerpt_ignosi_gagool.json` (catalogue title/ISRC/length), `scottbuckley_eyes_in_the_void.html`. The incompetech per-track pages load by JavaScript, so the catalogue JSON is the ISRC record.

## 6. Screened out (measured; see score/analysis/)
| Track | Why not |
|---|---|
| Gloom Horizon (MacLeod) | Best fit only r 0.21; it climbs and stays loud from about 0:39 with no withdrawal; 2:08 native leaves little offset room. |
| End of the Era (MacLeod) | Fit r 0.60, but pulse is weak (0.10–0.20 per 10 s): an elegiac drone in the window (fails retention §5). |
| Texture for Violincello and Pianoforte No. 2 | Low pulse (0.08–0.40); the cello/piano "jumble" leans eerie-horror. |
| Dark Times | 3–6 s silent head; low pulse (0.08–0.16 mid-track); funereal. |
| Satiate (only strings) | "Never lets the audience rest": no withdrawal; low pulse in most windows. Earlier screen-out (Dracula/Blackbeard). |
| Oppressive Gloom | LRA 3.8 (flat death march); earlier screen-out. |
| Drums of the Deep | LRA 4.7: constant drums, no ISOLATION; earlier screen-out. |
| Mary Celeste | Pulse 0.23; earlier screen-out. |
| Serpentine Trek | Negative fit (one long build); 1:47 too short. |
| Darkest Child, The Escalation, Impending Boom | Rejected on catalogue metadata (celesta horror cliché; a single long build; constant sixteenths). |

**Recently used, avoided:** MacLeod: Malicious, Immersed, At Launch, Crusade, Crusade - Heavy Industry, Rynos Theme, Lost Time, Magic Forest, Prelude and Action, For the Fallen, Chee Zee Caves V2, Virtutes Instrumenti, Ancient Rite, Desert City, Ancient Temple, Ancient Grudge, Wasteland Caravan, EmptyCity, Relics of Past, Deep Sea, Distant Tension, Failing Defense, Gregorian Chant, Ripples, Ossuary 6 - Air and Hellfire, The March of Devils Dome, Into the Ruined Temple, Eternal Terminal. Buckley: Memories Of Stone, Unraveling, Penumbra, Anabasis I. Nakarada: Before the Fall. OGA CC0: The Abyss, Ruins of an Ancient Culture, Hope, Return to Nowhere, A Dispirited Epic, Village Ruins, Eclipse Legion, Determined Pursuit, Dream 2, Dejected Overture.

## 7. Open / blocking
1. **Script not locked.** The VO and storyboard are DRAFT/HOLD for the gate and owner; the offset is re-fit after Oliver's read is timed (`score/analysis/phase_map_sbv2.py`, change SC/offset). This file stays DRAFT. A `score-cue-sheet.md` waits for the lock.
2. **No ear check.** Not yet checked: horror-cliché review, the "unresolved" quality of the B20 harmony, Ignosi's marimba/percussion colour (the title, like Gagool's, appears to come from King Solomon's Mines; check the colour doesn't read off-period for 1610 Upper Hungary), and Eyes In The Void's "glitch".
3. No Content ID pre-check done. MacLeod tracks are not normally in Content ID; Buckley's is (description credit required).
4. Weak spots in the primary: B04 (no musical lift, so Foley F1/F2 carries it) and B11–B12 (only partial thinning).
