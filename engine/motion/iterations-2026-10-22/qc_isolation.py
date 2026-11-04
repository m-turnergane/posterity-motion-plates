"""Layer-isolation stability QC: render each preset layer ALONE (same seed/index) and measure max |AFTER-plate|
outside that layer's own allow mask (must be 0) + its own mask coverage.  Needed because full-frame layers
(cloud shadows, light-shift) make the union-mask check vacuous.  Usage: qc_isolation.py configs/x.json"""
import json, sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import animate
cfg = json.load(open(sys.argv[1])); fps = cfg.get("fps", 30); N = int(round(cfg.get("half_seconds", 4.0) * fps)); res = {}
full = animate.Engine(cfg)
for j, L in enumerate(cfg["layers"]):
    E = animate.Engine(cfg)                      # same RNG seeding: layer j keeps rng [seed, j]
    E.layers = [E.layers[j]]; P = E.layers[0][1]; allow = P.allow(); out = ~allow; mx = 0.0; where = None
    for i in range(0, N, 4):
        img, dx, dy = E.render(i / fps); d = np.abs(img - E.plate).max(2)
        if out.any() and d[out].max() > mx:
            mx = float(d[out].max()); yy, xx = np.unravel_index(np.argmax(np.where(out, d, -1)), d.shape); where = dict(t=i / fps, x=int(xx), y=int(yy))
    res[f"{j}:{L['preset']}"] = dict(mask=L.get("mask"), own_mask_coverage_pct=round(float(allow.mean() * 100), 2), max_diff_outside_own_mask=mx, where=where)
# protect-zone luminance-only check for the full stack (geometry static, light may change)
print(json.dumps(res, indent=1))
