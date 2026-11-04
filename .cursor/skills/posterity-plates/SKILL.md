---
name: posterity-plates
description: Plan and review Posterity plates against Recovered Chronicle rules, references, and the budget gate. Use before any image generation or plate repair.
---

# Plates

1. Confirm `config/budget.yaml` `higgsfield.status` is not `blocked`, `image_model` is set, and `hold` is empty. If status is blocked, the model is empty, or `hold` names missing media or an owner pick, write what is missing and stop. Do not call Higgsfield.
2. Read template v2 in `intake/atelier-jr-2026-11-04/02-reference-paintings-and-prompts/prompts/HOUSE__PLATE-PROMPT-TEMPLATE-v2.md`. Scene first, one to four constraints.
3. Masters are unlettered 16:9. Do not crop a 9:16 Short plate into 1920×1080.
4. Generate only inside the approved cap, in batches of 4–6, after gate 4. Save job ids before polling.
5. Accept a still only after looking at identity, anatomy, costume, architecture, geography, invented text, and paint surface. An API success is not a KEEP.
6. Record the chosen file, md5, and job id on the shot manifest. Rejected takes stay on disk and out of git.
