"""Remove baked pins / labels from a painted base map (inpaint) -> CLEAN geographic background. The original is never modified.
Method (classical CV, deterministic): inside each user-given box, mask = pixels that differ strongly from a large-median background estimate (glow, text, rays)
plus explicit extra regions (e.g. a label's dark scrim); dilate; cv2 inpaint (Telea) in a few passes; re-inject matched high-frequency grain so the patch is not smooth.
`detect_baked(img)` is the QC warning: counts pin-like bright saturated blobs and ivory text-like components; used by the cartography QC to warn when a recipe uses a base with baked text."""
import numpy as np, cv2

def _lowfreq_repair(img, area, sigma=7.0):
    """Replace the LOW-frequency component inside `area` (uint8 0/1) by a smooth interpolation from the surroundings, keeping the original texture (high frequencies).
    Removes soft scrims / glows without smearing the painting."""
    f = img.astype(np.float32); low = cv2.GaussianBlur(f, (0, 0), sigma); hi = f - low
    am = cv2.dilate(area, np.ones((5, 5), np.uint8)); target = cv2.inpaint(np.clip(low, 0, 255).astype(np.uint8), am, 9, cv2.INPAINT_TELEA).astype(np.float32)
    target = cv2.GaussianBlur(target, (0, 0), 3.0); w = cv2.GaussianBlur(area.astype(np.float32), (0, 0), 4.0)[..., None]; w = np.clip(w * 1.6, 0, 1)
    new = target + hi
    return np.clip(f * (1 - w) + new * w, 0, 255).astype(np.uint8)

def remove_items(img, items, seed=0, scrim=True):
    """items: list of dict(pin=[x,y,r_core], glow=R, rays=R_or_0, label=[x0,y0,x1,y1] or None).  Returns (clean BGR, debug mask).
    Masks are TIGHT (pin core + hot glow pixels, thin ray / text strokes found by a top-hat filter) so Telea only has thin structures to fill; then the soft
    dark label scrim / pin halo is flattened by a mild local gain correction (low-frequency luminance only, bounded). Known limit: faint residual smudges
    can remain where a label sat on a coastline - check at 100% and prefer regenerating a clean map for production."""
    H, W = img.shape[:2]; hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV); g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    th = g - cv2.GaussianBlur(g, (0, 0), 3.0)
    mask = np.zeros((H, W), np.uint8); yy, xx = np.mgrid[0:H, 0:W]; halo = np.zeros((H, W), np.float32)
    for it in items:
        if it.get("pin"):
            x, y, r = it["pin"]; d = np.hypot(xx - x, yy - y); glow = it.get("glow", 30)
            hot = (d < glow) & (hsv[..., 2] > 200) & (hsv[..., 1] > 100) & (hsv[..., 0] < 32); core = (d < r + 4); white = (d < glow) & (g > 238)
            mask |= (hot | core | white).astype(np.uint8)
            if it.get("rays"): mask |= ((d < it["rays"]) & (th > 14) & (g > 170)).astype(np.uint8)
            halo = np.maximum(halo, np.clip(1 - d / (glow * 1.6), 0, 1))
        if it.get("label"):
            x0, y0, x1, y1 = it["label"]; sub = np.zeros((H, W), bool); sub[y0:y1, x0:x1] = True
            st = (sub & (th > 22) & (g > 165) & (hsv[..., 1] < 140)).astype(np.uint8)
            n, lab, stt, _ = cv2.connectedComponentsWithStats(cv2.dilate(st, np.ones((3, 3), np.uint8)))      # letters are small components; long bright coast outlines are kept
            keep = np.zeros(n, bool)
            for i in range(1, n):
                if stt[i, 2] <= 150 and stt[i, 3] <= 24: keep[i] = True
            mask |= (keep[lab] & (st > 0)).astype(np.uint8)
    mask = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    cur = cv2.inpaint(img, mask, 4, cv2.INPAINT_TELEA)
    sm = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), 2.0)[..., None]; cur = np.clip(cur * (1 - sm) + cv2.GaussianBlur(cur, (0, 0), 1.4) * sm, 0, 255).astype(np.uint8)   # kills Telea speckle
    if scrim:
        cf = cur.astype(np.float32); lowc = cv2.GaussianBlur(cf, (0, 0), 4.0)
        def equalize(sel, ring, lo, hi, sigma):
            """per-channel gain so the median colour inside `sel` matches the surrounding ring (bounded), feathered."""
            nonlocal cf
            ref = np.median(lowc[ring], axis=0); inn = np.median(lowc[sel], axis=0); gain = np.clip(ref / np.maximum(inn, 1), lo, hi)
            bl = cv2.GaussianBlur(sel.astype(np.float32), (0, 0), sigma)[..., None]; cf = cf * (1 + (gain[None, None, :] - 1) * bl)
        for it in items:
            if it.get("pin"):
                x, y, r = it["pin"]; d = np.hypot(xx - x, yy - y); gl = it.get("glow", 30)
                equalize(d < gl * 1.15, (d > gl * 1.5) & (d < gl * 2.2), 0.7, 1.45, 6.0)
            if it.get("label"):
                x0, y0, x1, y1 = it["label"]; sel = np.zeros((H, W), bool); sel[y0:y1, x0:x1] = True
                ring = np.zeros((H, W), bool); ring[max(y0 - 16, 0):y1 + 16, max(x0 - 16, 0):x1 + 16] = True; ring[max(y0 - 6, 0):y1 + 6, max(x0 - 6, 0):x1 + 6] = False
                equalize(sel, ring, 0.8, 1.5, 5.0)
        cur = np.clip(cf, 0, 255).astype(np.uint8)
    rng = np.random.default_rng(seed); ring = cv2.dilate(mask, np.ones((41, 41), np.uint8)) & (1 - cv2.dilate(mask, np.ones((9, 9), np.uint8)))
    f = img.astype(np.float32); hp = (f - cv2.GaussianBlur(f, (0, 0), 1.6)).mean(axis=2); sd = float(np.median(np.abs(hp[ring > 0])) * 1.48) if ring.any() else 2.0
    n = cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), 0.7); n *= 0.5 * sd / (n.std() + 1e-6); soft = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), 1.2)
    out = np.clip(cur.astype(np.float32) + (n * soft)[..., None], 0, 255).astype(np.uint8)
    return out, mask * 255

def detect_baked(img):
    """-> dict(pins, text_components, score). Heuristic WARNING only (never proof): a baked pin = compact near-white core ringed by saturated orange glow;
    baked label = a short wide run of ivory strokes on a darkened scrim (word-like component, 8-24 px high) whose surrounding ring is darker than the strokes."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV); g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY); H, W = g.shape
    core = ((hsv[..., 2] > 244) & (hsv[..., 1] < 45)).astype(np.uint8); n, lab, st, cen = cv2.connectedComponentsWithStats(core); pins = 0
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if not (6 <= w <= 40 and 6 <= h <= 40 and 0.6 <= w / h <= 1.6 and a / (w * h) > 0.5): continue
        cx, cy = cen[i]; yy, xx = np.ogrid[:H, :W]; d = np.hypot(xx - cx, yy - cy); r = max(w, h) / 2
        ring = (d > r + 2) & (d < r + 8) & (np.abs(xx - cx) < 60) & (np.abs(yy - cy) < 60); hv = hsv[ring]
        if len(hv) and ((hv[:, 1] > 150) & (hv[:, 2] > 190) & (hv[:, 0] < 32)).mean() > 0.5: pins += 1
    bright = ((g > 215) & (hsv[..., 1] < 80)).astype(np.uint8); cl = cv2.morphologyEx(bright, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (7, 3)))
    n2, lab2, st2, _ = cv2.connectedComponentsWithStats(cl); words = 0
    for x, y, w, h, a in st2[1:]:
        if not (40 <= w <= 200 and 9 <= h <= 24 and w / h >= 3.0 and 0.25 < a / (w * h) < 0.8): continue
        inner = g[y:y + h, x:x + w].astype(np.float32); ring = np.zeros((H, W), bool); ring[max(y - 8, 0):y + h + 8, max(x - 8, 0):x + w + 8] = True; ring[y:y + h, x:x + w] = False
        if np.percentile(inner, 95) - np.median(g[ring]) > 90 and np.median(g[ring]) < 150: words += 1
    return dict(pins=pins, text_components=words, score=pins + words)
