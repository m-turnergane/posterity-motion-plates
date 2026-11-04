# flames_v4 — every fire on the LOCKED torch_v1c treatment (2026-10-30)
Output: `final/flames_v4_reel.mp4`. 1080x1920, 30 fps, 17.000 s, 510 frames, 7,732,069 B, md5 e22c080aef829f6ad0984da3df4f4eb4.
Build: `flames_v4.py configs/reel_v4.json <new out>`. fx_v1c.py (md5 f31394f8…) is imported by path and unedited; smoke_v2 is untouched.
Shots (hard cuts): B13 7 s (push 1→1.06), P05 v2 7 s (push 1→1.06), live B10 cresset 3 s (no push).
- B13/B10: the fx_v1c spec as shipped, on the Edward master's own time base (t0 = slot f0/30). It includes the v1c haze/mist (screen-blend light). Removed: B13 foreground parallax (an affine displacement), and the candle flame_warp and teardrop on the three B13 back candles (they now render as steady torch-kind sources).
- P05: no Edward spec existed, so each of the 28 keyed flames_v2b town fires is a v1c torch source. Spill relight mask and feathered keep-out = the P05 protects (sky, sea, ships, glitter), which stay at 0 px changed. spill_amp 1.8, PULSE 0.13 (calibrated: `scratch/v4/calib*.py`). No embers.
- Smoke: none. The torch wisps are left out: v1c had none, and any moving plume next to the torches works against "surroundings steady". The P05 big-fire smoke is also left out: when in doubt, leave it out. The P05 sky plumes are static (no billow).
Proofs (`proofs/v4/`):
- `proof_v4_impulse_0px.r2.json`: impulse leak = 0 on all shots, so the displacement is exactly 0 px everywhere (no resampling).
- `proof_v4_reel.r2.json`: warp 0 and parallax off; P05 protect changed px = 0 and guards unchanged. Its phase-shift "pass:false" on B13/B10 is an estimator artifact (~0.5 px on identical odd-sized patches; see `diag_phasecorr_odd_patch_artifact.txt`).
- Phone stats: `reelstats_flames_v4_reel.r2.json`.
- `diag_v1c_vs_v4_haze_window.json` shows why the haze is kept.
Scratch render `scratch/v4/render/flames_v4_reel.mp4` (r1: haze off, t0 6) was superseded by r2 and kept, not deleted.


## LOCKED 2026-10-30 (owner): flames = flames_v4 / torch_v1c, all fire sizes
* The owner locked flames on **flames_v4 / torch_v1c** for every fire size, from candles and torches up to the large plate fires. Owner's words: "much better for the larger flames in our plates, simple and does the job".
* What it is: the painted flame shape holds, with a coherent glow and a local spill pulse at v1c strength, each on ONE scalar per frame per static map. There's no tongue, warp, displacement or moving light gradient. Protects stay at 0 px (verified by the impulse test).
* Reference: `final/flames_v4_reel.mp4` (md5 e22c080aef829f6ad0984da3df4f4eb4). Code: `flames_v4.py` + `configs/reel_v4.json`. Preset: `motion/PRESETS.md` section "torch_v1c (LOCKED 2026-10-30 by owner)".
* flames_v1–v3 / v3b are R&D only. Don't use them for new shots.
