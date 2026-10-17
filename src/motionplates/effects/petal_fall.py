"""petal_fall: cuts the artwork's own suspended petals (alpha sprites), removes them from the clean plate, and re-animates
them (plus seeded extra copies of the cut sprites) falling with 3-D flutter and settling on a surface polygon with shadow/slide."""
import math, numpy as np, cv2
from .base import Effect, register, blend_rgba
from ..core.util import smoothstep, polygon_mask, Noise1D

def cut_petal(base, spec):
    """Segment one petal by hand-authored ellipse + method. Returns (x0,y0,mask uint8)."""
    cx, cy, ax, ay = spec["cx"], spec["cy"], spec["ax"], spec["ay"]; pad = 10
    x0, y0, x1, y1 = cx - ax - pad, cy - ay - pad, cx + ax + pad, cy + ay + pad
    sub = np.ascontiguousarray(base[y0:y1, x0:x1][..., ::-1]); h, w = sub.shape[:2]
    if spec.get("method", "grabcut") == "luma":
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
    return x0, y0, fgm

def _depremult_edge(rgb, a):
    """Bleed interior colour into the 1-px rim so petal edges carry petal colour, not the old background."""
    core = (a > 0.98).astype(np.uint8); out = rgb.copy()
    for _ in range(3):
        k = cv2.dilate(core, np.ones((3, 3), np.uint8)); ring = (k > 0) & (core == 0)
        blur = cv2.blur(out * core[..., None], (3, 3)); cnt = cv2.blur(core.astype(np.float32), (3, 3))[..., None] + 1e-6
        out[ring] = (blur / cnt)[ring]; core = k
    return out

@register("petal_fall")
class PetalFall(Effect):
    def authoring_holes(self, base):
        self.cuts = []
        holes = np.zeros(base.shape[:2], np.uint8)
        for c in self.p["cuts"]:
            x0, y0, m = cut_petal(base, c); self.cuts.append((c, x0, y0, m))
            h, w = m.shape; holes[y0:y0 + h, x0:x0 + w] |= cv2.dilate(m, np.ones((7, 7), np.uint8))
        return holes
    def setup(self, ctx):
        P = self.p; rng = ctx.rng("petals", self.idx); self.sprites = {}; self.items = []
        base = ctx.base.astype(np.float32)
        for c, x0, y0, m in self.cuts:
            mm = cv2.erode(m, np.ones((3, 3), np.uint8)).astype(np.float32)
            a = cv2.GaussianBlur(mm, (0, 0), 0.8); sub = base[y0:y0 + m.shape[0], x0:x0 + m.shape[1]]
            rgb = _depremult_edge(sub, a)
            ys, xs = np.where(a > 0.02); xa, xb, ya, yb = xs.min() - 1, xs.max() + 2, ys.min() - 1, ys.max() + 2
            spr = np.dstack([rgb[ya:yb, xa:xb], a[ya:yb, xa:xb]]).astype(np.float32)
            # sprite origin = true centre of the cut bbox in plate coords
            self.sprites[c["id"]] = dict(img=spr, ox=x0 + (xa + xb) / 2.0, oy=y0 + (ya + yb) / 2.0)
        self.surf = polygon_mask((ctx.H, ctx.W), P["surface"]["polygon"], feather=3.0)
        yl = P["surface"]["land_y"]; self.land_y = lambda x: yl[0] + yl[1] * (x - yl[2])   # y = a + b*(x - x0)
        rel = P.get("release_s", {})
        for c in self.cuts:
            cs = c[0]; self.items.append(self._make(rng, cs["id"], self.sprites[cs["id"]]["ox"], self.sprites[cs["id"]]["oy"], rel.get(cs["id"], 1.0), original=True, flip=False, scale=1.0, fade=0.0))
        ex = P.get("extras", {}); n = ex.get("count", 0); ids = ex.get("ids") or [c[0]["id"] for c in self.cuts]
        t = ex.get("t0", 1.6)
        for i in range(n):
            sid = ids[int(rng.integers(len(ids)))]
            xr, yr = ex.get("x", [712, 744]), ex.get("y", [800, 830])
            self.items.append(self._make(rng, sid, rng.uniform(*xr), rng.uniform(*yr), t, original=False, flip=bool(rng.integers(2)), scale=rng.uniform(*ex.get("scale", [0.85, 1.2])), fade=0.22))
            t += rng.uniform(*ex.get("gap", [0.10, 0.22])); 
            if t > ex.get("t1", 3.2): t = ex.get("t0", 1.6) + rng.uniform(0, 0.6)
        self.items.sort(key=lambda d: d["t_rel"])
    def _make(self, rng, sid, x0, y0, t_rel, original, flip, scale, fade):
        P = self.p; ph = P.get("physics", {}); it = dict(sid=sid, x0=x0, y0=y0, t_rel=t_rel, original=original, flip=flip, scale=scale, fade=fade)
        it["vt"] = rng.uniform(*ph.get("terminal_px_s", [105, 165])); it["ta"] = rng.uniform(0.25, 0.45)
        it["vx"] = rng.uniform(*ph.get("drift_px_s", [-6, 20])); it["amp"] = rng.uniform(*ph.get("sway_px", [5, 13])); it["w"] = rng.uniform(*ph.get("sway_hz", [0.7, 1.5])) * 2 * math.pi
        it["pw"] = rng.uniform(0, 6.28); it["th0"] = rng.uniform(0, 6.28); it["Om"] = rng.uniform(*ph.get("tumble_rad_s", [3.0, 6.5])) * rng.choice([-1, 1])
        it["th2"] = rng.uniform(0, 6.28); it["Om2"] = rng.uniform(2.0, 4.5); it["spin"] = rng.uniform(-1.6, 1.6); it["phi0"] = rng.uniform(-0.5, 0.5)
        it["flat"] = rng.uniform(0.34, 0.5); it["rest_rot"] = rng.uniform(-0.8, 0.8); it["slide"] = rng.choice([0.0, 0.0, 1.0]) * rng.uniform(8, 24) * rng.choice([-1, 1]) + rng.uniform(-2, 2)
        it["bounce"] = rng.uniform(2.0, 4.5); it["fl"] = Noise1D(rng, 1.4)
        tx = x0 + it["vx"] * 1.3; ly = self.land_y(tx) + rng.uniform(*ph.get("land_jitter", [0, 30]))
        it["ly"] = ly if not original else max(ly, y0 + 30)
        # landing time by bisection on analytic fall
        lo, hi = 0.0, 6.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if self._y(it, mid) < it["ly"]: lo = mid
            else: hi = mid
        it["tl"] = t_rel + hi; it["xl"] = self._x(it, hi)
        return it
    def _y(self, it, tau):
        vt, ta = it["vt"], it["ta"]; y = it["y0"] + vt * (tau - ta * (1 - math.exp(-tau / ta)))
        wv = 2.6; y += 0.10 * vt / wv * math.sin(wv * tau + it["pw"]) * float(smoothstep(tau / 0.6))
        return y
    def _x(self, it, tau):
        return it["x0"] + it["vx"] * tau * float(smoothstep(tau / 0.8)) + it["amp"] * math.sin(it["w"] * tau + it["pw"]) * float(smoothstep(tau / 0.9))
    def _pose(self, it, t):
        """-> dict(x,y,sx,sy,rot,bright,alpha,h) at time t (h = height above landing)."""
        tau = t - it["t_rel"]
        if tau <= 0:
            return dict(x=it["x0"], y=it["y0"], sx=1.0, sy=1.0, rot=0.0, bright=1.0, alpha=0.0 if it["fade"] else 1.0, h=1e9, landed=False)
        alpha = min(1.0, tau / it["fade"]) if it["fade"] else 1.0
        w = float(smoothstep(tau / 0.55))   # blend from original pose (identity) into the dynamic pose
        if t < it["tl"]:
            x, y = self._x(it, tau), self._y(it, tau); h = it["ly"] - y
            th = it["th0"] + it["Om"] * tau; sy_d = max(0.26, abs(math.cos(th))); sx_d = 0.78 + 0.22 * abs(math.cos(it["th2"] + it["Om2"] * tau))
            k = float(smoothstep(1 - h / 38.0)) if h < 38 else 0.0     # flatten onto the surface over the last ~38 px
            sy_d = sy_d * (1 - k) + it["flat"] * k; rot = it["phi0"] * w + it["spin"] * tau * w + 0.22 * math.sin(2.2 * tau + it["pw"]) * w
            rot = rot * (1 - 0.6 * k) + it["rest_rot"] * 0.6 * k
            br = 0.80 + 0.25 * abs(math.cos(th)); landed = False
            sx, sy = 1 + w * (sx_d - 1), 1 + w * (sy_d - 1); bright = 1 + w * (br - 1)
        else:
            d = t - it["tl"]; x0, y0 = it["xl"], it["ly"]
            bnc = it["bounce"] * math.exp(-d / 0.09) * abs(math.sin(2 * math.pi * d / 0.26)) if d < 0.6 else 0.0
            sl = it["slide"] * (1 - math.exp(-d / 0.20)) if it["slide"] else 0.0
            x = x0 + sl; y = y0 - bnc; h = bnc
            th_end = it["th0"] + it["Om"] * (it["tl"] - it["t_rel"])
            rot_l = (it["phi0"] + it["spin"] * (it["tl"] - it["t_rel"]) + 0.22 * math.sin(2.2 * (it["tl"] - it["t_rel"]) + it["pw"]))
            rot_l = rot_l * 0.4 + it["rest_rot"] * 0.6
            rot = rot_l + 0.35 * (1 - math.exp(-d / 0.15)) * (1 if it["slide"] >= 0 else -1) * min(abs(it["slide"]) / 10, 1)
            sx = 0.85 + 0.15 * abs(math.cos(it["th2"])); sy = it["flat"] * (1 + 0.06 * math.exp(-d / 0.1) * math.sin(14 * d)); bright = 0.92; landed = True
        return dict(x=x, y=y, sx=sx, sy=sy, rot=rot, bright=bright, alpha=alpha, h=max(h, 0.0), landed=landed)
    def _render(self, ctx, st, frame, it, pz, pall_tint):
        sp = self.sprites[it["sid"]]; img = sp["img"]
        if it["flip"]: img = img[:, ::-1]
        h, w = img.shape[:2]
        M = ctx.camera_fn(0.5, st.t) if ctx.camera_fn else np.array([[1, 0, 0], [0, 1, 0]], np.float32)
        s_cam = float(M[0, 0]); X, Y = M @ np.array([pz["x"], pz["y"], 1.0], np.float32)
        sc = it["scale"] * s_cam; c, s_ = math.cos(pz["rot"]), math.sin(pz["rot"])
        A = np.array([[c * sc * pz["sx"], -s_ * sc * pz["sy"]], [s_ * sc * pz["sx"], c * sc * pz["sy"]]], np.float32)
        # sprite coords centred at sprite centre; flipping handled above so centre stays the bbox centre
        R = int(0.75 * max(h, w) * sc * 1.4) + 3; cx0, cy0 = w / 2.0, h / 2.0
        ox, oy = int(round(X)) - R, int(round(Y)) - R
        T = np.array([[A[0, 0], A[0, 1], R + (X - round(X)) - (A[0, 0] * cx0 + A[0, 1] * cy0)], [A[1, 0], A[1, 1], R + (Y - round(Y)) - (A[1, 0] * cx0 + A[1, 1] * cy0)]], np.float32)
        pm = np.dstack([img[..., :3] * img[..., 3:4], img[..., 3:4]]).astype(np.float32)
        patch = cv2.warpAffine(pm, T, (2 * R + 1, 2 * R + 1), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        b = pz["bright"]; patch[..., :3] *= b
        if pz["landed"] or pz["h"] < 60:   # mild pall tint (ambient bounce from the purple cloth) when near/on the surface
            k = 0.07 * (1 - min(pz["h"], 60) / 60.0); patch[..., :3] = patch[..., :3] * (1 - k) + pall_tint * k * patch[..., 3:4]
        patch *= pz["alpha"]
        blend_rgba(frame, patch, ox, oy)
    def _shadow(self, ctx, st, frame, it, pz):
        if pz["alpha"] <= 0 or it["t_rel"] > st.t: return
        # contact shadow on the surface under the petal (grows sharper/darker as it descends; stays when landed)
        if not pz["landed"]:
            x = pz["x"]; y = it["ly"] + 2; hh = min(pz["h"], 120.0); op = 0.42 * (1 - hh / 120.0) ** 1.6; spread = 1.0 + hh / 60.0
        else:
            x = pz["x"] + 2.5; y = pz["y"] + 3.0; op = 0.42; spread = 1.0
        if op < 0.02: return
        sp = self.sprites[it["sid"]]["img"]; rw = max(sp.shape[1], sp.shape[0]) * it["scale"] * 0.42 * spread; rh = rw * 0.32
        M = ctx.camera_fn(0.5, st.t) if ctx.camera_fn else np.array([[1, 0, 0], [0, 1, 0]], np.float32); X, Y = M @ np.array([x, y, 1.0], np.float32)
        R = int(rw * 1.6) + 4; xi, yi = int(round(X)), int(round(Y)); H, W = frame.shape[:2]
        xa, ya, xb, yb = max(xi - R, 0), max(yi - R, 0), min(xi + R + 1, W), min(yi + R + 1, H)
        if xb <= xa or yb <= ya: return
        yy, xx = np.mgrid[ya:yb, xa:xb].astype(np.float32); d = ((xx - X) / rw) ** 2 + ((yy - Y) / rh) ** 2
        a = np.exp(-d * 1.8) * op * pz["alpha"] * self.surf_cam(ctx, st, xa, xb, ya, yb)
        roi = frame[ya:yb, xa:xb]; roi *= (1 - a[..., None] * (1 - np.array([0.30, 0.16, 0.30], np.float32)))
    def surf_cam(self, ctx, st, xa, xb, ya, yb):
        if st.surf_cam is None:
            M = ctx.camera_fn(0.5, st.t) if ctx.camera_fn else np.array([[1, 0, 0], [0, 1, 0]], np.float32)
            st.surf_cam = cv2.warpAffine(self.surf, M, (ctx.W, ctx.H), flags=cv2.INTER_LINEAR)
        return st.surf_cam[ya:yb, xa:xb]
    def post(self, ctx, st, frame):
        st.surf_cam = None; tint = np.array(self.p.get("pall_tint", [92, 24, 62]), np.float32)
        poses = [(it, self._pose(it, st.t)) for it in self.items]
        for it, pz in poses: self._shadow(ctx, st, frame, it, pz)
        # depth sort: landed petals first (behind), then airborne by y
        for it, pz in sorted(poses, key=lambda a: (not a[1]["landed"], a[1]["y"])):
            if pz["alpha"] <= 0.001: continue
            self._render(ctx, st, frame, it, pz, tint)
