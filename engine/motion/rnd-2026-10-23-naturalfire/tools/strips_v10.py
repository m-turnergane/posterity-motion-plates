"""strips for a v10 iteration: 12 consecutive frames forge crop (zoom), layer-only diff (v10 - static, x3), phone 360x640 consecutive."""
import sys, json, numpy as np, cv2; sys.path.insert(0, 'tools'); import fire_v10 as F
d = sys.argv[1]; crop = [int(v) for v in (sys.argv[2].split(',') if len(sys.argv) > 2 else "430,600,660,1100".split(','))]; z = float(sys.argv[3]) if len(sys.argv) > 3 else 1.6
fr = np.load(f"{d}/frames_yuv.npy"); r = json.load(open(f"{d}/range.json")); base = F.decode_yuv(F.STATIC)
H, W = F.H, F.W
def rgb(f):
    return cv2.cvtColor(f.reshape(H * 3 // 2, W), cv2.COLOR_YUV2RGB_I420)
x0, y0, x1, y1 = crop; n = min(12, len(fr)); tiles = []; dif = []; ph = []
for k in range(n):
    a = rgb(fr[k]); b = rgb(base[r["f0"] + k])
    c = cv2.resize(a[y0:y1, x0:x1], None, fx=z, fy=z, interpolation=cv2.INTER_NEAREST); cv2.putText(c, str(r["f0"] + k), (4, 18), 0, .55, (255, 255, 255), 1)
    tiles.append(c); dd = np.clip((a.astype(int) - b.astype(int)) * 3, 0, 255).astype(np.uint8)[y0:y1, x0:x1]; dif.append(cv2.resize(dd, None, fx=z, fy=z, interpolation=cv2.INTER_NEAREST))
    ph.append(cv2.resize(a, (360, 640), interpolation=cv2.INTER_AREA)[150:400, 110:260])
sp = np.full((tiles[0].shape[0], 3, 3), 40, np.uint8)
row = lambda L: np.concatenate(sum([[t, sp[:t.shape[0]]] for t in L], [])[:-1], 1)
cv2.imwrite(f"{d}/strip12_crop.png", cv2.cvtColor(row(tiles), cv2.COLOR_RGB2BGR))
cv2.imwrite(f"{d}/strip12_diff.png", cv2.cvtColor(row(dif), cv2.COLOR_RGB2BGR))
cv2.imwrite(f"{d}/strip12_phone.png", cv2.cvtColor(cv2.resize(row(ph), None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST), cv2.COLOR_RGB2BGR))
# static reference tile
b = rgb(base[r["f0"]]); cv2.imwrite(f"{d}/static_crop.png", cv2.cvtColor(cv2.resize(b[y0:y1, x0:x1], None, fx=z, fy=z, interpolation=cv2.INTER_NEAREST), cv2.COLOR_RGB2BGR))
print("ok", tiles[0].shape)
