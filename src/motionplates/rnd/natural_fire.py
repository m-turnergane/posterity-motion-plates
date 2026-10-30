"""v13 (= v12 engine + per-tongue style by underlying paint: v11 thin tongues over white-hot/bright-yellow paint, v12 lobed licks over darker paint;
warm gap tint (cream paint near licks -> amber, soft gradient, tongue layer only); merged mass composited UNDER the single tongues;
pillar desync (varied heights from Lmax, no simultaneous same-height flares, fewer forks)).
v12 doc: (= v11 engine + lobed broad forge tongues, painterly stroke breakup, posterized tone, optional stepped layer, pillar height cap).
v11 doc: sprite TONGUES built from the plate's own painted flame strokes, over-composited (graded red->orange->small yellow core) on the
decoded v2c static frames, plus sharp streaked sparks. Painted fire stays a static base. Same output-space hard holdout as v10.
Each tongue: own birth, base x, width, target length, rise speed with bursts, detach (base snaps upward faster than tip -> tongue
pinches off and burns away), forked tip, crisp 0.8-plate-px alpha edge with jagged/stroke-driven contour; internal texture = the
plate's flame-stroke luminance detail sampled from a source patch that rides with the tongue (so it is the same brushwork).
Every position is monotone upward; nothing moves down. usage: fire_v11.py TAG SPEC.json [N] [iter|final]"""
import sys, os, json, subprocess, time, numpy as np, cv2
sys.path.insert(0, 'tools'); import prod as P; import fire_v10 as F; from noise import Perlin3, fbm
W, H = F.W, F.H; ss = F.ss
ZN = ["z0low", "z0top", "z1", "z2"]
STOPS = np.array([0, .2, .4, .6, .78, .9, 1.0], np.float32)
COLS = np.array([[110, 18, 6], [170, 35, 8], [220, 75, 12], [245, 130, 25], [255, 185, 60], [255, 225, 130], [255, 248, 210]], np.float32)
def grade(T, cols=COLS):
    T = np.clip(T, 0, 1); return np.stack([np.interp(T, STOPS, cols[:, c]) for c in range(3)], -1)

def smooth_bump(x): x = np.clip(x, 0, 1); return (x * (1 - x) * 4) ** 2

def stroke_tex(lum, nb=8, ln=9):
    """plate brushstroke texture smeared ALONG the local stroke direction (structure tensor), so breakup follows the painter's strokes."""
    hp = lum / (cv2.GaussianBlur(lum, (0, 0), 2.0) + 1.0)
    gx = cv2.Sobel(lum, cv2.CV_32F, 1, 0); gy = cv2.Sobel(lum, cv2.CV_32F, 0, 1)
    jxx = cv2.GaussianBlur(gx * gx, (0, 0), 3); jyy = cv2.GaussianBlur(gy * gy, (0, 0), 3); jxy = cv2.GaussianBlur(gx * gy, (0, 0), 3)
    th = 0.5 * np.arctan2(2 * jxy, jxx - jyy) + np.pi / 2           # stroke direction = perpendicular to dominant gradient
    out = np.zeros_like(hp); bins = np.round((th % np.pi) / np.pi * nb).astype(int) % nb
    for b in range(nb):
        an = b * np.pi / nb; k = np.zeros((ln, ln), np.float32); c = ln // 2
        cv2.line(k, (int(round(c - c * np.cos(an))), int(round(c - c * np.sin(an)))), (int(round(c + c * np.cos(an))), int(round(c + c * np.sin(an)))), 1.0, 1)
        out = np.where(bins == b, cv2.filter2D(hp, -1, k / k.sum()), out)
    return np.clip(1 + 1.8 * (out - 1), 0.5, 1.5).astype(np.float32)

class Tongue:
    pass

def make_tongues(z, zp0, gser, peaks, r, firepx, BR=None):
    """deterministic spawn list for zone z. rate follows the static glow (squared); extra tall fast licks at glow peaks."""
    out = []; dt = 1 / 120.0
    def spawn(tb, flare=False):
        zp = zp0; q = Tongue(); q.z = z
        q.x0 = float(np.clip(zp["xc"] + r.normal(0, zp["xw"]), zp["xa"], zp["xb"]))
        q.bright = -1.0
        if "hot" in zp0 and BR is not None:     # underlying paint brightness over the tongue's footprint decides the style
            wd = 0.4 * np.mean(zp0["w"]); ya = int(zp0["base_y"] - 0.6 * zp0["Hf"]); yb = int(zp0["base_y"] - 0.05 * zp0["Hf"])
            q.bright = float(BR[ya:yb, int(q.x0 - wd):int(q.x0 + wd) + 1].mean())
            if q.bright > zp0.get("hot_thr", 0.5):
                zp = {**zp0, **zp0["hot"]}
                if r.random() > zp0["hot"].get("keep", 1.0): return
        q.zp = zp; q.style = "hot" if zp is not zp0 else "dark"; Hf = zp["Hf"]
        if zp.get("flare_spread") and flare: tb = tb + r.uniform(*zp["flare_spread"])
        q.tb = tb; fast = flare or (r.random() < zp.get("p_fast", 0.3))
        q.w = r.uniform(*zp["w"]) * (0.85 if fast else 1.0)
        q.L = Hf * (r.uniform(.8, 1.25) if fast else r.uniform(.3, .75)) * (1.15 if flare else 1.0)
        if zp.get("L_from_cap"):     # heights drawn under the cap (not all clipped to Lmax -> no equal-height crown)
            q.L = zp["Lmax"] * (r.uniform(*zp.get("Lf_fast", [.5, 1.0])) if fast else r.uniform(*zp.get("Lf_slow", [.22, .6])))
        ds = zp.get("desync", 0.0)
        if ds:                       # a tall tongue born close in time to another tall one is made short (asymmetric heights/phases)
            for o_ in out:
                if abs(o_.tb - tb) < ds and o_.L > 0.6 * zp.get("Lmax", Hf) and q.L > 0.45 * zp.get("Lmax", Hf):
                    q.L *= r.uniform(*zp.get("desync_k", [0.35, 0.6])); break
        v0 = Hf * (r.uniform(2.4, 3.6) if fast else r.uniform(0.7, 1.4))
        a = np.arange(0, 3.0, dt); v = np.full_like(a, v0)
        # speed changes: 0-2 bursts (snaps) and a slow lazy drift in speed (non-periodic)
        for _ in range(r.poisson(0.9 if fast else 0.6)):
            ab, bd, bm = r.uniform(0, 0.5), r.uniform(0.06, 0.18), r.uniform(1.0, 3.0); v = v * (1 + bm * smooth_bump((a - ab) / bd))
        v = v * (1 + 0.35 * np.interp(a, np.linspace(0, 3, 13), r.uniform(-1, 1, 13)))
        Stip = np.cumsum(v) * dt
        idet = int(np.searchsorted(Stip, q.L)); idet = min(idet, len(a) - 1)
        vb = np.zeros_like(a); kb = r.uniform(1.3, 2.3)
        vb[idet:] = v[idet:] * kb * (1 + 1.5 * np.clip((a[idet:] - a[idet]) / 0.25, 0, 1))   # base snaps up, accelerating -> pinch-off
        Sbase = np.cumsum(vb) * dt
        alive = Stip - Sbase > 1.0; alive[:2] = True; iend = int(np.argmin(alive)) if not alive.all() else len(a) - 1
        # zone ceiling: never reach the zone's top edge (avoid a straight cut); the tongue burns off before it
        ceil = min(zp["base_y"] - zp["ytop"] - 6, zp.get("Hcap", 1e9))
        over = np.nonzero(Stip > ceil)[0]
        if len(over): iend = min(iend, int(over[0]))
        q.ceil = ceil; q.a = a[:iend + 1]; q.Stip = Stip[:iend + 1]; q.Sbase = Sbase[:iend + 1]; q.adet = a[idet]; q.T = q.a[-1]
        q.L = min(q.L, zp.get("Lmax", 1e9))
        q.w = max(q.w, zp.get("w_per_L", 0.2) * q.L)
        nl = int(r.integers(zp.get("lobes", [1, 1])[0], zp.get("lobes", [1, 1])[1] + 1))
        q.lobes = [(0.0, 1.0, 1.0, r.uniform(0, 200))] + [(r.uniform(-0.45, 0.45) * q.w, r.uniform(0.45, 0.85), r.uniform(0.5, 0.8), r.uniform(0, 200)) for _ in range(nl - 1)]  # (dx, length frac, width frac, seed)   # long licks keep a real body
        q.hot = r.uniform(0.75, 1.0) if fast else r.uniform(0.55, 0.9)
        q.lean = r.normal(0, 0.18) * q.L; q.wav = r.uniform(0.5, 1.6); q.seed = r.uniform(0, 200)
        q.fork_v = r.uniform(0.45, 0.75); q.fork_sep = r.uniform(0.5, 1.2) if r.random() < zp.get("p_fork", 0.6) else 0.0
        q.jag = r.uniform(0.25, 0.45); q.flare = flare
        i = r.integers(len(firepx)); q.sx, q.sy = float(firepx[i][1]), float(firepx[i][0])   # source stroke patch (plate), rides with the tongue
        out.append(q)
    t = -1.2; gmean = 1.0
    while t < 6.0:
        g = np.interp(t, np.arange(180) / 30.0, gser); rate = zp0["rate"] * (g / gmean) ** zp0.get("rate_k", 2.0)
        t += r.exponential(1 / max(rate, 0.05))
        if t < 6.0: spawn(t)
    for pk in peaks:
        for _ in range(r.integers(1, zp0.get("flare_nmax", 2) + 1)): spawn(pk / 30.0 + r.uniform(-0.05, 0.08), flare=True)
    return out

class Sparks:
    def __init__(s, zp_all, zones, gpeaks, r):
        s.parts = []; dt = 1 / 240.0
        for z, zp in zp_all.items():
            sp = zp.get("sparks");
            if not sp: continue
            zm = zones[z] > 0
            ev = []; t = -0.5
            while t < 6.0:
                t += r.exponential(1 / sp["burst_rate"]); ev.append(t)
            ev += [p / 30.0 for p in gpeaks[z]]
            for tb in ev:
                bx = np.clip(zp["xc"] + r.normal(0, zp["xw"]), zp["xa"], zp["xb"]); by = zp["base_y"] - r.uniform(2, 0.35 * zp["Hf"])
                for _ in range(r.integers(sp["n"][0], sp["n"][1] + 1)):
                    t0 = tb + r.uniform(0, 0.12); life = r.uniform(*sp["life"]); n = int(life / dt) + 2
                    vy = -r.uniform(*sp["vy"]); vx = r.normal(0, sp["vx"]); x, y = bx + r.normal(0, 2), by + r.normal(0, 2)
                    X = np.empty(n); Y = np.empty(n); kick = sp["jit"]
                    for k in range(n):
                        if k % 8 == 0: vx += r.normal(0, kick)             # erratic sideways jitter (random kicks ~30 Hz)
                        vy = min(vy * (1 - 1.6 * dt), -25.0); vx *= (1 - 3.0 * dt)  # drag, never stops rising
                        x += vx * dt; y += vy * dt; X[k] = x; Y[k] = y
                    ins = zm[np.clip(Y.astype(int), 0, zm.shape[0] - 1), np.clip(X.astype(int), 0, zm.shape[1] - 1)]
                    kend = int(np.argmin(ins)) if not ins.all() else n         # dies when it leaves the fire zone (occluded / out)
                    if kend < 3: continue
                    s.parts.append(dict(t0=t0, dt=dt, X=X[:kend], Y=Y[:kend], b=r.uniform(*sp["bright"]), tau=r.uniform(0.25, 0.6) * life, fl=r.uniform(0, 100), seed=r.integers(1 << 30)))
    def at(s, t, shutter):
        out = []
        for q in s.parts:
            a = t - q["t0"]; k1 = int(a / q["dt"]); k0 = int((a - shutter) / q["dt"])
            if a < 0 or k1 >= len(q["X"]): continue
            k0 = max(k0, 0); fl = 0.55 + 0.45 * np.random.default_rng(q["seed"] + int(t * 30)).random()
            out.append((q["X"][k0], q["Y"][k0], q["X"][k1], q["Y"][k1], q["b"] * np.exp(-a / q["tau"]) * fl * ss(0, 0.03, a)))
        return out

def main():
    tag, spec = sys.argv[1], json.load(open(sys.argv[2])); N = int(sys.argv[3]) if len(sys.argv) > 3 else 180; mode = sys.argv[4] if len(sys.argv) > 4 else "iter"
    f0 = int(spec.get("f0", 0)) if mode == "iter" else 0
    od = f"v13/iter/{tag}" if mode == "iter" else "v13/work"; os.makedirs(od, exist_ok=True)
    plate, zones, allowed, named = F.load_all(spec.get("maskver", "_b"))
    pf = plate.astype(np.float32); lum = pf @ np.array([.299, .587, .114], np.float32)
    tex = np.clip(lum / (cv2.GaussianBlur(lum, (0, 0), spec.get("tex_sigma", 3.0)) + 1.0), 0.55, 1.45).astype(np.float32)   # brushstroke detail
    stex = stroke_tex(lum); stex_s = cv2.GaussianBlur(stex, (0, 0), spec.get("dry_sigma", 1.2))
    BR = cv2.GaussianBlur(ss(spec.get("br_lo", 195.0), spec.get("br_hi", 235.0), lum).astype(np.float32), (0, 0), 3.0)   # 1 = white-hot / bright-yellow paint
    firecls = (lum > 120) & (pf[..., 0] > 190) & (pf[..., 0] - pf[..., 2] > 90)
    gl = spec["global"]; ZP = spec["zones"]; r = np.random.default_rng(spec.get("seed", 11))
    # ROI
    allz = np.maximum.reduce([zones[z] for z in ZN]) > 0; ys, xs = np.nonzero(allz)
    c = [F.plate2out(x, y, fi) for x in (xs.min() - 4, xs.max() + 4) for y in (ys.min() - 4, ys.max() + 4) for fi in (0, 179)]
    rx0 = int(min(p[0] for p in c)) // 2 * 2 - 8; ry0 = int(min(p[1] for p in c)) // 2 * 2 - 8; rx1 = int(max(p[0] for p in c)) // 2 * 2 + 10; ry1 = int(max(p[1] for p in c)) // 2 * 2 + 10
    Xg, Yg = np.meshgrid(np.arange(rx0, rx1, dtype=np.float32), np.arange(ry0, ry1, dtype=np.float32))
    base = F.decode_yuv(F.STATIC); assert len(base) == 180
    # glow series per zone (static output Y over the brightest painted px of the zone)
    gser, peaks = {}, {}
    for z in ZN:
        zm = zones[z] > 0; gm = (zm & (lum > np.percentile(lum[zm], 60))).astype(np.float32); vals = []
        for fi in range(180):
            px, py = F.out2plate(Xg, Yg, fi); m = cv2.remap(gm, px, py, cv2.INTER_NEAREST) > 0.5; vals.append(float(base[fi][:H][ry0:ry1, rx0:rx1][m].mean()))
        g = np.array(vals); g = g / g.mean(); gser[z] = g
        pk = [i for i in range(3, 177) if g[i] == g[max(0, i - 7):i + 8].max() and g[i] > 1.0 + gl.get("peak_thr", 0.04)]; peaks[z] = pk
    TG = []
    for z in ZN:
        if z not in ZP: continue
        zm = zones[z] > 0; fz = (cv2.dilate(zm.astype(np.uint8), np.ones((31, 31), np.uint8)) > 0) & firecls
        TG += make_tongues(z, ZP[z], gser[z], peaks[z], r, np.argwhere(fz), BR)
    SP = Sparks({z: ZP[z] for z in ZP}, zones, peaks, r)
    Pe = Perlin3(901); Pw = Perlin3(902); Q_gap = []
    fzm = cv2.GaussianBlur(((zones["z1"] > 0) | (zones["z2"] > 0)).astype(np.float32), (0, 0), 2.0)
    def FZ_out(fi): return cv2.remap(fzm, *F.out2plate(Xg, Yg, fi), cv2.INTER_LINEAR)
    protimg = np.repeat((~allowed)[..., None].astype(np.float32) * 255, 3, 2)
    zone_any = allowed.astype(np.float32)
    enc = None
    if mode == "final":
        outp = f"v13/work/{tag}_lossless420.mp4"; assert not os.path.exists(outp)
        enc = subprocess.Popen(["ffmpeg", "-n", "-v", "error", "-f", "rawvideo", "-pix_fmt", "yuv420p", "-s", f"{W}x{H}", "-r", "30", "-i", "pipe:0", "-an",
                                "-c:v", "libx264", "-qp", "0", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30", outp], stdin=subprocess.PIPE)
    q = dict(frames=0, layer_px_mean=0.0, hold_px_mean=0.0, tongues=len(TG), sparks=len(SP.parts), peaks=peaks, roi=[rx0, ry0, rx1, ry1], alive=[]); keep = []; t0 = time.time()
    RW, RH = rx1 - rx0, ry1 - ry0
    for fi in range(f0, f0 + N):
        t = fi / 30.0; fr = base[fi]; Yp = fr[:H]; Up = fr[H:H + H // 4].reshape(H // 2, W // 2); Vp = fr[H + H // 4:].reshape(H // 2, W // 2)
        px, py = F.out2plate(Xg, Yg, fi)
        Yr = Yp[ry0:ry1, rx0:rx1]; Ur = cv2.resize(Up[ry0 // 2:ry1 // 2, rx0 // 2:rx1 // 2], (RW, RH), interpolation=cv2.INTER_NEAREST)
        Vr = cv2.resize(Vp[ry0 // 2:ry1 // 2, rx0 // 2:rx1 // 2], (RW, RH), interpolation=cv2.INTER_NEAREST); brgb = F.yuv2rgb(Yr, Ur, Vr)
        C = np.zeros((RH, RW, 3), np.float32); A = np.zeros((RH, RW), np.float32); nal = 0; Tm = np.zeros((RH, RW), np.float32); Om = np.zeros((RH, RW), np.float32)
        stp = gl.get("layer_step", 1); tl = (fi // stp) * stp / 30.0   # tongue layer held for `stp` frames (sparks stay 30 fps)
        for tg in sorted(TG, key=lambda u: u.tb):
            a = tl - tg.tb
            if a < 0 or a > tg.T: continue
            k = min(int(a * 120), len(tg.Stip) - 1); zp = tg.zp; nal += 1
            ytip = zp["base_y"] - tg.Stip[k]; ybase = zp["base_y"] - tg.Sbase[k]; Lc = max(ybase - ytip, 1.0); attached = a < tg.adet
            detp = 0.0 if attached else float(np.clip((a - tg.adet) / max(tg.T - tg.adet, 1e-3), 0, 1))
            # output-space bbox of the tongue
            xa_, xb_ = tg.x0 - tg.w - abs(tg.lean) - 6, tg.x0 + tg.w + abs(tg.lean) + 6; ya_, yb_ = ytip - 3, ybase + (6 if attached else 3)
            (X0, Y0), (X1, Y1) = F.plate2out(xa_, ya_, fi), F.plate2out(xb_, yb_, fi)
            i0, i1 = max(int(Y0 - ry0) - 1, 0), min(int(Y1 - ry0) + 2, RH); j0, j1 = max(int(X0 - rx0) - 1, 0), min(int(X1 - rx0) + 2, RW)
            if i1 <= i0 or j1 <= j0: continue
            x = px[i0:i1, j0:j1].astype(np.float64); y = py[i0:i1, j0:j1].astype(np.float64)
            qv = (ybase - y) / Lc                                   # 0 at base, 1 at tip
            qc = np.clip(qv, 0, 1)
            # ---- lobed body: union of 1..n lobes sharing the root (broad, irregular, multi-lobed licks) ----
            d = np.full_like(x, -1e3); core = np.zeros_like(x); dist0 = None
            for li, (ldx, lf, wf, ls) in enumerate(tg.lobes):
                ql = np.clip(qv / lf, 0, 1)
                axis = tg.x0 + ldx * ql ** 0.7 + tg.lean * lf * ql ** 1.5 + tg.wav * 2.0 * Pw(np.full_like(x, ls if li else tg.seed), ql * Lc * lf / 14.0, 0.25 * a)
                hw = 0.5 * tg.w * wf * (1 - ql) ** zp.get("taper", 0.45) * (1.0 - 0.45 * detp)
                hw = hw * (1 + zp.get("wvar", 0.0) * Pw(np.full_like(x, ls + 50), qv * Lc / 9.0, 0.35 * a))      # variable width along the height (bulges / necks)
                hw = hw * min(1.0, Lc * lf / (zp.get("grow_k", 2.5) * tg.w * wf)) ** 0.7
                if not attached: hw = hw * ss(0, 0.45, ql) ** 0.8
                dist = np.abs(x - axis)
                if li == 0 and tg.fork_sep > 0:
                    fv = np.clip((qc - tg.fork_v) / (1 - tg.fork_v), 0, 1); sep = tg.fork_sep * tg.w * fv
                    d2 = np.minimum(np.abs(x - (axis - 0.45 * sep)), np.abs(x - (axis + 0.55 * sep))); dist = np.where(fv > 0, d2, dist)
                    hw = np.where(fv > 0, hw * (1 - 0.3 * fv), hw)
                dl = np.where(qv <= lf, hw - dist, -1e3)
                core = np.maximum(core, np.where(qv <= lf, np.clip(1 - dist / (hw + 0.5), 0, 1), 0)); d = np.maximum(d, dl)
                if li == 0: axis0 = axis
            # source stroke patch riding with the tongue (texture moves up with the tip; same brushwork scale)
            sxm = (tg.sx + (x - axis0)).astype(np.float32); sym = (tg.sy + (y - ytip) - 0.5 * Lc).astype(np.float32)
            tx = cv2.remap(tex, sxm, sym, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            stxs = cv2.remap(stex_s, sxm, sym, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            stx = cv2.remap(stex, sxm, sym, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)       # plate stroke-direction texture
            jag = fbm(Pe, (x - tg.x0) / 2.4 + tg.seed, (y - ytip) / 3.2, tg.seed * 0.1 + 0.6 * a, 3, gain=0.6)
            lump = Pe((x - tg.x0) / 6.0 + tg.seed, (y - ytip) / 7.0, tg.seed * 0.2 + 0.4 * a)
            d = d + min(1.0, Lc / (1.5 * tg.w)) * zp.get("jag_k", 1.0) * tg.jag * tg.w * (zp.get("jag0", 0.12) + qc ** 1.4) * jag + zp.get("lump", 0.0) * tg.w * lump + zp.get("kt", 0.9) * (tx - 1.0) * tg.w \
                  + zp.get("kst", gl.get("kst", 0.0)) * (stx - 1.0) * tg.w - 0.6 * tg.w * detp ** 2
            inside = (qv >= -0.02 if not attached else qv >= -0.15) & (qv <= 1.0)
            ae = np.clip(d / gl.get("aa", 0.8) + 0.5, 0, 1) * inside
            # dry-brush breakup: within an edge band only the bright stroke ridges of the plate texture keep paint
            band = max(zp.get("dry_band", gl.get("dry_band", 0.0)) * tg.w, 1e-3) if zp.get("dry_band", gl.get("dry_band", 0.0)) > 0 else 0.0
            if band > 1e-2: ae = ae * ss(-0.12, 0.12, (stxs - 1.0) * gl.get("dry_k", 1.0) + 0.7 * np.clip(d / band, 0, 1) - gl.get("dry_thr", 0.25))
            if attached: ae = ae * ss(-0.15, 0.0, qv + zp.get("base_jit", 0.0) * Pe((x - tg.x0) / 4.0 + tg.seed, 0.0 * x + 3.1, 0.3 * a) / Lc)          # merges into painted fire at the base (hidden by coal/paint)
            ae = ae * (1 - ss(zp.get("cap_fade", 0.75) * tg.ceil, tg.ceil, tg.Stip[k]) * ss(0.3, 1.0, qc))   # tips thin out before the height cap
            if not ae.any(): continue
            pv = 0.45 + 0.55 * ss(0.0, 0.22, qc) * (1 - 0.75 * ss(0.3, 1.0, qc))      # deeper at the very base and toward the tips, hottest low-middle
            T = tg.hot * core ** gl.get("core_k", 1.2) * pv * (1 - 0.35 * detp) * tx ** 1.3 * zp.get("heat", 1.0)
            T = gl.get("t_floor", 0.28) + (1 - gl.get("t_floor", 0.28)) * T            # thinnest px are deep red-orange, never brown-black
            T = np.clip(T + zp.get("rim_dark", 0.0) * (ss(0, zp.get("rim_w", 1.5), d) - 1), 0, 1)   # painted darker red contour
            if zp.get("t_lift", 0):   # luminance-matched licks: over bright paint the lick is amber/golden, not a darker silhouette
                T = np.maximum(T, zp["t_lift"] * cv2.remap(BR, x.astype(np.float32), y.astype(np.float32), cv2.INTER_LINEAR) * (0.75 + 0.25 * ss(0, 2.0, d)))
            nb = zp.get("poster", gl.get("poster", 0))
            if nb: Tn = T * nb; fr_ = Tn - np.floor(Tn); T = (np.floor(Tn) + ss(0.5 - gl.get("poster_soft", 0.15), 0.5 + gl.get("poster_soft", 0.15), fr_)) / nb   # flat painted tone bands
            col = grade(T) * np.clip(tx, 0.9, 1.1)[..., None] ** 0.5
            if zp.get("b_mul", 1.0) != 1.0: col = col.copy(); col[..., 2] *= zp["b_mul"]   # saturate: no pale cream cores next to the saturated yellow paint
            g = float(np.interp(t, np.arange(180) / 30.0, gser[tg.z]))
            r0 = zp.get("rim0", gl.get("rim0", 0.55)); ot = zp.get("o_thin", gl.get("o_thin", 0.4))
            o = ae * (r0 + (1 - r0) * ss(0, 2.0, d)) * (ot + (1 - ot) * ss(0.15, 0.6, T)) * zp.get("gain", 0.9) * min(g ** zp.get("glow_k", 1.0), 1.25)
            o = np.clip(o, 0, gl.get("amax", 0.92))
            T = np.minimum(T, zp.get("t_max", 1.0))   # keep forge licks in deep orange/red over the yellow paint (no flat white cut-outs)
            if zp.get("merge", 0):   # merged mass: max-union of heat/opacity -> no internal outlines where tongues overlap
                Tm[i0:i1, j0:j1] = np.maximum(Tm[i0:i1, j0:j1], T * (o > 0.02)); Om[i0:i1, j0:j1] = np.maximum(Om[i0:i1, j0:j1], o); continue
            Cs = C[i0:i1, j0:j1]; As = A[i0:i1, j0:j1]
            col = (col / 255.0) ** gl.get("lin_gamma", 2.2)   # premultiplied in linear light (no muddy red/yellow mixes)
            C[i0:i1, j0:j1] = Cs * (1 - o[..., None]) + col * o[..., None]; A[i0:i1, j0:j1] = As * (1 - o) + o
        if Om.any():   # merged mass goes UNDER the single (v11-style) tongues: premultiplied C_tot = C + (1 - A) * Cmass
            cm = (grade(Tm) / 255.0) ** gl.get("lin_gamma", 2.2); C = C + (1 - A)[..., None] * cm * Om[..., None]; A = A + (1 - A) * Om
        gt = spec.get("gap_tint")
        if gt and A.any():   # warm gap tint: cream/white-hot paint near (and between/inside) forge licks -> amber, soft gradient
            sig = gt.get("sigma", 6.0) * float(F.cam(fi)[0])
            prox = np.clip(cv2.GaussianBlur(A * FZ_out(fi), (0, 0), sig) / gt.get("p_full", 0.25), 0, 1) ** gt.get("p_pow", 0.8)
            bc = np.clip(brgb, 0, 255); lb = bc @ np.array([.299, .587, .114], np.float32); wb = (bc[..., 0] - bc[..., 2]) / (bc[..., 0] + 1.0)
            cream = ss(gt.get("l_lo", 205.0), gt.get("l_hi", 240.0), lb) * ss(gt.get("w_hi", 0.62), gt.get("w_lo", 0.3), wb)
            if gt.get("cream_sigma", 0): cream = cv2.GaussianBlur(cream.astype(np.float32), (0, 0), gt["cream_sigma"] * float(F.cam(fi)[0]))   # paint has blocky 8px texture: soft mask, no square patches
            at = np.clip(gt.get("k", 0.6) * prox * cream * (1 - A), 0, 1)
            if gt.get("stex", 0): at = at * np.clip(1 + gt["stex"] * (cv2.remap(stex, px, py, cv2.INTER_LINEAR) - 1), 0, 1.5)   # follows the brush strokes
            at = np.clip(at, 0, gl.get("amax", 0.92))
            tc = (np.array(gt.get("col", [255, 196, 70]), np.float32) / 255.0) ** gl.get("lin_gamma", 2.2)
            C = C + at[..., None] * tc; A = A + at; Q_gap.append(float((at > 1e-4).sum()))
        # sparks: hard 1-px streaks (supersampled AA line from pos(t - shutter) to pos(t)), additive
        SS = 4; can = np.zeros((RH * SS, RW * SS), np.float32)
        for (xa, ya, xb, yb, b) in SP.at(t, gl.get("shutter", 1 / 60)):
            (Xa, Ya), (Xb, Yb) = F.plate2out(xa, ya, fi), F.plate2out(xb, yb, fi)
            pa = (int((Xa - rx0) * SS), int((Ya - ry0) * SS)); pb = (int((Xb - rx0) * SS), int((Yb - ry0) * SS))
            cv2.line(can, pa, pb, float(min(b, 1.0)), gl.get("spark_th", 5), cv2.LINE_AA)
        sk = cv2.resize(can, (RW, RH), interpolation=cv2.INTER_AREA) * gl.get("spark_gain", 1.6)
        # holdout (output space, any >0 influence, +1 px, 2x2 block aligned) -- identical construction to v10
        ho = np.asarray(P.frame_out(protimg, F.BOX, F.SEG, fi))[ry0:ry1, rx0:rx1, 0] > 0
        ho = cv2.dilate(ho.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        ho2 = ho.reshape(RH // 2, 2, RW // 2, 2).any((1, 3)); ho = np.repeat(np.repeat(ho2, 2, 0), 2, 1)
        fd = np.clip(cv2.distanceTransform((~ho).astype(np.uint8), cv2.DIST_L2, 5) / gl.get("hold_feather", 1.0), 0, 1)
        Af = A * fd; Cf = C * fd[..., None]; skf = np.clip(sk * fd, 0, 1)
        LG = gl.get("lin_gamma", 2.2); bl = (np.clip(brgb, 0, 255) / 255.0) ** LG; cl = C * fd[..., None]; bl = np.clip(bl, 0, 1)
        comp = 255.0 * np.clip(bl * (1 - Af[..., None]) + cl, 0, 1) ** (1 / LG)                                    # over (premultiplied): reds/oranges show over bright paint
        comp = 255 - (255 - comp) * (1 - skf[..., None] * np.array(spec.get("spark_col", [255, 236, 190]), np.float32) / 255.0)
        comp = np.clip(comp, 0, 255)
        touched = ((Af > 1e-4) | (skf > 1e-4)) & ~ho
        ny, nu, nv = F.rgb2yuv(comp)
        Yo = Yp.copy(); Uo = Up.copy(); Vo = Vp.copy()
        Yo[ry0:ry1, rx0:rx1] = np.where(touched, np.clip(np.rint(ny), 0, 255), Yr).astype(np.uint8)
        tb = touched.reshape(RH // 2, 2, RW // 2, 2).any((1, 3)) & ~ho2
        mu = nu.reshape(RH // 2, 2, RW // 2, 2).mean((1, 3)); mv = nv.reshape(RH // 2, 2, RW // 2, 2).mean((1, 3))
        Ub = Up[ry0 // 2:ry1 // 2, rx0 // 2:rx1 // 2]; Vb = Vp[ry0 // 2:ry1 // 2, rx0 // 2:rx1 // 2]
        Uo[ry0 // 2:ry1 // 2, rx0 // 2:rx1 // 2] = np.where(tb, np.clip(np.rint(mu), 0, 255), Ub).astype(np.uint8)
        Vo[ry0 // 2:ry1 // 2, rx0 // 2:rx1 // 2] = np.where(tb, np.clip(np.rint(mv), 0, 255), Vb).astype(np.uint8)
        assert (Yo[ry0:ry1, rx0:rx1][ho] == Yr[ho]).all() and (Uo[ry0 // 2:ry1 // 2, rx0 // 2:rx1 // 2][ho2] == Ub[ho2]).all()
        q["frames"] += 1; q["layer_px_mean"] += float(touched.sum()); q["hold_px_mean"] += float(ho.sum()); q["alive"].append(nal)
        frame = np.concatenate([Yo.ravel(), Uo.ravel(), Vo.ravel()])
        if enc: enc.stdin.write(frame.tobytes())
        else: keep.append(frame)
        if (fi - f0) % 30 == 0: print(fi, round(time.time() - t0, 1), nal, flush=True)
    q["gap_tint_px_mean"] = float(np.mean(Q_gap)) if Q_gap else 0.0; q["styles"] = {z: {s_: sum(1 for u in TG if u.z == z and u.style == s_) for s_ in ("hot", "dark")} for z in ZN}
    q["layer_px_mean"] /= q["frames"]; q["hold_px_mean"] /= q["frames"]; q["sec_per_frame"] = round((time.time() - t0) / q["frames"], 3)
    q["glow_series"] = {z: [round(float(v), 4) for v in gser[z]] for z in ZN}
    if enc: enc.stdin.close(); assert enc.wait() == 0
    else: np.save(f"{od}/frames_yuv.npy", np.stack(keep)); json.dump(dict(f0=f0, N=N), open(f"{od}/range.json", "w"))
    json.dump(q, open(f"{od}/{tag}_layer_qc.json" if mode == "final" else f"{od}/layer_qc.json", "x" if mode == "final" else "w"))
    print("DONE", {k: v for k, v in q.items() if k not in ("glow_series", "alive")}, "alive mean", np.mean(q["alive"]))
if __name__ == "__main__": main()
