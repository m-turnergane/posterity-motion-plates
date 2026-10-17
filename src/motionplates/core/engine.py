import os, time, json, hashlib, subprocess, math
import numpy as np, cv2
from . import plate as P
from .layers import build_stack, export_stack, Layer, LayerStack
from .recipe import load_recipe, make_rng_factory
from .encode import FFmpegWriter, EncodeError, verify_video
from . import qc as QCm
from .validate import check_recipe, resolve_plates_root, RecipeError
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
        gw = getattr(ctx, "ground_warp", None)
        if gw is not None and L.kind == "bg":
            mx, my = gw(ctx, st.t); pm = cv2.remap(pm, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        elif not (abs(M[0, 0] - 1) < 1e-9 and abs(M[0, 2]) < 1e-9 and abs(M[1, 2]) < 1e-9):
            pm = cv2.warpAffine(pm, M, (ctx.W, ctx.H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE if L.kind == "bg" else cv2.BORDER_CONSTANT, borderValue=0)
        if out is None: out = pm[..., :3].copy()
        else: out = out * (1 - pm[..., 3:4]) + pm[..., :3]
    return out

class RenderRejected(RuntimeError):
    pass

def _frame0_masks(pre0, base, thr):
    d = np.abs(pre0.astype(np.int16) - base.astype(np.int16)).max(2)
    return d, (d > thr)

def _classify_diff(d, ctx, stack, holes):
    """Where is the frame-0 composition error concentrated? (share of pixels with diff>2 and of diff mass)"""
    ms = {}
    for L in stack.layers:
        if L.kind == "bg": continue
        a = L.alpha; ms["rim:" + L.name] = (a > 0.02) & (a < 0.98)
    if holes is not None: ms["petal_clean_plate_holes"] = cv2.dilate(holes, np.ones((5, 5), np.uint8)) > 0
    bh = stack.masks.get("bg_hole")
    if bh is not None: ms["bg_inpaint_zone"] = bh > 0
    sel = d > 2; tot = max(int(sel.sum()), 1); mass = float(d[sel].sum()) or 1.0; out = {}; claimed = np.zeros(d.shape, bool)
    for k, m in ms.items():
        mm = m & sel & ~claimed; out[k] = dict(pixels=int(mm.sum()), share_of_pixels=round(mm.sum() / tot, 3), share_of_mass=round(float(d[mm].sum()) / mass, 3)); claimed |= m
    rest = sel & ~claimed; out["elsewhere"] = dict(pixels=int(rest.sum()), share_of_pixels=round(rest.sum() / tot, 3), share_of_mass=round(float(d[rest].sum()) / mass, 3))
    return out

def prepare(recipe_path, plates_dir=None, seconds=None, frames=None, log=print, check_assets=True):
    """Validate + build everything needed to render frames (authoring stage). Returns ctx."""
    R = load_recipe(recipe_path); root = resolve_plates_root(plates_dir); check_recipe(R, root, check_assets)
    ctx = Ctx(); ctx.R = R; ctx.name = R["name"]; o = R.get("output", {}); ctx.W, ctx.H, ctx.fps = o.get("width", 1080), o.get("height", 1920), o.get("fps", 30)
    ctx.seconds = seconds or o.get("seconds", 5); ctx.N = frames or int(round(ctx.seconds * ctx.fps)); W, H = ctx.W, ctx.H
    ctx.plate_path = os.path.join(root, R["plate"]["file"]); base, ctx.pinfo = P.load_cover(ctx.plate_path, W, H); ctx.base = base
    ctx.rng = make_rng_factory(R.get("seed", 1)); ctx.camera_fn = lambda d, t: np.array([[1, 0, 0], [0, 1, 0]], np.float32)
    ctx.effects = build_effects(R["effects"]); ctx.timings = {}
    t0 = time.time(); holes = np.zeros((H, W), np.uint8)
    for e in ctx.effects:
        h = e.authoring_holes(base)
        if h is not None: holes |= h
    ctx.holes = holes; ctx.stack = build_stack(base, R, extra_holes=holes, log=log); ctx.timings.update(ctx.stack.timings); ctx.timings["authoring_build_s"] = time.time() - t0
    for e in ctx.effects: e.setup(ctx)
    ctx.pre0 = None; ctx.res = None; ctx.res_mask = None
    f0 = R.get("frame0", {}) or {}; ctx.f0_mode = f0.get("mode", "targeted"); ctx.f0_thr = f0.get("threshold", 1); ctx.f0_fade = f0.get("fade_s", R.get("frame0_residual_fade_s", 0.7))
    return ctx

def frame_at(ctx, f):
    """Stateless render of frame f -> uint8 RGB (applies the frame-0 correction fade). Frame 0 is always computed first on demand."""
    if ctx.pre0 is None and f != 0: frame_at(ctx, 0)
    t = f / ctx.fps; st = FrameState(ctx, t, f)
    for e in ctx.effects: e.layer_stage(ctx, st)
    fr = compose(ctx, st)
    for e in ctx.effects: e.post(ctx, st, fr)
    if f == 0:
        ctx.pre0 = np.clip(np.rint(fr), 0, 255).astype(np.uint8); d, m = _frame0_masks(ctx.pre0, ctx.base, ctx.f0_thr - 0.5 if ctx.f0_thr >= 1 else 0.5)
        res = ctx.base.astype(np.float32) - fr
        if ctx.f0_mode == "none": ctx.res = None; ctx.res_mask = None
        else:
            # targeted: correct only where composition really differs from the plate (dilated by 2px, feathered); everything else is untouched
            m8 = m.astype(np.uint8); ctx.res_mask = np.maximum(cv2.dilate(m8, np.ones((5, 5), np.uint8)).astype(np.float32), cv2.GaussianBlur(cv2.dilate(m8, np.ones((11, 11), np.uint8)).astype(np.float32), (0, 0), 2.0)); ctx.res = res * ctx.res_mask[..., None]
    w = 1 - float(smoothstep(t / ctx.f0_fade)) if ctx.f0_fade > 0 else 0.0
    if ctx.res is not None and w > 0: fr = fr + ctx.res * w
    return np.clip(np.rint(fr), 0, 255).astype(np.uint8)

def _diag_frame0(ctx, dbg):
    """Diagnostics for the frame-0 correction: where was the residual concentrated?"""
    os.makedirs(dbg, exist_ok=True); d = np.abs(ctx.pre0.astype(np.int16) - ctx.base.astype(np.int16)).max(2)
    cv2.imwrite(os.path.join(dbg, "frame0_residual_map.png"), cv2.applyColorMap(np.clip(d * 6, 0, 255).astype(np.uint8), cv2.COLORMAP_INFERNO))
    if ctx.res_mask is not None: cv2.imwrite(os.path.join(dbg, "frame0_correction_mask.png"), (ctx.res_mask * 255).astype(np.uint8))
    cls = _classify_diff(d, ctx, ctx.stack, ctx.holes)
    return dict(pre_correction=dict(mean_abs=float(d.mean()), max_abs=int(d.max()), pixels_over_2=int((d > 2).sum()), pixels_over_8=int((d > 8).sum()), fraction_over_2=float((d > 2).mean()),
                corrected_fraction=float((ctx.res_mask > 0.5).mean()) if ctx.res_mask is not None else 0.0), concentration=cls, mode=ctx.f0_mode, fade_s=ctx.f0_fade)

def render(recipe_path, outdir, plates_dir=None, seconds=None, frames=None, keep_lossless=False, export_layers=None, final_crf=14, log=print, only_times=None, profile="direct", threads=0, expect_status=None):
    """Render; raises RecipeError (invalid recipe), EncodeError (ffmpeg/verification), RenderRejected (QC FAIL). Returns the manifest dict (status in man['qc']['status'])."""
    t_all = time.time(); ctx = prepare(recipe_path, plates_dir, seconds, frames, log); R = ctx.R; name, W, H, FPS, N = ctx.name, ctx.W, ctx.H, ctx.fps, ctx.N
    os.makedirs(outdir, exist_ok=True)
    if export_layers: export_stack(ctx.stack, export_layers)
    still_dir = os.path.join(outdir, "stills_raw")
    if only_times:   # stills only: no video, no intermediate files, nothing else written
        os.makedirs(still_dir, exist_ok=True)
        for x in sorted(set(only_times)):
            f = int(round(x * FPS)); out = frame_at(ctx, f); cv2.imwrite(os.path.join(still_dir, f"{name}_t{x:.2f}.png"), cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
        log("stills only -> " + still_dir); return None
    still_idx = {int(round(s * FPS)): s for s in R.get("stills", [])}; os.makedirs(still_dir, exist_ok=True)
    meter = MotionMeter(); fsha = hashlib.sha1(); zones = R.get("safe_zones", []) or []; zmeters = {z["name"]: MotionMeter(thr=z.get("threshold", 2)) for z in zones}; bar_hits = []
    mp4 = os.path.join(outdir, f"{name}_animated.mp4"); t_r = time.time(); frame0 = None; info = None
    with FFmpegWriter(mp4, W, H, FPS, crf=final_crf, profile=profile, threads=threads) as wr:
        for f in range(N):
            out = frame_at(ctx, f)
            if f == 0: frame0 = out
            if f in still_idx: cv2.imwrite(os.path.join(still_dir, f"{name}_t{still_idx[f]:.2f}.png"), cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
            wr.write(out); meter.push(out); fsha.update(out.tobytes())
            for z in zones:
                x0, y0, x1, y1 = z["box"]; zmeters[z["name"]].push(out[y0:y1, x0:x1])
            if f % 15 == 0: bar_hits.append((f, P.detect_bars(out)))
            if f % 30 == 0: log(f"  frame {f}/{N}  {(f + 1) / (time.time() - t_r):.2f} fps")
    render_s = time.time() - t_r; t_v = time.time(); info = wr.finalize(dict(W=W, H=H, fps=FPS, frames=N)); verify_s = time.time() - t_v
    frames_sha1 = fsha.hexdigest(); dbg = os.path.join(outdir, "debug"); os.makedirs(dbg, exist_ok=True)
    cv2.imwrite(os.path.join(dbg, "frame0_pre_correction.png"), cv2.cvtColor(ctx.pre0, cv2.COLOR_RGB2BGR)); f0 = _diag_frame0(ctx, dbg)
    d0 = np.abs(frame0.astype(int) - ctx.base.astype(int)); f0.update(max_abs_diff_vs_plate=int(d0.max()), mean_abs_diff_vs_plate=float(d0.mean()))
    qc = QCm.QC(); ms = meter.summary()
    # --- automated checks ---
    qc.add("encode:verified", QCm.PASS, info, None, "ffprobe resolution/fps/frames/duration + full decode")
    qc.check_max("frame0:max_diff_vs_plate", f0["max_abs_diff_vs_plate"], review=0, fail=2, note="frame 0 must equal the plate (lossless RGB)")
    qc.check_max("frame0:correction_fraction", f0["pre_correction"]["corrected_fraction"], review=0.02, fail=0.10, note="share of the frame the frame-0 correction has to touch; large = start composition wrong")
    mo = R.get("qc", {}).get("motion", {}) or {}
    qc.check_min("motion:mean_frame_delta_floor", ms["mean_abs_frame_delta"], review=mo.get("floor", 0.12), fail=0.02, note="too static is not an animation")
    qc.check_max("motion:mean_frame_delta_cap", ms["mean_abs_frame_delta"], review=mo.get("cap", 1.6), fail=mo.get("fail_cap", 3.0), note="restraint cap")
    qc.check_max("motion:max_frame_delta", ms["max_mean_abs_frame_delta"], review=mo.get("max_frame", 3.0), fail=6.0, note="single-frame jumps")
    zs = {}
    for z in zones:
        sm = zmeters[z["name"]].summary(); zs[z["name"]] = dict(box=z["box"], limit_mean_delta=z.get("max_mean_delta"), limit_changed_fraction=z.get("max_changed_fraction"), **sm)
        if z.get("max_mean_delta") is not None: qc.check_max(f"safe_zone:{z['name']}:mean_delta", sm["mean_abs_frame_delta"], fail=z["max_mean_delta"], note="caption/UI-safe zone must stay calm")
        if z.get("max_changed_fraction") is not None: qc.check_max(f"safe_zone:{z['name']}:changed_fraction", sm["mean_changed_pixel_fraction"], fail=z["max_changed_fraction"])
    bars = any(any(v.values()) for _, v in bar_hits); qc.add("edge_bar_scan", QCm.FAIL if bars else QCm.PASS, bars, False, "white/black bars at frame edges")
    md = QCm.mask_diagnostics(ctx.stack, ctx.base, qc)
    # frame-to-frame determinism of the render hash is tested in CI; here the hash is recorded
    status, why = qc.final(R, frames_sha1, motion_plate=True)
    man = dict(name=name, version=__version__, recipe=os.path.abspath(recipe_path), recipe_md5=md5_file(recipe_path), plate=ctx.pinfo, seed=R.get("seed", 1),
               output=dict(W=W, H=H, fps=FPS, frames=N, seconds=N / FPS), engine=dict(python="numpy+OpenCV+Pillow", encode=f"ffmpeg libx264 {profile} crf{final_crf} (RGB->yuv420p once, bt709/tv tagged)"), verify=info,
               timings_s={k: round(v, 2) for k, v in ctx.timings.items()}, render_s=round(render_s, 2), render_fps=round(N / render_s, 2), verify_s=round(verify_s, 2), total_s=round(time.time() - t_all, 2),
               frame0=f0, motion=ms, frames_sha1=frames_sha1, safe_zones=zs, mask_diagnostics=md,
               edge_bar_scan={"frames_checked": len(bar_hits), "any_bar_detected": bars}, effects=R["effects"],
               qc=dict(status=status, reason=why, checks=qc.checks, playback_qc="REQUIRED: a human must watch the full-res MP4 on a phone-size player; set qc.playback_approved/approved_by/approved_frames_sha1 in the recipe"),
               mp4=mp4, mp4_md5=md5_file(mp4))
    try: man["git"] = subprocess.check_output(["git", "-C", os.path.dirname(os.path.abspath(__file__)), "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception: man["git"] = None
    cv2.imwrite(os.path.join(outdir, f"{name}_static_plate.png"), cv2.cvtColor(ctx.base, cv2.COLOR_RGB2BGR))
    if status == QCm.FAIL:
        rej = os.path.join(outdir, f"{name}_REJECTED.mp4"); os.replace(mp4, rej); man["mp4"] = rej; man["mp4_md5"] = md5_file(rej)
    json.dump(man, open(os.path.join(outdir, f"{name}_manifest.json"), "w"), indent=1, default=str)
    if status == QCm.FAIL: raise RenderRejected("QC FAIL: " + "; ".join(f"{c['name']}={c['value']}" for c in qc.checks if c["status"] == QCm.FAIL))
    return man
