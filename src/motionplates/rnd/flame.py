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
from noise import Perlin3, fbm, Noise1D, BandNoise
S_UP = 4
def smoothstep(a, b, x): t = np.clip((x - a) / (b - a + 1e-9), 0, 1); return t * t * (3 - 2 * t)
DEFAULT = dict(V=60.0, sx=7.0, sy=11.0, ev=1.1, amp_y=2.6, amp_x=1.0, p=1.3, stretch=0.05, clamp_k=0.7, Vg=80.0, gsx=5.0, gsy=9.0, evg=1.6,
               gs=0.75, q=1.4, c0=-0.35, c1=0.25, cA=0.25, gw=0.10, dark=(0.55, 0.36, 0.22), dark_blur=3.0, kb=0.06, evb=0.5, bsx=6.0,
               k_glow=1.0, T=0.8, D=14.0, pD=1.2, ka=1.2, osc=9.0, hf_sigma=1.2, k_breath=0.5, breath_hz=0.45, kbright=0.10, seed=0)
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
        hole = (self.m < 0.5).astype(np.uint8)
        r8 = np.clip(self.roi, 0, 255).astype(np.uint8); fill = cv2.inpaint(r8, hole, 4, cv2.INPAINT_TELEA).astype(np.float32)
        self.src = np.where(hole[..., None] > 0, fill, self.roi)   # flame paint only (non-flame px replaced by inpainted flame paint)
        self.up = cv2.resize(self.src, (w_ * S_UP, h_ * S_UP), interpolation=cv2.INTER_LANCZOS4)
        self.up_down = cv2.resize(self.up, (w_, h_), interpolation=cv2.INTER_AREA)
        bg = cv2.GaussianBlur(self.src, (0, 0), p["dark_blur"]) * np.float32(p["dark"])
        self.bg4 = cv2.resize(np.minimum(bg, self.src), (w_ * S_UP, h_ * S_UP), interpolation=cv2.INTER_LINEAR)
        self.Po = Perlin3(seed * 10 + 6); FX0, FY0 = self.FX + self.x0, self.FY + self.y0
        self.off = (0.5 + 0.5 * np.clip(fbm(self.Po, FX0 / p["osc"], FY0 / p["osc"], 0.0, 2) / 0.5, -1, 1)).astype(np.float32)  # per-pixel cycle offset 0..1
        self.Phi = 0.0; self.tlast = 0.0; self.Pd = Perlin3(seed * 10 + 1); self.Px = Perlin3(seed * 10 + 2); self.Pg = Perlin3(seed * 10 + 3); self.Pb = Perlin3(seed * 10 + 4)
        self.N1 = Noise1D(seed * 10 + 5); self.N2 = Noise1D(seed * 10 + 7); self.N3 = Noise1D(seed * 10 + 8)
        if self.prm.get("band"):   # v08+: true band-limited drivers (breath 0.3-0.6 Hz, tips 2-5 Hz)
            bl, bh = self.prm.get("breath_band", (0.3, 0.6)); tl, th = self.prm.get("tip_band", (2.0, 5.0))
            nb1, nb2, nb3 = BandNoise(seed * 10 + 5, bl, bh), BandNoise(seed * 10 + 7, tl, th), BandNoise(seed * 10 + 8, tl, th)
            self.N1 = lambda t, hz=None, o=None: 0.6 * nb1(t); self.N2 = lambda t, hz=None, o=None: 0.6 * nb2(t)
            self.N3 = lambda t, hz=None, o=None: 0.6 * nb3(t)
        self.gx = (self.FX + self.x0); self.gy = (self.FY + self.y0)   # global plate coords for noise (continuity irrelevant, but deterministic)
    def activity(self, t, fcurve):
        # glow-coupled activity: linear in the v2c flicker + a flare term that only fires on the glow's upper peaks
        p = self.prm; a = p["k_glow"] * (fcurve - 1.0) + p["k_breath"] * 0.25 * self.N1(t, p["breath_hz"], 2)
        fq, fm = getattr(self, "fq", None), getattr(self, "fm", None)
        self.flare = 0.0 if fq is None else float(np.clip((fcurve - fq) / max(fm - fq, 1e-6), 0, 1)) ** 1.5
        return a + p.get("k_flare", 0.0) * self.flare
    def fields(self, t, A):
        p = self.prm; X, Y, h = self.gx, self.gy, self.hgt
        n1 = fbm(self.Pd, X / p["sx"], (Y + p["V"] * t) / p["sy"], p["ev"] * t, 3)
        n2 = fbm(self.Px, X / (p["sx"] * 0.8), (Y + p["V"] * 0.8 * t) / (p["sy"] * 0.7), p["ev"] * 1.3 * t, 2)
        hp_ = h ** p["p"]
        dy = p["amp_y"] * hp_ * (1 + 0.5 * A) * n1 / 0.35 + p["stretch"] * A * h * self.Hf + p.get("flare_lift", 0.0) * self.flare * h * self.Hf
        dx = p["amp_x"] * hp_ * n2 / 0.35
        if p.get("taper_px"):   # source is flame-only (inpainted), so only a soft edge taper is needed
            sc = smoothstep(0.0, p["taper_px"], self.dist4)
        else:
            mag = np.hypot(dx, dy) + 1e-6; lim = p["clamp_k"] * self.dist4; sc = np.minimum(1.0, lim / mag)
        dx, dy = dx * sc, dy * sc; self.taper = sc
        gx_w = X + p.get("gwarp", 0.0) * n2 / 0.35                                               # gaps follow the lateral eddies
        g = fbm(self.Pg, gx_w / p["gsx"], (Y + p["Vg"] * t) / p["gsy"], p["evg"] * t, 3) / 0.35   # ~unit std
        tf = self.N2(t, p.get("tip_hz", 3.0), 2)                    # tip-height puffing, 2-6 Hz, non-periodic
        c = p["c0"] + (p["c1"] - p["c0"]) * h - p["cA"] * A + p.get("k_tipfl", 0.0) * tf * h ** 2   # threshold rises with height; flares lower it
        G = 1 - p["gs"] * h ** p["q"] * (1 - smoothstep(c - p["gw"] * 2, c + p["gw"] * 2, g))
        nb = fbm(self.Pb, X / p["bsx"], Y / p["bsx"], p["evb"] * t, 2) / 0.35
        Bm = 1 + p["kb"] * (1 - h) ** 2 * nb + p["kbright"] * A * (0.4 + 0.6 * h) + p.get("k_tipb", 0.0) * self.N3(t, p.get("tip_hz", 3.0) * 1.3, 2) * h ** 2
        return dx.astype(np.float32), dy.astype(np.float32), G.astype(np.float32), Bm.astype(np.float32)
    def phase(self, t, A):
        # integrated cycle phase; flares speed the upward stream (glow-coupled), never runs backwards
        p = self.prm
        if t < self.tlast - 1e-9: self.Phi, self.tlast = 0.0, 0.0
        n = int(round((t - self.tlast) * 120)); dt = (t - self.tlast) / max(n, 1)
        for k in range(n): self.Phi += dt / p["T"] * max(0.3, 1 + p["ka"] * A)
        self.tlast = t; return self.Phi
    def render(self, t, fcurve):
        p = self.prm; A = self.activity(t, fcurve); dx, dy, G, Bm = self.fields(t, A)
        Phi = self.phase(t, A); trav = p["D"] * self.hgt ** p["pD"] * (self.taper if p.get("taper_px") else 1.0)          # px of upward travel per cycle (0 at base)
        mapx = ((self.FX + dx + 0.5) * S_UP - 0.5).astype(np.float32)
        acc = 0; ws = []
        for k in (0.0, 0.5):
            ph = np.mod(Phi + self.off + k, 1.0); w = 1 - np.abs(2 * ph - 1)       # triangle weight, 0 at the reset
            mapy = ((self.FY + dy + trav * (ph - 0.5) + 0.5) * S_UP - 0.5).astype(np.float32)
            s = cv2.remap(self.up, mapx, mapy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
            acc = acc + s * w[..., None]; ws.append(w)
        wsum = ws[0] + ws[1]; acc = acc / wsum[..., None]
        nrm = np.sqrt(ws[0] ** 2 + ws[1] ** 2) / wsum                              # variance-preserving detail re-injection
        lp = cv2.GaussianBlur(acc, (0, 0), p["hf_sigma"] * S_UP)
        wu = lp + (acc - lp) / nrm[..., None]
        an = self.bg4 + (wu - self.bg4) * G[..., None]
        an = an * Bm[..., None]
        dn = cv2.resize(an, (self.shape[1], self.shape[0]), interpolation=cv2.INTER_AREA)
        out = self.roi + (dn - self.up_down)    # up_down = Down(Up(src)); identity -> exact plate                      # delta: identity warp, G=1, Bm=1 -> exact plate
        out = self.roi + (out - self.roi) * self.m[..., None]     # feathered mask; 0 outside
        self.last = dict(A=A, dmax=float(np.hypot(dx, dy).max()), dx=dx, dy=dy, G=G)
        return np.clip(out, 0, 255)
class FlameSet:
    def __init__(self, E, masks, specs):
        self.E = E; self.plate0 = E.plate.copy(); self.fl = []
        for i, (mk, sp) in enumerate(zip(masks, specs)):
            self.fl.append(Flame(self.plate0, mk, sp.get("layer", i), sp["name"], sp.get("prm", {}), sp.get("seed", 100 + i)))
        tt = np.arange(0, 6.0, 1 / 120)
        for f in self.fl:
            fc = np.array([self.fcurve(f.src_layer, t) for t in tt]); f.fq, f.fm = float(np.quantile(fc, f.prm.get("flare_q", 0.8))), float(fc.max())
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
