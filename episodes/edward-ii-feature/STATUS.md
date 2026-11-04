# Edward II / Kent feature

status: READY_FOR_PREP_PACK
updated: 2026-11-04
timezone: America/Toronto

## What this slot is

The production path for a 16:9 feature is being verified on this branch. The episode pack itself was kept off the 4 Nov handoff on purpose. Drop it here, unchanged, under `inbox/`. Do not treat the Edward Short (#31, portrait, about 88.5 s locked / 92.0 s earlier rough) as this film.

## Known without the pack

| Item | Value |
| --- | --- |
| Subject | Edward II / Edmund, Earl of Kent |
| Shape | About 12 min, 8 movements, native 16:9 |
| Title | UNKNOWN |
| Script | Named, not present: `script-proposal-v1.md` and `raw/script-vo-v1-DRAFT.txt` (Scriptor, 4 Nov 2026, 1,682 words, about 11:41). DRAFT, not locked |
| Claim ledger | Named, not present: `CLAIM-LEDGER-v1.md` (30 Oct). 43 rows. Gate 2 sign-off unknown |
| OPEN claims, keep out of narration | C02e, C11, C14b, C15, C16e, C17 |
| Plate budget | 33–34 masters = 30 owner generations + 3–4 desk-built. Not owner-approved |
| Feature plates | None |
| Score | Unknown. Gregorian Chant is not approved for the feature |
| Sample window 03:05–04:55 | Unconfirmed |

## Pipeline

| Piece | State |
| --- | --- |
| Delivery config | `config/delivery.yaml` approved |
| Voice config | `config/narration.yaml` approved, speed unknown |
| Higgsfield | Blocked, no cap |
| Engine branch | PR #5, not merged |
| Technical test film | `pipeline-test/README.md`. Picture verified. Narration blocked: the stored secret is a key ID, not an `sk_` key. |

## Next action

Wait for the prep pack. Then run gate 4 (shot list and plate packet) before any plate generation.
