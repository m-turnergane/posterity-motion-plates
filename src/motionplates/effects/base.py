"""Effect plug-in base. Stages: authoring_holes (clean-plate removal), setup, layer_stage (modify per-frame layer pixels),
camera (parallax), post (screen-space particles). All effects are pure functions of (seed, params, t)."""
import numpy as np
REGISTRY = {}

def register(name):
    def deco(cls):
        REGISTRY[name] = cls; cls.type = name; return cls
    return deco

class Effect:
    type = "base"
    def __init__(self, params, idx=0):
        self.p = params; self.idx = idx
    def authoring_holes(self, base):  # -> uint8 mask of objects to remove from the clean plate, or None
        return None
    def setup(self, ctx): pass
    def layer_stage(self, ctx, st): pass
    def post(self, ctx, st, frame): pass

def build_effects(specs):
    out = []
    for i, s in enumerate(specs):
        s = dict(s); typ = s.pop("type")
        if typ not in REGISTRY:
            raise KeyError(f"unknown effect {typ}; known: {sorted(REGISTRY)}")
        out.append(REGISTRY[typ](s, i))
    return out

def blend_rgba(frame, patch_premult, x0, y0, gain=1.0):
    """Composite premultiplied RGBA float patch (h,w,4; rgb already *alpha) onto frame at integer x0,y0 (clipped)."""
    h, w = patch_premult.shape[:2]; H, W = frame.shape[:2]
    xa, ya = max(x0, 0), max(y0, 0); xb, yb = min(x0 + w, W), min(y0 + h, H)
    if xb <= xa or yb <= ya: return
    p = patch_premult[ya - y0:yb - y0, xa - x0:xb - x0]
    roi = frame[ya:yb, xa:xb]
    roi *= (1 - p[..., 3:4]); roi += p[..., :3] * gain
