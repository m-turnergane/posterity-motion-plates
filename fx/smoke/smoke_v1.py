"""smoke_v1 -- procedural smoke overlay for still painted plates (Posterity engine R&D).

The plate NEVER moves.  Smoke is a semi-transparent layer composited on top:
  * density = multi-octave periodic noise, advected upward and domain-warped by a slowly
    evolving curl (swirl) field, so shapes billow and morph instead of rigidly scrolling;
  * each emitter has its own plume envelope: narrow at the source, widening and thinning as it
    rises, with a wandering centre line;
  * distant columns can be stacked in 2-3 depth layers at different speeds / scales;
  * fire glow lights the smoke from below on a smooth flicker clock;
  * nothing loops: textures are much taller than the distance scrolled in a shot, and the octaves
    scroll at incommensurate speeds;
  * everything eases in (no pop-in).
Pixels outside each emitter's footprint (and inside `protect` polygons) are bit-exact copies of
the plate; `zero_motion_report()` proves it.

Dependencies: numpy, opencv-python, ffmpeg (on PATH).  No other project code is imported.

CLI:
  python smoke_v1.py --plate PLATE.png --config CFG.json --out OUT.mp4 [--seconds 8] [--preview 360]
"""
import argparse, json, math, subprocess, sys
from pathlib import Path
import numpy as np
import cv2

# ----------------------------------------------------------------------------------------- noise helpers
def periodic_noise(rng, h, w, lo, hi, beta=2.2, ax=1.0, ay=1.0):
    """Seamless fractal noise (h, w), zero mean / unit std. lo = largest feature px, hi = smallest."""
    fy = np.fft.fftfreq(h)[:, None] * ay
    fx = np.fft.rfftfreq(w)[None, :] * ax
    f = np.sqrt(fx * fx + fy * fy)
    amp = (f * f + (1.0 / lo) ** 2) ** (-beta / 4) * np.exp(-(f * hi) ** 2)
    spec = (rng.standard_normal((h, w // 2 + 1)) + 1j * rng.standard_normal((h, w // 2 + 1))) * amp
    n = np.fft.irfft2(spec, s=(h, w)).astype(np.float32)
    n -= n.mean()
    return n / (n.std() + 1e-8)


def smoothstep(a, b, x):
    x = np.clip((x - a) / (b - a + 1e-9), 0, 1)
    return x * x * (3 - 2 * x)


def ease(t, t0, t1):
    return float(smoothstep(t0, t1, np.float32(t)))


class Flicker:
    """Smooth, non-repeating fire flicker f(t) ~ 1 +/- amp (sum of cubic-interpolated random walks)."""
    def __init__(self, rng, amp=0.18, rates=(1.3, 3.7, 8.9)):
        self.amp, self.rates = amp, rates
        self.tab = [rng.standard_normal(8192).astype(np.float32) for _ in rates]
        self.w = np.float32([0.55, 0.30, 0.15])

    def __call__(self, t):
        v = 0.0
        for tab, r, w in zip(self.tab, self.rates, self.w):
            i = t * r; j = int(i) % 8190; fr = i - int(i); fr = fr * fr * (3 - 2 * fr)
            v += w * (tab[j] * (1 - fr) + tab[j + 1] * fr)
        return 1.0 + self.amp * v


def poly_mask(shape, polys, feather=0.0):
    m = np.zeros(shape, np.float32)
    for p in polys or []:
        cv2.fillPoly(m, [np.int32(np.round(np.float32(p)))], 1.0)
    if feather > 0 and m.any():
        m = cv2.GaussianBlur(m, (0, 0), feather)
    return m


# ----------------------------------------------------------------------------------------- emitter presets
PRESETS = {
    # thin wick smoke from a snuffed candle: tall, narrow, curly, pale
    "candle": dict(height=260, w0=2.0, w1=34.0, lean=0.0, rise=34.0, opacity=0.62, lo=46, hi=3.0,
                   swirl=9.0, meander=0.55, thin=1.8, color_dark=[150, 146, 142], color_light=[205, 200, 194],
                   layers=1, detail=0.62, glow=None),
    # torch smoke: denser, warmer near the source, lit by the torch
    "torch": dict(height=360, w0=8.0, w1=90.0, lean=0.0, rise=46.0, opacity=0.6, lo=70, hi=2.0,
                  swirl=14.0, meander=0.35, thin=1.2, color_dark=[60, 54, 52], color_light=[130, 122, 118],
                  layers=1, detail=0.55, glow=dict(color=[255, 150, 70], strength=0.55, reach=0.35, flicker=0.2)),
    # big burning-city column: thick dark smoke, 2-3 depth layers
    "column": dict(height=700, w0=40.0, w1=260.0, lean=0.0, rise=30.0, opacity=0.86, lo=150, hi=5.0,
                   swirl=22.0, meander=0.22, thin=0.8, color_dark=[30, 24, 24], color_light=[78, 68, 68],
                   layers=2, detail=0.35, glow=dict(color=[255, 120, 50], strength=0.5, reach=0.14, flicker=0.22)),
    # low ground haze: horizontal band drifting sideways
    "haze": dict(rect=None, drift=10.0, opacity=0.35, lo=220, hi=6.0, swirl=18.0, feather=40.0,
                 color_dark=[150, 140, 135], color_light=[190, 180, 172], glow=None),
}


class Emitter:
    """One smoke source in plate pixel space.  Precomputes its footprint, textures and envelopes."""

    TEX_H, TEX_W = 2048, 512   # tall periodic textures: rise*duration << TEX_H so nothing repeats in a shot

    def __init__(self, spec, plate_shape, protect, rng, layer_index=0):
        self.kind = spec.get("type", "candle")
        q = {**PRESETS[self.kind], **spec}
        self.q = q
        H, W = plate_shape
        self.layer_index = layer_index
        if self.kind == "haze":
            self._init_haze(q, H, W, protect, rng)
        else:
            self._init_plume(q, H, W, protect, rng)
        self.flick = Flicker(rng, (q.get("glow") or {}).get("flicker", 0.2))

    # ---- plume geometry
    def _init_plume(self, q, H, W, protect, rng):
        sx, sy = map(float, q["src"]); h = float(q["height"])
        pad = q["w1"] * 1.4 + abs(q["lean"]) + q["meander"] * q["w1"] + q["swirl"] * 2
        x0, x1 = int(max(0, sx - pad)), int(min(W, sx + pad + 1))
        y0, y1 = int(max(0, sy - h * 1.05)), int(min(H, sy + q["w0"] * 2 + 6))
        self.bb = (x0, y0, x1, y1)
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        self.s = ((sy - yy) / h).astype(np.float32)                         # 0 at source, 1 at top
        self.xx = xx
        self.sx, self.sy, self.h = sx, sy, h
        s = np.clip(self.s, 0, 1.2)
        self.width = (q["w0"] + (q["w1"] - q["w0"]) * s ** 0.85).astype(np.float32)
        # vertical envelope: ease in just above the source, thin out and fade toward the top
        self.venv = (smoothstep(-0.01, 0.06, self.s) * (1 - smoothstep(0.55, 1.0, self.s)) *
                     (1 - 0.55 * s) ** q["thin"]).astype(np.float32)
        clip = 1 - protect[y0:y1, x0:x1]
        self.clip = clip.astype(np.float32)
        th, tw = self.TEX_H, self.TEX_W
        lo, hi = q["lo"], q["hi"]
        self.T1 = periodic_noise(rng, th, tw, lo, hi * 2, ay=1.5)           # big billows
        self.T2 = periodic_noise(rng, th, tw, lo * 0.4, hi, ay=1.2)        # curly detail
        psi = periodic_noise(rng, 1024, 512, lo * 0.9, lo * 0.15)          # stream function -> curl flow
        self.cu = cv2.Sobel(psi, cv2.CV_32F, 0, 1, ksize=5)
        self.cv = -cv2.Sobel(psi, cv2.CV_32F, 1, 0, ksize=5)
        sc = 1.0 / (np.abs(self.cu).std() + np.abs(self.cv).std() + 1e-6)
        self.cu *= sc; self.cv *= sc
        self.mtab = rng.standard_normal(4096).astype(np.float32)          # centre-line meander
        self.ph = float(rng.uniform(0, 400))

    def _init_haze(self, q, H, W, protect, rng):
        x0, y0, x1, y1 = q["rect"]
        f = q["feather"]
        X0, Y0, X1, Y1 = int(max(0, x0 - 2 * f)), int(max(0, y0 - 2 * f)), int(min(W, x1 + 2 * f)), int(min(H, y1 + 2 * f))
        self.bb = (X0, Y0, X1, Y1)
        m = np.zeros((Y1 - Y0, X1 - X0), np.float32); m[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] = 1
        m = cv2.GaussianBlur(m, (0, 0), f)
        self.env = m * (1 - protect[Y0:Y1, X0:X1])
        lo, hi = q["lo"], q["hi"]
        self.T1 = periodic_noise(rng, 1024, 2048, lo, hi * 2, ax=0.45)
        self.T2 = periodic_noise(rng, 1024, 2048, lo * 0.45, hi, ax=0.6)
        self.ph = float(rng.uniform(0, 500))
        self.s = None

    def _meander(self, s, t):
        """smooth wandering offset of the centre line in px, travelling upward with the smoke."""
        q = self.q
        i = (s * 3.0 - t * q["rise"] / self.h * 3.0) * 1.0 + self.ph
        i = np.mod(i, 4090.0); j = i.astype(np.int32); fr = i - j; fr = fr * fr * (3 - 2 * fr)
        n = self.mtab[j] * (1 - fr) + self.mtab[j + 1] * fr
        return q["meander"] * q["w1"] * np.clip(s, 0, None) ** 1.2 * n

    # ---- density & colour
    def render(self, t, plate_roi):
        """return (alpha (h,w), colour (h,w,3)) for this emitter's bounding box at time t (seconds)."""
        if self.kind == "haze":
            return self._render_haze(t)
        q = self.q
        s = self.s
        sc = np.clip(s, 0, 1.2)
        cx = self.sx + q["lean"] * sc ** 1.5 + self._meander(s[:, :1], t)      # per row
        across = (self.xx - cx) / self.width                                  # -1..1 inside plume
        # texture coords: u expands with plume width (features grow as they rise), v advected upward
        u = across * q["w1"] * 0.5 + 256.0
        dist = s * self.h                                                     # px above the source
        rise = q["rise"]
        # curl swirl, itself drifting upward slower than the smoke -> eddies roll through the plume
        cu_v = np.mod(dist * 0.5 + 0.0 - rise * 0.45 * t * 0.5 + self.ph, 1024).astype(np.float32)
        cu_u = np.mod(u * 0.5, 512).astype(np.float32)
        wu = cv2.remap(self.cu, cu_u, -cu_v % 1024, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        wv = cv2.remap(self.cv, cu_u, -cu_v % 1024, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        sw = q["swirl"] * (0.35 + 0.65 * np.clip(sc, 0, 1))
        uu = np.mod(u + wu * sw, self.TEX_W).astype(np.float32)
        v1 = np.mod(-(dist - rise * t) + wv * sw + self.ph, self.TEX_H).astype(np.float32)
        v2 = np.mod(-(dist * 1.07 - rise * 1.38 * t) + wv * sw * 1.4 + self.ph * 1.7, self.TEX_H).astype(np.float32)
        T1 = cv2.remap(self.T1, uu, v1, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        T2 = cv2.remap(self.T2, np.mod(uu * 1.3, self.TEX_W).astype(np.float32), v2, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        N = 0.7 * T1 + q["detail"] * T2
        # cross-section: soft core, the noise eats the edges -> billowy silhouette instead of a gaussian tube
        core = np.exp(-2.2 * across * across)
        D = smoothstep(0.1, 0.85, core * 1.05 + 0.4 * N * np.sqrt(core) - 0.2) * self.venv
        D *= smoothstep(0.02, 0.35, core)                                    # nothing outside the plume body
        a = np.clip(D * q["opacity"], 0, 0.97) * self.clip
        # colour: dark near the source -> lighter, cooler as it thins; self-shade with the noise
        mix = np.clip(sc * 1.1, 0, 1)[..., None]
        col = np.float32(q["color_dark"]) * (1 - mix) + np.float32(q["color_light"]) * mix
        # billow relief: emboss the density noise so puffs read as rounded volumes (lit from above-left)
        Nb = cv2.GaussianBlur(N, (0, 0), max(1.0, q["lo"] * 0.05))
        rel = cv2.Sobel(Nb, cv2.CV_32F, 1, 0, ksize=3) * 0.4 + cv2.Sobel(Nb, cv2.CV_32F, 0, 1, ksize=3)
        rel = np.tanh(rel / (np.abs(rel).mean() * 2.5 + 1e-6))
        col = col * (1 + 0.14 * np.clip(N, -2, 2) - q.get("relief", 0.22) * rel)[..., None]
        g = q.get("glow")
        if g:
            f = self.flick(t)
            lit = np.exp(-np.clip(s, 0, None) / g["reach"]) * g["strength"] * f * (0.6 + 0.4 * core)
            col = col + (np.float32(g["color"]) - col * 0.4) * np.clip(lit, 0, 1)[..., None]
        return a.astype(np.float32), col.astype(np.float32)

    def _render_haze(self, t):
        q = self.q; X0, Y0, X1, Y1 = self.bb; h, w = Y1 - Y0, X1 - X0
        d = q["drift"]
        M1 = np.float32([[1, 0, self.ph + d * t], [0, 1, 0.0]])
        M2 = np.float32([[1, 0, self.ph * 0.7 + d * 1.6 * t], [0, 1, 3.0 * t]])
        T1 = cv2.warpAffine(self.T1, M1, (w, h), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_WRAP)
        T2 = cv2.warpAffine(self.T2, M2, (w, h), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_WRAP)
        N = 0.65 * T1 + 0.45 * T2
        a = np.clip(smoothstep(-0.9, 1.4, N) * self.env * q["opacity"], 0, 0.9)
        col = np.broadcast_to(np.float32(q["color_light"]), (h, w, 3)).copy()
        return a.astype(np.float32), col


def _expand_layers(spec):
    """distant columns: one spec -> 1..3 depth layers (back layers bigger, slower, fainter, offset)."""
    n = int(spec.get("layers", PRESETS[spec.get("type", "candle")].get("layers", 1)))
    if spec.get("type") == "haze" or n <= 1:
        return [spec]
    out = []
    base = {**PRESETS[spec["type"]], **spec}
    for k in range(n):
        f = [1.0, 0.62, 0.42][k]
        L = dict(base)
        L.update(layers=1, rise=base["rise"] * f, opacity=base["opacity"] * [1.0, 0.55, 0.38][k],
                 w1=base["w1"] * [1.0, 1.25, 1.5][k], height=base["height"] * [1.0, 1.08, 1.15][k],
                 lean=base["lean"] * [1.0, 1.3, 1.6][k], lo=base["lo"] * [1.0, 1.35, 1.7][k],
                 seed=int(spec.get("seed", 0)) * 7 + k)
        out.append(L)
    return out[::-1]   # draw back layers first


# ----------------------------------------------------------------------------------------- scene
class SmokeScene:
    """All emitters of one plate.  `frame(t)` returns the plate with smoke composited (uint8 RGB, plate size)."""

    def __init__(self, plate_rgb, config):
        self.P = plate_rgb
        self.Pf = plate_rgb.astype(np.float32)
        H, W = plate_rgb.shape[:2]
        self.cfg = config
        self.protect = np.clip(poly_mask((H, W), config.get("protect"), 0), 0, 1)
        # feather the protect edge INWARD into the smoke side only: smoke fades out before the protected shape
        if self.protect.any():
            grown = cv2.dilate(self.protect, np.ones((9, 9), np.uint8))
            self.protect = np.maximum(self.protect, cv2.GaussianBlur(grown, (0, 0), 4))
        self.ease_in = float(config.get("ease_in", 0.7))
        seed = int(config.get("seed", 0))
        self.emitters = []
        for i, spec in enumerate(config["emitters"]):
            for L in _expand_layers(spec):
                rng = np.random.default_rng(seed * 1000 + i * 37 + int(L.get("seed", 0)))
                self.emitters.append(Emitter(L, (H, W), self.protect, rng))

    def frame(self, t):
        img = self.Pf.copy()
        k = ease(t, 0.0, self.ease_in) if self.ease_in > 0 else 1.0
        for e in self.emitters:
            x0, y0, x1, y1 = e.bb
            roi = img[y0:y1, x0:x1]
            a, col = e.render(t, roi)
            a = (a * k)[..., None]
            roi[...] = roi * (1 - a) + col * a
        return np.clip(np.rint(img), 0, 255).astype(np.uint8)

    def allow_mask(self):
        """True where smoke may touch pixels (union of emitter footprints minus protect)."""
        H, W = self.P.shape[:2]; m = np.zeros((H, W), bool)
        for e in self.emitters:
            x0, y0, x1, y1 = e.bb; m[y0:y1, x0:x1] = True
        return m & (self.protect < 0.999)


# ----------------------------------------------------------------------------------------- camera + IO
def push_frame(img, u, out_w, out_h, z0=1.0, z1=1.06):
    """StablePush: centre scale from z0 to z1 over u in [0,1] (smoothstep), cover-fit to out_w x out_h."""
    H, W = img.shape[:2]
    e = u * u * (3 - 2 * u)
    z = z0 + (z1 - z0) * e
    s = max(out_w / W, out_h / H) * z
    M = np.float32([[s, 0, out_w / 2 - s * W / 2], [0, s, out_h / 2 - s * H / 2]])
    return cv2.warpAffine(img, M, (out_w, out_h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def ffmpeg_writer(path, w, h, fps, crf=17):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps),
           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(path)]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def load_plate(path):
    a = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if a is None:
        raise FileNotFoundError(path)
    return cv2.cvtColor(a, cv2.COLOR_BGR2RGB)


def zero_motion_report(scene, times):
    """Diff rendered frames against the still plate.  Returns dict with max abs diff outside the allow mask
    (must be 0) and the count of changed pixels outside it."""
    allow = scene.allow_mask()
    worst, changed = 0, 0
    for t in times:
        f = scene.frame(t)
        d = np.abs(f.astype(np.int16) - scene.P.astype(np.int16)).max(-1)
        worst = max(worst, int(d[~allow].max())); changed += int((d[~allow] > 0).sum())
    return dict(frames=len(times), max_diff_outside=worst, changed_px_outside=changed,
                allow_fraction=float(allow.mean()))


def render(plate_path, config, out_path, seconds=8.0, fps=30, size=(1080, 1920), push=(1.0, 1.06)):
    scene = SmokeScene(load_plate(plate_path), config)
    n = int(round(seconds * fps)); w, h = size
    p = ffmpeg_writer(out_path, w, h, fps)
    for i in range(n):
        t = i / fps
        p.stdin.write(push_frame(scene.frame(t), i / max(n - 1, 1), w, h, *push).tobytes())
    p.stdin.close(); p.wait()
    return scene


def main(argv=None):
    ap = argparse.ArgumentParser(description="Composite procedural smoke over a still plate (plate never moves).")
    ap.add_argument("--plate", default=None, help="plate image (defaults to the config's \"plate\" field)"); ap.add_argument("--config", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--seconds", type=float, default=8.0); ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--preview", type=int, default=0, help="output width for a quick low-res preview (e.g. 360)")
    ap.add_argument("--no-push", action="store_true"); ap.add_argument("--proof", action="store_true",
                    help="also print the zero-motion report (frame diff vs still outside the smoke footprint)")
    ap.add_argument("--grab", default=None, help="also save a 360x640 PNG frame grab at --grab-t seconds")
    ap.add_argument("--grab-t", type=float, default=3.0)
    a = ap.parse_args(argv)
    cfg = json.load(open(a.config))
    a.plate = a.plate or cfg["plate"]
    w = a.preview or 1080; h = int(round(w * 16 / 9))
    scene = render(a.plate, cfg, a.out, a.seconds, a.fps, (w, h), (1.0, 1.0) if a.no_push else tuple(cfg.get("push", (1.0, 1.06))))
    if a.grab:
        u = min(a.grab_t / max(a.seconds, 1e-6), 1.0)
        z = (1.0, 1.0) if a.no_push else tuple(cfg.get("push", (1.0, 1.06)))
        g = push_frame(scene.frame(a.grab_t), u, 1080, 1920, *z)
        g = cv2.resize(g, (360, 640), interpolation=cv2.INTER_AREA)
        cv2.imwrite(a.grab, cv2.cvtColor(g, cv2.COLOR_RGB2BGR))
    if a.proof:
        print(json.dumps(zero_motion_report(scene, np.arange(0, a.seconds, 0.5)), indent=1))


if __name__ == "__main__":
    main()
