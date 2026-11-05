# AUDIT — Edward II v1c torches vs flames v2b / v3 (2026-10-30)

**Owner verdict (2026-10-30):** v3 "was distorting the things around it". The **Edward II v1c
torch treatment is LOCKED as the house torch standard, exactly as shipped** ("more like a
pulsing effect"). No tweak, no boost. flames_v1–v3 remain R&D only.

Preset entry: `docs/TORCH-V1C.md`

## Sources measured (read-only)

- Master `renders/posterity-edward-ii-v3b-ROUGH-v1c.mp4` (md5 `b4f0aa7a68619ed5928738698f6e2eaf`;
  1080×1920, 30 fps, 88.53 s).
- `standalones/edward-ii/edit/fx_v1c.py` (md5 `f31394f82a890b94d7670b009e984ce8`), with the LOCK
  `motion/presets/locked/house-candle-lightspill-v1.json` (md5 `0591d4c770c5363f1ca6135a5d961d17`)
  and engine helpers `presets/locked/engine/animate_b3_cb9e2b88.py` (md5 `cb9e2b880ab7b6940043ce3723de590a`).
- Torch / cresset slots: **S10 b10 cresset** f954–1056 (3.4 s), **S13 b13 three torches** f1274–1400 (4.2 s).
  Same plates (941×1672) as the flames configs, so the v3b surface boxes compare directly.

## Method

Phone = 360×640 INTER_AREA; swing = (max−min)/mean of a surface's mean luma in 1 s windows,
0.5 s step, median reported (the v3 `spill_report` metric), surfaces minus the flame zone.

(A) decoded master: boxes mapped per frame through cover-fit + the build's StablePush;
caption band (phone y 455–525) excluded.

(B) in memory: `fx_v1c.PlateFX(...).render(f/30, u)` — no push, no captions. A and B agree
within ~2 points, so the numbers are real, not codec/caption noise.

## Results — swing % at 360×640 (1 s windows, median)

| Surface | v2b | v3 (REJECTED) | **v1c master (decoded)** | v1c in-memory |
|---------|-----|---------------|--------------------------|---------------|
| B13 left_doorframe_wall | 3.4 | 18.1 | **38.7** | 36.3 |
| B13 right_door_wall | 1.5 | 16.2 | **38.4** | 36.7 |
| B13 left_stone_wall | 0.4 | 5.1 | **13.6** | 13.7 |
| B13 stairs L / R | 3.7 / 3.7 | 10.9 / 10.3 | **27.1 / 28.0** | 24.5 / 21.8 |
| B13 guard_face_l / r | 0 / 0 | 13.4 / 10.4 | **26.4 / 23.6** | 28.0 / 23.9 |
| B13 edward_face | – | – | **31.4** | 32.2 |
| B13 torch_holder_l_face | 0 | 17.3 | **23.0** | 24.5 |
| B13 coif chainmail L / R | 0.02 / 0 | 6.7 / 9.0 | **20.0 / 17.5** | 19.9 / 17.7 |
| B13 whole frame (1 s) | 4.9 | 5.8 (reel 7.1) | **14.2** (3 s p-p 20.1; max step 3.1 %) | 12.9 |
| B10 wall above / right of cresset | 4.4–4.9 | 15.9–18.6 | **41.8 / 46.3** | 40.4 / 44.4 |
| B10 pillar below | 3.0 | 10.7 | **33.2** | 33.1 |
| B10 gaoler_face / kent_face | 0 / – | 12.7 / – | **38.3 / 25.3** | 36.6 / 26.0 |
| B10 shoulder chainmail | 0 | 6.3 | **29.2** | 27.3 |
| B10 whole frame (1 s) | 3.1 | 6.4 (live 6.1) | **13.6** (max step 2.4 %) | 12.7 |

Energy above 5 Hz in the whole-frame signal: v1c 0.005–0.007 (no strobe). It reads within
1 s on a phone: the whole room breathes warmly.

## What this shows (the honest finding)

**v1c is not "weaker" than v3 — it is 2–3× STRONGER in luma swing.** What the owner likes is
the *kind* of change, not a low amplitude:

1. **v1c spill is one coherent pulse.** Each spill group's map is static
   (`amp·fall·facing·relight`, precomputed) and is multiplied per frame by ONE scalar
   `dl = mean(f−1)·min(√n,2.5)·PULSE[plate]`. Every pixel in a group rises and falls together,
   so it reads as light breathing, never as a shape moving. Falloff is soft and wide:
   `1/(1+(d/r)^2)`, r = 800·1.3·0.32·√clip(h/26,0.5,3) ≈ 330–570 px on these plates, with a
   facing term and relight mask.

2. **v3 spill varies in space and time.** Per-source clocks, exp falloff with a tight radius,
   vertical tongues and a moving flame-edge light field mean the brightness gradient *moves*
   across walls and faces. On the phone that reads as the surroundings warping, even at half
   v1c's swing. The heavy billow added flow-map/curl marbling on top.

3. v1c torch flames never change shape: the plate_flame gain only brightens the keyed flame
   pixels toward hot (255,238,190). There is no tongue (torch tongue = 0), no warp (warp is
   for candles with h ≥ 5 only) and no remap.

## Decisions

- **Boost recommendation: DROPPED.** v1c is locked as shipped.
- **v3 strong spill: REJECTED** for torch surroundings (it moves gradients across walls and faces).
- **v3 heavy sky billow: REJECTED** (marbling/smear at full res; reads as warping).
- **v3 vertical tongues: REJECTED on torches** (owner: painted flame shape holds). R&D only.
- **v3 size-scaled sparks:** not needed; v1c embers are the torch particle standard.
- **Keep from v3: the proof methods** (protect/guard 0-px checks, phone-scale swing per surface,
  matte-overlap checks), plus the new impulse test (v4) as the exact 0-px proof.

Note: `phaseCorrelate` returns ~0.5 px on IDENTICAL odd-sized patches
(`proofs/v4/diag_phasecorr_odd_patch_artifact.txt`), so use the impulse test, not phase shift,
as the pass/fail.

## See Also

- `docs/TORCH-V1C.md` — torch_v1c preset documentation
- `docs/NATURAL-FIRE-RND.md` — Natural fire R&D notes (SUPERSEDED for production)
- `src/motionplates/rnd/` — R&D modules (flames_v1–v3)
