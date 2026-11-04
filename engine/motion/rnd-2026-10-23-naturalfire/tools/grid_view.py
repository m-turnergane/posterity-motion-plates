import sys, json, numpy as np, cv2
sys.path.insert(0, 'tools'); import prod as P; from specs import load_masks
pl = cv2.imread(str(P.PLATE)); d = json.load(open(P.MASKS / "P05_candles.json"))
X0, Y0, X1, Y1, S = map(int, sys.argv[1:6]); out = sys.argv[6]; extra = sys.argv[7] if len(sys.argv) > 7 else None
im = cv2.resize(pl[Y0:Y1, X0:X1], None, fx=S, fy=S, interpolation=cv2.INTER_CUBIC)
def P2(x, y): return (int((x - X0 + 0.5) * S), int((y - Y0 + 0.5) * S))
for p in d["face_hand_polys"]: cv2.polylines(im, [np.array([P2(*q) for q in p], np.int32)], True, (255, 0, 255), 1)
for m in load_masks():
    cs, _ = cv2.findContours((m > 0.5).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(im, [((c.astype(np.float32) - [X0, Y0] + 0.5) * S).astype(np.int32) for c in cs], -1, (0, 255, 0), 1)
if extra:
    m = cv2.imread(extra, 0)
    if m is not None:
        cs, _ = cv2.findContours((m > 127).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(im, [((c.astype(np.float32) - [X0, Y0] + 0.5) * S).astype(np.int32) for c in cs], -1, (255, 255, 0), 1)
for x in range((X0 // 10 + 1) * 10, X1, 10):
    cv2.line(im, P2(x, Y0), P2(x, Y0 + (3 if x % 50 else 6)), (255, 255, 255), 1)
    if x % 50 == 0: cv2.putText(im, str(x), (P2(x, Y0)[0] + 2, 14), 0, 0.4, (255, 255, 255), 1)
for y in range((Y0 // 10 + 1) * 10, Y1, 10):
    cv2.line(im, P2(X0, y), P2(X0 + (3 if y % 50 else 6), y), (255, 255, 255), 1)
    if y % 50 == 0: cv2.putText(im, str(y), (14, P2(X0, y)[1] + 4), 0, 0.4, (255, 255, 255), 1)
cv2.imwrite(out, im)
