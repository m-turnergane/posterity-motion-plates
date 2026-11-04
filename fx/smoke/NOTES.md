# smoke R&D notes (state as of 2026-10-30, ~11:00 AM EDT)

Status: the PoC is done (overlay half of the spec). I stopped before polishing, per the owner's steering.

Done
- smoke_v1.py: plume emitters (candle/torch/column) plus haze, curl-warped advected periodic noise, depth layers,
  under-glow flicker, billow relief, ease-in, StablePush, ffmpeg writer, zero-motion proof, CLI.
- configs: b19_candle_wisps.json, p05v2_burning_town.json.
- poc/: b19 8 s and p05v2 8 s 1080x1920 clips with 360x640 grabs. Zero-motion: max_diff_outside = 0 on both.

Tuning history
- Speckle outside the plume came from the noise term where core≈0. Fixed by scaling with sqrt(core) and adding a core gate.
- The p05 column read as a pale orange veil. Fixed with darker colours, hi 5, detail 0.35, glow reach 0.14, and the relief emboss.

Next (not started)
1. Part (b): SMOKE MATTE billow of painted plumes (p05/p01/p06). Displace and re-shade the painted smoke only inside
   a feathered matte, with 0 px outside, verified by diff.
2. Torch demos (b10/b13) and haze-led plate (p01/p06).
3. Polish: candle "wormy" contour look, softer column edges, protect-edge seams, more volumetric glow.
4. Speed: cache per-row envelopes and render the back layers at half-res (p05 is ~1.7 s/frame).
5. Final banger reel (no text/vignette/letterbox, push 1.00→1.06).

---
## v2 progress log (smoke_v2.py) — updated 2026-10-30 11:29 EDT

Done (all with zero-motion proofs = 0 outside footprint / in protect / in guards):
- Pre-roll (`preroll`, default 8 s) — smoke established at frame 0; global fade-in removed (`ease_in` default 0).
  Per-emitter `start`/`end`: plumes grow up from the source (rising front), haze spreads from its centre.
- Fire auto-detection (`fires` block) -> one emitter per fire, sized by flame area (column/torch/ember classes);
  `flame_keepout` lets flames show through; `push_center` fixed-point push.
- smoke_key `dark_rel`/`rel_sigma` (local-darkness key for smoke vs similar-coloured sky).
- Haze `beta` (spectral slope; higher = softer).
Configs (configs/): b19_candle_wisps_v2, b10_wall_torch, b13_three_torches, p05v2_every_fire (46 auto plumes),
  p01v2_city_plumes (billow + 5 distant fire plumes), p06_doorway_plumes (billow + 5 base columns), p06_street_haze (haze-led).
Lessons: torch smoke over a torch-lit wall must be cool grey and low-detail (warm/high-detail reads as stone texture);
  flame_keepout must be 0 when the wall itself is fire-coloured — protect the flame body with a polygon instead.
Next: final reel (configs/reel_final.json), contact sheet, per-shot proofs, README v2 section.
Yield watch: jianwen/plates-v1 AND plates-v2 (scratch/yield.sh).
- 11:33 EDT: final reel rendered (final/smoke_v2_final_reel.mp4, 26 s, 1080x1920@30, 5 shots, --jobs 5 in ~2 min);
  final/proofs.json all zeros (0.5 s sampling); diff_*.png + contact_sheet.png written. README v2 section added.
Weak spots: p01 coast plumes small at 360; p05 light veil over town at 1:1; torch smoke reads mostly in motion;
  b13 fore-torch plume starts ~30 px above flame tip (protect feather gap); painterly texture < painted smoke.
