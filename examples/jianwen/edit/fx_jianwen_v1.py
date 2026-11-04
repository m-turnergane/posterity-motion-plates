"""Jianwen v1 -- per-plate fire / light-spill / atmosphere animation. ADAPTED COPY of edward-ii/edit/fx_v1c.py (that file is untouched).
Same locked house-candle-lightspill-v1 maths. Jianwen additions:
  * kind "bigfire" (burning roofs, brazier, campfire, distant city): painted flame SHAPE stays static; glow pulse + local spill only.
  * kind "lantern" (paper lanterns): flicker + glow + spill, plus a gentle pendulum SWAY of the lantern ROI about its cord pivot
    (<= ~1.2 deg, feathered mask limited to the lantern box: never land, faces or water).
  * candle-sized flames keep the locked flame_warp (shape motion); torches keep painted shapes (glow + spill only), as in Edward.
  * embers default to 2.2-3.6 plate px so they still read at 360x640 (Edward's 0.9-1.7 px vanish on a phone).
  * SPECS are per-plate ROIs in PLATE PIXELS and cannot be written until the plates exist: every entry below is a TEMPLATE
    (todo=True). The build refuses to render a plate whose spec is still todo (use --test-frames / --fx-overlays to fill them).
"""
import math, json, importlib.util
from pathlib import Path
import numpy as np, cv2

_ENG = "/workspace/posterity/motion/presets/locked/engine/animate_b3_cb9e2b88.py"
_spec = importlib.util.spec_from_file_location("lockeng", _ENG); LE = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(LE)
cv2.setNumThreads(1)
pnoise, scroll, smoothstep, lum, gauss_dot = LE.pnoise, LE.scroll, LE.smoothstep, LE.lum, LE.gauss_dot
LOCK = json.load(open("/workspace/posterity/motion/presets/locked/house-candle-lightspill-v1.json"))["layers"][0]["params"]
LSRC = LOCK["sources"][0]; LFL = LSRC["flicker"]; LWARP = LOCK["flame_warp"]; LPF = LOCK["plate_flame"]; LPOOL = LOCK["light_pool"]; LSP = LOCK["light_spill"][0]

# ------------------------------------------------------------------------------------------------ per-plate specs (plate px, 941x1672)
WARM_HAZE = (255, 196, 140); COOL_MIST = (196, 204, 220)
# TEMPLATES ONLY (no plates yet). Fill rects from the real plates with build_rough_jianwen_v1.py --fx-overlays, then drop todo=True.
# keys: auto/manual (candle flames), torch, bigfire, lantern=[dict(rect=(x0,y0,x1,y1), pivot=(x,y), amp_deg=1.0)], window, offscreen,
#       relight_exclude/relight_poly, spill_amp, haze, mist (+mist_exclude), motes, embers=[dict(spawn=[(x,y,rx,ry)], n=)], smoke, parallax
T = dict(todo=True)
SPECS = {
 "j01": dict(T, plan="bigfire: burning roof (static shape, pulse+spill on bearers/robes) | torch: soldiers' torches | embers off the roofline | warm haze lit"),
 "j02": dict(T, plan="manual/auto: single tall candle (shape motion) | spill on face/robe | warm haze + lit motes"),
 "j03": dict(T, plan="auto: candle rows on bronze stands | grouped spill | haze"),
 "j04": dict(T, plan="torch: wall torches | spill on armour/brick | optional thin snow-mist band (no land warp)"),
 "j05": dict(T, plan="auto: desk candles | lantern: paper lantern (pivot at cord) | spill on edicts/courier"),
 "j06": dict(T, plan="torch: massed army torches | spill on gate leaves/brick | faint smoke haze | NO war sfx"),
 "j07": dict(T, plan="bigfire: burning hall (static) | dense embers + smoke above roofline | spill on courtyard"),
 "j08": dict(T, plan="torch: pole torches | spill on mourners/coffin | faint smoke"),
 "j09": dict(T, plan="manual: single low candle | spill on floor/bedding/shoes | lit motes"),
 "j10": dict(T, plan="auto: candle rows | bigfire: brazier | spill up onto Yongle"),
 "j11": dict(T, plan="lantern: hanging paper lantern (sway) | spill on the two faces"),
 "j12": dict(T, plan="bigfire: campfire + embers + smoke | lantern: temple lantern (sway) | valley mist"),
 "j13": dict(T, plan="lantern: deck lanterns (small sway) | torch: quay torches | relight_exclude + mist_exclude the WATER (reflections static)"),
 "j14": dict(T, plan="torch: guards' torches | spill on Hu Ying/gate | dust haze"),
 "j15": dict(T, plan="manual: single low candle (shape motion) | strong local spill on both faces"),
 "j16": dict(T, plan="window: light gap under the door (flicker+spill on floor only) | manual: small candle by the blank page"),
 "j17": dict(T, plan="bigfire: distant city glow | lantern: paper lantern (sway) | embers + smoke + ground mist"),
 "outro": dict(T, plan="lantern: temple lantern (sway) | mist + few embers; relight_exclude/mist_exclude the baked lettering box"),
}

def plate_key(path):
    n = Path(path).name; return "outro" if "outro" in n else n.split("_")[0]
def spec_todo(path): k = plate_key(path); return k not in SPECS or bool(SPECS[k].get("todo", False))

# ------------------------------------------------------------------------------------------------ detection
def _L(a): return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
def detect_cores(P, rect, excl):
    x0, y0, x1, y1 = rect; pad = 16; X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(P.shape[1], x1 + pad), min(P.shape[0], y1 + pad)
    a = P[Y0:Y1, X0:X1].astype(np.float32); L = _L(a); bg = cv2.GaussianBlur(L, (0, 0), 4)
    core = (a[..., 0] >= 246) & (a[..., 1] >= 212) & (a[..., 2] >= 140) & (L - bg >= 22)
    n, lab, st, cen = cv2.connectedComponentsWithStats(core.astype(np.uint8), 8)
    out = []
    for i in range(1, n):
        x, y, w, h, A = st[i]; gx, gy = x + X0, y + Y0; cx, cy = gx + w / 2, gy + h / 2
        if not (2 <= A <= 400) or w > 1.25 * h + 1: continue
        if not (x0 <= cx < x1 and y0 <= cy < y1): continue
        if any(ex0 <= cx < ex1 and ey0 <= cy < ey1 for ex0, ey0, ex1, ey1 in excl): continue
        out.append([gx, gy, gx + w, gy + h])
    merged = True                       # one candle = one flame: merge cores that belong to the same flame (stacked / split cores)
    while merged:
        merged = False
        for i in range(len(out)):
            for j in range(i + 1, len(out)):
                a, b = out[i], out[j]; ha = max(a[3] - a[1], b[3] - b[1])
                if abs((a[0] + a[2]) / 2 - (b[0] + b[2]) / 2) <= max(3, (a[2] - a[0] + b[2] - b[0]) / 2) and abs((a[1] + a[3]) / 2 - (b[1] + b[3]) / 2) <= 1.6 * ha + 2:
                    out[i] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]; del out[j]; merged = True; break
            if merged: break
    return [tuple(o) for o in out]

def teardrop(P, core):
    cx0, cy0, cx1, cy1 = core; ch = cy1 - cy0; cw = cx1 - cx0
    h = max(4.0, ch * 1.7 + 1); base = cy1 + 0.5; cx = (cx0 + cx1) / 2; fw = max(cw + 2.0, 3.0)
    bx0, by0, bx1, by1 = int(cx - fw - 2), int(base - h - 2), int(cx + fw + 3), int(base + 3)
    bx0, by0 = max(0, bx0), max(0, by0); bx1, by1 = min(P.shape[1], bx1), min(P.shape[0], by1)
    yy, xx = np.mgrid[by0:by1, bx0:bx1].astype(np.float32); vy = (base - yy) / h; vx = (xx - cx + 0.5) / (fw / 2 + 0.5)
    width = np.clip(1 - vy, 0, 1) ** 0.7 * (0.6 + 0.4 * np.clip(vy * 4, 0, 1)) + 0.25 * (vy < 0.15)
    shape = np.clip(1 - (vx / (width + 1e-3)) ** 2, 0, 1) * (vy > -0.15) * (vy < 1.05)
    V = P[by0:by1, bx0:bx1].max(-1).astype(np.float32)
    m = np.clip(shape * 3, 0, 1) * smoothstep(120, 180, V)
    m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.7)
    return dict(bb=(bx0, by0, bx1, by1), mask=m, x=cx, base=base, h=h, w=fw)

def blob(P, rect, kind):
    x0, y0, x1, y1 = rect; a = P[y0:y1, x0:x1].astype(np.float32); L = _L(a); Lm = float(L.max())
    if kind == "manual":
        core = L >= max(225.0, 0.92 * Lm); lo = (L >= max(185.0, 0.74 * Lm)) & (a[..., 0] >= 200)
    elif kind == "torch":
        core = L >= 0.85 * Lm; lo = (L >= max(140.0, 0.55 * Lm)) & (a[..., 0] >= 170)
    else:
        core = L >= 0.85 * Lm; lo = L >= max(90.0, 0.55 * Lm)
    n, lab = cv2.connectedComponents(lo.astype(np.uint8), connectivity=8)
    keep = np.isin(lab, np.unique(lab[core & (lab > 0)])) if n > 1 else lo
    if kind == "torch": keep = lo
    m = cv2.GaussianBlur(cv2.dilate(keep.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), 1.0 if kind != "torch" else 1.6)
    ys, xs = np.nonzero(keep); 
    if len(ys) == 0: return None
    cyc, cxc = np.nonzero(core); cx = x0 + float(cxc.mean()) if len(cxc) else x0 + float(xs.mean())
    return dict(bb=(x0, y0, x1, y1), mask=m.astype(np.float32), x=cx, base=float(y0 + ys.max() + 1), h=float(ys.max() - ys.min() + 1), w=float(xs.max() - xs.min() + 1))

# ------------------------------------------------------------------------------------------------ flicker (locked _flick)
def mk_flick(rng, ampx):
    return dict(amps=[a * ampx for a in LFL["amps"]], fq=np.float32(LFL["freqs"]) * rng.uniform(0.85, 1.15, 4), fr=rng.uniform(0, 6.28, 4),
                noise=rng.standard_normal(4096), nz=LFL["noise"] * ampx, nhz=LFL["noise_hz"], floor=LFL["floor"])
def flick(F, t):
    a = 0.0
    for amp, f, ph in zip(F["amps"], F["fq"], F["fr"]): a += amp * math.sin(2 * math.pi * f * t + ph)
    i = t * F["nhz"]; j = int(i) % 4095; fr = i - int(i); fr = fr * fr * (3 - 2 * fr)
    return max(F["floor"], 1 + a + F["nz"] * (F["noise"][j] * (1 - fr) + F["noise"][j + 1] * fr))

def _rectmask(shape, rects, feather=0, polys=None):
    m = np.zeros(shape, np.float32)
    for r in rects or []: x0, y0, x1, y1 = r[:4]; m[max(0, y0):y1, max(0, x0):x1] = 1
    for p in polys or []: cv2.fillPoly(m, [np.int32(p)], 1.0)
    if feather: m = cv2.GaussianBlur(m, (0, 0), feather)
    return m

# per-plate pulse calibration (measured 2026-10-29, 3 s @30 fps): scale = min(near-source swing -> ~32 % p-p, whole-frame mean swing <= 15 % p-p, max step <= 6 %/frame)
PULSE = dict()   # Jianwen: calibrate per plate on the real plates (same targets); until then the build uses PULSE_DEFAULT
PULSE_DEFAULT = 0.35

# the locked spill radius (800 px on a 720-px plate) lights the whole frame; on these 941-px painted plates that read as whole-frame pumping,
# so v1c keeps spill local to each source: candle/torch radius x LOCAL, explicit off-screen radii x 0.6
LOCAL = 0.32

class PlateFX:
    def __init__(self, plate_path, seed=0):
        self.key = plate_key(plate_path); self.sp = SPECS.get(self.key, {}); sp = self.sp
        self.P = np.asarray(cv2.cvtColor(cv2.imread(str(plate_path)), cv2.COLOR_BGR2RGB)); H, W = self.P.shape[:2]; self.H, self.W = H, W
        self.Pf = self.P.astype(np.float32)
        rng = np.random.default_rng(1326 + seed + sum(map(ord, self.key)))
        self.srcs = []
        for r in sp.get("auto", []):
            for c in detect_cores(self.P, r, sp.get("exclude", [])):
                s = teardrop(self.P, c); s["kind"] = "candle"; self.srcs.append(s)
        for r in sp.get("manual", []):
            s = blob(self.P, r, "manual"); s and (s.update(kind="candle"), self.srcs.append(s))
        for r in sp.get("torch", []):
            s = blob(self.P, r, "torch"); s and (s.update(kind="torch"), self.srcs.append(s))
        for r in sp.get("bigfire", []):
            s = blob(self.P, r, "torch"); s and (s.update(kind="bigfire"), self.srcs.append(s))
        self.sway = []
        for L in sp.get("lantern", []):
            s = blob(self.P, L["rect"], "window")
            if s: s.update(kind="lantern"); self.srcs.append(s); self.sway.append(dict(L, ph=float(rng.uniform(0, 6.28))))
        for r in sp.get("window", []):
            s = blob(self.P, r, "window"); s and (s.update(kind="window"), self.srcs.append(s))
        for o in sp.get("offscreen", []):
            self.srcs.append(dict(kind="offscreen", x=o["xy"][0], base=o["xy"][1], h=o["h"], w=o["h"] / 2, bb=None, mask=None, radius=o["radius"] * 0.6))
        wa = sp.get("window_amp", 1.0); rm = sp.get("radius_mult", 1.0)
        for s in self.srcs:
            k = s["kind"]; s["F"] = mk_flick(rng, {"candle": 1.35, "torch": 1.5, "bigfire": 1.4, "lantern": 1.2, "offscreen": 1.5, "window": 0.8 * wa}[k])
            s["ftex"] = pnoise(rng, 256, 64, 18, 2, ay=1.8)
            hn = s["h"] / 26.0
            if "radius" not in s:
                s["radius"] = (LSP["radius"] * 1.3 * LOCAL * float(np.clip(hn, 0.2, 1.6)) ** 0.7 if k == "candle" else
                               LSP["radius"] * 1.3 * LOCAL * float(np.clip(hn, 0.5, 3.0)) ** 0.5 if k in ("torch", "lantern") else
                               LSP["radius"] * 1.3 * LOCAL * 1.8 * float(np.clip(hn, 0.5, 4.0)) ** 0.5 if k == "bigfire" else 40.0 * float(np.clip(hn, 0.5, 2)) / max(rm, 1e-3)) * rm
            s["weight"] = float(np.clip(hn, 0.25, 2.5)) ** 0.5 if k != "window" else 0.5
            if k == "candle" and s["h"] >= 5:
                s["warp"] = dict(sway=float(np.clip(LWARP["sway_px"] * hn, 0.5, LWARP["sway_px"])), height=s["h"] * 1.4,
                                 zone=int(np.clip(round(LWARP["zone_px"] * hn), 2, LWARP["zone_px"])), fr=rng.uniform(0, 6.28, 2), nz=rng.standard_normal(4096))
                self._prep_warp(s)
        self._prep_spill(rng)
        self._prep_atmos(rng)

    # ---- flame_warp, ROI-local (locked formula)
    def _prep_warp(self, s):
        q = s["warp"]; bx0, by0, bx1, by1 = s["bb"]; pad = q["zone"] + 5
        X0, Y0, X1, Y1 = max(0, bx0 - pad), max(0, by0 - pad - 4), min(self.W, bx1 + pad), min(self.H, by1 + pad)
        fm = np.zeros((Y1 - Y0, X1 - X0), np.float32); fm[by0 - Y0:by1 - Y0, bx0 - X0:bx1 - X0] = s["mask"]
        zone = cv2.dilate((fm > 0.05).astype(np.uint8), np.ones((2 * q["zone"] + 1,) * 2, np.uint8)).astype(np.float32)
        zone = cv2.GaussianBlur(zone, (0, 0), max(q["zone"] / 3, 0.8)) * zone
        yy, xx = np.mgrid[Y0:Y1, X0:X1].astype(np.float32); hgt = np.clip((s["base"] - yy) / q["height"], 0, 1.3)
        q.update(roi=(X0, Y0, X1, Y1), zone_m=zone, hm=(hgt * zone).astype(np.float32), xx=xx - X0, yy=yy - Y0)
    def _warp(self, img, s, t, f):
        q = s["warp"]; X0, Y0, X1, Y1 = q["roi"]
        i = t * 3.0; j = int(i) % 4095; fr = i - int(i); fr = fr * fr * (3 - 2 * fr); nz = q["nz"][j] * (1 - fr) + q["nz"][j + 1] * fr
        sw = 0.6 * math.sin(2 * math.pi * LWARP["sway_hz"][0] * t + q["fr"][0]) + 0.3 * math.sin(2 * math.pi * LWARP["sway_hz"][1] * t + q["fr"][1]) + 0.25 * nz
        h = q["hm"]; dx = -(q["sway"] * sw) * h ** 1.6; dy = LWARP["stretch"] * (f - 1.0) * q["height"] * h * (1.3 - h) * q["zone_m"]
        roi = img[Y0:Y1, X0:X1].copy()
        w = cv2.remap(roi, q["xx"] + dx.astype(np.float32), q["yy"] + dy.astype(np.float32), cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        nzm = (np.abs(dx) + np.abs(dy)) > 1e-6
        roi[nzm] = w[nzm]; img[Y0:Y1, X0:X1] = roi
        return float(np.abs(dx).max() if dx.size else 0), q["zone_m"] > 0

    # ---- grouped light-spill (locked falloff x facing x relight mask)
    def _prep_spill(self, rng):
        sp = self.sp; H, W = self.H, self.W; S = [s for s in self.srcs]
        self.groups = []; self.lm = np.zeros((H, W), np.float32); self.pool = None
        if not S: return
        G = min(sp.get("groups", 8), len(S)); pts = np.float32([[s["x"], s["base"]] for s in S])
        cen = [pts[0]]
        for _ in range(1, G): d = np.min([((pts - c) ** 2).sum(1) for c in cen], 0); cen.append(pts[int(d.argmax())])
        cen = np.float32(cen)
        for _ in range(12):
            lab = np.argmin(((pts[:, None] - cen[None]) ** 2).sum(-1), 1)
            cen = np.float32([pts[lab == g].mean(0) if (lab == g).any() else cen[g] for g in range(G)])
        rel = 1 - _rectmask((H, W), sp.get("relight_exclude"), 0, sp.get("relight_poly"))
        rel = np.clip(cv2.GaussianBlur(rel, (0, 0), 14), 0, 1) * rel + 0 * rel
        rel = cv2.GaussianBlur(rel, (0, 0), 6)
        Lp = lum(self.Pf); warm = np.clip((self.Pf[..., 0] - self.Pf[..., 2]) / 255.0 * 2, 0, 1)
        lit = smoothstep(0.02, 0.35, Lp) * (0.5 + 0.5 * warm)
        Lb = cv2.GaussianBlur(Lp, (0, 0), 6.0); gx = cv2.Sobel(Lb, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(Lb, cv2.CV_32F, 0, 1, ksize=3)
        gm = np.sqrt(gx * gx + gy * gy); gw = np.clip(gm / (np.percentile(gm, 95) + 1e-6), 0, 1)
        q4 = 4; Hq, Wq = (H + q4 - 1) // q4, (W + q4 - 1) // q4; Yq, Xq = np.mgrid[0:Hq, 0:Wq].astype(np.float32) * q4
        Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
        amp = sp.get("spill_amp", LSP["amp"]); off = np.float32(LSP["offset"])
        for g in range(G):
            mem = [S[i] for i in range(len(S)) if lab[i] == g]
            if not mem: continue
            keep = np.ones((Hq, Wq), np.float32)
            for s in mem:
                d = np.sqrt((Xq - s["x"] - off[0]) ** 2 + (Yq - (s["base"] - s["h"] * 0.5) - off[1]) ** 2)
                keep *= 1 - np.clip(s["weight"], 0, 1) / (1 + (d / s["radius"]) ** LSP["power"])
            fall = cv2.resize(1 - keep, (W, H), interpolation=cv2.INTER_LINEAR)
            wsum = sum(s["weight"] for s in mem); lx = sum(s["x"] * s["weight"] for s in mem) / wsum; ly = sum((s["base"] - s["h"] * 0.5) * s["weight"] for s in mem) / wsum
            d = np.sqrt((X - lx) ** 2 + (Y - ly) ** 2) + 1e-3; gd = (gx * (lx - X) / d + gy * (ly - Y) / d) / (gm + 1e-4)
            gterm = 0.5 + 0.5 * gd * gw
            facing = LSP["facing_floor"] + (1 - LSP["facing_floor"]) * np.clip(LSP["warm_weight"] * lit + LSP["grad_weight"] * gterm, 0, 1)
            # flames themselves are driven by plate_flame, not double-counted by spill
            self.groups.append(dict(mem=mem, map=(amp * fall * facing * rel).astype(np.float32), k=min(math.sqrt(len(mem)), 2.5)))
            self.lm = np.maximum(self.lm, fall)
        self.lm = (self.lm / max(self.lm.max(), 1e-6)).astype(np.float32)
        if sp.get("pool"):
            main = max(S, key=lambda s: s["h"] if s["kind"] == "candle" else 0)
            self.pool = dict(src=main, d=np.sqrt((X - main["x"]) ** 2 + (Y - main["base"]) ** 2).astype(np.float32), rel=rel)

    # ---- atmosphere
    def _prep_atmos(self, rng):
        sp = self.sp; H, W = self.H, self.W; self.layers = []
        mex = 1 - _rectmask((H, W), sp.get("mist_exclude"), 10)
        for kind in ("haze", "mist"):
            for L in sp.get(kind, []):
                feather = L.get("feather", 60 if kind == "haze" else 30)
                m = _rectmask((H, W), [L["rect"]], feather) * (mex if kind == "mist" else 1)
                if kind == "mist" and L["color"] is None:
                    x0, y0, x1, y1 = L["rect"]; c = self.Pf[y0:y1, x0:x1].reshape(-1, 3); c = np.percentile(c, 80, 0)
                    col = np.clip(c * 1.25 + 18, 0, 255)
                else: col = np.float32(L["color"])
                lo = L.get("lo", 150) / 4.0; Hq, Wq = H // 4 + 1, W // 4 + 1
                Hq, Wq = 1 << int(math.ceil(math.log2(Hq))), 1 << int(math.ceil(math.log2(Wq)))
                T1 = pnoise(rng, Hq, Wq, lo, lo * 0.18, beta=2.6, ax=0.55); T2 = pnoise(rng, Hq, Wq, lo * 0.6, lo * 0.12, beta=2.6, ax=0.7)   # soft wisps only (no grain shimmer on faces)
                self.layers.append(dict(kind=kind, m=m.astype(np.float32), col=np.float32(col), op=L["opacity"], v=L["v"], T1=T1, T2=T2, lit=L.get("lit", False)))
        self.motes = []
        for M in sp.get("motes", []):
            n = M["n"]; x0, y0, x1, y1 = M["rect"]
            if M["light"] == "shaft":
                sx0, sy0, sx1, sy1, fe = M["shaft"]; lmap = np.zeros((H, W), np.float32); lmap[sy0:sy1, sx0:sx1] = 1
                lmap = cv2.GaussianBlur(lmap, (0, 0), fe / 2); lmap /= max(lmap.max(), 1e-6); lmap = np.clip(lmap * 1.3, 0, 1)
            else: lmap = None
            self.motes.append(dict(q=M, x=rng.uniform(x0, x1, n), y=rng.uniform(y0, y1, n), vx=rng.uniform(-4, 4, n), vy=rng.uniform(-6, 2, n),
                                   ax=rng.uniform(2, 9, n), ay=rng.uniform(2, 7, n), wx=rng.uniform(0.05, 0.25, n), wy=rng.uniform(0.04, 0.2, n),
                                   ph=rng.uniform(0, 6.28, (n, 3)), tw=rng.uniform(0.3, 1.2, n), sz=rng.uniform(*M["size"], n),
                                   br=rng.uniform(0.35, 1.0, n), lmap=lmap))
        self.embers = []
        for Em in sp.get("embers", []):
            n = Em["n"]; spn = np.float32(Em["spawn"]); k = rng.integers(0, len(spn), n); ang = rng.uniform(0, 6.28, n); rad = np.sqrt(rng.uniform(0, 1, n))
            ep = dict(x=spn[k, 0] + np.cos(ang) * rad * spn[k, 2], y=spn[k, 1] + np.sin(ang) * rad * spn[k, 3], v=rng.uniform(25, 70, n), life=rng.uniform(1.2, 2.6, n),
                      sw=rng.uniform(0.3, 1.0, n) * 8, sf=rng.uniform(0.4, 1.4, n), ph=rng.uniform(0, 6.28, n), sz=rng.uniform(*Em.get("size", (2.2, 3.6)), n), br=rng.uniform(0.5, 1, n), fl=rng.uniform(5, 13, n))
            ep["t0"] = rng.uniform(0, 1, n) * ep["life"]; self.embers.append(ep)
        self.smoke = []
        for Sm in sp.get("smoke", []):
            r2 = np.random.default_rng(900 + Sm["seed"]); self.smoke.append(dict(q=Sm, a=r2.uniform(3, 9, 3), k=r2.uniform(0.018, 0.045, 3), w=r2.uniform(0.25, 0.6, 3), ph=r2.uniform(0, 6.28, 3),
                                                                                lean=r2.uniform(-25, 25)))
        self.moon = sp.get("moon")
        if self.moon:
            x0, y0, x1, y1 = self.moon["allow"]; a = np.zeros((H, W), np.float32); a[y0:y1, x0:x1] = 1; self.moon_allow = cv2.GaussianBlur(a, (0, 0), 4)
        self.par = sp.get("parallax")
        if self.par:
            pm = np.zeros((H, W), np.float32); cv2.fillPoly(pm, [np.int32(self.par["poly"])], 1.0)
            Lb = cv2.GaussianBlur(lum(self.Pf), (0, 0), 2.0)
            inner = cv2.erode(pm, np.ones((41, 41), np.uint8)); band = cv2.dilate(pm, np.ones((41, 41), np.uint8))
            m = np.maximum(inner, band * (Lb < self.par["dark"]))
            n, lab, st, _ = cv2.connectedComponentsWithStats((m > 0.5).astype(np.uint8), 8)
            if n > 1: big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])); m = (lab == big).astype(np.float32)
            m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
            self.par_m = cv2.GaussianBlur(m, (0, 0), 3.0).astype(np.float32)

    def info(self):
        from collections import Counter
        c = Counter(s["kind"] for s in self.srcs); nw = sum(1 for s in self.srcs if "warp" in s)
        return dict(plate=self.key, sources=dict(c), warped_candles=nw, spill_groups=len(self.groups), haze=sum(1 for L in self.layers if L["kind"] == "haze"),
                    mist=sum(1 for L in self.layers if L["kind"] == "mist"), motes=sum(len(m["x"]) for m in self.motes), embers=sum(len(e["x"]) for e in self.embers),
                    smoke=len(self.smoke), moon=bool(self.moon), parallax=bool(self.par), pool=bool(self.pool))
    def active(self): return bool(self.srcs or getattr(self, "sway", None) or self.layers or self.motes or self.embers or self.smoke or self.moon or self.par)

    def render(self, t, u=0.0, want_disp=False):
        img = self.Pf.copy(); dmax = 0.0; zones = []
        self.pulse = PULSE.get(self.key, PULSE_DEFAULT)
        fs = [flick(s["F"], t) for s in self.srcs]
        for s, f in zip(self.srcs, fs):
            if "warp" in s:
                dm, z = self._warp(img, s, t, f); dmax = max(dmax, dm); zones.append((s["warp"]["roi"], z))
        if self.pool:
            P = self.pool; f = flick(P["src"]["F"], t); R = LPOOL["r0"] * 1.3 * (1 + LPOOL["breathe"] * 0.35 * (f - 1))   # gentle pool breathing: the pool darkens the whole room, so a full-strength breathe reads as whole-frame pumping
            litp = 1.0 / (1 + (P["d"] / R) ** LPOOL["power"]); dk = LPOOL["dark"] * (1 - litp) * P["rel"]
            img *= (1 - dk[..., None] * np.float32(LPOOL["tint"]))
        sig = []
        for G in self.groups:
            dl = sum(flick(s["F"], t) - 1.0 for s in G["mem"]) / len(G["mem"]) * G["k"] * self.pulse; sig.append(dl)
            img *= 1 + (G["map"] * dl)[..., None] * np.float32(LSP["tint"])
        smean = float(np.mean(sig)) if sig else 0.0
        hot = np.float32(LPF.get("hot", [255, 238, 190]))   # engine default
        for s, f in zip(self.srcs, fs):
            if s["mask"] is None: continue
            x0, y0, x1, y1 = s["bb"]; fm = s["mask"][..., None]; roi = img[y0:y1, x0:x1]
            tongue = LPF["tongue"] if s["kind"] == "candle" else 0.0
            if tongue:
                T = scroll(s["ftex"], 0, LPF["rise"] * t); T = cv2.resize(T, (64, 256))[: y1 - y0, : x1 - x0] if T.shape[0] >= y1 - y0 and T.shape[1] >= x1 - x0 else cv2.resize(T, (x1 - x0, y1 - y0))
                T = T[..., None]
            else: T = 0.0
            gain = LPF["gain"] if s["kind"] != "window" else 0.5
            g = np.clip(gain * (f - 1) + tongue * T * 0.5, -0.5, 0.6)
            mod = np.where(g > 0, roi + (hot - roi) * np.clip(g, 0, 1) * 0.6 + roi * g * 0.2, roi * (1 + g))
            roi[...] = roi * (1 - fm) + mod * fm
        col = np.float32(LSRC["color"])
        for s, f in zip(self.srcs, fs):
            k = s["kind"]
            if k == "offscreen": continue
            hn = s["h"] / 26.0
            if k == "candle": sg, gn = float(np.clip(LSRC["halo"]["sigma"] * 1.3 * hn, 5, 90)), LSRC["halo"]["gain"]
            elif k == "torch": sg, gn = float(np.clip(0.9 * s["h"], 20, 120)), 0.18
            elif k == "bigfire": sg, gn = float(np.clip(0.8 * s["h"], 40, 220)), 0.16
            elif k == "lantern": sg, gn = float(np.clip(1.4 * s["h"], 14, 90)), 0.16
            else: sg, gn = float(np.clip(1.6 * s["h"], 8, 40)), 0.12 * self.sp.get("window_amp", 1.0)
            gauss_dot(img, s["x"], s["base"] - s["h"] * 0.5, sg, col, gn * 2.0 * min(1.0, max(self.pulse, 0.6)) * (f - 1.0))   # painted plates already carry the static glow: animate the halo as a pulse only (no exposure lift)
            if k == "candle":   # locked emissive teardrop (flame [4,26] scaled to the painted flame), candles only
                fw, fh = max(2.0, s["w"] * 0.45), s["h"] * 0.9; x, y = s["x"], s["base"]
                xa, xb, ya, yb = max(0, int(x - fw * 2)), min(self.W, int(x + fw * 2) + 1), max(0, int(y - fh * 1.4)), min(self.H, int(y + fh * 0.4) + 1)
                if xb > xa and yb > ya:
                    yy, xx = np.mgrid[ya:yb, xa:xb].astype(np.float32); vy = (y - yy) / fh; vx = (xx - x) / fw
                    width = np.clip(1 - vy, 0, 1) ** 0.7 * (0.6 + 0.4 * np.clip(vy * 4, 0, 1))
                    tg = cv2.remap(s["ftex"], ((vx * 14 + 32) % 64).astype(np.float32), ((vy * 70 - 60 * t) % 256).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
                    shape = np.clip(1 - (vx / (width + 1e-3)) ** 2, 0, 1) * (vy > -0.3) * np.clip(1 + vy * 3, 0, 1)
                    fl = np.clip(shape * (0.75 + 0.45 * tg) * (0.75 + 0.25 * f) - 0.25 * np.clip(vy, 0, 1), 0, 1) ** 1.3 * LSRC["flame_gain"]
                    core = np.float32([255, 236, 180]); c = col * (1 - fl[..., None]) + core * fl[..., None]
                    img[ya:yb, xa:xb] += fl[..., None] * c * 0.9
        np.clip(img, 0, 255, out=img)
        for L in self.sway:   # lantern pendulum sway: ROI-local rotation about the cord pivot, feathered to the lantern box only
            x0, y0, x1, y1 = L["rect"]; px, py = L["pivot"]; pad = 12
            X0, Y0, X1, Y1 = max(0, min(x0, px) - pad), max(0, min(y0, py) - pad), min(self.W, max(x1, px) + pad), min(self.H, max(y1, py) + pad)
            th = L.get("amp_deg", 1.0) * (0.75 * math.sin(2 * math.pi * 0.32 * t + L["ph"]) + 0.25 * math.sin(2 * math.pi * 0.71 * t + 2 * L["ph"]))
            M = cv2.getRotationMatrix2D((float(px - X0), float(py - Y0)), th, 1.0); roi = img[Y0:Y1, X0:X1]
            rot = cv2.warpAffine(roi, M, (X1 - X0, Y1 - Y0), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            m = np.zeros(roi.shape[:2], np.float32); m[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] = 1; m = cv2.GaussianBlur(m, (0, 0), 3)[..., None]
            roi[...] = roi * (1 - m) + rot * m
        # atmosphere (screen blends; no displacement)
        for L in self.layers:
            v = L["v"]; T = 0.62 * scroll(L["T1"], v[0] * t / 4, v[1] * t / 4) + 0.38 * scroll(L["T2"], v[0] * 1.7 * t / 4, v[1] * 1.4 * t / 4 + 0.6 * t)
            T = cv2.resize(T[: self.H // 4 + 1, : self.W // 4 + 1], (self.W, self.H), interpolation=cv2.INTER_LINEAR)
            a = L["op"] * np.clip(0.45 + 0.45 * T, 0, 1.2) * L["m"]
            if L["lit"]: a = a * (0.35 + 0.65 * self.lm) * (1 + 0.9 * smean)
            img[...] = 255 - (255 - img) * (1 - a[..., None] * L["col"] / 255.0)
        for M in self.motes:
            q = M["q"]; x0, y0, x1, y1 = q["rect"]; w, h = x1 - x0, y1 - y0
            px = x0 + (M["x"] - x0 + M["vx"] * t + M["ax"] * np.sin(2 * math.pi * M["wx"] * t + M["ph"][:, 0])) % w
            py = y0 + (M["y"] - y0 + M["vy"] * t + M["ay"] * np.sin(2 * math.pi * M["wy"] * t + M["ph"][:, 1])) % h
            edge = np.clip(np.minimum.reduce([px - x0, x1 - px, py - y0, y1 - py]) / 30.0, 0, 1)
            lm = M["lmap"] if M["lmap"] is not None else self.lm
            li = lm[np.clip(py.astype(int), 0, self.H - 1), np.clip(px.astype(int), 0, self.W - 1)]
            br = q["gain"] * M["br"] * li * edge * (0.55 + 0.45 * np.sin(2 * math.pi * M["tw"] * t + M["ph"][:, 2])) * (1 + 0.8 * smean if q["light"] == "lm" else 1)
            for x, y, b, sz in zip(px, py, br, M["sz"]):
                if b > 2: gauss_dot(img, x, y, sz * 0.8, np.float32(q["color"]) / 255.0, b)
        for ep in self.embers:
            age = (t + ep["t0"]) % ep["life"]; k = age / ep["life"]
            px = ep["x"] + 6 * age + ep["sw"] * np.sin(ep["ph"] + age * ep["sf"] * 2 * math.pi) * k; py = ep["y"] - ep["v"] * age
            br = ep["br"] * np.sin(math.pi * k) ** 0.6 * (0.7 + 0.3 * np.sin(ep["fl"] * t * 2 * math.pi + ep["ph"]))
            for x, y, b, sz in zip(px, py, br, ep["sz"]):
                gauss_dot(img, x, y, sz * 0.7, (255, 170, 80), b * 0.9); gauss_dot(img, x, y + sz * 1.2, sz * 0.6, (255, 170, 80), b * 0.35)
        for S in self.smoke:
            q = S["q"]; x0, yb = q["xy"]; Hs = q["height"]; ya = int(max(0, yb - Hs)); xa, xb = int(max(0, x0 - 70)), int(min(self.W, x0 + 70))
            yy = np.arange(ya, int(yb), dtype=np.float32); r = (yb - yy) / Hs
            xx = np.arange(xa, xb, dtype=np.float32)[None, :]
            acc = np.zeros((len(yy), xb - xa), np.float32)
            for i in range(3):
                xc = x0 + S["lean"] * r ** 1.5 + S["a"][i] * r ** 0.8 * np.sin(S["k"][i] * (yb - yy) * (1 + 0.3 * i) - 2 * math.pi * S["w"][i] * t + S["ph"][i]) * (1 + 2.5 * r)
                wd = 1.2 + 6.0 * r ** 1.2 + 0.8 * i
                puff = 0.55 + 0.45 * np.sin(0.05 * (yb - yy) - 2 * math.pi * 0.45 * t + S["ph"][i])
                al = (0.34 - 0.08 * i) * np.clip(r * 12, 0, 1) * (1 - smoothstep(0.55, 1.0, r)) * puff
                acc = np.maximum(acc, np.exp(-((xx - xc[:, None]) ** 2) / (2 * wd[:, None] ** 2)) * al[:, None])
            roi = img[ya:int(yb), xa:xb]; c = np.float32([196, 186, 176])
            roi[...] = roi + (c - roi) * acc[..., None]
        if self.moon:
            x, y = self.moon["xy"]; b = 0.5 + 0.5 * math.sin(2 * math.pi * 0.18 * t) * 0.6 + 0.2 * math.sin(2 * math.pi * 0.07 * t + 1)
            gauss_dot(img, x, y, 22, (205, 218, 255), 0.16 * b, self.moon_allow); gauss_dot(img, x, y, 70, (190, 205, 245), 0.07 * b, self.moon_allow)
        np.clip(img, 0, 255, out=img)
        if self.par:
            e = 1 + self.par["extra"] * (u * u * (3 - 2 * u)); ax, ay = self.par["anchor"]
            M = np.float32([[e, 0, ax * (1 - e)], [0, e, ay * (1 - e)]])
            fg = cv2.warpAffine(img, M, (self.W, self.H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            mm = cv2.warpAffine(self.par_m, M, (self.W, self.H), flags=cv2.INTER_LINEAR)[..., None]
            img = img * (1 - mm) + fg * mm
        out = np.clip(img + 0.5, 0, 255).astype(np.uint8)
        if want_disp: return out, dict(warp_max_px=dmax, zones=zones)
        return out

def overlay(fx, path):
    o = cv2.cvtColor(fx.P, cv2.COLOR_RGB2BGR).copy()
    for s in fx.srcs:
        c = dict(candle=(0, 255, 0), torch=(0, 0, 255), bigfire=(0, 128, 255), lantern=(255, 0, 128), window=(255, 255, 0), offscreen=(255, 0, 255))[s["kind"]]
        if s["bb"]: x0, y0, x1, y1 = s["bb"]; cv2.rectangle(o, (x0, y0), (x1, y1), c, 1)
        if "warp" in s: cv2.circle(o, (int(s["x"]), int(s["base"]) + 3), 2, (0, 255, 255), -1)
    for g in fx.groups:
        pass
    cv2.imwrite(str(path), o)
