"""Layer stacks: polygon (+optional GrabCut) masks -> depth layers, alpha elements, clean background plate."""
import os, time, json
import cv2, numpy as np
from .util import polygon_mask

def _grow(m, px):
    if px == 0:
        return m
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * abs(px) + 1,) * 2)
    return cv2.dilate(m, k) if px > 0 else cv2.erode(m, k)

def refine_grabcut(img_rgb, poly_mask, band=8, iters=4):
    """Edge-aware refinement inside a band around a hand-authored polygon (outside band = fixed)."""
    bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    hard = (poly_mask > 0.5).astype(np.uint8)
    sure_fg = _grow(hard, -band); sure_bg = 1 - _grow(hard, band)
    gc = np.full(hard.shape, cv2.GC_PR_BGD, np.uint8)
    gc[hard > 0] = cv2.GC_PR_FGD; gc[sure_fg > 0] = cv2.GC_FGD; gc[sure_bg > 0] = cv2.GC_BGD
    ys, xs = np.where((hard > 0) | (_grow(hard, band) > 0)); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    sub = bgr[y0:y1, x0:x1].copy(); g = gc[y0:y1, x0:x1].copy()
    bg = np.zeros((1, 65)); fg = np.zeros((1, 65))
    cv2.setRNGSeed(1234)  # GrabCut k-means uses the global cv RNG: pin for reproducibility
    cv2.grabCut(sub, g, None, bg, fg, iters, cv2.GC_INIT_WITH_MASK)
    out = np.zeros_like(hard); out[y0:y1, x0:x1] = ((g == 1) | (g == 3)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(out)
    if n > 2:  # keep components that are large
        keep = np.zeros_like(out)
        for i in range(1, n):
            if st[i, 4] > 0.02 * st[1:, 4].sum() or (lab[(sure_fg > 0)] == i).any():
                keep[lab == i] = 1
        out = keep
    out = cv2.morphologyEx(out, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return out.astype(np.float32)

def inpaint(img_rgb, hole, scale=0.25, radius=5, band_px=30):
    """Two-stage TELEA fill: coarse fill of the whole hole at reduced scale (deep interior is never revealed), then a full-resolution
    TELEA pass over a `band_px` ring next to the known pixels (this ring is what parallax actually reveals)."""
    h = (hole > 0.5).astype(np.uint8)
    if h.sum() == 0:
        return img_rgb.copy()
    H, W = h.shape; sw, sh = max(int(W * scale), 8), max(int(H * scale), 8)
    small = cv2.resize(img_rgb, (sw, sh), interpolation=cv2.INTER_AREA)
    hs = cv2.resize(h, (sw, sh), interpolation=cv2.INTER_NEAREST); hs = _grow(hs, 1)
    filled = cv2.inpaint(small, hs, radius, cv2.INPAINT_TELEA)
    up = cv2.resize(filled, (W, H), interpolation=cv2.INTER_CUBIC)
    work = img_rgb.copy(); work[h > 0] = up[h > 0]
    dist = cv2.distanceTransform(h, cv2.DIST_L2, 3)
    band = ((h > 0) & (dist <= band_px)).astype(np.uint8)
    out = cv2.inpaint(np.ascontiguousarray(work), band, radius, cv2.INPAINT_TELEA)
    res = work.copy(); res[band > 0] = out[band > 0]
    return res

def push_pull_fill(img, hole, exclude=None, noise=1.2, seed=1, texture=1.0, ring_px=26, luma_min=0):
    """Smooth diffusion fill (pyramid push-pull) using only valid surrounding pixels (hole & exclude pixels carry no weight).
    Good for smoky/defocused backgrounds where TELEA smears neighbouring skin/gold colour into the hole."""
    h = (hole > 0.5)
    valid = (~h) if exclude is None else (~h) & (exclude < 0.5)
    if ring_px:   # only sample a ring around the hole (no far-away colours) and optionally only bright haze pixels
        near = cv2.dilate(h.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * ring_px + 1,) * 2)) > 0
        valid = valid & near
    if luma_min: valid = valid & (img.astype(np.float32).mean(2) >= luma_min)
    w0 = valid.astype(np.float32); I0 = img.astype(np.float32) * w0[..., None]
    lv = [(I0, w0)]
    while min(lv[-1][1].shape) > 6:
        I, w = lv[-1]; lv.append((cv2.pyrDown(I), cv2.pyrDown(w)))
    I, w = lv[-1]; out = I / np.maximum(w, 1e-4)[..., None]
    for I, w in reversed(lv[:-1]):
        up = cv2.resize(out, (I.shape[1], I.shape[0]), interpolation=cv2.INTER_LINEAR)
        a = np.clip(w * 2.0, 0, 1)[..., None]; out = a * (I / np.maximum(w, 1e-4)[..., None]) + (1 - a) * up
    res = img.astype(np.float32).copy()
    if texture:   # fractal haze texture with the amplitude/colour statistics of the surrounding valid smoke, so fills are not plastic
        hu = h.astype(np.uint8); ring = valid
        f = img.astype(np.float32); hp = f - cv2.GaussianBlur(f, (0, 0), 7.0); sd = float(hp[ring].std()) if ring.any() else 3.0
        rng = np.random.default_rng(seed + 11); n = np.zeros(h.shape, np.float32)
        for sg, wt in ((2.5, 0.5), (6, 1.0), (14, 1.2), (30, 0.9)):
            g = cv2.GaussianBlur(rng.standard_normal(h.shape).astype(np.float32), (0, 0), sg); n += wt * g / (g.std() + 1e-6)
        n /= (n.std() + 1e-6); out = out + (n * sd * texture)[..., None] * np.array([1.0, 0.92, 0.8], np.float32)
    if noise:
        rng = np.random.default_rng(seed); n = cv2.GaussianBlur(rng.standard_normal(h.shape).astype(np.float32), (0, 0), 1.0) * noise * 2.2
        out = out + n[..., None]
    res[h] = out[h]
    return res

def smooth_quilt_fill(img, hole, exclude=None, luma_min=0, sigmas=(10, 30, 90), tile=20, seed=5, texture=1.0, mode='quilt', erode=None):
    """Clean-plate fill for smoky/defocused areas: (1) smooth base from normalised Gaussian convolution of valid haze pixels only
    (no facets, no skin/gold bleed), (2) real high-frequency haze texture quilted in from valid pixels near the hole (Hann-windowed tiles
    chosen by matching local brightness). Deterministic (seeded)."""
    f = img.astype(np.float32); h = hole > 0.5
    valid = (~h)
    if exclude is not None: valid &= exclude < 0.5
    valid &= f.mean(2) >= luma_min
    w0 = valid.astype(np.float32)
    # ensure coarse fallback fills deep interior: iterate from coarse to fine
    est_list = []
    for sg in sigmas:
        num = cv2.GaussianBlur(f * w0[..., None], (0, 0), sg); den = cv2.GaussianBlur(w0, (0, 0), sg)[..., None]
        est_list.append((num / np.maximum(den, 1e-6), np.clip(den / 0.12, 0, 1)))
    base = est_list[-1][0]
    for est, a in reversed(est_list[:-1]): base = est * a + base * (1 - a)
    out = f.copy()
    if texture and mode == 'noise':
        lp = cv2.GaussianBlur(f, (0, 0), 3.5); hp = f - lp; sd = float(hp[valid & (cv2.dilate(h.astype(np.uint8), np.ones((81, 81), np.uint8)) > 0)].std())
        rng = np.random.default_rng(seed); n = np.zeros(h.shape, np.float32)
        for sg, wt in ((1.5, 0.5), (4, 1.0), (10, 1.0), (24, 0.8)):
            g = cv2.GaussianBlur(rng.standard_normal(h.shape).astype(np.float32), (0, 0), sg); n += wt * g / (g.std() + 1e-6)
        base = base + (n / (n.std() + 1e-6) * sd * texture)[..., None] * np.array([1.0, 0.92, 0.8], np.float32)
    elif texture:
        lp = cv2.GaussianBlur(f, (0, 0), 3.5); hp = f - lp
        rng = np.random.default_rng(seed); H, W = h.shape
        near = cv2.dilate(h.astype(np.uint8), np.ones((121, 121), np.uint8)) > 0
        vm = (cv2.erode(valid.astype(np.uint8), np.ones((erode or tile, erode or tile), np.uint8)) > 0) & near
        ys, xs = np.where(vm); cand = np.stack([ys, xs], 1)
        if len(cand) > 4000: cand = cand[rng.choice(len(cand), 4000, replace=False)]
        cl = np.array([lp[y, x].mean() for y, x in cand]) if len(cand) else None
        win = np.outer(np.hanning(tile + 2)[1:-1], np.hanning(tile + 2)[1:-1]).astype(np.float32)[..., None]
        acc = np.zeros_like(f); wsum = np.zeros((H, W, 1), np.float32); hy, hx = np.where(h)
        if len(hy) and cl is not None:
            for ty in range(hy.min() - tile // 2, hy.max() + tile, tile // 2):
                for tx in range(hx.min() - tile // 2, hx.max() + tile, tile // 2):
                    y0, x0 = ty, tx; y1, x1 = y0 + tile, x0 + tile
                    if y0 < 0 or x0 < 0 or y1 > H or x1 > W or not h[y0:y1, x0:x1].any(): continue
                    tb = base[y0 + tile // 2, x0 + tile // 2].mean(); order = np.argsort(np.abs(cl - tb))[:25]
                    sy, sx = cand[order[rng.integers(len(order))]]
                    acc[y0:y1, x0:x1] += hp[sy:sy + tile, sx:sx + tile] * win; wsum[y0:y1, x0:x1] += win
        base = base + texture * acc / np.maximum(wsum, 1e-3) * (wsum > 0.05)
    m = cv2.GaussianBlur(h.astype(np.float32), (0, 0), 1.2)[..., None]
    out = f * (1 - m) + base * m
    return np.clip(out, 0, 255)

def detect_specks(img_rgb, region_polys, delta=26, max_area=90, shape=None):
    """Small bright blobs (frozen sparkles / bokeh specks) inside region polygons -> uint8 mask (for clean-plate removal)."""
    H, W = img_rgb.shape[:2]; reg = np.zeros((H, W), np.uint8)
    for p in region_polys: cv2.fillPoly(reg, [np.array(p, np.int32)], 1)
    g = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY).astype(np.float32); med = cv2.medianBlur(g.astype(np.uint8), 21).astype(np.float32)
    b = ((g - med > delta) & (reg > 0)).astype(np.uint8); n, lab, st, _ = cv2.connectedComponentsWithStats(b)
    out = np.zeros((H, W), np.uint8)
    for i in range(1, n):
        if st[i, 4] <= max_area: out[lab == i] = 1
    return cv2.dilate(out, np.ones((5, 5), np.uint8))

class Layer:
    def __init__(self, name, rgb, alpha, depth, kind="layer"):
        self.name, self.rgb, self.alpha, self.depth, self.kind = name, rgb, alpha, depth, kind  # rgb float32 HxWx3 0..255

class LayerStack:
    def __init__(self, base_rgb):
        self.base = base_rgb; self.layers = []; self.masks = {}; self.timings = {}; self.clean_plate = None

    def by_name(self, n):
        return next(l for l in self.layers if l.name == n)

def build_stack(base_rgb, spec, extra_holes=None, log=print):
    """spec: {layers:[{name,depth,polygons,refine,grow,feather}], elements:[{name,polygons,grow,feather,depth}]}
    layers are listed back->front. `extra_holes`: uint8 mask of removed objects (e.g. petals) inpainted in the clean plate first."""
    H, W = base_rgb.shape[:2]; st = LayerStack(base_rgb); T = {}
    t0 = time.time()
    clean = base_rgb
    cp = spec.get("clean_plate", {}) or {}
    if extra_holes is not None and extra_holes.any():
        holes = extra_holes.copy()
        if cp.get("speck_regions"):
            holes |= detect_specks(base_rgb, cp["speck_regions"], **cp.get("speck_params", {}))
        holes = cv2.dilate(holes, np.ones((2 * cp.get("hole_grow", 3) + 1,) * 2, np.uint8))
        if cp.get("method") == "telea_exclude":
            ex = np.zeros(holes.shape, np.uint8)
            for pp in cp.get("exclude", []): cv2.fillPoly(ex, [np.array(pp, np.int32)], 1)
            aug = (holes | cv2.dilate(ex, np.ones((5, 5), np.uint8))).astype(np.uint8)
            filled = cv2.inpaint(np.ascontiguousarray(base_rgb), aug, cp.get("radius", 9), cv2.INPAINT_TELEA).astype(np.float32)
            tx = cp.get("texture", 0.0)
            if tx:
                f = base_rgb.astype(np.float32); valid = (aug == 0); hp = f - cv2.GaussianBlur(f, (0, 0), 7.0)
                ringm = (cv2.dilate(aug, np.ones((61, 61), np.uint8)) > 0) & valid; sd = float(hp[ringm].std())
                rng = np.random.default_rng(3); n = np.zeros(holes.shape, np.float32)
                for sg, wt in ((2.0, 0.6), (5, 1.0), (12, 1.0)):
                    g = cv2.GaussianBlur(rng.standard_normal(holes.shape).astype(np.float32), (0, 0), sg); n += wt * g / (g.std() + 1e-6)
                n /= n.std() + 1e-6; filled += (n * sd * tx)[..., None] * np.array([1.0, 0.92, 0.8], np.float32)
            clean = base_rgb.copy(); hm = holes > 0; clean[hm] = np.clip(filled[hm], 0, 255).astype(np.uint8)
        elif cp.get("method") == "smooth_quilt":
            ex = np.zeros(holes.shape, np.float32)
            for pp in cp.get("exclude", []): cv2.fillPoly(ex, [np.array(pp, np.int32)], 1.0)
            ex = cv2.dilate(ex, np.ones((7, 7), np.uint8))
            clean = smooth_quilt_fill(base_rgb, holes, ex, **cp.get("fill_params", {})).astype(np.uint8)
        elif cp.get("method", "pushpull") == "pushpull":
            ex = np.zeros(holes.shape, np.float32)
            for pp in cp.get("exclude", []): cv2.fillPoly(ex, [np.array(pp, np.int32)], 1.0)
            clean = np.clip(push_pull_fill(base_rgb, holes, ex, **cp.get('fill_params', {})), 0, 255).astype(np.uint8)
        else:
            clean = inpaint(base_rgb, holes, scale=1.0, radius=6)
        st.clean_holes = holes
        st.clean_plate_petals = clean
    T["clean_plate_inpaint_s"] = time.time() - t0
    st.clean_plate = clean
    cl = clean.astype(np.float32)
    defs = []
    for d in spec.get("layers", []):
        t1 = time.time()
        m = np.zeros((H, W), np.float32)
        for p in d["polygons"]:
            m = np.maximum(m, polygon_mask((H, W), p))
        ref = d.get("refine")
        if ref:
            m = np.maximum(refine_grabcut(clean, m, **ref) * 1.0, _grow((m > 0.5).astype(np.uint8), -ref.get("band", 8)).astype(np.float32))
        hard = _grow((m > 0.5).astype(np.uint8), d.get("grow", 2)).astype(np.float32)
        soft = cv2.GaussianBlur(hard, (0, 0), d.get("feather", 1.5)) if d.get("feather", 1.5) > 0 else hard
        # keep alpha=1 inside the hard core, soft only outward/inward ramp ~ feather
        defs.append(dict(name=d["name"], depth=d.get("depth", 0.5), hard=hard, alpha=soft, kind="layer"))
        T["mask_" + d["name"] + "_s"] = time.time() - t1
    elems = []
    for e in spec.get("elements", []):
        m = np.zeros((H, W), np.float32)
        for p in e["polygons"]:
            m = np.maximum(m, polygon_mask((H, W), p))
        hard = _grow((m > 0.5).astype(np.uint8), e.get("grow", 2)).astype(np.float32)
        soft = cv2.GaussianBlur(hard, (0, 0), e.get("feather", 1.2))
        elems.append(dict(name=e["name"], depth=e.get("depth", 0.0), hard=hard, alpha=soft, kind="element"))
    t1 = time.time()
    all_front = np.zeros((H, W), np.float32)
    for d in defs + elems:
        all_front = np.maximum(all_front, d["hard"])
    bg_hole = _grow(all_front.astype(np.uint8), 3)
    bg_rgb = inpaint(clean, bg_hole).astype(np.float32)
    T["inpaint_bg_s"] = time.time() - t1
    st.layers.append(Layer("bg", bg_rgb, np.ones((H, W), np.float32), 0.0, "bg"))
    st.masks["bg_hole"] = bg_hole
    for e in elems:
        st.layers.append(Layer(e["name"], cl.copy(), e["alpha"], e["depth"], "element")); st.masks[e["name"]] = e["alpha"]
    for i, d in enumerate(defs):
        t1 = time.time()
        front = np.zeros((H, W), np.float32)
        for dd in defs[i + 1:]:
            front = np.maximum(front, dd["hard"])
        rgb = inpaint(clean, _grow(front.astype(np.uint8), 3)).astype(np.float32) if front.any() else cl.copy()
        st.layers.append(Layer(d["name"], rgb, d["alpha"], d["depth"], "layer")); st.masks[d["name"]] = d["alpha"]
        T["inpaint_" + d["name"] + "_s"] = time.time() - t1
    st.timings = T
    return st

def export_stack(st, outdir):
    os.makedirs(outdir, exist_ok=True)
    cv2.imwrite(os.path.join(outdir, "clean_plate.png"), cv2.cvtColor(st.clean_plate, cv2.COLOR_RGB2BGR))
    for l in st.layers:
        rgba = np.dstack([np.clip(l.rgb, 0, 255), l.alpha * 255]).astype(np.uint8)
        cv2.imwrite(os.path.join(outdir, f"layer_{l.name}.png"), cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA))
