# Edward II / Kent feature

status: DESK_HANDOFF
updated: 2026-11-05
timezone: America/Toronto

Current handoff: [`ACT-I-PLAN.md`](ACT-I-PLAN.md). Where the shot list or an earlier brief disagrees with that plan, the plan wins.

| What | Path |
| --- | --- |
| Current plan | [`ACT-I-PLAN.md`](ACT-I-PLAN.md) |
| 5 Nov recovery | [`checkpoint/RECOVERY-2026-11-05.md`](checkpoint/RECOVERY-2026-11-05.md) |
| Original recovery | [`CHECKPOINT.md`](CHECKPOINT.md) and [`checkpoint/SHA256SUMS`](checkpoint/SHA256SUMS) |
| Working review download | [`checkpoint/RECOVERY-2026-11-05.md`](checkpoint/RECOVERY-2026-11-05.md), media `ec5d1b4f-aa83-4257-b5f7-2323d1469f70` |
| Encoded opening | [`TEST-TWO-RECORD.md`](TEST-TWO-RECORD.md) |
| First cut | [`OPENING-SAMPLE.md`](OPENING-SAMPLE.md) |

The 3:00 PM brief is [`OPENING-TEST-TWO.md`](OPENING-TEST-TWO.md). It does not override the plan.

## What this slot is

The long-form pilot. Desk files are in `inbox/VIDEO-PACK-v2/`, unchanged. The retrieval note is `PACK-RECEIPT.md`. Do not treat Edward Short #31 as this film.

## From the pack

| Item | Value |
| --- | --- |
| Pack | VIDEO-PACK v2.1, repinned after 12:50 PM America/Toronto |
| Subject | Edward II / Edmund, Earl of Kent |
| Shape | Three acts. Estimate 805.6 s (13:25.6) at 2.4 words/s, about 1:25 over the ~12 min target. Re-time to the recorded VO |
| Title | The Letter for a Buried King. Owner, 1:44 PM |
| Script | `sources/raw/script-vo-v3.2-LOCKED.txt`. 101 lines, 1,884 words, md5 `11f4e6f9ac7d640d006dac33533472f6`. Owner approved as is. Archivist countersigned. Do not edit it |
| Claim ledger | `sources/CLAIM-LEDGER-v3.2.md`, md5 prefix `8e824c98` |
| OPEN claims, keep out of narration | C02e, C11-b, C14b-b, C15, C16e-b, C17-b. C20 is disputed |
| Sample | Second cut revised after 8:25 PM. 70.733 s. See `TEST-TWO-RECORD.md`. The first cut remains 69.733 s. The rest of Act I is planned in `ACT-I-PLAN.md` and not generated |
| Score | The opening sample's second cut uses Penumbra from 0:30. The first cut still uses Anabasis I. Gregorian Chant is not in the plan |
| Maps | Engine only for routes, labels, and markers. Explorer's Chart is still a proposal |
| Feature plates | Opening set generated: H06, H01, N14, DK1, CB1, N01, N21. N22 not generated. Files stay in `var/`. The current funeral pictures are in `ACT-I-PLAN.md`. The jointed H01 attempt is not reused |

## Pipeline

| Piece | State |
| --- | --- |
| Delivery config | `config/delivery.yaml` approved |
| Voice config | `config/narration.yaml` approved, speed unknown. L04 and the spoken title were re-read for this cut. The other nine files were not replaced |
| Higgsfield | Closed at 12:33 PM America/Toronto on 5 Nov 2026. No further spending. Purchased assets stay. New stills are ordinary ChatGPT chats |
| Engine branch | PR #5, not merged |
| Technical test film | `pipeline-test/README.md`. Picture and one Oliver line verified. Not the episode |

## Restore everything that is outside Git

Git holds the plan, the engine code, the desk pack, and the font. It does not hold the films, plates, voice, or score. Confirm each sha256 before use. A later 404 on a provider URL means the file expired. The media id is the handle to keep.

1. Original recovery, the first cut. Manifest [`CHECKPOINT.md`](CHECKPOINT.md), per-file sums [`checkpoint/SHA256SUMS`](checkpoint/SHA256SUMS). Zip sha256 `6d0708c38a6a49d4c74022941477dbd9b4d6ef8382e4e4c61517464746275986`, 156,284,214 bytes. Media `aa75b380-355d-436f-a9e5-447703c1aed5`. Download `https://d2ol7oe51mr4n9.cloudfront.net/user_3Lbrwnemvw3b6zIMpp3eP4wjBUF/aa75b380-355d-436f-a9e5-447703c1aed5.zip`. Unzip root `edward-checkpoint-stage/`. It contains the first film, the generated plates, the sealing clip, the nine original Oliver takes and alignments, captions, Anabasis I, and the wordmark.
2. 5 Nov recovery, the revised opening's additions. Manifest [`checkpoint/RECOVERY-2026-11-05.md`](checkpoint/RECOVERY-2026-11-05.md). Zip sha256 `9d878329d8e072407c5e6e03715da6c20e28ac11e4bb6e9ea81e625dd4eab254`, 55,354,821 bytes. Media `383214a0-d820-4a68-a669-aff3d4e5e5d0`. Download `https://d2ol7oe51mr4n9.cloudfront.net/user_3Lbrwnemvw3b6zIMpp3eP4wjBUF/383214a0-d820-4a68-a669-aff3d4e5e5d0.zip`. It contains S003, S004, S007, S007a, S009, the re-read L04 and title, Penumbra, the effects configuration, and the shot clock. It does not replace the first-cut archive.
3. Working review. Zip sha256 `58628dc985788254c2d7e01ba52884c03b296e7fd30949df55397992f94068e1`, 63,693,219 bytes. Media `ec5d1b4f-aa83-4257-b5f7-2323d1469f70`. Download `https://d2ol7oe51mr4n9.cloudfront.net/user_3Lbrwnemvw3b6zIMpp3eP4wjBUF/ec5d1b4f-aa83-4257-b5f7-2323d1469f70.zip`. The file inside is `opening-sample-test-two-review.mp4`, sha256 `23ea109edcff7a01c42ffcc2f368c505da127abce105d2aa7354f49852e3cc4b`, 63,693,053 bytes. The 172,313,796-byte master, sha256 `9b4f84e9a30c290b3717e33db94cabaf42862082ad6a0c159089870d8d15256b`, was not uploaded. Rebuild it from the two archives with `python tools/assemble_opening_test_two.py --full`, then `python tools/assemble_opening_test_two.py --review`.
4. Lay the files out under `var/edward-ii-feature/` as the two manifests describe. Plates for the revised cut go in `opening-sample-test-two/plates/`. L04 and the title go in `opening-sample-test-two/vo/`. Penumbra goes in `retrieved/score/Penumbra.mp3`. The wordmark goes in `wordmark/posterity-master.png`. The first-cut plates, clip, and the nine original takes stay under `opening-sample/`.
5. The title font is in git at `assets/fonts/ofl/imfelldwpica/IMFePIrm28P.ttf`. The first-cut assembler reads that path. `ELEVENLABS_API_KEY` stays in the session secret field. It is not in git. Do not re-record a line unless a new read is authorized.
6. The Britain guide image is still only in `EDWARD-II-VIDEO-PACK-v2-MEDIA-part09-of-10.zip`. It is not in either recovery archive. Map registration waits on that file. Explorer's Chart is still a proposal.

## Next action

Make the ChatGPT list in [`ACT-I-PLAN.md`](ACT-I-PLAN.md). S004 stays the purchased raised-axe plate until that resting-axe still is accepted. The sealing clip stays. Do not submit a Higgsfield job, publish, or start the full film from this handoff. PR #5 stays unmerged.
