"""Light-spill QC: per-region relative luminance change over the AFTER half (plate space) and its correlation with the
flame's brightness -> proves flame and spill breathe in sync, and quantifies 'visible but subtle'.
Usage: qc_spill_sync.py configs/x.json '{"face":[x0,y0,x1,y1],...}' flame_box"""
import json, sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import animate
cfg = json.load(open(sys.argv[1])); boxes = json.loads(sys.argv[2]); fb = json.loads(sys.argv[3])
E = animate.Engine(cfg); fps = cfg.get("fps", 30); N = int(round(cfg.get("half_seconds", 4.0) * fps))
L0 = {k: animate.lum(E.plate[y0:y1, x0:x1]).mean() for k, (x0, y0, x1, y1) in boxes.items()}
ser = {k: [] for k in boxes}; fl = []
for i in range(N):
    img, dx, dy = E.render(i / fps)
    for k, (x0, y0, x1, y1) in boxes.items(): ser[k].append(animate.lum(img[y0:y1, x0:x1]).mean() / L0[k] - 1)
    x0, y0, x1, y1 = fb; fl.append(animate.lum(img[y0:y1, x0:x1]).mean())
fl = np.array(fl); out = {}
for k, v in ser.items():
    v = np.array(v) * 100
    out[k] = dict(min_pct=round(float(v.min()), 2), max_pct=round(float(v.max()), 2), std_pct=round(float(v.std()), 2),
                  max_step_pct_per_frame=round(float(np.abs(np.diff(v)).max()), 2), corr_with_flame=round(float(np.corrcoef(v, fl)[0, 1]), 3))
print(json.dumps(out, indent=1))
