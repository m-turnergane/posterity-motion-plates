# STANDING LAW: Long-form (16:9 features)
Written by Vellum, Fri 30 Oct 2026, ~5:35pm ET. It carries the owner's long-form decisions of 30 Oct 2026 (5:27pm ET).

## 1. Scope and precedence
- This law covers **long-form 16:9 features only**. It changes nothing for Shorts.
- It **adds** to the house laws. Anything not covered here follows the existing Shorts laws and `edit-preferences.md`, unchanged. That includes Oliver as the voice (`jfIS2w2yJi0grJZPyEsk`) and the narrated house tagline "History remembers the victors. We remember the rest." It also includes these rules:
  - No on-screen status labels and no "ILLUSTRATIVE RECONSTRUCTION" text.
  - No chapter cards and no evidence stamps. Attribution happens in the narration.
  - Implied execution without gore is fine.
  - Every lit plate gets candle or firelight flicker with spill, plus real animation. A plain slow push does not count.
  - Cut plates that look slammed in.
  - The owner generates every plate and posts manually. Prompts arrive paste-ready.
  - Specialists never DM the owner.
  - Nothing is deleted without the owner's explicit yes, and anything is backed up before it is overwritten.
  - The opening veto, causal-context gate, Examiner v2 law and retention law all apply.
- **Only two Shorts laws are overridden:**
  - **Music** (§9). Up to three score sections instead of one score.
  - **Captions** (§10). Clean picture plus an optional YouTube CC track, instead of burned-in narrator captions.
  Shorts keep their single score and burned captions.
- Monetization is not a production law. The title and thumbnail are the owner's decisions.

## 2. Format
- 16:9, 1920x1080, 30 fps. Stereo; master loudness follows the house encode.
- The approved read sets the length. We aim for 11–13 minutes, but we never pad to reach it or cut below it to hit a number.
- There is one brand outro: the POSTERITY wordmark and the narrated tagline over a background unique to that episode.

## 3. Story discipline
- **One central question**, stated within the opening and answered, or honestly left open, at the end.
- **A human center.** One person whose choices drive the film.
- **An early contradiction** that a first-time viewer can follow from the narration and the image together.
- **Every scene changes what the viewer understands.** If a scene only repeats or decorates, cut it.
- **No artificial resets.** No chapter cards, no re-hooks, no "but first", no recap of what was just said.
- **Keep distinct documents distinct.** Each letter, record or chronicle has its own writer, recipient, date and surviving form. Narration and image must never merge two of them, and must never imply a link that the evidence ledger does not support.

## 4. Evidence: the claim ledger
The Archivist owns the ledger. No line is narrated, and no plate is prompted, before its claim reaches a status that permits it.

| claim_id | proposition | source_type | locator | status | permitted narration wording | reviewer |
|---|---|---|---|---|---|---|
| C01 | what is asserted, in one sentence | primary / chronicle / record / secondary / tradition | file, folio, page or URL, and our source ID | established / attributed / disputed / inference / OPEN | the exact safe wording | Archivist (initials and time) |

- The status describes **the proposition**, not the source.
  - *Attributed* means we can only say that a named source says it.
  - *Inference* is ours or a historian's, and is named as such.
  - *OPEN* blocks narration.
- Translations need a stated provenance. Modern copyrighted translations are paraphrased or quoted briefly with credit.

## 5. Workflow gates (in order; each gate has one owner)
| # | Gate | Owner | Passes when |
|---|---|---|---|
| 1 | Scope and decision packet | Vellum, then the owner | The central question, human center and exclusions are agreed |
| 2 | Claim ledger | Archivist | Every essential claim is established, attributed or disputed. No essential claim is OPEN |
| 3 | Master script + audio-only read | Scriptor (sole script owner), then Atelier for the Oliver read | Vellum and the Examiner (TRANSCRIPT-ONLY, then an audio-only pass) clear the read. The read sets the runtime |
| 4 | Planned shot list + plate packet review | Atelier, then Vellum, then the owner | Coverage, reuse and owner workload are approved **before any plate is generated** |
| 5 | Plates in batches of 4–6 | Owner generates; Vellum calls KEEP or REDO per plate | Every master on the manifest is KEEP |
| 6 | Rough cut | Atelier | It is built from manifest filenames with pinned presets and passes the guardrails |
| 7 | Examiner full-film passes | Examiner, then Vellum judges | In order: audio-only, mute, normal, technical. Verdict PASS or PASS WITH NOTES |
| 8 | Owner approval | Owner | He approves **the actual export file** (filename and md5), not a preview |
| 9 | Private or unlisted playback check | Owner uploads; Atelier and Vellum check | Playback, captions track, audio and resolution are correct on YouTube |
| 10 | Publish | Owner | He flips it public. A publish date is a possibility, never a deadline |

The owner never has a review obligation that the schedule forces onto a fixed morning. The 6am Shorts review loop does not apply to features.

## 6. Artwork
- **A master budget is set at gate 4.** About 30–36 masters per 12-minute feature, each reused on purpose: a callback, a reveal, or a tighter crop carrying a new beat. Reuse never fills dead time. The asset-reuse rule from `edit-preferences.md` stands: a crop of the same plate is not a new asset, and the same image does not play on consecutive beats unless the continuity is meaningful.
- **The 1.5x crop limit applies to the 16:9 frame.** Measure it as output pixels per plate pixel, not only as zoom relative to cover-fit. A portrait Short plate cannot become a 16:9 master by cropping. It needs an owner-generated 16:9 outpaint or a regeneration.
- **Plate packet and manifest.** Atelier delivers a complete, continuity-checked 16:9 plate packet with paste-ready prompts. It uses consistent character reference blocks and hero IDs and comes in batches of 4–6. With it comes a machine-readable manifest in JSON and CSV with these fields:
  - plate_id, scene_id, shot_ids, prompt
  - aspect and target resolution
  - the exact save filename
  - reference and hero IDs
  - batch number, notes
  The engine ingests plates by filename only. No autonomous image generation and no image API.
- **Continuity references.** Each recurring figure has one character block, pasted verbatim. No authentic likeness is claimed, and no actor likeness is used.
- Paperwork is limited to three items: the claim ledger, a brief scene outline, and the auto-generated technical shot manifest.

## 7. Motion
- Use only **pinned, locked presets**, by version and md5: smoke_v2, torch_v1c (torches, cressets, larger fires), fx_candle with smoke_v2 wisps (candles), water_v1 (still sea; only fixed glints and reflections move), and dust_v1 (`motion/PRESETS.md`).
- Every lit plate gets the lit-plate animation rule (§1).
- Depth layers and camera moves beyond the locked push are R&D. Do not depend on them until they are locked.
- Any shot that falls back to a lesser treatment is flagged in the QA report by shot ID, with the reason.

## 8. Versioning
- Every approval names the version it approves: file, md5 or mtime, and time.
- A change reopens only the gates that depend on it. A changed line reopens its claim, its read and its shots, not the whole film.
- There is one master script, and Scriptor owns it. Nobody else edits it, and nobody overwrites anything concurrently: back up first, and write new versions as new files.

## 9. Music (exception to the one-primary-score law)
- A feature may use **up to three complementary sections** that form one coherent score:
  - **Act I, the mystery:** restrained and atmospheric.
  - **Act II, the political danger:** more tension and movement.
  - **Act III, the investigation and aftermath:** contemplative, ending on a deliberate emotional resolution.
- Do not loop one short cue to fill a feature.
- Section changes happen on story turns, at musical phrase boundaries, with crossfades. No chopped re-seeks inside a section. Narration stays clearly above the bed.
- **Every cue has a rights record.** It covers:
  - creator and title, source URL, and licence with version
  - the exact attribution line and the permitted use
  - local file and md5, and the captured licence evidence
  Free, rights-clean music only, unless the owner approves spend.

## 10. Captions (exception to burned-in narrator captions)
- The picture stays clean: no burned-in captions.
- Ship an accurate, optional YouTube CC track in SRT or VTT. Build it from the narration alignment, then correct it by hand.
- Proper names are checked against the claim ledger's spellings. Display forms such as "Edward II" are allowed even where the TTS script spells words out.

## 11. Engine prerequisites (before full assembly)
- The long-form build uses a **content-hash shot cache key** (plate bytes, config, preset versions and size), never the filename alone.
- **Every CLI takes `--size WxH`**, with no portrait hard-codes, and renders at 1920x1080.
- **Landscape QC preview** at 640x360, aspect-preserving, replaces the portrait phone check for features.
- Known engine bugs that touch features are fixed on the copy the build actually uses, or worked around and noted, before gate 6.
