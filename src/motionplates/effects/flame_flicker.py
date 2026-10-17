import math, numpy as np, cv2
from ..core.util import remap
from .base import Effect, register
from ..core.util import multi_flicker, smoothstep, Noise1D

WARM = np.array([1.0, 0.72, 0.38], np.float32)

def local_light(st, layers, cx, cy, R, gain, warm=WARM, aniso=(1.0, 1.0), recv_lo=0.05, recv_hi=0.45, field=None):
    """Add/multiply a localized warm light with smooth falloff onto the named layers (ROI-only).
    gain>0 brightens (receiver-aware: dark surfaces respond less), gain<0 dims. field: optional 2-D modulation sampled in ROI."""
    H, W = st.H, st.W; rx, ry = R * aniso[0], R * aniso[1]; ex, ey = int(rx * 2.2), int(ry * 2.2)
    x0, x1, y0, y1 = max(int(cx - ex), 0), min(int(cx + ex), W), max(int(cy - ey), 0), min(int(cy + ey), H)
    if x1 <= x0 or y1 <= y0: return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    d2 = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    fall = np.exp(-d2 * 1.6) * 0.75 + np.exp(-d2 * 0.45) * 0.25   # tight core + wide skirt
    if field is not None: fall = fall * field(x0, x1, y0, y1)
    for ln in layers:
        rgb = st.rgb(ln); roi = rgb[y0:y1, x0:x1]
        lum = roi.mean(2) / 255.0; recv = 0.35 + 0.65 * smoothstep((lum - recv_lo) / (recv_hi - recv_lo))
        g = (gain * fall * recv)[..., None]
        roi *= (1 + g * warm * 0.9); roi += g * warm * 22.0

@register("flame_flicker")
class FlameFlicker(Effect):
    """Flame silhouette warp + colour shift + localized warm light on neighbouring surfaces, irregular multi-band flicker.
    params: flames: [{x,y,rx,ry (flame ROI ellipse), layer, lum_lo, lum_hi, warp_px, rise_px, light_R, light_gain,
    light_layers, color_shift, seed_offset}], ramp_in s."""
    def setup(self, ctx):
        self.fl = []
        for i, f in enumerate(self.p["flames"]):
            rng = ctx.rng("flame", self.idx * 100 + i)
            m = np.zeros((ctx.H, ctx.W), np.float32)
            cv2.ellipse(m, (int(f["x"]), int(f["y"])), (int(f["rx"]), int(f["ry"])), 0, 0, 360, 1.0, -1)
            lum = ctx.base.astype(np.float32).mean(2) / 255.0
            fm = m * smoothstep((lum - f.get("lum_lo", 0.78)) / (f.get("lum_hi", 0.93) - f.get("lum_lo", 0.78)))
            fm = cv2.GaussianBlur(fm, (0, 0), f.get("soft", 2.0))
            x0, x1 = max(int(f["x"] - f["rx"] * 1.5), 0), min(int(f["x"] + f["rx"] * 1.5), ctx.W); y0, y1 = max(int(f["y"] - f["ry"] * 1.6), 0), min(int(f["y"] + f["ry"] * 1.3), ctx.H)
            bb = (x0, x1, y0, y1); wm = cv2.GaussianBlur(cv2.dilate(fm, np.ones((9, 9), np.uint8)), (0, 0), 3.0)
            self.fl.append(dict(f=f, fm=fm[y0:y1, x0:x1], wm=wm[y0:y1, x0:x1], bb=bb, fl_light=multi_flicker(rng), fl_shape=multi_flicker(rng, ((2.2, .3), (5.0, .35), (9.0, .2), (15., .15))),
                                nxs=[Noise1D(rng, fr) for fr in (1.3, 2.9, 5.7)], ph=rng.uniform(0, 6.28, 3)))
    def layer_stage(self, ctx, st):
        t = st.t; ramp = float(smoothstep(t / self.p.get("ramp_in", 0.5))) if st.f > 0 else 0.0
        if ramp == 0: return
        for fd in self.fl:
            f = fd["f"]; x0, x1, y0, y1 = fd["bb"]; rgb = st.rgb(f.get("layer", "bg")); roi = rgb[y0:y1, x0:x1]
            s = fd["fl_shape"](t) * ramp; L = fd["fl_light"](t) * ramp
            h, w = roi.shape[:2]; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); hn = 1 - (yy / h)   # 1 at flame tip side (top)
            warp = f.get("warp_px", 2.0); rise = f.get("rise_px", 2.0)
            dx = warp * (fd["nxs"][0](t - yy * 0.012) * 0.6 + fd["nxs"][1](t - yy * 0.02) * 0.4) * (0.3 + hn) * ramp * fd["wm"]
            dy = (-rise * (0.5 + 0.5 * s) * hn - 0.4 * rise * s) * fd["wm"]
            mapx = xx + dx; mapy = yy + dy
            warped = remap(roi, mapx, mapy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
            fm = fd["fm"][..., None]
            cs = f.get("color_shift", 0.18)
            hot = np.array([255, 240, 200], np.float32); cool = np.array([255, 170, 80], np.float32)
            tint = hot * (0.5 + 0.5 * s) + cool * (0.5 - 0.5 * s)
            warped = warped * (1 - fm * cs * abs(s)) + tint * fm * cs * abs(s)
            warped = warped * (1 + fm * (0.10 * L))
            roi[...] = roi * (1 - fd["wm"][..., None]) + warped * fd["wm"][..., None]
            local_light(st, f.get("light_layers", ["bg"]), f["x"], f["y"] - f.get("light_dy", 0), f.get("light_R", 120), f.get("light_gain", 0.25) * L,
                        aniso=tuple(f.get("aniso", [1.0, 1.0])))
