#!/workspace/mpvenv/bin/python
"""P01+P02 collision check / smallest-nudge search for intro v2 (Chronicle Reveal at anchor f174, carried across the f100 cut).
Obstacles per frame where the title is visible: YuNet faces (both plates, +8 px guard); P02 lid-gap candle glint (luma > 150 components >= 20 px,
upper 700 px, +8 px guard); P02 key subject (braid / pommel / hand / sword: below the lid-gap line, box from frame analysis); P01 coffin-lid glint; captions.
Overlay masks are built at topPercent 16 and shifted rigidly by dy px (topPercent = 16 + dy / 19.2)."""
import sys, json, subprocess, importlib.util
from pathlib import Path
import numpy as np, cv2
sys.argv = [sys.argv[0], 'lib']; ROOT = Path('/workspace/posterity'); R3 = ROOT / 'standalones/bjorn/rough_v3'
s = importlib.util.spec_from_file_location('iv', str(R3 / 'build/intro_v3b.py')); IV = importlib.util.module_from_spec(s); s.loader.exec_module(IV)
s = importlib.util.spec_from_file_location('sn', str(ROOT / 'engine-rnd/snow/snow_v1b.py')); SN = importlib.util.module_from_spec(s); s.loader.exec_module(SN)
H, W = 1920, 1080; G = 8; K = np.ones((2 * G + 1, 2 * G + 1), np.uint8)
M = IV.masks(0, 200); vis = sorted(M); print('title visible frames', vis[0], vis[-1], flush=True)
A = IV.decode(IV.V2B, 200)
obst = {}; info = {}; RAW = {}
for f in vis:
    o = np.zeros((H, W), np.uint8); fr = A[f]; tags = []; raw = np.zeros((H, W), np.uint8)
    for x, y, w, h, sc in SN.detect_faces(fr, 0.6):
        if f >= 100: tags.append(('yunet_false_positive_P02', [int(x), int(y), int(x + w), int(y + h)])); continue   # P02 = hand/sword/coffin, no faces (v2 plate face pass: 0); YuNet fires on lid/ring-handle texture
        cv2.rectangle(raw, (int(x), int(y)), (int(x + w), int(y + h)), 1, -1)
        cv2.rectangle(o, (int(x) - G, int(y) - G), (int(x + w) + G, int(y + h) + G), 1, -1); tags.append(('face', [int(x), int(y), int(x + w), int(y + h)]))
    l = fr.astype(np.float32) @ np.array([.299, .587, .114], np.float32)
    if f >= 100:   # P02 lid-gap glint
        m = ((l > 150) & (np.arange(H)[:, None] < 700)).astype(np.uint8); n, lab, st, _ = cv2.connectedComponentsWithStats(m)
        g = np.isin(lab, [i for i in range(1, n) if st[i, 4] >= 20]).astype(np.uint8); ys, xs = np.nonzero(g)
        tags.append(('glint', [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())])); o |= cv2.dilate(g, K); raw |= g
    else:          # P01 coffin-lid glint (as QA v1)
        l2 = cv2.GaussianBlur(np.where((np.arange(H)[:, None] >= 620) & (np.arange(H)[:, None] < 900), l, 0), (0, 0), 6); yy, xx = np.unravel_index(np.argmax(l2), l2.shape)
        ys, xs = np.nonzero(l2 > l2[yy, xx] * 0.85); b = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]; tags.append(('glint', b)); cv2.rectangle(raw, (b[0], b[1]), (b[2], b[3]), 1, -1); cv2.rectangle(o, (b[0] - G, b[1] - G), (b[2] + G, b[3] + G), 1, -1)
    obst[f] = o.astype(bool); info[f] = tags; RAW[f] = cv2.distanceTransform((1 - raw).astype(np.uint8), cv2.DIST_L2, 5)
def hits(dy):
    r = {}
    for f in vis:
        m = np.roll(M[f], dy, axis=0); n = int((m & obst[f]).sum())
        if n: r[f] = n
    return r
h0 = hits(0); res = dict(visible=[vis[0], vis[-1]], at16=dict(frames_hit=len(h0), first_last=[min(h0), max(h0)] if h0 else None, px_max=max(h0.values()) if h0 else 0))
best = {}
for sgn in (-1, 1):
    for k in range(0, 200 if sgn < 0 else 400):
        dy = sgn * k
        if not hits(dy): best[sgn] = dy; break
res['clear_dy_up'] = best.get(-1); res['clear_dy_down'] = best.get(1)
for k in ('clear_dy_up', 'clear_dy_down'):
    if res[k] is not None: res[k + '_top_pct'] = round(16 + res[k] / 19.2, 3)
def gaps(dy):
    g1 = min(float(RAW[f][np.roll(M[f], dy, axis=0)].min()) for f in vis if f < 100); g2 = min(float(RAW[f][np.roll(M[f], dy, axis=0)].min()) for f in vis if f >= 100)
    return dict(P01_min_gap_px=round(g1, 1), P02_min_gap_px=round(g2, 1))
res['gaps_at16'] = gaps(0)
if res['clear_dy_up'] is not None: res['gaps_at_clear_up'] = gaps(res['clear_dy_up'])
res['fp_frames'] = {f: [t for t in info[f] if t[0].startswith('yunet')] for f in vis if any(t[0].startswith('yunet') for t in info[f])}
# gap report at chosen dy (smallest |dy|): min vertical distance from overlay to each obstacle class
res['obstacles_sample'] = {f: info[f] for f in (vis[0], 55, 99, 100, 142, 171) if f in info}
json.dump(res, open(R3 / 'logs/intro_v3b_search.json', 'w'), indent=1, default=str); print(json.dumps(res, default=str))
