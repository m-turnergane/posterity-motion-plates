"""Per-frame change (dF% = mean|dL|/mean L inside the flame region) of the real-fire references: the 'no strobing' ceiling for v09."""
import sys, json, numpy as np
sys.path.insert(0, 'tools'); from ref_analysis import REFS, read; from firestats import flame_masks
out = {}
for k, r in REFS.items():
    rs = []
    for s in (0.5, 6.5, 12.5):
        fr = read(r['path'], s, 180, r['crop'])
        if len(fr) < 120: continue
        L, M = flame_masks(fr, None, r['thr'], r['warm']); reg = np.mean(M, 0) > 0.05
        Lf = np.stack([f.astype(np.float32).mean(2) for f in fr])
        d = np.abs(np.diff(Lf, axis=0))[:, reg].mean(1) / Lf[1:, reg].mean(1)
        # 30 fps-normalised (refs ~29.97): fine
        rs.append(dict(win=s, dF_mean=round(100 * float(d.mean()), 2), dF_p95=round(100 * float(np.percentile(d, 95)), 2), dF_max=round(100 * float(d.max()), 2),
                       area_px=int(reg.sum()))); print(k, rs[-1], flush=True)
    out[k] = rs
json.dump(out, open('ref/ref_dF_stats.json', 'x'), indent=1)
