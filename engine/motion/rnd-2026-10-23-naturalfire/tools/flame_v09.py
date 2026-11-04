"""v09 flame model = tools/flame.py (v08, unchanged there) + extension zones.
Core (painted fire, masks_v09/P05_fire_ci.png): exactly the v08 model (advected flame paint, intermittency gate, brightness) in delta form.
Extension (masks_v09/P05_fire_ci_ext.png, above each core, only over dark/smoky unprotected px): the static image stays the plate;
  flame paint advected UP out of the core (carried with its own advected alpha) is LIGHTEN-blended over the plate, gated by the same
  intermittency field and faded with height -> tongues travel past the painted edge, detach and die. Zero motion -> alpha 0 -> exact plate.
Height h runs 0 (core base) .. 1 (core top) .. 1+e (top of extension)."""
import numpy as np, cv2
from noise import Perlin3, fbm, Noise1D, BandNoise
from flame import DEFAULT, smoothstep, S_UP
class FlameX:
    def __init__(self, plate, core, ext, src_layer, name, prm, seed):
        self.name, self.src_layer = name, src_layer; self.prm = p = {**DEFAULT, **prm}
        H, W = core.shape; dom = (core > 0) | (ext > 0); ys, xs = np.nonzero(dom); mg = 6
        self.y0, self.y1, self.x0, self.x1 = max(0, ys.min() - mg), min(H, ys.max() + mg + 1), max(0, xs.min() - mg), min(W, xs.max() + mg + 1)
        sl = (slice(self.y0, self.y1), slice(self.x0, self.x1))
        self.m = core[sl].astype(np.float32); self.e = ext[sl].astype(np.float32)
        self.roi = plate[sl].astype(np.float32); h_, w_ = self.m.shape; self.shape = (h_, w_)
        wy = (self.m > 0.5).sum(1); cs = np.cumsum(wy); tot = cs[-1]
        ytop = int(np.searchsorted(cs, 0.005 * tot)); ybot = int(np.searchsorted(cs, 0.995 * tot)); self.Hf = float(ybot - ytop + 1); self.ytop, self.ybot = ytop, ybot
        self.fy = (np.arange(h_ * S_UP) + 0.5) / S_UP - 0.5; self.fx = (np.arange(w_ * S_UP) + 0.5) / S_UP - 0.5
        FY, FX = np.meshgrid(self.fy, self.fx, indexing="ij"); self.FY, self.FX = FY.astype(np.float32), FX.astype(np.float32)
        self.hraw = np.clip((ybot - FY) / self.Hf, 0, 2).astype(np.float32)
        self.hgt = np.minimum(self.hraw, 1.0)                                 # core-model height (as v08)
        eh = max(1.0, float((self.e > 0.05).any(1).sum())) / self.Hf          # extension height in flame heights
        self.efade = (1 - smoothstep(1.0, 1.0 + eh * p.get("ext_reach", 1.0), self.hraw)).astype(np.float32)
        dom_b = ((self.m > 0.5) | (self.e > 0.05)).astype(np.uint8)
        dist = cv2.distanceTransform(np.pad(dom_b, 1), cv2.DIST_L2, 5)[1:-1, 1:-1]
        self.dist4 = cv2.resize(dist, (w_ * S_UP, h_ * S_UP), interpolation=cv2.INTER_LINEAR)
        hole = (self.m < 0.5).astype(np.uint8)
        r8 = np.clip(self.roi, 0, 255).astype(np.uint8); fill = cv2.inpaint(r8, hole, 4, cv2.INPAINT_TELEA).astype(np.float32)
        self.src = np.where(hole[..., None] > 0, fill, self.roi)
        self.up = cv2.resize(self.src, (w_ * S_UP, h_ * S_UP), interpolation=cv2.INTER_LANCZOS4)
        self.up_down = cv2.resize(self.up, (w_, h_), interpolation=cv2.INTER_AREA)
        self.uproi = cv2.resize(self.roi, (w_ * S_UP, h_ * S_UP), interpolation=cv2.INTER_LANCZOS4)
        self.uproi_down = cv2.resize(self.uproi, (w_, h_), interpolation=cv2.INTER_AREA)
        self.a4 = cv2.resize(np.clip(self.m, 0, 1), (w_ * S_UP, h_ * S_UP), interpolation=cv2.INTER_LINEAR)   # flame-paint alpha (advected with the paint)
        bg = cv2.GaussianBlur(self.src, (0, 0), p["dark_blur"]) * np.float32(p["dark"])
        self.bg4 = cv2.resize(np.minimum(bg, self.src), (w_ * S_UP, h_ * S_UP), interpolation=cv2.INTER_LINEAR)
        self.Po = Perlin3(seed * 10 + 6); FX0, FY0 = self.FX + self.x0, self.FY + self.y0
        self.off = (0.5 + 0.5 * np.clip(fbm(self.Po, FX0 / p["osc"], FY0 / p["osc"], 0.0, 2) / 0.5, -1, 1)).astype(np.float32)
        self.Phi = 0.0; self.tlast = 0.0; self.Pd = Perlin3(seed * 10 + 1); self.Px = Perlin3(seed * 10 + 2); self.Pg = Perlin3(seed * 10 + 3); self.Pb = Perlin3(seed * 10 + 4)
        bl, bh = p.get("breath_band", (0.3, 0.6)); tl, th = p.get("tip_band", (2.0, 5.0))
        nb1, nb2, nb3 = BandNoise(seed * 10 + 5, bl, bh), BandNoise(seed * 10 + 7, tl, th), BandNoise(seed * 10 + 8, tl, th)
        self.N1 = lambda t, hz=None, o=None: 0.6 * nb1(t); self.N2 = lambda t, hz=None, o=None: 0.6 * nb2(t); self.N3 = lambda t, hz=None, o=None: 0.6 * nb3(t)
        self.gx = (self.FX + self.x0); self.gy = (self.FY + self.y0)
    def activity(self, t, fcurve):
        p = self.prm; a = p["k_glow"] * (fcurve - 1.0) + p["k_breath"] * 0.25 * self.N1(t)
        fq, fm = getattr(self, "fq", None), getattr(self, "fm", None)
        self.flare = 0.0 if fq is None else float(np.clip((fcurve - fq) / max(fm - fq, 1e-6), 0, 1)) ** 1.5
        return a + p.get("k_flare", 0.0) * self.flare
    def fields(self, t, A):
        p = self.prm; X, Y, h, hr = self.gx, self.gy, self.hgt, self.hraw
        n1 = fbm(self.Pd, X / p["sx"], (Y + p["V"] * t) / p["sy"], p["ev"] * t, 3)
        n2 = fbm(self.Px, X / (p["sx"] * 0.8), (Y + p["V"] * 0.8 * t) / (p["sy"] * 0.7), p["ev"] * 1.3 * t, 2)
        hp_ = hr ** p["p"]
        dy = p["amp_y"] * hp_ * (1 + 0.5 * A) * n1 / 0.35 + p["stretch"] * A * hr * self.Hf + p.get("flare_lift", 0.0) * self.flare * hr * self.Hf
        dx = p["amp_x"] * (h ** p.get("px", p["p"])) * n2 / 0.35
        sc = smoothstep(0.0, p["taper_px"], self.dist4); dx, dy = dx * sc, dy * sc; self.taper = sc
        gx_w = X + p.get("gwarp", 0.0) * n2 / 0.35
        g = fbm(self.Pg, gx_w / p["gsx"], (Y + p["Vg"] * t) / p["gsy"], p["evg"] * t, 3) / 0.35
        tf = self.N2(t)
        c = p["c0"] + (p["c1"] - p["c0"]) * hr - p["cA"] * A + p.get("k_tipfl", 0.0) * tf * np.minimum(hr, 1.3) ** 2
        G = 1 - p["gs"] * np.minimum(hr, 1) ** p["q"] * (1 - smoothstep(c - p["gw"] * 2, c + p["gw"] * 2, g))
        Ge = smoothstep(c - p["gw"] * 2, c + p["gw"] * 2, g + p.get("ext_gate_bias", 0.0))     # extension: only gate-passing tongues
        nb = fbm(self.Pb, X / p["bsx"], Y / p["bsx"], p["evb"] * t, 2) / 0.35
        Bm = 1 + p["kb"] * (1 - h) ** 2 * nb + p["kbright"] * A * (0.4 + 0.6 * h) + p.get("k_tipb", 0.0) * self.N3(t) * h ** 2
        return dx.astype(np.float32), dy.astype(np.float32), G.astype(np.float32), Ge.astype(np.float32), Bm.astype(np.float32)
    def phase(self, t, A):
        p = self.prm
        if t < self.tlast - 1e-9: self.Phi, self.tlast = 0.0, 0.0
        n = int(round((t - self.tlast) * 120)); dt = (t - self.tlast) / max(n, 1)
        for k in range(n): self.Phi += dt / p["T"] * max(0.3, 1 + p["ka"] * A)
        self.tlast = t; return self.Phi
    def render(self, t, fcurve):
        p = self.prm; A = self.activity(t, fcurve); dx, dy, G, Ge, Bm = self.fields(t, A)
        Phi = self.phase(t, A); trav = p["D"] * self.hraw ** p["pD"] * self.taper
        mapx = ((self.FX + dx + 0.5) * S_UP - 0.5).astype(np.float32)
        acc = 0; aacc = 0; ws = []
        for k in (0.0, 0.5):
            ph = np.mod(Phi + self.off + k, 1.0); w = 1 - np.abs(2 * ph - 1)
            mapy = ((self.FY + dy + trav * (ph - 0.5) + 0.5) * S_UP - 0.5).astype(np.float32)
            s = cv2.remap(self.up, mapx, mapy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
            a = cv2.remap(self.a4, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
            acc = acc + s * w[..., None]; aacc = aacc + a * w; ws.append(w)
        wsum = ws[0] + ws[1]; acc = acc / wsum[..., None]; alpha = aacc / wsum
        nrm = np.sqrt(ws[0] ** 2 + ws[1] ** 2) / wsum
        lp = cv2.GaussianBlur(acc, (0, 0), p["hf_sigma"] * S_UP)
        wu = lp + (acc - lp) / nrm[..., None]
        an = (self.bg4 + (wu - self.bg4) * G[..., None]) * Bm[..., None]
        dn = cv2.resize(an, (self.shape[1], self.shape[0]), interpolation=cv2.INTER_AREA)
        # extension: lighten-only flame over the real plate, weight = advected paint alpha x gate x height fade
        we = np.clip(alpha * Ge * self.efade * p.get("ext_gain", 1.0), 0, 1)
        fl = wu * Bm[..., None]; ex = self.uproi + np.maximum(fl - self.uproi, 0) * we[..., None]
        dne = cv2.resize(ex, (self.shape[1], self.shape[0]), interpolation=cv2.INTER_AREA)
        out = self.roi + (dn - self.up_down) * self.m[..., None] + (dne - self.uproi_down) * self.e[..., None]
        self.last = dict(A=A, dmax=float(np.hypot(dx, dy).max()), ext_w=float(we.max()))
        return np.clip(out, 0, 255)
class FlameSetX:
    def __init__(self, E, cores, exts, specs):
        self.E = E; self.plate0 = E.plate.copy(); self.fl = []
        for i, (mk, ex, sp) in enumerate(zip(cores, exts, specs)):
            self.fl.append(FlameX(self.plate0, mk, ex, sp.get("layer", i), sp["name"], sp.get("prm", {}), sp.get("seed", 100 + i)))
        tt = np.arange(0, 6.0, 1 / 120)
        for f in self.fl:
            fc = np.array([self.fcurve(f.src_layer, t) for t in tt]); f.fq, f.fm = float(np.quantile(fc, f.prm.get("flare_q", 0.8))), float(fc.max())
        self.union = np.zeros(cores[0].shape, bool)
        for mk, ex in zip(cores, exts): self.union |= (mk > 0) | (ex > 0)
    def fcurve(self, li, t):
        F = self.E.layers[li][1]; return F._flick(F.src[0], t)
    def plate_at(self, t):
        pl = self.plate0.copy()
        for f in self.fl:   # flames may overlap in ROI boxes: each writes only its own (core|ext) support
            o = f.render(t, self.fcurve(f.src_layer, t)); sup = (f.m > 0) | (f.e > 0)
            pl[f.y0:f.y1, f.x0:f.x1] += (o - f.roi) * sup[..., None]   # additive deltas: overlapping ROI boxes compose
        pl[~self.union] = self.plate0[~self.union]
        return pl
    def render(self, t):
        self.E.plate = self.plate_at(t)
        try: img, dx, dy = self.E.render(t)
        finally: self.E.plate = self.plate0
        return img
def load_masks_v09(d="masks_v09"):
    rd = lambda n: cv2.imread(f"{d}/{n}", cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255.0
    return [rd(f"P05_fire_c{i}.png") for i in range(3)], [rd(f"P05_fire_c{i}_ext.png") for i in range(3)]
