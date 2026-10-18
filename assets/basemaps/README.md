# Base maps

`tamerlane_eurasia_painted.png` — owner-supplied painted Eurasia / Middle East map for the internal PoC C (cartography).
- 941x1672 px (9:16), PNG, 3.5 MB, md5 `1004379863d6234fce808a05654cd055`.
- NOT committed (see .gitignore; the repo must not hold large binaries). Place the file here manually and verify the md5.
- Contains baked glowing pins and labels (CONSTANTINOPLE, BAGHDAD, DELHI, SAMARKAND); see docs/POC-C-CARTOGRAPHY-DESIGN.md for the treatment (inpaint vs overlay).
- Internal use only; never posted.

## `tamerlane_eurasia_clean.png` (generated, NOT committed)
Base map with the baked pins, glows, rays and the four labels removed, so every marker/label is drawn by the engine and tied to the georef. Regenerate deterministically:
`python tools/clean_basemap.py assets/basemaps/tamerlane_eurasia_painted.png assets/basemaps/tamerlane_eurasia_clean.png` -> md5 `f29e9b544a72bcacb6bd42bc37e05aeb` (original untouched; it remains the fallback).
Method: tight stroke/pin masks (not whole boxes), Telea inpaint, masked blur, per-channel gain equalisation of the darkened scrim/orange glow, matched grain. Checked at 100 %: text, pins and rays gone and coasts/rivers intact; **residual faint smudges remain** (grey scrim east of Samarkand over the Pamirs, orange halo remnant near Samarkand, soft patch at the Black Sea/Constantinople). Acceptable for the internal PoC; a repaint or an owner-supplied label-free map is the real fix. `detect_baked()` reports 1 pin + 4 text components on the original and 0 on the clean map.
