# Opening sample, test two

Review film for 4 Nov 2026. Branch `cursor/atelier-jr-intake-596c`. The renderer landed in `ecaf054`, on top of checkpoint `875fc74`. Reviewed commit `0b2f0ef` is that checkpoint's parent. The owner authorized 23.50 Higgsfield credits and 8 submissions at 5:39 PM America/Toronto (`2026-11-04T22:39:00Z`). This pass spent 16.50 across 6 submissions and encoded the film. It did not merge, publish, or start the full feature.

The brief is [`OPENING-TEST-TWO.md`](OPENING-TEST-TWO.md). The first cut stays [`OPENING-SAMPLE.md`](OPENING-SAMPLE.md).

## The review file

`var/edward-ii-feature/opening-sample-test-two/opening-sample-test-two.mp4`

| Check | Value |
| --- | --- |
| sha256 | `2decd5633fb8ce73c15c2bbfe0084a702aa7e705cfa227731226d9a2c38cdaa6` |
| bytes | 28,759,240 |
| Duration | 69.733 s (2,092 frames at 30 fps). Timeline end 69.740 s |
| Picture | H.264, 1920×1080, 30 fps, progressive, yuv420p |
| Audio | AAC LC, 48 kHz, stereo |
| Captions | `mov_text`, language `eng`, plus `captions.srt` and `captions.vtt`. 21 cues |
| Loudness | −14.0 LUFS integrated, true peak −1.3 dBTP |
| Mix | Voice −19.2, bed −31.2, duck 4.4 |

The first sample is unchanged: `var/edward-ii-feature/opening-sample/opening-sample.mp4`, sha256 `f4f77a9f0f74122d84a19a5901f1d49ae3ce208fd4d837fcf54748bc786a44f8`, 65,284,020 bytes. `tools/assemble_opening_sample.py` still refuses unless `--rebuild-first-cut` is passed.

Narration is the nine Oliver takes and their alignment. Score is Anabasis I from 0:00, no dip. Neither was rendered again. `GET /v1/user/subscription` was not retried.

## What changed from the first cut

- The camera is fixed. One float cover-fit, `INTER_CUBIC`. S002 is a static 1:1 insert of the sealing still (`z=1.4222`, window 1920×1080). No N01 push.
- S001 stays the accepted H06 clip, decoded in order. The softness is that 720p file scaled into the 1080 frame.
- House flame, smoke, and spill run on the sampled frame. S002, S003, S005, S007, S007a, S008, and S009. S004 and S008a are still.
- The intro is black ink on the CB1 parchment interior, then a hard cut to a black card with cream centred `ACT I`. The certificate border and the left-to-right wipe are gone.
- S003 is a new Gloucester plate. The figure on the hearse is a jointed wooden effigy. Kent is bareheaded. Attempt 1, which still read as a corpse, is not in the film.
- S004 is a new pre-strike tableau. Kent is at the block, the axe is raised, and there is no impact. The empty platform is gone.
- S007 is Kent alone in the hall. S007a is Edward alone on the throne. S008 is the one remaining wide of the recovered N01 plate. S009 is a new court picture, not a cooled crop of N01.
- H01 and the empty-platform N14 leave this cut.

## Shot clock

Same Oliver timing as the first cut. Gap 0.40 s, intro gap 7.5 s, tail 0.60 s. L08 still splits at word 27, "even".

| Shot | Start | Stop | Picture | Motion on the export |
| --- | --- | --- | --- | --- |
| S001 | 0.000 | 4.951 | H06 clip | Subject and flame move. Frame shift 0.01 px between 1.0 s and 1.5 s |
| S002 | 4.951 | 11.435 | H06 v2 still, 1:1 | Candle and wisp. Shift 0.00 px between 6.0 s and 6.8 s |
| S003 | 11.435 | 14.482 | `S003.png`, attempt 2 | Candles on the hearse. Kent's side stays still. Shift 0.00 px |
| S004 | 14.482 | 19.619 | `S004.png` | Locked. Mean difference 0.00 between 16.0 s and 18.5 s. Rain is painted |
| S005 | 19.619 | 24.449 | DK1 | Spill on the letter. Shift 0.00 px between 21.0 s and 23.0 s |
| SC01 | 24.449 | 31.949 | CB1 interior, then black | Ink, then the card. Card cut at local 5.20 s, absolute 29.649 s |
| S007 | 31.949 | 41.962 | `S007.png` | One torch. Shift 0.00 px |
| S007a | 41.962 | 47.285 | `S007a.png` | One torch at the right edge. Shift 0.00 px |
| S008 | 47.285 | 54.901 | N01 | Two torches. Shift 0.00 px |
| S008a | 54.901 | 59.481 | N21 | Locked daylight. No flame |
| S009 | 59.481 | 69.740 | `S009.png` | Two cressets. Shift 0.00 px |

Intro, local to the 7.5 s gap: wordmark about 0.35–2.80 s, title about 1.85–3.55 s, both then hold. Type sits at y=250 so the leaf's centre fold stays below the letters. Ink RGB `(16, 12, 10)`, multiply. Title is IM Fell DW Pica roman, 52 px. The card is cream `(236, 226, 208)`, 92 px, tracking 10, fade about 0.35 s.

## Export frames

Pulled from the finished mp4, not from the renderer. Times are absolute.

| Time | Frame | What is in it |
| --- | --- | --- |
| 2.50 | `review/s001-b.jpg` | The sealing clip. One candle, one wisp, blank letter |
| 7.00 | `review/s002.jpg` | The 1:1 insert. Hands, wax, knife, one flame |
| 12.80 | `review/s003.jpg` | Jointed oak effigy, painted wooden face, wooden crown, Kent bareheaded, monks without crowns |
| 17.00 | `review/s004.jpg` | Kent at the block, axe raised and clear of him, rain, scaffold, crowd, castle. No impact |
| 23.00 | `review/s005-23.jpg` | The letter, warm on the candle side. String, seal, and folds stay put |
| 26.20 | `review/intro-early.jpg` | Wordmark mid-ink. Title has not started |
| 28.60 | `review/intro-hold.jpg` | `POSTERITY` and `The Letter for a Buried King`, both settled. The fold is below the type |
| 30.20 | `review/act.jpg` | Black field, cream centred `ACT I` |
| 36.00 | `review/s007.jpg` | Kent alone, medium, window and one torch. No crown |
| 44.50 | `review/s007a.jpg` | Edward alone, simple gold crown, blue-and-gold robe, hands on the chair |
| 51.00 | `review/s008.jpg` | The one N01 wide. Both men. Extra fleurs stay on this plate |
| 57.00 | `review/s008a.jpg` | Gascony terrace, daylight |
| 64.00 | `review/s009.jpg` | King, two courtiers, four barons with sheathed swords, queen in the far doorway, rain on the window |

S005 between 21.0 s and 23.0 s differs by about 47 / 41 / 10 levels across the left, middle, and right thirds. The warmth sits on the letter and the wood beside the candle. The right-hand desk moves less. The paper geometry does not.

Earlier plate proofs, effect against the unprocessed cover at 1.25 s: S002 mean 1.95, S005 mean 12.60, S008 mean 3.24, S003 mean 1.39, S007 mean 0.06, S007a mean 1.58, S009 mean 0.82. S007's torch change is small. The export pair two seconds apart reaches a max of 101, so the flame is moving, quietly.

## Sources and effects

New plates are 2688×1520. Their effect rectangles are pixels of that file (`native: true`) and are not scaled from the 2752×1536 recovered plates. Kept plates still scale from that reference. Seed 1611. `S004` has no effect entry.

| Shot | Source | Identity | Effects |
| --- | --- | --- | --- |
| S001 | `opening-sample/plates/H06-i2v.mp4` | sha256 `f5b0f5c4e295eaf4cb3a8433c763d209e0326f4c61d93490c3d73a8d65939f3f`, md5 `d4f222dc6394f285e5adaa6be23af37b`, 1280×720, 145 frames, 24 fps | None beyond the clip |
| S002 | `H06-v2.png` | sha256 `858cfd6360003e33f66ec8d11d0a4b6e61f261e2735618715157a6595e31fcab` | Candle rect and a thin wisp. Hands protected |
| S003 | `plates/S003.png` | md5 `f4cce52d2362b517f741d9395dda785c`, sha256 `308d07a4566fdeccef4f917e07b613a62252fa7a5a1d8d11bcddb2ee0171299d`, 6,537,982 bytes. Job `b7cb133b-d9dd-4119-9d8e-db54fb64ce09` | Eight torch rects on the candles, two wisps, Kent protected |
| S004 | `plates/S004.png` | md5 `283e2a44b9b3d7d5127539be835e9994`, sha256 `d962f1d96f9b574954126cffda40d31589c298e6938c29712571d0b179582064`, 7,519,067 bytes. Job `c6e3cff2-97b7-481b-a4af-b9a460dee7ac` | None. Rain stays in the paint |
| S005 | `DK1.png` | sha256 `64eb734d7a75c973aa64786b12a8fc9ee302622dcb8583067147ad3fd67dcb41` | Offscreen candle, spill only. Paper is not warped |
| SC01 | `CB1.png` interior | sha256 `7f091ad8957076b462598b37689a35f33d5d648a3ad1c9e30aac9944b23bebc3` | Ink mask from `wordmark/posterity-master.png`, sha256 `ccd67ec31c0315ede5bce14ffaaa366d3bec7611a962514d29f75033baddfead` |
| S007 | `plates/S007.png` | md5 `92a73ff2be1ff62a5f9a5f4fd55f3710`, sha256 `7f97c800f23b658faf6e71a06659f9741d2e2004edfab8d9c3602e1a44da515d`, 7,020,471 bytes. Job `f5fb95e2-252b-42bb-9714-5349913584b0` | One torch, one wisp, Kent protected |
| S007a | `plates/S007a.png` | md5 `fa82e466a806da583fa2b4e4762ff56a`, sha256 `2b4be0ee8de365a077553bfe81d53b73f5e1bbe2c96c87654df621003fbf58f8`, 8,141,309 bytes. Job `b9dbc05b-ed59-494c-962e-e196c9e9072f` | One torch, one wisp, the king protected |
| S008 | `N01.png` | sha256 `877b7136eeb8f8ba139a2cf6e1f08934674721857ee0a9062f82506369dc12fd` | Two torches, two wisps, both faces protected |
| S008a | `N21.png` | sha256 `b07690c28d1c0bd469e7dfa92ff67e8cb8316b17b5e1d16a85ffcf220fe6ae52` | None |
| S009 | `plates/S009.png` | md5 `8b3390c789afff4bc35ff43df3dcbdcd`, sha256 `dfb2cca7381b617e63cf6c70bcb95b5f67b2455e075a8b530c33c216f9cf74d5`, 7,873,223 bytes. Job `a445f067-3441-4662-97a9-548c58dd441d` | Two cressets, two wisps, king and barons protected |

Score sha256 `964e693611445d808d4cdb748006ae22c7fa8534b126acdca39bcc74de95d76c`.

Rejected and kept beside the delivery plate: S003 attempt 1, job `37ae68ed-e632-4ba4-9001-e9b1562b74af`, md5 `653294a9071b69e6653f5bc88b18fe2b`, file `S003-attempt1.png`. It is not copied onto `S003.png`.

## Spend

Balance before this authorization, read at 3:49 PM America/Toronto: 48 credits, Plus, `unlim.available` false. Balance after the six charges, read at 6:01 PM America/Toronto (`2026-11-04T23:01:00Z`): **31.5**.

| When (America/Toronto) | Charge | Credits |
| --- | --- | --- |
| 5:43:52 PM | S004, GPT Image 2.5, high, 2k, 16:9 | −2.75 |
| 5:47:55 PM | S003 attempt 1, S007, S007a, S009, same settings | −11.00 |
| 5:53:58 PM | S003 attempt 2, same settings | −2.75 |
| **This authorization** | **6 of 8 submissions** | **−16.50** |

The ledger matches 48 − 16.50 = 31.5. No other charge posted between the authorization and that read. The unused high-2k retry (2.75) and the high-4k S004 slot (4.25) were not submitted. S004 was accepted at 2k. Those 7.00 credits and 2 submissions are not a new budget. `config/budget.yaml` holds the pass at `owner-review`.

Account total spent is now 78.5: the opening 62, plus this 16.50. ElevenLabs `spent_credits` stays 0 because the subscription endpoint is still unread. Characters already sent stay 1,083.

`nano_banana_pro` at 2 credits was a price reference only. No Seedance job was submitted. No plan was bought.

## Picture path

`src/motionplates/opening/` and `tools/assemble_opening_test_two.py`. Camera default `z=1`, centre 0.5, 0.5. A window that overruns the plate by more than a pixel raises. Replacement plates override recovered stills when the file exists under `var/edward-ii-feature/opening-sample-test-two/plates/`. `--full` refuses while any of the five required names is missing.

The font files match `checkpoint/SHA256SUMS` and live at `assets/fonts/ofl/imfelldwpica/`. The first-cut assembler still opens `/tmp/engine-wt/fonts/ofl/imfelldwpica/IMFePIrm28P.ttf`.

`pytest -q` after the effect table and this record: 57 passed, 1 skipped. The tests do not render the film.

## Commands

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest -q
python tools/assemble_opening_test_two.py --timeline
python tools/assemble_opening_test_two.py
python tools/assemble_opening_test_two.py --full
```

`--full` writes the mp4 above. Proof frames from the renderer, not the export, land in `var/edward-ii-feature/opening-sample-test-two/proofs/`. Export frames from this review are in `var/edward-ii-feature/opening-sample-test-two/review/`. Rebuilding the comparison cut takes `python tools/assemble_opening_sample.py --rebuild-first-cut` and overwrites `opening-sample.mp4`.

## Known limits

- The H06 clip stays 720p. A 720p reshoot was quoted at 42 credits and a 1080p reshoot at 96. Neither fits this cap, and neither adds a new composition.
- S004's rain does not move. Warping the plate to fake rain was rejected.
- S003, S004, and S009 are more photographic than the kept Nano Banana plates. S007 and S007a sit closer to N01. The cut between those finishes is visible.
- N01's extra fleurs and the hand-on-chin pose remain on the one wide, S008.
- S007's torch is a small change. It does not read as a second flame.
- S005's letter breathes. The right side of the desk moves less than the paper.
- S009's nearer courtier wears a red cap, not a crown. The swords stay sheathed.
- The clerk's sheet on the kept N21 plate has painted marks. That plate was not regenerated.
- Ink-on-paper inspiration images were never found. The candlelight and rain-swept paintings were the guides that were used.
- ElevenLabs live balance is still unknown.
- The film is for the owner's creative review. It is not approved for playback in the editor, and it is not the full feature.
