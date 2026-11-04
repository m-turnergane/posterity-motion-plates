"""Luminance swing QC (batch 3): per-region and whole-frame mean luminance over the AFTER half, plate space, 0-255 scale and %,
relative to the plate (BEFORE) value, plus the largest frame-to-frame step (strobing check).
Usage: qc_swing.py configs/x.json '{"face":[x0,y0,x1,y1],...}'"""
import json, sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import animate
cfg = json.load(open(sys.argv[1])); boxes = json.loads(sys.argv[2]); boxes["whole_frame"] = None
E = animate.Engine(cfg); fps = cfg.get("fps", 30); N = int(round(cfg.get("half_seconds", 4.0) * fps))
def m(img, b): return float(animate.lum(img if b is None else img[b[1]:b[3], b[0]:b[2]]).mean() * 255)
L0 = {k: m(E.plate, b) for k, b in boxes.items()}; ser = {k: [] for k in boxes}
for i in range(N):
    img, _, _ = E.render(i / fps)
    for k, b in boxes.items(): ser[k].append(m(img, b))
out = {}
for k, v in ser.items():
    v = np.array(v); b = L0[k]
    out[k] = dict(plate_mean_255=round(b, 2), min_255=round(float(v.min() - b), 2), max_255=round(float(v.max() - b), 2),
                  min_pct=round(float(100 * (v.min() / b - 1)), 1), max_pct=round(float(100 * (v.max() / b - 1)), 1),
                  peak_to_peak_pct=round(float(100 * (v.max() - v.min()) / b), 1), half_swing_about_mid_pct=round(float(50 * (v.max() - v.min()) / ((v.max() + v.min()) / 2)), 1),
                  max_step_255_per_frame=round(float(np.abs(np.diff(v)).max()), 2), max_step_pct_per_frame=round(float(100 * np.abs(np.diff(v)).max() / b), 2),
                  first_1s_peak_to_peak_pct=round(float(100 * (v[:fps].max() - v[:fps].min()) / b), 1))
print(json.dumps(out, indent=1))
