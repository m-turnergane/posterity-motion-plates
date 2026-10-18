"""Mobile-size motion check for a clip (advisory numbers + images for a HUMAN to look at; this is NOT playback QC).
usage: motion_report.py CLIP.mp4 OUTDIR [--static PLATE.png]
 - downscales to 390x844 (phone-size) via ffmpeg, computes: mean |frame-to-frame| delta, p99 |pixel change vs frame 0|, max displacement-proxy,
   share of pixels that ever change by >6 grey levels, and the bounding box of that moving area
 - writes heat.png (change heatmap), mobile_contact.jpg (frames 0 / mid / last at 390x844) and 100pct_crop.png (moving-area crop, frame0|last at 100%)"""
import sys, os, json, subprocess, numpy as np, cv2
def frames(path, w=390, h=844):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={w}:{h}:flags=area", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, h, w, 3)
def main(clip, out, static=None):
    os.makedirs(out, exist_ok=True); F = frames(clip).astype(np.float32); n = len(F)
    d = np.abs(np.diff(F, axis=0)).mean(axis=(1, 2, 3)); dev = np.abs(F - F[0]).max(axis=3); peak = dev.max(axis=0)
    ever = peak > 6; ys, xs = np.where(ever)
    stats = dict(frames=n, mobile_size=[390, 844], mean_frame_delta=round(float(d.mean()), 4), max_frame_delta=round(float(d.max()), 4), p99_change_vs_frame0=round(float(np.percentile(dev[-1], 99)), 2),
                 max_change_vs_frame0=round(float(dev.max()), 1), moving_pixel_share_gt6=round(float(ever.mean()), 4), moving_bbox=[int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if len(xs) else None,
                 visible_motion=bool(ever.mean() > 0.002 or dev.max() > 25), restrained=bool(d.max() < 3.0 and np.percentile(dev[-1], 99) < 40))
    heat = cv2.applyColorMap(np.clip(peak * 6, 0, 255).astype(np.uint8), cv2.COLORMAP_INFERNO); cv2.imwrite(os.path.join(out, "heat.png"), heat)
    pick = [0, n // 2, n - 1]; cv2.imwrite(os.path.join(out, "mobile_contact.jpg"), cv2.cvtColor(np.hstack([F[i].astype(np.uint8) for i in pick]), cv2.COLOR_RGB2BGR))
    # 100% crop from the full-res clip around the moving area
    cap = cv2.VideoCapture(clip); W = int(cap.get(3)); H = int(cap.get(4)); frs = []
    for i in (0, n - 1):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i); ok, f = cap.read(); frs.append(f)
    if stats["moving_bbox"]:
        x0, y0, x1, y1 = stats["moving_bbox"]; sx, sy = W / 390, H / 844; cx, cy = int((x0 + x1) / 2 * sx), int((y0 + y1) / 2 * sy)
    else: cx, cy = W // 2, H // 2
    cw, ch = 540, 700; X0 = int(np.clip(cx - cw // 2, 0, W - cw)); Y0 = int(np.clip(cy - ch // 2, 0, H - ch))
    crop = np.hstack([frs[0][Y0:Y0 + ch, X0:X0 + cw], frs[1][Y0:Y0 + ch, X0:X0 + cw]]); cv2.imwrite(os.path.join(out, "100pct_crop_first_last.png"), crop)
    stats["crop_origin_fullres"] = [X0, Y0, cw, ch]; json.dump(stats, open(os.path.join(out, "motion_stats.json"), "w"), indent=1); print(json.dumps(stats)); return stats
if __name__ == "__main__": main(sys.argv[1], sys.argv[2])
