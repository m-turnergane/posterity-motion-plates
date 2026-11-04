import sys, json, numpy as np, cv2
sys.path.insert(0, 'tools'); import prod as P; from specs import load_masks
pl = cv2.imread(str(P.PLATE)); pr = cv2.imread(str(P.MASKS / "P05_protect.png"), 0); d = json.load(open(P.MASKS / "P05_candles.json"))
X0, Y0, X1, Y1, S = map(int, sys.argv[1:6]); out = sys.argv[6]
im = pl.copy()
ov = im.copy(); ov[pr > 0] = (ov[pr > 0] * 0.5 + np.array([255, 0, 0]) * 0.5).astype(np.uint8)   # protect = blue tint
im = cv2.addWeighted(im, 0.55, ov, 0.45, 0)
for p in d["face_hand_polys"]: cv2.polylines(im, [np.array(p, np.int32)], True, (255, 0, 255), 1)
for p in d["exclude_polys"]: cv2.polylines(im, [np.array(p, np.int32)], True, (0, 0, 0), 1)
for i, m in enumerate(load_masks()):
    cs, _ = cv2.findContours((m > 0.5).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); cv2.drawContours(im, cs, -1, (0, 255, 0), 1)
c = cv2.resize(im[Y0:Y1, X0:X1], None, fx=S, fy=S, interpolation=cv2.INTER_NEAREST)
raw = cv2.resize(pl[Y0:Y1, X0:X1], None, fx=S, fy=S, interpolation=cv2.INTER_NEAREST)
for img in (c, raw):
    for x in range(X0 - X0 % 20 + 20, X1, 20): cv2.line(img, ((x - X0) * S, 0), ((x - X0) * S, 6), (255, 255, 255), 1); cv2.putText(img, str(x), ((x - X0) * S + 1, 16), 0, 0.3, (255, 255, 255), 1) if x % 40 == 0 else None
    for y in range(Y0 - Y0 % 20 + 20, Y1, 20): cv2.line(img, (0, (y - Y0) * S), (6, (y - Y0) * S), (255, 255, 255), 1); cv2.putText(img, str(y), (8, (y - Y0) * S + 4), 0, 0.3, (255, 255, 255), 1) if y % 40 == 0 else None
cv2.imwrite(out, np.hstack([raw, c]))
print((pr > 0).mean(), pl.shape)
