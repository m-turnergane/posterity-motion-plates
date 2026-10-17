"""petal_fall (v0.3): individual flowers released from a hand.
 * suspended petals of the artwork are cut out (real pixels, alpha sprites), removed from the clean plate, and re-animated;
 * extra petals are procedural variants of the real petal pixel set (random affine + curvature + silhouette jitter + hue/brightness jitter
   + cross-texture blend) -- never flipped/scaled copies; pairwise sprite similarity is measured and reported;
 * 3-D tumble: each petal is a curved flat disc with a rotation R(t)=Rz(psi)Rx(phi)Ry(chi); its image is the elliptical projection
   (cos-modulated width), with lateral sway coupled to the tilt and scaled by size; light-direction shading follows the normal;
 * landing on a perspective plane (quad of the bier covering): scale/shear by depth; gentle contact = damped rock + friction slide + soft shadow;
 * motion blur by sub-frame accumulation; 2x supersampled edges."""
import math, numpy as np, cv2
from .base import Effect, register, blend_rgba
from ..core.util import smoothstep, polygon_mask, Noise1D

def cut_petal(base, spec):
    """Segment one petal by hand-authored ellipse + method. Returns (x0,y0,mask uint8)."""
    cx, cy, ax, ay = (int(round(spec[k])) for k in ("cx", "cy", "ax", "ay")); pad = 10
    x0, y0, x1, y1 = cx - ax - pad, cy - ay - pad, cx + ax + pad, cy + ay + pad
    sub = np.ascontiguousarray(base[y0:y1, x0:x1][..., ::-1]); h, w = sub.shape[:2]
    if spec.get("method") == "ellipse":
        fgm = np.zeros((h, w), np.uint8); cv2.ellipse(fgm, (cx - x0, cy - y0), (max(int(ax * 0.85), 1), max(int(ay * 0.85), 1)), spec.get("angle", 0), 0, 360, 1, -1)
    elif spec.get("method", "grabcut") == "luma":
        g = cv2.cvtColor(sub, cv2.COLOR_BGR2GRAY); ee = np.zeros((h, w), np.uint8)
        cv2.ellipse(ee, (cx - x0, cy - y0), (int(ax * 1.25), int(ay * 1.25)), 0, 0, 360, 1, -1)
        fgm = ((g > spec.get("thr", 172)) & (ee > 0)).astype(np.uint8)
        fgm = cv2.morphologyEx(fgm, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        fgm = cv2.morphologyEx(fgm, cv2.MORPH_OPEN, np.ones((spec.get("open", 5),) * 2, np.uint8))   # drop thin stems
        cnt, _ = cv2.findContours(fgm.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); fgm = np.zeros_like(fgm); cv2.drawContours(fgm, cnt, -1, 1, -1)
    else:
        m = np.full((h, w), cv2.GC_BGD, np.uint8); m[3:-3, 3:-3] = cv2.GC_PR_BGD
        e = np.zeros((h, w), np.uint8); cv2.ellipse(e, (cx - x0, cy - y0), (int(ax * 1.15), int(ay * 1.15)), 0, 0, 360, 1, -1); m[e > 0] = cv2.GC_PR_FGD
        e = np.zeros((h, w), np.uint8); cv2.ellipse(e, (cx - x0, cy - y0), (int(ax * .5), int(ay * .5)), 0, 0, 360, 1, -1); m[e > 0] = cv2.GC_FGD
        cv2.setRNGSeed(1234)
        cv2.grabCut(sub, m, None, np.zeros((1, 65)), np.zeros((1, 65)), 6, cv2.GC_INIT_WITH_MASK)
        fgm = ((m == 1) | (m == 3)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(fgm)
    if n > 1: fgm = (lab == 1 + np.argmax(st[1:, 4])).astype(np.uint8)
    if int(fgm.sum()) < 6:      # tiny petals (e.g. proxy renders): fall back to the authored ellipse
        fgm = np.zeros_like(fgm); cv2.ellipse(fgm, (cx - x0, cy - y0), (max(int(ax * 0.9), 1), max(int(ay * 0.9), 1)), 0, 0, 360, 1, -1)
    return x0, y0, fgm

def _depremult_edge(rgb, a):
    """Bleed interior colour into the 1-px rim so petal edges carry petal colour, not the old background."""
    core = (a > 0.98).astype(np.uint8); out = rgb.copy()
    for _ in range(3):
        k = cv2.dilate(core, np.ones((3, 3), np.uint8)); ring = (k > 0) & (core == 0)
        blur = cv2.blur(out * core[..., None], (3, 3)); cnt = cv2.blur(core.astype(np.float32), (3, 3))[..., None] + 1e-6
        out[ring] = (blur / cnt)[ring]; core = k
    return out


def _rot(psi, phi, chi):
    cz, sz, cx, sx, cy, sy = math.cos(psi), math.sin(psi), math.cos(phi), math.sin(phi), math.cos(chi), math.sin(chi)
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]); Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]]); Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    return Rz @ Rx @ Ry

def _proj(R, sin_e, cos_e):
    """world->image linear map (3 -> 2): x right, y away from camera (up in image), z up."""
    return np.array([[R[0, 0], R[0, 1], R[0, 2]], [-(R[1, 0] * sin_e + R[2, 0] * cos_e), -(R[1, 1] * sin_e + R[2, 1] * cos_e), -(R[1, 2] * sin_e + R[2, 2] * cos_e)]])

def _bleed(rgb, core, iters=6):
    core = core.astype(np.uint8); out = rgb.copy()
    for _ in range(iters):
        k = cv2.dilate(core, np.ones((3, 3), np.uint8)); ring = (k > 0) & (core == 0)
        blur = cv2.blur(out * core[..., None], (3, 3)); cnt = cv2.blur(core.astype(np.float32), (3, 3))[..., None] + 1e-6
        out[ring] = (blur / cnt)[ring]; core = k
    return out

def make_sprite(base, bg, c, x0, y0, m, ss=2):
    """alpha sprite (supersampled x ss) from a cut mask. Rim colour is solved against the clean plate behind the petal then clamped to the
    bled interior colour (no dark halos). returns dict(rgb, a, w, h, ox, oy) with rgb/a float32 at ss resolution."""
    h, w = m.shape; sub = base[y0:y0 + h, x0:x0 + w]; sbg = bg[y0:y0 + h, x0:x0 + w]
    mm = cv2.dilate(m, np.ones((3, 3), np.uint8)).astype(np.float32); a = cv2.GaussianBlur(mm, (0, 0), 0.8)
    core = (a > 0.97); interior = _bleed(sub, core, 7)
    sol = np.clip((sub - sbg * (1 - a[..., None])) / np.maximum(a, 0.05)[..., None], 0, 255); rim = (a > 0.05) & (a < 0.97)
    dev = np.clip(sol - interior, -22, 22); rgb = np.where(rim[..., None], interior + dev * 0.5, interior)
    ys, xs = np.where(a > 0.02); xa, xb, ya, yb = xs.min() - 2, xs.max() + 3, ys.min() - 2, ys.max() + 3
    rgb, a = rgb[ya:yb, xa:xb], a[ya:yb, xa:xb]
    big = lambda z: cv2.resize(z, None, fx=ss, fy=ss, interpolation=cv2.INTER_CUBIC)
    rgb2, a2 = np.clip(big(rgb), 0, 255), np.clip(big(a), 0, 1)
    return dict(rgb=rgb2.astype(np.float32), a=a2.astype(np.float32), w=a2.shape[1], h=a2.shape[0], ox=x0 + (xa + xb) / 2.0, oy=y0 + (ya + yb) / 2.0, ss=ss)

def load_pack(path):
    """sprite pack = directory of RGBA PNGs (2x supersampled petal sprites) -> {id: sprite}. See tools/export_petal_pack.py."""
    import os
    if not path: return {}
    out = {}
    for fn in sorted(os.listdir(path)):
        if fn.lower().endswith(".png"):
            im = cv2.cvtColor(cv2.imread(os.path.join(path, fn), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA).astype(np.float32); a = im[..., 3] / 255.0
            out["pack_" + fn[:-4]] = dict(rgb=im[..., :3], a=a, w=a.shape[1], h=a.shape[0], ox=0, oy=0, ss=2)
    return out

def export_pack(sources, path):
    import os
    os.makedirs(path, exist_ok=True)
    for k, sp in sources.items():
        rgba = np.dstack([sp["rgb"], sp["a"] * 255]).astype(np.uint8); cv2.imwrite(os.path.join(path, f"{k}.png"), cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA))

def _smooth_noise(rng, shape, sigma):
    g = cv2.GaussianBlur(rng.standard_normal(shape).astype(np.float32), (0, 0), sigma); return g / (g.std() + 1e-6)

def make_variant(src, other, rng, jit):
    """Procedural variant of a real petal sprite: random affine (non-uniform scale, shear, rotation), curvature/edge displacement, silhouette
    jitter, cross-texture blend with a second source (aligned by resize), hue/saturation/brightness jitter confined to the source palette."""
    ss = src["ss"]; rgb, a = src["rgb"], src["a"]; h, w = a.shape
    if other is not None and jit.get("blend", 0.3) > 0:
        o = cv2.resize(other["rgb"], (w, h), interpolation=cv2.INTER_AREA); k = rng.uniform(0.15, jit.get("blend", 0.3)) 
        hsv_s = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2HSV)[..., 0].mean(); hsv_o = cv2.cvtColor(o.astype(np.uint8), cv2.COLOR_RGB2HSV)[..., 0].mean()
        if abs(hsv_s - hsv_o) < 14 or abs(abs(hsv_s - hsv_o) - 180) < 14: rgb = rgb * (1 - k) + o * k      # only blend textures within the same colour family
    sx, sy = rng.uniform(*jit.get("scale_x", [0.82, 1.22])), rng.uniform(*jit.get("scale_y", [0.82, 1.28])); sh = rng.uniform(-jit.get("shear", 0.22), jit.get("shear", 0.22)); th = rng.uniform(0, 2 * math.pi)
    A = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]]) @ np.array([[sx, sh * sx], [0, sy]])
    pad = int(0.35 * max(w, h) * max(sx, sy)) + 6; W2, H2 = int(w * max(sx, sy) * 1.5) + 2 * pad, int(h * max(sx, sy) * 1.5) + 2 * pad
    c0 = np.array([w / 2.0, h / 2.0]); c1 = np.array([W2 / 2.0, H2 / 2.0]); M = np.hstack([A, (c1 - A @ c0)[:, None]]).astype(np.float32)
    # curvature / silhouette displacement field (smooth), applied on the output grid
    dx = _smooth_noise(rng, (H2, W2), 6 * ss) * jit.get("curve_px", 2.4) * ss; dy = _smooth_noise(rng, (H2, W2), 6 * ss) * jit.get("curve_px", 2.4) * ss
    pm = np.dstack([rgb * a[..., None], a]).astype(np.float32); wp = cv2.warpAffine(pm, M, (W2, H2), flags=cv2.INTER_CUBIC, borderValue=0)
    yy, xx = np.mgrid[0:H2, 0:W2].astype(np.float32); wp = cv2.remap(wp, xx + dx, yy + dy, cv2.INTER_LINEAR, borderValue=0)
    al = np.clip(wp[..., 3], 0, 1); al = np.clip(al + _smooth_noise(rng, (H2, W2), 3 * ss) * jit.get("edge_noise", 0.10) * (al > 0.02) * (al < 0.98), 0, 1)
    rgbw = wp[..., :3] / np.maximum(wp[..., 3:4], 1e-3); rgbw = _bleed(np.clip(rgbw, 0, 255).astype(np.float32), al > 0.9, 5)
    hsv = cv2.cvtColor(rgbw.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    hsv[..., 0] = (hsv[..., 0] + rng.uniform(-jit.get("hue", 4), jit.get("hue", 4))) % 180; hsv[..., 1] = np.clip(hsv[..., 1] * rng.uniform(*jit.get("sat", [0.88, 1.10])), 0, 255)
    hsv[..., 2] = np.clip(hsv[..., 2] * rng.uniform(*jit.get("val", [0.86, 1.08])) * (1 + 0.10 * rng.uniform(-1, 1) * (xx - W2 / 2) / W2), 0, 255)   # gentle gradient across the petal
    out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
    ys, xs = np.where(al > 0.02); xa, xb, ya, yb = xs.min() - 2, xs.max() + 3, ys.min() - 2, ys.max() + 3
    return dict(rgb=out[ya:yb, xa:xb], a=al[ya:yb, xa:xb], w=xb - xa, h=yb - ya, ss=ss, ox=0, oy=0, variant=True)

def sprite_signature(sp, n=24):
    """rotation/flip-tolerant signature for similarity checks: aligned to principal axis, resized, mean-removed colour luma."""
    a = sp["a"]; ys, xs = np.nonzero(a > 0.3); c = np.array([xs.mean(), ys.mean()]); cov = np.cov(np.stack([xs - c[0], ys - c[1]])); ev, evec = np.linalg.eigh(cov); ang = math.degrees(math.atan2(evec[1, 1], evec[0, 1]))
    M = cv2.getRotationMatrix2D((float(c[0]), float(c[1])), ang, 1.0); R = max(a.shape) * 1.2; M[:, 2] += (R / 2 - c)
    g = cv2.cvtColor(sp["rgb"].astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32); pm = np.dstack([g * a, a])
    w = cv2.warpAffine(pm, M, (int(R), int(R))); s = cv2.resize(w, (n, n), interpolation=cv2.INTER_AREA); return s[..., 0], s[..., 1]

def sprite_similarity(s1, s2):
    """max normalised correlation over the 4 axis-aligned flips/rotations of the principal-axis-aligned signature (flip-invariant => a mirrored copy scores ~1)."""
    (g1, a1), (g2, a2) = sprite_signature(s1), sprite_signature(s2); best = -1
    for k in range(2):
        for fl in (False, True):
            for rot in (0, 2):
                b = np.rot90(a2, rot); bg = np.rot90(g2, rot)
                if fl: b, bg = b[:, ::-1], bg[:, ::-1]
                x = np.concatenate([a1.ravel(), g1.ravel() / 255.0]); y = np.concatenate([b.ravel(), bg.ravel() / 255.0]); x = x - x.mean(); y = y - y.mean()
                best = max(best, float((x @ y) / (np.linalg.norm(x) * np.linalg.norm(y) + 1e-9)))
    return best

@register("petal_fall")
class PetalFall(Effect):
    def authoring_holes(self, base):
        self.cuts = []; holes = np.zeros(base.shape[:2], np.uint8)
        for c in self.p["cuts"]:
            x0, y0, m = cut_petal(base, c); self.cuts.append((c, x0, y0, m))
            if c.get("remove", True):
                h, w = m.shape; holes[y0:y0 + h, x0:x0 + w] |= cv2.dilate(m, np.ones((2 * self.p.get("hole_px", 2) + 1,) * 2, np.uint8))
        return holes
    # ------------------------------------------------------------------ setup
    def setup(self, ctx):
        P = self.p; rng = ctx.rng("petals", self.idx); self.items = []; self.sources = {}; ss = 2; self.ss = ss
        base = ctx.base.astype(np.float32); bg = ctx.stack.clean_plate.astype(np.float32)
        for c, x0, y0, m in self.cuts: self.sources[c["id"]] = make_sprite(base, bg if c.get("remove", True) else base, c, x0, y0, m, ss)
        for pid, spr in load_pack(P.get("source_pack")).items(): self.sources.setdefault(pid, spr)       # reusable petal source packs (RGBA sprites authored once)
        sf = P.get("surface", {}); q = np.array(sf["quad"], np.float32)       # back-left, back-right, front-right, front-left
        self.quad = q; self.Hm = cv2.getPerspectiveTransform(np.array([[0, 0], [1, 0], [1, 1], [0, 1]], np.float32), q)
        self.surf = polygon_mask((ctx.H, ctx.W), (q + np.array([[-6, -10], [6, -10], [6, 6], [-6, 6]], np.float32)).tolist(), feather=2.5)
        ph = P.get("physics", {}); self.sin_e = math.sin(math.radians(ph.get("elevation_deg", 27))); self.cos_e = math.cos(math.radians(ph.get("elevation_deg", 27)))
        L = np.array(ph.get("light_dir", [0.5, 0.45, 0.74]), float); self.L = L / np.linalg.norm(L)
        self.hand = polygon_mask((ctx.H, ctx.W), P["hand_occluder"], feather=1.2) if P.get("hand_occluder") else None
        self.spawn_hand = P.get("hand_occluder")
        placed = []
        rel = P.get("release_s", {}); ids = [c["id"] for c, *_ in self.cuts]
        for c, *_ in self.cuts:
            it = self._make(rng, c["id"], self.sources[c["id"]], self.sources[c["id"]]["ox"], self.sources[c["id"]]["oy"], rel.get(c["id"], 1.2), True, placed, 1.0, None)
            self.items.append(it)
        ex = P.get("extras", {}); n = ex.get("count", 0)
        if n:
            t0, t1, gap = ex.get("t0", 1.9), ex.get("t1", 3.3), ex.get("min_gap", 0.18)
            # strictly increasing release times in [t0,t1]: stratified jitter, then enforce min gap (never recycled into earlier windows)
            edges = np.linspace(t0, t1, n + 1); ts = [rng.uniform(edges[i] + 0.15 * (edges[i + 1] - edges[i]), edges[i + 1] - 0.15 * (edges[i + 1] - edges[i])) for i in range(n)]
            gap = min(gap, 0.9 * (t1 - t0) / max(n - 1, 1))
            for i in range(1, n): ts[i] = max(ts[i], ts[i - 1] + gap)
            if ts[-1] > t1: ts = [t0 + (x - ts[0]) * (t1 - t0) / max(ts[-1] - ts[0], 1e-6) for x in ts]     # stay inside the release window (never wraps/recycles)
            pool = [i for i in (ex.get("sources") or ids) if i in self.sources]; pool = pool or list(self.sources); used = {}
            for i in range(n):
                pool_sorted = sorted(pool, key=lambda k: (used.get(k, 0), rng.random())); sid = pool_sorted[0]; used[sid] = used.get(sid, 0) + 1
                other = self.sources[pool_sorted[1 + int(rng.integers(max(len(pool_sorted) - 1, 1)))]] if len(pool_sorted) > 1 else None
                spr = make_variant(self.sources[sid], other, rng, ex.get("variation", {}))
                xr, yr = ex.get("x", [694, 716]), ex.get("y", [802, 818])
                it = self._make(rng, f"x{i}_{sid}", spr, rng.uniform(*xr), rng.uniform(*yr), ts[i], False, placed, rng.uniform(*ex.get("scale", [0.92, 1.18])), sid)
                self.items.append(it)
        self.items.sort(key=lambda d: d["t_rel"])
        self.report = self._similarity_report()
    def _similarity_report(self):
        sp = [(it["id"], it["spr"]) for it in self.items]; worst = (0.0, None); 
        for i in range(len(sp)):
            for j in range(i + 1, len(sp)):
                s = sprite_similarity(sp[i][1], sp[j][1])
                if s > worst[0]: worst = (s, (sp[i][0], sp[j][0]))
        return dict(petals=len(sp), max_pair_similarity=round(worst[0], 3), most_similar_pair=worst[1])
    def _plane(self, u, v):
        """image point + local scale + u-axis slope at plane coords (u: left->right, v: back->front)."""
        def f(u_, v_):
            p = self.Hm @ np.array([u_, v_, 1.0]); return p[:2] / p[2]
        p = f(u, v); u0, u1, v0, v1 = max(u - 0.02, 0), min(u + 0.02, 1), max(v - 0.05, 0), min(v + 0.05, 1)
        du = f(u1, v) - f(u0, v); dv = f(u, v1) - f(u, v0)
        sc = math.sqrt(abs(du[0] * dv[1] - du[1] * dv[0]) / ((u1 - u0) * (v1 - v0))); return p, sc, du[1] / du[0]
    def _make(self, rng, pid, spr, x0, y0, t_rel, original, placed, scale, srcid):
        P = self.p; ph = P.get("physics", {}); it = dict(id=pid, spr=spr, x0=x0, y0=y0, t_rel=t_rel, original=original, srcid=srcid)
        # landing spot on the plane, spaced from previously landed petals
        lu = ph.get("land_u", [0.12, 0.88]); lv = ph.get("land_v", [0.1, 0.9]); sep = ph.get("min_sep_px", 30)
        for _ in range(60):
            u, v = rng.uniform(*lu), rng.uniform(*lv); p, sc, slope = self._plane(u, v)
            # prefer landing near the release x (petals fall nearly vertically from the hand)
            if abs(p[0] - x0) > ph.get("max_lateral_px", 70) and _ < 50: continue
            if all(math.hypot(p[0] - q[0], p[1] - q[1]) > sep for q in placed): break
        placed.append(p); it.update(u=u, v=v, L=p, depth_scale=sc / self._plane(0.5, 1.0)[1], slope=slope)
        size = max(spr["w"], spr["h"]) / spr["ss"]; it["size"] = size; it["scale"] = scale * it["depth_scale"] * (1.0 if original else 1.0)
        szf = float(np.clip(size / 44.0, 0.55, 1.5))
        it["vt"] = rng.uniform(*ph.get("terminal_px_s", [88, 128])) * (0.82 + 0.25 * (1 / szf)) * it["depth_scale"]; it["ta"] = rng.uniform(0.28, 0.5); it["v0"] = rng.uniform(25, 70) if not original else rng.uniform(0, 25)
        w0 = rng.uniform(*ph.get("flutter_hz", [0.9, 1.6])) * 2 * math.pi / math.sqrt(szf)       # larger petals flutter slower
        it.update(w=w0, pw=rng.uniform(0, 6.28), phi_m=math.radians(rng.uniform(-18, 35)), phi_a=math.radians(rng.uniform(32, 62)), chi0=rng.uniform(0, 6.28), chi_w=rng.uniform(1.0, 2.6) * rng.choice([-1, 1]),
                  psi0=rng.uniform(0, 6.28), psi_w=rng.uniform(-1.3, 1.3), kappa=rng.uniform(0.10, 0.34), sway=rng.uniform(*ph.get("sway_px", [4, 9])) * szf, drift=rng.uniform(-6, 6),
                  rest_psi=rng.uniform(0, 2 * math.pi), slide=rng.uniform(*ph.get("slide_px", [1.0, 6.0])) * rng.choice([-1, 1]), slide_tau=rng.uniform(0.10, 0.2), rock_amp=math.radians(rng.uniform(4, 11)),
                  rock_hz=rng.uniform(2.4, 3.6), rock_tau=rng.uniform(0.07, 0.11), lift=rng.uniform(0, 7))
        # landing time: solve y(tau)=L.y - lift
        ly = p[1] - it["lift"]; it["ly"] = max(ly, y0 + 25); lo, hi = 0.0, 8.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if self._y(it, mid) < it["ly"]: lo = mid
            else: hi = mid
        it["tl"] = t_rel + hi; it["tau_land"] = hi
        return it
    # -------------------------------------------------------------- kinematics
    def _y(self, it, tau):
        vt, ta, v0 = it["vt"], it["ta"], it["v0"]; return it["y0"] + vt * tau - (vt - v0) * ta * (1 - math.exp(-tau / ta))
    def _xy(self, it, tau):
        """centre position (image px) while airborne, h = remaining height to the landing point."""
        y = self._y(it, tau); prog = float(np.clip((y - it["y0"]) / max(it["ly"] - it["y0"], 1.0), 0, 1)); h = it["ly"] - y
        x = it["x0"] + (it["L"][0] - it["x0"]) * prog * prog * (3 - 2 * prog) + it["drift"] * tau
        env = float(smoothstep(h / 45.0)) * float(smoothstep(tau / 0.35))                    # sway dies out as the petal nears the surface
        sw = it["sway"] * env * (math.sin(it["w"] * tau + it["pw"]) - math.sin(it["pw"]))   # lateral oscillation ~ coupled with tilt phase
        return x + sw, y, h
    def _angles(self, it, tau, h):
        env = float(smoothstep(h / 40.0)); w = it["w"]
        phi = it["phi_m"] + it["phi_a"] * math.sin(w * tau + it["pw"] + 1.2) * (0.35 + 0.65 * env)
        chi = it["chi0"] + it["chi_w"] * tau * (0.4 + 0.6 * env); psi = it["psi0"] + it["psi_w"] * tau
        return psi, phi, chi
    def _basis(self, it, t):
        """-> (centre xy, 2x3 image map of the (a,b,z) local axes incl. curvature z-axis, brightness, alpha, h, landed)"""
        tau = t - it["t_rel"]; sc = it["scale"]
        if tau <= 0: return None
        if t < it["tl"]:
            x, y, h = self._xy(it, tau); psi, phi, chi = self._angles(it, tau, h); R = _rot(psi, phi, chi); landed = False
            tilt = _proj(R, self.sin_e, self.cos_e)
        else:
            d = t - it["tl"]; x_end, y_end, _ = self._xy(it, it["tau_land"]); psi, phi, chi = self._angles(it, it["tau_land"], 0.0)
            b = 1 - math.exp(-d / it["rock_tau"]) * math.cos(2 * math.pi * it["rock_hz"] * d)            # 0 -> 1 with a small damped overshoot (rock)
            Ra = _rot(psi, phi, chi); Rf = _rot(it["rest_psi"], 0.0, 0.0); Rm = Ra * (1 - b) + Rf * b       # blend orientation air -> flat
            U, _, Vt = np.linalg.svd(Rm); R = U @ Vt
            if np.linalg.det(R) < 0: R[:, 2] *= -1
            rock = it["rock_amp"] * math.exp(-d / (it["rock_tau"] * 2.2)) * math.sin(2 * math.pi * it["rock_hz"] * 0.8 * d + 0.7)
            R = _rot(0, rock, 0) @ R
            slide = it["slide"] * (1 - math.exp(-d / it["slide_tau"])); x, y, h = x_end + slide, y_end + 1.5 * math.exp(-d / 0.1) * 0 - 0.0, 0.0; landed = True
            tilt = _proj(R, self.sin_e, self.cos_e)
        return dict(x=x, y=y, R=R, tilt=tilt, h=h, landed=landed, tau=tau)
    def _frame_params(self, it, t, jitter_t=0.0):
        if it["original"] and t + jitter_t <= it["t_rel"]:      # still hanging exactly where the artwork has it (identity pose = the original pixels)
            B = dict(x=it["x0"], y=it["y0"], R=np.eye(3), tilt=None, h=1e9, landed=False, tau=0.0)
            return dict(B=B, M=np.eye(2), zc=np.zeros(2), bright=1.0, alpha=1.0, nl=1.0, sc_pos=1.0, emerge=False, grow=1.0)
        B = self._basis(it, t + jitter_t)
        if B is None: return None
        tau = B["tau"]; w = float(smoothstep(tau / 0.55)) if it["original"] else 1.0
        sh = np.array([[1.0, 0.0], [it["slope"], 1.0]])                    # plane u-axis tilt (perspective of the covering)
        Md = sh @ B["tilt"][:, :2] * it["scale"]; zc = sh @ B["tilt"][:, 2] * it["scale"]   # 2x2 + curvature axis
        U_, S_, Vt_ = np.linalg.svd(Md); S_ = np.maximum(S_, S_[0] * 0.36); Md = U_ @ np.diag(S_) @ Vt_      # never fully edge-on (no needle-thin slivers)
        if it["original"]: M = (1 - w) * np.eye(2) + w * Md; zc = zc * w
        else: M = Md
        n = B["R"][:, 2]; nl = abs(float(n @ self.L)); br = 0.76 + 0.40 * nl ** 0.85          # light-direction shading from the petal normal
        bright = 1 + (1 - w) * 0 + w * (br - 1) if it["original"] else br
        alpha = 1.0 if it["original"] else float(smoothstep(tau / 0.22))
        return dict(B=B, M=M, zc=zc, bright=bright, alpha=alpha, nl=nl, sc_pos=1.0, emerge=(not it["original"]) and tau < 0.4, grow=1.0 if it["original"] else 0.72 + 0.28 * float(smoothstep(tau / 0.35)))
    # --------------------------------------------------------------- rendering
    def _render_patch(self, ctx, st, it, fp, Mcam, kappa_px, grid):
        """premultiplied RGBA patch (2x supersampled -> area downsample) for one sub-frame; returns (patch, x0, y0)."""
        spr = it["spr"]; ss = spr["ss"]; B = fp["B"]; M = fp["M"] * fp["grow"]; zc = fp["zc"] * fp["grow"]
        cx, cy = B["x"], B["y"]; X, Y = Mcam @ np.array([cx, cy, 1.0], np.float32); s_cam = float(Mcam[0, 0])
        M = M * s_cam; zc = zc * s_cam
        xi, yi, R = grid; fx, fy = X - xi, Y - yi; n = 2 * R + 1; N2 = n * ss
        gy, gx = np.mgrid[0:N2, 0:N2].astype(np.float32); px = (gx + 0.5) / ss - 0.5 - R - fx; py = (gy + 0.5) / ss - 0.5 - R - fy       # output offset from the centre in 1x px
        # inverse map (a,b) with curvature z = kappa*(a^2+b^2)/D: Newton from the affine inverse
        Minv = np.linalg.inv(M) if abs(np.linalg.det(M)) > 1e-4 else np.linalg.pinv(M); D = max(spr["w"], spr["h"]) / ss
        a = Minv[0, 0] * px + Minv[0, 1] * py; b = Minv[1, 0] * px + Minv[1, 1] * py
        if kappa_px > 0:
            for _ in range(2):
                z = kappa_px * (a * a + b * b) / D; fa = M[0, 0] * a + M[0, 1] * b + zc[0] * z; fb = M[1, 0] * a + M[1, 1] * b + zc[1] * z
                ea, eb = fa - px, fb - py; a -= Minv[0, 0] * ea + Minv[0, 1] * eb; b -= Minv[1, 0] * ea + Minv[1, 1] * eb
        sxm = (a * ss + spr["w"] / 2.0 - 0.5).astype(np.float32); sym = (b * ss + spr["h"] / 2.0 - 0.5).astype(np.float32)
        src = it.setdefault("_pm", np.dstack([spr["rgb"] * spr["a"][..., None], spr["a"]]).astype(np.float32))
        pm = cv2.remap(src, sxm, sym, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        # fake shading across the (curved) petal from the tilt: lit side brighter
        patch = cv2.resize(pm, (n, n), interpolation=cv2.INTER_AREA)
        sh = 1.0 + 0.10 * np.clip((a.reshape(N2, N2) / D), -1, 1)[::ss, ::ss][:n, :n] * float(B["R"][0, 2] - 0.0) * 4
        patch[..., :3] *= (fp["bright"] * np.clip(sh, 0.85, 1.15))[..., None]
        return patch, xi - R, yi - R
    def _shadow(self, ctx, st, frame, it, fp, Mcam):
        B = fp["B"]
        if fp["alpha"] <= 0: return
        h = min(B["h"], 90.0); op = 0.40 * (1 - h / 90.0) ** 1.4 * fp["alpha"]
        if op < 0.02: return
        x = (B["x"] if B["landed"] else it["x0"] + (B["x"] - it["x0"])) ; y = it["ly"] + (0 if B["landed"] else 3)
        off = (-2.5, 2.5) if B["landed"] else (-2 - h * 0.05, 2 + h * 0.03)
        X, Y = Mcam @ np.array([x + off[0], y + off[1] + 4, 1.0], np.float32); rw = it["size"] * it["scale"] * 0.40 * (1 + h / 90.0); rh = max(rw * 0.30, 2.0); sig = 1.0 + h / 30.0
        R = int(rw * 1.8 + 6); xi, yi = int(round(X)), int(round(Y)); H, W = frame.shape[:2]; xa, ya, xb, yb = max(xi - R, 0), max(yi - R, 0), min(xi + R + 1, W), min(yi + R + 1, H)
        if xb <= xa or yb <= ya: return
        if st.surf_cam is None:
            st.surf_cam = cv2.warpAffine(self.surf, Mcam, (ctx.W, ctx.H), flags=cv2.INTER_LINEAR)
        yy, xx = np.mgrid[ya:yb, xa:xb].astype(np.float32); d = ((xx - X) / rw) ** 2 + ((yy - Y) / rh) ** 2
        a = np.exp(-d * 1.6 / sig) * op * st.surf_cam[ya:yb, xa:xb]; roi = frame[ya:yb, xa:xb]; roi *= (1 - a[..., None] * (1 - np.array([0.34, 0.20, 0.30], np.float32)))
    def post(self, ctx, st, frame):
        st.surf_cam = None; Mcam = ctx.camera_fn(0.5, st.t) if ctx.camera_fn else np.array([[1, 0, 0], [0, 1, 0]], np.float32); Mcam = Mcam.astype(np.float32)
        ph = self.p.get("physics", {}); K = int(ph.get("motion_blur_samples", 4)); shutter = ph.get("shutter", 0.55) / ctx.fps
        tint = np.array(self.p.get("pall_tint", [92, 24, 62]), np.float32); vis = []
        for it in self.items:
            if st.t - it["t_rel"] <= 0 and not it["original"]: continue
            fp0 = self._frame_params(it, st.t)
            if fp0 is None: continue
            vis.append((it, fp0))
        for it, fp in vis: self._shadow(ctx, st, frame, it, fp, Mcam)
        for it, fp in sorted(vis, key=lambda a: (not a[1]["B"]["landed"], a[1]["B"]["y"])):
            X0, Y0 = Mcam @ np.array([fp["B"]["x"], fp["B"]["y"], 1.0], np.float32); sp_ = it["spr"]; Rr = int(0.5 * math.hypot(sp_["w"], sp_["h"]) / sp_["ss"] * it["scale"] * float(Mcam[0, 0]) * 1.35) + 14
            grid = (int(round(X0)), int(round(Y0)), Rr); acc = None; moving = (not fp["B"]["landed"]) or (st.t - it["tl"] < 0.5)
            ts = [(-0.5 + (k + 0.5) / K) * shutter for k in range(K)] if (K > 1 and moving and st.t > it["t_rel"]) else [0.0]
            for dt in ts:
                f2 = self._frame_params(it, st.t, dt) or fp; kp = it["kappa"]
                patch, x0, y0 = self._render_patch(ctx, st, it, f2, Mcam, kp, grid)
                acc = patch if acc is None else _accum(acc, patch)
            patch = acc / len(ts)
            if fp["B"]["landed"] or fp["B"]["h"] < 40:
                k = 0.06 * (1 - min(fp["B"]["h"], 40) / 40.0); patch[..., :3] = patch[..., :3] * (1 - k) + tint * k * patch[..., 3:4]
            patch *= fp["alpha"]
            if fp["emerge"] and self.hand is not None:       # petals leave the fingers: hidden behind the hand silhouette for the first fraction of a second
                hm = cv2.warpAffine(self.hand, Mcam, (ctx.W, ctx.H), flags=cv2.INTER_LINEAR)[y0:y0 + patch.shape[0], x0:x0 + patch.shape[1]] if (x0 >= 0 and y0 >= 0 and x0 + patch.shape[1] <= ctx.W and y0 + patch.shape[0] <= ctx.H) else None
                if hm is not None: patch *= (1 - hm)[..., None]
            blend_rgba(frame, patch, x0, y0)

def _accum(a, b):
    return a + b
