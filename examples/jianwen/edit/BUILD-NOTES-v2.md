# Jianwen v2 build notes (2026-10-30, America/Toronto)

Title: DID THE EMPEROR WALK OUT OF THE FIRE?  VO: vo/final-vo-oliver-jianwen-v2.wav (speech ends 89.28 s; tagline 85.23 s, not captioned).
Build: `/workspace/mpvenv/bin/python edit/build_rough_jianwen_v2.py` (refuses to overwrite; refuses unlanded / todo plates; asserts >= 4 GiB free).

## Files
- build_rough_jianwen_v2.py -- the build (pre-smoke original in superseded/2026-10-30_v2_pre-smoke/, K01-K05 state in superseded/2026-10-30_v2b_k01-k05/)
- fx_jianwen_v2.py -- locked templates (md5 6c4160305cd8e6ef9f2b09c11b5780a6, untouched)
- fx_jianwen_v2b.py -- real per-plate fx for K01-K11 + smoke_v2 + grade + framing + pulse calibration + LEGEND position
- smoke_v2 imported BY PATH from engine-rnd/smoke/smoke_v2.py (md5-locked 80bb28695757f7568b005e8ba8327bde; nothing under engine-rnd/ edited or copied)

## Layer order
PlateFX (flicker/glow/spill/embers/mist; ALL flame shapes static -- no candle warp, no lantern sway, no billow/parallax displacement)
-> smoke_v2 (pre-roll, protect masks at 0 px, per-slot zero-motion proof every 15 f) -> grade -> crop -> 2x Lanczos cover to 1080x1920
-> StablePush -> title / LEGEND overlay -> ASS captions (libass, on top).

## Pulse calibration (spill only; halo + painted-flame brightness flicker unchanged)
Measured on the real plates, 90 f, atmos off; whole-frame swing / max step:
k01 0.11 5.9%/0.88 | k02 0.25 5.8%/1.14 | k03 0.03 9.7%/1.04 (halo floor 6.3%) | k04 0.045 5.7%/0.88 | k05 0.075 6.1%/1.02
k06 0.035 5.7%/1.06 | k07 0.02 8.5%/1.39 (halo floor 6.6%) | k08 0.03 6.5%/0.80 | k09 0.12 5.9%/1.08 | k10 0.03 5.9%/0.65 | k11 0.35 1.9%/0.30
(was 0.35 everywhere: up to 47.5% swing -> the k01-k05-a previews pumped; superseded by k01-k11-b.)

## LEGEND (S12/K11)
Owner 12:13: TOP-CENTRE (align=center, xPct 50 = label centre, cap top yPct 5.5, 36 px). Clear of the moon (upper-right) and the
upper-left tree for the whole push (qc/v2b-k06-k11/test_01395_S12.png, test_01470_S12.png). Smoke protect group legend_top = frac [0.28,0,0.72,0.13].

## Previews
previews_v2/k01-k11-b/S01..S12_360x640.mp4 + S01-S12_360x640.mp4 (VO only, not the mix). QC stills: qc/v2b-k06-k11/.
Full master only when all 20 plates + the outro have landed (K12-K19 + outro still templates).
