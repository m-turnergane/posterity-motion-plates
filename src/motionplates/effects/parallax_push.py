import numpy as np
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
    def e(self, t):
        return float(smootherstep((t - self.t0) / (self.t1 - self.t0)))
    def scale_end(self, depth):
        bg, mid, fg = self.es["bg"], self.es["mid"], self.es["fg"]
        return bg + (mid - bg) * depth / 0.5 if depth <= 0.5 else mid + (fg - mid) * (depth - 0.5) / 0.5
    def matrix_for_depth(self, depth, t):
        e = self.e(t); s = 1 + (self.scale_end(depth) - 1) * e
        ax, ay = self.a; dx, dy = (self.drift.get("fg", [0, 0]) if depth > 0.75 else (0, 0))
        return np.array([[s, 0, ax * (1 - s) + dx * e], [0, s, ay * (1 - s) + dy * e]], np.float32)
