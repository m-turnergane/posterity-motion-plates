"""v10: NEW-material fire layer composited in OUTPUT space over the decoded v2c static frames (painted flames stay a static base).
Layer = procedural rising flame field (noise advected strictly upward in a height-stretched coordinate; threshold rises with height ->
tongues detach, thin and burn off above the painted tips; colour ramp sampled from the plate's own flame paint) + a few rising embers.
Screen composite with caps. Hard holdout = camera-mapped protect (any >0, dilated, 2x2-chroma-block aligned), so protected px and every
px the layer leaves at 0 are bit-identical (Y and chroma) to v2c static.
usage: fire_v10.py TAG SPEC.json [N] [mode: iter|final]"""
import sys, os, json, subprocess, time, numpy as np, cv2
sys.path.insert(0, 'tools'); import prod as P; from noise import Perlin3, fbm
W, H = P.W, P.H; SEG = dict(P.SEG_POC); SEG["frames"] = 180
BOX = P.plate_box(); L0, T0 = BOX[0], BOX[1]; CW, CH = BOX[2] - L0, BOX[3] - T0; SC = max(W / CW, H / CH); OFX, OFY = (CW * SC - W) / 2, (CH * SC - H) / 2
STATIC = "work/final_v09_v2cstatic_lossless.mp4"     # v2c static twin (engine b3 + prod camera; bit-identical to prod per qc/verify_static_vs_prod.json)
def ss(a, b, x): t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)
def cam(fi): u = fi / (SEG["frames"] - 1); return P.cam(SEG, u, fi / 30.0)
def out2plate(X, Y, fi):
    s, cx, cy = cam(fi); xc = X / s + (cx - W / (2 * s)); yc = Y / s + (cy - H / (2 * s)); return (xc + OFX) / SC + L0, (yc + OFY) / SC + T0
def plate2out(x, y, fi):
    s, cx, cy = cam(fi); xc = (x - L0) * SC - OFX; yc = (y - T0) * SC - OFY; return (xc - (cx - W / (2 * s))) * s, (yc - (cy - H / (2 * s))) * s
def decode_yuv(p):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "rawvideo", "-pix_fmt", "yuv420p", "pipe:1"], capture_output=True, check=True).stdout
    return np.frombuffer(r, np.uint8).reshape(-1, H * 3 // 2, W)
# BT.601 limited (ffmpeg default for untagged yuv420p)
def yuv2rgb(Y, U, V):
    y = (Y.astype(np.float32) - 16) * (255 / 219); u = (U.astype(np.float32) - 128) * (255 / 224); v = (V.astype(np.float32) - 128) * (255 / 224)
    return np.stack([y + 1.402 * v, y - 0.344136 * u - 0.714136 * v, y + 1.772 * u], -1)
def rgb2yuv(R):
    r, g, b = R[..., 0], R[..., 1], R[..., 2]; y = 0.299 * r + 0.587 * g + 0.114 * b
    return 16 + y * (219 / 255), 128 + (b - y) / 1.772 * (224 / 255), 128 + (r - y) / 1.402 * (224 / 255)

class Flame:
    """one zone source. h = (base_y - y)/Hf (0 at the coal/base line, 1 at the nominal top). env = allowed zone (soft) x lateral column window.
    procedural rising field evaluated at arbitrary plate coords."""
    def __init__(s, name, zone, p, seed, plate):
        s.p = p; s.name = name; Hh, Ww = zone.shape; s.Hf = float(p["Hf"]); Y = np.arange(Hh, dtype=np.float32)[:, None]; X = np.arange(Ww, dtype=np.float32)[None, :]
        s.h = np.broadcast_to((p["base_y"] - Y) / s.Hf, (Hh, Ww)).astype(np.float32).copy()
        col = np.exp(-0.5 * ((X - p["xc"]) / p["xw"]) ** 2)
        zs = cv2.GaussianBlur((zone > 0).astype(np.float32), (0, 0), 1.0)
        s.env = (zs * col * ss(-0.12, 0.02, s.h)).astype(np.float32); s.env[zone == 0] = 0
        s.zone = zone > 0
        s.P1, s.P2, s.P3 = Perlin3(seed * 10 + 1), Perlin3(seed * 10 + 2), Perlin3(seed * 10 + 3)
        s.htop = 1.0
        # colour ramp from the painted fire in/around this zone: luminance-quantile bins of the brighter half (dark -> bright)
        pf = plate.astype(np.float32); firepx = (pf @ np.array([.299, .587, .114], np.float32) > 140) & (pf[..., 0] > 200) & (pf[..., 0] - pf[..., 2] > 100)
        win = (cv2.dilate(zone, np.ones((41, 41), np.uint8)) > 0) & firepx
        if win.sum() < 300: win = firepx
        px = pf[win]; lum = px @ np.array([.299, .587, .114], np.float32)
        px = px[(lum > np.percentile(lum, p.get("ramp_lo", 20))) & (lum < np.percentile(lum, p.get("ramp_hi", 90)))]; lum = px @ np.array([.299, .587, .114], np.float32); px = px[np.argsort(lum)]
        s.ramp = np.array([np.median(a, 0) for a in np.array_split(px, 24)], np.float32)
        # glow-sense mask: brightest painted px of the zone
        zl = (plate.astype(np.float32) @ np.array([.299, .587, .114], np.float32)); s.gmask = s.zone & (zl > np.percentile(zl[s.zone], 60))
    def field(s, x, y, t):
        """strictly-rising flame density. Pattern coordinate Ys - V t: every feature moves only upward (no back-and-forth); evolution via the
        3rd noise axis (slow morph, not motion). Height stretch -> tongues accelerate/elongate; threshold rises with h -> tongues taper to points,
        detach and burn off. Lateral narrowing with height (tongues converge)."""
        p = s.p; h = s.h_at; Hf = s.Hf
        Ys = Hf * (np.maximum(h, -0.3) + 0.35) ** p.get("stretch", 0.72)
        V = p["V"] * Hf; ev = p.get("ev", 0.6)
        xr = (x - p["xc"]) * (1 + p.get("conv", 0.25) * np.clip(h, 0, 1.5)) + p["xc"]
        wx = p.get("warp", 0.5) * fbm(s.P2, xr / (2.5 * p["sx"]), (Ys - V * t) / (2.5 * p["sy"]), 0.6 * ev * t, 2)
        n1 = fbm(s.P1, xr / p["sx"] + wx, (Ys - V * t) / p["sy"], ev * t, p.get("oct", 3), gain=p.get("ogain", 0.5))
        n2 = fbm(s.P3, xr / (2.2 * p["sx"]) + 0.6 * wx, (Ys - V * t) / (2.0 * p["sy"]), 0.7 * ev * t, 2)
        n = 0.5 + p.get("nk", 1.9) * (0.55 * n1 + 0.45 * n2)
        th = p.get("th0", 0.35) + (p.get("th1", 1.05) - p.get("th0", 0.35)) * ss(p.get("h_lo", 0.15), 1.0, h)
        I = ss(0, 1, (n - th) / p.get("soft", 0.3))
        Ic = ss(0, 1, (n - th) / (p.get("soft", 0.3) * p.get("csoft", 1.0)))   # wider ramp for colour: hot core only deep inside a tongue
        s.cidx = Ic * (1 - p.get("cool", 0.45) * np.clip(h, 0, 1.2))      # colour index: cooler (deeper orange) as it rises
        return I

class Embers:
    def __init__(s, cores, plate, spec, seed):
        r = np.random.default_rng(seed); s.parts = []
        for ci, es in enumerate(spec):
            if es.get("rate", 0) <= 0: continue
            m = cores[ci] > 127; ys, xs = np.nonzero(m); lum = plate[ys, xs].astype(np.float32).mean(1)
            ylo = np.percentile(ys, es.get("base_pct", 55)); sel = (ys >= ylo) & (lum > np.percentile(lum, 50)); ys, xs = ys[sel], xs[sel]
            n = r.poisson(es["rate"] * 7.5)
            for k in range(n):
                i = r.integers(len(xs)); t0 = r.uniform(-1.5, 6.0)
                s.parts.append(dict(x=xs[i] + r.uniform(-.5, .5), y=ys[i] + r.uniform(-.5, .5), t0=t0, life=r.uniform(*es.get("life", [0.6, 1.5])),
                                    vy=-r.uniform(*es.get("vy", [45, 100])), vx=r.normal(0, es.get("vx", 7)), wseed=r.uniform(0, 100), fseed=r.uniform(0, 100),
                                    b=r.uniform(*es.get("bright", [0.55, 1.0])), sz=r.uniform(*es.get("size", [0.6, 1.0])), drag=es.get("drag", 0.35)))
        s.Pw = Perlin3(seed + 77)
    def at(s, t):
        out = []
        for q in s.parts:
            a = t - q["t0"]
            if a < 0 or a > q["life"]: continue
            # monotone rise with drag (never moves down); lateral: constant drift + slow non-periodic wander (integrated low-freq noise, small)
            ky = q["drag"]; y = q["y"] + q["vy"] * (1 - np.exp(-ky * a)) / ky
            x = q["x"] + q["vx"] * a + 4.0 * float(s.Pw(np.array([q["wseed"] + 0.7 * a]), np.array([0.0]), 0.0)[0])
            fl = 0.65 + 0.35 * float(s.Pw(np.array([q["fseed"] + 9 * a]), np.array([5.0]), 1.0)[0]) * 2
            env = ss(0, 0.08, a) * (1 - ss(0.55 * q["life"], q["life"], a))
            out.append((x, y, q["b"] * env * np.clip(fl, 0.2, 1.3), q["sz"] * (1 - 0.35 * a / q["life"])))
        return out

ZN = ["z0low", "z0top", "z1", "z2"]
def load_all(ver=""):
    plate = cv2.cvtColor(cv2.imread(str(P.PLATE)), cv2.COLOR_BGR2RGB)
    zones = {k: cv2.imread(f"v10/masks/P05_v10_zone_{k}{ver}.png", 0) for k in ZN}
    allowed = cv2.imread(f"v10/masks/P05_v10_allowed{ver}.png", 0) > 0; named = cv2.imread(f"v10/masks/P05_v10_named_protect{ver}.png", 0) > 0
    assert not (allowed & named).any()
    return plate, zones, allowed, named

def main():
    tag, spec = sys.argv[1], json.load(open(sys.argv[2])); N = int(sys.argv[3]) if len(sys.argv) > 3 else 180; mode = sys.argv[4] if len(sys.argv) > 4 else "iter"
    f0 = int(spec.get("f0", 0)) if mode == "iter" else 0
    od = f"v10/iter/{tag}" if mode == "iter" else "v10/work"; os.makedirs(od, exist_ok=(mode != "iter"))
    plate, zones, allowed, named = load_all(spec.get("maskver", ""))
    FL = [Flame(k, zones[k], spec["flames"][k], 7 + i, plate) for i, k in enumerate(ZN) if k in spec["flames"]]
    for f in FL:
        if "ramp_from" in f.p: f.ramp = [g for g in FL if g.name == f.p["ramp_from"]][0].ramp.copy()
    EM = Embers([zones[k] for k in ZN], plate, [spec.get("embers", {}).get(k, {}) for k in ZN], 4242)
    env_all = np.maximum.reduce([f.env for f in FL]); ys, xs = np.nonzero(env_all > 0.005)
    # output ROI (union over the push) + margin
    X0, Y0 = plate2out(xs.min() - 6, ys.min() - 6, 0); X1, Y1 = plate2out(xs.max() + 6, ys.max() + 6, 0)
    X0b, Y0b = plate2out(xs.min() - 6, ys.min() - 6, 179); X1b, Y1b = plate2out(xs.max() + 6, ys.max() + 6, 179)
    rx0, ry0 = int(min(X0, X0b)) // 2 * 2 - 8, int(min(Y0, Y0b)) // 2 * 2 - 8; rx1, ry1 = int(max(X1, X1b)) // 2 * 2 + 10, int(max(Y1, Y1b)) // 2 * 2 + 10
    Xg, Yg = np.meshgrid(np.arange(rx0, rx1, dtype=np.float32), np.arange(ry0, ry1, dtype=np.float32))
    base = decode_yuv(STATIC); assert len(base) == 180
    protimg = np.repeat((~allowed)[..., None].astype(np.float32) * 255, 3, 2)   # hold = everything NOT allowed (superset of named protect)
    gl = spec.get("global", {}); cap, maxd, gain = gl.get("cap", 247.0), gl.get("maxd", 80.0), gl.get("gain", 1.0)
    # per-flame glow coupling: static output luminance inside each flame's painted support, normalised (layer breathes with the v2c glow)
    enc = None
    if mode == "final":
        outp = f"v10/work/{tag}_lossless420.mp4"; assert not os.path.exists(outp)
        enc = subprocess.Popen(["ffmpeg", "-n", "-v", "error", "-f", "rawvideo", "-pix_fmt", "yuv420p", "-s", f"{W}x{H}", "-r", "30", "-i", "pipe:0", "-an",
                                "-c:v", "libx264", "-qp", "0", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30", outp], stdin=subprocess.PIPE)
    q = dict(frames=0, layer_px_mean=0.0, hold_px_mean=0.0, max_add=0.0, roi=[rx0, ry0, rx1, ry1]); keep = []; t0 = time.time()
    gser = []
    # glow reference per flame: mean static output RGB inside the camera-mapped painted core, over the shot (layer gain follows the v2c glow ratio)
    for k, f in enumerate(FL):
        cm = cv2.GaussianBlur(f.gmask.astype(np.float32), (0, 0), 1.0); vals = []
        for fj in range(0, 180, 6):
            pxj, pyj = out2plate(Xg, Yg, fj); fr = base[fj]
            Yr_ = fr[:H][ry0:ry1, rx0:rx1].astype(np.float32); m = cv2.remap(cm, pxj, pyj, cv2.INTER_LINEAR) > 0.5; vals.append(Yr_[m].mean())
        f.gref_y = float(np.mean(vals))
    for fi in range(f0, f0 + N):
        t = fi / 30.0; fr = base[fi]; Yp = fr[:H]; Up = fr[H:H + H // 4].reshape(H // 2, W // 2); Vp = fr[H + H // 4:].reshape(H // 2, W // 2)
        px, py = out2plate(Xg, Yg, fi)
        lay = np.zeros(Xg.shape + (3,), np.float32); alpha_tot = np.zeros(Xg.shape, np.float32)
        Yr = Yp[ry0:ry1, rx0:rx1]; Ur = cv2.resize(Up[ry0 // 2:ry1 // 2, rx0 // 2:rx1 // 2], (rx1 - rx0, ry1 - ry0), interpolation=cv2.INTER_NEAREST)
        Vr = cv2.resize(Vp[ry0 // 2:ry1 // 2, rx0 // 2:rx1 // 2], (rx1 - rx0, ry1 - ry0), interpolation=cv2.INTER_NEAREST); brgb = yuv2rgb(Yr, Ur, Vr)
        gf = []; occ = np.zeros(lay.shape[:2], np.float32); hue = np.zeros_like(lay)
        for f in FL:
            e = cv2.remap(f.env, px, py, cv2.INTER_LINEAR, borderValue=0); sel = e > 0.004
            if not sel.any(): gf.append(1.0); continue
            gref = f.gref_y
            f.h_at = cv2.remap(f.h, px, py, cv2.INTER_LINEAR)[sel]
            I = f.field(px[sel].astype(np.float64), py[sel].astype(np.float64), t) * e[sel]
            core_sel = cv2.remap(cv2.GaussianBlur(f.gmask.astype(np.float32), (0, 0), 1.0), px, py, cv2.INTER_LINEAR)[sel] > 0.5
            g_now = float(Yr[sel][core_sel].astype(np.float32).mean()) if core_sel.any() else gref; gf.append(g_now / gref)
            gk = (g_now / gref) ** f.p.get("glow_k", 1.5) if gref > 1 else 1.0
            ci = np.clip(f.cidx, 0, 1) ** f.p.get("cgamma", 0.8) * (len(f.ramp) - 1); i0 = np.floor(ci).astype(int); i1 = np.minimum(i0 + 1, len(f.ramp) - 1); fr_ = (ci - i0)[:, None]
            col = (f.ramp[i0] * (1 - fr_) + f.ramp[i1] * fr_) * np.array(f.p.get("tint", [1.0, 1.0, 1.0]), np.float32)
            a = np.clip(I ** f.p.get("apow", 1.3) * f.p.get("gain", 1.0) * gain * gk, 0, 1)
            cur = lay[sel]; lay[sel] = 255 - (255 - cur) * (1 - a[:, None] * col / 255.0)        # screen-accumulate sources
            oc = f.p.get("occl", 0.0)
            if oc > 0:   # emissive flame body partly hides what is behind it -> saturate toward the flame hue (never touches R up-only logic of screen)
                w_ = a * oc; better = w_ > occ[sel]
                o_ = occ[sel]; o_[better] = w_[better]; occ[sel] = o_
                h_ = hue[sel]; h_[better] = col[better] / np.maximum(col[better].max(1, keepdims=True), 1); hue[sel] = h_
        gser.append(gf)
        # embers (output-space gaussian splats, additive)
        for (x, y, b, sz) in EM.at(t):
            X, Y = plate2out(x, y, fi); X -= rx0; Y -= ry0
            if not (2 < X < rx1 - rx0 - 3 and 2 < Y < ry1 - ry0 - 3): continue
            ix, iy = int(X), int(Y); yy, xx = np.mgrid[iy - 3:iy + 4, ix - 3:ix + 4]; sg = 0.55 + 0.6 * sz
            w = np.exp(-((xx - X) ** 2 + (yy - Y) ** 2) / (2 * sg * sg)) * b * spec.get("ember_gain", 1.0)
            ec = np.array(spec.get("ember_col", [255, 196, 110]), np.float32)
            cur = lay[iy - 3:iy + 4, ix - 3:ix + 4]; lay[iy - 3:iy + 4, ix - 3:ix + 4] = 255 - (255 - cur) * (1 - np.clip(w, 0, 1)[..., None] * ec / 255.0)
        # holdout in OUTPUT space (camera-mapped protect; any >0; dilated 2 px; then 2x2 block aligned)
        ho = np.asarray(P.frame_out(protimg, BOX, SEG, fi))[ry0:ry1, rx0:rx1, 0] > gl.get("hold_thr", 0.0)
        ho = cv2.dilate(ho.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        ho2 = ho.reshape((ry1 - ry0) // 2, 2, (rx1 - rx0) // 2, 2).any((1, 3)); ho = np.repeat(np.repeat(ho2, 2, 0), 2, 1)
        fd = np.clip(cv2.distanceTransform((~ho).astype(np.uint8), cv2.DIST_L2, 5) / gl.get("hold_feather", 2.5), 0, 1)
        # screen composite with caps
        a_l = lay / 255.0 * fd[..., None]
        comp = 255 - (255 - brgb) * (1 - a_l)
        comp = np.minimum(comp, np.maximum(brgb, cap)); comp = np.minimum(comp, brgb + maxd); comp = np.maximum(comp, brgb)
        if occ.any():   # pull the non-dominant channels toward the flame hue at the composite's own peak level (only lowers G/B, never R-peak)
            ow = (occ * fd)[..., None]; tc = hue * comp.max(2, keepdims=True)
            comp = comp + ow * (np.minimum(tc, comp) - comp)
        touched = (a_l.max(2) > 1e-4) & ~ho
        ny, nu, nv = rgb2yuv(comp)
        Yo = Yp.copy(); Uo = Up.copy(); Vo = Vp.copy()
        yr = np.where(touched, np.clip(np.rint(ny), 0, 255), Yr).astype(np.uint8); Yo[ry0:ry1, rx0:rx1] = yr
        tb = touched.reshape((ry1 - ry0) // 2, 2, (rx1 - rx0) // 2, 2).any((1, 3)) & ~ho2
        mu = nu.reshape((ry1 - ry0) // 2, 2, (rx1 - rx0) // 2, 2).mean((1, 3)); mv = nv.reshape((ry1 - ry0) // 2, 2, (rx1 - rx0) // 2, 2).mean((1, 3))
        # chroma: only where the block is touched; blend toward the new chroma by the block's mean layer weight so untouched-looking px keep base hue
        Ub = Up[ry0 // 2:ry1 // 2, rx0 // 2:rx1 // 2]; Vb = Vp[ry0 // 2:ry1 // 2, rx0 // 2:rx1 // 2]
        Uo[ry0 // 2:ry1 // 2, rx0 // 2:rx1 // 2] = np.where(tb, np.clip(np.rint(mu), 0, 255), Ub).astype(np.uint8)
        Vo[ry0 // 2:ry1 // 2, rx0 // 2:rx1 // 2] = np.where(tb, np.clip(np.rint(mv), 0, 255), Vb).astype(np.uint8)
        # sanity: holdout exact
        assert (Yo[ry0:ry1, rx0:rx1][ho] == Yr[ho]).all()
        q["frames"] += 1; q["layer_px_mean"] += float(touched.sum()); q["hold_px_mean"] += float(ho.sum()); q["max_add"] = max(q["max_add"], float((comp - brgb).max()))
        frame = np.concatenate([Yo.ravel(), Uo.ravel(), Vo.ravel()])
        if enc: enc.stdin.write(frame.tobytes())
        else: keep.append(frame)
        if (fi - f0) % 30 == 0: print(fi, round(time.time() - t0, 1), flush=True)
    q["layer_px_mean"] /= q["frames"]; q["hold_px_mean"] /= q["frames"]; q["glow_series_flame_lum"] = gser; q["sec_per_frame"] = round((time.time() - t0) / q["frames"], 3)
    if enc: enc.stdin.close(); enc.wait()
    else: np.save(f"{od}/frames_yuv.npy", np.stack(keep)); json.dump(dict(f0=f0, N=N), open(f"{od}/range.json", "w"))
    json.dump(q, open(f"{od}/{tag}_layer_qc.json" if mode == "final" else f"{od}/layer_qc.json", "x" if mode == "final" else "w"))
    print("DONE", {k: v for k, v in q.items() if k != "glow_series_flame_lum"})
if __name__ == "__main__": main()
