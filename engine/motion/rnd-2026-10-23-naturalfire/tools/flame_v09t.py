"""v09 'tongue' extension (subclass of flame_v09.FlameX; core model unchanged = v08).
Extension: per column, the top band of the (advected) core flame (depth dd = ext_band * Hf) is STRETCHED upward by a lick reach
R(x,t) = lick(x,t) * ext_h * ext_reach (lick = travelling band-limited noise in x and t, raised on flares) -> tongues grow out of the
painted edge, the intermittency gate (rising at Vg) cuts them into detached pieces which rise and die (height fade). Lighten-only over
the real plate; zero lick -> exact plate."""
import numpy as np, cv2
from noise import Perlin3, fbm
from flame import smoothstep, S_UP
from flame_v09 import FlameX, FlameSetX as _FSX, load_masks_v09
class FlameT(FlameX):
    def __init__(self, plate, core, ext, src_layer, name, prm, seed):
        super().__init__(plate, core, ext, src_layer, name, prm, seed)
        # drop narrow ext slivers (e.g. the gap between the c0 column and the pillar guard): keep only parts >= ext_min_w px wide in x
        k = int(prm.get("ext_min_w", 9))
        if k > 1:
            keep = cv2.morphologyEx((self.e > 0.3).astype(np.uint8), cv2.MORPH_OPEN, np.ones((1, k), np.uint8)).astype(np.float32)
            keep = cv2.dilate(keep, np.ones((1, k), np.uint8)); keep = cv2.GaussianBlur(keep, (0, 0), 2.0)
            self.e = (self.e * np.minimum(keep * 1.5, 1.0)).astype(np.float32)
        p = self.prm; h_, w_ = self.shape
        cm = self.m > 0.5; has = cm.any(0); top = np.where(has, cm.argmax(0), -1).astype(np.float32)
        # smooth tops of valid columns (ragged paint edges -> smooth stretch origin)
        xs = np.arange(w_); tv = np.interp(xs, xs[has], top[has]) if has.any() else np.zeros(w_)
        tv = cv2.GaussianBlur(tv.reshape(1, -1).astype(np.float32), (0, 0), 1.0).ravel()
        tu = np.interp(self.fx, xs, tv).astype(np.float32); self.top4 = np.broadcast_to(tu[None, :], self.FY.shape).astype(np.float32)
        self.ehpx = p.get("ext_frac", 0.22) * self.Hf                       # tongue reach scale = the extension height (0.22 Hf), not the ext mask's row span
        # distance to the R&D protected set (faces/hands+margin, gold, stone faces, figures): gate gaps / cells / tongues fade out
        # over gate_edge_px towards protected edges so polygon guard lines never show as straight dark edges
        pr = cv2.imread("masks_v09/P05_rnd_protect.png", 0)[self.y0:self.y1, self.x0:self.x1] > 0
        dp = cv2.distanceTransform((~pr).astype(np.uint8), cv2.DIST_L2, 5)
        self.pfade = cv2.resize(smoothstep(0.0, p.get("gate_edge_px", 7.0), dp).astype(np.float32), (w_ * S_UP, h_ * S_UP), interpolation=cv2.INTER_LINEAR)
        self.Pc = Perlin3(seed * 10 + 12); self.Pl = Perlin3(seed * 10 + 9); self.Pl2 = Perlin3(seed * 10 + 11)
        self.dd = p.get("ext_band", 0.18) * self.Hf
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
        lp = cv2.GaussianBlur(acc, (0, 0), p["hf_sigma"] * S_UP); wu = lp + (acc - lp) / nrm[..., None]
        G = 1 - (1 - G) * self.pfade
        an = (self.bg4 + (wu - self.bg4) * G[..., None]) * Bm[..., None]
        if p.get("kcell", 0.0) > 0:   # rising luminance pockets (turbulent cells carried up at Vc): v09 legibility at phone scale
            nc = fbm(self.Pc, self.gx / p.get("csx", 8.0), (self.gy + p.get("Vc", 60.0) * t) / p.get("csy", 14.0), p.get("evc", 1.2) * t, 2) / 0.35
            f1 = (p["kcell"] * np.clip(nc, -1.5, 1.5) * (0.35 + 0.65 * (1 - self.hgt)) * self.pfade)[..., None]
            wch = np.where(f1 > 0, np.float32([1.0, 0.9, 0.55]), np.float32([0.8, 1.0, 1.2]))   # brighter -> yellower, darker -> redder (no white/grey)
            an1 = an * (1 + f1 * wch); base = np.maximum(an, 205.0); room = np.maximum(255.0 - base, 1.0)
            an = np.where(an1 > base, base + room * np.tanh((an1 - base) / room), an1)            # soft knee on the INCREASE only: no clipping/white smear, static paint untouched
        dn = cv2.resize(an, (self.shape[1], self.shape[0]), interpolation=cv2.INTER_AREA)
        # ---- tongues: stretch the top band of the advected flame upward by R(x,t)
        X = self.gx[0]                                                       # 1-D x (up grid)
        ln = fbm(self.Pl, X / p.get("lick_sx", 7.0), 0.0 * X, p.get("lick_ev", 1.6) * t, 2) / 0.35 \
            + 0.5 * fbm(self.Pl2, X / (p.get("lick_sx", 7.0) * 0.5), 0.0 * X, p.get("lick_ev", 1.6) * 2.1 * t, 1) / 0.35
        lv = ln * (1 + p.get("lick_A", 0.6) * A) + p.get("lick_flare", 0.5) * self.flare - p.get("lick_thr", 0.1)
        lk = np.clip(lv / 1.2, 0, 1) ** p.get("lick_pow", 1.6)                 # peaked (not plateau) -> pointed tongues, no flat-topped bars
        R = (lk * self.ehpx * p.get("ext_reach", 1.0)).astype(np.float32)[None, :]
        d = self.top4 - self.FY                                              # px above the (smoothed) painted top
        u = np.clip((d + self.dd) / (self.dd + R + 1e-3), 0, 1.5)            # 0 at band bottom .. 1 at tongue tip
        ysrc = self.top4 + self.dd - u * self.dd
        my = ((ysrc + 0.5) * S_UP - 0.5).astype(np.float32); mx = ((self.FX + 0.6 * dx + 0.5) * S_UP - 0.5).astype(np.float32)
        fl = cv2.remap(wu * Bm[..., None], mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        ae = cv2.remap(alpha, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        tip = 1 - smoothstep(p.get("tip_soft", 0.75), 1.0, u)               # soft tongue tip
        we = np.clip(ae * Ge * tip * self.efade * self.pfade * p.get("ext_gain", 1.0) * (d > -1), 0, 1)
        lum = lambda X: X[..., 0] * 0.299 + X[..., 1] * 0.587 + X[..., 2] * 0.114
        kb_ = np.clip((lum(fl) - lum(self.uproi)) / 40.0, 0, 1)                 # flame light only where the tongue is brighter (luma), hue kept (no per-channel 'pink' lighten)
        ex = self.uproi + (fl - self.uproi) * (we * kb_)[..., None]
        dne = cv2.resize(ex, (self.shape[1], self.shape[0]), interpolation=cv2.INTER_AREA)
        out = self.roi + (dn - self.up_down) * self.m[..., None] + (dne - self.uproi_down) * self.e[..., None]
        self.last = dict(A=A, dmax=float(np.hypot(dx, dy).max()), ext_w=float(we.max()), lick=float(lk.mean()))
        return np.clip(out, 0, 255)
class FlameSetX(_FSX):
    def __init__(self, E, cores, exts, specs):
        import flame_v09; old = flame_v09.FlameX; flame_v09.FlameX = FlameT
        try: super().__init__(E, cores, exts, specs)
        finally: flame_v09.FlameX = old
