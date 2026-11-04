# 01 · Channel and editorial bible (Posterity)

Compiled by Grok Bot (desk handoff), Wed 4 Nov 2026 ET, from box files only. Every rule carries a tag:

| Tag | Meaning |
|---|---|
| **[CURRENT · owner · date/source]** | Owner-approved and in force |
| **[EPISODE]** | Applied to one episode only. Do not generalise it without an owner yes |
| **[PROVISIONAL]** | Proposed or implemented by the desk, never approved by the owner |
| **[SUPERSEDED]** | Replaced. The replacement is named |
| **[UNKNOWN]** | Not recoverable from the box |

"Proposed", "implemented", "approved" and "live" are kept separate. Implemented means it exists in code or a file. Approved means the owner said yes. Live means it was published.

Verbatim house sources are in `02-reference-paintings-and-prompts/` (art bible, recovered-chronicle law) and `01-house-law/STANDING-LAW-longform.md` (with `edit-preferences.md` and `team-ops.md`). Owner feedback files are in `05-reference-renders-and-owner-feedback/owner-feedback-verbatim-files/`.

## 1. Premise
- **What the channel is.** Posterity is a history channel built from short vertical documentaries (Shorts / TikTok / Reels). It has started its first long-form feature (Edward II / Kent, 16:9).
  - Each film is a real story told from the record, and every claim is weighed. The decision packet's viewer promise for the feature is "a real political thriller told from the records, with every claim weighed."
  - **[CURRENT · owner · DECISION-PACKET-v1 (a), pending the packet (i) answer]**
- **The look: the Recovered Chronicle.** Painted, candle-lit "recovered" plates with restrained motion, and maps built from real geodata. **[CURRENT · owner · Recovered Chronicle law 16 Sep; art bible]**
- **Formats.**
  - Shorts: 9:16, 1080x1920, 30 fps.
  - Long-form: 16:9, 1920x1080, 30 fps, stereo.
  - The 16:9 spec is **law, not a fallback**. **[CURRENT · owner · 30 Oct 5:27pm, STANDING-LAW-longform §2]**
- **Roster.** Standalones, micro-anomalies (<60 s) and serials (After Troy I–IV, Croatoan I–III). Serial law and the Examiner gate apply. **[CURRENT · owner · Serial law; Examiner gate 2 Oct]**

## 2. Accounts and URLs (desk ledger; the IDs were read by public scrape and not re-checked today)
| Platform | Handle / URL | Status |
|---|---|---|
| YouTube | https://www.youtube.com/@posterity-archive (channel UC2P5EHjGTYziokzCgaSVHpw) | Live. New channel since 19 Oct (publish-log) |
| YouTube (old) | @PosterityArchive | **Terminated 5 Oct.** Do not use it. The Sep 23 website draft still links it |
| TikTok | https://www.tiktok.com/@posterity.archive | Live |
| Instagram | https://www.instagram.com/posterityarchive/ | Live |
| Website | UNKNOWN. A page draft exists (Sep 23); no deployed URL was found | UNKNOWN |

Per-episode links are in `05-reference-renders-and-owner-feedback/REFERENCE-PICKS.md`.

## 3. Roles and authority (`ledger/team-ops.md`) [CURRENT · owner]
| Role | Agent | Owns |
|---|---|---|
| Owner (Muhammad Gane) | n/a | Final quality gate on the rough cut, credentials, spend and strategy. **Generates every plate and posts every video by hand.** Nothing is deleted without his yes |
| Vellum (EIC) | Cursor agent 2801856 | Content direction, what ships, packets, law files, and the only route to the owner |
| Archivist | 2972944 | Discovery, fact-check, **claim ledger** |
| Scriptor | 2972950 | **Sole owner of the script** |
| Atelier | 2972958 | VO, visuals, edit, masters, engine |
| Pulse | 2972961 | Analytics, publish-log |
| Examiner | 0eac0731-80d5-48d4-85e6-c4b7801100a0 | Story and rough-cut review gate |
| **Atelier Jr** (new) | Cursor Cloud production agent | Production under Atelier's role. Sign-off authority beyond that is UNKNOWN, so the owner should state it |

- Specialists never DM the owner. Everything goes through Vellum. **[CURRENT · owner · team-ops]**

## 4. Editorial standards
- **Story first.** The opening states the contradiction in both narration and image within the first 5 s. Use several purposeful visual beats; a crop, zoom or fire preset alone does not count. **[CURRENT · owner · Edward OWNER-DIRECTION-v3, 29 Oct; also the Retention/Motion/Score law, 27 Sep]**
- **No standalone intro before the hook.** The title lockup rides over the opening cuts. **[CURRENT · owner · edit-preferences]**
- **Causal context gate.** The viewer must know why each beat matters before the next one arrives. **[CURRENT · owner · 1 Oct]**
- **Never invent anything.** No invented motives, dialogue, encounters or certainty.
  - Example: the Edward amendment says "NO invented encounter at an emptied funeral hearse".
  - **[CURRENT · owner · Edward OWNER-AMENDMENT-v3b, 29 Oct 12:05pm]**
- **Keep source distinctions on screen and in VO:** documented, chronicle, contested, legend. Narrate legend as legend ("one chronicle claims…"). **[CURRENT · owner · v3b amendment; recovered-chronicle three-layer grammar 16 Sep]**
- **No "ILLUSTRATIVE RECONSTRUCTION" text and no status labels on picture.** **[CURRENT · owner · 27 Oct; long-form law §1]**
  - The old System E on-screen labels are **[SUPERSEDED]** for long-form by "no status labels / no IR text".
- **The TTS reads a spoken script** (`raw/script-vo.txt`, with numbers and names written out), not the display script. **[CURRENT · owner · 27 Sep]**
- **Hard cuts by default.** **[CURRENT · owner · edit-preferences]**
- **Asset reuse.** Reuse a recognisable composition for callbacks, for example Edward's Corfe composition for the letter's revelation. **[CURRENT · owner · 19 Sep; v3b]**

## 5. Evidence categories and the claim ledger
- **Statuses** (long-form law §4): established / attributed / disputed / inference / **OPEN**. **OPEN blocks narration.** **[CURRENT · owner · law §4]**
- **House band:** DOCUMENTED / CONTEMPORARY CLAIM / INTERPRETATION / UNCERTAIN / LEGEND. **[CURRENT · desk/house · CLAIM-LEDGER-v1 header]**
- **Ledger row fields:** claim_id, proposition, source_type, locator, seen (FIRST-HAND / SECOND-HAND), status, band, permitted narration wording, reviewer.
  - The Archivist owns every row.
  - Quotes are machine-checked against `raw/*.txt` (`python3 raw/_verify_quotes.py`).
- **Map evidence grammar:** documented = continuous ink; reported = broken, lighter line; approximate = shaded area. **[CURRENT · owner · OWNER-ATLAS-BRIEF 31 Oct]**
- **Shorts:** the Archivist countersign (`ARCHIVIST-COUNTERSIGN-*.md`) gates the script. An example is `03-source-docs-bjorn-worked-example/claims-v2-countersign.md`.

## 6. Owner feedback: how it arrives and how to treat it
- Owner reviews come through Vellum as VERBATIM files (`OWNER-DIRECTION-*`, `OWNER-AMENDMENT-*`, `OWNER-REVISION-*`, `OWNER-ROUGH-DIRECTIVE-*`).
- They are binding for that episode **[EPISODE]**. They become house law only when the owner or Vellum files them in `ledger/edit-preferences.md` or a STANDING-LAW file.
- Copies are in `05-…/owner-feedback-verbatim-files/`:

| Episode | Files |
|---|---|
| Edward II | v3 direction + v3b amendment |
| Björn | revision + rough directive, 3 Nov |
| Báthory | narration v3 + gate notes, 31 Oct |
| Croatoan | Ch I review; Ch II review + restructure |
| Ugarit | directive |
| Germanicus | v5 |
| Jianwen | v2 |
| Seven-cut review | 8 Oct |

**Recurring owner themes, as evidenced in those files:**
- an immediate contradiction in the hook
- a human centre
- consequences that feel consequential
- an ending on reversal or payoff
- no exposition dumps
- every visual beat purposeful
- maps that read clearly
- source honesty

## 7. Brand
- **Outro (locked).** POSTERITY wordmark plus the narrated tagline, over a **unique background for each episode**, about 3–4 s. Long-form uses one brand outro. **[CURRENT · owner · brand lock 27 Sep; law §1–2]**
- **Voice.** Oliver (ElevenLabs voice ID `jfIS2w2yJi0grJZPyEsk`), with the narrated tagline. **[CURRENT · owner · law §1]**
  - The model, settings and chain are in `06-…/ATELIER-ENGINE-NOTES.md` §9. That file is authoritative.
- **Locked avatar and banner:** `02-…/AVATAR_LOCKED.png`, `BANNER_LOCKED.png`.
