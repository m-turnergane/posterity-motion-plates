# Edward II / Kent feature

status: ACT_I_PLAN_READY
updated: 2026-11-04
timezone: America/Toronto

Current handoff: [`ACT-I-PLAN.md`](ACT-I-PLAN.md). The encoded opening is [`TEST-TWO-RECORD.md`](TEST-TWO-RECORD.md). The 3:00 PM brief is [`OPENING-TEST-TWO.md`](OPENING-TEST-TWO.md). The first-cut record is [`CHECKPOINT.md`](CHECKPOINT.md) and [`OPENING-SAMPLE.md`](OPENING-SAMPLE.md). The comparison film is unchanged. Where the shot list or the 3:00 PM brief disagrees with the plan, the plan wins.

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
| Feature plates | Opening set generated: H06, H01, N14, DK1, CB1, N01, N21. N22 not generated. Files stay in `var/` |

## Pipeline

| Piece | State |
| --- | --- |
| Delivery config | `config/delivery.yaml` approved |
| Voice config | `config/narration.yaml` approved, speed unknown. L04 and the spoken title were re-read for this cut. The other nine files were not replaced |
| Higgsfield | Test two spent 22.00 of an authorized 23.50, all 8 submissions. Balance re-read at about 8:30 PM America/Toronto was still 26. The next still is quoted in `ACT-I-PLAN.md` and not submitted |
| Engine branch | PR #5, not merged |
| Technical test film | `pipeline-test/README.md`. Picture and one Oliver line verified. Not the episode |

## Next action

The opening cut matches `ACT-I-PLAN.md` except S004, which is still the raised-axe plate. The resting-axe still is quoted at 2.75 credits, with one retry, and has not been submitted. A 1080p landing clip is quoted at 96 and does not fit the 26-credit balance. Do not submit either, merge, publish, or start the full film until that spend is authorized. Explorer's Chart is still a proposal. PR #5 stays unmerged.
