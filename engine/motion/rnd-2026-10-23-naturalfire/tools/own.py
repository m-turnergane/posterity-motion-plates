"""Flame's OWN behaviour (glow divided out): poc/static ratio series in tip/body bands; sharpness ratio; per-frame change."""
import sys, json, numpy as np, cv2
from scipy import signal
sys.path.insert(0, 'tools'); from specs import load_masks
F = np.load(sys.argv[1]).astype(np.float32); S = np.load('iter/v00_static/crop_frames.npy').astype(np.float32); CX0, CY0 = 368, 672
masks = load_masks(); res = {}
def bands(s, fps=30):
    s = signal.detrend(s - s.mean()); f, P = signal.welch(s, fs=fps, nperseg=128, noverlap=96); tot = P[f > 0.1].sum() + 1e-12
    b = {k: round(float(P[(f >= lo) & (f < hi)].sum() / tot), 3) for k, (lo, hi) in {"0.1-0.3": (.1, .3), "0.3-0.6": (.3, .6), "0.6-2": (.6, 2), "2-5": (2, 5), "5-15": (5, 15)}.items()}
    b["centroid_hz"] = round(float((f[f > .1] * P[f > .1]).sum() / tot), 2); return b
for i, mk in enumerate(masks):
    m = mk[CY0:CY0 + F.shape[1], CX0:CX0 + F.shape[2]] > 0.5; ys = np.nonzero(m.any(1))[0]; y0, y1 = ys.min(), ys.max()
    hh = np.zeros_like(m, np.float32); hh[y0:y1 + 1] = np.linspace(1, 0, y1 - y0 + 1)[:, None]
    tip = m & (hh > 0.6); body = m & (hh < 0.35)
    Lp, Ls = F.mean(3), S.mean(3)
    rt = Lp[:, tip].mean(1) / Ls[:, tip].mean(1); rb = Lp[:, body].mean(1) / Ls[:, body].mean(1)
    lap = lambda X: np.array([cv2.Laplacian(x, cv2.CV_32F)[m].var() for x in X])
    sh = lap(Lp) / lap(Ls)
    # local (pixel) own change: |d(Lp/Ls)| per frame
    R = Lp[:, m] / Ls[:, m]; d = np.abs(np.diff(R, axis=0)).mean(1)
    res[f"c{i}"] = dict(tip_own_cv=round(float(rt.std() / rt.mean()), 4), tip_own=bands(rt), body_own_cv=round(float(rb.std() / rb.mean()), 4), body_own=bands(rb),
                        sharp_ratio_mean=round(float(sh.mean()), 3), sharp_ratio_min=round(float(sh.min()), 3), own_pixel_change_pct=round(100 * float(d.mean()), 2))
    print(f"c{i}", res[f"c{i}"])
if len(sys.argv) > 2: json.dump(res, open(sys.argv[2], 'w'), indent=1)
