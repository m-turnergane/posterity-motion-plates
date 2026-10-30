"""Per-layer displacement QC: max |displacement| of plate pixels per preset layer (sampled every 3rd AFTER frame), and
how far each layer's warp reaches into the protect mask.  Usage: qc_layers.py configs/x.json"""
import json, sys, numpy as np
sys.path.insert(0, __import__("os").path.dirname(__file__))
from animate import Engine
cfg = json.load(open(sys.argv[1])); E = Engine(cfg); fps = cfg.get("fps", 30); N = int(round(cfg.get("half_seconds", 4.0) * fps))
res = {}
for j, (L, P) in enumerate(E.layers):
    mx = 0.0; mp = 0.0; edge = 0.0
    for i in range(0, N, 3):
        d = P.disp(i / fps)
        if d is None: break
        m = np.sqrt(d[0] ** 2 + d[1] ** 2); mx = max(mx, float(m.max()))
        if E.protect.any(): mp = max(mp, float(m[E.protect].max()))
    res[f"{j}:{L['preset']}"] = dict(max_disp_px=round(mx, 3), max_disp_in_protect_px=round(mp, 3), uses_displacement=mx > 0)
print(json.dumps(res, indent=1))
