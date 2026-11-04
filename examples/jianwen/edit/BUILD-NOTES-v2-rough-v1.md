# Jianwen v2 — ROUGH v1 build notes (2026-10-30, EDT)

## Deliverables
- MASTER  renders/posterity-jianwen-v2-ROUGH-v1.mp4  md5 0f148f172e3fe0074c71dd599f7e8e30  89,349,527 B  1080x1920 h264 30fps 2700f, AAC 48k, 90.000 s
- PREVIEW renders/posterity-jianwen-v2-ROUGH-v1-preview.mp4  md5 589b1a28ba494aacef6065c935a159a9  31,305,713 B  720x1280, 90.000 s
- Slot previews: edit/previews_v2/rough-v1-pv/ (S12-OUTRO_360x640.mp4 md5 119859c0…)
- Audio: ebur128 independent: I -14.1 LUFS, TP -1.7 dBFS, LRA 2.4 LU

## Per-plate (K12–K19, outro)
- K12 (S13): auto candles + flame-shape warp, warm mist (faces excluded); pulse .05; no smoke (lit candles).
- K13 (S14): amber grade lift(.010,.004,0) gain(1.04,1,.90); 3 lanterns gentle sway (0.7–0.8°); thin slow incense smoke (opacity .30), faces+lanterns protected (guard 0).
- K14 (S15): manual candle + warp, far lantern static glow; pulse .10; no smoke.
- K15 (S16): 9 torches static shapes, glow+spill (wet ground excluded), smoke_v2 plumes torch + gate x2; moon/water/faces protected (guard 0); dust mist, 6 embers.
- K16 (S17): candle + warp, lamp glass glow; pulse .12; no smoke.
- K17 (S18): single candle + warp; pulse .08; no smoke.
- K18 (S19): candle flick_mult 1.5 (harder flicker), pulse .15; max step ≤1.25%/f plate-level, no strobe; no smoke.
- K19 (S20): candle; page frozen (freeze_proof.json: 90 frames, diff 0 plate and 0 post-grade/cover); no smoke.
- OUTRO: static z=1.0, baked lettering as-is & frozen (diff 0 over 146 frames), window + torch glow/spill only, mist only y≥1260, no captions (last caption ends ≤ OUTRO_T 85.133 s).

## Owner 12:59 — LEGEND removed
LEGEND=dict(enabled=False); legend_layer returns None; 0 frames with legend overlay; S12 has 0 overlay frames; S12 smoke protects moon/tree (legend_top dropped). Visual check of S12 frames: no tag text.
Note: timeline.json still carries the locked grid's S12 motion-note string "…LEGEND label upper-left" (metadata only) and the plate filename k11_LEGEND_…; neither renders.

## QC files (qc/v2-rough-v1/)
qc_overlays_captions.json, judge_master_360x640.json, steps_vs_captions.json, flicker_residual_nocaption.json, freeze_proof.json, test_*_S02A/S02B (title/hat), contact_sheet.jpg
