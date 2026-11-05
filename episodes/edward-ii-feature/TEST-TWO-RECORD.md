# Opening sample, test two

Review film for 4 Nov 2026. Branch `cursor/atelier-jr-intake-596c`. The renderer landed in `ecaf054`, on top of checkpoint `875fc74`. Reviewed commit `0b2f0ef` is that checkpoint's parent. The owner authorized 23.50 Higgsfield credits and 8 submissions at 5:39 PM America/Toronto (`2026-11-04T22:39:00Z`). The first encode spent 16.50 across 6 submissions. At 6:20 PM the owner asked for a spoken title, Penumbra instead of Anabasis I, a stone effigy, and motivated light on the king's face. Those two stills used the last two submissions, 5.50 credits. The cap is now 22.00 credits and 8 submissions. It did not merge, publish, or start the full feature.

The brief is [`OPENING-TEST-TWO.md`](OPENING-TEST-TWO.md). The current plan is [`ACT-I-PLAN.md`](ACT-I-PLAN.md). The first cut stays [`OPENING-SAMPLE.md`](OPENING-SAMPLE.md).

After 8:25 PM America/Toronto the same evening, the cut was revised without a new Higgsfield charge. Kent is on screen for his introduction, Edward is on screen when he is named, L04 and the spoken title were re-read, and the locked camera became a small scale push with the flame painted on the plate first. The raised-axe plate is still the picture for S004. The resting-axe replacement is quoted in the plan and has not been submitted.

## The review file

`var/edward-ii-feature/opening-sample-test-two/opening-sample-test-two.mp4`

| Check | Value |
| --- | --- |
| sha256 | `9b4f84e9a30c290b3717e33db94cabaf42862082ad6a0c159089870d8d15256b` |
| bytes | 172,313,796 |
| Duration | 70.733 s (2,122 frames at 30 fps). Timeline end 70.727 s |
| Picture | H.264, 1920×1080, 30 fps, progressive, yuv420p |
| Audio | AAC LC, 48 kHz, stereo |
| Captions | `mov_text`, language `eng`, plus `captions.srt` and `captions.vtt`. 23 cues |
| Loudness | −14.0 LUFS integrated, true peak −1.3 dBTP |
| Mix | Voice −19.4, bed −31.4, duck 4.9 |

## Smaller review encode

Made the morning of 5 Nov 2026, America/Toronto. This is a transcode of the master above. The master was not re-rendered and its hash is unchanged.

`var/edward-ii-feature/opening-sample-test-two/opening-sample-test-two-review.mp4`

| Check | Value |
| --- | --- |
| sha256 | `23ea109edcff7a01c42ffcc2f368c505da127abce105d2aa7354f49852e3cc4b` |
| bytes | 63,693,053 |
| Picture | H.264, 1920×1080, 30 fps, 2,122 frames, the same count as the master |
| Encode | libx264, crf 18, maxrate 8000k, bufsize 16000k, AAC 192 kb/s, captions copied |
| Audio and captions | Same programme as the master |

An uncapped crf 18 of this cut was about 122 MB and would not copy onto the review volume. The cap is why this file is smaller. Frame steps inside each shot stay steady. The ink and the act card sit still. Between 5.3 s and 7.1 s the candle flame stays on the wick while the framing eases.

A stored zip of this review file is Higgsfield media `ec5d1b4f-aa83-4257-b5f7-2323d1469f70`. The zip sha256 is `58628dc985788254c2d7e01ba52884c03b296e7fd30949df55397992f94068e1`, 63,693,219 bytes. The mp4 inside matches the hash above. The URL is in `checkpoint/RECOVERY-2026-11-05.md`.

The first sample is unchanged: `var/edward-ii-feature/opening-sample/opening-sample.mp4`, sha256 `f4f77a9f0f74122d84a19a5901f1d49ae3ce208fd4d837fcf54748bc786a44f8`, 65,284,020 bytes. `tools/assemble_opening_sample.py` still refuses unless `--rebuild-first-cut` is passed.

Narration is the nine Oliver takes, with L04 and the spoken title replaced in this cut's voice directory only. The files in `opening-sample/vo` are unchanged. L04 keeps the house stability of 0.5, with the funeral line before it and the question after it. The title uses stability 0.72, with the question before it and L07 after it. Wording is unchanged. The comparison against the accepted lines is in [`ACT-I-PLAN.md`](ACT-I-PLAN.md). The title runs 25.313–30.886 s. The act card follows it, at local 6.223 s of the intro, absolute 31.136 s. The score is Penumbra from 0:30 of the file. md5 `2acea4098213d02c944d57a2faa19a51`. The first 30 s of that track is nearly silent, which is why SCORE-PLAN starts it at or after 0:30. Credit: 'Penumbra' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au. The first cut still uses Anabasis I.

## What changed from the first cut

- The camera eases a scale-only push, `1.00 → 1.04` on a full-frame still, `smoothstep`, float `INTER_CUBIC`. S002 is Kent's face and signet hand at `z` 1.25→1.28. S002b is the accepted Edward medium at `z` 1.00→1.025. No window upscales. Depth is not added on top. Flame is painted on the plate, then resampled.
- S001 stays the accepted H06 clip, decoded in order. The softness is that 720p file scaled into the 1080 frame.
- House flame, smoke, and spill are painted on the plate, then the camera resamples that plate. S002, S002b, S003, S005, S007, S007a, S008, and S009. S004 and S008a have the push and no flame.
- The intro is black ink on the CB1 parchment interior, then a hard cut to a black card with cream centred `ACT I`. The certificate border and the left-to-right wipe are gone.
- S003 is Gloucester. The figure on the tomb is a limestone recumbent effigy, one carving, hands together. The jointed wooden take is not in the film. Kent is bareheaded.
- S004 is still the raised-axe tableau from the earlier encode. The resting-axe replacement is quoted and not generated. There is no swing and no impact. The empty platform is gone.
- S007 is Kent alone in the hall. S007a is Edward alone on the throne. S008 is the one remaining wide of the recovered N01 plate. S009 is a new court picture, not a cooled crop of N01.
- H01 and the empty-platform N14 leave this cut.

## Shot clock

L04 and the title are longer than the first takes, so the clock moved. Gap 0.40 s, tail 0.60 s. The intro holds long enough for the title and then 1.80 s of the card. L08 still splits at word 27, "even".

| Shot | Start | Stop | Picture | Motion on the export |
| --- | --- | --- | --- | --- |
| S001 | 0.000 | 4.951 | H06 clip | The clip's own motion. No second push |
| S002 | 4.951 | 7.470 | H06 still, Kent's face and signet hand | Candle on the plate, then `z` 1.25→1.28 |
| S002b | 7.470 | 11.435 | `S007a.png`, Edward on the throne | That plate's torch, face protected, then `z` 1.00→1.025 |
| S003 | 11.435 | 14.482 | `S003.png`, stone effigy | Candles on the plate, then the push. Kent's head is protected |
| S004 | 14.482 | 20.083 | `S004.png`, axe still raised | Push only. Rain is painted. Mean change over 0.50 s is the push, not a swing |
| S005 | 20.083 | 24.913 | DK1 | Spill on the plate, then the push. The paper is not warped |
| SC01 | 24.913 | 32.936 | CB1 interior, then black | Ink, then the card at local 6.223 s |
| S007 | 32.936 | 42.949 | `S007.png` | One torch on the plate, then the push |
| S007a | 42.949 | 48.272 | `S007a.png` | One torch, the king protected, then the push |
| S008 | 48.272 | 55.888 | N01 | Two torches on the plate, then the push |
| S008a | 55.888 | 60.468 | N21 | Push only. One frame step at 58.0 s changes 2.5% of pixels by more than 8 levels |
| S009 | 60.468 | 70.727 | `S009.png`, relit | Two cressets on the plate, faces protected, then the push |

Intro, local to the 7.5 s gap: wordmark about 0.35–2.80 s, title about 1.85–3.55 s, both then hold. Type sits at y=250 so the leaf's centre fold stays below the letters. Ink RGB `(16, 12, 10)`, multiply. Title is IM Fell DW Pica roman, 52 px. The card is cream `(236, 226, 208)`, 92 px, tracking 10, fade about 0.35 s.

## Export frames

Pulled from the finished mp4, not from the renderer. Times are absolute.

| Time | Frame | What is in it |
| --- | --- | --- |
| 2.50 | `review/s001-b.jpg` | The sealing clip. One candle, one wisp, blank letter |
| 6.20 | `review/s002-kent.jpg` | Kent's face and the signet hand. The seal is in frame. He is not cropped to the hands |
| 9.20 | `review/s002-edward.jpg` | Edward alone on the throne, the accepted S007a plate, while the line names him |
| 12.80 | `review/s003-stone.jpg` | Limestone tomb effigy, praying hands, crown part of the carving, Kent bareheaded |
| 17.50 | `review/s004-raised.jpg` | The current plate: Kent at the block, axe raised and clear of him. No impact. The resting-axe still is not in this file |
| 23.00 | `review/s005-23.jpg` | The letter, warm on the candle side. String, seal, and folds stay put |
| 26.20 | `review/intro-early.jpg` | Wordmark mid-ink. Title has not started |
| 28.60 | `review/intro-hold.jpg` | `POSTERITY` and `The Letter for a Buried King`, both settled. The fold is below the type |
| 31.50 | `review/act.jpg` | Black field, cream centred `ACT I`, after the spoken title has finished |
| 36.00 | `review/s007.jpg` | Kent alone, medium, window and one torch. No crown |
| 44.50 | `review/s007a.jpg` | Edward alone, simple gold crown, blue-and-gold robe, hands on the chair |
| 51.00 | `review/s008.jpg` | The one N01 wide. Both men. Extra fleurs stay on this plate |
| 57.00 | `review/s008a.jpg` | Gascony terrace, daylight |
| 64.00 | `review/s009-relit.jpg` | King, two courtiers, four barons with sheathed swords, queen in the doorway. Face light comes from the near torch |

S005 between 21.0 s and 23.0 s differs by about 47 / 41 / 10 levels across the left, middle, and right thirds. The warmth sits on the letter and the wood beside the candle. The right-hand desk moves less. The paper geometry does not.

Earlier plate proofs, effect against the unprocessed cover at 1.25 s: S002 mean 1.95, S005 mean 12.60, S008 mean 3.24, S003 mean 1.39, S007 mean 0.06, S007a mean 1.58, S009 mean 0.82. S007's torch change is small. The export pair two seconds apart reaches a max of 101, so the flame is moving, quietly.

## Sources and effects

New plates are 2688×1520. Their effect rectangles are pixels of that file (`native: true`) and are not scaled from the 2752×1536 recovered plates. Kept plates still scale from that reference. Seed 1611. `S004` has no effect entry.

| Shot | Source | Identity | Effects |
| --- | --- | --- | --- |
| S001 | `opening-sample/plates/H06-i2v.mp4` | sha256 `f5b0f5c4e295eaf4cb3a8433c763d209e0326f4c61d93490c3d73a8d65939f3f`, md5 `d4f222dc6394f285e5adaa6be23af37b`, 1280×720, 145 frames, 24 fps | None beyond the clip |
| S002 | `H06-v2.png` | sha256 `858cfd6360003e33f66ec8d11d0a4b6e61f261e2735618715157a6595e31fcab` | Candle rect and a thin wisp, painted on the plate |
| S002b | `plates/S007a.png` | same file as S007a | That plate's torch. The king's face is protected |
| S003 | `plates/S003.png` | md5 `3fad8ac5e9052795ed3ec1606f23d8df`, sha256 `275da1328ac5ea4a5f86280d3a14629b15a521dc06f7f17f90c64bb758495d77`, 7,554,546 bytes. Job `a829656f-fdd5-4fda-9f71-72083ec022fd` | Eight candle cores, two wisps, Kent's head protected |
| S004 | `plates/S004.png` | md5 `283e2a44b9b3d7d5127539be835e9994`, sha256 `d962f1d96f9b574954126cffda40d31589c298e6938c29712571d0b179582064`, 7,519,067 bytes. Job `c6e3cff2-97b7-481b-a4af-b9a460dee7ac` | None. Rain stays in the paint |
| S005 | `DK1.png` | sha256 `64eb734d7a75c973aa64786b12a8fc9ee302622dcb8583067147ad3fd67dcb41` | Offscreen candle, spill only. Paper is not warped |
| SC01 | `CB1.png` interior | sha256 `7f091ad8957076b462598b37689a35f33d5d648a3ad1c9e30aac9944b23bebc3` | Ink mask from `wordmark/posterity-master.png`, sha256 `ccd67ec31c0315ede5bce14ffaaa366d3bec7611a962514d29f75033baddfead` |
| S007 | `plates/S007.png` | md5 `92a73ff2be1ff62a5f9a5f4fd55f3710`, sha256 `7f97c800f23b658faf6e71a06659f9741d2e2004edfab8d9c3602e1a44da515d`, 7,020,471 bytes. Job `f5fb95e2-252b-42bb-9714-5349913584b0` | One torch, one wisp, Kent protected |
| S007a | `plates/S007a.png` | md5 `fa82e466a806da583fa2b4e4762ff56a`, sha256 `2b4be0ee8de365a077553bfe81d53b73f5e1bbe2c96c87654df621003fbf58f8`, 8,141,309 bytes. Job `b9dbc05b-ed59-494c-962e-e196c9e9072f` | One torch, one wisp, the king protected |
| S008 | `N01.png` | sha256 `877b7136eeb8f8ba139a2cf6e1f08934674721857ee0a9062f82506369dc12fd` | Two torches, two wisps, both faces protected |
| S008a | `N21.png` | sha256 `b07690c28d1c0bd469e7dfa92ff67e8cb8316b17b5e1d16a85ffcf220fe6ae52` | None |
| S009 | `plates/S009.png` | md5 `88718c5c16c6dde52873863e814e55bc`, sha256 `aaf697d251dc249116dea4550e077626c3617a8101f3a84db9fddd7a3c86354f`, 7,529,284 bytes. Job `6960adb1-baec-4919-81d5-3f785b35883f` | Two cressets, two wisps, king and barons protected |

The bed in this cut is Penumbra, md5 above, from 30.0 s. Anabasis I, sha256 `964e693611445d808d4cdb748006ae22c7fa8534b126acdca39bcc74de95d76c`, stays on the first cut.

Rejected and kept beside the delivery plate: S003 attempt 1, job `37ae68ed-e632-4ba4-9001-e9b1562b74af`, md5 `653294a9071b69e6653f5bc88b18fe2b`, file `S003-attempt1.png`. It is not copied onto `S003.png`.

## Spend

Balance before this authorization, read at 3:49 PM America/Toronto: 48 credits, Plus, `unlim.available` false. Balance after the eight charges, read about 6:30 PM America/Toronto (`2026-11-04T23:30:00Z`): **26**. Re-read at about 8:30 PM America/Toronto (`2026-11-05T01:30:00Z`), before the Act I quote: **26**. No job was submitted for that quote.

| When (America/Toronto) | Charge | Credits |
| --- | --- | --- |
| 5:43:52 PM | S004, GPT Image 2.5, high, 2k, 16:9 | −2.75 |
| 5:47:55 PM | S003 attempt 1, S007, S007a, S009, same settings | −11.00 |
| 5:53:58 PM | S003 attempt 2, same settings | −2.75 |
| 6:25 PM | S003 stone effigy and S009 relit face, same settings | −5.50 |
| **This authorization** | **8 of 8 submissions** | **−22.00** |

The ledger matches 48 − 22.00 = 26. The 4k S004 slot was not used. One and a half credits remain, and no submission slot remains. That remainder is not a new budget. `config/budget.yaml` now holds the pass at `no-further-spend`.

Account total spent is now 84: the opening 62, plus this 22.00. ElevenLabs `spent_credits` stays 0 because the subscription endpoint is still unread. Characters sent are 1,467. The character-cost header is 626, of which 162 is the six L04 and title calls. The live quotes, not spent, were reconfirmed on the morning of 5 Nov 2026. A high 2k still is 2.75 and a high 4k still is 4.25. The Act I clip comparison, including Seedance 1080p at 96, is in [`ACT-I-PLAN.md`](ACT-I-PLAN.md). The 720p price is rejected. Nothing in that inventory was submitted. The balance that morning was still 26.

`nano_banana_pro` at 2 credits was a price reference only. No Seedance job was submitted. No plan was bought.

## Picture path

`src/motionplates/opening/` and `tools/assemble_opening_test_two.py`. A still eases `z` and resamples in floating point. A window that upscales, or that leaves the plate, raises. Effects are built on the plate, then warped with that window. Replacement plates override recovered stills when the file exists under `var/edward-ii-feature/opening-sample-test-two/plates/`. `--full` refuses while any of the five required names is missing.

The font files match `checkpoint/SHA256SUMS` and live at `assets/fonts/ofl/imfelldwpica/`. Both assemblers open `IMFePIrm28P.ttf` there.

`pytest -q` after this pass: 58 passed, 1 skipped. The tests do not render the film.

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

- Motion from a generated clip exists only on S001. That H06 file is 6.04 s and 720p, and S001 uses the first 4.95 s. It is not extended. Everywhere else, the moving pixels are the scale push plus candle, torch, smoke, or the letter's spill.
- S002 shows Kent. S002b shows Edward on the accepted throne plate. The sealing action is not repeated.
- The H06 clip stays 720p. A 1080p replacement was quoted at 96 credits, which the 26-credit balance cannot pay. The 42-credit 720p quote is rejected.
- S004 is still the raised-axe plate. The resting-axe still is quoted at 2.75 and has not been generated.
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
