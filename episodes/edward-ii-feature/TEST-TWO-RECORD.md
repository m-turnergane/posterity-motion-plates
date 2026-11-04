# Opening sample, test two

Working note for 4 Nov 2026, about 3:49 PM America/Toronto. Branch `cursor/atelier-jr-intake-596c`, from checkpoint commit `875fc74`. Reviewed commit `0b2f0ef` is the parent of that checkpoint. This session spent nothing, generated nothing, and did not merge.

The review film is not encoded. Five pictures are still the wrong plate, and there is no numeric credit cap. The local renderer, the intro preview, and the effect proofs are what can be looked at now. The brief is [`OPENING-TEST-TWO.md`](OPENING-TEST-TWO.md). The first cut stays [`OPENING-SAMPLE.md`](OPENING-SAMPLE.md).

## First cut, unchanged

`var/edward-ii-feature/opening-sample/opening-sample.mp4`

| Check | Value |
| --- | --- |
| sha256 | `f4f77a9f0f74122d84a19a5901f1d49ae3ce208fd4d837fcf54748bc786a44f8` |
| bytes | 65,284,020 |
| Narration | The nine Oliver takes and their alignment, reused |
| Score | Anabasis I from 0:00, no dip |

`tools/assemble_opening_sample.py` now refuses to run unless `--rebuild-first-cut` is passed, so a later command cannot overwrite that file by accident. Its `sample()` uses the same window as before and resamples it in floating point.

## Recovery

The zip at the checkpoint URL was already on this machine. sha256 `6d0708c38a6a49d4c74022941477dbd9b4d6ef8382e4e4c61517464746275986`, 156,284,214 bytes. Higgsfield media id `aa75b380-355d-436f-a9e5-447703c1aed5`. Unzip root `edward-checkpoint-stage/`. Per-file sums are `checkpoint/SHA256SUMS`.

The ElevenLabs secret is set. `GET /v1/user/subscription` returned 401 again. The nine takes were not rendered again. Higgsfield answered as Plus, 48 credits, free-trial unlimited not spendable, `auto_create_project` false. No job was submitted. Quotes below used `get_cost: true` and `use_unlim: false`.

## Picture path

`src/motionplates/opening/` is the test-two picture path. `tools/assemble_opening_test_two.py` drives it.

| Piece | Behaviour |
| --- | --- |
| Camera | One float warp, `INTER_CUBIC`, pixel-centre matrix. Default `z=1`, centre 0.5, 0.5. A window that overruns the plate by more than a pixel raises |
| S002 | Static 1:1 insert. On the 2752×1536 sealing still, `z=1.4222`, centre `(960/2752, 996/1536)`, source window 1920×1080. No upscale |
| S001 | The accepted H06 clip, decoded in order, frame `round(t × 24)`. Scaled with Lanczos only because the file is 1280×720. No second camera |
| Effects | House `PlateFX` and `SmokeScene` run after that resample, on S002, S005, and S008. Seed 1611. Flame warp stays inside the candle rect. The letter's offscreen source spills light and does not warp the paper |
| Intro | CB1 interior only, no certificate border. Wordmark is the locked raster master, width 1080, used as a mask. Ink RGB `(16, 12, 10)`, multiply. Title is IM Fell DW Pica roman, 52 px. Hard cut at 5.20 s to a black card, cream `(236, 226, 208)` `ACT I`, 92 px, tracking 10, fade 0.35 s |
| Encode | `--full` exits before writing `opening-sample-test-two.mp4` while any required replacement is missing |

The font files match `checkpoint/SHA256SUMS` and now live at `assets/fonts/ofl/imfelldwpica/`. The first-cut assembler still opens the copy at `/tmp/engine-wt/fonts/ofl/imfelldwpica/IMFePIrm28P.ttf`.

## Shot clock

Same Oliver timing as the first cut. Duration 69.740 s. Gap 0.40 s, intro gap 7.5 s, tail 0.60 s. L08 still splits at word 27, "even".

| Shot | Start | Stop | Plate this pass | What the frame is |
| --- | --- | --- | --- | --- |
| S001 | 0.000 | 4.951 | H06 clip | Keep. Hand lifts, wax settles, letter stays blank. Softness is the 720p file scaled 1.5× |
| S002 | 4.951 | 11.435 | H06 v2 still | Keep. Locked insert of candle, hands, and the blank letter. Local flame and a thin wisp |
| S003 | 11.435 | 14.482 | needs `S003.png` | Gloucester. No extra crown. The effigy reads as a carved figure |
| S004 | 14.482 | 19.619 | needs `S004.png` | Pre-strike tableau. Kent at the block, axe raised, no impact. First anchor |
| S005 | 19.619 | 24.449 | DK1 | Keep. Locked wide. Spill from the partial candle. Paper and wax stay still |
| SC01 | 24.449 | 31.949 | CB1 interior | Local intro, then the black card |
| S007 | 31.949 | 41.962 | needs `S007.png` | Kent, medium, in the hall. The king is outside the frame |
| S007a | 41.962 | 47.285 | needs `S007a.png` | Edward, medium. Kent is outside the frame |
| S008 | 47.285 | 54.901 | N01 | The one locked wide of that plate. Torches flicker and smoke. Faces are protected |
| S008a | 54.901 | 59.481 | N21 | Keep. Gascony terrace, daylight, no candle effect |
| S009 | 59.481 | 69.740 | needs `S009.png` | One new picture for the whole hold. A grade of N01 is not that picture |

N01 stays in the film once, as S008. It still has the extra fleurs and the hand-on-chin pose. H06 v2, DK1, N21, the CB1 interior, and the wordmark stay. H01 and the empty-platform N14 leave the film when the replacements exist.

Intro, local to the 7.5 s gap: wordmark 0.35–2.80 s, title 1.85–3.55 s, both then hold. Type sits at y=250 so the leaf's centre fold is below the letters. The card cuts in at 5.20 s and holds to 7.50 s.

## What the proofs measured

Rendered by `python tools/assemble_opening_test_two.py` after the last source edit. Difference is the effect frame at 1.25 s against the unprocessed plate. Thirds are left, middle, right.

| Shot | Source window | z | Mean | Max | Thirds |
| --- | --- | --- | --- | --- | --- |
| S002 | 1920×1080 | 1.4222 | 1.95 | 149 | 4.20 / 1.45 / 0.20 |
| S005 | 2730.67×1536 | 1.000 | 12.60 | 56 | 18.67 / 15.87 / 3.27 |
| S008 | 2730.67×1536 | 1.000 | 3.24 | 100 | 1.56 / 3.43 / 4.73 |

S001 clip: 145 frames, 24 fps, 6.042 s, 1280×720. The proof pairs the nearest-neighbour upscale of the raw frame with the Lanczos fit. The composition matches. A 720p reshoot is 42 credits and does not add resolution. A 1080p reshoot is 96 credits, more than the balance. Neither is in the ask.

S005's warmth is on the letter and the wood beside the candle. The right-hand desk moves by about 3 levels. The string, seal, and folds stay put. S002's change sits on the candle. S008's change sits on the torches.

Local preview, 7.500 s, 1920×1080, 30 fps, 225 frames: `var/edward-ii-feature/opening-sample-test-two/proofs/intro-preview.mp4`. It is the branding passage on its own, not the opening sample.

`pytest -q` on this branch after the change: 57 passed, 1 skipped.

## The one ask

Balance read at 3:49 PM America/Toronto: 48 credits on Plus. This session spent 0. The balance is not a cap.

Authorize **23.50 credits**, at most **8 submissions**, or name a lower number. Nothing is submitted until that number is given.

| Item | Settings | Credits |
| --- | --- | --- |
| Five stills | `gpt_image_2_5`, 16:9, quality `high`, resolution `2k`, count 1, `use_unlim` false | 2.75 × 5 = 13.75 |
| Two retries | same high 2k still, only if a plate fails review | 5.50 |
| One anchor replacement | same model, quality `high`, resolution `4k`, only if the 2k S004 is the right picture and too soft | 4.25 |
| **Aggregate** | | **23.50** |

Order: S004 first, judged native against the rain-swept reference before the other four. Then S003, S007, S007a, and S009. If S004 fails twice, stop and report it. There is no acceptable fallback plate for that beat. A later plate that fails twice is reported. It is not replaced with a crop of N01.

`nano_banana_pro` at 2 credits for 16:9 2k is a price reference from the same read. It is not a second visual test. Website Unlimited labels do not apply: `unlim.available` is false. No plan purchase.

The two short references stay the guides for the new stills. Ink-on-paper inspiration images were not in the recovery set and were not invented. New plates get flame rectangles only after the still exists. A daylight plate does not get a candle.

## Commands

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest -q
python tools/assemble_opening_test_two.py --timeline
python tools/assemble_opening_test_two.py
python tools/assemble_opening_test_two.py --full
```

`--full` writes `var/edward-ii-feature/opening-sample-test-two/opening-sample-test-two.mp4` only after `S003.png`, `S004.png`, `S007.png`, `S007a.png`, and `S009.png` are in `var/edward-ii-feature/opening-sample-test-two/plates/`. Until then it exits and names the missing pictures. Proof frames land in `var/edward-ii-feature/opening-sample-test-two/proofs/`.

## Known limits

The integrated film does not exist yet, so there is no export loudness number for test two. The voice and score path is the first cut's, reused when `--full` is allowed. Effect rectangles are measured on the recovered 2752×1536 plates. S002's procedural flame is drawn on top of the painted candle; the proof still shows one flame and a thin wisp. S005's candle is already painted at the left edge, and the effect only breathes the spill. N01's extra fleurs remain on the one wide. The H06 clip stays 720p. The first-cut file was not rebuilt, so its old integer-sampled frames are still the comparison copy.
