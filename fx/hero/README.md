# b10 Corfe: full-stack stress test (fullstack_v1)

**Stack:** locked depth_v1 (one camera transform), torch_v1c glow and room ambience, and smoke_v2 rising from the torch only.
There is no dust (owner amendment) and no body motion. smoke_v2's own camera is never used: `push_frame` is called 0 times.

## Method
- `fullstack_v1.py` checks the md5 of every locked file and imports each one read-only by path. It installs a counting trap on `smoke_v2.push_frame`.
- **torch_v1c:** `PlateFX(plate, seed=10)` is rendered in plate space and goes into depth_v1 as `plate_fx`.
  - depth_v1 splits the delta by card coverage, so the glow rides on the one camera.
  - Face keep-out: the torch delta is zeroed on the Kent and gaoler face polys, dilated 6 px and feathered 18 px. Without it the torch moves the faces by up to 41 and 57 levels.
- **smoke_v2:** the `b10_wall_torch` emitters (wall_torch and wisp) use the same loop as `SmokeScene.frame`, but premultiplied.
  - The smoke goes in as depth_v1 `layer_fx["near"]`, so the plume rides the arch card's single warp.
  - A plate_fx split would tear the plume, because 8.4% of the smoke alpha lies where near-alpha is below 0.5.
- **Length:** 7 s, 30 fps, 210 frames. The 1080x1920 master is crf 20; the 540 A/B clips are crf 23. No audio stream, no text, vignette, letterbox or watermark.

## Run
```
/workspace/mpvenv/bin/python fullstack_v1.py run --tag fullstack_v1
/workspace/mpvenv/bin/python fullstack_v1.py run --tag fullstack_v1_restrained --smoke-gain 0.4 --final-only
/workspace/mpvenv/bin/python proofs_static.py
/workspace/mpvenv/bin/python proofs_face_attrib.py
```

## Outputs
| File | What it is |
|---|---|
| `final/b10_corfe_fullstack_v1.mp4` | Full stack at 1080x1920 |
| `final/b10_corfe_fullstack_v1_f105.png` | Still grab |
| `final/b10_corfe_fullstack_v1_restrained.mp4` (+ `_f105.png`) | Smoke alpha ×0.4. **This is the recommended variant.** |
| `poc/b10_corfe_fullstack_v1_poc540.mp4` | 540p POC |
| `ab/..._ab540_torch_off.mp4`, `ab/..._ab540_smoke_off.mp4` | Per-effect toggles |
| `ab/..._ab540_both_off_depth_only.mp4` | Reference with both effects off |
| `proofs/static_fullstack_v1.json`, `run_fullstack_v1.json`, `run_fullstack_v1_restrained.json`, `face_attrib_fullstack_v1.json` | Proofs |
| `proofs/deltamap_fullstack_v1_{torch,smoke}_{max,mean}.png` | On/off delta maps per effect |

The delta maps were labelled the wrong way round at run time. I swapped them back after the run and fixed the code at `fullstack_v1.py:200`. The correction is recorded in the JSON.
