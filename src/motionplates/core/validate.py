"""Recipe validation (structure, polygons, references, output settings, assets) — runs before any rendering.
Returns a list of problems; `check_recipe` raises RecipeError with all of them."""
import os, math
from ..effects.base import REGISTRY

class RecipeError(ValueError):
    pass

class PlatesRootError(RecipeError):
    pass

ENV = "MOTIONPLATES_PLATES"

def resolve_plates_root(cli_value=None):
    """CLI value > $MOTIONPLATES_PLATES. No hardcoded default (a project path must be configured explicitly)."""
    root = cli_value or os.environ.get(ENV)
    if not root:
        raise PlatesRootError(f"No plates directory configured. Pass --plates DIR or set ${ENV}=DIR (plates are read from there and never copied).")
    if not os.path.isdir(root):
        raise PlatesRootError(f"plates directory does not exist: {root}")
    return root

def _is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)

def _poly_problems(poly, W, H, where, slack=0.15):
    p = []
    if not isinstance(poly, (list, tuple)) or len(poly) < 3: return [f"{where}: polygon needs >= 3 vertices"]
    for i, v in enumerate(poly):
        if not (isinstance(v, (list, tuple)) and len(v) == 2 and _is_num(v[0]) and _is_num(v[1])): p.append(f"{where}[{i}]: vertex must be [x, y] numbers"); continue
        if not (-slack * W <= v[0] <= (1 + slack) * W and -slack * H <= v[1] <= (1 + slack) * H): p.append(f"{where}[{i}]: vertex {v} far outside the {W}x{H} frame")
    if not p:
        a = 0.5 * abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly))))
        if a < 4: p.append(f"{where}: degenerate polygon (area {a:.1f}px^2)")
    return p

def validate_recipe(R, plates_root=None, check_assets=True):
    P = []; need = lambda k: P.append(f"missing required key '{k}'") if k not in R else None
    for k in ("name", "plate", "effects"): need(k)
    if P: return P
    o = R.get("output", {}) or {}; W, H, fps, secs = o.get("width", 1080), o.get("height", 1920), o.get("fps", 30), o.get("seconds", 5)
    for k, v in (("width", W), ("height", H)):
        if not (isinstance(v, int) and 16 <= v <= 4096 and v % 2 == 0): P.append(f"output.{k} must be an even int in 16..4096 (got {v!r})")
    if not (_is_num(fps) and 1 <= fps <= 120): P.append(f"output.fps invalid: {fps!r}")
    if not (_is_num(secs) and 0.2 <= secs <= 120): P.append(f"output.seconds invalid: {secs!r} (duration is a recipe parameter, 0.2..120 s)")
    if not isinstance(R.get("seed", 1), int): P.append("seed must be an int")
    if not isinstance(R["plate"], dict) or "file" not in R["plate"]: P.append("plate.file is required")
    elif os.path.isabs(R["plate"]["file"]) or ".." in R["plate"]["file"].split("/"): P.append("plate.file must be relative to the plates root")
    elif check_assets and plates_root and not os.path.isfile(os.path.join(plates_root, R["plate"]["file"])): P.append(f"plate file not found: {os.path.join(plates_root, R['plate']['file'])}")
    names = {}
    for kind in ("layers", "elements"):
        for i, d in enumerate(R.get(kind, []) or []):
            n = d.get("name")
            if not n: P.append(f"{kind}[{i}]: name required"); continue
            if n in names or n == "bg": P.append(f"{kind}[{i}]: duplicate or reserved name '{n}'")
            names[n] = kind
            if not d.get("polygons"): P.append(f"{kind}[{n}]: polygons required")
            for j, poly in enumerate(d.get("polygons", [])): P += _poly_problems(poly, W, H, f"{kind}[{n}].polygons[{j}]")
            if kind == "layers" and not (_is_num(d.get("depth", 0.5)) and 0 <= d.get("depth", 0.5) <= 1.5): P.append(f"layers[{n}]: depth must be 0..1.5")
    for i, z in enumerate(R.get("safe_zones", []) or []):
        b = z.get("box"); 
        if not (isinstance(b, list) and len(b) == 4 and 0 <= b[0] < b[2] <= W and 0 <= b[1] < b[3] <= H): P.append(f"safe_zones[{i}]: box must be [x0,y0,x1,y1] inside the frame")
        if "name" not in z: P.append(f"safe_zones[{i}]: name required")
        if "max_mean_delta" not in z and "max_changed_fraction" not in z: P.append(f"safe_zones[{i}]: needs max_mean_delta or max_changed_fraction")
    allnames = set(names) | {"bg"}
    for i, e in enumerate(R.get("effects", [])):
        t = e.get("type")
        if t not in REGISTRY: P.append(f"effects[{i}]: unknown type {t!r} (known: {sorted(REGISTRY)})"); continue
        w = f"effects[{i}:{t}]"
        for key in ("layer",):
            if e.get(key) is not None and e[key] not in allnames: P.append(f"{w}: layer '{e[key]}' not defined")
        for n in e.get("elements", []) or []:
            if names.get(n) != "elements": P.append(f"{w}: element '{n}' not defined in elements")
        for fl in e.get("flames", []) or []:
            for key in ("layer",):
                if fl.get(key) and fl[key] not in allnames: P.append(f"{w}: flame layer '{fl[key]}' not defined")
            for n in fl.get("light_layers", []) or []:
                if n not in allnames: P.append(f"{w}: light layer '{n}' not defined")
            if not (_is_num(fl.get("x", 0)) and 0 <= fl.get("x", 0) <= W and 0 <= fl.get("y", 0) <= H): P.append(f"{w}: flame at {fl.get('x')},{fl.get('y')} outside frame")
        for key in ("region", "polygon"):
            if e.get(key): P += _poly_problems(e[key], W, H, f"{w}.{key}")
        if t == "petal_fall":
            sp = e.get("surface", {}).get("quad")
            if not sp or len(sp) != 4: P.append(f"{w}: surface.quad (4 corners: back-left, back-right, front-right, front-left) required")
            else: P += _poly_problems(sp, W, H, f"{w}.surface.quad")
            if e.get("hand_occluder"): P += _poly_problems(e["hand_occluder"], W, H, f"{w}.hand_occluder")
            ids = [c.get("id") for c in e.get("cuts", [])]
            if len(ids) != len(set(ids)): P.append(f"{w}: duplicate cut ids")
            for c in e.get("cuts", []):
                for k in ("id", "cx", "cy", "ax", "ay"):
                    if k not in c: P.append(f"{w}: cut missing '{k}'")
                if c.get("cx") is not None and not (0 <= c["cx"] <= W and 0 <= c["cy"] <= H): P.append(f"{w}: cut {c.get('id')} outside frame")
            for k in (e.get("release_s", {}) or {}):
                if k not in ids: P.append(f"{w}: release_s refers to unknown cut '{k}'")
        if t == "parallax_push":
            a = e.get("anchor")
            if a is not None and not (len(a) == 2 and 0 <= a[0] <= W and 0 <= a[1] <= H): P.append(f"{w}: anchor outside frame")
    qc = R.get("qc", {}) or {}
    if qc.get("playback_approved") not in (None, True, False): P.append("qc.playback_approved must be true/false")
    return P

def check_recipe(R, plates_root=None, check_assets=True):
    P = validate_recipe(R, plates_root, check_assets)
    if P: raise RecipeError("recipe invalid:\n  - " + "\n  - ".join(P))
