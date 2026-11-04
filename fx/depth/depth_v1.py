"""depth_v1: 2.5D depth layers + restrained camera moves from ONE painted plate (R&D, 2026-10-30).

The plate is split into 2-4 RIGID layers (far -> near). Every layer is a flat RGBA card; each frame every layer is
resampled exactly ONCE by its own uniform-scale + translate affine (no rotation, no shear, no mesh, no flow, no
per-pixel displacement), then the cards are composited back-to-front with premultiplied "over". The camera push,
the lateral drift / orbit and the cover-fit framing are all folded into that ONE matrix per layer (layer_affine()).
There is no global push on the composite.

Mattes (cfg["matte"]["mode"]):
  "hybrid" (default): hard layer membership = depth band from Depth Anything V2 Small (ONNX, CPU, ~1.5 s/plate,
           cached .npy) AND/OR hand polygons from the config (include / exclude / force), then an edge-aware guided
           filter (guide = plate) turns the hard cut into a 1-3 px soft alpha that sits on the painted edge.
  "poly":  pure hand polygons (feathered by a Gaussian), no model. Used as the baseline in DEPTH_MODEL_EVAL.md.
  "depth": depth band only (no polygons), guided-filter edges.
Disocclusion: each layer k is EXTENDED under the nearer layers by R px (R >= max relative layer offset + margin) and
that extension is pre-filled from layer k's own pixels only (cv2.inpaint TELEA with every non-own pixel masked, so a
nearer figure's colours can never be sources) + matched grain. The far layer is filled everywhere under nearer layers.
Edge colours are un-mixed (F = (C - (1-a) B) / a) against the composite of the farther layers, so a moving edge carries
no background fringe (no halo), and the zero-motion composite reproduces the plate (proof: recon PSNR).

CLI (all outputs refuse to overwrite):
  depth_v1.py render <cfg.json> <out.mp4> [--size 540x960] [--seconds S] [--crf N]
  depth_v1.py reel   <reel.json> <out.mp4>
  depth_v1.py proof  <cfg.json> <out.json>    disocclusion + rigidity + single-transform + recon + guardrail
  depth_v1.py stats  <cfg.json> <out.json>    phone 360x640 (or 640x360) swing / jitter / >5 Hz
  depth_v1.py layers <cfg.json> <out.png>     contact sheet: plate | depth | layer mattes | filled far layer
  depth_v1.py maxgrab <cfg.json> <out.png>    frame at max offset | revealed px (magenta) | fill close-up
Effects API (see README "Composing with locked effects"): DepthShot.frame(e, size, o, plate_fx=, layer_fx=, screen_fx=, t=).
"""
import importlib.util, json, math, sys, time, hashlib, subprocess
from pathlib import Path
import numpy as np, cv2

HERE = Path(__file__).resolve().parent
MODEL = HERE / "models" / "da2_small.onnx"      # onnx-community/depth-anything-v2-small (Apache-2.0), 99 MB
CACHE = HERE / "cache"
cv2.setNumThreads(4)

def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
try:
    G = _load("guardrails", HERE.parent.parent / "motion" / "guardrails.py")
except Exception as e:                                            # noted in every proof json
    G = None; G_ERR = repr(e)

# ------------------------------------------------------------------ the ONE resampler (instrumented)
WARP_LOG = []                                                   # (frame_id, layer_name) for the single-transform proof
INTERP = cv2.INTER_LANCZOS4
def _warp(img, M, size, tag):
    """The only call to cv2.warpAffine in this module. tag = (frame_id, layer_name)."""
    WARP_LOG.append(tag)
    return cv2.warpAffine(img, M, size, flags=INTERP, borderMode=cv2.BORDER_REPLICATE)

# ------------------------------------------------------------------ helpers
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def load_rgb(p):
    a = cv2.imread(str(p), cv2.IMREAD_COLOR); assert a is not None, p; return cv2.cvtColor(a, cv2.COLOR_BGR2RGB)
def luma(a): return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
def poly_mask(shape, polys, W, H):
    """polys in plate FRACTIONS [[x,y],...] (resolution independent)."""
    m = np.zeros(shape, np.uint8)
    for p in polys or []: cv2.fillPoly(m, [np.int32(np.round(np.float64(p) * [W, H]))], 1)
    return m > 0
def disk(r): r = max(int(r), 1); return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
def guided(I, p, r, eps):
    """He et al. guided filter, gray guide I in [0,1], input p in [0,1]."""
    k = (2 * r + 1, 2 * r + 1); bf = lambda x: cv2.boxFilter(x, -1, k, borderType=cv2.BORDER_REFLECT)
    mI, mp = bf(I), bf(p); cIp = bf(I * p) - mI * mp; vI = bf(I * I) - mI * mI
    a = cIp / (vI + eps); b = mp - a * mI
    return bf(a) * I + bf(b)
def smooth_progress(n, ramp_in=0.5, ramp_out=0.5, v_end=0.35, fps=30):
    """Normalised position 0..1 for n frames from a C1 velocity profile: starts already moving at v_end x cruise,
    cosine-ramps to cruise in ramp_in s, cruises, cosine-ramps back to v_end in the last ramp_out s.
    Moving from frame 0 = the move reads within the first second after a hard cut; no stop/start pumping."""
    t = np.arange(n) / fps; T = (n - 1) / fps; v = np.ones(n)
    a = t < ramp_in; v[a] = v_end + (1 - v_end) * 0.5 * (1 - np.cos(np.pi * t[a] / ramp_in))
    b = t > T - ramp_out; v[b] = v_end + (1 - v_end) * 0.5 * (1 - np.cos(np.pi * (T - t[b]) / ramp_out))
    x = np.concatenate([[0], np.cumsum((v[1:] + v[:-1]) / 2)]); return x / x[-1]

# ------------------------------------------------------------------ depth model (optional)
def depth_map(plate_path, P):
    CACHE.mkdir(exist_ok=True); f = CACHE / f"da2s_{md5(plate_path)}.npy"
    if f.exists(): return np.load(f).astype(np.float32), dict(cached=True)
    import onnxruntime as ort
    sess = ort.InferenceSession(str(MODEL), providers=["CPUExecutionProvider"]); i = sess.get_inputs()[0]
    h, w = P.shape[:2]; s = 518 / min(h, w); W, H = int(round(w * s / 14)) * 14, int(round(h * s / 14)) * 14
    x = cv2.resize(P, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255
    x = ((x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]).transpose(2, 0, 1)[None].astype(np.float32)
    t0 = time.time(); d = np.squeeze(sess.run(None, {i.name: x})[0]); dt = time.time() - t0
    d = cv2.resize(d, (w, h), interpolation=cv2.INTER_CUBIC); d = (d - d.min()) / (d.max() - d.min() + 1e-9)
    np.save(f, d.astype(np.float16)); return d.astype(np.float32), dict(cached=False, infer_s=round(dt, 2), net_in=[W, H])

# ------------------------------------------------------------------ shot
class DepthShot:
    def __init__(self, cfg):
        self.cfg = cfg; self.P = load_rgb(cfg["plate"]); H, W = self.P.shape[:2]; self.H, self.W = H, W
        self.Pf = self.P.astype(np.float32) / 255; m = cfg.get("matte", {}); self.mode = m.get("mode", "hybrid")
        self.D = None; self.depth_info = None
        if self.mode in ("hybrid", "depth"): self.D, self.depth_info = depth_map(cfg["plate"], self.P)
        self.layers = cfg["layers"]; self._build_masks(); self._build_cards()

    # --- hard membership -------------------------------------------------------------------------------------
    def _build_masks(self):
        H, W = self.H, self.W; m = self.cfg.get("matte", {}); hard = []
        for k, L in enumerate(self.layers):
            if k == 0: hard.append(np.ones((H, W), bool)); continue
            if self.mode == "poly":
                M = poly_mask((H, W), L["polys"], W, H)
            else:
                M = self.D >= float(L.get("depth_min", 1.1))
                if "depth_max" in L: M &= self.D < float(L["depth_max"])
                if L.get("region"): M &= poly_mask((H, W), L["region"], W, H)        # hand: which blobs belong here
                if self.mode == "hybrid" and L.get("polys"): M |= poly_mask((H, W), L["polys"], W, H)
            if L.get("exclude"): M &= ~poly_mask((H, W), L["exclude"], W, H)
            M = M.astype(np.uint8)
            o = int(L.get("open_px", 2)); M = cv2.morphologyEx(M, cv2.MORPH_OPEN, disk(o)) if o else M
            c = int(L.get("close_px", 3)); M = cv2.morphologyEx(M, cv2.MORPH_CLOSE, disk(c)) if c else M
            n, lab, st, _ = cv2.connectedComponentsWithStats(M, 8); amin = float(L.get("min_area_frac", 0.002)) * H * W
            keep = np.zeros(n, bool); keep[1:] = st[1:, cv2.CC_STAT_AREA] >= amin; M = keep[lab]
            # fill enclosed holes (no see-through pockets inside a figure)
            inv = (~M).astype(np.uint8); n2, lab2, st2, _ = cv2.connectedComponentsWithStats(inv, 4)
            hmax = float(L.get("hole_fill_frac", 0.004)) * H * W
            for j in range(1, n2):
                x, y, w_, h_, a = st2[j]
                if a < hmax and x > 0 and y > 0 and x + w_ < W and y + h_ < H: M |= lab2 == j
            hard.append(M)
        for k in range(1, len(hard)):                    # exclusive: nearer wins
            for j in range(k + 1, len(hard)): hard[k] &= ~hard[j]
        self.hard = hard

    # --- cards: extended + filled colour, soft alpha, un-mixed edges --------------------------------------------
    def _fill(self, own_core, rng, grain=True):
        """Fill every pixel outside own_core from own_core pixels only (TELEA) + matched grain."""
        img = (self.Pf * 255).astype(np.uint8); mask = (~own_core).astype(np.uint8)
        F = cv2.inpaint(img, mask, int(self.cfg.get("matte", {}).get("inpaint_radius", 6)), cv2.INPAINT_TELEA).astype(np.float32) / 255
        if grain:   # TELEA is smooth; add the plate's own high-frequency level so a revealed strip is not a flat smear
            hp = self.Pf - cv2.GaussianBlur(self.Pf, (0, 0), 1.6); ring = cv2.dilate(mask, disk(12)).astype(bool) & own_core
            sd = float(hp[ring].std()) if ring.any() else 0.0
            n = cv2.GaussianBlur(rng.standard_normal((self.H, self.W)).astype(np.float32), (0, 0), 0.8)[..., None]
            n = n / (n.std() + 1e-6) * sd * 0.8; F = np.where(mask.astype(bool)[..., None], np.clip(F + n, 0, 1), F)
        return F

    def _build_cards(self):
        H, W = self.H, self.W; m = self.cfg.get("matte", {}); rng = np.random.default_rng(7)
        R = int(round(self.cfg.get("reveal_px", 0) or self.reveal_needed_px() + 6))
        g = luma(self.Pf).astype(np.float32); C = self.Pf; cards = []; comp = None
        for k, L in enumerate(self.layers):
            own = self.hard[k]; nearer = np.zeros((H, W), bool)
            for j in range(k + 1, len(self.hard)): nearer |= self.hard[j]
            core = cv2.erode(own.astype(np.uint8), disk(2)).astype(bool) if k else (~cv2.dilate(nearer.astype(np.uint8), disk(3)).astype(bool))
            Fr = self._fill(core, rng) if (nearer.any() or k) else C.copy()
            if k == 0:
                a = np.ones((H, W), np.float32); F = Fr.copy(); keep = ~cv2.dilate(nearer.astype(np.uint8), disk(3)).astype(bool)
                sm = np.zeros((H, W), bool)
                for LL in self.layers[1:]:
                    if LL.get("seams"): sm |= poly_mask((H, W), LL["seams"], W, H)
                keep |= sm; self.seam_all = sm; F[keep] = C[keep]; comp = F.copy(); cards.append(dict(name=L["name"], F=F, a=a, ext=np.ones((H, W), bool))); continue
            ext = own | (nearer & cv2.dilate(own.astype(np.uint8), disk(R)).astype(bool))
            seam = poly_mask((H, W), L.get("seams", []), W, H) if L.get("seams") else np.zeros((H, W), bool)
            if self.mode == "poly":
                fe = float(L.get("feather_px", 2.0)); a = cv2.GaussianBlur(ext.astype(np.float32), (0, 0), fe) if fe > 0 else ext.astype(np.float32)
            else:
                gr, ge = int(m.get("guided_r", 4)), float(m.get("guided_eps", 2e-3))
                a = guided(g, ext.astype(np.float32), gr, ge)
                band = cv2.dilate(ext.astype(np.uint8), disk(gr + 1)).astype(bool) & ~cv2.erode(ext.astype(np.uint8), disk(gr + 1)).astype(bool)
                a = np.where(band, a, ext.astype(np.float32))                      # guided only in the edge band
            if seam.any():   # continuous surface (ground/floor) cut: wide feather, plate colours both sides (no smear, no tear)
                aw = cv2.GaussianBlur(own.astype(np.float32), (0, 0), float(L.get("seam_feather_px", 18)))
                a = np.where(seam, aw, a)
            a = np.clip(a, 0, 1); a[a < 0.02] = 0; a[a > 0.98] = 1
            a[cv2.erode(own.astype(np.uint8), disk(3)).astype(bool) & ~seam] = 1  # solid interior (faces never translucent)
            # un-mix edge colours against the farther-layer composite (comp) -> no fringe carried by a moving edge
            F = Fr.copy(); A = a[..., None]
            un = np.clip((C - (1 - A) * comp) / np.maximum(A, 1e-3), 0, 1)
            w = np.clip((a - 0.15) / 0.35, 0, 1)[..., None]                       # trust un-mixing only where a >= 0.5
            edge = (~nearer)                                                       # own silhouette vs FARTHER layers
            F = np.where(edge[..., None], w * un + (1 - w) * Fr, Fr)
            F[own & (a >= 0.999)] = C[own & (a >= 0.999)]                          # interior = plate pixels, bit-exact
            F[seam] = C[seam]
            comp = comp * (1 - A) + F * A
            cards.append(dict(name=L["name"], F=F, a=a, ext=ext))
        self.cards = cards; self.recon = comp; self.R = R
        for c in cards: c["pm"] = np.dstack([c["F"] * c["a"][..., None], c["a"]]).astype(np.float32)   # premultiplied RGBA

    # --- camera -------------------------------------------------------------------------------------------------
    def out_frame(self, size):
        """Cover-fit window (plate px) and cover scale for this output size. Optional cfg['crop'] = window
        [x0,y0,x1,y1] in plate fractions per aspect key ('16x9' / '9x16'). Crop zoom is relative to full-plate cover-fit."""
        w, h = size; key = "16x9" if w > h else "9x16"; cr = self.cfg.get("crop", {}).get(key)
        W, H = self.W, self.H
        if cr: x0, y0, x1, y1 = cr[0] * W, cr[1] * H, cr[2] * W, cr[3] * H
        else: x0, y0, x1, y1 = 0, 0, W, H
        s = max(w / (x1 - x0), h / (y1 - y0)); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        crop_zoom = s / max(w / W, h / H)
        return s, (cx, cy), crop_zoom
    def cam(self): return self.cfg.get("camera", {})
    def layer_params(self, k, e):
        """zoom z_k and translation (fraction of output width/height) for layer k at progress e in [0,1]."""
        c = self.cam(); L = self.layers[k]; z0, z1 = c.get("push", [1.0, 1.0]); g = float(L.get("push_gain", 1.0))
        z = 1.0 + ((z0 - 1.0) + (z1 - z0) * e) * g
        w = float(L.get("parallax", 0.0)) - float(c.get("pivot", 0.0)); tr = float(c.get("travel", 0.0)); d = c.get("dir", [1.0, 0.0])
        tx = tr * (e - 0.5) * w * d[0]; ty = tr * (e - 0.5) * w * d[1]
        return z, tx, ty
    def reveal_needed_px(self):
        """Max relative displacement between any two layers anywhere on the plate, in PLATE px, over both formats."""
        ax, ay = self.anchor(); rmax = max(math.hypot(x - ax, y - ay) for x in (0, self.W) for y in (0, self.H)); best = 0.0
        for size in (self.size_for("9x16"), self.size_for("16x9")):
            s, _, _ = self.out_frame(size); w, h = size
            for e in (0.0, 1.0):
                P = [self.layer_params(k, e) for k in range(len(self.layers))]
                for a in P:
                    for b in P: best = max(best, abs(a[0] - b[0]) * rmax + math.hypot((a[1] - b[1]) * w, (a[2] - b[2]) * h) / s)
        return best
    def size_for(self, key): return (1080, 1920) if key == "9x16" else (1920, 1080)

    def _covers(self, k, e, size, o):
        w, h = size; M = self.layer_affine(k, e, size, o); S = M[0, 0]
        x0, x1 = (0 - M[0, 2]) / S, (w - M[0, 2]) / S; y0, y1 = (0 - M[1, 2]) / S, (h - M[1, 2]) / S
        return x0 >= -1e-6 and y0 >= -1e-6 and x1 <= self.W + 1e-6 and y1 <= self.H + 1e-6
    def overscan(self, size, n=181):
        """ONE constant overscan factor shared by all layers (keeps layers registered). Smallest o such that every
        card that is opaque at the plate border (always the far card) still covers the whole output at every frame."""
        E = smooth_progress(n, **self.cam().get("ease", {})); ks = []
        for k in range(len(self.layers)):
            a = self.cards[k]["a"]
            if k == 0 or a[0].max() > 0 or a[-1].max() > 0 or a[:, 0].max() > 0 or a[:, -1].max() > 0: ks.append(k)
        ok = lambda o: all(self._covers(k, e, size, o) for k in ks for e in E[::5].tolist() + [E[-1]])
        if ok(1.0): return 1.0
        lo, hi = 1.0, 1.6
        for _ in range(30):
            mid = (lo + hi) / 2; lo, hi = (lo, mid) if ok(mid) else (mid, hi)
        return hi
    def anchor(self):
        a = self.cam().get("anchor", [0.5, 0.5]); return a[0] * self.W, a[1] * self.H

    def layer_affine(self, k, e, size, o):
        """THE single camera transform of layer k: cover-fit x overscan x layer zoom about the anchor, + layer shift.
        Returns 2x3 uniform-scale+translate matrix plate px -> output px."""
        w, h = size; s, (cx, cy), _ = self.out_frame(size); z, tx, ty = self.layer_params(k, e); ax, ay = self.anchor()
        S = s * o * z; Aox, Aoy = w / 2 + (ax - cx) * s, h / 2 + (ay - cy) * s        # anchor's cover-fit output position
        return np.float32([[S, 0, Aox - S * ax + tx * w], [0, S, Aoy - S * ay + ty * h]])

    def guard(self, size, mode="refuse", n=181):
        o = self.overscan(size, n); _, _, cz = self.out_frame(size)
        zmax = max(self.layer_params(k, e)[0] for k in range(len(self.layers)) for e in (0.0, 1.0)) * o * cz
        if G is None: return [dict(check="crop_zoom", ok=zmax <= 1.5, zoom=zmax, note="guardrails.py did not import: " + G_ERR)]
        return [G.check_crop_zoom(zmax, mode=mode, plate_wh=(self.W, self.H), out_wh=size)]

    # --- frame ----------------------------------------------------------------------------------------------------
    def frame(self, e, size, o=None, fid=None, plate_fx=None, layer_fx=None, screen_fx=None, t=0.0, return_layers=False):
        """Composite at progress e. Exactly one _warp per layer. Effects:
          plate_fx(t)  -> plate-space RGB float [0,1] (a locked effect rendered with ITS camera disabled). Its delta vs the
                          plate is split across the layers by their exclusive coverage, so it rides each layer's single warp.
          layer_fx[name](t) -> plate-space premultiplied RGBA overlay (or None) added to that layer card before its warp.
          screen_fx(img, t) -> screen-space post (grain, grade, titles: NEVER a camera move)."""
        w, h = size; o = self.overscan(size) if o is None else o; out = None; lay = []
        delta = (plate_fx(t) - self.Pf) if plate_fx else None
        cover = 1.0
        if delta is not None:   # exclusive coverage weights at zero motion, near -> far
            wts = []
            for c in self.cards[::-1]: wts.append(c["a"] * cover); cover = cover * (1 - c["a"])
            wts = wts[::-1]
        for k, c in enumerate(self.cards):
            pm = c["pm"]
            if delta is not None or (layer_fx and c["name"] in layer_fx):
                pm = pm.copy()
                if delta is not None: pm[..., :3] += delta * wts[k][..., None]
                if layer_fx and c["name"] in layer_fx:
                    ov = layer_fx[c["name"]](t)
                    if ov is not None: pm = pm * (1 - ov[..., 3:4]) + ov
            M = self.layer_affine(k, e, size, o)
            Wk = _warp(pm, M, (w, h), (fid, c["name"]))
            a = np.clip(Wk[..., 3:4], 0, 1); rgb = np.clip(Wk[..., :3], 0, a)
            out = rgb if out is None else out * (1 - a) + rgb
            if return_layers: lay.append((M, a[..., 0]))
        if screen_fx: out = screen_fx(out, t)
        out = np.clip(out, 0, 1)
        return (out, lay) if return_layers else out

    def info(self):
        return dict(mode=self.mode, depth=self.depth_info, reveal_px=self.R,
                    layers=[dict(name=L["name"], own_frac=round(float(self.hard[k].mean()), 4)) for k, L in enumerate(self.layers)])

# ------------------------------------------------------------------ IO
def parse_size(s): w, h = map(int, s.lower().split("x")); return w, h
def ffmpeg_writer(path, w, h, fps, crf=25):
    cmd = ["ffmpeg", "-n", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
           "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(path)]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)
def _cfg(path): c = json.load(open(path)); c.setdefault("name", Path(path).stem); return c
def to8(x): return (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)

def render(cfg, out, size, seconds=None, crf=25, writer=None, fps=30, sh=None):
    sh = sh or DepthShot(cfg); n = int(round((seconds or cfg.get("seconds", 6.0)) * fps)); size = tuple(size)
    rep = sh.guard(size, n=n); o = sh.overscan(size, n); E = smooth_progress(n, fps=fps, **sh.cam().get("ease", {}))
    print("shot", cfg["name"], size, json.dumps(sh.info(), default=str), "overscan", round(o, 4), json.dumps(rep, default=str), file=sys.stderr, flush=True)
    p = writer or ffmpeg_writer(out, size[0], size[1], fps, crf)
    for i in range(n): p.stdin.write(to8(sh.frame(E[i], size, o, fid=i)).tobytes())
    if writer is None: p.stdin.close(); assert p.wait() == 0
    return sh

def reel(reel_json, out, fps=30):
    R = json.load(open(reel_json)); size = parse_size(R["size"]); shots = []
    for s in R["shots"]:
        cfg = _cfg(HERE / s["config"]); sh = DepthShot(cfg); sh.guard(size); shots.append((cfg, sh, s.get("seconds", 6.0)))
    p = ffmpeg_writer(out, size[0], size[1], fps, int(R.get("crf", 25)))
    for cfg, sh, sec in shots: render(cfg, out, size, seconds=sec, writer=p, fps=fps, sh=sh)
    p.stdin.close(); assert p.wait() == 0

# ------------------------------------------------------------------ proofs
def _sizes(cfg): return [parse_size(s) for s in cfg.get("formats", ["1080x1920"])]
def proof(cfg, out_json, fps=30):
    sh = DepthShot(cfg); r = dict(name=cfg["name"], plate=cfg["plate"], plate_md5=md5(cfg["plate"]), info=sh.info(), formats={})
    # (0) zero-motion reconstruction (plate -> cards -> composite at native res)
    err = np.abs(sh.recon - sh.Pf) * 255; mse = float((err ** 2).mean())
    r["recon_native"] = dict(psnr_db=round(10 * math.log10(255 ** 2 / max(mse, 1e-9)), 2), max_abs=round(float(err.max()), 2),
                             px_ge4=int((err.max(-1) >= 4).sum()), px_ge4_frac=round(float((err.max(-1) >= 4).mean()), 6))
    for size in _sizes(cfg):
        n = int(round(cfg.get("seconds", 6.0) * fps)); o = sh.overscan(size, n); E = smooth_progress(n, fps=fps, **sh.cam().get("ease", {}))
        R = dict(size=list(size), overscan=round(o, 5), guardrail=sh.guard(size, mode="warn", n=n))
        # (1) single transform: WARP_LOG must hold exactly one entry per layer per frame and nothing else
        WARP_LOG.clear(); ids = [0, n // 2, n - 1]
        frames = {i: sh.frame(E[i], size, o, fid=i, return_layers=True) for i in ids}
        cnt = {}
        for t in WARP_LOG: cnt[t] = cnt.get(t, 0) + 1
        R["single_transform"] = dict(warps_logged=len(WARP_LOG), expected=len(ids) * len(sh.cards),
                                     max_warps_per_layer_frame=max(cnt.values()), pass_=len(WARP_LOG) == len(ids) * len(sh.cards) and max(cnt.values()) == 1)
        # numeric: a dot at plate point X in layer k must land at M_k X (one affine). A stacked global push would move it.
        R["single_transform"]["dot_test"] = dot_test(sh, size, o, E[n - 1])
        # matrices are uniform scale + translate only
        Ms = [sh.layer_affine(k, E[i], size, o) for k in range(len(sh.cards)) for i in ids]
        R["single_transform"]["uniform_scale_no_shear_no_rot"] = bool(all(abs(M[0, 1]) < 1e-9 and abs(M[1, 0]) < 1e-9 and abs(M[0, 0] - M[1, 1]) < 1e-6 for M in Ms))
        # (2) disocclusion at max offset (both ends)
        R["disocclusion"] = [disocclusion(sh, size, o, e) for e in (E[0], E[-1])]
        # (3) rigidity of protected regions
        R["rigidity"] = rigidity(sh, size, o, E, ids)
        r["formats"][f"{size[0]}x{size[1]}"] = R
    ok = r["recon_native"]["psnr_db"] > 40
    for R in r["formats"].values():
        ok &= R["single_transform"]["pass_"] and R["single_transform"]["dot_test"]["pass_"] and R["single_transform"]["uniform_scale_no_shear_no_rot"]
        ok &= all(d["holes_px"] == 0 for d in R["disocclusion"]) and all(g.get("ok") and g.get("pixel_density", {}).get("pass", True) for g in R["guardrail"])
        ok &= all(p["pass_"] for p in R["rigidity"])
    r["pass"] = bool(ok)
    json.dump(r, open(out_json, "x"), indent=1, default=float); print(json.dumps(r, default=float)[:3000]); return r

def dot_test(sh, size, o, e):
    """Replace each card by a single opaque dot (in its own interior) and check where the composite puts it."""
    w, h = size; res = []; save = [c["pm"] for c in sh.cards]
    try:
        for k, c in enumerate(sh.cards):
            core = cv2.erode(sh.hard[k].astype(np.uint8), disk(25)).astype(bool) if k else np.ones((sh.H, sh.W), bool)
            ys, xs = np.nonzero(core)
            if not len(xs): continue
            M0 = sh.layer_affine(k, e, size, o); ox = M0[0, 0] * xs + M0[0, 2]; oy = M0[1, 1] * ys + M0[1, 2]
            d2 = (ox - 0.3 * w) ** 2 + (oy - 0.3 * h) ** 2   # off-centre so a stacked push would visibly move it
            ok = (ox > 40) & (ox < w - 40) & (oy > 40) & (oy < h - 40)
            if not ok.any(): continue
            j = int(np.argmin(np.where(ok, d2, np.inf))); X, Y = int(xs[j]), int(ys[j])
            for kk, cc in enumerate(sh.cards): cc["pm"] = np.zeros_like(save[kk])
            pm = np.zeros_like(save[k]); cv2.circle(pm, (X, Y), 6, (1, 1, 1, 1), -1); c["pm"] = cv2.GaussianBlur(pm, (0, 0), 1.5)
            img = luma(sh.frame(e, size, o, fid=("dot", k))); M = sh.layer_affine(k, e, size, o)
            px = M @ np.float64([X, Y, 1]); ws = img.sum(); cy, cx = (np.indices(img.shape) * img).reshape(2, -1).sum(1) / max(ws, 1e-9)
            # what a stacked global push (house 1.00->1.06 about the frame centre) would have produced:
            z = sh.cam().get("push", [1, 1])[1]; stacked = (np.float64([w / 2, h / 2]) + (px - [w / 2, h / 2]) * z)
            res.append(dict(layer=c["name"], plate_xy=[X, Y], expected=[round(px[0], 3), round(px[1], 3)], measured=[round(cx, 3), round(cy, 3)],
                            err_px=round(float(math.hypot(cx - px[0], cy - px[1])), 4),
                            err_if_double_push_px=round(float(math.hypot(cx - stacked[0], cy - stacked[1])), 2)))
    finally:
        for kk, cc in enumerate(sh.cards): cc["pm"] = save[kk]
    return dict(dots=res, pass_=all(d["err_px"] < 0.05 for d in res))

def disocclusion(sh, size, o, e):
    """Revealed px = output px where, at progress e, some layer k is visible through a spot that at the plate's own
    layering (zero relative motion: all layers on the subject layer's matrix) was covered by a nearer layer, i.e. the
    pre-filled extension / far fill is on screen. Holes = output px with total alpha < 0.999 (nothing drawn)."""
    w, h = size; img, lay = sh.frame(e, size, o, fid=("dis", e), return_layers=True)
    ref_k = int(sh.cfg.get("camera", {}).get("ref_layer", len(sh.cards) - 1))
    Mref = sh.layer_affine(ref_k, e, size, o)
    def wm(m, M): return cv2.warpAffine(m.astype(np.float32), M, (w, h), flags=cv2.INTER_LINEAR) > 0.5
    cover = np.zeros((h, w), np.float32); vis_fill = np.zeros((h, w), bool); vis_true = np.zeros((h, w), bool)
    for k in range(len(sh.cards) - 1, -1, -1):
        M, a = lay[k]
        nearer = np.zeros((sh.H, sh.W), bool)
        for j in range(k + 1, len(sh.cards)): nearer |= sh.hard[j]
        # (seam bands on the far card hold the TRUE plate under a wide blend, so they are not counted as fill)
        filled = wm(nearer & ~sh.seam_all, M) if k == 0 else wm(sh.cards[k]["ext"] & ~sh.hard[k], M)
        vis = (1 - cover) * a; vis_fill |= (vis > 0.5) & filled
        cover = cover + (1 - cover) * a
    holes = int((cover < 0.999).sum())
    # fill quality: high-frequency energy in revealed px vs a ring of true pixels right next to them (smear => ratio << 1)
    g = luma(img); hp = np.abs(g - cv2.GaussianBlur(g, (0, 0), 1.5))
    ring = cv2.dilate(vis_fill.astype(np.uint8), disk(6)).astype(bool) & ~vis_fill
    rev_w = 0.0
    if vis_fill.any():   # typical revealed strip width = area / (perimeter/2)
        cs, _ = cv2.findContours(vis_fill.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); per = sum(cv2.arcLength(c, True) for c in cs)
        rev_w = 2 * vis_fill.sum() / max(per, 1)
    return dict(e=round(float(e), 4), revealed_px=int(vis_fill.sum()), revealed_frac=round(float(vis_fill.mean()), 5),
                revealed_strip_mean_width_px=round(rev_w, 2), holes_px=holes,
                hf_revealed=round(float(hp[vis_fill].mean()) * 255, 3) if vis_fill.any() else None,
                hf_ring=round(float(hp[ring].mean()) * 255, 3) if ring.any() else None,
                hf_ratio=round(float(hp[vis_fill].mean() / max(hp[ring].mean(), 1e-9)), 3) if vis_fill.any() else None)

def rigidity(sh, size, o, E, ids):
    """Each protect poly (face / hand / figure / text) must (a) sit fully inside ONE layer's solid interior (alpha = 1
    on the eroded region at native res), and (b) in the composite equal the ORIGINAL plate resampled by that layer's
    single matrix (MAE / max / NCC on the warped region eroded 2 px). That is 'moves only rigidly, never warped'."""
    w, h = size; out = []
    for k, L in enumerate(sh.layers):
        for pr in L.get("protect", []):
            m0 = poly_mask((sh.H, sh.W), [pr["poly"]], sh.W, sh.H); m = m0 & sh.hard[k]; me = cv2.erode(m.astype(np.uint8), disk(4)).astype(bool)   # interior (silhouette AA edge excluded)
            a_min = float(sh.cards[k]["a"][me].min()) if me.any() else 0.0
            nearer = np.zeros((sh.H, sh.W), bool)
            for j in range(k + 1, len(sh.hard)): nearer |= sh.hard[j]
            occl = float((nearer & m).mean() / max(m.mean(), 1e-9))
            res = dict(layer=L["name"], name=pr["name"], area_px=int(m0.sum()), in_layer_frac=round(float(m.sum() / max(m0.sum(), 1)), 4), alpha_min_native=round(a_min, 4), occluded_frac=round(occl, 4), frames=[])
            for i in ids:
                img = sh.frame(E[i], size, o, fid=("rig", i)); M = sh.layer_affine(k, E[i], size, o)
                ref = cv2.warpAffine(sh.Pf, M, (w, h), flags=INTERP, borderMode=cv2.BORDER_REPLICATE)
                mm = cv2.erode((cv2.warpAffine(me.astype(np.float32), M, (w, h), flags=cv2.INTER_LINEAR) > 0.99).astype(np.uint8), disk(2)).astype(bool)
                if mm.sum() < 50: res["frames"].append(dict(frame=int(i), in_view=False)); continue
                d = np.abs(img - ref)[mm] * 255; A = luma(img)[mm]; B = luma(np.clip(ref, 0, 1))[mm]
                ncc = float(((A - A.mean()) * (B - B.mean())).mean() / (A.std() * B.std() + 1e-9))
                res["frames"].append(dict(frame=int(i), mae=round(float(d.mean()), 4), max=round(float(d.max()), 3), ncc=round(ncc, 6), px=int(mm.sum())))
            res["pass_"] = a_min >= 0.999 and res["in_layer_frac"] >= float(pr.get("min_in_layer", 0.97)) and all(f["mae"] < 0.5 and f["ncc"] > 0.999 for f in res["frames"] if f.get("in_view", True))
            out.append(res)
    return out

def series_stats(v, fps=30, win=1.0, step=0.5):
    v = np.asarray(v, np.float64); n = int(win * fps); sw = []
    for i in range(0, len(v) - n + 1, int(step * fps)): ww = v[i:i + n]; sw.append((ww.max() - ww.min()) / max(ww.mean(), 1e-6))
    st = np.abs(np.diff(v)) / max(v.mean(), 1e-6); x = v - v.mean(); Pw = np.abs(np.fft.rfft(x)) ** 2; f = np.fft.rfftfreq(len(x), 1 / fps)
    return dict(swing_1s_median_pct=round(100 * float(np.median(sw)), 3), swing_1s_max_pct=round(100 * float(np.max(sw)), 3),
                max_step_pct=round(100 * float(st.max()), 4), energy_above_5hz=round(float(Pw[f > 5].sum() / max(Pw[1:].sum(), 1e-12)), 4))

def stats(cfg, out_json, fps=30):
    """Phone read at 360x640 (9:16) / 640x360 (16:9): full-res frames area-downscaled to phone size.
    whole_frame: mean-luma series (pumping / flicker). Motion: per-layer measured trajectory (phase correlation of the
    phone frame vs frame 0 inside each layer's solid region) -> jitter = RMS of the 2nd difference after removing a
    smooth fit, energy of the velocity above 5 Hz, phone px travelled in the first 1 s and in the whole shot."""
    sh = DepthShot(cfg); r = dict(name=cfg["name"], formats={})
    for size in _sizes(cfg):
        n = int(round(cfg.get("seconds", 6.0) * fps)); o = sh.overscan(size, n); E = smooth_progress(n, fps=fps, **sh.cam().get("ease", {}))
        ph = (360, 640) if size[1] > size[0] else (640, 360)
        fr = [luma(cv2.resize(sh.frame(E[i], size, o, fid=i), ph, interpolation=cv2.INTER_AREA)) * 255 for i in range(n)]
        R = dict(size=list(size), phone=list(ph), whole_frame=series_stats([f.mean() for f in fr], fps), layers={})
        # analytic phone-px trajectory of each layer's solid-region centroid
        for k in range(len(sh.cards)):
            core = sh.hard[k] if k else ~cv2.dilate(np.any(sh.hard[1:], 0).astype(np.uint8), disk(5)).astype(bool)
            ys, xs = np.nonzero(core); X, Y = xs.mean(), ys.mean()
            tr = np.array([sh.layer_affine(k, E[i], size, o) @ [X, Y, 1] for i in range(n)]) * (ph[0] / size[0])
            # measured: phase correlation on a window around the region in phone frames
            m = cv2.resize(core.astype(np.uint8) * 255, (sh.W, sh.H)); 
            M0 = sh.layer_affine(k, E[0], size, o); mw = cv2.warpAffine(core.astype(np.float32), M0, size, flags=cv2.INTER_LINEAR)
            mw = cv2.resize(mw, ph, interpolation=cv2.INTER_AREA) > 0.95; mw = cv2.erode(mw.astype(np.uint8), disk(3)).astype(np.float32)
            win = cv2.createHanningWindow(ph, cv2.CV_32F) * mw
            meas = [(0.0, 0.0)]
            for i in range(1, n):
                (dx, dy), _ = cv2.phaseCorrelate(fr[i - 1].astype(np.float32) * mw, fr[i].astype(np.float32) * mw, win); meas.append((dx, dy))
            v = np.array(meas)[1:]; pos = np.cumsum(v, 0)
            sp = np.hypot(*np.diff(tr, axis=0).T)
            vel = np.hypot(*v.T); x = vel - vel.mean(); Pw = np.abs(np.fft.rfft(x)) ** 2; f = np.fft.rfftfreq(len(x), 1 / fps)
            res = pos - np.array([np.polyval(np.polyfit(np.arange(len(pos)), pos[:, j], 5), np.arange(len(pos))) for j in (0, 1)]).T
            R["layers"][sh.cards[k]["name"]] = dict(
                travel_phone_px=round(float(np.hypot(*(tr[-1] - tr[0]))), 2), travel_first_1s_phone_px=round(float(np.hypot(*(tr[fps] - tr[0]))), 2),
                speed_phone_px_s_max=round(float(sp.max() * fps), 2), measured_travel_px=round(float(np.hypot(*pos[-1])), 2),
                jitter_rms_px=round(float(np.sqrt((res ** 2).sum(1).mean())), 4), vel_energy_above_5hz=round(float(Pw[f > 5].sum() / max(Pw[1:].sum(), 1e-12)), 4))
        # relative parallax: one plate point (nearest layer's centroid) carried by the nearest vs the farthest card
        ys, xs = np.nonzero(sh.hard[-1]); Pn = np.float64([xs.mean(), ys.mean(), 1]); kN = len(sh.cards) - 1; sc = ph[0] / size[0]
        rel = np.array([(sh.layer_affine(kN, E[i], size, o) - sh.layer_affine(0, E[i], size, o)) @ Pn for i in range(n)]) * sc
        R["relative_parallax_phone_px"] = round(float(np.hypot(*(rel[-1] - rel[0]))), 2)
        R["relative_parallax_first_1s_phone_px"] = round(float(np.hypot(*(rel[fps] - rel[0]))), 2)
        R["relative_parallax_pct_of_width"] = round(float(np.hypot(*(rel[-1] - rel[0]))) / ph[0] * 100, 2)
        r["formats"][f"{size[0]}x{size[1]}"] = R
    json.dump(r, open(out_json, "x"), indent=1); print(json.dumps(r)[:3000]); return r

# ------------------------------------------------------------------ inspection sheets
def layers_sheet(cfg, out_png):
    sh = DepthShot(cfg); H = 640; s = H / sh.H; rs = lambda x: cv2.resize(x, (int(sh.W * s), H), interpolation=cv2.INTER_AREA)
    tiles = [rs(sh.P)]
    if sh.D is not None: tiles.append(cv2.cvtColor(cv2.applyColorMap(rs((sh.D * 255).astype(np.uint8)), cv2.COLORMAP_TURBO), cv2.COLOR_BGR2RGB))
    cols = [(255, 80, 80), (80, 255, 80), (80, 160, 255), (255, 255, 0)]
    ov = sh.Pf.copy() * 0.45
    for k in range(1, len(sh.cards)): ov = ov * (1 - 0.5 * sh.cards[k]["a"][..., None]) + 0.5 * sh.cards[k]["a"][..., None] * np.float32(cols[k]) / 255
    tiles.append(rs(to8(ov)))
    for k in range(1, len(sh.cards)): tiles.append(rs(to8(sh.cards[k]["F"] * sh.cards[k]["a"][..., None] + (1 - sh.cards[k]["a"][..., None]) * [0, 1, 0])))
    tiles.append(rs(to8(sh.cards[0]["F"])))
    cv2.imwrite(out_png, cv2.cvtColor(np.hstack(tiles), cv2.COLOR_RGB2BGR))

def maxgrab(cfg, out_png, size=None):
    sh = DepthShot(cfg); size = size or _sizes(cfg)[0]; n = int(round(cfg.get("seconds", 6.0) * 30)); o = sh.overscan(size, n)
    rows = []
    for e in (0.0, 1.0):
        img = sh.frame(e, size, o); d = disocclusion(sh, size, o, e)
        # recompute revealed mask for display
        w, h = size; lay = sh.frame(e, size, o, return_layers=True)[1]; cover = np.zeros((h, w), np.float32); vf = np.zeros((h, w), bool)
        for k in range(len(sh.cards) - 1, -1, -1):
            M, a = lay[k]; nearer = np.zeros((sh.H, sh.W), bool)
            for j in range(k + 1, len(sh.cards)): nearer |= sh.hard[j]
            fl = (sh.cards[k]["ext"] & ~sh.hard[k]) if k else (nearer & ~sh.seam_all)
            fl = cv2.warpAffine(fl.astype(np.float32), M, (w, h)) > 0.5; vf |= ((1 - cover) * a > 0.5) & fl; cover = cover + (1 - cover) * a
        mag = img.copy(); mag[vf] = mag[vf] * 0.3 + np.float32([1, 0, 1]) * 0.7
        ys, xs = np.nonzero(vf)
        if len(xs):
            j = len(xs) // 2; cx, cy = xs[j], ys[j]; x0 = int(np.clip(cx - 90, 0, w - 180)); y0 = int(np.clip(cy - 90, 0, h - 180))
            crop = cv2.resize(img[y0:y0 + 180, x0:x0 + 180], (h // 2, h // 2), interpolation=cv2.INTER_NEAREST)
            crop2 = cv2.resize(mag[y0:y0 + 180, x0:x0 + 180], (h // 2, h // 2), interpolation=cv2.INTER_NEAREST)
            side = np.vstack([crop, crop2])[:h]
        else: side = np.zeros((h, h // 2, 3), np.float32)
        side = np.pad(side, ((0, h - side.shape[0]), (0, 0), (0, 0)))
        rows.append(np.hstack([img, mag, side]))
    cv2.imwrite(out_png, cv2.cvtColor(to8(np.vstack(rows)), cv2.COLOR_RGB2BGR))

if __name__ == "__main__":
    a = sys.argv[1:]; cmd = a[0]
    def opt(k, d=None): return a[a.index(k) + 1] if k in a else d
    out = a[2]; assert not Path(out).exists(), "never overwrite: " + out
    if cmd == "reel": reel(a[1], out)
    else:
        cfg = _cfg(a[1])
        if cmd == "render": render(cfg, out, parse_size(opt("--size", "540x960")), seconds=float(opt("--seconds", cfg.get("seconds", 6))), crf=int(opt("--crf", 25)))
        elif cmd == "proof": proof(cfg, out)
        elif cmd == "stats": stats(cfg, out)
        elif cmd == "layers": layers_sheet(cfg, out)
        elif cmd == "maxgrab": maxgrab(cfg, out, parse_size(opt("--size")) if opt("--size") else None)
