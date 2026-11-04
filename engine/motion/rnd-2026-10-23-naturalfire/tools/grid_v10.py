"""12 consecutive frames of a crop as a 2x6 grid (+ optional diff vs static). usage: grid_v10.py ITERDIR x0,y0,x1,y1 zoom out.png [diff] [step]"""
import sys, json, numpy as np, cv2; sys.path.insert(0, 'tools'); import fire_v10 as F
d, crop, z, out = sys.argv[1], [int(v) for v in sys.argv[2].split(',')], float(sys.argv[3]), sys.argv[4]; diff = len(sys.argv) > 5 and sys.argv[5] == "diff"; step = int(sys.argv[6]) if len(sys.argv) > 6 else 1
fr = np.load(f"{d}/frames_yuv.npy", mmap_mode='r'); r = json.load(open(f"{d}/range.json")); base = F.decode_yuv(F.STATIC) if diff else None
x0, y0, x1, y1 = crop; T = []
for k in range(0, min(12 * step, len(fr)), step):
    a = cv2.cvtColor(np.ascontiguousarray(fr[k]).reshape(F.H * 3 // 2, F.W), cv2.COLOR_YUV2RGB_I420)
    if diff: b = cv2.cvtColor(base[r["f0"] + k].reshape(F.H * 3 // 2, F.W), cv2.COLOR_YUV2RGB_I420); a = np.clip((a.astype(int) - b.astype(int)) * 3, 0, 255).astype(np.uint8)
    c = cv2.resize(a[y0:y1, x0:x1], None, fx=z, fy=z, interpolation=cv2.INTER_CUBIC if z > 1 else cv2.INTER_AREA); cv2.putText(c, str(r["f0"] + k), (3, 14), 0, .45, (255, 255, 255), 1); T.append(c)
while len(T) < 12: T.append(np.zeros_like(T[0]))
sp = lambda t: np.full((t.shape[0], 2, 3), 60, np.uint8)
rows = [np.concatenate(sum([[t, sp(t)] for t in T[i:i + 6]], [])[:-1], 1) for i in (0, 6)]
g = np.concatenate([rows[0], np.full((2, rows[0].shape[1], 3), 60, np.uint8), rows[1]], 0); cv2.imwrite(out, cv2.cvtColor(g, cv2.COLOR_RGB2BGR)); print(g.shape)
