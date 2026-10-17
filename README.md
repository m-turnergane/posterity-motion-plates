# posterity-motion-plates (experimental, private)

Restrained painterly motion for *selected* Posterity plates: petals that fall and settle, flickering braziers/torches with localized light, swaying banners, drifting dust and a small eased 2.5D push with real layer parallax. Python-first (NumPy + OpenCV + Pillow + FFmpeg); no second compositing engine. Separate from the production editor: the ordinary stills pipeline is unchanged and the original plate stays the fallback.

## Quick start
```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt && pip install -e .
export MOTIONPLATES_PLATES=/workspace/posterity/day20/alexander-corpse/plates   # read-only; plates are never copied here
python -m motionplates render recipes/poc_a_augustus.yaml --out out/a --compare --export-layers out/a/layers   # PoC A, ~100 s on 8 cores
python -m motionplates render recipes/poc_b_corridor.yaml --out out/b --compare                              # PoC B
python -m motionplates render recipes/poc_a_augustus.yaml --out out/a --at 0,1.4,4.97                       # fast iteration: stills only
pytest -q                                                                                                    # tests on a generated synthetic plate
```
Outputs per recipe: `<name>_animated.mp4` (1080x1920, 30 fps, crf14 yuv420p), `<name>_compare_sidebyside.mp4` (static | animated, 1280 wide), labelled stills + static/animated pair JPGs, `<name>_manifest.json` (plate md5, recipe md5, seed, params, timings, frame-0 diff, motion stats, per-frame SHA1, safe-zone and edge scans). Lossless intermediate (x264 crf0 intra) is deleted unless `--keep-lossless`.

## How it works
1. **Plate** -> `core/plate.py` (same bar detection + cover-fit as the build scripts).
2. **Layer stack** -> `core/layers.py`: hand-authored polygons in the recipe (optionally refined with GrabCut inside a band) become depth layers (bg, mid, fg) and alpha elements (banners). Objects to remove (e.g. the artwork's suspended petals) are cut as alpha sprites and the **clean plate** is filled (`telea_exclude` + haze texture). Each layer gets disocclusion fill behind whatever is in front (two-stage TELEA: coarse + full-res band).
3. **Effects** (`effects/`), configured by YAML + presets: `parallax_push`, `petal_fall`, `flame_flicker` (flame warp + colour shift + localized light), `torch_light` (broad light + moving soft shadow field), `banner_sway`, `fabric_ripple`, `dust_motes`.
4. **Frame loop** (`core/engine.py`): stateless in `t`; per frame: effects edit layer pixels -> eased differential parallax composite -> particles -> fading residual so frame 0 == plate -> lossless pipe -> delivery encode.

See `docs/ARCHITECTURE.md`, `docs/AUTHORING-EFFORT.md`, `AGENTS.md`, `docs/EXPERIMENT-C-grok-imagine.md` (skipped).
