# flames_v1 progress log (2026-10-30). NOTES.md was left untouched.
- Built flames_v1.py to the NOTES.md plan. Tuning found along the way:
  - Fine noise detail in a vertical-only field turns into column-to-column shear. That produced sharp, swirly
    "squiggles" and a smeared white core. Fix: smooth textures (no detail under ~0.6 of a feature), a shear clamp
    (|dD/dx| ≤ shear_max) next to the stretch clamp, and wider fingers (scale_x 0.6).
  - Moving E across a varying fill tinted cores blue-grey. Fix: warm-order caps (G ≤ rGR·R, B ≤ rBG·G, capped by the
    plate's own percentiles), and thinning/flow are applied through the temperature exponents so a thinned flame goes redder.
  - The defocused foreground torch on B13 needs `soften: 2`. Without it the moved light is sharper than the plate.
  - Sparks are born from the top of every keyed column, not one global tip (that made dotted single-file lines). Drift is 12 and wobble 5.
  - P05: the key had to be raised (v_min .74, rb_min 95) and the region capped at y ≤ 1440 so sun-lit walls and grass don't key.
    Shore sun glitter (x 840-1080, y 872-965) is protected too.
- Shipped: the v1b configs, poc clips, proofs and stills, and the reel final/flames_v1_reel.mp4. All proofs pass with 0 px.
- Next ideas: per-fire amplitude floor for tiny distant fires (phone readability); optional ember glow pulsing on
  the char/embers under fires; spark size by fire size; flames+smoke default pairing for P05.
