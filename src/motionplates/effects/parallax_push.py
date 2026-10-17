import numpy as np, cv2
from .base import Effect, register
from ..core.util import smootherstep

@register("parallax_push")
class ParallaxPush(Effect):
    """Eased 2.5D push-in. Each layer scales about `anchor` by its own amount (bg least, fg most) -> differential parallax.
    params: anchor [x,y]; end_scale {bg,mid,fg} (a few %); t0,t1 (s); drift_px {fg:[dx,dy]} optional."""
    def setup(self, ctx):
        self.a = self.p.get("anchor", [ctx.W / 2, ctx.H / 2]); self.es = self.p.get("end_scale", {"bg": 1.012, "mid": 1.03, "fg": 1.05})
        self.t0 = self.p.get("t0", 0.0); self.t1 = self.p.get("t1", ctx.seconds); self.drift = self.p.get("drift_px", {})
        ctx.camera_fn = self.matrix_for_depth
        gr = self.p.get("ground_ramp")      # continuous ground-plane parallax for the background layer: scale grows smoothly with y (no layer edges => no disocclusion at rubble/boulders)
        ctx.ground_warp = None
        if gr:
            self.gr = gr; H = ctx.H; ys = np.arange(H, dtype=np.float64); sm = np.clip((ys - gr["y0"]) / max(gr["y1"] - gr["y0"], 1), 0, 1); sm = sm * sm * (3 - 2 * sm)
            bg = self.es["bg"]; self.S_end = bg + (gr.get("end_scale", 1.04) - bg) * sm; self._cache = {}; ctx.ground_warp = self.ground_maps
    def ground_maps(self, ctx, t):
        k = round(t, 6)
        if k in self._cache: return self._cache[k]
        e = self.e(t); H, W = ctx.H, ctx.W; ax, ay = self.a; s = 1 + (self.S_end - 1) * e                       # per-row scale s(y)
        ys = np.arange(H, dtype=np.float64); Y = ay + np.concatenate([[0.0], np.cumsum((s[1:] + s[:-1]) / 2 * 1.0)]) - np.interp(ay, ys, np.concatenate([[0.0], np.cumsum((s[1:] + s[:-1]) / 2)]))
        yo = np.arange(H, dtype=np.float64); ysrc = np.interp(yo, Y, ys); ssrc = np.interp(ysrc, ys, s)
        mx = (ax + (np.arange(W)[None, :] - ax) / ssrc[:, None]).astype(np.float32); my = np.repeat(ysrc[:, None], W, 1).astype(np.float32)
        self._cache = {k: (mx, my)}; return mx, my
    def e(self, t):
        return float(smootherstep((t - self.t0) / (self.t1 - self.t0)))
    def scale_end(self, depth):
        bg, mid, fg = self.es["bg"], self.es["mid"], self.es["fg"]
        return bg + (mid - bg) * depth / 0.5 if depth <= 0.5 else mid + (fg - mid) * (depth - 0.5) / 0.5
    def matrix_for_depth(self, depth, t):
        e = self.e(t); s = 1 + (self.scale_end(depth) - 1) * e
        ax, ay = self.a; dx, dy = (self.drift.get("fg", [0, 0]) if depth > 0.75 else (0, 0))
        return np.array([[s, 0, ax * (1 - s) + dx * e], [0, s, ay * (1 - s) + dy * e]], np.float32)
