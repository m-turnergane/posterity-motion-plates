# Posterity / Atelier Jr

The owner is the creative gate. This agent runs routine production and does not publish.

## Start

1. Read `docs/knowledge-index.md` and `docs/decisions.md`, then the active `episodes/<id>/STATUS.md`.
2. Open only the playbook or workflow section the task needs. Desk originals are in `intake/atelier-jr-2026-11-04/`. The desk index wins over the ChatGPT handoff.
3. Resume saved jobs and configs before any new paid call.

## Standing rules

- Keep approved narration, claim status, and references. Separate standing rules, episode choices, and proposals. Do not invent research, settings, URLs, or metrics.
- Long-form is native 16:9. Shorts are native 9:16. Do not crop a Short plate into 16:9.
- Higgsfield for this long-form experiment only, after one style sample and then a full review cut, and only inside `config/budget.yaml`. Shorts plates stay owner-generated. ElevenLabs stops for a fresh ask before about 30,000 draft credits.
- Secrets stay out of the repo, logs, and prompts. Large media stays out of git. Checksums may be committed.
- The lead owns story, pictures, and the shared spend ledger.

## Motion plates in this repo

`src/motionplates` stays the deterministic plate engine. These rules still bind that package:

1. Plates are read from `--plates` or `$MOTIONPLATES_PLATES`. Do not copy plates into git. Do not commit `*.mp4` or `*.png` outside `tests/data` and the ignored preview exceptions.
2. Frame 0 matches the cover-fit plate. Effects start from zero. The fading residual corrects the clean-plate swap.
3. Randomness comes only from `ctx.rng(name, idx)`. No clock and no global RNG. Any frame can render alone with `--at`.
4. Camera push stays a few percent and eased. No generic Ken Burns. Flicker is multi-band smooth noise, not a uniform pulse.
5. If a motion MP4 is missing or fails QC, the original plate is the fallback. Playback approval is per `frames_sha1`.
6. No network publishing and no secrets in the tree. Do not merge to master or turn this on in production without the owner's approval.

The consolidated house engine is branch `engine/consolidate-2026-11-04` (PR #5). Do not resolve its `tests/test_motionplates.py` conflict from this branch.
