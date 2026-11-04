---
name: posterity-intake
description: Normalize a Posterity desk pack into a claim-linked shot manifest and a list of missing assets. Use when a new episode folder or inbox arrives.
---

# Intake

1. Read `docs/knowledge-index.md`, `docs/decisions.md`, and `episodes/<id>/STATUS.md`.
2. Leave the desk files unchanged in `episodes/<id>/inbox/`. Record byte size and md5 in STATUS.
3. If the spoken script, claim ledger, or shot list is absent, stop and say so. Do not draft them.
4. Write `episodes/<id>/manifest.json` only from rows that cite a claim id present in the ledger. Fields: movement_id, scene_id, shot_id, plate_id, vo_id, claim_ids, purpose, prompt, motion, duration_estimate_s, status.
5. Mark estimates as estimates. Exact timing waits for the accepted voice recording.
6. List asset requirements and which OPEN claims are excluded from narration.
