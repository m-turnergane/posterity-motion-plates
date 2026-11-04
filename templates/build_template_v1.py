#!/workspace/mpvenv/bin/python
"""POSTERITY build template v1 (box) -- generic rough-cut builder for any size (default 1080x1920 Shorts; 1920x1080 long-form).

Based on standalones/jianwen/edit/build_rough_jianwen_v2.py (newest + cleanest house build: prepare_cover / StablePush cam /
Chronicle Reveal / ASS captions ceil-floor + cut-straddle check / smoke_v2 by path + zero-motion proof / -14 LUFS loudness loop),
with refuse-to-overwrite + plate-mismatch guards borrowed from day21/atahualpa/edit/build_rough_atahualpa_v2c.py.
Episode-specific parts (VO word grid, md5 pins, slot rules, LEGEND) are replaced by two input files:
  --manifest  JSON or CSV, one row per plate (plate_id, scene_id, shot_ids, prompt, aspect, target_resolution, expected_filename, refs, notes)
  --timeline  JSON shot list (+ optional title / captions / audio); shots find their plate through the manifest's shot_ids
Fixes vs. every earlier build script:
  1. content-hash shot cache: clips/{sid}.mp4 is reused ONLY when clips/{sid}.key matches md5(plate) + md5(resolved segment JSON) +
     md5(fx/smoke config) + md5(effect engine files) (+ size/fps/encoder/template md5). A mismatched clip is renamed
     {sid}.stale-<YYYYmmdd-HHMMSS>.mp4 (never deleted) and re-rendered. Same rule for audio/mix.wav (mix.key) and phone-QC stills.
  2. --size WxH: every dimension (cover/push/crop, caption PlayRes/margins/font, title band + safe area, phone QC, preview) derives from it.
     guardrails.check_crop_zoom (max 1.5x) is called for every shot and REFUSES before anything renders.
  3. pixel density (EIC ruling 2026-10-30): guardrails.check_pixel_density refuses any shot above 1.5 output px per REAL source px
     (cover-fit x peak push x crop, both axes; 16:9 and 9:16). All offending shots are listed at planning, before any render.
  4. depth_v1 (LOCKED 2026-10-30 6:16pm ET) as an OPT-IN per-shot layer (OFF by default): a shot with "depth" renders through
     depth_v1.DepthShot's single-transform path INSTEAD of the template push (never two stacked camera transforms); fx / smoke /
     dust_v1 / water_v1 compose as plate_fx inside each layer's one matrix (their own cameras are never called). Density is
     checked per layer (gate = the larger layer scale). Planning WARNs on back-to-back depth shots touching a character plate.
Nothing in this file edits a locked file: smoke_v2.py / the fx module are imported BY PATH and md5-checked.
Run with /workspace/mpvenv/bin/python FROM THIS FILE (multiprocessing; never pipe it through stdin).
"""
import argparse, csv, hashlib, importlib.util, json, math, os, shutil, subprocess, sys, time
from pathlib import Path
import multiprocessing as mp
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent                       # .../posterity/motion/templates
MOTION = HERE.parent                                         # .../posterity/motion
ROOT = Path(os.environ.get("POSTERITY_ROOT", str(MOTION.parent)))   # .../posterity (no hard-coded /workspace)
GUARDRAILS = MOTION / "guardrails.py"
SMOKE_V2_DEFAULT = ROOT / "engine-rnd" / "smoke" / "smoke_v2.py"; SMOKE_V2_MD5 = "80bb28695757f7568b005e8ba8327bde"   # LOCKED
DEPTH_V1_DEFAULT = ROOT / "engine-rnd" / "depth" / "depth_v1.py"; DEPTH_V1_MD5 = "dd5cd5011c88b3b56528b96fedae5494"   # LOCKED 2026-10-30 6:16pm ET
PLATE_FX_ENGINES = {"dust": (ROOT / "engine-rnd" / "dust" / "dust_v1.py", "c0ad4ef55357ddd47ca73b9a93ffc760", "DustShot"),    # LOCKED; depth shots only
                    "water": (ROOT / "engine-rnd" / "water" / "water_v1.py", "811734e9e3919bddbe3ef22022203d5f", "WaterShot")}
FONT_DIR = "/usr/share/fonts/truetype/sand-box/custom/Source Serif Pro/"
MANIFEST_FIELDS = ["plate_id", "scene_id", "shot_ids", "prompt", "aspect", "target_resolution", "expected_filename", "refs", "notes",
                   "plate_type", "scene_action", "depth_ok_reason"]   # optional: plate_type 'character' feeds the back-to-back depth WARN
SHOT_KEYS = {"id", "plate_id", "seconds", "frames", "anchor", "push", "crop", "smoke", "fx", "depth", "dust", "water",
             "character", "plate_type", "scene_action", "depth_ok_reason", "note", "notes"}
REQUIRED_FIELDS = ["plate_id", "shot_ids", "expected_filename"]

def md5f(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def md5j(o): return hashlib.md5(json.dumps(o, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
def load_by_path(name, path):
    sp = importlib.util.spec_from_file_location(name, str(path)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
TEMPLATE_MD5 = md5f(__file__)

# ------------------------------------------------------------------ args
def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--manifest", required=True, help="plate manifest (.json or .csv), one row per plate")
    ap.add_argument("--plates-dir", default=None, help="where expected_filename lives (default: the manifest's folder)")
    ap.add_argument("--timeline", required=True, help="timeline JSON (shots / title / captions / audio); relative paths resolve from its folder")
    ap.add_argument("--size", default="1080x1920", help="output WxH (1080x1920 Shorts default; 1920x1080 long-form)")
    ap.add_argument("--fps", type=int, default=None, help="override the timeline fps (default 30)")
    ap.add_argument("--tag", default="v1", help="names the master/preview; masters are never overwritten")
    ap.add_argument("--build-dir", required=True, help="scratch: clips/ audio/ qc/ live here (re-used SAFELY via .key sidecars)")
    ap.add_argument("--out-dir", default=None, help="master + preview folder (default: <build-dir>/out)")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--smoke-engine", default=str(SMOKE_V2_DEFAULT), help="locked smoke_v2.py (md5-checked)")
    ap.add_argument("--depth-engine", default=str(DEPTH_V1_DEFAULT), help="locked depth_v1.py (md5-checked; only loaded when a shot opts in to depth)")
    ap.add_argument("--fx-module", default=None, help="optional per-plate fx module exposing PlateFX(plate_path, seed) (e.g. an episode's fx_*.py); imported by path, never edited")
    ap.add_argument("--extra-key-files", default="", help="comma list of extra files whose md5 joins every shot key (e.g. a locked preset JSON the fx module reads)")
    ap.add_argument("--proof-every", type=int, default=3, help="smoke zero-motion proof sampled every N frames")
    ap.add_argument("--check", action="store_true", help="resolve manifest + timeline + guardrails, print the plan, render nothing")
    ap.add_argument("--clips-only", action="store_true", help="render/refresh clips (+ phone QC), no audio, no master")
    ap.add_argument("--audio-only", action="store_true")
    ap.add_argument("--no-phone-qc", action="store_true")
    ap.add_argument("--min-free-gib", type=float, default=4.0)
    return ap.parse_args(argv)

# ------------------------------------------------------------------ geometry derived from --size (all former 1080x1920 constants)
def parse_size(s):
    try: w, h = [int(v) for v in s.lower().split("x")]
    except Exception: raise SystemExit(f"--size must be WxH, got {s!r}")
    if w < 16 or h < 16 or w % 2 or h % 2: raise SystemExit(f"--size {w}x{h}: both sides must be even and >= 16 (yuv420p)")
    return w, h
def derive_geometry(W, H):
    portrait = H >= W; U = min(W, H) / 1080.0          # U: house pixel constants were authored at 1080 short side
    if portrait:   # Shorts / Reels: UI bands top ~11.5 %, bottom ~20 % (house 400 px of 1920), 60 px (of 1080) sides
        safe = dict(x0=round(W * 60 / 1080), y0=round(H * 220 / 1920), x1=W - round(W * 60 / 1080), y1=H - round(H * 384 / 1920))
        cap = dict(font=54 * U, outline=4 * U, shadow=2 * U, ml=80 * U, mr=80 * U, mv=400 * H / 1920, maxc=24)
        title = dict(top_pct=16.0, width_pct=94.0, max_line_w=0.92 * W)
        phone = (360, int(round(360 * H / W / 2)) * 2)          # 360 wide (360x640 for 9:16)
        preview = (720, int(round(720 * H / W / 2)) * 2)
    else:          # long-form 16:9: EBU title-safe 10 % / action-safe 5 %
        safe = dict(x0=round(W * 0.10), y0=round(H * 0.10), x1=W - round(W * 0.10), y1=H - round(H * 0.10))
        cap = dict(font=54 * U, outline=4 * U, shadow=2 * U, ml=W * 0.10, mr=W * 0.10, mv=H * 0.09, maxc=42)
        title = dict(top_pct=24.0, width_pct=None, max_line_w=0.80 * W)   # band (269 px @1080) centred at 24 % -> top edge ~11.5 %, inside title-safe
        phone = (int(round(360 * W / H / 2)) * 2, 360)          # landscape equivalent: 360 short side (640x360 for 16:9)
        preview = (int(round(720 * W / H / 2)) * 2, 720)
    return dict(W=W, H=H, portrait=portrait, U=U, safe=safe, cap=cap, title=title, phone=phone, preview=preview)

# ------------------------------------------------------------------ manifest ingest (JSON or CSV) -> plates resolved by expected_filename
def _listish(v):
    if v is None: return []
    if isinstance(v, list): return [str(x).strip() for x in v if str(x).strip()]
    return [x.strip() for x in str(v).replace("|", ";").split(";") if x.strip()]
def load_manifest(path, plates_dir=None):
    path = Path(path)
    if not path.is_file(): raise SystemExit(f"MANIFEST: {path} not found")
    if path.suffix.lower() == ".csv":
        with open(path, newline="") as f: rows = [r for r in csv.DictReader(f) if any((v or "").strip() for v in r.values())]
        meta = {}
    elif path.suffix.lower() == ".json":
        d = json.load(open(path)); rows = d["plates"] if isinstance(d, dict) else d; meta = {k: v for k, v in d.items() if k != "plates"} if isinstance(d, dict) else {}
    else: raise SystemExit(f"MANIFEST: {path} must be .json or .csv")
    base = Path(plates_dir) if plates_dir else Path(meta.get("plates_dir", "")) if meta.get("plates_dir") else path.parent
    if not base.is_absolute(): base = (path.parent / base).resolve()
    errs, out, seen_id, seen_fn, shot_owner = [], [], {}, {}, {}
    for i, r in enumerate(rows):
        r = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in r.items() if k}
        n = f"row {i + 1}" + (f" ({r.get('plate_id')})" if r.get("plate_id") else "")
        unknown = sorted(set(r) - set(MANIFEST_FIELDS))
        if unknown: errs.append(f"{n}: unknown field(s) {unknown}")
        for k in REQUIRED_FIELDS:
            if not r.get(k): errs.append(f"{n}: '{k}' is empty")
        fn = str(r.get("expected_filename") or "")
        if fn and (Path(fn).is_absolute() or ".." in Path(fn).parts): errs.append(f"{n}: expected_filename must be relative to the plates dir, got {fn!r}")
        row = {k: r.get(k, "") for k in MANIFEST_FIELDS}; row["shot_ids"] = _listish(r.get("shot_ids")); row["refs"] = _listish(r.get("refs"))
        pid = row["plate_id"]
        if pid in seen_id: errs.append(f"{n}: duplicate plate_id {pid!r} (also row {seen_id[pid]})")
        if fn in seen_fn: errs.append(f"{n}: duplicate expected_filename {fn!r} (also row {seen_fn[fn]}) -- one row per plate")
        seen_id[pid] = seen_fn[fn] = i + 1
        for sid in row["shot_ids"]:
            if sid in shot_owner: errs.append(f"{n}: shot {sid!r} already belongs to plate {shot_owner[sid]!r}")
            shot_owner[sid] = pid
        a = str(row.get("aspect") or ""); tr = str(row.get("target_resolution") or "")
        if a and tr:
            try:
                aw, ah = [float(x) for x in a.split(":")]; tw, th = [int(x) for x in tr.lower().split("x")]
                if abs(aw / ah - tw / th) > 0.01: errs.append(f"{n}: aspect {a} != target_resolution {tr}")
            except Exception: errs.append(f"{n}: unparseable aspect {a!r} / target_resolution {tr!r}")
        row["path"] = str(base / fn) if fn else ""; row["_row"] = i + 1; out.append(row)
    if errs: raise SystemExit("MANIFEST INVALID (" + str(path) + "):\n   " + "\n   ".join(errs))
    return out, base
def require_plate_files(rows, base, needed_ids):
    miss = [r for r in rows if r["plate_id"] in needed_ids and not Path(r["path"]).is_file()]
    if miss:
        lines = [f"{r['plate_id']:10} shots {','.join(r['shot_ids']):14} expected {r['expected_filename']}" for r in miss]
        print(f"REFUSING: {len(miss)}/{len(needed_ids)} manifest plate file(s) missing in {base} -> nothing rendered:", file=sys.stderr)
        for l in lines: print("   missing", l, file=sys.stderr)
        sys.exit(2)

# ------------------------------------------------------------------ globals filled by setup() (inherited by fork workers)
A = G = None; W = H = FPS = None; UP = 2; SEGS = []; SEG = {}; CR = None; BUILD = CLIPS = AUD = QC = None
SM = FX = GR = DP = None; PFX_MOD = {}; ENGINE_MD5 = {}; TEMPLATE_CAM_CALLS = [0]; EFFECT_CAM_CALLS = [0]; RUN_TS = time.strftime("%Y%m%d-%H%M%S"); FLAGS = []
ENC_INTER = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "8", "-preset", "fast"]
ENC_FINAL = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "medium", "-profile:v", "high"]

def crop_box(plate_size, c):   # relative crop (frac of the plate frame, plate aspect kept) -> pixel box, clamped inside the plate
    pw, ph = plate_size; cw, ch = pw * c["frac"], ph * c["frac"]; cx, cy = c["center"][0] * pw, c["center"][1] * ph
    l = min(max(cx - cw / 2, 0), pw - cw); t = min(max(cy - ch / 2, 0), ph - ch)
    return (int(round(l)), int(round(t)), int(round(l + cw)), int(round(t + ch)))

def setup(args):
    global A, G, W, H, FPS, SEGS, SEG, CR, BUILD, CLIPS, AUD, QC, SM, FX, GR, DP, ENGINE_MD5, TL, TLDIR
    A = args; W, H = parse_size(args.size); G = derive_geometry(W, H)
    GR = load_by_path("posterity_guardrails", GUARDRAILS)
    TLP = Path(args.timeline); TLDIR = TLP.resolve().parent; TL = json.load(open(TLP)); FPS = int(args.fps or TL.get("fps", 30))
    rows, base = load_manifest(args.manifest, args.plates_dir)
    by_shot = {sid: r for r in rows for sid in r["shot_ids"]}; by_id = {r["plate_id"]: r for r in rows}
    shots = TL.get("shots") or []; errs = []
    if not shots: raise SystemExit("TIMELINE: no shots")
    ids = [s.get("id") for s in shots]
    if len(set(ids)) != len(ids) or not all(ids): raise SystemExit(f"TIMELINE: shot ids must be unique and non-empty: {ids}")
    for s in shots:
        r = by_id.get(s["plate_id"]) if s.get("plate_id") else by_shot.get(s["id"])
        if r is None: errs.append(f"shot {s['id']}: no manifest row lists it in shot_ids" + (f" (plate_id {s['plate_id']!r} unknown)" if s.get("plate_id") else ""))
        elif s.get("plate_id") and s["id"] not in r["shot_ids"]: errs.append(f"shot {s['id']}: plate_id {s['plate_id']} does not list it in shot_ids")
        else: s["_row"] = r
        if not (("seconds" in s) ^ ("frames" in s)): errs.append(f"shot {s['id']}: give exactly one of seconds / frames")
        bad = sorted(k for k in s if k not in SHOT_KEYS and not k.startswith("_"))
        if bad: FLAGS.append(f"FLAG shot {s['id']}: unknown key(s) {bad} (ignored)")
    unused = [r["plate_id"] for r in rows if not any(sid in ids for sid in r["shot_ids"])]
    if unused: FLAGS.append(f"FLAG manifest plates not used by the timeline: {unused}")
    orphan = [sid for sid in by_shot if sid not in ids]
    if orphan: FLAGS.append(f"FLAG manifest shot_ids not in the timeline: {orphan}")
    if errs: raise SystemExit("TIMELINE/MANIFEST MISMATCH:\n   " + "\n   ".join(errs))
    require_plate_files(rows, base, {s["_row"]["plate_id"] for s in shots})
    # ---- engines by path (locked; md5-checked) -> part of every shot key
    if any(s.get("smoke") for s in shots):
        se = Path(args.smoke_engine)
        if not se.is_file(): raise SystemExit(f"smoke engine not found: {se}")
        if se.resolve() == SMOKE_V2_DEFAULT.resolve() and md5f(se) != SMOKE_V2_MD5: raise SystemExit(f"locked smoke_v2.py changed: {md5f(se)} != {SMOKE_V2_MD5}")
        SM = load_by_path("smoke_v2_locked", se); ENGINE_MD5["smoke_engine"] = md5f(se)
    if args.fx_module:
        FX = load_by_path("plate_fx", args.fx_module); ENGINE_MD5["fx_module"] = md5f(args.fx_module)
        if getattr(FX, "_ENG", None) and Path(FX._ENG).is_file(): ENGINE_MD5["fx_module_engine"] = md5f(FX._ENG)
    for p in [x for x in args.extra_key_files.split(",") if x.strip()]: ENGINE_MD5["extra:" + Path(p).name] = md5f(p)
    if any(depth_on(s) for s in shots):   # depth is OPT-IN: the locked engine is only loaded when a shot asks for it
        de = Path(args.depth_engine)
        if not de.is_file(): raise SystemExit(f"depth engine not found: {de}")
        if de.resolve() == DEPTH_V1_DEFAULT.resolve() and md5f(de) != DEPTH_V1_MD5: raise SystemExit(f"locked depth_v1.py changed: {md5f(de)} != {DEPTH_V1_MD5}")
        DP = load_by_path("depth_v1_locked", de); ENGINE_MD5["depth_engine"] = md5f(de)
        mp_ = getattr(DP, "MODEL", None); ENGINE_MD5["depth_model"] = f"{Path(mp_).name}:{Path(mp_).stat().st_size}" if mp_ and Path(mp_).is_file() else None
    for kind, (pth, m5, _) in PLATE_FX_ENGINES.items():
        if any(s.get(kind) for s in shots):
            if not pth.is_file(): raise SystemExit(f"{kind} engine not found: {pth}")
            if md5f(pth) != m5: raise SystemExit(f"locked {pth.name} changed: {md5f(pth)} != {m5}")
            m = load_by_path(f"{kind}_v1_locked", pth); ENGINE_MD5[f"{kind}_engine"] = m5
            if hasattr(m, "F3") and hasattr(m.F3, "push_frame"):   # the effect's own camera must never run inside a depth shot: count it
                _orig = m.F3.push_frame
                def _trap(*a, _o=_orig, **k): EFFECT_CAM_CALLS[0] += 1; return _o(*a, **k)
                m.F3.push_frame = _trap
            PFX_MOD[kind] = m
    # ---- segments
    f0 = 0; SEGS = []
    for s in shots:
        r = s["_row"]; n = int(s["frames"]) if "frames" in s else int(round(float(s["seconds"]) * FPS))
        if n < 2: raise SystemExit(f"shot {s['id']}: {n} frames (< 2)")
        z = s.get("push", [1.0, 1.06]); smk = s.get("smoke")
        seg = dict(id=s["id"], plate_id=r["plate_id"], scene_id=r["scene_id"], plate=r["path"], f0=f0, f1=f0 + n, frames=n,
                   anchor=list(s.get("anchor", [0.5, 0.5])), z_start=float(z[0]), z_end=float(z[1]), crop_rel=s.get("crop"), crop=None,
                   smoke=str((TLDIR / smk).resolve()) if smk else None, fx=bool(s.get("fx", True)) and FX is not None)
        seg["character"] = bool(s.get("character")) or str(s.get("plate_type") or r.get("plate_type") or "").strip().lower() == "character"
        seg["scene_action"] = s.get("scene_action") or r.get("scene_action") or None
        seg["depth_ok_reason"] = s.get("depth_ok_reason") or r.get("depth_ok_reason") or None
        seg["depth"] = resolve_depth(s, seg) if depth_on(s) else None          # OFF unless the shot explicitly opts in
        seg["plate_fx_cfgs"] = {k: resolve_plate_fx_cfg(s, seg, k) for k in PLATE_FX_ENGINES if s.get(k)} or None
        if seg["plate_fx_cfgs"] and not seg["depth"]:
            raise SystemExit(f"shot {s['id']}: dust/water in the template compose only inside a depth shot (flat-shot dust/water: use the engine's own render)")
        if seg["depth"]:
            if seg["crop_rel"]: raise SystemExit(f"shot {s['id']}: template 'crop' + depth -> put the window in the depth config 'crop' {{'16x9'|'9x16': [x0,y0,x1,y1]}}")
            dz = seg["depth"]["camera"]["push"]; seg["z_start"], seg["z_end"] = float(dz[0]), float(dz[1])   # reported only: the template push is NOT applied
        seg["start"], seg["end"], seg["duration"] = f0 / FPS, (f0 + n) / FPS, n / FPS; SEGS.append(seg); f0 += n
    for k, s in enumerate(SEGS):   # smoke clock: per contiguous same-plate run (house rule, Jianwen v2)
        s["run_f0"] = SEGS[k - 1]["run_f0"] if k and SEGS[k - 1]["plate"] == s["plate"] else s["f0"]
    SEG = {s["id"]: s for s in SEGS}
    for s in SEGS:   # preflight: a bad / foreign smoke config refuses here (and in --check), not inside a worker
        if s["smoke"]:
            if not Path(s["smoke"]).is_file(): raise SystemExit(f"{s['id']}: smoke config missing: {s['smoke']}")
            smoke_cfg(s)
    # ---- per-shot plate checks + guardrails (refuse > 1.5x zoom AND > 1.5 output px / source px, before anything renders)
    gerr = []; derr = []
    for s in SEGS:
        pw, ph = Image.open(s["plate"]).size; r = SEG[s["id"]]; tr = by_id[s["plate_id"]]["target_resolution"]
        if tr and tr.lower() != f"{pw}x{ph}": FLAGS.append(f"FLAG {s['id']}: plate is {pw}x{ph}, manifest target_resolution {tr}")
        if s["depth"]:
            ge, de = depth_guard(s, (pw, ph)); gerr += ge; derr += de; continue
        crop_zoom = 1.0
        if s["crop_rel"]:
            c = s["crop_rel"]; assert 0 < c["frac"] <= 1, s["id"]; s["crop"] = crop_box((pw, ph), c); crop_zoom = 1.0 / c["frac"]
        cw, ch = (s["crop"][2] - s["crop"][0], s["crop"][3] - s["crop"][1]) if s["crop"] else (pw, ph)
        vis = min((cw / ch) / (W / H), (W / H) / (cw / ch))   # share of the source the cover-fit keeps (aspect mismatch)
        if vis < 0.75: FLAGS.append(f"FLAG {s['id']}: source {cw}x{ch} vs output {W}x{H} -> cover-fit keeps only {vis:.0%} of the frame (wrong-aspect plate?)")
        zoom = max(s["z_start"], s["z_end"]) * crop_zoom
        try:   # zoom rel. cover-fit of the FULL plate (crop_zoom already in zoom); density checked separately below
            rep = GR.check_crop_zoom(zoom, mode="refuse", plate_wh=(pw, ph), out_wh=(W, H), density=False); s["guard"] = rep
        except GR.GuardrailError as e: gerr.append(f"{s['id']}: {e}")
        # pixel density on the REAL plate file size: cover-fit of the visible source (crop) x peak push, both axes
        d = GR.check_pixel_density(s["plate"], (W, H), (s["z_start"], s["z_end"]), crop_zoom=crop_zoom, mode="measure",
                                   name=f"{s['id']} ({s['plate_id']} {Path(s['plate']).name})")
        s["density"] = d
        if not d["pass"]: derr.append(f"{s['id']}: {d['msg']}")
        up = max(W / cw, H / ch) * max(s["z_start"], s["z_end"])
        if up > 1.0 / 0.70: FLAGS.append(f"FLAG {s['id']}: source upscale {up:.2f}x at peak push (> 1.43x may read soft)")
    if gerr or derr:
        msg = []
        if gerr: msg.append(f"GUARDRAIL REFUSED (max crop/push zoom {GR.MAX_ZOOM}x): {len(gerr)} shot(s)\n   " + "\n   ".join(gerr))
        if derr: msg.append(f"GUARDRAIL REFUSED (pixel density > {GR.MAX_PX_DENSITY} output px per source px, EIC 2026-10-30): "
                            f"{len(derr)}/{len(SEGS)} shot(s) at {W}x{H}\n   " + "\n   ".join(derr))
        raise SystemExit("\n".join(msg))
    depth_flags()
    # ---- title (Chronicle Reveal) sized from --size
    t = TL.get("title")
    if t:
        top = float(t.get("top_pct", G["title"]["top_pct"])); s0 = int(t.get("start_f", 8)); x = int(t["exit_f"])
        CR = dict(title=t["text"], fontSize=int(round(t.get("font_px", 78) * G["U"])), color=(243, 237, 224), topPercent=top, offsetX=-16 * G["U"],
                  strokeEnterStart=s0, strokeEnterEnd=s0 + 18, strokeClearStart=x + 9, strokeClearEnd=x + 30,
                  manifestStart=s0 + 6, manifestEnd=s0 + 34, exitStart=x, exitEnd=x + 20, bandHeightPx=269 * G["U"],
                  widthPercent=G["title"]["width_pct"], peakOpacity=0.92, fill="#5A1A18", edge="#3A0E0C", mid="#6E2A1C",
                  scaleFrom=0.92, scaleTo=1.0, exitScaleTo=0.94, settleYPx=4 * G["U"], afterEdgeLagFrames=2,
                  letterSettleFrames=12, trackingEm=0.02, nudgeY=-4 * G["U"], font=t.get("font", "SourceSerifPro-Semibold.ttf"))
        if x <= s0 + 34: raise SystemExit(f"title exit_f {x} must be after start_f + 34 = {s0 + 34}")
    # ---- build dirs
    BUILD = Path(args.build_dir); CLIPS = BUILD / "clips"; AUD = BUILD / "audio"; QC = BUILD / "qc"

# ------------------------------------------------------------------ depth_v1 (opt-in per shot; OFF by default)
def depth_on(s):
    d = s.get("depth"); return d is not None and d is not False and not (isinstance(d, dict) and d.get("enabled") is False)
def _cfg_plate_ok(cfg, cfg_dir, seg, what):
    """a config written for another plate is refused (mattes / zones are plate-specific); the shot's plate is then forced."""
    if cfg.get("plate"):
        cp = Path(cfg["plate"]); cp = cp if cp.is_absolute() else Path(cfg_dir) / cp
        if not cp.is_file() or md5f(cp) != md5f(seg["plate"]): raise SystemExit(f"{seg['id']}: {what} points at another plate ({cfg['plate']})")
    cfg["plate"] = seg["plate"]; return cfg
def resolve_depth(s, seg):
    """'depth': "cfg.json" | {"config": "cfg.json", ...overrides} | {inline: matte/layers/camera/crop/...}. Returns a resolved
    depth_v1 config (plain JSON) that also joins the shot's content-hash key."""
    d = s["depth"]; src = None
    if d is True: raise SystemExit(f"shot {s['id']}: depth: true needs mattes -> give a depth_v1 config path or inline layers")
    if isinstance(d, str): d = {"config": d}
    if not isinstance(d, dict): raise SystemExit(f"shot {s['id']}: depth must be a config path or an object, got {type(d).__name__}")
    d = json.loads(json.dumps(d)); d.pop("enabled", None)
    if d.get("config"):
        src = (TLDIR / d.pop("config")).resolve()
        if not src.is_file(): raise SystemExit(f"shot {s['id']}: depth config missing: {src}")
        base = json.load(open(src)); base = _cfg_plate_ok(base, src.parent, seg, f"depth config {src.name}")
        for k, v in d.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict): base[k] = {**base[k], **v}
            else: base[k] = v
        cfg = base
    else: cfg = _cfg_plate_ok(d, TLDIR, seg, "inline depth config")
    if not cfg.get("layers") or len(cfg["layers"]) < 2: raise SystemExit(f"shot {s['id']}: depth config needs >= 2 layers (far first)")
    cfg["plate"] = seg["plate"]; cfg["name"] = cfg.get("name") or s["id"]; cfg["seconds"] = seg["frames"] / FPS
    cam = dict(cfg.get("camera") or {})
    if "push" not in cam: cam["push"] = list(s.get("push", [1.0, 1.06]))            # the shot push folds INTO the layer matrices
    cfg["camera"] = cam
    for k in ("formats", "note", "notes", "_note"): cfg.pop(k, None)
    cfg["_src"] = str(src) if src else None
    return cfg
def resolve_plate_fx_cfg(s, seg, kind):
    p = (TLDIR / s[kind]).resolve()
    if not p.is_file(): raise SystemExit(f"shot {s['id']}: {kind} config missing: {p}")
    cfg = _cfg_plate_ok(json.load(open(p)), p.parent, seg, f"{kind} config {p.name}"); cfg["_src"] = str(p); return cfg
def get_depth(seg):
    k = ("depth", seg["id"])
    if k not in _CACHE:   # built at planning (DA2 depth cached per plate md5 by depth_v1); fork workers inherit it
        _CACHE[k] = DP.DepthShot({kk: v for kk, v in seg["depth"].items() if kk != "_src"})
    return _CACHE[k]
def get_plate_fx(seg):
    k = ("pfx", seg["id"])
    if k not in _CACHE:
        _CACHE[k] = [(kind, getattr(PFX_MOD[kind], PLATE_FX_ENGINES[kind][2])({kk: v for kk, v in cfg.items() if kk != "_src"}))
                     for kind, cfg in (seg["plate_fx_cfgs"] or {}).items()]
    return _CACHE[k]
def depth_guard(s, plate_wh):
    """zoom + pixel density PER LAYER (layer scale = cover x overscan x layer zoom x depth crop); the gate is the larger one."""
    sh = get_depth(s); n = s["frames"]; o = sh.overscan((W, H), n); _, _, cz = sh.out_frame((W, H)); ge, de = [], []
    per = []
    for k, L in enumerate(sh.layers):
        zk = max(sh.layer_params(k, e)[0] for e in (0.0, 1.0))
        d = GR.check_pixel_density(s["plate"], (W, H), (1.0, zk * o), crop_zoom=cz, mode="measure", name=f"{s['id']} layer {L['name']} ({s['plate_id']} {Path(s['plate']).name})")
        per.append(dict(layer=L["name"], zoom=round(zk * o * cz, 4), density=d["ratio"], pass_=d["pass"], msg=d.get("msg")))
    worst = max(per, key=lambda x: x["density"]); zmax = max(x["zoom"] for x in per)
    try: s["guard"] = GR.check_crop_zoom(zmax, mode="refuse", plate_wh=plate_wh, out_wh=(W, H), density=False)
    except GR.GuardrailError as e: ge.append(f"{s['id']} (depth): {e}")
    s["density"] = dict(ratio=worst["density"], pass_=worst["pass_"], gate_layer=worst["layer"], per_layer=[{k: v for k, v in x.items() if k != "msg"} for x in per])
    s["depth_overscan"] = round(o, 5)
    if not worst["pass_"]: de.append(f"{s['id']} (depth, larger layer scale = {worst['layer']}): {worst['msg']}")
    return ge, de
def depth_flags():
    """owner rule 2026-10-30: depth is for motion / action plates; never on back-to-back character plates (WARN, not a refusal)."""
    for a, b in zip(SEGS, SEGS[1:]):
        if a["depth"] and b["depth"] and (a["character"] or b["character"]):
            who = [x["id"] for x in (a, b) if x["character"]]
            FLAGS.append(f"WARN depth back-to-back on character plate(s): {a['id']} -> {b['id']} (character: {who}) -- owner rule: never depth on "
                         f"back-to-back character plates; keep one flat (candle / smoke / dust / torch / water)")
    for s in SEGS:
        if s["depth"] and not (s["scene_action"] or s["depth_ok_reason"]):
            FLAGS.append(f"WARN depth on {s['id']} without scene_action / depth_ok_reason (depth is for motion/action plates: say why)")
        if s["depth"] and s["fx"] and getattr(get_fx(s), "par", None):
            FLAGS.append(f"FLAG {s['id']}: fx module has its own parallax ('par'); inside depth it is frozen (u=0), depth_v1 is the only camera")
    nd = sum(1 for s in SEGS if s["depth"])
    if nd and nd * 3 > len(SEGS) + 2:
        FLAGS.append(f"FLAG depth on {nd}/{len(SEGS)} shots (loose ceiling ~1 in 3; primary test is motion/action)")

# ------------------------------------------------------------------ house picture helpers (Germanicus v5b via Jianwen v2; W/H from --size)
def prepare_cover(im, up=UP):
    im = im.convert("RGB"); tw, th = W * up, H * up; sw, sh = im.size
    sc = max(tw / sw, th / sh); nw, nh = int(math.ceil(sw * sc)), int(math.ceil(sh * sc))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS); l, t = (nw - tw) // 2, (nh - th) // 2
    return im.crop((l, t, l + tw, t + th))
def cam(seg, u, t):
    z0, z = seg["z_start"], seg["z_end"]; s = z0 * (z / z0) ** u; ax, ay = seg["anchor"]
    cx = ax * W * (1 - 1 / s) + W / (2 * s); cy = ay * H * (1 - 1 / s) + H / (2 * s); hw, hh = W / (2 * s), H / (2 * s)
    return s, min(max(cx, hw), W - hw), min(max(cy, hh), H - hh)
def cam_frame(base, seg, u, t):
    TEMPLATE_CAM_CALLS[0] += 1
    bw, bh = base.size; s, cx, cy = cam(seg, u, t); k = bw / W; ww, wh = bw / s, bh / s; l, tp = cx * k - ww / 2, cy * k - wh / 2
    big = base.transform((W * 2, H * 2), Image.Transform.AFFINE, (ww / (2 * W), 0, l, 0, wh / (2 * H), tp), resample=Image.Resampling.BICUBIC)
    return Image.fromarray(cv2.resize(np.asarray(big), (W, H), interpolation=cv2.INTER_AREA))

# ------------------------------------------------------------------ Chronicle Reveal (Jianwen v2 maths; px constants x U, band/width from --size)
TITLE_LINE_H = 0.84
def cubic_bezier(x1, y1, x2, y2):
    def bez(t, a, b): return 3 * a * t * (1 - t) ** 2 + 3 * b * t * t * (1 - t) + t ** 3
    def f(x):
        if x <= 0: return 0.0
        if x >= 1: return 1.0
        lo, hi = 0.0, 1.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if bez(mid, x1, x2) < x: lo = mid
            else: hi = mid
        return bez((lo + hi) / 2, y1, y2)
    return f
E_DRAG = cubic_bezier(0.33, 0.0, 0.2, 1); E_IN = cubic_bezier(0.22, 1, 0.36, 1); E_OUT = cubic_bezier(0.4, 0, 0.2, 1)
LIN = lambda x: min(max(x, 0.0), 1.0)
def interp(f, a, b, v0, v1, ease=LIN):
    p = (1.0 if f >= b else 0.0) if b <= a else min(max((f - a) / (b - a), 0.0), 1.0)
    return v0 + (v1 - v0) * ease(p)
def hexrgb(h): h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)
def smooth_noise(h, w, cell_y, cell_x, seed):
    rng = np.random.default_rng(seed); gh, gw = max(2, int(h / cell_y) + 3), max(2, int(w / cell_x) + 3)
    g = rng.random((gh, gw)).astype(np.float32)
    return np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.Resampling.BICUBIC), np.float32) / 255.0
_GLYPHS = None; _STRIKE = None
def title_font(): return ImageFont.truetype(FONT_DIR + CR["font"], CR["fontSize"])
def title_lines_w():
    f = title_font(); tr = CR["trackingEm"] * CR["fontSize"]
    return [sum(f.getlength(c) for c in l) + tr * (len(l) - 1) for l in CR["title"].split("\n")]
def strike_wh():
    U = G["U"]; bh = max(8, int(round(CR["bandHeightPx"])))
    bw = int(round(W * CR["widthPercent"] / 100)) if CR["widthPercent"] else int(round(min(W * 0.94, max(title_lines_w()) * 1.07 + 40 * U)))
    return max(16, bw), bh
def build_strike_rgba():
    U = max(G["U"], 1e-3); bw, bh = strike_wh()
    topY = [78, 62, 71, 55, 68, 48, 60, 52, 70, 58, 65, 50, 72, 56, 64, 54, 75, 60, 70, 66, 80]
    botY = [128, 142, 135, 150, 138, 155, 140, 148, 132, 145, 138, 152, 130, 144, 136, 150, 125, 140, 134, 138, 122]
    def chain(ys):
        m = len(ys); xs_out, ys_out = [], []
        for k in range(1, m):
            x0, x1 = (k - 1) / (m - 1) * 1000, k / (m - 1) * 1000; cx, cy = (x0 + x1) / 2, ys[k - 1]
            for t in np.linspace(0, 1, 40):
                xs_out.append((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1); ys_out.append((1 - t) ** 2 * ys[k - 1] + 2 * (1 - t) * t * cy + t * t * ys[k])
        return np.array(xs_out), np.array(ys_out)
    xt, yt = chain(topY); xb, yb = chain(botY); xs = np.arange(bw) / bw * 1000
    top = np.interp(xs, xt, yt) / 200 * bh; bot = np.interp(xs, xb, yb) / 200 * bh
    yy = np.arange(bh)[:, None].astype(np.float32)
    dy = (smooth_noise(bh, bw, 17 * U, 29 * U, 3) - 0.5) * 2 * 4.4 * U; dx_n = (smooth_noise(bh, bw, 17 * U, 29 * U, 4) - 0.5) * 2 * 3.3 * U; yyd = yy + dy
    fringe = smooth_noise(bh, bw, 3 * U, 9 * U, 7)
    m_top = np.clip((yyd - top[None, :]) / (2.0 * U) + 0.5, 0, 1); m_bot = np.clip((bot[None, :] - yyd) / (2.0 * U) + 0.5, 0, 1); mask = m_top * m_bot
    edge_zone = np.clip(1 - np.minimum(np.abs(yyd - top[None, :]), np.abs(yyd - bot[None, :])) / (10.0 * U), 0, 1)
    mask = mask * (1 - edge_zone * 0.55 * (fringe > 0.62))
    xx = np.arange(bw)[None, :].astype(np.float32) + dx_n; endfade = np.clip(xx / (6.0 * U), 0, 1) * np.clip((bw - 1 - xx) / (6.0 * U), 0, 1); mask = mask * endfade
    t = np.clip((yy / bh * 200 - 48) / (155 - 48), 0, 1)
    stops = [(0.0, CR["edge"], 0.55), (0.18, CR["mid"], 0.95), (0.42, CR["fill"], 1.0), (0.58, CR["fill"], 1.0), (0.78, CR["mid"], 0.92), (1.0, CR["edge"], 0.5)]
    so = np.array([s[0] for s in stops]); sc = np.stack([hexrgb(s[1]) for s in stops]); sa = np.array([s[2] for s in stops]); tt = t[:, 0]
    col = np.stack([np.interp(tt, so, sc[:, c]) for c in range(3)], -1)[:, None, :].repeat(bw, 1); alp = np.interp(tt, so, sa)[:, None].repeat(bw, 1)
    u = np.arange(bw) / (bw - 1)
    lg_c = np.stack([np.interp(u, [0, .08, .5, .92, 1], [0x2A, 0x5A, 0x7A, 0x5A, 0x2A]), np.interp(u, [0, .08, .5, .92, 1], [0x0A, 0x1A, 0x32, 0x1A, 0x0A]),
                     np.interp(u, [0, .08, .5, .92, 1], [0x08, 0x18, 0x20, 0x18, 0x08])], -1)
    lg_a = np.interp(u, [0, .08, .5, .92, 1], [0.35, 0, 0.12, 0, 0.4]); col = col * (1 - lg_a[None, :, None]) + lg_c[None, :, :] * lg_a[None, :, None]
    Y, X = np.mgrid[0:bh, 0:bw].astype(np.float32)
    for cx, cy, r, c, a in [(0.28, 0.45, 0.38, "#2E0C0A", 0.45), (0.68, 0.58, 0.32, "#8A3A28", 0.28), (0.48, 0.40, 0.55, "#4A1410", 0.20)]:
        d = np.sqrt(((X / bw - cx) / r) ** 2 + ((Y / bh - cy) / r) ** 2); k = np.clip(1 - d, 0, 1) * a
        col = col * (1 - k[..., None]) + hexrgb(c)[None, None, :] * k[..., None]
    rng = np.random.default_rng(11); grain = rng.random((bh, bw)).astype(np.float32)
    grain = np.asarray(Image.fromarray((grain * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8 * U)), np.float32) / 255
    streak = smooth_noise(bh, bw, 2.5 * U, 90 * U, 21); mult = 1 - 0.22 * (grain - 0.5) * 2 * 0.5 - 0.18 * (streak - 0.5)
    col = np.clip(col * mult[..., None], 0, 255); a = np.clip(mask * alp, 0, 1)
    return Image.fromarray(np.dstack([col, a * 255]).astype(np.uint8), "RGBA"), bw, bh
def strike_layer(frame):
    global _STRIKE
    if CR is None: return None
    s0, s1, c0, c1 = CR["strokeEnterStart"], CR["strokeEnterEnd"], CR["strokeClearStart"], CR["strokeClearEnd"]
    if frame < s0 or frame >= c1: return None
    if _STRIKE is None: _STRIKE = build_strike_rgba()
    img, bw, bh = _STRIKE
    lead = interp(frame, s0, s1, 0, 1, E_DRAG); clr = interp(frame, c0, c1, 0, 1, E_OUT); vis = lead * (1 - clr)
    op = CR["peakOpacity"] * interp(frame, c0, c1, 1, 0, E_OUT)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); vw = int(round(bw * vis))
    if vw <= 0: return None
    piece = img.crop((0, 0, vw, bh)); a = np.asarray(piece.getchannel("A"), np.float32) * op; piece.putalpha(Image.fromarray(a.astype(np.uint8)))
    x0 = int(round((W - bw) / 2 + CR["offsetX"])); y0 = int(round(H * CR["topPercent"] / 100 - bh / 2)); layer.alpha_composite(piece, (x0, y0))
    if 0 < lead < 1:
        tip = interp(lead, 0, 0.15, 0.35, 0.55) if lead < 0.15 else (interp(lead, 0.15, 0.85, 0.55, 0.4) if lead < 0.85 else interp(lead, 0.85, 1, 0.4, 0))
        bl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(bl)
        cx = x0 + vw; cy = y0 + bh / 2; rx = 28 / 1000 * bw; ry = 42 / 200 * bh
        dr.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=tuple(hexrgb(CR["mid"]).astype(int)) + (int(255 * tip * 0.55 * op),))
        layer.alpha_composite(bl.filter(ImageFilter.GaussianBlur(6 * G["U"])))
    return layer
def title_layout():
    global _GLYPHS
    if _GLYPHS is not None: return _GLYPHS
    U = G["U"]; fs = CR["fontSize"]; font = title_font(); lines = CR["title"].split("\n"); track = CR["trackingEm"] * fs
    asc, desc = font.getmetrics(); line_h = TITLE_LINE_H * fs; gap = round(fs * 0.04); block_h = len(lines) * line_h + (len(lines) - 1) * gap
    cy = H * CR["topPercent"] / 100 + CR["nudgeY"]; top = cy - block_h / 2
    flat = sum(len(l) for l in lines); last = max(flat - 1, 1); glyphs = []; gi = 0; cap_h = font.getbbox("H")[3] - font.getbbox("H")[1]
    for li, line in enumerate(lines):
        widths = [font.getlength(ch) for ch in line]; total = sum(widths) + track * (len(line) - 1)
        if total > G["title"]["max_line_w"]: raise SystemExit(f"title line too wide for {W}x{H}: '{line}' {total:.0f} px > {G['title']['max_line_w']:.0f}")
        x = W / 2 + CR["offsetX"] - total / 2; line_mid = top + li * (line_h + gap) + line_h / 2
        for ch, wch in zip(line, widths):
            if ch != " ":
                pad = max(2, int(round(12 * U))); spr = Image.new("RGBA", (int(wch + 2 * pad), asc + desc + 2 * pad), (0, 0, 0, 0)); sh = Image.new("RGBA", spr.size, (0, 0, 0, 0))
                ImageDraw.Draw(sh).text((pad, pad + 2 * U), ch, font=font, fill=(0, 0, 0, 115)); spr.alpha_composite(sh.filter(ImageFilter.GaussianBlur(1.0 * U)))
                ImageDraw.Draw(spr).text((pad, pad), ch, font=font, fill=CR["color"] + (255,))
                hb = font.getbbox("H"); y_img = line_mid - (hb[1] + cap_h / 2) - pad
                glyphs.append({"spr": spr, "x": x - pad, "y": y_img, "lx": gi / last})
            x += wch + track; gi += 1
    _GLYPHS = glyphs; return glyphs
def title_safe_report():
    """title block (strike band + text) must sit inside the derived safe area."""
    if CR is None: return None
    bw, bh = strike_wh(); x0 = (W - bw) / 2 + CR["offsetX"]; y0 = H * CR["topPercent"] / 100 - bh / 2; S = G["safe"]
    tw = max(title_lines_w()); tx0 = W / 2 + CR["offsetX"] - tw / 2
    rep = dict(band=[round(x0), round(y0), round(x0 + bw), round(y0 + bh)], text_x=[round(tx0), round(tx0 + tw)], safe=S)
    rep["text_inside_safe"] = S["x0"] <= tx0 and tx0 + tw <= S["x1"] and S["y0"] <= y0 and y0 + bh <= S["y1"]
    if not rep["text_inside_safe"]: FLAGS.append(f"FLAG title block {rep['band']} / text x {rep['text_x']} outside safe area {S}")
    return rep
def title_layer(frame):
    c = CR
    if c is None or frame >= c["exitEnd"]: return None
    lead = interp(frame, c["strokeEnterStart"], c["strokeEnterEnd"], 0, 1, E_DRAG)
    if frame < c["manifestStart"] and lead <= 0: return None
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); any_on = False
    for g in title_layout():
        lx = g["lx"]; edge_pass = c["strokeEnterStart"] + lx * (c["strokeEnterEnd"] - c["strokeEnterStart"])
        li0 = max(c["manifestStart"], edge_pass + c["afterEdgeLagFrames"]); li1 = min(c["manifestEnd"], li0 + c["letterSettleFrames"])
        op = interp(frame, li0, li1, 0, 1, E_IN); y = interp(frame, li0, li1, c["settleYPx"], 0, E_IN); sc = interp(frame, li0, li1, c["scaleFrom"], c["scaleTo"], E_IN)
        if c["manifestEnd"] <= frame < c["exitStart"]: op, y, sc = 1.0, 0.0, c["scaleTo"]
        if frame >= c["exitStart"]:
            span = c["exitEnd"] - c["exitStart"]; le0 = c["exitStart"] + (1 - lx) * span * 0.45; le1 = min(c["exitEnd"], le0 + span * 0.55)
            op = op * interp(frame, le0, le1, 1, 0, E_OUT); y = interp(frame, le0, le1, 0, -c["settleYPx"] * 0.85, E_OUT); sc = interp(frame, le0, le1, c["scaleTo"], c["exitScaleTo"], E_OUT)
        if op < 0.01: continue
        spr = g["spr"]; sw, sh = spr.size
        if abs(sc - 1) > 1e-3:
            nw, nh = max(1, round(sw * sc)), max(1, round(sh * sc)); spr2 = spr.resize((nw, nh), Image.Resampling.LANCZOS); ox = g["x"] + (sw - nw) * 0.5; oy = g["y"] + (sh - nh) * 0.7
        else: spr2 = spr; ox, oy = g["x"], g["y"]
        a = np.asarray(spr2.getchannel("A"), np.float32) * op; spr2 = spr2.copy(); spr2.putalpha(Image.fromarray(a.astype(np.uint8)))
        layer.alpha_composite(spr2, (int(round(ox)), int(round(oy + y)))); any_on = True
    return layer if any_on else None
def overlay_for(gf):
    ls = [l for l in (strike_layer(gf), title_layer(gf)) if l is not None]
    if not ls: return None
    out = ls[0].copy()
    for x in ls[1:]: out.alpha_composite(x)
    return out
def title_frames():
    return (CR["strokeEnterStart"], max(CR["exitEnd"], CR["strokeClearEnd"])) if CR else None

# ------------------------------------------------------------------ plate space: PlateFX (optional) -> smoke_v2 (optional) -> grade -> crop -> cover
_CACHE = {}
def plate_rgb(path):
    if ("P", path) not in _CACHE: _CACHE[("P", path)] = np.ascontiguousarray(cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB))
    return _CACHE[("P", path)]
def smoke_cfg(seg):
    cfg = json.load(open(seg["smoke"]))
    if cfg.get("plate"):   # Atahualpa v2c rule: a config written for another plate is refused, not silently re-used
        cp = Path(cfg["plate"]); cp = cp if cp.is_absolute() else Path(seg["smoke"]).parent / cp
        if not cp.is_file() or md5f(cp) != md5f(seg["plate"]): raise SystemExit(f"{seg['id']}: smoke config {seg['smoke']} points at another plate ({cfg['plate']})")
    return {k: v for k, v in cfg.items() if k not in ("plate", "note", "push", "push_center")}
def get_fx(seg):
    k = ("fx", seg["id"])
    if k not in _CACHE:
        fx = None
        if seg["fx"]:
            seed = int(hashlib.md5(Path(seg["plate"]).name.encode()).hexdigest()[:6], 16)   # per PLATE: fx continues through same-plate cuts
            fx = FX.PlateFX(seg["plate"], seed=seed); fx = fx if fx.active() else None
        _CACHE[k] = fx
    return _CACHE[k]
def get_smoke(seg):
    k = ("sm", seg["id"])
    if k in _CACHE: return _CACHE[k]
    if not seg["smoke"]: _CACHE[k] = None; return None
    P0 = plate_rgb(seg["plate"]); Hh, Ww = P0.shape[:2]; cfg = smoke_cfg(seg); sc = SM.SmokeScene(P0, cfg)
    guards = {n: SM.poly_mask((Hh, Ww), [p], 0) > 0.5 for n, p in (cfg.get("guards") or {}).items()}
    _CACHE[k] = dict(sc=sc, allow=sc.allow_mask(), prot=sc.protect_bin > 0.5, guards=guards, n_em=len(sc.emitters)); return _CACHE[k]
def grade(img, seg):
    if FX is not None and hasattr(FX, "grade") and hasattr(FX, "plate_key"): return FX.grade(img, FX.plate_key(seg["plate"]))
    return img
def plate_frame(seg, gf, u, proof=None):
    fx = get_fx(seg); S = get_smoke(seg)
    if fx is None and S is None:
        k = ("static", seg["id"])
        if k not in _CACHE:
            im = Image.fromarray(grade(plate_rgb(seg["plate"]), seg)); _CACHE[k] = prepare_cover(im.crop(seg["crop"]) if seg["crop"] else im)
        return _CACHE[k]
    img = fx_smoke(seg, gf, u, proof, fx, S)
    im = Image.fromarray(grade(img, seg))
    if seg["crop"]: im = im.crop(seg["crop"])
    return prepare_cover(im)
def fx_smoke(seg, gf, u, proof, fx, S):   # plate space, ungraded: PlateFX (optional) -> smoke_v2 (optional)
    img = fx.render(gf / FPS, u) if fx is not None else plate_rgb(seg["plate"])
    if S is not None:
        sc = S["sc"]; keep = sc.Pf; sc.Pf = img.astype(np.float32)   # emitters composite over the fx frame (they never read the plate)
        try: out = sc.frame((gf - seg["run_f0"]) / FPS)
        finally: sc.Pf = keep
        if proof is not None:
            d = np.abs(out.astype(np.int16) - img.astype(np.int16)).max(-1)
            proof["frames"] += 1; proof["max_outside_allow"] = max(proof["max_outside_allow"], int(d[~S["allow"]].max(initial=0)))
            proof["max_in_protect"] = max(proof["max_in_protect"], int(d[S["prot"]].max(initial=0))); proof["max_changed"] = max(proof["max_changed"], int(d.max()))
            for n, m in S["guards"].items(): proof["guards"][n] = max(proof["guards"].get(n, 0), int(d[m].max(initial=0)))
        img = out
    return img
def depth_plate_fx(seg, gf, proof=None):
    """plate-space RGB float [0,1] for depth_v1's plate_fx, or None (pure depth). fx (its own parallax frozen: u=0) -> smoke_v2
    -> dust_v1 / water_v1 deltas (their .frame(t) only: their cameras never run) -> grade. Same plate as the depth cards."""
    fx = get_fx(seg); S = get_smoke(seg); E = get_plate_fx(seg)
    graded = FX is not None and hasattr(FX, "grade") and hasattr(FX, "plate_key")
    if fx is None and S is None and not E and not graded: return None
    img = fx_smoke(seg, gf, 0.0, proof, fx, S) if (fx is not None or S is not None) else plate_rgb(seg["plate"])
    if E:
        acc = img.astype(np.float32); P0 = plate_rgb(seg["plate"]).astype(np.float32); t = (gf - seg["run_f0"]) / FPS
        for _, eng in E: acc += eng.frame(t).astype(np.float32) - P0
        img = np.clip(acc + 0.5, 0, 255).astype(np.uint8)
    return grade(img, seg).astype(np.float32) / 255.0

# ------------------------------------------------------------------ content-hash cache (.key sidecars; stale outputs renamed, never deleted)
class KeyedCache:
    """reuse `path` only if `path.key` == key; otherwise rename path (+ its sidecars) to *.stale-<ts>.* and report 'render'."""
    def __init__(self, path, parts, sidecars=()):
        self.path = Path(path); self.parts = parts; self.key = md5j(parts); self.kp = self.path.with_suffix(".key"); self.sidecars = [Path(s) for s in sidecars]
    def _stale(self, p):
        if not p.exists(): return None
        ts = RUN_TS; n = 0
        while True:
            q = p.with_name(f"{p.stem}.stale-{ts}{'' if not n else f'-{n}'}{p.suffix}")
            if not q.exists(): break
            n += 1
        p.rename(q); return q
    def check(self):
        have = json.load(open(self.kp)).get("key") if self.kp.is_file() else None
        if self.path.exists() and have == self.key: return "hit", []
        why = "no output yet" if not self.path.exists() else ("no .key sidecar (legacy / interrupted)" if have is None else "key mismatch")
        diff = []
        if have is not None and self.kp.is_file():
            old = json.load(open(self.kp)).get("parts", {}); diff = sorted(k for k in set(old) | set(self.parts) if old.get(k) != self.parts.get(k))
        moved = [str(q) for q in (self._stale(p) for p in [self.path, self.kp, *self.sidecars]) if q]
        return "render", dict(why=why, changed=diff, renamed=moved)
    def commit(self):
        tmp = self.kp.with_suffix(".key.part"); json.dump(dict(key=self.key, parts=self.parts, written=time.strftime("%Y-%m-%d %H:%M:%S %Z")), open(tmp, "w"), indent=1, default=str); tmp.rename(self.kp)

def engine_md5s(seg):   # effect engine files that can change THIS shot's pixels
    e = {}
    if seg["smoke"]: e["smoke_engine"] = ENGINE_MD5["smoke_engine"]
    if seg["fx"]: e.update({k: v for k, v in ENGINE_MD5.items() if k.startswith("fx_module")})
    if seg["smoke"] or seg["fx"]: e.update({k: v for k, v in ENGINE_MD5.items() if k.startswith("extra:")})
    if seg.get("depth"): e.update({k: ENGINE_MD5.get(k) for k in ("depth_engine", "depth_model")})
    for kind in (seg.get("plate_fx_cfgs") or {}): e[f"{kind}_engine"] = ENGINE_MD5[f"{kind}_engine"]
    return e
def shot_key_parts(seg):
    tf = title_frames(); title_on = bool(tf) and seg["f0"] < tf[1] and seg["f1"] > tf[0]
    segj = {k: v for k, v in seg.items() if k not in ("guard",)}
    return dict(kind="shot", template=TEMPLATE_MD5, size=f"{W}x{H}", fps=FPS, up=UP, enc=ENC_INTER, plate=md5f(seg["plate"]), segment=md5j(segj),
                fx_smoke_config=md5f(seg["smoke"]) if seg["smoke"] else None, engine=engine_md5s(seg), proof_every=A.proof_every if seg["smoke"] else None,
                title=md5j(dict(CR=CR, font=md5f(FONT_DIR + CR["font"]))) if title_on else None,
                depth=md5j(seg["depth"]) if seg.get("depth") else None,
                depth_src=md5f(seg["depth"]["_src"]) if seg.get("depth") and seg["depth"].get("_src") else None,
                plate_fx=md5j(seg["plate_fx_cfgs"]) if seg.get("plate_fx_cfgs") else None)

def _render_task(sid):
    """Pool wrapper: a SystemExit/exception inside a worker would otherwise kill the worker and hang imap forever."""
    try: return render_segment(sid)
    except BaseException as e: return sid, "ERROR", 0, dict(why=f"{type(e).__name__}: {e}", changed=[], renamed=[])
def render_segment(sid):
    seg = SEG[sid]; dst = CLIPS / f"{sid}.mp4"; pj = CLIPS / f"{sid}.smoke_proof.json"; dj = CLIPS / f"{sid}.depth_proof.json"
    kc = KeyedCache(dst, shot_key_parts(seg), sidecars=[pj, dj]); st, info = kc.check()
    if st == "hit": return sid, "hit", 0, None
    tmp = CLIPS / f"{sid}.part.mp4"
    if tmp.exists(): KeyedCache._stale(kc, tmp)   # interrupted run: keep it, out of the way
    nfr = seg["frames"]
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0", "-frames:v", str(nfr), "-an", *ENC_INTER, "-r", str(FPS), str(tmp)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE); on = bool(seg["smoke"])
    proof = dict(slot=sid, plate=Path(seg["plate"]).name, smoke_cfg=seg["smoke"], every=A.proof_every, frames=0, max_outside_allow=0, max_in_protect=0, max_changed=0, guards={})
    if seg.get("depth"): render_depth_frames(seg, proc, proof, on, dj)
    for fi in (range(nfr) if not seg.get("depth") else ()):
        u = fi / max(nfr - 1, 1); gf = seg["f0"] + fi
        b = plate_frame(seg, gf, u, proof if (on and fi % A.proof_every == 0) else None)
        frame = cam_frame(b, seg, u, fi / FPS); ov = overlay_for(gf)
        if ov is not None: fr = frame.convert("RGBA"); fr.alpha_composite(ov); frame = fr.convert("RGB")
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    if proc.wait(): raise SystemExit(f"encode fail {sid}")
    if on:
        proof["zero_motion_ok"] = proof["max_outside_allow"] == 0 and proof["max_in_protect"] == 0 and all(v == 0 for v in proof["guards"].values())
        proof["emitter_layers"] = get_smoke(seg)["n_em"]; json.dump(proof, open(pj, "w"), indent=1)
        if not proof["zero_motion_ok"]: raise SystemExit(f"SMOKE ZERO-MOTION FAIL {sid}: {proof} (clip left as {tmp}, no key written)")
    tmp.rename(dst); kc.commit()
    return sid, "render", nfr, info

def render_depth_frames(seg, proc, proof, on, dj):
    """depth_v1 single-transform path: ONE uniform matrix per layer per frame (push + drift folded in); NO template push."""
    sh = get_depth(seg); nfr = seg["frames"]; size = (W, H); o = sh.overscan(size, nfr)
    E = DP.smooth_progress(nfr, fps=FPS, **sh.cam().get("ease", {})); DP.WARP_LOG.clear(); c0, e0 = TEMPLATE_CAM_CALLS[0], EFFECT_CAM_CALLS[0]
    for fi in range(nfr):
        gf = seg["f0"] + fi; pf = depth_plate_fx(seg, gf, proof if (on and fi % A.proof_every == 0) else None)
        out = sh.frame(float(E[fi]), size, o, fid=fi, plate_fx=(lambda t, _p=pf: _p) if pf is not None else None, t=fi / FPS)
        frame = Image.fromarray(DP.to8(out)); ov = overlay_for(gf)
        if ov is not None: fr = frame.convert("RGBA"); fr.alpha_composite(ov); frame = fr.convert("RGB")
        proc.stdin.write(frame.tobytes())
    cnt = {}
    for t in DP.WARP_LOG: cnt[t] = cnt.get(t, 0) + 1
    rep = dict(slot=seg["id"], plate=Path(seg["plate"]).name, depth_src=seg["depth"].get("_src"), frames=nfr, layers=[c["name"] for c in sh.cards],
               overscan=round(o, 5), warps_logged=len(DP.WARP_LOG), expected=nfr * len(sh.cards), max_warps_per_layer_frame=max(cnt.values()) if cnt else 0,
               template_cam_calls=TEMPLATE_CAM_CALLS[0] - c0, effect_camera_calls=EFFECT_CAM_CALLS[0] - e0,
               plate_fx=sorted((seg.get("plate_fx_cfgs") or {}).keys()) + (["fx"] if get_fx(seg) is not None else []) + (["smoke"] if seg["smoke"] else []),
               density=seg.get("density"))
    rep["single_transform_ok"] = rep["warps_logged"] == rep["expected"] and rep["max_warps_per_layer_frame"] == 1 and rep["template_cam_calls"] == 0 and rep["effect_camera_calls"] == 0
    json.dump(rep, open(dj, "w"), indent=1, default=str)
    if not rep["single_transform_ok"]: raise SystemExit(f"DEPTH SINGLE-TRANSFORM FAIL {seg['id']}: {rep}")

# ------------------------------------------------------------------ captions (timeline cues; ceil/floor; no cue may straddle a cut); style from --size
def wrap_text(txt, maxc):
    w = txt.split()
    if len(txt) <= maxc or len(w) < 2: return [txt]
    best = min(range(1, len(w)), key=lambda k: max(len(" ".join(w[:k])), len(" ".join(w[k:]))))
    return [" ".join(w[:best]), " ".join(w[best:])]
def ass_cs(t, end=False):
    x = max(0.0, t) * 100; return int(math.floor(x + 1e-6)) if end else int(math.ceil(x - 1e-6))
def ass_time(t, end=False):
    cs = ass_cs(t, end); s, cs = divmod(cs, 100); m, s = divmod(s, 60); h, m = divmod(m, 60); return f"{h}:{m:02d}:{s:02d}.{cs:02d}"
def build_ass():
    cues = TL.get("captions") or []
    if not cues: return None, []
    c = G["cap"]; r = lambda v: max(0, int(round(v)))
    ass = ["[Script Info]", f"Title: Posterity build_template_v1 {A.tag}", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 2", "ScaledBorderAndShadow: yes", "", "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
           f"Style: Default,DejaVu Sans,{max(6, r(c['font']))},&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,{max(1, r(c['outline']))},{max(1, r(c['shadow']))},2,{r(c['ml'])},{r(c['mr'])},{r(c['mv'])},1",
           "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    cuts = [s["start"] for s in SEGS[1:]]; total = SEGS[-1]["end"]; ev = []
    for q in cues:
        st, en, txt = float(q["start"]), min(float(q["end"]), total), q["text"]
        if not (0 <= st < en): raise SystemExit(f"caption '{txt}': bad times {st}-{en}")
        if any(st + 1e-6 < t < en - 1e-6 for t in cuts): raise SystemExit(f"caption straddles a cut: '{txt}' {st}-{en}")
        c0, c1 = ass_cs(st), ass_cs(en, True); fr = [k for k in range(int(c0 * FPS / 100) - 1, int(c1 * FPS / 100) + 2) if c0 <= k * 100 / FPS < c1]
        shots = {s["id"] for k in fr for s in SEGS if s["f0"] <= k < s["f1"]}
        if len(shots) > 1: raise SystemExit(f"caption on screen across a cut: '{txt}' shots {shots}")
        ass.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en, True)},Default,,0,0,0,," + r"{\fad(120,80)}" + r"\N".join(wrap_text(txt, c["maxc"])))
        ev.append(dict(start=st, end=en, text=txt))
    return "\n".join(ass) + "\n", ev

# ------------------------------------------------------------------ audio (Jianwen v2 chain, generic): VO (+ optional bed, ducked) -> loudness loop; keyed mix.wav
def ff(*a): subprocess.check_call(["ffmpeg", "-y", "-v", "error", *a])
def ebur(path):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True); Iv = TP = None; summ = False
    for ln in p.stderr.splitlines():
        if "Summary:" in ln: summ = True
        if summ and ln.strip().startswith("I:"): Iv = float(ln.split("I:")[1].split("LUFS")[0])
        if summ and ln.strip().startswith("Peak:"): TP = float(ln.split("Peak:")[1].split("dBFS")[0])
    return Iv, TP
AUDIO_CHAIN = dict(vo="highpass=f=80,acompressor=threshold=0.125:ratio=3:attack=8:release=140:knee=3:makeup=1,aresample=48000",
                   bed="aresample=48000,highpass=f=70,equalizer=f=2500:t=q:w=1.0:g=-3.0,afade=t=in:d=1.2",
                   duck="sidechaincompress=threshold=0.02:ratio=4:attack=25:release=450:knee=4:makeup=1",
                   limiter="aresample=192000,alimiter=limit=0.8:attack=3:release=60:level=false:asc=1,aresample=48000")
def build_audio():
    au = TL.get("audio") or {}
    if not au.get("vo") and not au.get("music"): return None, "no audio in timeline"
    vo = (TLDIR / au["vo"]).resolve() if au.get("vo") else None; mu = (TLDIR / au["music"]).resolve() if au.get("music") else None
    for p in (vo, mu):
        if p is not None and not p.is_file(): raise SystemExit(f"audio file missing: {p}")
    DUR = SEGS[-1]["end"]; lufs = float(au.get("lufs", -14.0)); tp_max = float(au.get("tp_max", -1.5)); bed_db = float(au.get("bed_db", -17.5))
    mix = AUD / "mix.wav"
    parts = dict(kind="mix", template=TEMPLATE_MD5, vo=md5f(vo) if vo else None, music=md5f(mu) if mu else None, dur=round(DUR, 4), lufs=lufs, tp_max=tp_max, bed_db=bed_db, chain=md5j(AUDIO_CHAIN))
    kc = KeyedCache(mix, parts, sidecars=[AUD / "mix_stats.json"]); st, info = kc.check()
    if st == "hit": return mix, "hit"
    wk = AUD / f"work-{kc.key[:12]}"
    if wk.exists(): KeyedCache._stale(kc, wk)
    wk.mkdir(parents=True); SR = 48000; N = int(round(DUR * SR)); fade1 = max(DUR - 0.05, 0.1); fade0 = max(fade1 - 1.35, 0)
    ins, fc = [], []
    if vo: ff("-i", str(vo), "-af", AUDIO_CHAIN["vo"], "-ac", "1", "-c:a", "pcm_f32le", str(wk / "vo_proc.wav")); ins += ["-i", str(wk / "vo_proc.wav")]
    if mu: ff("-i", str(mu), "-t", f"{DUR:.3f}", "-af", AUDIO_CHAIN["bed"] + f",afade=t=out:st={fade0:.3f}:d={fade1 - fade0:.3f}", "-ac", "2", "-c:a", "pcm_f32le", str(wk / "bed.wav")); ins += ["-i", str(wk / "bed.wav")]
    if vo and mu: fc = f"[0:a]pan=stereo|c0=c0|c1=c0,asplit=2[v][k];[1:a]volume={bed_db}dB[b];[b][k]{AUDIO_CHAIN['duck']}[bd];[v][bd]amix=inputs=2:normalize=0:duration=first,apad=whole_len={N}"
    elif vo: fc = f"[0:a]pan=stereo|c0=c0|c1=c0,apad=whole_len={N}"
    else: fc = f"[0:a]volume={bed_db}dB,apad=whole_len={N}"
    pre = wk / "premix.wav"; ff(*ins, "-filter_complex", fc, "-t", f"{DUR:.4f}", "-c:a", "pcm_f32le", str(pre))
    I0, _ = ebur(pre); gain = lufs - I0; I1 = TP1 = None
    for it in range(8):
        cand = wk / f"mix_it{it}.wav"
        ff("-i", str(pre), "-af", f"volume={gain:.3f}dB," + AUDIO_CHAIN["limiter"], "-c:a", "pcm_s24le", str(cand)); I1, TP1 = ebur(cand)
        if I1 is not None and abs(I1 - lufs) <= 0.1 and TP1 <= tp_max: break
        if I1 is None: break
        gain += (lufs - I1)
    shutil.copyfile(cand, mix); json.dump(dict(premix_I=I0, gain=gain, mix_I=I1, mix_TP=TP1, lufs_target=lufs, iterations=it + 1, work=str(wk)), open(AUD / "mix_stats.json", "w"), indent=1)
    if I1 is None or abs(I1 - lufs) > 0.5: FLAGS.append(f"FLAG mix loudness {I1} LUFS (target {lufs}; short test audio cannot gate properly)")
    kc.commit(); return mix, info

# ------------------------------------------------------------------ phone QC: mid-frame still per shot at the derived phone size (keyed)
def phone_qc(seg):
    pw, ph = G["phone"]; p = QC / f"{seg['id']}_phone_{pw}x{ph}.png"; clip = CLIPS / f"{seg['id']}.mp4"
    kc = KeyedCache(p, dict(kind="phone_qc", clip_key=json.load(open(CLIPS / f"{seg['id']}.key"))["key"], size=f"{pw}x{ph}")); st, info = kc.check()
    if st == "hit": return p, "hit"
    mid = seg["frames"] // 2; tmp = QC / f"{seg['id']}_phone.part.png"
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", str(clip), "-vf", f"select=eq(n\\,{mid}),scale={pw}:{ph}:flags=lanczos", "-frames:v", "1", str(tmp)])
    tmp.rename(p); kc.commit(); return p, "render"

# ------------------------------------------------------------------ main
def print_plan():
    print(f"size {W}x{H} ({'portrait' if G['portrait'] else 'landscape'}) fps {FPS} | phone QC {G['phone'][0]}x{G['phone'][1]} | preview {G['preview'][0]}x{G['preview'][1]} | safe {G['safe']}")
    for s in SEGS:
        g = s.get("guard", {})
        print(f"  {s['id']:6} {s['plate_id']:10} {Path(s['plate']).name:34} f{s['f0']:5d}-{s['f1']:5d} {s['duration']:6.3f}s push {s['z_start']:.3f}->{s['z_end']:.3f}"
              f"{' crop ' + str(s['crop']) if s['crop'] else ''} zoom {g.get('zoom', 0):.3f}x density {s.get('density', {}).get('ratio', 0):.3f} {g.get('msg', '')}{' smoke' if s['smoke'] else ''}{' fx' if s['fx'] else ''}"
              + (f" DEPTH {len(s['depth']['layers'])} layers (template push skipped) overscan {s.get('depth_overscan')} gate layer {s['density'].get('gate_layer')} per-layer "
                 + ",".join(f"{x['layer']}:{x['density']:.3f}" for x in s['density'].get('per_layer', [])) + (f" +{','.join(s['plate_fx_cfgs'])}" if s['plate_fx_cfgs'] else "") if s['depth'] else "")
              + (" [character]" if s['character'] else ""))
    tr = title_safe_report()
    if tr: print("  title:", tr)

def main(argv=None):
    args = parse_args(argv); setup(args); print_plan()
    ass_text, cap_ev = build_ass()
    print("FLAGS:" if FLAGS else "FLAGS: none"); [print(" ", f) for f in FLAGS]
    if args.check: print("CHECK OK (nothing rendered)"); return 0
    free = shutil.disk_usage(str(Path(args.build_dir).resolve().parent if not Path(args.build_dir).exists() else args.build_dir)).free / 2 ** 30
    if free < args.min_free_gib: raise SystemExit(f"only {free:.1f} GiB free (< {args.min_free_gib})")
    for d in (BUILD, CLIPS, AUD, QC): d.mkdir(parents=True, exist_ok=True)
    report = dict(run=RUN_TS, size=f"{W}x{H}", fps=FPS, tag=args.tag, template_md5=TEMPLATE_MD5, engines=ENGINE_MD5, shots={}, audio=None, phone_qc={})
    out_dir = Path(args.out_dir) if args.out_dir else BUILD / "out"
    MASTER = out_dir / f"{TL.get('name', 'posterity')}-{args.tag}-{W}x{H}.mp4"; PREVIEW = MASTER.with_name(MASTER.stem + "-preview.mp4")
    if not (args.clips_only or args.audio_only):
        for p in (MASTER, PREVIEW):
            if p.exists(): raise SystemExit(f"{p} exists: refusing to overwrite (use a new --tag)")
    if not args.clips_only:
        mix, ainfo = build_audio(); report["audio"] = dict(path=str(mix) if mix else None, status=ainfo if isinstance(ainfo, str) else "render", detail=ainfo if isinstance(ainfo, dict) else None)
        print("audio:", report["audio"])
        if args.audio_only: json.dump(report, open(BUILD / f"cache_report_{RUN_TS}.json", "w"), indent=1, default=str); return 0
    order = [s["id"] for s in sorted(SEGS, key=lambda s: -s["frames"])]
    ctx = mp.get_context("fork")
    with ctx.Pool(max(1, min(args.jobs, len(order)))) as pool:
        for sid, st, n, info in pool.imap_unordered(_render_task, order):
            report["shots"][sid] = dict(status=st, frames=n, detail=info)
            if st == "ERROR": print(f"clip {sid}: FAILED  {info['why']}", flush=True); continue
            print(f"clip {sid}: {'CACHE HIT' if st == 'hit' else 'RENDERED ' + str(n) + ' fr'}" + (f"  ({info['why']}; changed {info['changed']}; renamed {info['renamed']})" if info else ""), flush=True)
    bad = [k for k, v in report["shots"].items() if v["status"] == "ERROR"]
    if bad:
        json.dump(report, open(BUILD / f"cache_report_{RUN_TS}.json", "w"), indent=1, default=str)
        raise SystemExit(f"CLIP FAILURES {bad}: no master written (good clips keep their keys)")
    if not args.no_phone_qc:
        for s in SEGS: p, st = phone_qc(s); report["phone_qc"][s["id"]] = dict(path=str(p), status=st)
    if not args.clips_only:
        out_dir.mkdir(parents=True, exist_ok=True); cl = BUILD / f"concat_{RUN_TS}.txt"; cl.write_text("".join(f"file '{CLIPS / (s['id'] + '.mp4')}'\n" for s in SEGS))
        vf = []
        if ass_text: ap_ = BUILD / f"captions_{args.tag}_{RUN_TS}.ass"; ap_.write_text(ass_text); vf = ["-vf", "ass='" + str(ap_).replace(":", "\\:") + "'"]
        mix = report["audio"]["path"] if report["audio"] else None; DUR = SEGS[-1]["end"]
        cmd = ["ffmpeg", "-n", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(cl)] + (["-i", mix, "-map", "0:v", "-map", "1:a"] if mix else []) + vf + ENC_FINAL + ["-r", str(FPS)] \
              + (["-c:a", "aac", "-b:a", "320k", "-ar", "48000"] if mix else ["-an"]) + ["-t", f"{DUR:.4f}", "-movflags", "+faststart", str(MASTER)]
        subprocess.check_call(cmd); pw, ph = G["preview"]
        if min(W, H) > 720:   # preview only when it is a real downscale (720 short side)
            subprocess.check_call(["ffmpeg", "-n", "-v", "error", "-i", str(MASTER), "-vf", f"scale={pw}:{ph}:flags=lanczos", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium"]
                                  + (["-c:a", "copy"] if mix else ["-an"]) + ["-movflags", "+faststart", str(PREVIEW)])
        report["master"] = dict(path=str(MASTER), md5=md5f(MASTER)); report["preview"] = dict(path=str(PREVIEW), md5=md5f(PREVIEW)) if PREVIEW.exists() else None
        print("master", MASTER, report["master"]["md5"])
    rp = BUILD / f"cache_report_{RUN_TS}.json"; json.dump(report, open(rp, "w"), indent=1, default=str); print("report", rp)
    return 0

if __name__ == "__main__":
    sys.exit(main())
