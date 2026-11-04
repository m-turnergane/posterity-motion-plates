"""Flame motion statistics (shared by reference clips and the POC).
frames: list of HxWx3 uint8 RGB (a crop around the flame), fps, region: HxW bool where flame may be (None = whole crop),
flame pixels per frame = region & luminance above thr. All flow is computed after rescaling so the flame height is ~TARGET px."""
import numpy as np, cv2
from scipy import signal
TARGET = 200.0

def lumf(f): return (0.299 * f[..., 0] + 0.587 * f[..., 1] + 0.114 * f[..., 2]).astype(np.float32) / 255.0

def flame_masks(frames, region, thr, warm=None):
    L = [lumf(f) for f in frames]; R = np.ones(L[0].shape, bool) if region is None else region
    if warm is None: return L, [(l > thr) & R for l in L]
    return L, [(l > thr) & R & (((f[..., 0].astype(np.float32) - f[..., 2]) / 255.0 > warm) | (l > 0.9)) for l, f in zip(L, frames)]

def height_of(ms):
    hs = []
    for m in ms:
        ys = np.nonzero(m.any(1))[0]
        if len(ys) > 3:
            rows = m.sum(1); cs = np.cumsum(rows); tot = cs[-1]
            y5 = np.searchsorted(cs, 0.02 * tot); y95 = np.searchsorted(cs, 0.98 * tot); hs.append(y95 - y5 + 1)
    return float(np.median(hs)) if hs else 1.0

def stats(frames, fps, region=None, thr=0.55, bg=None, tip_frac=0.35, label="", warm=None):
    L, M = flame_masks(frames, region, thr, warm)
    Hf = height_of(M); sc = TARGET / Hf
    sz = (int(round(L[0].shape[1] * sc)), int(round(L[0].shape[0] * sc)))
    G = [cv2.resize(np.clip(l * 255, 0, 255).astype(np.uint8), sz, interpolation=cv2.INTER_CUBIC if sc > 1 else cv2.INTER_AREA) for l in L]
    Ms = [cv2.resize(m.astype(np.uint8), sz, interpolation=cv2.INTER_NEAREST).astype(bool) for m in M]
    BG = None if bg is None else cv2.resize(bg.astype(np.uint8), sz, interpolation=cv2.INTER_NEAREST).astype(bool)
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    absx, absy, upw, sway, rot, rise, mvx = [], [], [], [], [], [], []
    yy = np.mgrid[0:sz[1], 0:sz[0]][0].astype(np.float32)
    for a, b, m in zip(G[:-1], G[1:], Ms[:-1]):
        fl = dis.calc(a, b, None); vx, vy = fl[..., 0], fl[..., 1]
        if BG is not None and BG.any():   # remove camera motion
            vx = vx - np.median(vx[BG]); vy = vy - np.median(vy[BG])
        if m.sum() < 20: continue
        w = np.ones(m.sum(), np.float32); x_, y_ = vx[m], vy[m]
        absx.append(np.mean(np.abs(x_))); absy.append(np.mean(np.abs(y_)))
        mag = np.hypot(x_, y_) + 1e-6; upw.append(float(np.sum(mag * (y_ < 0)) / np.sum(mag)))
        mvx.append(float(np.mean(x_)))
        ys = yy[m]; yc = ys.mean(); A = np.stack([np.ones_like(ys), ys - yc], 1)
        coef, *_ = np.linalg.lstsq(A, x_, rcond=None); rot.append(float(coef[1]))
        top = ys < np.percentile(ys, 50)
        r_ = -y_[top]; rise.append(float(np.median(r_)))
    absx, absy, mvx = np.array(absx), np.array(absy), np.array(mvx)
    # structure advection: phase correlation of masked luminance in the upper half (lag 1 frame)
    am = np.mean(Ms, 0) > 0.1; rr = np.nonzero(am.any(1))[0]; cc = np.nonzero(am.any(0))[0]
    pr = []
    if len(rr) > 8:
        ya, yb = rr.min(), int(rr.min() + 0.55 * (rr.max() - rr.min())); xa, xb = cc.min(), cc.max() + 1
        win = cv2.createHanningWindow((xb - xa, yb - ya), cv2.CV_32F)
        for k in range(len(G) - 1):
            a = (G[k][ya:yb, xa:xb] * Ms[k][ya:yb, xa:xb]).astype(np.float32); b = (G[k + 1][ya:yb, xa:xb] * Ms[k + 1][ya:yb, xa:xb]).astype(np.float32)
            if a.sum() < 1 or b.sum() < 1: continue
            (dx, dy), resp = cv2.phaseCorrelate(a, b, win)
            if resp > 0.05: pr.append(-dy)
    pattern_rise = float(np.median(pr)) * fps / TARGET if pr else float('nan')
    # px/frame at TARGET scale -> flame heights per second
    rise_hps = float(np.median(rise)) * fps / TARGET
    # tip and body brightness series (original scale)
    allm = np.mean(M, 0) > 0.15
    rows = np.nonzero(allm.any(1))[0]
    y0, y1 = (rows.min(), rows.max()) if len(rows) else (0, L[0].shape[0] - 1)
    ytip = int(y0 + tip_frac * (y1 - y0)); ybody = int(y0 + 0.6 * (y1 - y0))
    tip = np.array([np.sum(l[y0:ytip] * m[y0:ytip]) for l, m in zip(L, M)]); body = np.array([np.sum(l[ybody:y1 + 1] * m[ybody:y1 + 1]) for l, m in zip(L, M)])
    def spec(s):
        s = s - s.mean(); s = signal.detrend(s)
        f, P = signal.welch(s, fs=fps, nperseg=min(len(s), 128), noverlap=min(len(s), 128) * 3 // 4)
        tot = P[f > 0.1].sum() + 1e-12
        bands = {"0.1-0.3": (0.1, 0.3), "0.3-0.6": (0.3, 0.6), "0.6-2": (0.6, 2), "2-5": (2, 5), "5-15": (5, 15)}
        out = {k: round(float(P[(f >= lo) & (f < hi)].sum() / tot), 3) for k, (lo, hi) in bands.items()}
        out["centroid_hz"] = round(float((f[f > 0.1] * P[f > 0.1]).sum() / tot), 2)
        return out, f, P
    tsp, ft, Pt = spec(tip.astype(float)); bsp, fb, Pb = spec(body.astype(float))
    tsp["cv"] = round(float(np.std(tip) / (np.mean(tip) + 1e-9)), 3); bsp["cv"] = round(float(np.std(body) / (np.mean(body) + 1e-9)), 3)
    # wisp detachment: bright components separated from the main body, above its centroid
    births = 0; prev = 0; counts = []
    amin = max(3, int(0.0006 * Hf * Hf))
    for m in M:
        n, lab, st, cen = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
        if n <= 1: counts.append(0); prev = 0; continue
        big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])); by = cen[big][1]; btop = st[big, cv2.CC_STAT_TOP]
        c = sum(1 for i in range(1, n) if i != big and st[i, cv2.CC_STAT_AREA] >= amin and cen[i][1] < by and st[i, cv2.CC_STAT_TOP + 0] + st[i, cv2.CC_STAT_HEIGHT] <= btop + 0.6 * (by - btop))
        counts.append(c); births += max(0, c - prev); prev = c
    dur = len(frames) / fps
    return dict(label=label, frames=len(frames), fps=round(fps, 3), flame_height_px=round(Hf, 1), flow_scale=round(sc, 3),
                vert_lat_ratio=round(float(absy.mean() / (absx.mean() + 1e-9)), 2), upward_fraction=round(float(np.mean(upw)), 3),
                mean_abs_vx_hps=round(float(absx.mean()) * fps / TARGET, 3), mean_abs_vy_hps=round(float(absy.mean()) * fps / TARGET, 3),
                global_sway_index=round(float(np.std(mvx) / (absx.mean() + 1e-9)), 3), rotation_shear_std=round(float(np.std(rot)), 5),
                rise_speed_heights_per_s=round(rise_hps, 2), pattern_rise_heights_per_s=round(pattern_rise, 2), tip_spectrum=tsp, body_spectrum=bsp,
                wisp_births_per_s=round(births / dur, 2), wisps_visible_mean=round(float(np.mean(counts)), 2))
