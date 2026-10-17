import numpy as np, cv2
from ..core.util import remap
from .base import Effect, register
from ..core.util import Noise1D, smoothstep

@register("banner_sway")
class BannerSway(Effect):
    """Restrained cloth sway for alpha-element layers (banners): mesh-like displacement, pinned at the top, growing toward the hem,
    sum of a travelling sine + seeded noise. params: elements:[names], amp_px, freq_hz, ramp_in, wave_k"""
    def setup(self, ctx):
        self.el = []
        for i, n in enumerate(self.p["elements"]):
            L = ctx.stack.by_name(n); ys, xs = np.where(L.alpha > 0.02)
            x0, x1, y0, y1 = max(xs.min() - 12, 0), min(xs.max() + 13, ctx.W), max(ys.min() - 4, 0), min(ys.max() + 8, ctx.H)
            rng = ctx.rng("banner", self.idx * 10 + i)
            self.el.append(dict(n=n, bb=(x0, x1, y0, y1), top=ys.min(), bot=ys.max(), ph=rng.uniform(0, 6.28), nz=Noise1D(rng, 0.55), nz2=Noise1D(rng, 1.3),
                                amp=self.p.get("amp_px", 4.0) * rng.uniform(0.8, 1.15), fr=self.p.get("freq_hz", 0.45) * rng.uniform(0.85, 1.15)))
    def layer_stage(self, ctx, st):
        t = st.t; ramp = float(smoothstep(t / self.p.get("ramp_in", 0.8))) if st.f > 0 else 0.0
        if ramp == 0: return
        k = self.p.get("wave_k", 0.012)
        for e in self.el:
            x0, x1, y0, y1 = e["bb"]; L = ctx.stack.by_name(e["n"]); rgb = st.rgb(e["n"]); a = st.alpha(e["n"])
            h, w = y1 - y0, x1 - x0; yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
            wgt = np.clip((yy - e["top"]) / max(e["bot"] - e["top"], 1), 0, 1) ** 1.5
            ph = 2 * np.pi * e["fr"] * t + e["ph"] - yy * k
            dx = e["amp"] * wgt * (0.62 * np.sin(ph) + 0.28 * e["nz"](t) + 0.10 * e["nz2"](t)) * ramp
            dy = -0.04 * np.abs(dx) * wgt * 3     # slight foreshortening when swung
            mx, my = xx - x0 - dx, yy - y0 - dy
            rgb[y0:y1, x0:x1] = remap(L.rgb[y0:y1, x0:x1], mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            a[y0:y1, x0:x1] = remap(L.alpha[y0:y1, x0:x1], mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
