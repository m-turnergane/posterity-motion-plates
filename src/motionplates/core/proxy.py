"""Low-res proxy previews: scale a recipe (all pixel-space coordinates/lengths) and the output size by s (e.g. 0.25 -> 270x480).
Pure recipe transform: the same engine renders it, ~s^2 as many pixels. Used for fast authoring iteration; never for delivery."""
import copy

COORD_KEYS = {"polygons", "polygon", "region", "quad", "hand_occluder", "exclude", "speck_regions", "anchor", "box"}
LEN_KEYS = {"x", "y", "cx", "cy", "ax", "ay", "rx", "ry", "light_R", "R", "light_dy", "warp_px", "rise_px", "amp_px", "wavelength_px", "speed_px_s", "terminal_px_s",
            "sway_px", "slide_px", "min_sep_px", "max_lateral_px", "size", "speed", "rise", "scale_px", "rise_px_s", "land_jitter", "drift_px_s"}
SOFT_KEYS = {"grow", "feather", "band", "hole_grow", "soft", "radius", "hole_px", "open"}    # kernel-like: scale but keep >= 1 when > 0

def _scale(v, s):
    if isinstance(v, bool): return v
    if isinstance(v, (int, float)): return v * s
    if isinstance(v, (list, tuple)): return [_scale(x, s) for x in v]
    return v

def _walk(o, s, parent_key=None):
    if isinstance(o, dict):
        out = {}
        for k, v in o.items():
            if k in COORD_KEYS: out[k] = _scale(v, s)
            elif k in LEN_KEYS and not isinstance(v, (dict,)): out[k] = _scale(v, s)
            elif k in SOFT_KEYS and isinstance(v, (int, float)): out[k] = max(1, int(round(v * s))) if v > 0 else v
            elif k == "end_scale" or k == "type" or k == "preset": out[k] = v
            else: out[k] = _walk(v, s, k)
        return out
    if isinstance(o, list): return [_walk(x, s, parent_key) for x in o]
    return o

def scale_recipe(R, s):
    """returns a new recipe dict scaled by s (0 < s <= 1)."""
    R2 = _walk(copy.deepcopy(R), s); o = R2.setdefault("output", {})
    o["width"] = int(round(R.get("output", {}).get("width", 1080) * s / 2) * 2); o["height"] = int(round(R.get("output", {}).get("height", 1920) * s / 2) * 2)
    for z in R2.get("safe_zones", []) or []: z["box"] = [int(round(v)) for v in z["box"]]
    if R.get("stills") is not None: R2["stills"] = R["stills"]
    R2["_proxy_scale"] = s; R2["name"] = R["name"] + f"_proxy{int(round(s * 100))}"
    return R2
