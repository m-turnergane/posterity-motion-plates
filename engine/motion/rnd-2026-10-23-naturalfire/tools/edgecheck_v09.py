"""Explain decoded-lossless pixels changed outside the 9x9 support: magnitude + distance to support (yuv420p chroma 2x2 straddle?)."""
import sys, json, subprocess, numpy as np, cv2
sys.path.insert(0, 'tools'); import prod as P; from specs import load_masks; from flame_v09 import load_masks_v09
def dec(p):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"], capture_output=True, check=True).stdout
    return np.frombuffer(r, np.uint8).reshape(-1, P.H, P.W, 3)
A, S = dec("work/final_v09_poc_lossless.mp4"), dec("work/final_v09_v2cstatic_lossless.mp4")
_c, _e = load_masks_v09(); union = np.maximum.reduce(load_masks() + _c + _e); box = P.plate_box(); seg = dict(P.SEG_POC); seg["frames"] = 180
mimg = np.repeat((union * 255).astype(np.float32)[..., None], 3, 2)
tot, mx, dists, frames = 0, 0, [], 0
for fi in range(len(A)):
    d = np.abs(A[fi].astype(int) - S[fi]).max(-1)
    sup0 = np.asarray(P.frame_out(mimg, box, seg, fi))[..., 0] > 0
    sup = cv2.dilate(sup0.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
    bad = (d > 0) & ~sup
    if bad.any():
        frames += 1; tot += int(bad.sum()); mx = max(mx, int(d[bad].max()))
        dt = cv2.distanceTransform((~sup).astype(np.uint8), cv2.DIST_L2, 3); dists += list(dt[bad])
    if fi % 45 == 0: print(fi, tot, flush=True)
r = dict(px_total=tot, frames_with_any=frames, max_abs=mx, max_dist_from_9x9_support_px=round(float(max(dists)) if dists else 0, 2), mean_dist=round(float(np.mean(dists)) if dists else 0, 2))
print(r); json.dump(r, open("qc/final_v09_decoded_edge_check.json", "x"))
