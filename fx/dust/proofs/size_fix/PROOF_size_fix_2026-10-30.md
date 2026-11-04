# dust_v1 size-density fix: proof (2026-10-30, ~5:49pm ET)

Change: guard() now passes out_wh=out_size(cfg, size) to guardrails.check_shot (was the 1080x1920 default).
render() passes its --size; reel() passes the reel's size. No visual math touched (diff = 3 lines: guard def/body, render's guard call, reel's guard call).
dust_v1.py md5 9ea7ab68e3f64ebd25dbd3e82da6e00b -> c0ad4ef55357ddd47ca73b9a93ffc760
Backup: engine-rnd/dust/superseded/dust_v1.py.pre-size-density-2026-10-30

Locked reels re-rendered with the patched file (dust_v1.py reel <cfg> <out>), compared by md5 + cmp:
- reel_v1     -> dust_v1_reel_rerender.mp4      acc858d393bcf785363a52e466aceed3 == final/dust_v1_reel.mp4      BYTE-IDENTICAL
- reel_ref_v1 -> dust_v1_ref_reel_rerender.mp4  74744cd11f6c37452e9568081f3179e1 == final/dust_v1_ref_reel.mp4  BYTE-IDENTICAL
(Encode is deterministic, so framemd5 fallback not needed.)

Size tests (t1a_tomb_shaft_v1c, plate seq1a.png 941x1672, push 1.06):
- render --size 1920x1080 --seconds 0.1 -> REFUSED (exit 1, GuardrailError 2.163 px/px > 1.5), no file written
- reel with size 1920x1080 (test_reel_1920x1080.json) -> REFUSED (same error), no file written
- render --size 1080x1920 --seconds 0.1 -> OK (exit 0, 1080x1920, 3 frames, density 1.217)
