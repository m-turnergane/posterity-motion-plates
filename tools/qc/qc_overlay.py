"""Readable mask-overlay QC still: per-layer masks tinted + outlined; full-frame layers (>=95 % coverage) are only listed.
Protect masks = white hatch.  Usage: qc_overlay.py configs/x.json out.png"""
import json, sys, os, numpy as np, cv2
from engine_loader import load_animate
animate = load_animate()
cfg = json.load(open(sys.argv[1])); out = sys.argv[2]
if os.path.exists(out): raise SystemExit("exists: " + out)
E = animate.Engine(cfg); ov = E.plate.copy()
cols = [(255, 60, 60), (60, 140, 255), (60, 230, 90), (255, 0, 255), (255, 200, 0), (0, 230, 230)]
lines = []; cont = []
for j, (L, P) in enumerate(E.layers):
    c = cols[j % len(cols)]; a = P.allow(); cov = a.mean() * 100
    m = P.m if cov < 95 else None
    if cov >= 95 and P.m.mean() < 0.95: m = P.m        # e.g. smoke clipped to opening but ash full-frame: show the clip mask
    if m is not None:
        al = (np.clip(m, 0, 1) * 0.42)[..., None]; ov = ov * (1 - al) + np.float32(c) * al
        cont.append(((m > 0.5).astype(np.uint8), c))
    lines.append((f"{L['preset']}  mask {os.path.basename(L.get('mask') or 'none')}  allow {cov:.0f}%" + ("  (full frame)" if m is None else ""), c))
ov = np.round(ov).astype(np.uint8)
for b, c in cont:
    cs, _ = cv2.findContours(b, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE); cv2.drawContours(ov, cs, -1, c, 2)
if E.protect.any(): ov[((E.X + E.Y) % 16 < 2) & E.protect] = (255, 255, 255)
ov[8:24 + 26 * (len(lines) + 1), 8:E.W - 8] = (ov[8:24 + 26 * (len(lines) + 1), 8:E.W - 8] * 0.35).astype(np.uint8); ov = np.ascontiguousarray(ov)
y = 34
for t, c in lines:
    cv2.rectangle(ov, (16, y - 14), (30, y), c, -1); cv2.putText(ov, t, (38, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA); y += 26
if E.protect.any(): cv2.putText(ov, "white hatch = protect mask (displacement measured, must be 0)", (16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
cv2.imwrite(out, cv2.cvtColor(ov, cv2.COLOR_RGB2BGR)); print("wrote", out)
