# 03 · Editing, motion, maps, typography and audio bible

**Authoritative technical source:** `06-technical-and-asset-manifest/ATELIER-ENGINE-NOTES.md`, written by Atelier. It covers exact preset md5s, the mix chain, ElevenLabs settings, fonts, registration and commands. When this file and the engine notes disagree on a number, **the engine notes win**.

This file adds the editorial layer: what the owner approved, when, and what is still open. Tags follow 01. Worked-example sources are copied verbatim into `03-source-docs-bjorn-worked-example/`.

## 1. Editing
- **Story first.** The hook comes first. There is no standalone intro; the title lockup rides over the opening cuts. **[CURRENT · owner · 16 Sep / 27 Sep]**
- **The opening.** Several purposeful, individually legible and visually distinct beats in the first 5 s. **[CURRENT · owner · Edward v3 / v3b, 29 Oct]**
- **Cuts and stills.** Hard cuts by default. No long holds on one painting; Edward's owner note rejects a 7 s hold on the funeral plate. **[CURRENT · owner]**
- **Retention / Motion / Score law, 27 Sep.** Motion and score serve the beat. **[CURRENT · owner · edit-preferences]**
- **Long-form story discipline:**
  - no chapter cards
  - one brand outro
  - runtime of 11–13 min, set by the audio-only read
  - **[CURRENT · owner · law §1–3]**

## 2. Motion
- **Restrained and story-motivated.** Static shots and slow pushes are the core. No micro-shake, fake handheld or kinetic filler. **[CURRENT · owner · 16 Sep]**
- **Camera:** a push of 1.00→1.06. **[CURRENT · engine notes §6]**
- **Locked presets:** torch_v1c, fx_candle, smoke_v2, water_v1 and dust_v1. Every lit plate gets flicker (long-form law §1). **[CURRENT · owner-locked 22–30 Oct · engine notes §6]**
- **depth_v1:**
  - The engine notes list it as "LOCKED 2026-10-30, opt-in, OFF by default".
  - DECISION-PACKET (f) says "Depth layers and restrained camera: R&D. Not used".
  - **Treat it as OFF for the feature unless the owner says otherwise. [PROVISIONAL]**
- **snow_v1b:** lock status **UNKNOWN**.
- **Guardrails:**
  - Refuse more than 1.5 output px per real source px.
  - Fire FX only on sharp native fire.
  - One named waiver exists; add no new waivers.
  - **[CURRENT · engine notes §6]**

## 3. Maps
- **Built from real geodata only:** Natural Earth, ETOPO1, OHM, plus the desk REALMS and MAP-PLACES files. **[CURRENT · owner · 19 Sep; atlas brief]**
- **OWNER-ATLAS-BRIEF, 31 Oct** (verbatim copy at `03-source-docs-bjorn-worked-example/HOUSE__OWNER-ATLAS-BRIEF-2026-10-31.md`):

| Time (ET) | Brief point | Tag |
|---|---|---|
| 9:01am | "Living Chronicle Atlas": zoom-aware medallion markers, collision-aware label hierarchy, vermilion/iron-red/oxblood ink routes. 16:9 is primary for long-form, with native 9:16 built from the same spec (not a crop) | [CURRENT · owner] |
| 9:44am | The procedural base map is **not approved**. Use strong realm pigments, 75/25 political/terrain | [CURRENT · owner] |
| 11:07am | **ARCHITECTURE CHANGE:** the owner paints the atlas plate against a desk geo reference. Atelier registers it to geography (control points / warp) and overlays routes, labels, markers and camera. Geodata stays the truth | [CURRENT · owner] |
| — | Map classes: Imperial Atlas / Explorer's Chart / Chronicle Artifact | [CURRENT · owner] |
| — | Explorer's Chart for Edward | [PROVISIONAL · Vellum proposal] |
| — | Evidence grammar: continuous ink = documented; broken, lighter line = reported; shaded area = approximate. No status text. Place names are the only text | [CURRENT · owner] |

- **Acceptance test from the brief.** A short Edward excerpt in 16:9 and 9:16, reviewed with real narration. **Not yet run [UNKNOWN whether scheduled].**
- **Worked example: Björn P05 atlas.**
  - An owner-painted plate registered to LAEA geography. The fit is similarity, not TPS (engine notes §5).
  - A word-locked ship.
  - IM Fell English SC labels.
- **Edward:**
  - The atlas refpack v2 is ready (engine R&D on the box: `/workspace/posterity/engine-rnd/maps/atlas/refpack/`, not copied; episode-specific).
  - **No owner-painted Edward atlas plate was found on the box: UNKNOWN / not yet generated.**
  - The procedural Edward maps v1 reel (30 Oct) predates the brief: **[SUPERSEDED R&D]**.
  - Not included here (episode R&D; see the Atelier map R&D folders on the box).

## 4. Typography
| Element | Spec | Tag |
|---|---|---|
| Title | Chronicle Reveal v3.2b: Source Serif Pro Semibold 78 px, caps, RGB (243,237,224) on an oxblood painted strike (#5A1A18 / #3A0E0C / #6E2A1C). topPercent 16 by default (Björn 31, on owner instruction "move title down 15%"). Timing from anchor f174: strike 8–26, manifest 14–42, hold 42–142, exit 142–162 | [CURRENT · owner · STANDING LOCK 27 Sep; Björn ruling 3 Nov = EPISODE] |
| Shorts captions | DejaVu Sans 54 bold, white, outline 4, shadow 2, bottom-centre, MarginV 400. Phrase chunks of up to 7 words in 2 lines of ≤24 characters. No karaoke. Text must equal the VO words. No captions on the outro | [CURRENT · owner-approved on published Shorts · engine notes §8] |
| Map labels | IM Fell English SC / French Canon. Place names only | [CURRENT · owner · atlas brief] |
| Long-form subtitles | **Clean picture plus an optional, selectable YouTube CC track (SRT/VTT).** No burned captions | [CURRENT · owner · law §10] |

## 5. Audio
| Item | Value | Tag |
|---|---|---|
| Voice | Oliver, ElevenLabs voice_id `jfIS2w2yJi0grJZPyEsk` (model and settings: engine notes §9) | [CURRENT · owner · law §1] |
| Voice (old) | Katherine, interim | [SUPERSEDED by Oliver] |
| Spoken script | `raw/script-vo*.txt`, a TTS spelling separate from the display script | [CURRENT · owner · 27 Sep] |
| Loudness | **−14 LUFS integrated, ≤ −1 dBTP** (source: `bathory__SCORE-LOCK-v3.md`; engine notes §9) | [CURRENT] |
| Measured | Björn v4d −14.0 LUFS / −4.2 dBTP / LRA 2.6. Báthory v3c about −14.1 / −4.2 to −4.4 dBTP | measured |
| VO over bed | VO about 10–14 dB above the bed (Björn: bed 12 LU under); sidechain duck | [CURRENT · house practice] |
| Long-form music | **Up to three score sections:** Act I mystery, Act II political danger, Act III investigation and aftermath. Crossfade on phrase boundaries. A **rights record for every cue** | [CURRENT · owner · law §9] |
| Music rights | CC-BY cues with verbatim credit in the descriptions (`06-…/rights/`) | [CURRENT] |

**Music on recent Shorts**
- Björn: "Uprising" (Scott Buckley)
- Báthory: "Anabasis I" (Scott Buckley)
- Edward Short: **"Gregorian Chant" (Kevin MacLeod)**, CC BY 4.0

**Long-form cue selection: UNKNOWN.**
- Whether "Gregorian Chant" may be one of the three sections is **packet (i) item 3: unanswered**.

## 6. Björn worked example (#34, published 3 Nov)
**How it got there**
- **Sources:** `OWNER-ROUGH-DIRECTIVE-2026-11-03.md` (10:34am), `OWNER-REVISION-2026-11-03.md`, and QA for v4, v4b, v4c and v4d.
- **The path:** v2b (weak; preview in 05) → v3 → v4 → v4b → v4c → **v4d** (published).

**Owner items**
- The directive's P0–P2 items are verbatim in the directive file.
- **P06 masked water** and the **P13 rapid zoom**: these are the desk's mapping of the "glisten" and "funeral pan" items. **The owner's exact words were not found on the box: UNKNOWN.**

**v4c rulings (a)–(e)**
- (a) PROVENCE label moved west.
- (b) The ship holds at Pisa.
- (c) The Gibraltar label sits on the water.
- (d) The Rhône stroke is thicker. **OCR reads it as "Rbone", so the circumflex glyph needs a ruling: OPEN.**
- (e) P17A gets the full proof treatment, with the figure matted.

**v4d changes**
- one continuous "Uprising" run
- P11–P13 levels rising
- the P05 Pisa label moved to (866,822)

**Final:** −14.0 LUFS / −4.2 dBTP, 102.433 s.
