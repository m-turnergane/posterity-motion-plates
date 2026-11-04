"""Zero-motion proofs + diff images + contact sheet for a smoke_v2 reel.
usage: python proofs_v2.py configs/reel_final.json final/   [--reel-mp4 final/smoke_v2_final_reel.mp4]
Writes OUT/proofs.json, OUT/diff_<shot>.png (plate | frame | |diff|x4, protect in blue, guards in red),
OUT/contact_sheet.png (3 frames per shot at 360x640, read from the rendered reel if given)."""
import json, sys, subprocess, argparse
from pathlib import Path
import numpy as np, cv2
import smoke_v2 as S

ap = argparse.ArgumentParser(); ap.add_argument("reel"); ap.add_argument("out"); ap.add_argument("--reel-mp4", default=None)
ap.add_argument("--step", type=float, default=0.5)
a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
reel = json.load(open(a.reel)); base = Path(a.reel).parent.parent
res = {}
for shot in reel["shots"]:
    name = Path(shot["config"]).stem; cfg = json.load(open(base / shot["config"]))
    sc = S.SmokeScene(S.load_plate(cfg["plate"]), cfg)
    times = list(np.arange(0, shot["seconds"] + 1e-6, a.step))
    r = S.zero_motion_report(sc, times, cfg.get("guards")); r["seconds"] = shot["seconds"]; r["times_step"] = a.step
    res[name] = r; print(name, json.dumps(r), flush=True)
    t = shot["seconds"] / 2; f = sc.frame(t); P = sc.P
    d = np.abs(f.astype(np.int16) - P.astype(np.int16)).max(-1)
    heat = cv2.cvtColor(np.clip(d * 4, 0, 255).astype(np.uint8), cv2.COLOR_GRAY2RGB)
    H, W = P.shape[:2]
    for p in cfg.get("protect", []):
        cv2.polylines(heat, [np.int32(p)], True, (60, 120, 255), 2)
    for p in (cfg.get("guards") or {}).values():
        cv2.polylines(heat, [np.int32(p)], True, (255, 40, 40), 2)
    im = np.hstack([P, f, heat]); s = 640 / H
    cv2.imwrite(str(out / f"diff_{name}.png"), cv2.cvtColor(cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2BGR))
json.dump(res, open(out / "proofs.json", "w"), indent=1)
if a.reel_mp4:
    rows, t0 = [], 0.0
    for shot in reel["shots"]:
        tiles = []
        for tt in (0.05, shot["seconds"] / 2, shot["seconds"] - 0.05):
            raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{t0 + tt:.3f}", "-i", a.reel_mp4, "-frames:v", "1",
                                  "-vf", "scale=360:640", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
            tiles.append(np.frombuffer(raw, np.uint8).reshape(640, 360, 3))
        rows.append(np.hstack(tiles)); t0 += shot["seconds"]
    sheet = np.vstack(rows)                     # one row per shot: start | middle | end
    cv2.imwrite(str(out / "contact_sheet.png"), sheet)
