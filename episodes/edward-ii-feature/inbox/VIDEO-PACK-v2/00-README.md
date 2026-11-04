# VIDEO PACK v2.1: Edward II / Edmund, Earl of Kent (first long-form)

**v2.1 (2026-11-04, after 12:50pm ET): repinned in place to script v3.2 LOCKED.** The owner approved Edward II script v3.2 as is at 12:50pm ET. Canonical VO: **sources/raw/script-vo-v3.2-LOCKED.txt** (md5 11f4e6f9ac7d640d006dac33533472f6, 101 lines, 1,884 words; byte-identical copy of the desk's raw/script-vo-v3.2-PROPOSED.txt). Claims: **sources/CLAIM-LEDGER-v3.2.md/.json** (8e824c98 / c654b495), countersigned in sources/ARCHIVIST-SCRIPT-v3.2-CHECK.md (480224d8). **Script v2 (852babf5) and script v3 (4e8996e0) are SUPERSEDED**, as are ledger v3 and V3-PROPOSAL-IMPACT.md (resolved in V3.2-ADOPTION-RESOLVED.md). Pre-v2.1 backup: /workspace/tmp/vp2/pre-v3.2/. Changes: CHANGELOG-v2.md §v2.1. The folder name stays VIDEO-PACK-v2.

v2 is VIDEO-PACK-v1 plus the fixes from the GPT review of 2026-11-04 (reviews/gpt-2026-11-04/). v1 is unchanged at ../VIDEO-PACK-v1/. Every change is listed in CHANGELOG-v2.md.

## Docs and media
- **This pack and its DOCS zip are docs only.** The media archive is a **separate download**: 10 independent MEDIA zips, each under 24 MiB, prefix `VIDEO-PACK-v2-MEDIA/`. They hold atlas guides, geodata, score MP3s, the Short reference plates and the T01 photos. See ASSET-TRANSFER-INDEX.md/.csv for the per-file md5s, the REQUIRED/OPTIONAL/REGENERABLE/MISSING status of each file, and how to get it.
- Code is not duplicated here. It lives in the engine repo bundle that already went to Atelier Jr: `06-technical-and-asset-manifest/engine.bundle`, branch engine/consolidate-2026-11-04, HEAD c3a192dd. That covers the renderer, components, PRESETS.md, Chronicle Reveal v3.2b, the outro builder, cartography scripts and OFL fonts.
- Owner Drive folders: plate archive https://drive.google.com/drive/folders/1oSSP805SIUXEVhGBA7ytg3vkcpegHR9w, video dump https://drive.google.com/drive/folders/11_Rx49M2UUJByXAsZOwUFUjIpD45ncy_
- **The full channel/desk handoff is still needed.** This episode pack does not replace it.

## Precedence (highest first)
1. Owner messages from 2026-11-04, as recorded in PILOT-OVERRIDE-v1.md and DECISION-BUNDLE.md.
2. PILOT-OVERRIDE-v1.md (the operative law for this pilot). It overrides the conflicting STANDING-LAW-longform clauses on image/API generation, per-plate owner generation and locked motion presets. All other law stands.
3. This README, then SHOT-LIST v2 and PLATE-PROMPTS v2 (SHOT INTENT governs; the old MOTION HANDOFF blocks are v1 suggestions), then MAP-PACK v2, REGISTRATION-PLAN-v2.1, LONGFORM-HOUSE-INTRO-BRIEF, SCORE-PLAN and STYLE-SAMPLE.
4. sources/ (read-only copies). Claims: **sources/CLAIM-LEDGER-v3.2.md (md5 8e824c98…)**, keyed in this pack by line ID (see SHOT-LIST.json claims_note). CLAIM-LEDGER-v3 and older are SUPERSEDED.

## Approval state
- Approved: acts (11:49), Higgsfield generation by Atelier Jr (10:38), score pool, ~12-min target, intro direction (12:39), outro (12:40), **act cards APPROVED 12:41** (CB1 leaf with only "ACT I/II/III" centred, pen-stroke write-in; no subtitles), map rule (12:44). All times are ET.
- Script **v3.2 APPROVED by the owner (12:50pm ET) and COUNTERSIGNED by Archivist** (sources/raw/script-vo-v3.2-LOCKED.txt). Script v2 (raw/script-vo-v2-DRAFT.txt) and v3 (raw/script-vo-v3-PROPOSED.txt, script-proposal-v3-SURGICAL.md) are SUPERSEDED and kept for the record only. **No VO edits here; any VO change voids the countersign.**
- Open owner items: the one yes/no plan, the title pick, the tagline-on-screen pick and the wordmark master. All are in DECISION-BUNDLE.md.
- Nothing has been generated yet.

## Budget and sequence (owner, 12:35pm ET)
- **No budget constraints for the sample phase.**
- Sequence: **sample → owner gate → full film only after the owner's go-ahead.**
- One guardrail: **ask the owner before a plan upgrade or anything that would exhaust the account.**
- The full-film budget is decided at the go-ahead gate.

## Prompts
- PLATE-PROMPTS carries a **ready-to-paste Nano Banana Pro prompt for each plate**.
- **Atelier Jr writes the I2V prompts** from each plate's SHOT INTENT block: dramatic_intent, required_invariants and permitted_action. Atelier Jr also picks the model, method and fallback.

## IMPORTER RULE (review D6)
- VO comes **only from the canonical raw script** (sources/raw/script-vo-v3.2-LOCKED.txt: 101 lines, 1,884 words), one render per line ID (L01…L98, incl. L07a, L57a, L57b, L86a, L96a, L97a; L06, L61, L72 are cut).
- **Never generate VO from SHOT-LIST vo_text.** In v2.1, split shots carry only their own words, so vo_text concatenates to exactly the 1,884 script words (checked), but the render still comes from the LOCKED file. Map shots onto the recorded VO's word alignment by line ID and the "(part, N of M words)" marks.
- Re-time every TC to the recorded VO. All TCs in this pack are estimates.

## Structure and timing (v2.1 estimate 805.6 s = 13:25.6; v2 was 735.2 s)
- v2.1 TCs (words / 2.4 per s; no v3.2 VO recorded yet): title SC01 0:29.5, ACT I card SC02 0:34.0, ACT II card SC03 3:33.7, ACT III card SC04 7:39.6, outro S099 13:16.1, end 13:25.6. VO 791.1 s + cards 14.5 s. 110 shot-list rows (106 picture shots + 4 cards).
- Cold open L01–L05, then **house INTRO SC01+SC02** (7.5 s total). Ink spills and blooms across the aged leaf; the POSTERITY wordmark and the feature title write in letter by letter by pen-stroke (not a fade); the leaf settles into the ACT I card; the score runs continuously.
- Invariants: exact wordmark geometry, legible type, ink that reads as physical, no blotting over the type. See LONGFORM-HOUSE-INTRO-BRIEF.md.
- Act cards SC02/SC03/SC04 show only the act number (approved 12:41).
- **OUTRO S099 (9.5 s) on E01:**
  - the scene's mist is woven with ink
  - the POSTERITY wordmark writes in by pen-stroke (a bookend to the intro)
  - the narrator reads the tagline verbatim: "History remembers the victors. We remember the rest."
  - the score runs to a final fade
- The house title and the tagline outro are mandatory.
- v1/v2 TC offsets no longer apply; use SHOT-LIST v2.1 TCs.

## Maps (owner, 12:44pm ET; MAP-PACK §2c)
- Maps stay on the deterministic engine. **I2V never draws routes, labels or markers.**
- Optional **HYBRID LAYER TEST**:
  - an I2V atmosphere clip made from the approved map plate, with no camera move
  - composited under the engine's routes, labels and markers, with the realm masks kept
  - coastlines and borders must not drift; mask land and borders
  - drift of more than a few px means falling back to engine FX
- One test in the sample phase: ME1 (S030) if the optional Act II sample runs; otherwise a standalone 5 s test on AB.
- Registration authority: REGISTRATION-PLAN-v2.1 (homography). Route beats were re-timed for v3.2 in MAP-PACK §4b: ME3 and ME4 stay staged, ME4 now rides L73 (S074) with +2.07 s; MB1+MB2 run as one draw. No beat runs short. Map labels stay the v2 set (no new labels).

## House presets (from the engine PRESETS/house record; anything not recorded is UNKNOWN)
- **Narration (ElevenLabs):**
  - voice Oliver Silk `jfIS2w2yJi0grJZPyEsk`, model eleven_multilingual_v2
  - stability 0.5, similarity_boost 0.75, style 0, use_speaker_boost true
  - seed 1611, output mp3_44100_128, with-timestamps endpoint
  - speed UNKNOWN
  - `<break time="0.8s"/>` before the tagline
  - API key from env `ELEVENLABS_API_KEY` (never written down)
  - pronunciation per PRONUNCIATION.md
- **Retime:** comma pause ≤0.22 s, sentence ≤0.40 s, line ≤0.45 s; 48 kHz.
- **Mix:**
  - VO: highpass 70 Hz → +10 dB → acompressor −22 dB 2.2:1 att 6 / rel 140, makeup 2 → −14 dB 4:1 2/60, knee 3
  - bed 12 LU under the VO
  - sidechain duck: threshold 0.035, ratio 2.5, att 15, rel 700, knee 4
  - bus comp −16 dB 1.6:1 20/250 → alimiter 0.85
  - final −14 LUFS ±0.5, ≤ −1 dBTP
- **Delivery:**
  - libx264 preset slow crf 16 yuv420p +faststart, AAC 256k, never overwrite (-n)
  - long-form: no burned captions; SRT optional
  - publishing is manual, by the owner

## Content rules (unchanged)
- Nothing graphic.
- L31: no devil visual.
- L65 is never quoted on screen.
- Vercelli stays yearless.
- The Fieschi letter gets no archive name.
- OPEN claims (C02e, C11-b, C14b-b, C15, C16e-b, C17-b) are never shown as fact. C20 is disputed.
- On-screen text is limited to the intro, act numbers, map labels and the outro wordmark.

## Contents (changed in v2.1)
- SHOT-LIST.csv/.json (rebuilt for v3.2), PLATE-PROMPTS.md (v3.2 VO on every plate; new N21, optional N22, N23; N20 RESERVE), PLATE-MANIFEST.csv/.json, MAP-PACK.md §4/§4b, STYLE-SAMPLE.md, SCORE-PLAN.md, DECISION-BUNDLE.md, PRONUNCIATION.md, SOURCES-MANIFEST.csv, ASSET-TRANSFER-INDEX.md/.csv (new plate rows), CHANGELOG-v2.md §v2.1, V3.2-ADOPTION-RESOLVED.md (new), V3-PROPOSAL-IMPACT.md (marked RESOLVED)
- sources/ additions: raw/script-vo-v3.2-LOCKED.txt, CLAIM-LEDGER-v3.2.md/.json, ARCHIVIST-SCRIPT-v3.2-CHECK.md, script-vo-v3.2-diff-vs-v3.md

## Contents (new or changed in v2)
- 00-README.md, PILOT-OVERRIDE-v1.md, DECISION-BUNDLE.md, CHANGELOG-v2.md
- ASSET-TRANSFER-INDEX.md/.csv
- LONGFORM-HOUSE-INTRO-BRIEF.md
- SHOT-LIST.csv/.json, PLATE-PROMPTS.md, MAP-PACK.md, REGISTRATION-PLAN-v2.1.md, registration/register_atlas_h.py
- STYLE-SAMPLE.md, SCORE-PLAN.md, SOURCES-MANIFEST.csv, V3-PROPOSAL-IMPACT.md
- sources/ additions: ledger v3, v3 proposals, T01 licence JSON

(v2 note: PLATE-MANIFEST and PRONUNCIATION were unchanged from v1; both change in v2.1.)

## Missing
1. POSTERITY wordmark master: owner to supply.
2. Short plate b06: not on the box and not found in Drive.
3. A 16:9 Chronicle Reveal comp: v3.2b exists only as a 1080x1920 build. The long-form intro is a new component (see the brief).
4. OFL.txt for Source Serif Pro is not on the box.
5. (v2.1) No v3.2 VO has been recorded; every TC is a words/2.4 estimate.
6. (v2.1) New plates N21 (required) and N22, N23 (optional) are prompt-only; nothing generated.
