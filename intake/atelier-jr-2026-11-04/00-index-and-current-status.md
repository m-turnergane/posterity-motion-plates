# 00 · Atelier Jr handoff: index and current status

Posterity desk → Atelier Jr (Cursor Cloud production agent). Compiled Wed 4 Nov 2026, ~11am ET, from box files only.
- Nothing here invents a number, setting, URL or approval. **UNKNOWN** means the fact is not recoverable from the box.
- Rules are tagged: Current owner-approved (with date) / Episode-specific / Provisional / Superseded / Unknown. The tag key is in 01.
- This package **complements** `GPT-CURSOR-AGENT-HANDOFF-2026-11-04.md` (the owner's brief). It supplies the desk facts behind that brief and corrects it where the desk record differs (see below).

## START HERE: operating order (owner's intended sequence)
| Step | What | Where |
|---|---|---|
| 1 | **Read the handoff:** this index, then 01 → 02 → 03 → 05. Read the GPT handoff for the owner's goals | this folder |
| 2 | **Set up your environment:** Python env, fonts, ffmpeg, Remotion. Get your own credentials for ElevenLabs, GitHub and Higgsfield from the owner; none are in this package | `06-…/ATELIER-ENGINE-NOTES.md` §2–4 |
| 3 | **Push the engine branch** to the existing private repo from `engine.bundle`. This is the **FIRST TASK section at the top of ATELIER-ENGINE-NOTES.md**. No new repo, no visibility change, no force-push | `06-…/ATELIER-ENGINE-NOTES.md` "FIRST TASK", `06-…/engine.bundle` |
| 4 | **Plan:** map the house law (gates 1–10) onto your workflow and list your input needs | `01-house-law/STANDING-LAW-longform.md`, 01 §3 |
| 5 | **Take the separate new video pack.** The Edward II prep docs are delivered **separately**, not in this package | `04-longform-pilot/README.md` (pointer + status) |
| 6 | **Connect to Higgsfield.** Note: long-form law §6 says "no autonomous image generation and no image API". The owner should formally amend §6 before any automated plate generation (see Decisions) | — |
| 7 | **Produce the draft** under the gates: shot list/plate packet (gate 4) before plates; Examiner passes; the owner approves the actual export | law §5 |

## Engine repo
| Item | Value |
|---|---|
| Repo | https://github.com/m-turnergane/posterity-motion-plates (private, existing) |
| Branch | `engine/consolidate-2026-11-04` |
| SHA | `c3a192dd240bd9c201a4eb7fa2e4abdd982be357` |
| Status | **NOT pushed.** Atelier Jr pushes it from the bundle as its first task (owner decision, 4 Nov) |
| Bundle | `06-…/engine.bundle`, md5 `5e8a9c2940bb02aea54e5e9d958600c7` |

- Everything else about the repo and commit (local commits not on the remote, merge caveats, commands): **see ATELIER-ENGINE-NOTES.md**. It is authoritative.

## Contents
| Path | What |
|---|---|
| `00-index-and-current-status.md` | This file |
| `01-channel-and-editorial-bible.md` | Premise, accounts/URLs, roles and authority, editorial standards, evidence categories and the claim ledger format, owner feedback, brand |
| `01-house-law/` | Verbatim: `STANDING-LAW-longform.md`, `edit-preferences.md`, `team-ops.md` |
| `02-recovered-chronicle-visual-bible.md` | Look, palette, continuity, 9:16/16:9 sizes and safe areas, unlettered masters, essential vs flexible, prompt template |
| `02-reference-paintings-and-prompts/` | 27 curated owner plates (best plates and unique outros per episode), episode prompt files, the house art bible, the recovered-chronicle law, template v2, avatar/banner |
| `03-editing-motion-map-audio-bible.md` | Editing, motion presets, the maps/atlas brief, typography, audio/LUFS/music law, the Björn worked example |
| `03-source-docs-bjorn-worked-example/` | Björn directive, QA v4–v4d, score plan, storyboard, script, countersign, motion system/presets, OWNER-ATLAS-BRIEF |
| `04-longform-pilot/README.md` | **Pointer only.** Episode prep lives at `/workspace/posterity/longform/edward-ii-feature/` (owner directive: kept separate) |
| `05-reference-renders-and-owner-feedback/` | `REFERENCE-PICKS.md` (picks + why, metrics, links, weak→fix), 7 video examples, verbatim owner feedback files |
| `06-technical-and-asset-manifest/` | **ATELIER-ENGINE-NOTES.md** (authoritative, by Atelier), **engine.bundle**, full asset CSV (759 rows, ~9.4 GB on the box, with md5), package checksums, rights/credits, README |

## Complete plate and outro archive
**The owner's Google Drive folder** backs up every plate and every unique outro. Link: **PENDING** (owner to supply). This package carries a curated box set only; the full box inventory is in `06-…/ASSET-MANIFEST-all-plates-outros-renders.csv`.

## Latest approvals and current status
- **Last published:** #34 Björn, "Wrong Rome, Wrong Viking? The Coffin Trick", Tue 3 Nov. YT 3:13pm ET, TT 3:16pm ET. IG link UNKNOWN.
- **Active episode:** the Edward II / Kent long-form feature (about 12 min, 8 movements, 16:9). No superseding topic was found.
  - Script: `script-proposal-v1.md` + `raw/script-vo-v1-DRAFT.txt` (Scriptor, 4 Nov). 1,682 words, est. ~11:41. **DRAFT under Archivist countersign, NOT locked.**
  - Decision packet (i) owner answers: **not found** (treatment and sample, budget, Gregorian Chant, checkpoint).
  - No feature plates generated. The Mon 2 Nov checkpoint did not happen.
- **Owner-approved standing items:**

| Item | Approved |
|---|---|
| Long-form law | 30 Oct |
| Atlas brief + architecture change | 31 Oct, 9:01 / 9:44 / 11:07am |
| PLATE-PROMPT-TEMPLATE-v2 | 31 Oct, 1:40 / 1:43pm |
| Locked presets | 22–30 Oct |
| Chronicle Reveal v3.2b title | 27 Sep |
| Outro brand lock | 27 Sep |
| No IR text | 27 Oct |
| Oliver voice | — |
| −14 LUFS / ≤ −1 dBTP | — |

## Corrections to the GPT handoff (desk record differs)
| GPT § | GPT says / implies | Desk record |
|---|---|---|
| §2 | YouTube @PosterityArchive | That channel was **terminated 5 Oct**. Current: https://www.youtube.com/@posterity-archive (UC2P5EHjGTYziokzCgaSVHpw). TikTok https://www.tiktok.com/@posterity.archive. Instagram https://www.instagram.com/posterityarchive/ |
| §2 | Outro open to design | **Locked:** POSTERITY wordmark + narrated tagline ("History remembers the victors. We remember the rest.") over a unique background per episode (27 Sep; law §1–2) |
| §3 | Collaborators | Add the **Archivist** (owns the claim ledger) and the **Examiner** (story/rough-cut gate). Vellum is EIC (content direction and what ships), not only packaging. Specialists never DM the owner |
| §6 / §13 | Nano Banana Pro / Higgsfield generation | No desk record of the owner's image model: **UNKNOWN**. Law §6: "the owner generates every plate… no autonomous image generation and no image API". This **conflicts** with Higgsfield automation, so it needs an owner amendment |
| §7 | 1920x1080 30 fps as a fallback | It is **law** (30 Oct 5:27pm, law §2). No Short plate can be cropped to 16:9 within the 1.5x guardrail (2.04 px/px) |
| §8 | Maps | The 31 Oct atlas brief is binding: owner-painted atlas plate → Atelier registers it to geography and overlays animation; place names are the only text; ink evidence grammar; map classes (Explorer's Chart proposed for Edward) |
| §9 | Audio/caption presets unknown | Known: −14 LUFS / ≤ −1 dBTP; Shorts ASS caption spec; long-form = clean picture + **selectable CC track** (law §10). Voice, model and settings: see ATELIER-ENGINE-NOTES.md §9 |
| §10 | Pilot planning context | 8 movements exist (packet, 30 Oct); script v1 DRAFT exists (4 Nov, not locked). "30 vs 34" reconciles as 33–34 masters = 30 owner generations + 3–4 desk-built. Mon 2 Nov checkpoint did not happen. "The Letter to a Dead King" is the **Short's** title (owner-preferred, 29 Oct); **the feature title is UNKNOWN** |
| §11 | Björn lessons; Salem "continuity anchors" | Björn specifics are the v4b–v4d rulings (03 §6). The Salem anchor-plate claim is **not supported** by box files ("recognition anchor" in Salem is editorial). Anchors-first plate order is documented for **Björn** (3 Nov PASTE-ORDER) |

## Desk answers to GPT §16 "Unknowns"
| Unknown | Answer |
|---|---|
| TikTok / IG URLs | 01 §2; per-episode in 05. Björn IG: UNKNOWN |
| Pilot package / approval state | 04 README: packet (i) unanswered; script DRAFT |
| Eight movements | In the separate prep pack (packet (b)); not copied by owner directive |
| Plate ceiling | 33–34 masters / 30 owner generations (packet (e)). Owner approval: UNKNOWN |
| Title / outro templates | 03 §4; engine notes §7 |
| TTS / audio / caption presets | Engine notes §8–9; 03 §5. ElevenLabs effective speed: UNKNOWN |
| Licensed score | `06-…/rights/`. Long-form cue choice: UNKNOWN (packet (i) item 3) |
| Atelier source | `engine.bundle` → private repo (step 3) |
| Cloud tool availability; Higgsfield / ElevenLabs balances; spending cap; durable media destination | **UNKNOWN.** Owner to supply. Drive archive link PENDING |

## Gaps and UNKNOWNs (summary)
- **Links and archives:**
  - Drive archive link (PENDING)
  - Björn IG link
  - deployed website URL
- **Media not on the box:**
  - serial plates
  - Dracula and Blackbeard masters
  - Croatoan I/II and After Troy Ch1/Ch3 masters
- **Unclear uploads:** which Germanicus and which Jianwen file was uploaded.
- **Engine and audio:**
  - ElevenLabs effective speed
  - snow_v1b lock status
  - Remotion render unverified on the box
  - numeric 16:9 safe-area margins
  - exact per-episode accent hex values
- **Björn owner wording:** "glisten" / "funeral pan".
- **Feature status:**
  - feature title
  - gate 2 sign-off
  - Edward atlas plate not generated

## Owner decisions needed
1. Supply the **Google Drive archive link**.
2. **Image-API law vs Higgsfield:** amend law §6, or confirm the scope of step 6.
3. Answer **decision packet (i)**: treatment and the 3:05–4:55 sample; the ~34-master / 30-generation budget (~7.5–13.5 owner-hours, estimated); **Gregorian Chant** as a long-form section or all-new cues.
4. Feature **title**.
5. Atelier Jr's **sign-off authority** beyond Atelier's role; spending cap; media destination.
6. **Björn IG link**; the "Rhône" glyph ruling (OCR reads "Rbone").
7. Which **Germanicus** and **Jianwen** masters were uploaded.
8. Recover the **missing masters** (serials, Dracula, Blackbeard) into the Drive / manifest.
9. Confirm **Explorer's Chart** for Edward; confirm **depth_v1** stays off.
10. Approve rewriting the 16:9 hero prompts in **template v2** before the owner pastes them.

## Owner override: long-form law §6 for this experiment (Wed 4 Nov 2026, ~10:56am ET)
**Current owner-approved rule (episode/experiment scope).** The owner has directed that Atelier Jr connects to Higgsfield and produces the draft (operating order step 6–7). For the Atelier Jr long-form experiment this supersedes the ban in `STANDING-LAW-longform.md` §6 on autonomous image generation and image APIs. The rest of §6 stands: the owner remains the creative gate, review is one compact style/motion sample before the main spend and then a full review cut, and nothing is published by the agent. The Shorts pipeline is unchanged (the owner generates the plates).

## Owner-supplied links (Wed 4 Nov 2026, ~11:03am ET)
- **Complete plate + unique-outro archive (Google Drive):** https://drive.google.com/drive/folders/1oSSP805SIUXEVhGBA7ytg3vkcpegHR9w (replaces PENDING above)
- **Video dump (Google Drive, partial, not every video):** https://drive.google.com/drive/folders/11_Rx49M2UUJByXAsZOwUFUjIpD45ncy_
- **Björn Ironside #34 Instagram:** https://www.instagram.com/p/DfSuOk7qSH8/

## Drive archive (inventory Wed 4 Nov 2026, 11:05am ET)
- Read-only manifest: `06-technical-and-asset-manifest/DRIVE-ARCHIVE-MANIFEST.csv`. Summary, missing-item resolution and box duplicates: `06-…/DRIVE-ARCHIVE-SUMMARY.md`.
- Drive now supplies these masters: Dracula ROUGH v3.2, Blackbeard ROUGH v1, Croatoan Ch1 (ROUGH v4-motion) and Ch2 (ROUGH v2d), Croatoan Ch3 FINAL v1b, Edward II ROUGH v1c. **Still missing:** serial plates, After Troy Ch1 and Ch3 masters.

## ElevenLabs budget (owner screenshot, Wed 4 Nov 2026, 11:05am ET)
- Creator plan: 220,030 credits in total, 166,104 remaining. The long-form VO is about 1,715 words, roughly 10k characters, so one full pass costs about 10k credits. **Cap:** Atelier Jr stops and asks the owner before using more than about 30,000 credits on this draft.
