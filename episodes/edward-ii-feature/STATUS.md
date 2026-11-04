# Edward II / Kent feature

status: PACK_V2_1_IN
updated: 2026-11-04
timezone: America/Toronto

## What this slot is

The long-form pilot. Desk files are in `inbox/VIDEO-PACK-v2/`, unchanged. The retrieval note is `PACK-RECEIPT.md`. Do not treat Edward Short #31 as this film.

## From the pack

| Item | Value |
| --- | --- |
| Pack | VIDEO-PACK v2.1, repinned after 12:50 PM America/Toronto |
| Subject | Edward II / Edmund, Earl of Kent |
| Shape | Three acts. Estimate 805.6 s (13:25.6) at 2.4 words/s, about 1:25 over the ~12 min target. Re-time to the recorded VO |
| Title | Not picked. Recommended: The Letter for a Buried King |
| Script | `sources/raw/script-vo-v3.2-LOCKED.txt`. 101 lines, 1,884 words, md5 `11f4e6f9ac7d640d006dac33533472f6`. Owner approved as is. Archivist countersigned. Do not edit it |
| Claim ledger | `sources/CLAIM-LEDGER-v3.2.md`, md5 prefix `8e824c98` |
| OPEN claims, keep out of narration | C02e, C11-b, C14b-b, C15, C16e-b, C17-b. C20 is disputed |
| Sample | Opening, about 83.6 s: S001–S005, SC01+SC02, S007–S009. Optional Act II sample includes the ME1 map test |
| Score | Five Scott Buckley CC BY 4.0 candidates are on this disk, checksums matched. Act I pick is still Penumbra (recommended) or Anabasis I. Gregorian Chant is not in the plan |
| Maps | Engine only for routes, labels, and markers. Explorer's Chart is still a proposal |
| Feature plates | None generated. Prompts are in `PLATE-PROMPTS.md` |

## Pipeline

| Piece | State |
| --- | --- |
| Delivery config | `config/delivery.yaml` approved |
| Voice config | `config/narration.yaml` approved, speed unknown. Feature lines not rendered |
| Higgsfield | Sample phase authorized. Hold `reference-media`: 40 atlas guides and 21 Short plates are not on disk. Model `nano_banana_pro`. Nothing generated |
| Engine branch | PR #5, not merged |
| Technical test film | `pipeline-test/README.md`. Picture and one Oliver line verified. Not the episode |

## Next action

The owner picks are in `inbox/VIDEO-PACK-v2/DECISION-BUNDLE.md`: the yes/no plan, the title, the tagline-on-screen choice, and the wordmark master. The opening sample waits on those picks and on the atlas guides and Short plates.
