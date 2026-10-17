import numpy as np, cv2
from .base import Effect, register
from .flame_flicker import local_light, WARM
from ..core.util import multi_flicker, smoothstep, polygon_mask

def _noise_tex(rng, h, w, octaves=3):
    out = np.zeros((h, w), np.float32); a = 1.0
    for o in range(octaves):
        g = rng.standard_normal((h // (4 * 2 ** (octaves - 1 - o)) + 3, w // (4 * 2 ** (octaves - 1 - o)) + 3)).astype(np.float32)
        out += a * cv2.resize(g, (w, h), interpolation=cv2.INTER_CUBIC); a *= 0.5
    return out / out.std()

@register("torch_light")
class TorchLight(Effect):
    """Torch/fire light on a scene: per-source irregular flicker (local warm light) + slowly morphing soft shadow modulation
    (low-frequency noise field, keyframed and cosine-blended) limited to a wall/floor region polygon.
    params: sources:[{x,y,R,gain,aniso,layers}], shadow:{amount, region, keyframe_s, scale}"""
    def setup(self, ctx):
        self.src = []
        for i, s in enumerate(self.p["sources"]):
            self.src.append((s, multi_flicker(ctx.rng("torch", self.idx * 100 + i), ((1.4, .3), (3.1, .3), (6.3, .25), (11., .15)))))
        sh = self.p.get("shadow")
        if sh:
            rng = ctx.rng("torchshadow", self.idx); self.sh = sh; self.kf_s = sh.get("keyframe_s", 1.1)
            n = int(ctx.seconds / self.kf_s) + 3; gh, gw = ctx.H // 12, ctx.W // 12
            self.tex = [_noise_tex(rng, gh, gw) for _ in range(n)]
            self.region = cv2.resize(polygon_mask((ctx.H, ctx.W), sh["region"], feather=sh.get("feather", 25)), (gw, gh), interpolation=cv2.INTER_AREA)
    def _shadow_field(self, t):
        u = t / self.kf_s; i = int(u); fr = u - i; k = 0.5 - 0.5 * np.cos(np.pi * fr)
        return self.tex[i] * (1 - k) + self.tex[i + 1] * k
    def layer_stage(self, ctx, st):
        t = st.t; ramp = float(smoothstep(t / self.p.get("ramp_in", 0.6))) if st.f > 0 else 0.0
        if ramp == 0: return
        sf = None
        if hasattr(self, "tex"):
            n = self._shadow_field(t)
            sf = cv2.resize(n * self.region, (ctx.W, ctx.H), interpolation=cv2.INTER_CUBIC)
        for s, fl in self.src:
            L = fl(t) * ramp
            fld = None
            if sf is not None:
                amt = self.sh.get("light_mod", 0.5)
                fld = lambda x0, x1, y0, y1, sf=sf, amt=amt: np.clip(1 + amt * sf[y0:y1, x0:x1], 0.2, 1.8)
            local_light(st, s.get("layers", ["bg"]), s["x"], s["y"], s["R"], s["gain"] * L, aniso=tuple(s.get("aniso", [1, 1])), field=fld)
        if sf is not None:
            a = self.sh.get("amount", 0.06) * ramp
            for ln in self.sh.get("layers", ["bg"]):
                rgb = st.rgb(ln); rgb *= (1 + a * np.clip(sf, -2, 2))[..., None] * 1.0 + 0.0
