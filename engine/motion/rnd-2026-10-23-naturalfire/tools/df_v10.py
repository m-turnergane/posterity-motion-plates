"""per-frame change in the layer-support region (output RGB, mean |F_t - F_t-1| over px where the layer is active in either frame), v10 vs static."""
import sys, json, numpy as np, cv2; sys.path.insert(0, 'tools'); import fire_v10 as F
d = sys.argv[1]; fr = np.load(f"{d}/frames_yuv.npy", mmap_mode='r'); r = json.load(open(f"{d}/range.json")); base = F.decode_yuv(F.STATIC)
rgb = lambda f: cv2.cvtColor(np.ascontiguousarray(f).reshape(F.H * 3 // 2, F.W), cv2.COLOR_YUV2RGB_I420).astype(np.float32)
A = [rgb(fr[k]) for k in range(len(fr))]; B = [rgb(base[r["f0"] + k]) for k in range(len(fr))]
act = [np.abs(a - b).max(2) > 2 for a, b in zip(A, B)]; out = []
for k in range(1, len(A)):
    m = act[k] | act[k - 1]; m4 = act[k] & act[k-1]
    out.append((float(np.abs(A[k] - A[k - 1]).max(2)[m].mean()), float(np.abs(B[k] - B[k - 1]).max(2)[m].mean()), int(m.sum())))
o = np.array(out); print("v10 dF mean %.2f max %.2f | static dF mean %.2f | active px %d" % (o[:, 0].mean(), o[:, 0].max(), o[:, 1].mean(), o[:, 2].mean()))
