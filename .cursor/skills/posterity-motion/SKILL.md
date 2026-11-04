---
name: posterity-motion
description: Choose deterministic or generative motion for one Posterity shot, run it, and check drift. Use when a plate needs a move.
---

# Motion

1. Prefer a locked deterministic preset (push 1.00→1.06 scale-only, torch_v1c, fx_candle, smoke_v2, water_v1, dust_v1). depth_v1 stays off unless `docs/decisions.md` says otherwise.
2. Use Higgsfield video only when the shot needs new physical motion and `config/budget.yaml` allows spend. Otherwise do not submit.
3. Run from branch `engine/consolidate-2026-11-04` for house FX. `fx/water/water_v1_1.py` and `fx/dust/dust_v1.py` load `engine/motion/guardrails.py`.
4. Poll the saved job id after a timeout. Do not submit a second paid job for the same shot.
5. Inspect the first, middle, and last frames. Reject face or costume drift, invented text, rubber motion, and glossy surfaces. If QC fails, the still plate is the fallback.
6. `src/motionplates` on this branch remains the experimental plate engine. Frame 0 must match the plate.
