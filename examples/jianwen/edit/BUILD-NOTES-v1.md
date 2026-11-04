# Jianwen ROUGH v1: build notes (DRAFT script, not run on plates)

- `build_rough_jianwen_v1.py` + `fx_jianwen_v1.py` are adapted copies of Edward II `build_rough_edward_ii_v3b_v1c.py` / `fx_v1c.py` (originals untouched). `make_timing_grid_v1.py` writes `timing_grid_v1.json` / `TIMING-GRID-v1.md`. The build checks the grid's md5, and the grid checks the VO and word-alignment md5s.
- Run: `/workspace/mpvenv/bin/python edit/build_rough_jianwen_v1.py [--tag v1]` writes `/workspace/posterity/renders/posterity-jianwen-ROUGH-<tag>.mp4` + `-preview.mp4`.
- Guards (in order):
  1. Prints disk free.
  2. Exits with code 2 and renders nothing if any of the 18 plates is missing from `plates-v1/`.
  3. Exits with code 3 if any fx spec is still a template.
  4. Refuses if the master or preview already exists (ffmpeg also runs with `-n`).
  5. Needs at least 4 GiB free.
- Order of work once the plates land:
  1. Drop the plates into `plates-v1/` with the exact file names from the grid.
  2. Run `--fx-overlays`, which writes `/dev/shm/jwqc/overlay_S*.png`.
  3. Fill `fx_jianwen_v1.SPECS` per plate: rects in plate pixels; remove `todo=True`. Calibrate `PULSE` per plate (default 0.35).
  4. Set the `ANCHOR` push targets.
  5. Check the title band on J01 with `--test-frames 30,60,100`. topPercent defaults to 32.5; fontSize is 74 because the house size of 88 overflows.
  6. Render.
- Audio:
  - `--audio-only` needs no plates. Tested into /tmp scratch: −14.1 LUFS, −1.9 dBTP.
  - Bed: −17.5 dB before ducking, which puts gaps at about −27 to −32 dBFS, matching Edward's −25 to −30.
  - No SFX.
- Motion rules carried over: flame-shape warp on candle-sized flames only. Lanterns sway through a ROI-local rotation inside the lantern box. Torches and big fires keep their painted shapes and get glow and spill only. No land, face or water warp. Embers are 2.2-3.6 plate px so they read at phone size. Captions fade in/out over 120/80 ms. The title is the v3.2b 4.0 s lock on S01, clean by frame 118. Push is 1.00 to 1.06 (1.00 to 1.02 on the outro).

## v1b update (Vellum's calls, 2026-10-30)

- **Grid:** the build now reads `timing_grid_v1b.json`, made by `make_timing_grid_v1b.py`; GRID_MD5 is locked. The v1 grid, its MD and its generator are kept unchanged for reference.
- **Opening:** J01 is split in two.
  - **S01A WIDE:** 0.000-2.600 s (f0-78, 2.60 s), "They pulled a burned body from the palace". Push 1.00 to 1.04.
  - **S01B TIGHT:** 2.600-4.933 s (f78-148, 2.33 s), "and called it the emperor." This is a reframe/crop of the same J01 plate. Push 1.00 to 1.04.
  - **Cut:** on "and" (0.21 s gap, so the cut sits on the word-start frame). That gives 2 cuts in the first 5 s (f78, f148).
  - **Fx continuity:** S01A and S01B share the fx seed (keyed by plate) and the global clock, so fire and embers run continuously through the cut.
- **Title:** two-line, size 74, topPercent 32.5, with the v3.2b 4.0 s lock across both shots. Stroke f8-26, letters f14-42, full hold f42-88; the S01A|S01B cut at f78 falls inside the hold, as Edward v3 carried its title across the opening cuts. Exit f88-108, clear f97-118, so it is gone before S02 at f148. The script asserts that the cut lands inside the hold.
- **Tight crop:** the placeholder is centre (0.50, 0.55), frac 0.75; on a 1080x1920 plate that is 810x1440 px, a 1.33x upscale. Set the real values with `--s01b-center x,y --s01b-frac f` (or edit the grid). Rules:
  - `--opening auto` (default) splits when frac ≥ 0.70.
  - Below 0.70 it falls back to one WIDE S01 at 0-4.933 s with a faster push of 1.00 to 1.14 and prints a FLAG. `--opening fallback` forces this.
  - It also flags a crop that leaves under 756 source px for the 1080 px output.
- **First checks when J01 lands:** run `--test-frames 30,60,77,78,100,130`. Read the title height against faces in both the wide shot and the tight one; the tight shot magnifies faces under the fixed title band. Then pick the S01B centre and frac.
- **Outro:** motion approved at 4.97 s: light lantern sway, mist and a few embers, all kept off the lettering. Fill the outro fx spec with a lettering-exclusion rect.
- **Unchanged:** VO (Zhu Di "Joo-Dee" accepted) and Ripples.
- **Captions:** the v1b grid has 48 cues. "from the palace" is now its own cue so no caption straddles the f78 cut.
