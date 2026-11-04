#!/workspace/mpvenv/bin/python
"""B03: Lanczos-upscale the CLEAN plate to 1080x1920 (cover), register to refpack_bathory v2 (ref_notext_v2 + CPs) via river-ink NCC per CP,
fit affine (+ TPS if needed), report residuals, write the registered plate + reg json. Never touches source files."""
import json, numpy as np, cv2
from pathlib import Path
from PIL import Image
RP = Path('/workspace/posterity/engine-rnd/maps/atlas/refpack_bathory'); OUT = Path(__file__).resolve().parent
PLATE = Path('/workspace/posterity/standalones/bathory/v2/plates/b03_atlas_upper_hungary_CLEAN.png')
W, H = 1080, 1920
im = Image.open(PLATE).convert('RGB'); sw, sh = im.size; sc = max(W / sw, H / sh)
nw, nh = int(np.ceil(sw * sc)), int(np.ceil(sh * sc)); up = im.resize((nw, nh), Image.Resampling.LANCZOS)
l, t = (nw - W) // 2, (nh - H) // 2; up = np.asarray(up.crop((l, t, l + W, t + H))).astype(np.float32)
ref = np.asarray(Image.open(RP / 'img_v2/bathory_b03v2_9x16_ref_notext_v2.png').convert('RGB')).astype(np.float32)
def rivmask(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = np.clip(((b - r) - 8) / 30, 0, 1)
    m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.5)
    # tiny fixed noise: stops TM_CCOEFF_NORMED returning 1.0 on zero-variance (river-free) windows
    return m + np.random.default_rng(7).normal(0, 0.01, m.shape).astype(np.float32)
mp, mr = rivmask(up), rivmask(ref)
cps = json.load(open(RP / 'control_points_refpack_bathory_v2.json'))['control_points']
R, S = 28, 40   # half window (56x56), search radius
res = []
for c in cps:
    if c['role'] != 'primary': continue
    x, y = c['px']; xi, yi = int(round(x)), int(round(y))
    if not (R <= xi < W - R and R <= yi < H - R): res.append(dict(id=c['id'], name=c['name'], ok=False, why='edge')); continue
    tpl = mr[yi - R:yi + R, xi - R:xi + R]
    if tpl.std() < 0.02: res.append(dict(id=c['id'], name=c['name'], ok=False, why='flat ref')); continue
    y0, y1, x0, x1 = max(0, yi - R - S), min(H, yi + R + S), max(0, xi - R - S), min(W, xi + R + S)
    srch = mp[y0:y1, x0:x1]
    r = cv2.matchTemplate(srch, tpl, cv2.TM_CCOEFF_NORMED); _, mx, _, loc = cv2.minMaxLoc(r)
    # subpixel refine
    lx, ly = loc
    def sub(v, i, n):
        if 0 < i < n - 1:
            a, b, cc = v[i - 1], v[i], v[i + 1]; d = a - 2 * b + cc
            return i + (0.5 * (a - cc) / d if abs(d) > 1e-9 else 0)
        return i
    sx = sub(r[ly, :], lx, r.shape[1]); sy = sub(r[:, lx], ly, r.shape[0])
    px = x0 + sx + R; py = y0 + sy + R   # plate position matching the ref CP (xi,yi)
    px += x - xi; py += y - yi
    res.append(dict(id=c['id'], name=c['name'], ref=[x, y], plate=[round(float(px), 2), round(float(py), 2)], ncc=round(float(mx), 3), ok=bool(mx >= 0.6)))
    res[-1]["plate"] = [float(v) for v in res[-1]["plate"]]
acc = [r for r in res if r.get('ok')]
P = np.array([r['plate'] for r in acc]); Q = np.array([r['ref'] for r in acc])
raw = np.linalg.norm(P - Q, axis=1)
# affine plate->ref, LOO rejection of > 12 px
keep = np.ones(len(acc), bool)
for _ in range(10):
    A, _ = cv2.estimateAffine2D(P[keep], Q[keep], method=cv2.LMEDS)
    pr = (np.c_[P, np.ones(len(P))] @ A.T); e = np.linalg.norm(pr - Q, axis=1)
    if e[keep].max() <= 12: break
    keep[np.argmax(np.where(keep, e, -1))] = False
for r, ee, rr, k in zip(acc, e, raw, keep): r.update(raw_px=round(float(rr), 2), affine_resid_px=round(float(ee), 2), used=bool(k))
# QA: residual of each accepted CP AFTER warping (affine): re-measure by NCC on the warped plate
warped = cv2.warpAffine(up, A, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
mw = rivmask(warped); post = []
for c in cps:
    if c['role'] != 'primary': continue
    x, y = c['px']; xi, yi = int(round(x)), int(round(y))
    if not (R <= xi < W - R and R <= yi < H - R): continue
    tpl = mr[yi - R:yi + R, xi - R:xi + R]
    if tpl.std() < 0.02: continue
    y0, y1, x0, x1 = max(0, yi - R - S), min(H, yi + R + S), max(0, xi - R - S), min(W, xi + R + S)
    r = cv2.matchTemplate(mw[y0:y1, x0:x1], tpl, cv2.TM_CCOEFF_NORMED); _, mx, _, loc = cv2.minMaxLoc(r)
    if mx < 0.6: continue
    dx, dy = x0 + loc[0] + R - xi, y0 + loc[1] + R - yi; post.append(dict(id=c['id'], resid_px=round(float(np.hypot(dx, dy)), 2), ncc=round(float(mx), 3)))
pv = np.array([p['resid_px'] for p in post])
stat = dict(n_primary=sum(1 for c in cps if c['role'] == 'primary'), n_accepted=len(acc), n_used=int(keep.sum()), affine=A.tolist(),
            scale=float(np.sqrt(abs(np.linalg.det(A[:, :2])))), shift_px=[float(A[0, 2]), float(A[1, 2])],
            raw_median=float(np.median(raw)), raw_max=float(raw.max()),
            post_median=float(np.median(pv)), post_p95=float(np.percentile(pv, 95)), post_max=float(pv.max()),
            n_pass_4px=int((pv <= 4).sum()), n_flag_8px=int(((pv > 4) & (pv <= 8)).sum()), n_fail=int((pv > 8).sum()))
# Váh chamfer: ref Váh ridge vs plate river ridge (distance transform)
refv = (mr > 0.5).astype(np.uint8); plv = (mw > 0.5).astype(np.uint8)
dt = cv2.distanceTransform(1 - plv, cv2.DIST_L2, 5); d = dt[refv > 0]
stat.update(chamfer_median=float(np.median(d)), chamfer_p95=float(np.percentile(d, 95)))
json.dump(dict(stat=stat, cps=res, post=post), open(OUT / 'b03_registration.json', 'w'), indent=1)
Image.fromarray(np.clip(warped, 0, 255).astype(np.uint8)).save(OUT / 'b03_registered_1080x1920.png')
print(json.dumps(stat, indent=1)); print([ (r['id'], r.get('ncc'), r.get('raw_px'), r.get('affine_resid_px')) for r in res])
