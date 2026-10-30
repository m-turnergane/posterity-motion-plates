"""Strict per-layer containment QC (batch 3): render each layer alone and measure the max change OUTSIDE the layer's declared
mask PNG (not its allow-region). Catches overlays whose bounding box leaks past the mask (e.g. flames over a foreground jamb)."""
import json, sys, numpy as np, cv2
sys.path.insert(0, '/workspace/posterity/motion/iterations-2026-10-22'); import animate
cfg = json.load(open(sys.argv[1])); ts = [0.5, 1.3, 2.0, 2.7, 3.5]; res = {}
for j, L in enumerate(cfg["layers"]):
    E = animate.Engine(cfg); E.layers = [E.layers[j]]; P = E.layers[0][1]
    out = ~(P.m > 1e-4); mx = 0.0; where = None
    for t in ts:
        d = np.abs(E.render(t)[0] - E.plate).max(2); d[~out] = 0
        if d.max() > mx: mx = float(d.max()); yy, xx = np.unravel_index(d.argmax(), d.shape); where = dict(t=t, x=int(xx), y=int(yy))
    res[f"{j}:{L['preset']}"] = dict(mask=L.get("mask"), max_diff_outside_declared_mask=round(mx, 3), where=where, frames_checked=ts)
print(json.dumps(res, indent=1))
