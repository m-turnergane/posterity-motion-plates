"""dust_v1: drifting motes + soft haze in painted light shafts, and blowing dust on dry ground. MATTE-ONLY.

Owner rules (same as smoke_v2 / water_v1): the plate never moves; nothing is displaced or resampled before the
shared camera framing. Only dust pixels change:
  * zones: each zone is a polygon (shaft or ground) x a luminance key from the ORIGINAL plate (so dust "catches the
    light": brighter where the painted light is). Everything outside the union of zone polygons, and every protect
    polygon (faces, hands, figures, lanterns, walls, coast, text), is forced back to the plate: 0 changed px.
  * motes: N particles per zone with depth (size / speed / brightness), slow drift + gentle multi-sine turbulence,
    analytic positions p(t + pre_roll) so they are already moving at frame 0. Each mote has its own slow life
    envelope (5-12 s, smooth cos^2 fade) so none ever pops in; positions wrap only inside a margin where the zone map
    is 0 (invisible). Brightness = amp x zone map at the mote x envelope -> motes glow in the shaft, vanish in shadow.
    Composited with a screen blend (never clips to flat white).
  * haze (shafts): STATIC shaft-shaped haze map x a few fixed soft blobs, each breathing on its own <= 0.15 Hz clock.
    No travelling bands, no moving light gradients (fixed-point modulation only).
  * sheets (ground): blowing dust: two seamless periodic noise textures advected slowly by the wind at different
    speeds/scales (they evolve, never slide rigidly), keyed to the ground zone and to the plate's light. The texture
    period is >> the distance travelled in a shot, so it never visibly loops.
Guardrails: motion/guardrails.py check_shot (refuse > 1.5x of native fill) is called before every render/reel.

CLI (all outputs refuse to overwrite):
  dust_v1.py render  <cfg.json> <out.mp4> [--seconds S] [--size 540x960] [--crf N]
  dust_v1.py reel    <reel.json> <out.mp4>
  dust_v1.py proof   <cfg.json> <out.json>     impulse 0-px leak proof + protect 0-changed-px proof
  dust_v1.py stats   <cfg.json> <out.json>     phone 360x640 swing / >5 Hz / read / pop metrics
  dust_v1.py overlay <cfg.json> <out.png>      zones, protect, mote domain over the plate (+ phone strip)
  dust_v1.py grab    <cfg.json> <out.png> [--t T]   phone-size before|after grab
"""
import importlib.util, json, math, sys
from pathlib import Path
import numpy as np, cv2

HERE = Path(__file__).resolve().parent
def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
F3 = _load("flames_v3", HERE.parent / "flames" / "flames_v3.py")            # helpers only (read-only import)
G = _load("guardrails", HERE.parent.parent / "motion" / "guardrails.py")
cv2.setNumThreads(4)

def L_of(a): return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
def poly(shape, polys):
    m = np.zeros(shape, np.uint8)
    for p in polys or []: cv2.fillPoly(m, [np.int32(p)], 1)
    return m > 0

class DustShot:
    def __init__(self, cfg):
        self.cfg = cfg; self.P = F3.load_plate(cfg["plate"]); H, W = self.P.shape[:2]; self.H, self.W = H, W
        self.Pf = self.P.astype(np.float32); L0 = L_of(self.Pf)                 # ALL static maps from the original plate
        rng = np.random.default_rng(int(cfg.get("seed", 0)))
        prot = poly((H, W), cfg.get("protect", []))
        zp = [poly((H, W), [z["poly"]]) & ~prot for z in cfg["zones"]]
        allow = np.zeros((H, W), bool)
        for m in zp: allow |= m
        self.protect = ~allow
        self.keep = F3.keepout_fade(self.protect.astype(np.uint8), float(cfg.get("protect_feather", 8)))
        self.zones = []
        for z, m in zip(cfg["zones"], zp):
            Lb = cv2.GaussianBlur(L0, (0, 0), float(z.get("lum_blur", 6)))
            key = F3.smoothstep(float(z.get("lum_lo", 60)), float(z.get("lum_hi", 200)), Lb) ** float(z.get("lum_gamma", 1.0))
            f = float(z.get("feather", 24))
            soft = cv2.GaussianBlur(m.astype(np.float32), (0, 0), f / 2) * m if f > 0 else m.astype(np.float32)
            M = (key * soft * self.keep).astype(np.float32)
            ys, xs = np.nonzero(M > 1e-3); bb = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1) if len(xs) else (0, 0, 1, 1)
            col = np.float32(z["color"]) if z.get("color") else np.float32(np.percentile(self.Pf[M > 0.5], 90, axis=0) if (M > 0.5).any() else (255, 240, 210))
            self.zones.append(dict(cfg=z, M=M, bb=bb, color=col))
        self.layers = []
        for Ly in cfg.get("layers", []):
            k = Ly["type"]; Z = self.zones[int(Ly.get("zone", 0))]
            if k == "motes": self.layers.append(self._prep_motes(Ly, Z, rng))
            elif k == "haze": self.layers.append(self._prep_haze(Ly, Z, rng))
            elif k == "sheets": self.layers.append(self._prep_sheets(Ly, Z, rng))
            else: raise ValueError(k)

    # ------------------------------------------------------------------------------------------- motes
    def _prep_motes(self, Ly, Z, rng):
        n = int(Ly.get("n", 300)); x0, y0, x1, y1 = Z["bb"]
        s_lo, s_hi = Ly.get("sigma", [0.8, 3.0]); v_lo, v_hi = Ly.get("speed", [6, 20])
        mg = int(math.ceil(3 * s_hi * 1.6)) + 6                                     # wrap margin: zone map is 0 there
        dom = (x0 - mg, y0 - mg, x1 + mg, y1 + mg)
        d = np.float32(Ly.get("dir", [0.0, 1.0])); d /= np.linalg.norm(d) + 1e-9
        z = rng.uniform(0, 1, n) ** float(Ly.get("depth_power", 2.0))            # most motes far / small, few near / big
        ang = rng.uniform(-1, 1, n) * math.radians(float(Ly.get("dir_jitter_deg", 20)))
        ca, sa = np.cos(ang), np.sin(ang); dx = d[0] * ca - d[1] * sa; dy = d[0] * sa + d[1] * ca
        spd = (v_lo + (v_hi - v_lo) * z) * rng.uniform(0.8, 1.2, n)
        ta = float(Ly.get("turb_px", 6)); tl, th = Ly.get("turb_hz", [0.08, 0.35])
        lt_lo, lt_hi = Ly.get("life_s", [5.0, 12.0])
        return dict(type="motes", Z=Z, n=n, dom=dom, x0=rng.uniform(dom[0], dom[2], n), y0=rng.uniform(dom[1], dom[3], n),
                    vx=dx * spd, vy=dy * spd, sig=s_lo + (s_hi - s_lo) * z, bri=float(Ly.get("near_gain", 1.6)) ** z * rng.uniform(0.55, 1.0, n),
                    ta=ta * (0.5 + z), f=rng.uniform(tl, th, (4, n)), ph=rng.uniform(0, 6.2832, (4, n)),
                    life=rng.uniform(lt_lo, lt_hi, n), lph=rng.uniform(0, 1, n), env_pow=float(Ly.get("env_pow", 0.8)),
                    amp=float(Ly.get("amp", 120)), pre=float(Ly.get("pre_roll", 40.0)), color=np.float32(Ly.get("color", Z["color"])) / 255.0,
                    min_sigma_phone=float(Ly.get("min_sigma", 0.0)))

    def _mote_pos(self, L, t):
        T = t + L["pre"]; f, ph, ta = L["f"], L["ph"], L["ta"]
        tx = ta * (np.sin(6.2832 * f[0] * T + ph[0]) + 0.5 * np.sin(6.2832 * f[1] * T + ph[1])) / 1.5
        ty = ta * (np.sin(6.2832 * f[2] * T + ph[2]) + 0.5 * np.sin(6.2832 * f[3] * T + ph[3])) / 1.5
        X0, Y0, X1, Y1 = L["dom"]
        x = X0 + np.mod(L["x0"] + L["vx"] * T - X0, X1 - X0) + tx
        y = Y0 + np.mod(L["y0"] + L["vy"] * T - Y0, Y1 - Y0) + ty
        env = (0.5 - 0.5 * np.cos(6.2832 * (T / L["life"] + L["lph"]))) ** L["env_pow"]
        return x, y, env

    def _motes(self, L, t, A):
        x, y, env = self._mote_pos(L, t); M = L["Z"]["M"]; H, W = self.H, self.W
        xi = np.clip(np.round(x).astype(int), 0, W - 1); yi = np.clip(np.round(y).astype(int), 0, H - 1)
        inside = (x > -8) & (x < W + 8) & (y > -8) & (y < H + 8)
        b = L["amp"] * L["bri"] * env * np.where(inside, M[yi, xi], 0.0)
        for i in np.nonzero(b > 0.4)[0]:
            s = L["sig"][i]; r = int(math.ceil(3 * s)) + 1; cx, cy = x[i], y[i]
            ix0, iy0 = int(math.floor(cx)) - r, int(math.floor(cy)) - r; ix1, iy1 = ix0 + 2 * r + 2, iy0 + 2 * r + 2
            jx0, jy0, jx1, jy1 = max(ix0, 0), max(iy0, 0), min(ix1, W), min(iy1, H)
            if jx1 <= jx0 or jy1 <= jy0: continue
            gx = np.exp(-0.5 * ((np.arange(jx0, jx1) - cx) / s) ** 2); gy = np.exp(-0.5 * ((np.arange(jy0, jy1) - cy) / s) ** 2)
            A[jy0:jy1, jx0:jx1] += (b[i] * gy[:, None] * gx[None, :])[..., None] * L["color"][None, None]

    # ------------------------------------------------------------------------------------------- haze (fixed-point breathing)
    def _prep_haze(self, Ly, Z, rng):
        x0, y0, x1, y1 = Z["bb"]; H, W = self.H, self.W; k = int(Ly.get("blobs", 6)); bs = float(Ly.get("blob_sigma", 90))
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); B = []
        cs = [(rng.uniform(x0, x1), rng.uniform(y0, y1)) for _ in range(k)]
        for cx, cy in cs: B.append(np.exp(-0.5 * (((xx - cx) ** 2 + (yy - cy) ** 2) / bs ** 2)).astype(np.float32))
        B = np.stack(B); B /= np.maximum(B.sum(0), 0.35)[None]
        lo, hi = Ly.get("hz", [0.05, 0.15])
        return dict(type="haze", Z=Z, B=B, f=rng.uniform(lo, hi, k), ph=rng.uniform(0, 6.2832, k), amp=float(Ly.get("amp", 6.0)),
                    base=float(Ly.get("base", 0.0)), color=np.float32(Ly.get("color", Z["color"])) / 255.0)

    def _haze(self, L, t, A):
        w = np.sin(6.2832 * L["f"] * t + L["ph"]).astype(np.float32)
        fld = L["base"] + np.tensordot(w, L["B"], 1)
        A += (L["amp"] * L["Z"]["M"] * fld)[..., None] * L["color"][None, None]

    # ------------------------------------------------------------------------------------------- sheets (ground dust)
    def _prep_sheets(self, Ly, Z, rng):
        th, tw = Ly.get("tex", [1024, 2048]); scs = Ly.get("scales", [[220, 18], [110, 10]])
        tex = [F3.periodic_noise(rng, th, tw, lo, hi) for lo, hi in scs]
        return dict(type="sheets", Z=Z, tex=tex, wind=[np.float32(w) for w in Ly.get("wind", [[18, -2], [11, 1]])],
                    thr=float(Ly.get("thresh", 0.2)), gam=float(Ly.get("gamma", 1.4)), amp=float(Ly.get("amp", 0.12)),
                    sq=float(Ly.get("squash_y", 2.5)), color=np.float32(Ly.get("color", Z["color"])))

    def _sheets(self, L, t, img):
        x0, y0, x1, y1 = L["Z"]["bb"]; h, w = y1 - y0, x1 - x0
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32); acc = np.zeros((h, w), np.float32)
        for tx, wv in zip(L["tex"], L["wind"]):
            mx = np.mod(xx - wv[0] * t, tx.shape[1]); my = np.mod(yy * L["sq"] - wv[1] * t * L["sq"], tx.shape[0])   # squashed = flat, ground-hugging
            acc += cv2.remap(tx, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        acc /= len(L["tex"]) ** 0.5
        a = (np.clip((acc - L["thr"]) / (2.5 - L["thr"]), 0, 1) ** L["gam"]) * L["amp"] * L["Z"]["M"][y0:y1, x0:x1]
        sub = img[y0:y1, x0:x1]; sub += (L["color"][None, None] - sub) * a[..., None]

    # ------------------------------------------------------------------------------------------- compose
    def frame(self, t):
        img = self.Pf.copy(); A = np.zeros_like(img)
        for L in self.layers:
            if L["type"] == "sheets": self._sheets(L, t, img)
        for L in self.layers:
            if L["type"] == "haze": self._haze(L, t, A)
            elif L["type"] == "motes": self._motes(L, t, A)
        img = img + np.maximum(A, -img) * np.where(A > 0, (255.0 - img) / 255.0, 1.0)       # screen for light, plain for dimming
        o = self.Pf + (img - self.Pf) * self.keep[..., None]                                   # matte (Pf = what the renderer reads)
        out = np.clip(o + 0.5, 0, 255).astype(np.uint8)
        out[self.protect] = self.P[self.protect]
        return out

    def set_plate_for_proof(self, Pf): self.Pf = Pf
    def info(self):
        return dict(plate=self.cfg["plate"], allow_px=int((~self.protect).sum()), protect_px=int(self.protect.sum()),
                    zones=[dict(type=z["cfg"].get("type"), bb=z["bb"], color=[round(float(c)) for c in z["color"]], M_px=int((z["M"] > 0.05).sum())) for z in self.zones],
                    motes=[L["n"] for L in self.layers if L["type"] == "motes"])

# ---------------------------------------------------------------------------------------------- io
def out_size(cfg, size=None):
    s = size or cfg.get("size", "1080x1920"); w, h = map(int, s.split("x")); return w, h
def _cam(cfg): z0, z1 = cfg.get("push", (1.0, 1.0)); return float(z0), float(z1), tuple(cfg.get("push_center", (0.5, 0.5)))
def guard(cfg, P=None, mode="refuse", size=None):   # size: the actual output WxH (2026-10-30 size-density fix; was always 1080x1920)
    P = F3.load_plate(cfg["plate"]) if P is None else P; return G.check_shot(cfg, P, mode=mode, out_wh=out_size(cfg, size))
def render(cfg, out, seconds=None, size=None, crf=None, writer=None, fps=30):
    guard(cfg, size=size); sh = DustShot(cfg); w, h = out_size(cfg, size); n = int(round((seconds or cfg.get("seconds", 6.0)) * fps)); z0, z1, c = _cam(cfg)
    p = writer or F3.ffmpeg_writer(out, w, h, fps, crf=int(crf or cfg.get("crf", 24)))
    print("shot", cfg.get("name"), json.dumps(sh.info(), default=str), file=sys.stderr, flush=True)
    for i in range(n): p.stdin.write(F3.push_frame(sh.frame(i / fps), i / max(n - 1, 1), w, h, z0, z1, center=c).tobytes())
    if writer is None: p.stdin.close(); assert p.wait() == 0
def _cfg(path):
    c = json.load(open(path)); c.setdefault("name", Path(path).stem); return c

def proof(cfg, out_json, times=None):
    """(1) impulse: +-24 on an isolated 9-px lattice of the plate the renderer reads; render the same t with/without.
    PASS only if the difference is confined to the impulse pixels (no resampling / displacement anywhere).
    (2) protect: changed px vs plate inside protect (everything outside the dust zones + protect polys) == 0."""
    sh = DustShot(cfg); P = sh.P; H, W = P.shape[:2]; times = times or [0.0, 0.7, 1.5, 2.6, 3.4, 4.5, 5.9]
    Gm = np.zeros((H, W), bool); Gm[4::9, 4::9] = True
    sgn = np.where(P[Gm].mean(-1) > 128, -24, 24).astype(np.float32)
    Pf0 = sh.Pf.copy(); Pf1 = Pf0.copy(); Pf1[Gm] += sgn[:, None]
    r = dict(name=cfg["name"], plate=cfg["plate"], times=times, impulses=int(Gm.sum()), leaked_px_total=0, protect_px=int(sh.protect.sum()),
             protect_changed_px=[], allow_changed_px=[], changed_frac_of_frame=[], max_abs_diff_in_allow=[],
             guardrails=guard(cfg, P, mode="warn"))
    for t in times:
        sh.set_plate_for_proof(Pf0); a = sh.frame(t).astype(int)
        sh.set_plate_for_proof(Pf1); b = sh.frame(t).astype(int)
        r["leaked_px_total"] += int(((np.abs(a - b).max(-1) > 0) & ~Gm).sum())
        ch = np.abs(a - P.astype(int)).max(-1)
        r["protect_changed_px"].append(int((ch[sh.protect] > 0).sum())); r["allow_changed_px"].append(int((ch[~sh.protect] > 0).sum()))
        r["changed_frac_of_frame"].append(round(float((ch > 0).mean()), 5)); r["max_abs_diff_in_allow"].append(int(ch[~sh.protect].max()))
    sh.set_plate_for_proof(Pf0)
    r["pass_impulse_0px"] = r["leaked_px_total"] == 0; r["pass_protect_0px"] = max(r["protect_changed_px"]) == 0
    r["pass"] = r["pass_impulse_0px"] and r["pass_protect_0px"] and all(c["ok"] or c.get("waived") for c in r["guardrails"])
    json.dump(r, open(out_json, "x"), indent=1, default=float); print(json.dumps(r, default=float)); return r

def phone(img): return cv2.resize(img, (360, 640), interpolation=cv2.INTER_AREA)
def series_stats(v, fps=30, win=1.0, step=0.5):
    v = np.asarray(v, np.float64); n = int(win * fps); sw = []
    for i in range(0, len(v) - n + 1, int(step * fps)): w = v[i:i + n]; sw.append((w.max() - w.min()) / max(w.mean(), 1e-6))
    st = np.abs(np.diff(v)) / max(v.mean(), 1e-6); x = v - v.mean(); Pw = np.abs(np.fft.rfft(x)) ** 2; f = np.fft.rfftfreq(len(x), 1 / fps)
    return dict(swing_1s_median_pct=round(100 * float(np.median(sw)), 3), swing_1s_max_pct=round(100 * float(np.max(sw)), 3),
                max_step_pct=round(100 * float(st.max()), 4), energy_above_5hz=round(float(Pw[f > 5].sum() / max(Pw[1:].sum(), 1e-12)), 4))

def stats(cfg, out_json, seconds=6.0, fps=30):
    """Phone (360x640) metrics on the framed output. read_px_1s: phone px whose luma range within the first 1 s is >= 6
    levels (something visibly moves/glints in the first second). pop: max over frames of phone px whose luma jumps
    >= 12 levels in ONE frame (should be ~0: motes fade, never pop). Region series: whole frame and dust zones."""
    sh = DustShot(cfg); w, h = out_size(cfg); n = int(seconds * fps); z0, z1, c = _cam(cfg)
    def fr(im, i): return phone(F3.push_frame(im, i / max(n - 1, 1), w, h, z0, z1, center=c))
    def mk(m, i): return fr(np.repeat((m.astype(np.uint8) * 255)[..., None], 3, -1), i)[..., 0] > 127
    zm = mk((~sh.protect), 0)                                                                  # dust zone (allow), frame 0 camera
    out_m = np.stack([~cv2.dilate(mk((~sh.protect), i).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) for i in range(n)])
    prot_m = np.stack([cv2.erode(mk(sh.protect, i).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) for i in range(n)])
    seq = np.stack([F3.luma(fr(sh.frame(i / fps), i)) for i in range(n)]).astype(np.float32)
    base = np.stack([F3.luma(fr(sh.P, i)) for i in range(n)]).astype(np.float32)          # still plate through the SAME camera
    d = seq - base; jump = np.abs(np.diff(d, axis=0))
    r = dict(name=cfg["name"], seconds=seconds, phone="360x640", push=[z0, z1],
             whole_frame=series_stats(seq.mean((1, 2)), fps), dust_zone=series_stats(seq[:, zm].mean(1), fps) if zm.any() else None,
             read_px_1s_range_ge6=int(((d[:30].max(0) - d[:30].min(0)) >= 6).sum()), read_px_1s_range_ge12=int(((d[:30].max(0) - d[:30].min(0)) >= 12).sum()),
             mean_abs_lift_in_zone=round(float(np.abs(d[:, zm]).mean()), 3) if zm.any() else 0,
             pop_px_max_per_frame_jump_ge12=int((jump >= 12).sum((1, 2)).max()), pop_px_max_per_frame_jump_ge8=int((jump >= 8).sum((1, 2)).max()),
             outside_zone_px_changed_ge2=int(((np.abs(d) >= 2) & out_m).any(0).sum()),           # per-frame masks follow the push
             protect_px_changed_ge2=int(((np.abs(d) >= 2) & prot_m).any(0).sum()))
    pz = np.abs(d).mean((1, 2)); r["dust_energy_series"] = series_stats(pz + 1.0, fps)
    json.dump(r, open(out_json, "x"), indent=1); print(json.dumps(r)); return r

def overlay(cfg, out_png):
    sh = DustShot(cfg); im = cv2.cvtColor(sh.P, cv2.COLOR_RGB2BGR).copy(); o = im.copy()
    o[sh.protect] = (o[sh.protect] * 0.5 + np.float32([255, 60, 60]) * 0.5).astype(np.uint8)
    for z in sh.zones:
        M = z["M"]; o = (o * (1 - 0.6 * M[..., None]) + np.float32([0, 200, 255]) * 0.6 * M[..., None]).astype(np.uint8)
    for L in sh.layers:
        if L["type"] == "motes": X0, Y0, X1, Y1 = map(int, L["dom"]); cv2.rectangle(o, (X0, Y0), (X1, Y1), (0, 255, 0), 2)
    cv2.imwrite(out_png, np.hstack([im, o]))
def grab(cfg, out_png, t=3.0):
    sh = DustShot(cfg); w, h = out_size(cfg); z0, z1, c = _cam(cfg); u = t / max(cfg.get("seconds", 6.0), 1e-6)
    a = phone(F3.push_frame(sh.P, u, w, h, z0, z1, center=c)); b = phone(F3.push_frame(sh.frame(t), u, w, h, z0, z1, center=c))
    dd = np.clip(np.abs(b.astype(int) - a.astype(int)) * 4, 0, 255).astype(np.uint8)
    cv2.imwrite(out_png, cv2.cvtColor(np.hstack([a, b, dd]), cv2.COLOR_RGB2BGR))

def reel(reel_json, out, fps=30):
    R = json.load(open(reel_json)); w, h = map(int, R.get("size", "1080x1920").split("x")); shots = []
    for s in R["shots"]:
        cfg = _cfg(HERE / s["config"]); cfg.update({k: v for k, v in s.items() if k != "config"}); guard(cfg, size=f"{w}x{h}"); shots.append((cfg, s["seconds"]))
    p = F3.ffmpeg_writer(out, w, h, fps, crf=int(R.get("crf", 24)))
    for cfg, sec in shots: render(cfg, out, seconds=sec, size=f"{w}x{h}", writer=p)
    p.stdin.close(); assert p.wait() == 0

if __name__ == "__main__":
    a = sys.argv[1:]; cmd = a[0]
    def opt(k, d=None): return a[a.index(k) + 1] if k in a else d
    if cmd == "reel": assert not Path(a[2]).exists(); reel(a[1], a[2])
    else:
        cfg = _cfg(a[1]); out = a[2]; assert not Path(out).exists(), "never overwrite"
        if cmd == "render": render(cfg, out, seconds=float(opt("--seconds", cfg.get("seconds", 6))), size=opt("--size"), crf=opt("--crf"))
        elif cmd == "proof": proof(cfg, out)
        elif cmd == "stats": stats(cfg, out, seconds=float(opt("--seconds", 6.0)))
        elif cmd == "overlay": overlay(cfg, out)
        elif cmd == "grab": grab(cfg, out, t=float(opt("--t", 3.0)))
