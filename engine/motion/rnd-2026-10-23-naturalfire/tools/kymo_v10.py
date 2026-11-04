"""kymographs (y vs t) of v10 - static at given output columns (avg over 3 px), each frame = 4 px wide. Upward travel = streaks rising to the right;
wobble/oscillation = streaks reversing slope. usage: kymo_v10.py ITERDIR out.png X:y0:y1 [X:y0:y1 ...]"""
import sys, json, numpy as np, cv2; sys.path.insert(0, 'tools'); import fire_v10 as F
d, out = sys.argv[1], sys.argv[2]; fr = np.load(f"{d}/frames_yuv.npy", mmap_mode='r'); r = json.load(open(f"{d}/range.json")); base = F.decode_yuv(F.STATIC)
cols = [tuple(int(v) for v in a.split(':')) for a in sys.argv[3:]]; panels = []
for (X, y0, y1) in cols:
    K = []
    for k in range(len(fr)):
        a = np.ascontiguousarray(fr[k]).reshape(-1, F.W)[:F.H].astype(np.float32); b = base[r["f0"] + k][:F.H].astype(np.float32)
        K.append((a - b)[y0:y1, X - 1:X + 2].mean(1))
    K = np.clip(np.stack(K, 1) * 4, 0, 255).astype(np.uint8); K = cv2.resize(K, (K.shape[1] * 4, K.shape[0] * 2), interpolation=cv2.INTER_NEAREST)
    K = cv2.copyMakeBorder(K, 14, 2, 2, 2, cv2.BORDER_CONSTANT, value=80); cv2.putText(K, f"x{X}", (2, 11), 0, .4, 255, 1); panels.append(K)
h = max(p.shape[0] for p in panels); panels = [cv2.copyMakeBorder(p, 0, h - p.shape[0], 0, 0, cv2.BORDER_CONSTANT, value=40) for p in panels]
cv2.imwrite(out, np.concatenate(panels, 1)); print(out)
