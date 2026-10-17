import os, time, json, hashlib, subprocess, math
import numpy as np, cv2
from . import plate as P
from .layers import build_stack, export_stack, Layer, LayerStack
from .recipe import load_recipe, make_rng_factory
from .encode import LosslessWriter, final_encode
from .metrics import MotionMeter
from .util import md5_file, md5_bytes, smoothstep
from .. import __version__
from ..effects import build_effects

class Ctx:
    pass

class FrameState:
    def __init__(self, ctx, t, f):
        self.ctx, self.t, self.f, self.H, self.W = ctx, t, f, ctx.H, ctx.W; self._rgb = {}; self._a = {}; self.surf_cam = None
    def rgb(self, n):
        if n not in self._rgb: self._rgb[n] = self.ctx.stack.by_name(n).rgb.copy()
        return self._rgb[n]
    def alpha(self, n):
        if n not in self._a: self._a[n] = self.ctx.stack.by_name(n).alpha.copy()
        return self._a[n]

def _stack_cache_key(recipe, plate_md5):
    spec = json.dumps({"layers": recipe.get("layers"), "elements": recipe.get("elements"), "petal": [e for e in recipe["effects"] if e["type"] == "petal_fall"], "v": __version__}, sort_keys=True)
    return md5_bytes((spec + plate_md5).encode())

def compose(ctx, st):
    out = None
    for L in ctx.stack.layers:
        rgb = st._rgb.get(L.name, L.rgb); a = st._a.get(L.name, L.alpha)
        pm = np.dstack([rgb * a[..., None], a])
        M = ctx.camera_fn(L.depth, st.t)
        if not (abs(M[0, 0] - 1) < 1e-9 and abs(M[0, 2]) < 1e-9 and abs(M[1, 2]) < 1e-9):
            pm = cv2.warpAffine(pm, M, (ctx.W, ctx.H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE if L.kind == "bg" else cv2.BORDER_CONSTANT, borderValue=0)
        if out is None: out = pm[..., :3].copy()
        else: out = out * (1 - pm[..., 3:4]) + pm[..., :3]
    return out

def render(recipe_path, outdir, plates_dir=None, seconds=None, frames=None, keep_lossless=False, export_layers=None, final_crf=14, log=print, only_times=None):
    t_all = time.time(); R = load_recipe(recipe_path); name = R["name"]; os.makedirs(outdir, exist_ok=True)
    o = R.get("output", {}); W, H, FPS = o.get("width", 1080), o.get("height", 1920), o.get("fps", 30); secs = seconds or o.get("seconds", 5); N = frames or int(round(secs * FPS))
    plate_path = os.path.join(plates_dir or P.plates_root(), R["plate"]["file"])
    base, pinfo = P.load_cover(plate_path, W, H)
    ctx = Ctx(); ctx.W, ctx.H, ctx.fps, ctx.seconds, ctx.base = W, H, FPS, secs, base; ctx.rng = make_rng_factory(R.get("seed", 1)); ctx.camera_fn = lambda d, t: np.array([[1, 0, 0], [0, 1, 0]], np.float32)
    effects = build_effects(R["effects"]); timings = {}
    # authoring stage (clean plate): effects may declare objects to remove
    t0 = time.time(); holes = np.zeros((H, W), np.uint8)
    for e in effects:
        h = e.authoring_holes(base)
        if h is not None: holes |= h
    stack = build_stack(base, R, extra_holes=holes, log=log); ctx.stack = stack; timings.update(stack.timings); timings["authoring_build_s"] = time.time() - t0
    if export_layers: export_stack(stack, export_layers)
    for e in effects: e.setup(ctx)
    lossless = os.path.join(outdir, f"{name}_lossless.mp4"); wr = LosslessWriter(lossless, W, H, FPS); meter = MotionMeter()
    still_idx = {int(round(s * FPS)): s for s in R.get("stills", [])}; still_dir = os.path.join(outdir, "stills_raw"); os.makedirs(still_dir, exist_ok=True)
    res = None; frame0 = None; pre0 = None; t_r = time.time(); fsha = hashlib.sha1(); zones = R.get('safe_zones', []) or []; zmeters = {z['name']: MotionMeter() for z in zones}; bar_hits = []
    frame_list = [int(round(x * FPS)) for x in sorted(set([0] + list(only_times)))] if only_times else range(N)
    if only_times: still_idx = {int(round(x * FPS)): x for x in only_times}
    for f in frame_list:
        t = f / FPS; st = FrameState(ctx, t, f)
        for e in effects: e.layer_stage(ctx, st)
        fr = compose(ctx, st)
        for e in effects: e.post(ctx, st, fr)
        if f == 0:
            pre0 = np.clip(np.rint(fr), 0, 255).astype(np.uint8); res = base.astype(np.float32) - fr
        w = 1 - float(smoothstep(t / R.get("frame0_residual_fade_s", 0.7)))
        if w > 0: fr = fr + res * w
        out = np.clip(np.rint(fr), 0, 255).astype(np.uint8)
        if f == 0: frame0 = out
        if f in still_idx: cv2.imwrite(os.path.join(still_dir, f"{name}_t{still_idx[f]:.2f}.png"), cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
        wr.write(out); meter.push(out); fsha.update(out.tobytes())
        for z in zones:
            x0, y0, x1, y1 = z['box']; zmeters[z['name']].push(out[y0:y1, x0:x1])
        if f % 15 == 0 and not only_times: bar_hits.append((f, P.detect_bars(out)))
        if only_times: continue
        if f % 30 == 0: log(f"  frame {f}/{N}  {(f + 1) / (time.time() - t_r):.2f} fps")
    wr.close(); render_s = time.time() - t_r
    if only_times:
        log('stills only -> ' + still_dir); return None
    d0 = np.abs(frame0.astype(int) - base.astype(int)); dpre = np.abs(pre0.astype(int) - base.astype(int))
    dbg = os.path.join(outdir, 'debug'); os.makedirs(dbg, exist_ok=True)
    cv2.imwrite(os.path.join(dbg, 'frame0_pre_residual.png'), cv2.cvtColor(pre0, cv2.COLOR_RGB2BGR)); cv2.imwrite(os.path.join(dbg, 'frame0_pre_residual_diff_x8.png'), np.clip(dpre.max(2) * 8, 0, 255).astype(np.uint8))
    mp4 = os.path.join(outdir, f"{name}_animated.mp4"); final_encode(lossless, mp4, final_crf)
    man = dict(name=name, version=__version__, recipe=os.path.abspath(recipe_path), recipe_md5=md5_file(recipe_path), plate=pinfo, seed=R.get("seed", 1),
               output=dict(W=W, H=H, fps=FPS, frames=N, seconds=N / FPS), engine=dict(python="numpy+OpenCV+Pillow", encode="ffmpeg libx264 lossless intermediate -> crf%d" % final_crf),
               timings_s={k: round(v, 2) for k, v in timings.items()}, render_s=round(render_s, 2), render_fps=round(N / render_s, 2), total_s=round(time.time() - t_all, 2),
               frame0=dict(max_abs_diff_vs_plate=int(d0.max()), mean_abs_diff_vs_plate=float(d0.mean()), pre_residual_max=int(dpre.max()), pre_residual_mean=float(dpre.mean()),
                           pre_residual_pixels_over_8=int((dpre.max(2) > 8).sum()), note="frame 0 = plate after residual correction; residual fades out over frame0_residual_fade_s"),
               motion=meter.summary(), frames_sha1=fsha.hexdigest(), safe_zones={z['name']: dict(box=z['box'], max_mean_delta_allowed=z.get('max_mean_delta'), **zmeters[z['name']].summary()) for z in zones},
               edge_bar_scan={'frames_checked': len(bar_hits), 'any_bar_detected': any(any(v.values()) for _, v in bar_hits)}, effects=R["effects"], mp4=mp4, mp4_md5=md5_file(mp4), lossless_md5=md5_file(lossless))
    try: man["git"] = subprocess.check_output(["git", "-C", os.path.dirname(os.path.abspath(__file__)), "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception: man["git"] = None
    json.dump(man, open(os.path.join(outdir, f"{name}_manifest.json"), "w"), indent=1)
    np.save(os.path.join(outdir, "_static.npy"), base) if False else None
    cv2.imwrite(os.path.join(outdir, f"{name}_static_plate.png"), cv2.cvtColor(base, cv2.COLOR_RGB2BGR))
    if not keep_lossless: pass
    return man
