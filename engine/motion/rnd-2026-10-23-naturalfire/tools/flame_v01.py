"""Natural-fire plate animation inside the P05 flame masks (R&D 2026-10-23).
Moves ONLY the painted flame pixels, inside the feathered flame masks; everything else is the exact plate.
Model per flame (plate px, t in s):
  h(x,y)          = height above the flame base, 0 base .. 1 top of mask
  activity A(t)   = k_glow*(f_i(t)-1) + k_breath*n_breath(t)   f_i = THE v2c flicker curve of the matching glow layer (coupling)
  displacement    : source = (x + dx, y + dy); dy>0 samples from below => content moves UP.
                    dy = amp_y*h^p*(1+0.5A)*fbm(x/sx, (y+V*t)/sy, ev*t) + stretch*A*h*Hf   (upward-advected, non-periodic)
                    dx = amp_x*h^p*fbm2(...)                                                (small lateral eddies)
                    |d| clamped to clamp_k * distance-to-mask-edge  -> 0 at the edge, never samples outside the flame
  intermittency   : G = 1 - gs*h^q*(1-smoothstep(c(h,A) - w, c(h,A) + w, gate_noise(x, y+Vg*t, evg*t)))
                    the gate pattern rises faster than the body -> tongues separate at the top, rise and fade (wisps)
  out             = B + (Warp(plate) - B)*G, B = dim ember background (low-passed plate * dark_tint)
  base breathing  : *(1 + kb*(1-h)^2 * cell_noise(x, y, evb*t))  (coals: brightness only, no displacement)
Warp: plate ROI upsampled x4 (Lanczos), remapped bicubic, INTER_AREA down; applied as a delta so zero displacement = exact plate."""
import numpy as np, cv2, math
from noise import Perlin3, fbm, Noise1D
S_UP = 4
def smoothstep(a, b, x): t = np.clip((x - a) / (b - a + 1e-9), 0, 1); return t * t * (3 - 2 * t)
DEFAULT = dict(V=60.0, sx=7.0, sy=11.0, ev=1.1, amp_y=2.6, amp_x=1.0, p=1.3, stretch=0.05, clamp_k=0.7, Vg=80.0, gsx=5.0, gsy=9.0, evg=1.6,
               gs=0.75, q=1.4, c0=-0.35, c1=0.25, cA=0.25, gw=0.10, dark=(0.55, 0.36, 0.22), dark_blur=3.0, kb=0.06, evb=0.5, bsx=6.0,
               k_glow=1.0, k_breath=0.5, breath_hz=0.45, kbright=0.10, seed=0)
class Flame:
    def __init__(self, plate, mask, src_layer, name, prm, seed):
        self.name, self.src_layer = name, src_layer; self.prm = p = {**DEFAULT, **prm}
        H, W = mask.shape; ys, xs = np.nonzero(mask > 0); mg = 6
        self.y0, self.y1, self.x0, self.x1 = max(0, ys.min() - mg), min(H, ys.max() + mg + 1), max(0, xs.min() - mg), min(W, xs.max() + mg + 1)
        self.m = mask[self.y0:self.y1, self.x0:self.x1].astype(np.float32)
        self.roi = plate[self.y0:self.y1, self.x0:self.x1].astype(np.float32)
        h_, w_ = self.m.shape; self.shape = (h_, w_)
        # height coordinate from the mask's weighted vertical extent
        wy = (self.m > 0.5).sum(1); cs = np.cumsum(wy); tot = cs[-1]
        ytop = int(np.searchsorted(cs, 0.005 * tot)); ybot = int(np.searchsorted(cs, 0.995 * tot)); self.Hf = float(ybot - ytop + 1)
        self.ytop, self.ybot = ytop, ybot
        # 4x grids (plate-px coordinates of each fine sample centre)
        self.fy = (np.arange(h_ * S_UP) + 0.5) / S_UP - 0.5; self.fx = (np.arange(w_ * S_UP) + 0.5) / S_UP - 0.5
        FY, FX = np.meshgrid(self.fy, self.fx, indexing="ij"); self.FY, self.FX = FY.astype(np.float32), FX.astype(np.float32)
        self.hgt = np.clip((ybot - FY) / self.Hf, 0, 1).astype(np.float32)
        m_bin = (self.m > 0.5).astype(np.uint8)
        dist = cv2.distanceTransform(np.pad(m_bin, 1), cv2.DIST_L2, 5)[1:-1, 1:-1]
        self.dist4 = cv2.resize(dist, (w_ * S_UP, h_ * S_UP), interpolation=cv2.INTER_LINEAR)
        self.up = cv2.resize(self.roi, (w_ * S_UP, h_ * S_UP), interpolation=cv2.INTER_LANCZOS4)
        self.up_down = cv2.resize(self.up, (w_, h_), interpolation=cv2.INTER_AREA)
        bg = cv2.GaussianBlur(self.roi, (0, 0), p["dark_blur"]) * np.float32(p["dark"])
        self.bg4 = cv2.resize(np.minimum(bg, self.roi), (w_ * S_UP, h_ * S_UP), interpolation=cv2.INTER_LINEAR)
        self.Pd = Perlin3(seed * 10 + 1); self.Px = Perlin3(seed * 10 + 2); self.Pg = Perlin3(seed * 10 + 3); self.Pb = Perlin3(seed * 10 + 4)
        self.N1 = Noise1D(seed * 10 + 5)
        self.gx = (self.FX + self.x0); self.gy = (self.FY + self.y0)   # global plate coords for noise (continuity irrelevant, but deterministic)
    def activity(self, t, fcurve):
        p = self.prm; return p["k_glow"] * (fcurve - 1.0) + p["k_breath"] * 0.25 * self.N1(t, p["breath_hz"], 2)
    def fields(self, t, A):
        p = self.prm; X, Y, h = self.gx, self.gy, self.hgt
        n1 = fbm(self.Pd, X / p["sx"], (Y + p["V"] * t) / p["sy"], p["ev"] * t, 3)
        n2 = fbm(self.Px, X / (p["sx"] * 0.8), (Y + p["V"] * 0.8 * t) / (p["sy"] * 0.7), p["ev"] * 1.3 * t, 2)
        hp_ = h ** p["p"]
        dy = p["amp_y"] * hp_ * (1 + 0.5 * A) * n1 / 0.35 + p["stretch"] * A * h * self.Hf
        dx = p["amp_x"] * hp_ * n2 / 0.35
        mag = np.hypot(dx, dy) + 1e-6; lim = p["clamp_k"] * self.dist4; sc = np.minimum(1.0, lim / mag)
        dx, dy = dx * sc, dy * sc
        g = fbm(self.Pg, X / p["gsx"], (Y + p["Vg"] * t) / p["gsy"], p["evg"] * t, 3) / 0.35   # ~unit std
        c = p["c0"] + (p["c1"] - p["c0"]) * h - p["cA"] * A        # threshold rises with height; flares lower it (more flame)
        G = 1 - p["gs"] * h ** p["q"] * (1 - smoothstep(c - p["gw"] * 2, c + p["gw"] * 2, g))
        nb = fbm(self.Pb, X / p["bsx"], Y / p["bsx"], p["evb"] * t, 2) / 0.35
        Bm = 1 + p["kb"] * (1 - h) ** 2 * nb + p["kbright"] * A * (0.4 + 0.6 * h)
        return dx.astype(np.float32), dy.astype(np.float32), G.astype(np.float32), Bm.astype(np.float32)
    def render(self, t, fcurve):
        A = self.activity(t, fcurve); dx, dy, G, Bm = self.fields(t, A)
        mapx = ((self.FX + dx + 0.5) * S_UP - 0.5).astype(np.float32); mapy = ((self.FY + dy + 0.5) * S_UP - 0.5).astype(np.float32)
        wu = cv2.remap(self.up, mapx, mapy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        an = self.bg4 + (wu - self.bg4) * G[..., None]
        an = an * Bm[..., None]
        dn = cv2.resize(an, (self.shape[1], self.shape[0]), interpolation=cv2.INTER_AREA)
        out = self.roi + (dn - self.up_down)                      # delta: identity warp, G=1, Bm=1 -> exact plate
        out = self.roi + (out - self.roi) * self.m[..., None]     # feathered mask; 0 outside
        self.last = dict(A=A, dmax=float(np.hypot(dx, dy).max()), dx=dx, dy=dy, G=G)
        return np.clip(out, 0, 255)
class FlameSet:
    def __init__(self, E, masks, specs):
        self.E = E; self.plate0 = E.plate.copy(); self.fl = []
        for i, (mk, sp) in enumerate(zip(masks, specs)):
            self.fl.append(Flame(self.plate0, mk, sp.get("layer", i), sp["name"], sp.get("prm", {}), sp.get("seed", 100 + i)))
        self.union = np.zeros(masks[0].shape, bool)
        for mk in masks: self.union |= mk > 0
    def fcurve(self, li, t):
        F = self.E.layers[li][1]; return F._flick(F.src[0], t)
    def plate_at(self, t):
        pl = self.plate0.copy()
        for f in self.fl:
            pl[f.y0:f.y1, f.x0:f.x1] = f.render(t, self.fcurve(f.src_layer, t))
        pl[~self.union] = self.plate0[~self.union]                # hard guarantee: nothing outside the flame masks changes
        return pl
    def render(self, t):
        self.E.plate = self.plate_at(t)
        try: img, dx, dy = self.E.render(t)
        finally: self.E.plate = self.plate0
        return img
