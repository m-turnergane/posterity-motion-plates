# Environment motion templates + swap-with-fallback (production-adjacent, restrained)

Templates (recipes/templates/env_*.yaml, existing effects only, no new effect code, no layers/GrabCut; one coarse feathered polygon at most):
| template | effect used | typical plates | notes |
|---|---|---|---|
| env_torchlight | flame_flicker + torch_light | torchlit interiors, lanterns, braziers, campfires | set x,y per flame; gain <= 0.3 |
| env_dust | dust_motes | light shafts, halls, ruins | 40-110 motes, keep out of caption band |
| env_smoke | smoke_drift | chimney / fire / battlefield smoke | polygon around plume, amp <= 2 px |
| env_mist | smoke_drift (broad, slow) | ground fog, river haze, sky haze | large scale_px, low wisp opacity |
| env_foliage | fabric_ripple (low amp, long wavelength) | grass, reeds, tree canopies | NOT individual leaves; amp <= 1.5 px |
| env_water | fabric_ripple (tiny) | calm water | keep shorelines/hulls outside the polygon |
All: 1080x1920, 30 fps, `output.seconds` = slot duration + ~0.5 s handles (recipe parameter), **no camera push baked** (the editor applies its own push-in), safe-zone check on the caption band, status always REVIEW_REQUIRED.

## Per clip procedure
1. `motionplates new --template env_torchlight --plate seqNN_x_OWNER.png --name seqNN_torch --out work/recipes/seqNN_torch.yaml`; edit PARAMS (coordinates in the 1080x1920 cover-fit plate; seconds).
2. `motionplates validate work/recipes/seqNN_torch.yaml --plates PLATES_DIR`
3. `motionplates render ... --plates PLATES_DIR --out work/seqNN --compare`  (use `--proxy 0.35` for quick looks only)
4. `python tools/motion_report.py work/seqNN/seqNN_torch_animated.mp4 work/seqNN/mobile` -> 390x844 stats, heat map, contact sheet, 100% crop. LOOK at the crop (halos/edges at the polygon boundary, flicker not pulsing, caption band calm). Reject anything doubtful; the static plate is the shot.
5. Hand the clip + manifest + side-by-side to the owner. Approval only by a human-committed `approvals/<mp4_sha256>.json` (docs/APPROVALS.md). Agents never create it.

## Build-script swap with automatic fallback
```
motionplates resolve PLATE.png CLIP_DIR NAME --slot-seconds 6.2          # prints JSON {"kind": "clip"|"static", "path": ..., "reason": ...}
```
or in Python: `from motionplates.fallback import resolve; r = resolve(plate, clip_dir, name, slot_seconds=6.2)` then `src = r["path"]`; if `r["kind"] == "clip"` feed the MP4 as the video segment, else the PNG through the normal still path (the build's own push-in applies in both cases). `resolve` never raises. It returns the static PNG unless: manifest+mp4 exist, mp4 SHA-256 matches the manifest, the plate md5 matches the plate being swapped, status is not FAIL/PROXY, ffprobe + full decode verify (size/fps/frames/yuv420p), the clip is at least as long as the slot, AND a valid human approval record exists for that MP4's SHA-256. `--allow-unapproved` exists for preview builds only (result flagged `approved: false`; a publish build must not pass it). A missing static plate returns kind MISSING (exit 3) - the build must fail loudly.
