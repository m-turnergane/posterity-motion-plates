# flames — NOTES (state at pause)

PAUSED 2026-10-30 11:54 EDT: Jianwen plate landed (standalones/jianwen/plates-v1/k01_night_burial_as_emperor.png).
Progress: nothing built yet — package dir created, no code/renders. smoke_v1/v2 untouched (locked).

Planned design (resume here):
- Emissive model: plate = bg + E, bg = soft-fill of surroundings over the dilated flame matte; E = plate - bg.
  Untouched pixels are exactly plate (E unchanged outside the flame zone) -> zero-motion by construction.
- Flame matte: hot hue + high value (V>~0.9, R-B large) + yellow-white core, limited to hand `regions`,
  plus `add`/`protect` polygons; per-component processing (size-scaled noise, own flicker clock & seed).
- Motion = VERTICAL-ONLY displacement D = L*(B-b0), B = rising anisotropic noise (two textures, different
  speeds) -> upward-flowing internal turbulence, licking tongues at the tips that detach and shrink; no dx => no
  sway/squiggle. Tongue extension faded by height above the matte (fringe zone).
- Flicker: slow smooth clock (<5 Hz, amp ~0.1), channel exponents (R1, G1.4, B2) => brighter=whiter, dimmer=redder,
  stronger at tips than core. Light spill = multiplicative ring (declared spill zone, minus protect) synced to the
  same clock. Sparks: deterministic particles born in the top band, rising with decel + gentle drift, confined to a
  declared spark zone. Pre-roll (t + preroll) for everything.
- Proof: diff vs plate; 0 outside (flame+fringe ∪ spark ∪ spill); 0 outside flame+fringe with sparks/spill off; 0 in protect/guards.
- PoC targets: b13 (three torches) + p05 v2 (burning town) 6-8 s clips, grabs for b10 cresset; then STOP.
Disk at pause: 62 GB free.
