import numpy as np, cv2
from ..core.util import remap, polygon_mask, smoothstep
from .base import Effect, register

@register("smoke_drift")
class SmokeDrift(Effect):
    """Slow smoke/haze life limited to authored regions of ONE layer: (1) a low-frequency flow warp of the plate's own smoke pixels (<= ~2 px,
    evolving slowly, zero at the region boundary) and (2) optional faint warm wisps that scroll upward (blended toward the haze colour, never added).
    params: layer, regions:[{polygon, amp_px, rise_px_s, wisp_opacity, feather}], ramp_in (s). Everything outside the polygons is untouched."""
    def setup(self, ctx):
        self.regs = []
        for i, r in enumerate(self.p["regions"]):
            m = polygon_mask((ctx.H, ctx.W), r["polygon"], feather=r.get("feather", 18)); ys, xs = np.where(m > 0.01)
            x0, x1, y0, y1 = max(xs.min() - 2, 0), min(xs.max() + 3, ctx.W), max(ys.min() - 2, 0), min(ys.max() + 3, ctx.H); rng = ctx.rng("smoke", self.idx * 10 + i)
            h, w = y1 - y0, x1 - x0; sg = r.get("scale_px", 24)
            nz = lambda s, sh: cv2.GaussianBlur(rng.standard_normal(sh).astype(np.float32), (0, 0), s) 
            f = [nz(sg, (h, w)) for _ in range(4)]; f = [x / (x.std() + 1e-6) for x in f]
            T = int(self.p.get("seconds_hint", 6) * r.get("rise_px_s", 8)) + 2 * h; tall = nz(sg * 0.8, (T, w)) ; tall = tall / (tall.std() + 1e-6)
            self.regs.append(dict(r=r, bb=(x0, x1, y0, y1), m=m[y0:y1, x0:x1], f=f, tall=tall, ph=rng.uniform(0, 6.28), ph2=rng.uniform(0, 6.28)))
    def layer_stage(self, ctx, st):
        if st.f == 0: return
        t = st.t; ramp = float(smoothstep(t / self.p.get("ramp_in", 1.0))); rgb = st.rgb(self.p["layer"]); L = ctx.stack.by_name(self.p["layer"])
        for g in self.regs:
            r = g["r"]; x0, x1, y0, y1 = g["bb"]; h, w = y1 - y0, x1 - x0; m = g["m"]; amp = r.get("amp_px", 1.6) * ramp
            w1, w2 = 0.23, 0.17; c1, s1, c2, s2 = np.cos(w1 * t + g["ph"]), np.sin(w1 * t + g["ph"]), np.cos(w2 * t + g["ph2"]), np.sin(w2 * t + g["ph2"])
            dx = (g["f"][0] * c1 + g["f"][1] * s1) * 0.7071; dy = (g["f"][2] * c2 + g["f"][3] * s2) * 0.7071 - 0.5   # slightly biased upward
            yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
            mapx = xx - x0 - amp * m * dx; mapy = yy - y0 - amp * m * dy
            roi = rgb[y0:y1, x0:x1]; src = L.rgb[y0:y1, x0:x1]; out = remap(src, mapx, mapy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
            wo = r.get("wisp_opacity", 0.0)
            if wo > 0:
                sh = (t * r.get("rise_px_s", 8)) % max(g["tall"].shape[0] - h - 2, 1); win = cv2.warpAffine(g["tall"], np.float32([[1, 0, 0], [0, 1, -(g["tall"].shape[0] - h - 2 - sh)]]), (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
                al = np.clip((win - 0.35) * 0.55, 0, 1) * m * wo * ramp; col = np.array(r.get("color", [236, 206, 170]), np.float32)
                out = out + (col - out) * al[..., None]
            roi[...] = out
