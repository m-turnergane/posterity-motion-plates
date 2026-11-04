"""Perceived-motion metrics on the temporally high-passed flame signal (static paint removed), same for reference and POC.
hp = L - centred moving average (9 frames). Rescaled so flame height = 100 px.
 hp_rise_hps   : median vertical shift between consecutive hp frames (phase correlation), flame heights / s (positive = up)
 hp_lat_hps    : median |horizontal shift| (heights/s) ; hp_vl = rise / lateral
 hp_energy     : std(hp)/mean(L) inside region (how much the fire 'moves' in brightness terms)
 decorr_s      : time for the normalised hp autocorrelation to fall below 0.5 (pattern lifetime)
 corr_1s_max   : max normalised correlation of hp frames at lags 0.5..3 s (loop / repetition detector)"""
import numpy as np, cv2
def lum(f): return (0.299 * f[..., 0] + 0.587 * f[..., 1] + 0.114 * f[..., 2]).astype(np.float32) / 255.0
def hp_metrics(frames, fps, region, Hf, top_frac=None):
    L = np.stack([lum(f) for f in frames]); n = len(L); k = 4
    cs = np.cumsum(np.pad(L, ((1, 0), (0, 0), (0, 0))), 0)
    ma = np.stack([(cs[min(n, i + k + 1)] - cs[max(0, i - k)]) / (min(n, i + k + 1) - max(0, i - k)) for i in range(n)])
    H = (L - ma)[k:n - k]; Lm = L[k:n - k]
    reg = region.copy()
    if top_frac is not None:
        rr = np.nonzero(reg.any(1))[0]; reg[int(rr.min() + top_frac * (rr.max() - rr.min())):] = False
    ys, xs = np.nonzero(reg); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    sc = 100.0 / Hf; sz = (max(8, int(round((x1 - x0) * sc))), max(8, int(round((y1 - y0) * sc))))
    R = cv2.resize(reg[y0:y1, x0:x1].astype(np.float32), sz, interpolation=cv2.INTER_AREA)
    Hs = [cv2.resize(h[y0:y1, x0:x1], sz, interpolation=cv2.INTER_AREA) * R for h in H]
    win = cv2.createHanningWindow(sz, cv2.CV_32F)
    dys, dxs = [], []
    for a, b in zip(Hs[:-1], Hs[1:]):
        (dx, dy), resp = cv2.phaseCorrelate(a.astype(np.float32), b.astype(np.float32), win)
        if resp > 0.03: dys.append(-dy); dxs.append(abs(dx))
    m = reg[None]
    energy = float(np.std(H[:, reg]) / (Lm[:, reg].mean() + 1e-9))
    V = np.stack([h[reg] for h in H]); V = V - V.mean(1, keepdims=True); nv = np.linalg.norm(V, axis=1) + 1e-9
    def corr(l): return float(np.mean([(V[i] @ V[i + l]) / (nv[i] * nv[i + l]) for i in range(0, len(V) - l)]))
    ac = [corr(l) for l in range(1, min(30, len(V) - 1))]
    dec = next((l for l, c in enumerate(ac, 1) if c < 0.5), len(ac)) / fps; ac1 = ac[0]; ac3 = ac[2]
    lags = [int(round(s * fps)) for s in np.arange(0.5, 3.01, 1 / fps * 3) if int(round(s * fps)) < len(V) - 10]
    cmax = max(corr(l) for l in lags) if lags else float('nan')
    rise = float(np.median(dys)) * fps / 100 if dys else float('nan'); lat = float(np.median(dxs)) * fps / 100 if dxs else float('nan')
    return dict(hp_rise_hps=round(rise, 3), hp_lat_hps=round(lat, 3), hp_vl=round(abs(rise) / (lat + 1e-6), 2), hp_energy=round(energy, 4),
                decorr_s=round(dec, 3), ac1=round(ac1, 3), ac3=round(ac3, 3), corr_0p5to3s_max=round(cmax, 3), n_pairs=len(dys))
