# Natural-fire R&D — P05 forge (day21/atahualpa) — 2026-10-23

> **STATUS: R&D ONLY — SUPERSEDED FOR PRODUCTION (2026-10-30)**
>
> This natural-fire R&D work (and the flames_v1–v3 experiments) has been superseded by
> **torch_v1c**, which is LOCKED as the house torch standard. The owner verdict was that
> v3 "was distorting the things around it" while v1c is "more like a pulsing effect".
>
> For production torch/cresset/brazier/larger-fire work, use `src/motionplates/standalone/fx_torch.py`.
> See `docs/TORCH-V1C.md` for the production preset documentation.

Scope: one POC, 6 s, 1080x1920@30, no audio. Nothing in prod touched (renders/, configs, masks, PRESETS.md, presets/locked read-only).
Engine: locked `animate_b3_cb9e2b88.py` (the md5 prod v2c asserts; brief said "b9" — b3/cb9e2b88 is the one that reproduces prod bit-exactly).
Repro check: `qc/verify_static_vs_prod.json` — our pipeline reproduces prod `P05_static.mp4` frames 0/1/76/152 bit-identically.

## Method in one line
Animate the *plate* inside the three prod flame masks only, then run the unchanged v2c engine (same relight, spill, halo, pool,
same flicker curves) and the prod camera. Because the engine's emit stage is pointwise, glow and everything outside the masks are
bit-identical to v2c; the flame's own pixels get relit by the same pulse (coupling for free), and flame activity is driven by that
same per-source flicker curve (flares fire on the glow's peaks).

## References (tools/ref_analysis.py, tools/ref_hp.py; licences in ref/ref_flow_stats_raw.json)
- fireplace_bosnia (CC BY-SA 4.0) — best match (enclosed fire). DIS: V/L 2.4–3.7, upward .90–.99, rise .37–.50 H/s.
  HP-pattern (static removed): rise .34–.55 H/s, top-half .45–.68, ac1 ~.39.
- campfire_claytor (CC BY 2.0) — HP rise .52–.83 H/s; DIS unreliable (camera reframes, saturated core).
- fire_bastique (PD) — free candle-ish flame on black, much more lateral (HP V/L .6), not representative of a forge mouth.
- forge_etueffont (CC BY 4.0) excluded: mostly no visible fire in the usable window.
Glow-only v2c baseline (v00_static) in the flame masks: per-frame change 2.0 % mean (max 7.9 % — the v2c pulse itself), HP rise 0.

## Iterations (plate-space previews, iter/<v>/: strip12_c*.png consecutive, strip_0p5s_forge.png, kymo.png, stats.json, hp.json)
| v | change | HP rise H/s c0/c1/c2 | DIS V/L c0/c1 | per-frame chg % mean (c0/c1/c2) | verdict |
|---|---|---|---|---|---|
| v00 | static (v2c) | 0/0/0 | 1.35/0.89 | 2.11/2.02/1.91 | reference for "glow only" |
| v01 | fbm displacement + intermittency gate only | n/a | 3.3/2.0 | 2.96/3.27/2.19 | jiggle, not travel: DIS rise .07–.11, pattern doesn't move up |
| v02 | + flow-map upward advection of the flame's own paint (2 phases, per-pixel offset, variance-preserving detail re-injection), inpainted flame-only source | 1.18/1.01/.35 | 4.5/4.2 | 2.94/3.31/2.18 | real upward travel (kymo diagonals) but too fast (gate/noise 60–80 px/s) and too faint |
| v03 | slower noise (V 35, Vg 45), D 20 | .62/.58/.34 | 5.5/5.0 | 2.77/3.17/2.19 | speeds now in the bosnia/claytor band; visually almost indistinguishable from static — too timid |
| v04 | bolder: gate .9 from mid-height, darker gaps, D 26, amp_y 4, soft edge taper instead of hard clamp | .63/.44/.37 | 6.6/6.8 | 3.46/4.26/2.36 | c1 reads as fire now; gaps blotchy (isotropic fbm) |
| v05 | anisotropic gate (tongue-shaped, 4x15 px), gate warped by lateral eddies, faster gate evolution (tips), glow-peak flares (taller + faster + brighter) | .48/.37/.36 | 4.5/4.2 | 3.35/4.10/2.37 | licks rise, separate, re-form; some wavy "liquid" swirl at mid-height of c1; c0 still subtle |

v05 full render through prod camera (qc/v05_render_qc.json): plate outside masks max|Δ| 0, protected+face/hand polys 0,
engine output outside masks 0, output-space outside the camera-mapped mask support 0 px changed, glow zone series identical (corr 1.0, amp 14.77 both).
| v06 | swirl fix: displacement noise elongated vertically (sy 16), amp_y 4→3 (c1 2.8), softer gap edges (gw .18); tip-height puffing term (threshold modulated ∝h²) + tip brightness flicker | .48/.61/.36 | 4.2/4.1 | 3.22/3.81/2.35 | less "liquid" wobble, licks more vertical/tongue-like; tips still not flickering fast enough (tip 2–5 Hz own-share .19/.08) |
| v07 | tip terms doubled | .49/.61/.37 | 4.0/4.1 | 3.19/3.81/2.31 | barely changed → diagnosed: `Noise1D(hz)` is value noise whose energy sits far BELOW `hz` (3 "Hz" ⇒ mostly 0.2–0.7 Hz). All 1D drivers were mislabelled |
| v08 | **BandNoise**: FFT-bandpassed white noise, energy really in 0.3–0.6 Hz (breath) and 2–5 Hz (tip puffing / tip brightness); non-periodic over the shot | .46/.63/.37 | 4.1/3.8 | 3.34/4.02/2.41 | tips now flicker: own tip spectrum 2–5 Hz share .50/.52/.54 (v05: .12/.07/.05), centroid 2.3 Hz; no strobe (c1 mean 4.0 %, ≤5); chosen as final |

"Own" metrics (tools/own.py) divide out the v2c glow (POC/static ratio), so they show what the flame itself does, independent of the inherited pulse.
v08 own: tip cv c0 9.4 % / c1 6.8 % / c2 2.4 %; sharpness (Laplacian variance in mask, POC/static) 1.38 / 1.26 / 1.12 (no softening; slightly crisper because the gaps add contrast).
Loop check: HP-pattern correlation at lags 0.5–3 s max .10 / .05 / .08 (static plate .25/.28/.15 because it is literally the same image; references ≤.02).

---------------------------------------------------------------------------------------------------------------------------
# FINAL — v08 (tag `final_v08`), rendered 2026-10-23 ~22:06 EDT

## Deliverables (this folder)
| file | what |
|---|---|
| `P05_naturalfire_poc_final_v08.mp4` (+ `.md5`: 12c17a3d99f0f4d0c8c981904812e7da) | the POC: 1080x1920, 30 fps, 180 frames, 6.000 s, no audio, no captions; prod ENC_FINAL (x264 crf16 high) |
| `P05_naturalfire_vs_v2cstatic_sbs_final_v08.mp4` (+ `.md5`: a88a21d9a5fa1a2174dc41e9280a65d7) | 2160x1920 side-by-side, LEFT = POC, RIGHT = v2c static, same 6 s, same StablePush (z 1→1.04) |
| `strips/final_v08_flame4_0p25s_fullres.png` | 4 frames (f60/68/75/83, ≈0.25 s apart), native output pixels, forge crop out(400,740)-(690,1140) |
| `strips/final_v08_full_360x640.png` | whole frame at 360x640, f0/36/72/108/144/179 |
| `strips/final_v08_flame30_consec_1s_fullres.png` | adversarial: 30 consecutive frames (f90–119), native pixels |
| `strips/final_v08_flame12_consec_fullres.png`, `strips/final_v08_flame_0p5s_fullres.png` | 12 consecutive (f40–51) / every 0.5 s |
| `review/c1_f90_99.png`, `review/c0_f90_99.png` (3x), `review/c1_f100_119.png` (2x) | zoomed views of the 30-frame window used for the visual review |
| `work/final_v08_poc_lossless.mp4`, `work/final_v08_v2cstatic_lossless.mp4` | crf0 intermediates (static twin md5 = the v05 static twin: deterministic) |
| `qc/final_v08_render_qc.json`, `qc/final_v08_output_qc.json`, `qc/final_v08_decoded_edge_check.json`, `qc/final_v08_decoded_protected_check.json` | raw QC |

## QC table (final_v08)
| check | result | pass |
|---|---|---|
| plate: change outside flame masks (180 f) | max\|Δ\| 0.0 | ✅ |
| plate: change on P05_protect ∪ face/hand polys | max\|Δ\| 0.0 | ✅ |
| engine output (relit, pre-camera) outside flame masks | max\|Δ\| 0.0 | ✅ |
| output RGB (pre-encode) outside camera-mapped mask support (+4 px resample margin) | 0 px changed, all 180 f | ✅ |
| decoded lossless, camera-mapped protected set (≈2.05 M px/frame) | 0 px changed, max 0 | ✅ |
| decoded lossless, outside support | 116 px total over 180 f (42 f), max ±3/255, all ≤2.9 px from the support edge = yuv420p chroma subsampling bleed of the in-mask change, not motion; RGB before encode is 0 | ✅ (codec) |
| displacement on protected / outside mask | 0 px by construction (source ROI is flame-only, result hard-reset outside the union) and confirmed by the rows above | ✅ |
| glow vs v2c (engine glow-zone series, prod QC definition) | amp 14.7744 vs 14.7744, corr 1.000000, max diff 0.0 | ✅ exact |
| per-frame change in flame (output, mean / p95 / max) | c0 3.62 / 7.8 / 12.1 %, c1 4.24 / 8.0 / 11.5 %, c2 2.58 / 6.2 / 8.3 % (v2c static: 2.30/2.17/2.03 mean, 10.6/8.9/7.7 max) | ✅ mean <5 %; peaks are glow-peak flares |
| sharpness ratio (Laplacian var in mask, POC/static, output) | c0 1.34 (min 1.13), c1 1.20 (min 0.93), c2 1.10 (min 1.00) | ✅ no softening |
| loop / autocorrelation (HP pattern corr, lags 0.5–3 s, max) | .10 / .05 / .08 (static plate .25/.28/.15; refs ≤.03) | ✅ no loop |
| HF energy of the moving pattern (hp_energy, std/mean L) | .052 / .068 / .035 vs static .029 / .027 / .024 (refs .15–.24) | ⚠ alive but well below real video |
| iterate-vs-render determinism | flame mean series max diff 0.015 (uint8 rounding) → plate-space stats below apply to the delivered file | ✅ |

## Flow stats — POC vs references (DIS + HP-pattern; POC measured in plate space, identical to render)
| | DIS V/L | upward frac | global sway | rot/shear std | HP rise (heights/s) | own tip 2–5 Hz share | HP corr 0.5–3 s |
|---|---|---|---|---|---|---|---|
| bosnia fireplace (CC BY-SA 4.0) | 2.4–3.7 | .90–.995 | .23–.61 | .002–.006 | .34–.55 | .01–.09 (raw) | ≤.02 |
| claytor campfire (CC BY 2.0) | 1.2–1.4 | .62–.63 | .53–.59 | .022–.027 | .52–.83 | .16–.29 (raw) | ≤.03 |
| bastique candle-ish (PD) | 1.4 | .65 | .55 | .031 | .92 | .16 (raw) | ≤.02 |
| **POC c0 open flame** | 4.1 | .96 | .41 | .0025 | .46 | .50 | .10 |
| **POC c1 furnace mouth** | 3.8 | .97 | .26 | .0017 | .63 | .52 | .05 |
| **POC c2 embers** | 4.2 | .97 | .38 | .0009 | .37 | .54 | .08 |
POC tip/body "own" spectra are measured with the v2c glow divided out (tools/own.py); raw tip spectra (glow included) are dominated by the inherited 0.55 Hz pulse.
Reading: POC sits in the enclosed-fire (bosnia) regime — strongly vertical, no rotation, rise speed inside the bosnia band (c1 slightly faster, like claytor).

## Method (tools/flame.py, spec iter/specs/final_v08.json)
1. Per prod flame mask (c0 open flame 404,750 / c1 furnace mouth 459,855 / c2 embers 528,942 — unchanged prod masks), take ROI+6 px, TELEA-inpaint the non-flame pixels with flame paint so resampling can only ever move flame paint; 4x Lanczos up.
2. **Upward advection of the flame's own pixels**: 2-phase flow map (offset 0.5, triangle weights, per-pixel phase offset from fbm, phase speed ×(1+1.2·A)); travel D·h^1.2 (0 at base, max at tips; c0 28 px, c1 26, c2 9 plate px over T=.75 s cycles) + variance-preserving detail re-injection so the blend never softens.
3. Upward-advected fbm turbulence: dy ∝ h^1.3 (amp 3.0 / 2.8 / 1.5 px), lateral eddies dx (1.8 / 1.8 / 0.8 px), vertically elongated noise (sy 16) to avoid liquid swirl; soft 2.5 px edge taper.
4. **Licks that detach**: intermittency gate from anisotropic fbm (4–5 × 14–15 px tongues) rising at 45 px/s, evolving 2.6/s, laterally warped; threshold rises with height, falls with activity and is "puffed" by a 2–5 Hz band-limited driver ∝h² (tip height flicker). Gaps fade to the dim ember background (blurred paint × [.45,.25,.12]) → tips shed fading wisps.
5. Base/coals: brightness only (kb (1-h)² cell noise), no displacement.
6. Activity A = (v2c flicker of the matching glow layer − 1) + 0.5·0.25·breath(0.3–0.6 Hz band noise) + flare; flare = ((f−q80)/(fmax−q80))^1.5 of that same v2c flicker → flames get taller/faster/brighter exactly on the glow peaks (coupling) without touching the glow. Tip brightness flicker 2–5 Hz (k .06/.055/.04).
7. INTER_AREA down, delta form against Down(Up(src)), feathered mask blend, hard reset outside the union → animated plate.
8. Swap the animated plate into the **unchanged** locked engine `animate_b3_cb9e2b88.py` (prod v2c config, relight/spill/halo/pool and flicker untouched) and the prod camera (crop box → prepare_cover → StablePush SEG z 1→1.04, 180 f). All 1D drivers are band-limited noise / fbm — no sines added by me, nothing periodic within the shot.
Cost: 2.76 s/frame (both twins), deterministic.

## Honest flaw list
1. **Small at phone scale.** The animated flames are ~50–70 output px tall in a 1920 frame; at 360x640 the difference vs static is subtle — mostly reads as "the furnace mouth is alive". c1 is the convincing one; c0 is narrow (3–15 px) and its motion is modest; c2 embers only shimmer.
2. **Painted fire outside the prod masks stays still** (the tall flame column above c0 / between the blocks, the upper furnace). I did not touch or widen prod masks, so those painted flames cannot move; at full res this is the biggest giveaway.
3. **Tips are clipped by the mask top**: licks cannot rise above the mask, they fade at its edge rather than escape upward.
4. **Moving-pattern energy is ~3–4x below real fire video** (hp_energy .035–.068 vs .15–.24) — deliberate restraint for "no strobe"/per-frame <5 %; a real fire has more violent change.
5. **The glow pulse is inherited from v2c**, which is a sum of sines (0.55 Hz-dominant); because brightness is coupled to it, the overall breathing has that v2c regularity. Flame shape itself is non-periodic (corr .05–.10).
6. Peak per-frame change at glow-peak flares reaches 11–12 % (static v2c itself peaks 9–11 %); mean is within budget.
7. Slight crispening (sharpness ratio 1.1–1.34) from the dark gaps between tongues; no halos seen, but it is not "identical texture".
8. Faint "liquid" waviness can still be spotted mid-height in c1 when stepping frames at 3x; not visible in playback at 1x in my review. I judged this not a real defect worth another iteration.
9. A greyish-green tint at c1 left exists in the v2c static too (glow tint), not introduced here.
10. No sparks/embers/shimmer added (optional in brief): inside-mask-only sparks would be tiny and risk looking pasted on; omitted by choice.
11. Engine: the brief said b9; prod v2c asserts and bit-reproduces with b3 `cb9e2b88` — used that. Reference forge_etueffont (CC BY 4.0) excluded (little visible fire).
12. Decoded files have ≤±3/255 chroma bleed within 3 px of the flame support (yuv420p); unavoidable with prod's pixel format.

---------------------------------------------------------------------------------------------------------------
## v09 (2026-10-23) — phone-legibility iteration (flaws 1–4 of v08). v08 files untouched.

R&D masks: masks_v09/ (cores cover all painted fire; feathered extension zones above each flame, ~15–30% Hf, only over
dark/background, excluding faces/hands/gold/figures via masks_v09/P05_rnd_protect.png). Prod masks/configs read-only; the glow
still uses prod masks (v2c exact). Measurement tool: tools/iterate_v09.py (crop of forge, per-flame core/prod/ext stats).
Metrics below: core dF mean (%), hpE (temporal high-pass energy), static twin dF ~2.4 / hpE ~.03.

| tag | change | c0/c1/c2 dF | c0/c1/c2 hpE | verdict |
|---|---|---|---|---|
| v09a | v08 params on v09 masks (baseline) | 3.79/4.93/2.60 | .056/.077/.035 | ext zone barely lit (0.2%) — advection too short above h=1 |
| v09b | tongue-stretch model (flame_v09t.FlameT): top band stretched up by travelling lick noise, LIGHTEN blend | 4.04/5.83/2.93 | .061/.095/.042 | tongues now exist (5–13% lit); features too small to read at 360x640 |
| v09c | ~2x larger gate/displacement features | 3.88/5.61/2.82 | .059/.094/.040 | better phone read, energy flat |
| v09d | deeper gate, bigger amp_y, ext_gain 1.8 | 3.99/5.80/3.11 | .060/.099/.047 | c0 still steady at base |
| v09e | + rising luminance cells (kcell .16) | 4.30/5.99/3.18 | .065/.101/.048 | visible rising brightness cells, good |
| v09f | kcell .26/.24/.18, c2 stronger | 4.77/6.21/3.58 | .073/.104/.056 | pale patches at c0 base (suspected clip) |
| v09g | channel-weighted cells + soft knee on increase only | 4.83/6.03/3.54 | .074/.101/.056 | energy ~1.3–1.6x v09a; BUT zoom diag showed a flat-topped bar tongue beside the pillar (pinkish, per-channel lighten) and straight-edged dark gaps along protect-polygon lines in c1 |
| v09h, v09i | stronger variants of g | — | — | killed before finishing (built on the flawed tongue code); empty dirs left, no data |
| v09j | fixes: tongue reach = 0.22·Hf (was ext row span), peaked lick (pointed tongues), luma-weighted blend (no pink), gate/cell/tongue fade within 7 px of protected edges | 4.36/5.69/3.50 | .064/.095/.055 | straight guard edges gone; pink gone; thin orange sliver tongue remains in pillar gap; c1 gaps slightly vertical-bar-like |
| v09k | j + drop ext slivers < 9 px wide, ext_reach 1.0, c1 gsy 18 / D 34 | 4.36/5.85/3.50 | .064/.097/.055 | c1 V/L 8.4→10.4 (less watery wobble), rise .51; ext tongues rarer (lit 0.3–0.9%, wisps 4–10% of frames); c1 sharp min .69; remaining narrow tongue beside pillar is core paint. **Picked → final_v09** |

v09 pick (iteration stage): v09k (spec copied to iter/specs/final_v09.json). vs v09a (= v08 params): core hpE 1.15x/1.26x/1.56x, dF +0.6/+0.9/+0.9 pts;
c0 sway .57 (v09a on same masks .53; bosnia .23–.61). Render + QC pending.

Process note (honest): during v09g a first knee version also compressed static paint; I killed that run and deleted the
just-created partial iter/v09g dir before re-running v09g (the only deletion in this R&D folder; it held my own partial output).

final_v09 render: done 23:35 (UTC-4). plate_protected(R&D)/face-hand/outside-union maxabs 0; glow corr 1.0, max_abs_diff 0.0; prod_protect_px_touched_any_frame 2559 (prod-protect px that the expanded R&D cores cover — expected from requested mask expansion; none are face/hand). Finalize pending.
finalize_v09 done 23:51 (UTC-4): poc md5 aafa62ba950355b159aaa84bf7e6a0d6, sbs md5 9c23bd75bd9c3d955ddb50d22760224a. Checks pending.
Checks (final_v09, decoded lossless POC vs decoded lossless v2c static twin):
- edge: 3 px total changed outside flame support (2 frames, max 2/255, ≤0.95 px from support) [v08: 116 px] → qc/final_v09_decoded_edge_check.json
- protected, R&D protect | face/hand, unmargined: 118,863 px·frames (~660 px/frame), max 23/255 — camera-resample ring where R&D protect directly abuts the expanded cores (plate-space protected maxabs is 0); eroded 2 plate px: 10,844 px·frames, max 4/255; face/hand polys only: 12 px·frames, max 2/255 [v08 prod-protect check: 0]. Not a displacement leak; it is resample bleed across a mask edge with no margin.
- protcheck_v09.py first run crashed (my edit put `cand=` into a comment); fixed and re-run; added protcheck_v09b.py (erode / face-hand-only variants).
- like-for-like vs v08 (decoded finals): qc/final_v09_vs_v08_like_for_like.json

### v09 final — QC table (decoded finals, like-for-like; phone_dL = mean |ΔL| over 1/3 s at 1/3 scale; "excess" = minus the static twin, which carries the v2c glow pulse)
| region | dF mean v08 → v09 (static) | phone_dL excess v08 → v09 | hp_energy excess v08 → v09 | HP corr (loop) v09 |
|---|---|---|---|---|
| c0 core (v09 mask) | 3.27 → 4.46 (2.48) | 1.50 → 3.62 (2.4x) | .015 → .032 (2.1x) | .054 |
| c1 core | 3.78 → 6.11 (2.47) | 2.00 → 4.48 (2.2x) | .028 → .066 (2.4x) | .056 |
| c2 core | 2.61 → 3.69 (2.11) | 1.10 → 3.25 (3.0x) | .008 → .028 (3.5x) | .067 |
| c0/c1/c2 prod mask | 3.62/4.31/2.63 → 4.22/4.99/3.78 | 3.07/3.93/1.32 → 5.45/5.39/3.71 | | .075/.069/.066 |
| c0/c1/c2 extension | 1.90/3.14/2.79 → 2.04/3.30/2.85 (static 1.91/3.17/2.83) | ≈0 → +0.4/+0.2/+0.1 | | |
dF max (core) 11.2/13.5/9.6 — inside real-fire refs (claytor max 16–19, bosnia 17.8–20.5). c1 mean 6.1% ≈ the ~6% ceiling.
Sharpness ratio (vs static) mean/min: c0 1.06/.86, c1 .95/.68, c2 1.09/.95. Glow: engine corr 1.0, max_abs_diff 0.0 (exact v2c). Outside union/protected (plate) 0. 180 f, 1080x1920, 30 fps, 6.0 s, no audio.

### v09 flow stats (plate space, iter v09k = final spec)
| | DIS V/L | upward frac | global sway | rotation/shear std | rise (heights/s, DIS) | HP corr |
|---|---|---|---|---|---|---|
| c0 | 6.06 | .988 | .57 (v09a same masks .53; bosnia .23–.61) | .0007 | .09 | .07 |
| c1 | 4.26 (crop stat V/L 10.4) | .979 | .22 | .0016 | .30 | .06 |
| c2 | 4.61 | .982 | .33 | .0013 | .20 | .06 |
Still bosnia (enclosed fire) regime: strongly vertical, no rotation (no swivel).

### v09 adversarial review (30 consecutive frames, 0.25 s strip, v08-vs-v09 phone strip, zoom diags)
Better than v08: mouth (c1) and column (c0) flames visibly change shape within 0.25 s at full res and read at 360x640; painted fire outside the
prod masks (column behind pillar, lower-right beside block) now moves; no strobing (smooth consecutive frames), no swivel, no loop.
Flaws (honest):
1. Extension/tongue zones barely contribute (ext dF ≈ static, phone_dL +0.1–0.4): flaw 3 (tips clipped at mask top) is only weakly fixed. Stronger tongues (v09g) produced pasted-looking flat bars / pink tint, so I traded reach for cleanliness.
2. c1 dark gate gaps sometimes form vertical "picket" columns when stepping frames at 3x; reads as flame gaps in playback, but it is the most synthetic-looking element.
3. c1 sharpness min .68 (v08 ~.75): some frames soften the mouth slightly.
4. Protected-set output ring: R&D protect abuts the expanded cores with no margin, so camera resampling bleeds up to 23/255 in a ~1 px ring (≤4/255 after 2 px erosion; face/hand ≤2/255, 12 px total). v08 was 0. Plate-space displacement on protected px is 0.
5. 2559 prod-protect px are inside the requested expanded R&D cores and animate (none face/hand) — consequence of item 1 of the brief.
6. Thin narrow tongue beside the pillar (c0 core paint) flickers; small at phone scale.
7. c1 mean dF 6.1% sits at the upper limit.

### Pick: v09 (P05_naturalfire_poc_final_v09.mp4)
Reason: 2.2–3x v08's visible (phone-scale) motion above the static glow on every flame, moving fire now covers all painted fire, inside real-fire
dF levels, no swivel/loop/strobe and no pasted-on look in review. v08 remains the safer fallback if the owner finds the c1 "picket" gaps or the
slight softening objectionable. v08 files untouched.
Deliverables: P05_naturalfire_poc_final_v09.mp4 (md5 aafa62ba950355b159aaa84bf7e6a0d6), P05_naturalfire_vs_v2cstatic_sbs_final_v09.mp4
(md5 9c23bd75bd9c3d955ddb50d22760224a), strips/final_v09_*.png, masks_v09/P05_fire_v09_mask_overlay.png, qc/final_v09_*.json.

===============================================================================================================
## v10 (2026-10-24 00:05 UTC-4) — NEW APPROACH after v09 failed independent review (2/10: "2D warp/wobble filter", smear, edge pull)
v09 is NOT to be used or sent. v09 files kept (no deletion) but superseded.
Plan: painted flames = static base (exact v2c static frames, untouched); motion = NEW additive layer only:
procedural rising flame field (noise advected strictly upward, threshold rising with height -> tongues detach, thin, vanish above
painted tips; colour ramp sampled from the plate's flame paint), screen-composited with caps, plus a few rising embers.
Composited in OUTPUT space on the decoded v2c static planes (yuv420p), under a hard holdout (camera-mapped protect, 2x2-chroma-block
aligned) -> protected px and every px the layer does not touch are bit-identical to v2c static. Final encoded lossless yuv420p
so the decoded final can be proven exact. Work dir: v10/.

### v10 log (Oct 24, UTC-4)
- Mapping check: plate->output via prod camera matches measured impulse centroids to ~0.1 px (frames 0 and 179).
- tools/fire_v10.py: decoded v2c static yuv420p planes = base; procedural layer evaluated per output px via inverse camera (full-res, no resample of paint);
  screen composite in RGB (BT.601 limited) only where layer>0 and outside holdout; Y/U/V copied verbatim elsewhere (chroma per 2x2 block).
- v10a (v09 core/ext envelopes + v09 R&D protect): layer squeezed to a 5 px sliver at c0 (R&D protect had a 5 px margin + coarse boxes). Dropped.
- New masks (tools/masks_v10.py -> v10/masks/): named_protect = v09 guard boxes (no margin) + prod face/hand polys + new rim/lintel/jamb/sill polys;
  allowed = 4 explicit zones (z0low beside pillar, z0top above pillar top over smoke, z1 central forge mouth y>=798, z2 lower mouth) minus protect.
  Holdout = camera-mapped NOT-allowed, any influence (>0), +1 px, 2x2 block aligned -> only allowed-zone px can change.
  _b variant: right-smith head box trimmed to x>=462 (head/hair start ~x477) so the fire above the pillar top can carry tongues. QC reports both.
- v10b: blobby flat pale patches (cut-out look). v10c: thin needle "comb" (sx too small). Kymographs confirm strictly upward streaks, no reversal.
- v10d: broad tongues (sx=0.2 zone width, sy=1.9 sx, soft .4, conv .35, cooler colour with height) -> flame-like layer shapes.
- v10e/f: z0top over smoke; ramp from fire-classified plate px (z0top borrows z0low ramp; smoke-lit ramp looked grey). Tongues lick up from
  behind pillar top and detach as wisps. dF on active px 14.4 (static 5.9) ~ real-fire ref range 11.6-16.5.
- v10g (full 180, Hf z0top 90, soft .32): kymograph shows streaks with VERTICAL leading edges = tongues popping in over their whole height
  (evolution axis ev .9 doing the work, not advection) -> "flicker", not "rise". v10h ev .25: parallelogram streaks, both edges slanted = advected.
- v10i: screen over smoke/bright paint whitened tongues (cream). Added "occl": flame body pulls non-dominant channels toward the flame hue
  at the composite's own peak level (emissive body hides what is behind it). ev .4 compromise.
- v10j: colour index on a 3x wider soft ramp (csoft 3, cgamma 1.2): hot yellow only deep in a tongue, orange edges, deeper tips. Reads as fire at 2x and at 360x640.
- FINAL = v10j params (v10/specs/final_v10.json), 180 frames, lossless 4:2:0 master.

## final_v10 (Oct 24 2026, UTC-4)
Files: P05_naturalfire_poc_final_v10.mp4 (lossless qp0 yuv420p master, High 4:4:4 Predictive, md5 82eb42c0593251bc29eb67af64f46a61)
       P05_naturalfire_poc_final_v10_crf16.mp4 (phone/share encode, prod ENC_FINAL, md5 e4e83f19904541ea15b9723b6878452c)
       P05_naturalfire_vs_v2cstatic_sbs_final_v10.mp4 (header labels LEFT = v10, RIGHT = v2c static; crf16; md5 495badbf9565c4032cc4f8e8dfdbe144)
       v10/strips/final_v10_{flame4_0p25s_fullres, flame12_consec_fullres, flame12_consec_diffx3, phone4_0p25s_360x640, phone12_consec_360x640_forgezoom3x}.png
       v10/qc/final_v10_qc.json, v10/work/final_v10_layer_qc.json, kymographs in v10/qc/.
QC (decoded master vs decoded v2c static, all 180 frames, any Y/U/V difference):
  named protect (_b: rims/lintel/jambs/sill/tools/hands/faces/stone/gold/figures) = 0 px; everything outside the 4 allowed fire zones = 0 px.
  Original untrimmed prod right-smith head box: 182,470 px-frames changed, all inside the trimmed strip plate x424-461 y578-609 (smoke/fire above
  the pillar; the head starts ~x477) - verified the _b vs original protect difference is exactly that strip.
  Glow: untouched px are bit-identical (max |dY| 0) -> v2c glow reproduced exactly; >=99.63% of each frame identical; ~5.7k px/frame changed.
  dF (active px, max-channel) v10 13.2 vs static 4.7 (real-fire ref 11.6-16.5).
  crf16 copy: residual in protect vs a crf16 static encode max 27, mean 3.1 (codec decisions, not the layer) -> only the lossless master carries the 0 proof.
Method: painted fire untouched (static base, brightness only via v2c glow). New material = procedural flame density per zone, evaluated per output px
  through the inverse camera, noise advected strictly upward in a height-stretched coordinate (accelerates, elongates), threshold rising with height
  (tongues taper, detach, burn off above painted tips), lateral convergence, slow non-periodic evolution; colours from the plate's own fire-pixel ramp;
  gain follows the static glow; screen + hue-saturation composite with caps; deterministic embers (monotone rise, drift, flicker, fade).
  Output-space holdout = camera-mapped NOT-allowed (any influence, +1 px, 2x2 chroma-block aligned); Y/U/V copied verbatim there. No heat shimmer (dropped: any
  displacement risks edge pull). No blur, no warp of paint.
Honest flaws:
  - Visible fire area is small (4 zones, ~5.7k output px); on a phone the change reads mainly above the left pillar top and in the lower forge mouth.
  - z1 (central forge) is already near-white in the paint: the layer mostly adds yellow there (diff shows green/yellow), motion there is subtle.
  - Tongues are procedural noise shapes; at 2x some read slightly soft/blobby rather than crisp painted licks; the 2.5-5 px holdout feather can dim a tongue at zone edges.
  - Holdout relies on the _b mask (head box trimmed to x>=462); against the original prod box the change is non-zero (reported above).
  - Lossless master is High 4:4:4 Predictive profile: not playable in some browsers/phones; the crf16 copy plays everywhere but is not bit-exact in protect.
  - Evolution ev .4: small in-place morph remains on top of advection (kymograph of the final params not run at 180 f; ev .25 iter shown).
  - UPDATE: kymograph from the DECODED final now in v10/qc/final_v10_kymo_decoded.png (x488/x605/x520): streaks lean up-right only (rising), no
    reversal; x605 also shows a steady horizontal band near the base (constant hue-saturation of the coal bed) = static-looking component there.

## v11 (2026-10-24) — response to 4/10 review: crisp stroke-textured tongues, over-compositing, burst dynamics, sharp sparks
Engine: tools/fire_v11.py (new; v10 untouched). Holdout construction identical to v10 (verbatim Y/U/V copy in hold, asserted).
Iterations (24-frame iter dirs under v11/iter/, specs under v11/specs/):
- v11a: first run. Crisp, jagged edges and red-orange grade work, but tongues are thin, dark-red "worms" (T too low); layer about 1.3k px/frame.
- v11b: widths ×2, rate up, taper 0.45, T = core^0.6 profile, o_thin 0.4. z0top reads as real flame, but has dark rims (outline/sticker look) and torn-paper edges in z2.
- v11c: T floor 0.28 (thin parts deep red-orange, never brown), rim opacity ramp, vertical heat profile (deeper at the root and tips, hottest low-middle), jag grows with height (smooth body, ragged tips), kt 0.25. z0top good; z1/z2 become yellow, waxy blobs.
- v11d: core^1.2 (small hot core), detached bottoms pointed rather than bulbs, w ≥ 0.2·L so long licks keep a body.
- v11e: over-composite in LINEAR light (premultiplied); kills the muddy ochre of red-over-yellow sRGB mixes. Found NaN green dots from negative rgb^2.2 → fixed by clipping (v11f).
- v11f: per-zone grade for bright paint (z0low/z1 heat 0.75–0.8 so bodies are orange against yellow-white; z2 heat 1.2); o_thin/rim0 0.75–0.8.
- v11g: z1/z2/z0low narrower, pointier tongues (taper 0.75), more of them (rate 6/14/12). This removes the tulip/dome shapes.
- v11h: newborn tongues start as narrow points and widen as they grow (hw ∝ min(1, L/2.5w)^0.7). No more onion domes.
- v11i: jag0 0.25 and kt 0.35 in the bright zones. Full 180-frame iteration: 278 tongues, 82 sparks, about 21 alive per frame, layer about 2.4k px/frame.
  The kymograph shows rising streaks with varied slopes (fast snaps and lazy ones), upward only, plus burst clusters at the glow peaks.
  At phone scale, z0top tongues read clearly; the forge zones are subtler.
→ final_v11 = v11i spec.

### final_v11 (delivered 2026-10-24, spec v11/specs/final_v11.json = v11i)
Files (md5):
- P05_naturalfire_poc_final_v11.mp4 (lossless qp0 yuv420p, High 4:4:4 Predictive): e00aab9c79f1a6add3edcf7d82eb62ae
- P05_naturalfire_poc_final_v11_crf16.mp4: 73ea34dfd4b14dd9725c14ac46b62d54
- P05_naturalfire_vs_v2cstatic_sbs_final_v11.mp4 (header: LEFT = v11 / RIGHT = v2c static): f9e691638adc65160a2c959a7bed0818

Decoded master is bit-identical to the v11i iteration frames.
Strips are in v11/strips/final_v11_*. QC is v11/qc/final_v11_qc.json; the kymograph is v11/qc/final_v11_kymo_decoded.png.

QC on decoded files:
- named_protect_b: 0 changed px (sum and max). Outside allowed zones: 0.
- Original prod boxes: 92,115 px-frames, all in the trimmed strip x424–461 (smoke above the pillar).
- Untouched px are bit-identical, so the glow is identical to v2c. About 2.8k changed px per frame.
- dF: 26.6 vs 4.8 for static.
- crf16 residual in protect (vs crf16 static): max 32, mean 3.1. This is codec noise only.

Method:
- Additive tongue sprites over the static v2c plate, composited OVER in linear light (premultiplied).
- Crisp 0.8-px alpha edge; jag noise grows toward the tip; forks.
- Internal texture comes from the plate's own painted flame strokes. A high-pass stroke patch is sampled from fire-classified paint near each zone and rides with the tongue.
- Grade: deep red/orange at the root and thin parts, orange body, small yellow-white core (core^1.2).
- Per-tongue speed varies, with snap bursts and lazy drift (fast 30%, lazy 70%). Each tongue detaches and pinches off.
- Spawn rate ∝ glow², plus flare licks at the glow peaks (f22–24, 73–74, 124–125).
- Sparks are hard AA streaks (1/60 s shutter, 4× supersampled) in erratic bursts, with random lateral kicks. They die when they leave the zone.

Honest flaws:
- In the forge mouth (z1/z2, bright yellow paint) the tongues are subtler at phone scale than at the pillar top. Some z2 licks still look smooth/"horn"-like rather than wispy.
- The stroke texture is visible at 2× but mostly lost at phone scale.
- Sparks are sparse (82 in 6 s).
- Attached roots sit still while a slow tongue rises (horizontal kymograph bands at the forge base, f0–45). This is physically plausible, but noticeable in the diff.
- z0low (narrow slot) contributes little.

## v12 iteration log (2026-10-24)
Engine is tools/fire_v12.py (v11 + lobed tongues, painterly breakup, per-zone poster, merged forge mass, height cap, optional layer_step). Specs are in v12/specs/.
- v12a: dry-brush/stroke breakup far too strong (confetti in forge, dotted pillar outlines); 2.6k px/f.
- v12b: gentler breakup (dry_band .08, kst .08, dry_thr), forge jag_k .45; better, but small chips at the forge base and a dotted rim on the pillar.
- v12c: jag scaled by growth, dry gate on a blurred stroke texture (sigma 1.2), forge rate/width up; z2 now broad multi-lobed licks; 3.8k.
- v12d/e: jittered root fade (base_jit 7px), z1 dry .04 and no dark rim. Pillar dotted rim was caused by POSTERIZATION, so z0top poster is now 0. hold_feather 7.
- v12f/g: layer_step 2 test. dF alternates 0 / ~38 (max 37.9 vs 31.5 at step 1), which reads as judder against the 30 fps sparks and camera. REJECTED; stays at step 1.
- v12h/i: full 180 frames; pillar f83 capped (Hcap 80, Lmax 55). Dense forge showed a tangle of internal outlines where tongues overlap.
- v12j: forge zones use `merge` (max-union of heat/opacity, composited once), so there are no internal outlines and it reads as one fire mass with a lumpy silhouette.
- v12k-m: forge rate/width up, z1 heat .5 / gain 1.2 / o_thin 1.0 (deeper orange-red over yellow). v12m (f0 0, 180 frames) is the final candidate.
  Coverage (Y-changed px/frame by region): v12m z1+z2 = 3639 vs v10 3024 vs v11 1284. Total is 4717 vs v10 5216; the pillar was deliberately capped (1434 vs v10 2545).
- v12n: forge T capped at 0.72 (t_max; licks stay deep orange/red, no flat white cut-outs from merged cores); pillar Hcap 66 / Lmax 46 (was 80/55).
- A first final render from the v12m spec was superseded before handoff. It was moved, not deleted, to v12/iter/superseded_final_v12m/ (P05 files, md5s, strips, qc, residual ref, spec).

## final_v12 (spec v12/specs/final_v12.json = v12n with f0 0, layer_step 1)
Files:
- P05_naturalfire_poc_final_v12.mp4: lossless master, High 4:4:4 Predictive, yuv420p, 180 frames. md5 74d04b7fd7523488dca3cfc7af049ca1 (same as v12/work/final_v12_lossless420.mp4)
- P05_naturalfire_poc_final_v12_crf16.mp4: md5 63932e9e93e371c3afcba5b299396474
- P05_naturalfire_vs_v2cstatic_sbs_final_v12.mp4: md5 23bc2e42129d0c4dff40d16e78515a22
- .md5 sidecars; strips in v12/strips/final_v12_*; QC in v12/qc/final_v12_qc.json; kymograph in v12/qc/final_v12_kymo_decoded.png
QC:
- Trimmed head box (_b): 0 changed px. Outside allowed: 0.
- Original prod boxes: 113,310 px-frames changed (max 1262/frame), all in the trimmed strip x424-461 y578-609 (smoke/fire above the pillar). This follows because _b = 0 and original minus _b is that strip.
- Glow: untouched px max |dY| = 0 vs v2c static; identical-px fraction min 0.9959.
- dF in the active region: 22.1 vs static 5.4. crf16 residual in protect_b: max 31, mean 3.14.
- Coverage (Y-changed px/frame): forge mouth z1+z2 3639 (v10 3024, v11 1284), pillar 1218 (capped), total about 4.5k (v10 5.2k, v11 2.3k).
Method: v11 dynamics unchanged (spawn, rise, detach, sparks, linear-light over, hard holdout, zero-displacement base). Added:
- lobed tongues (1-3 lobes, per-lobe width variation, low-frequency lump edge);
- forge zones composited as one merged mass (max-union of heat and opacity), so there are no internal outlines;
- light painterly breakup: stroke-direction texture from the plate (structure-tensor oriented smear), with a blurred dry-brush gate only in the outer ~8% of the width;
- forge only: 5-band soft posterized tone;
- forge T cap 0.72 (deep orange/red over the yellow paint);
- root-line jitter;
- pillar height cap with tip fade.
Layer stepping (2s) was tested and rejected as judder.
Flaws (honest):
- Forge licks are flatter, cut-paper painted shapes. They read as painted, but at full res some white-hot paint between dark-orange licks reads as cream cut-outs (f68, f75).
- The z1 (upper forge window) mass is sometimes muted peach-orange over the hottest yellow, so contrast is lower there than in z2.
- Total coverage is below v10 because the pillar is capped. Forge-mouth coverage exceeds v10.
- Pillar tongues are still thin forked horns ("crown" at f80-84), but shorter. Pillar texture is unchanged from v11 apart from the cap: posterize/dry-brush were removed there because they produced dotted outlines.
- The base band at the z2 root persists (horizontal kymograph band at x606).
- The tongue layer is still a synthetic overlay on a frozen painting. The painterly breakup is subtle by design (strong settings shredded the shapes).

---
## v13 — FINAL pass (2026-10-24, America/Toronto)
Goal: fix v12's cream cut-outs in the forge mouth (f68–75), keep v12 pillar cap but break up the f80–84 crown. Everything else (holdout, 0 base displacement, glow = v2c, sparks) unchanged. v11/v12 files untouched.

### Diagnosis of v12 defect
The "cream cut-outs" were the static paint itself (~253,254,156) left visible between v12's darker, lobed, opaque orange licks over the white-hot part of the window -> paper-cut silhouettes. Not a compositing bug.

### New code (tools/fire_v13.py, from fire_v12.py)
- Paint-brightness map BR = blur(ss(140,200,plate lum)). Per tongue, footprint BR mean vs zone `hot_thr` picks style: "hot" (v11 tongue params, zone `hot` dict) or "dark" (v12 lobed / variable width). (Plate is darker than output; 195/235 thresholds gave ~0 -> 140/200.)
- v12 merged mass composited UNDER single tongues.
- `gap_tint`: soft amber wash on the tongue layer only, = k * prox(blurred lick alpha within forge zones) * cream(base lum high & low warmth) * (1-A). Cream mask blurred (`cream_sigma`) because the paint has blocky ~8px texture -> without it the tint showed square patches (v13o).
- `b_mul` per-zone: lowers blue of tongue colour so hot-style cores stay saturated amber, not pale cream next to the saturated yellow paint.
- Pillar: `L_from_cap` (lengths drawn as fraction of v12 cap, separate fast/slow ranges), `desync` (a tall tongue born within ds s of another is shortened x0.35–0.6), `flare_nmax`/`flare_spread` (flare spawns offset in time) -> no simultaneous symmetric fork.
- `t_lift` (luminance-matched licks) implemented but REJECTED: produced pale ghost licks (v13c).

### Iterations (30-frame windows f60–89 unless noted; v13/iter/*)
- a: first split, z1/z2 hot_thr .4, dry_band .04 -> dark-style fragments over z1 still shredded.
- b: hot_thr .2, dry_band 0, kst .04, tint k .75 col 255,180,55. Better; tint barely visible.
- c: t_lift .8 -> pale ghost licks. Rejected.
- d: z1 all hot-style (hot_thr -1), z2 all dark/lobed. Cut-outs gone; z2 lobed licks over dark coal read well.
- e: d without tint (A/B). f: hold_feather 1 -> no difference (keep 7).
- g: pillar rate 17, Lf ranges up -> single smooth cones. h: pillar rate 20, w 10–20, wvar .35, lump .15, taper .55 -> varied asymmetric licks, no crown.
- i: z1 hot keep .5, grow_k .4 -> z1 presence back to v11 level (z1 Y-changed 1086 px/f vs v11 512; v13h only 403).
- j: i without tint (A/B). k: z1 heat .55 -> no visible change. m: z1 hot t_max .82 -> small change.
- n: + b_mul .45 (saturated cores), tint w_hi .8.
- o: tint k 1.0, p_full .12, col 255,170,45, sigma 7 -> square patches (blocky paint) -> fixed in
- p: cream_sigma 4, stex 0 -> soft continuous amber, no patches. CHOSEN -> final_v13.json (f0 0).
Note: perceived "pale/lavender" fringes in zooms were simultaneous contrast (no pixel paler than static: checked sat/lum vs static at f68/f75).

### final_v13 (first final, from v13p) — SUPERSEDED, kept for the record
Rendered + finalized (P05_naturalfire_poc_final_v13*.mp4, md5 master c5c86587…, crf16 2b4056cc…, sbs e600dce8…). QC passed (named_b 0, outside 0, glow 0), BUT self-review found the pillar nearly dormant: z0 Y-changed 342 px/f over 180 f vs v11 1083 / v12 1218; at 360x640 the pillar fire basically disappears. Regression vs v11 -> not the deliverable.
Root cause: `L_from_cap` drew L as a fraction of Lmax; L is also the detach length (idet), so tongues pinched off early and short. v12 drew L from Hf (60–94) and let the Hcap ceiling end them.

### Pillar re-tune (30-frame windows)
- q: w 14–28, rate 26, Lf up -> still tiny (z0 531). r: rate 30, desync_k param -> 586. s: Lf relative >1 -> 624, still tiny.
- t (A/B): v12 pillar spec inside v13 code -> pillar alive again (z0 1335) and already less crown-like (different draws).
- u: v12 pillar + desync .3 -> desync kills most tall licks. v: desync .12 -> still empty at f74–84.
- w: v12 pillar + flare_spread [0,.25] (no desync) -> z0 1333, varied; residual V/fork shapes (p_fork defaulted to 0.6).
- x: + p_fork .2 -> varied heights/timing, asymmetric, no crown/simultaneous fork at f74–84. CHOSEN -> final_v13x.json.

### final_v13x — DELIVERABLE
Spec v13/specs/final_v13x.json (v13p forge + v12 pillar params + flare_spread [0,.25] + p_fork .2; f0 0). Render tools/fire_v13.py, finalize tools/finalize_v13x.py.
- Master P05_naturalfire_poc_final_v13x.mp4 md5 0dbcbb51eabd888d6c2d59f47f341a7e (= v13/work/final_v13x_lossless420.mp4)
- crf16 P05_naturalfire_poc_final_v13x_crf16.mp4 md5 4e67bc32dce272226ff6f919ebed0b22
- SBS P05_naturalfire_vs_v2cstatic_sbs_final_v13x.mp4 md5 08891e40877a243ebb0bb9a160229c79
- QC v13/qc/final_v13x_qc.json: named_b changed px 0 (all 180 f, decoded); outside allowed 0; original prod boxes 107242 px total, only possible in plate strip x424–461 y578–609 (named_orig minus named_b, verified) — v11 92115, v12 113310; glow max |dY| untouched px 0.
- Coverage 180 f (Y-changed px/f): z0 1092 / z1 1299 / z2 2182 (v11 1083/375/909, v12 1218/1574/2065).
- Strips v13/strips/final_v13x_* incl. vs_v11_forgezoom_f68_f75_f83, vs_v11_forgemouth_tight_f68_f75_f83, vs_v11_v12_pillar_f80_f84.

### Flaws (honest)
1. Pillar: crown gone, but at f80–84 it is a short cluster of 3–4 near-parallel strands of similar height — calmer and much less dramatic than v11's tall leaping licks; at 360x640 it reads as "glow + small fire", weaker than v11.
2. z1 (forge window) tongues are essentially v11 tongues — no real improvement there; soft amber tint near their bases can read as a faint lighter haze at 2.8x zoom (simultaneous contrast; no pixel is paler than static).
3. z2 lobed licks are the real gain (flame-like, fuller), but at times busy/dense vs v11.
4. Gap tint is subtle; invisible at phone size.
5. Original-prod-box strip changes (x424–461) slightly higher than v11 (still outside trimmed head box; named_b 0).

### Verdict: v13x is NOT clearly better than v11.
Better: z2 coal fire, no cream cut-outs, no crown. Worse/equal: pillar less dramatic, z1 same. Net: a sidegrade; v11 remains the safest pick unless the owner prefers the fuller lower-right fire.
