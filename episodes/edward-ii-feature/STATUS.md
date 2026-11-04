# Edward II / Kent feature

status: OPENING_TEST_TWO_LOCAL
updated: 2026-11-04
timezone: America/Toronto

Current handoff: [`TEST-TWO-RECORD.md`](TEST-TWO-RECORD.md). The brief is [`OPENING-TEST-TWO.md`](OPENING-TEST-TWO.md). The first-cut record is [`CHECKPOINT.md`](CHECKPOINT.md) and [`OPENING-SAMPLE.md`](OPENING-SAMPLE.md). The comparison film is unchanged.

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
| Sample | Cut. 69.733 s, retimed to the Oliver recording. See `OPENING-SAMPLE.md`. Act II and the map test were not in this pass |
| Score | Act I is Anabasis I, overriding Penumbra. The other four candidates stay on disk. Gregorian Chant is not in the plan |
| Maps | Engine only for routes, labels, and markers. Explorer's Chart is still a proposal |
| Feature plates | Opening set generated: H06, H01, N14, DK1, CB1, N01, N21. N22 not generated. Files stay in `var/` |

## Pipeline

| Piece | State |
| --- | --- |
| Delivery config | `config/delivery.yaml` approved |
| Voice config | `config/narration.yaml` approved, speed unknown. Opening lines L01–L05, L07, L07a, L08, L09 rendered once |
| Higgsfield | Sample phase authorized. 62 credits spent, 48 remaining at 3:49 PM America/Toronto. Test-two stills are quoted and not submitted. See `TEST-TWO-RECORD.md` |
| Engine branch | PR #5, not merged |
| Technical test film | `pipeline-test/README.md`. Picture and one Oliver line verified. Not the episode |

## Next action

The local test-two renderer is in. `opening-sample-test-two.mp4` is not encoded. Five plates are still the wrong picture, and the 23.50-credit ask in `TEST-TWO-RECORD.md` has no answer yet. Do not submit a generation before that cap is a number. The full film, the outro, and any plan upgrade wait. Explorer's Chart is still a proposal. PR #5 stays unmerged.
