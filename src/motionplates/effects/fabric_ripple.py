import numpy as np, cv2
from ..core.util import remap
from .base import Effect, register
from ..core.util import smoothstep, polygon_mask, Noise1D

@register("fabric_ripple")
class FabricRipple(Effect):
    """Very slight cloth life: sub-pixel travelling-wave displacement + shading modulation inside a feathered polygon of one layer.
    params: layer, region polygon, amp_px (<=1), shade (<=0.05), wavelength_px, speed_px_s, angle_deg"""
    def setup(self, ctx):
        p = self.p; m = polygon_mask((ctx.H, ctx.W), p["region"], feather=p.get("feather", 12))
        ys, xs = np.where(m > 0.01); self.bb = (xs.min(), xs.max() + 1, ys.min(), ys.max() + 1); x0, x1, y0, y1 = self.bb; self.m = m[y0:y1, x0:x1]
        rng = ctx.rng("fabric", self.idx); self.ph = rng.uniform(0, 6.28); self.nz = Noise1D(rng, 0.4)
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32); a = np.deg2rad(p.get("angle_deg", 20)); self.u = xx * np.cos(a) + yy * np.sin(a)
        self.yy, self.xx = yy - y0, xx - x0
    def layer_stage(self, ctx, st):
        p = self.p; t = st.t; ramp = float(smoothstep(t / 1.0)) if st.f > 0 else 0.0
        if ramp == 0: return
        x0, x1, y0, y1 = self.bb; rgb = st.rgb(p["layer"]); roi = rgb[y0:y1, x0:x1]
        lam = p.get("wavelength_px", 90); k = 2 * np.pi / lam; ph = k * (self.u - p.get("speed_px_s", 22) * t) + self.ph
        w2 = 0.35 * np.sin(1.7 * ph + 1.3 + 0.6 * self.nz(t))
        s = np.sin(ph) + w2; amp = p.get("amp_px", 0.8) * ramp * self.m
        mapx = self.xx + amp * 0.35 * s; mapy = self.yy + amp * s
        out = remap(roi, mapx, mapy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        sh = (1 + p.get("shade", 0.035) * ramp * self.m * (np.cos(ph) + 0.4 * np.cos(1.7 * ph + 1.3)))[..., None]
        roi[...] = out * sh
