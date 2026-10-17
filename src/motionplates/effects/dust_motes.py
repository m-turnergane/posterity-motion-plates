import math, numpy as np, cv2
from .base import Effect, register
from ..core.util import Noise1D, smoothstep, polygon_mask

@register("dust_motes")
class DustMotes(Effect):
    """Seeded drifting sun-lit dust. params: count, size [min,max] px, speed px/s, rise, depth [min,max] (parallax), intensity,
    luma_bias (spawn preferentially in bright shafts), region polygon, fade_in s."""
    def setup(self, ctx):
        p = self.p; rng = ctx.rng("dust", self.idx); n = p.get("count", 90); H, W = ctx.H, ctx.W
        lum = cv2.cvtColor(ctx.base.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
        reg = polygon_mask((H, W), p["region"]) if "region" in p else np.ones((H, W), np.float32)
        w = reg * (0.15 + lum ** p.get("luma_bias", 1.5)); w = cv2.resize(w, (W // 8, H // 8), interpolation=cv2.INTER_AREA); w /= w.sum()
        idx = rng.choice(w.size, size=n, p=w.ravel()); ys, xs = np.divmod(idx, w.shape[1])
        self.x = xs * 8 + rng.uniform(0, 8, n); self.y = ys * 8 + rng.uniform(0, 8, n)
        sz = p.get("size", [1.6, 4.2]); self.size = rng.uniform(*sz, n) ** 1.0
        self.depth = rng.uniform(*p.get("depth", [0.2, 0.9]), n)
        sp = p.get("speed", 9.0); self.vx = rng.uniform(-1, 1, n) * sp; self.vy = rng.uniform(-0.6, 1.0, n) * sp * 0.6 - p.get("rise", 2.0)
        self.nx = [Noise1D(rng, rng.uniform(0.25, 0.7)) for _ in range(n)]; self.ny = [Noise1D(rng, rng.uniform(0.25, 0.7)) for _ in range(n)]
        self.tw = [Noise1D(rng, rng.uniform(0.6, 1.6)) for _ in range(n)]
        self.amp = rng.uniform(0.45, 1.0, n) * p.get("intensity", 1.0); self.fade = p.get("fade_in", 0.8)
        self.lum = lum; self.col = np.array(p.get("color", [255, 226, 170]), np.float32)
        self.sprites = {}
    def sprite(self, r):
        k = int(round(r * 4)); 
        if k not in self.sprites:
            R = int(math.ceil(r * 2.6)) + 1; yy, xx = np.mgrid[-R:R + 1, -R:R + 1].astype(np.float32)
            g = np.exp(-(xx ** 2 + yy ** 2) / (2 * (k / 4 * 0.62) ** 2)); self.sprites[k] = g
        return self.sprites[k]
    def post(self, ctx, st, frame):
        t = st.t; H, W = frame.shape[:2]; ramp = float(smoothstep(t / self.fade)) if st.f > 0 else 0.0
        if ramp <= 0: return
        for i in range(len(self.x)):
            x = self.x[i] + self.vx[i] * t + 16 * self.nx[i](t) * (0.5 + self.depth[i]); y = self.y[i] + self.vy[i] * t + 10 * self.ny[i](t)
            X, Y = ctx.camera_fn(self.depth[i], t) @ np.array([x % W, y % H, 1.0], np.float32)
            if not (0 <= X < W and 0 <= Y < H): continue
            tw = 0.7 + 0.3 * self.tw[i](t)
            # fade near frame edges and by local lum so motes read as lit by the shaft, not stickers
            l = self.lum[int(Y), int(X)]; a = self.amp[i] * tw * ramp * (0.55 + 0.9 * l) * (0.8 + 0.4 * self.depth[i])
            g = self.sprite(self.size[i]); R = g.shape[0] // 2; xi, yi = int(round(X)), int(round(Y))
            xa, ya, xb, yb = max(xi - R, 0), max(yi - R, 0), min(xi + R + 1, W), min(yi + R + 1, H)
            gg = g[ya - (yi - R):yb - (yi - R), xa - (xi - R):xb - (xi - R)]
            roi = frame[ya:yb, xa:xb]; add = gg[..., None] * self.col * a * 0.95
            roi += add * (1 - roi / 330.0)  # soft-clip add
