"""forge-mouth zoom compare strip. usage: zoomcmp_v13.py OUT.png x0,y0,x1,y1 zoom f1,f2,.. LABEL=src [LABEL=src ...]
src = .mp4 (decoded) or iter dir with frames_yuv.npy + range.json (frames outside its range are skipped -> grey). rows = sources, cols = frames."""
import sys, json, os, subprocess, numpy as np, cv2
sys.path.insert(0, 'tools'); import fire_v10 as F
out, crop, z, fr = sys.argv[1], [int(v) for v in sys.argv[2].split(',')], float(sys.argv[3]), [int(v) for v in sys.argv[4].split(',')]
x0, y0, x1, y1 = crop; rows = []
def get(src, f):
    if src.endswith('.mp4'):
        r = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vf", f"select=eq(n\\,{f})", "-vframes", "1", "-f", "rawvideo", "-pix_fmt", "yuv420p", "pipe:1"], capture_output=True, check=True).stdout
        a = np.frombuffer(r, np.uint8)
    else:
        rg = json.load(open(f"{src}/range.json")); k = f - rg["f0"]
        if not (0 <= k < rg["N"]): return None
        a = np.asarray(np.load(f"{src}/frames_yuv.npy", mmap_mode='r')[k])
    return cv2.cvtColor(a.reshape(F.H * 3 // 2, F.W), cv2.COLOR_YUV2BGR_I420)
for it in sys.argv[5:]:
    lab, src = it.split('=', 1); T = []
    for f in fr:
        a = get(src, f); c = np.full((int((y1 - y0) * z), int((x1 - x0) * z), 3), 60, np.uint8) if a is None else cv2.resize(a[y0:y1, x0:x1], None, fx=z, fy=z, interpolation=cv2.INTER_CUBIC)
        cv2.rectangle(c, (0, 0), (len(lab) * 11 + 50, 20), (0, 0, 0), -1); cv2.putText(c, f"{lab} f{f}", (4, 15), 0, .5, (255, 255, 255), 1, cv2.LINE_AA)
        c[:, -2:] = 30; T.append(c)
    rows.append(np.concatenate(T, 1))
for r_ in rows: r_[-2:] = 30
assert not os.path.exists(out) or out.startswith('/tmp'); cv2.imwrite(out, np.concatenate(rows, 0)); print(out)
