"""Shared motion guardrails (2026-10-30, after the water_v1 K11 shot-2 failure; see engine-rnd/water/K11_FIRE_DIAGNOSIS.md).

  check_crop_zoom(zoom, max_zoom=1.5)          zoom = push/crop factor RELATIVE TO NATIVE COVER-FIT (1.0 = plate fills the frame).
                                               If plate_wh is given it ALSO runs check_pixel_density (density=True default).
  check_pixel_density(plate, out_wh, push)      output px per SOURCE px (cover-fit scale x max push x crop) <= 1.5, both axes
                                               (EIC ruling 2026-10-30: a 941x1672 plate cover-fit into 1920x1080 = 2.04 -> refused).
  check_fire_sharpness(plate, rects, zoom)      torch_v1c / water fire reflections only on sharp, native-resolution fire.
  check_shot(cfg, plate=None, mode="refuse")    convenience: push / crop zoom + fire rects from a shot config.

mode="refuse" raises GuardrailError; mode="warn" prints a WARNING to stderr and returns the report. Pure numpy/cv2, no side effects.
"""
import sys, json, math
from pathlib import Path
import numpy as np, cv2

MAX_ZOOM = 1.5              # never crop/zoom past ~1.5x of native fill
FIRE_MIN_LAPVAR = 100.0     # Laplacian variance of the fire rect luma at NATIVE res (locked torch plates measure 134-707; K11 fires 412-1790)
FIRE_MAX_ZOOM = 1.5         # fire effects additionally refuse any zoom above this
MAX_PX_DENSITY = 1.5        # EIC ruling 2026-10-30: never more than 1.5 output px per real source px (long-form 16:9 AND Shorts 9:16)

class GuardrailError(RuntimeError): pass

# Locked shots that pre-date this guardrail and are kept bit-identical. Waived = WARN (never refuse), only at exactly this zoom.
# Do NOT add new entries for new work; fix the framing instead.
# Scope (rev 2026-10-30 5:14pm, EIC ruling): a waiver matches ONLY the exact locked shot -- same config name AND same plate
# file (path + md5) AND push exactly [1.6, 1.6] AND no extra crop_zoom AND no fire block. It downgrades ONLY the crop_zoom
# check to warn; it is not a general 1.6x allowance and never relaxes the fire-sharpness check.
LOCKED_WAIVERS = {
    "p05v2_sun_glitter_v1d": dict(zoom=1.6, push=(1.6, 1.6),
        plate="/workspace/posterity/micro-anomaly/ugarit/plates/p05_coastal_town_raid_v2_OWNER.png",
        plate_md5="41025b966ebda2c4ecf9af6282d6a1b3",
        reason="water_v1 reel shot 3 (sun glitter), LOCKED by owner 2026-10-30 4:53pm ET at a 1.6x static crop; "
               "1.6x exemption accepted by EIC 2026-10-30, warn-only, this shot only",
        # pixel-density extension (rev 2026-10-30 pixel-density ruling): the 1080x1920 OWNER plate at a static 1.6x into the
        # 1080x1920 Short measures exactly 1.600 output px / source px (> 1.5). Same exact-shot match as above PLUS output
        # must be exactly 1080x1920 PLUS the measured density must be 1.6 -> density check downgraded to warn. Nothing else.
        density=1.6, out_wh=(1080, 1920)),
}

def _md5(path):
    import hashlib
    try: return hashlib.md5(open(path, "rb").read()).hexdigest()
    except OSError: return None

def waiver_for(cfg):
    """Return the waiver dict only if cfg IS the exact locked shot, else None."""
    wv = LOCKED_WAIVERS.get(cfg.get("name"))
    if not wv: return None
    push = tuple(float(v) for v in cfg.get("push", (1.0, 1.0)))
    if (len(push) != 2 or any(abs(a - b) > 1e-9 for a, b in zip(push, wv["push"])) or "crop_zoom" in cfg or cfg.get("fire")
            or str(cfg.get("plate")) != wv["plate"] or _md5(cfg.get("plate", "")) != wv["plate_md5"]):
        return None
    return wv

def _emit(ok, msg, mode, rep):
    """mode: refuse (raise) | warn (stderr WARNING) | measure (silent; caller decides)."""
    rep["ok"] = bool(ok); rep["msg"] = "ok" if ok else msg
    if not ok:
        if mode == "refuse": raise GuardrailError(msg)
        if mode == "measure": return rep
        print("WARNING guardrail: " + msg, file=sys.stderr)
    return rep

def output_px_per_plate_px(plate_wh, out_wh, zoom):
    (W, H), (w, h) = plate_wh, out_wh; return max(w / W, h / H) * zoom

def plate_size(plate):
    """REAL source size (w, h) from a file path (header read), an image array, or a (w, h) pair. Never a nominal size."""
    if isinstance(plate, np.ndarray): return int(plate.shape[1]), int(plate.shape[0])
    if isinstance(plate, (tuple, list)) and len(plate) == 2 and all(isinstance(v, (int, float, np.integer)) for v in plate):
        return int(plate[0]), int(plate[1])
    from PIL import Image
    with Image.open(str(plate)) as im: return im.size

def check_pixel_density(plate, out_wh, push_range=(1.0, 1.0), max_ratio=MAX_PX_DENSITY, mode="refuse", crop_zoom=1.0, name=None):
    """Output pixels per SOURCE pixel at the tightest moment of the shot, on both axes.
    plate: path / RGB array / (w, h) of the FULL plate (real file size). out_wh: output frame (W, H).
    push_range: [z0, z1] push relative to cover-fit (the max is used). crop_zoom: extra crop factor relative to cover-fit
    (1 / crop frac). ratio = max(W / visible_w, H / visible_h) where visible = cover-fit window / (max push x crop_zoom)."""
    pw, ph = plate_size(plate); W, H = int(out_wh[0]), int(out_wh[1])
    pr = push_range if isinstance(push_range, (list, tuple)) else (push_range, push_range)
    z = max(float(v) for v in pr) * float(crop_zoom); cover = max(W / pw, H / ph)
    vis_w, vis_h = W / (cover * z), H / (cover * z)                    # visible source crop (plate px) at peak push
    ax = dict(x=W / vis_w, y=H / vis_h); ratio = max(ax.values())
    label = name or (Path(str(plate)).name if isinstance(plate, (str, Path)) else f"plate {pw}x{ph}")
    rep = dict(check="pixel_density", plate=str(plate) if isinstance(plate, (str, Path)) else None, plate_wh=[pw, ph], out_wh=[W, H],
               push_max=round(z / float(crop_zoom), 6), crop_zoom=float(crop_zoom), cover_scale=round(cover, 4),
               visible_src_wh=[round(vis_w, 1), round(vis_h, 1)], ratio=round(ratio, 3), ratio_x=round(ax["x"], 3), ratio_y=round(ax["y"], 3),
               max_ratio=max_ratio)
    ok = ratio <= max_ratio + 1e-9; rep["pass"] = bool(ok)
    msg = (f"{label}: {ratio:.3f} output px per source px > {max_ratio} (plate {pw}x{ph} -> {W}x{H}, cover-fit {cover:.3f}x "
           f"x peak push/crop {z:.3f}x; visible source only {vis_w:.0f}x{vis_h:.0f} px) -- needs a native (same-aspect) >= "
           f"{math.ceil(pw * ratio / max_ratio)}x{math.ceil(ph * ratio / max_ratio)} plate or less push")
    return _emit(ok, msg, mode, rep)

def check_crop_zoom(zoom, max_zoom=MAX_ZOOM, mode="refuse", plate_wh=None, out_wh=(1080, 1920), density=True, max_ratio=MAX_PX_DENSITY):
    """zoom is relative to cover-fit of plate_wh. With plate_wh (the real full-plate size) the pixel-density check also runs
    (refuses > 1.5 output px per source px in refuse mode); its report is attached as rep['pixel_density']."""
    z = float(max(zoom) if isinstance(zoom, (list, tuple)) else zoom)
    rep = dict(check="crop_zoom", zoom=z, max_zoom=max_zoom)
    if plate_wh: rep["output_px_per_plate_px"] = round(output_px_per_plate_px(plate_wh, out_wh, z), 3)
    rep = _emit(z <= max_zoom + 1e-9, f"zoom {z:.3f}x of native fill exceeds {max_zoom}x (plate is upscaled and goes soft)", mode, rep)
    if plate_wh and density: rep["pixel_density"] = check_pixel_density(tuple(plate_wh), out_wh, (z, z), max_ratio=max_ratio, mode=mode)
    return rep

def lapvar(img, rect):
    x0, y0, x1, y1 = [int(v) for v in rect[:4]]; g = img[y0:y1, x0:x1]
    if g.ndim == 3: g = cv2.cvtColor(g, cv2.COLOR_RGB2GRAY)
    return float(cv2.Laplacian(g.astype(np.float64), cv2.CV_64F).var()) if g.size else 0.0

def check_fire_sharpness(plate, rects, zoom=1.0, min_lapvar=FIRE_MIN_LAPVAR, max_zoom=FIRE_MAX_ZOOM, mode="refuse"):
    """plate: RGB uint8 at NATIVE res (never a resampled frame). rects: [(x0,y0,x1,y1), ...] fire/torch rects."""
    z = float(max(zoom) if isinstance(zoom, (list, tuple)) else zoom)
    lv = [round(lapvar(plate, r), 1) for r in rects]; soft = [i for i, v in enumerate(lv) if v < min_lapvar]
    rep = dict(check="fire_sharpness", zoom=z, lapvar=lv, min_lapvar=min_lapvar, soft_rects=soft, max_zoom=max_zoom)
    msgs = []
    if z > max_zoom + 1e-9: msgs.append(f"fire at {z:.3f}x zoom (> {max_zoom}x): torch_v1c / fire reflections run only on native-resolution fire")
    if soft: msgs.append(f"soft fire rects {soft} (Laplacian var {[lv[i] for i in soft]} < {min_lapvar})")
    return _emit(not msgs, "; ".join(msgs) or "ok", mode, rep)

def check_shot(cfg, plate=None, mode="refuse", out_wh=(1080, 1920)):
    """cfg keys used: push [z0,z1] (zoom rel. native fill), crop_zoom (optional extra), fire.torch rects, plate (path).
    Runs crop_zoom, pixel_density (real plate size: the array if given, else the cfg plate file) and fire sharpness."""
    z = max(float(v) for v in cfg.get("push", (1.0, 1.0))) * float(cfg.get("crop_zoom", 1.0))
    wh = (plate.shape[1], plate.shape[0]) if plate is not None else None
    wv = waiver_for(cfg)
    zmode = mode
    if wv and abs(z - wv["zoom"]) < 1e-6:
        print(f"WARNING guardrail: {cfg.get('name')} zoom {z}x > {MAX_ZOOM}x WAIVED ({wv['reason']})", file=sys.stderr); zmode = "warn"
    reps = [check_crop_zoom(z, mode=zmode, plate_wh=wh, out_wh=out_wh, density=False)]
    if wv and abs(z - wv["zoom"]) < 1e-6: reps[0]["waived"] = wv["reason"]
    # ---- pixel density (EIC ruling 2026-10-30), measured on the real plate
    src = wh or (cfg.get("plate") if cfg.get("plate") and Path(str(cfg["plate"])).is_file() else None)
    name = cfg.get("name") or (Path(str(cfg.get("plate"))).name if cfg.get("plate") else "shot")
    if src is None:
        reps.append(_emit(False, f"{name}: pixel density not measurable (no plate array and no readable cfg plate file)", mode,
                          dict(check="pixel_density", ratio=None, **{"pass": False})))
    else:
        d = check_pixel_density(src, out_wh, (z, z), mode="measure", name=name)
        dw = wv if (wv and abs(z - wv["zoom"]) < 1e-6 and tuple(int(v) for v in out_wh) == tuple(wv["out_wh"])
                    and abs(d["ratio"] - wv["density"]) < 1e-3) else None
        if not d["pass"] and dw:
            print(f"WARNING guardrail: {name} pixel density {d['ratio']} > {MAX_PX_DENSITY} WAIVED ({dw['reason']}; density extension, "
                  f"exact shot only)", file=sys.stderr); d["waived"] = dw["reason"]
        elif not d["pass"] and mode == "refuse": raise GuardrailError(d["msg"])
        elif not d["pass"]: print("WARNING guardrail: " + d["msg"], file=sys.stderr)
        reps.append(d)
    if cfg.get("fire") and plate is not None: reps.append(check_fire_sharpness(plate, cfg["fire"].get("torch", []), z, mode=mode))
    return reps

if __name__ == "__main__":
    # python guardrails.py <shot_cfg.json> [--size WxH] [--warn-only]   -> report; exits 3 on any refusal (default: refuse)
    a = sys.argv[1:]; warn = "--warn-only" in a; a = [x for x in a if x != "--warn-only"]
    size = (1080, 1920)
    if "--size" in a: i = a.index("--size"); size = tuple(int(v) for v in a[i + 1].lower().split("x")); del a[i:i + 2]
    c = json.load(open(a[0])); P = cv2.cvtColor(cv2.imread(c["plate"]), cv2.COLOR_BGR2RGB) if c.get("plate") else None
    try: print(json.dumps(check_shot(c, P, mode="warn" if warn else "refuse", out_wh=size), indent=1))
    except GuardrailError as e: print(f"GUARDRAIL REFUSED: {e}", file=sys.stderr); sys.exit(3)
