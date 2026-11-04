"""snow_v1b: snow_v1 turned up a notch (owner feedback 2026-10-31: ~1.7x flakes, mid/near a bit larger and more visible).
snow_v1 itself is unchanged. Below is the v1 description; only the numbers in TIER_DEFAULTS / PRESETS differ.

snow_v1: subtle, painterly snowfall over a still plate (variant of the locked dust_v1). MATTE-ONLY, SCREEN-SPACE.

Owner idea (via Vellum): restrained period snowfall on the Bathory winter plates B11 / B12 / B17. Not a stock overlay.
(B10 was on the first list; the owner replaced its plate with an interior and ruled B10 flat + candle + dust, no snow.)
Each preset pins its plate md5: the hand masks belong to that image, so a swapped plate is refused, not silently mis-masked.

Model (read top to bottom):
  * camera: the plate gets the house StablePush (1.00 -> 1.06, same maths as flames_v3.push_frame / smoke_v2) and is
    cover-fit to 1080x1920. The SNOW IS COMPOSITED AFTER THE PUSH, in output (screen) space: flake positions, sizes and
    speeds are in output px, so flakes never zoom with the plate. Only the static mattes / colour map ride the camera.
  * tiers: 2-3 depth tiers (far / mid / near). Nearer = larger, softer, faster, sways more. Few flakes per tier.
  * motion: each flake falls at a constant slow speed plus a per-plate wind drift, with a gentle 2-sine lateral sway
    (0.08-0.3 Hz) and a small vertical flutter. Positions are analytic p(t + pre_roll) -> deterministic and already
    moving at frame 0. Wrapping happens only in an off-screen margin.
  * no pops: every flake has its own slow life envelope (6-14 s, (0.5-0.5cos)^p) so it fades in and out in the air, and
    every matte edge is feathered so a flake dissolves (never clips) where it meets a keep-out.
  * colour: from the plate's ambient light. snow_white = the plate's own lit-snow colour (bright, low-saturation px);
    a heavily blurred plate gives the local light, which sets the flake's brightness and tints it (warm by a torch,
    blue-grey in night sky). Far flakes are pulled further toward the local ambient (aerial perspective).
  * depth gating (occlusion): Depth Anything V2 Small (the depth_v1 model, read-only) gives plate depth D (0 far..1 near).
    A tier is visible only where the painted surface is farther than the tier (D < tier.depth, soft ramp), so far/mid
    flakes go behind figures, carts and near walls; only the near tier can pass in front of them.
  * keep-out (0 changed px, enforced by a hard reset): faces (YuNet auto-detect, models/, plus hand boxes per plate,
    padded for hats/scarves), subject/light-source boxes (torches, brazier), and interiors seen through doors.
  * settled snow stays still: there is no ground/sheet layer at all (unlike dust_v1); `land` polygons fade every tier
    to `land_gain` (0 = flakes "land" and dissolve at the ground line), so nothing moves on the ground.
Guardrails: motion/guardrails.py check_shot (refuse) before every render: <= 1.5 output px per source px at peak push.

CLI (all outputs refuse to overwrite; <preset> = a PRESETS key, or a JSON file {"base": key, ...overrides}):
  snow_v1b.py presets
  snow_v1b.py render  <preset> <out.mp4> [--seconds 4] [--size 1080x1920] [--crf 20]
  snow_v1b.py reel    <out.mp4> [--presets b11,b12,b17] [--seconds 4] [--crf 20]
  snow_v1b.py sheet   <out.png> [--presets ...] [--t 2.0]          contact sheet: one still per plate (540x960 each)
  snow_v1b.py proof   <preset> <out.json>    keep-out 0-px proof, outside-matte 0-px proof, determinism, guardrail
  snow_v1b.py stats   <preset> <out.json>    flakes on screen per tier, phone 360x640 pop / flicker / read metrics
  snow_v1b.py overlay <preset> <out.png>     plate | tier mattes (R far, G mid, B near) + keep-out (magenta)
"""
import hashlib, importlib.util, json, math, subprocess, sys
from pathlib import Path
import numpy as np, cv2

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent                                        # /workspace/posterity
PLATES = ROOT / "standalones" / "bathory" / "v2" / "plates"
DEPTH_MODEL = HERE.parent / "depth" / "models" / "da2_small.onnx"  # read-only (depth_v1's model)
FACE_MODEL = HERE / "models" / "face_detection_yunet_2023mar.onnx" # OpenCV zoo YuNet (MIT)
CACHE = HERE / "cache"
cv2.setNumThreads(4)

def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
G = _load("guardrails", ROOT / "motion" / "guardrails.py")      # house guardrails (read-only import)

# ============================================================================================ presets
# Units: tier sigma / speed / sway in OUTPUT px at 1080x1920 (scaled for previews); boxes / polys in PLATE px.
TIER_DEFAULTS = {
    "far":  dict(n=187, depth=0.30, sigma=[1.2, 1.6],  speed=[30, 42],  sway=[4, 8],   sway_hz=[0.10, 0.22], opacity=0.50, aerial=0.35),
    "mid":  dict(n=102, depth=0.55, sigma=[2.2, 2.9],  speed=[52, 72],  sway=[8, 14],  sway_hz=[0.09, 0.20], opacity=0.66, aerial=0.15),
    "near": dict(n=37,  depth=0.92, sigma=[4.0, 5.6],  speed=[88, 120], sway=[14, 24], sway_hz=[0.07, 0.16], opacity=0.64, aerial=0.0),
}
PRESETS = {
    # REDONE PLATE (owner, 1:29pm ET): two carriers bear a covered body on a bier across the snowy courtyard; brazier left,
    # restrained blood in the snow, lit doorway right (candle, a figure). Old empty-courtyard plate = b11_..._v1.png (unused).
    # far/mid pass BEHIND carriers + bier via depth; the heads band, bier + cloth, brazier (flame + glow) and the doorway are
    # keep-outs (0 px); ground (snow + blood) has no snow motion. The same polys feed the depth_v1 build (see README).
    "b11": dict(plate=str(PLATES / "b11_bytca_door_shut.png"), plate_md5="32aa34cb6a207b5b2e2138d2c96d1c12", seed=1111, push=[1.0, 1.06], push_center=[0.55, 0.5], wind=-4.0, depth_soft=0.025,
                # DA2 here: arcade ~0.10-0.15, carriers/bier ~0.20-0.25, ground 0.3-1.0 -> far/mid gate below the carriers
                tiers=dict(far=dict(n=300, depth=0.155), mid=dict(n=152, depth=0.175), near=dict(n=58)),
                faces=[],
                subjects=[[[392, 700], [505, 700], [505, 825], [392, 825]],          # carrier 1 head + hat
                          [[672, 805], [772, 805], [772, 912], [672, 912]]],         # carrier 2 head + hat
                keepout=[[[420, 885], [775, 885], [775, 1045], [420, 1045]],         # bier + body cloth
                         [[85, 985], [295, 985], [295, 1262], [85, 1262]]],          # brazier + flame + glow (torch pulse)
                interior=[[[775, 680], [925, 680], [925, 1100], [775, 1100]]],      # lit doorway (candle, figure)
                land=[[[0, 1215], [942, 1180], [942, 1672], [0, 1672]]], land_gain=0.0, land_feather=80),
    # Night, fortress on the crag, torch procession. Snow reads against the dark sky; keep it off the torch line.
    "b12": dict(plate=str(PLATES / "b12_taken_up_to_fortress.png"), plate_md5="78699fc77cbbba1365ced9f37d8569ae", seed=1212, color_gain=1.6, push=[1.0, 1.06], push_center=[0.5, 0.38], wind=6.0,
                tiers=dict(far=dict(n=204, depth=0.35), mid=dict(n=94, depth=0.6), near=dict(n=31)),
                faces=[], keepout=[[[330, 560], [630, 560], [630, 760], [330, 760]]], interior=[],
                land=[[[0, 1240], [942, 1215], [942, 1670], [0, 1670]]], land_gain=0.0, land_feather=70),
    # Dusk street, crowd queueing at a lit doorway, brazier. Crowd heads band + every YuNet face kept out; the doorway
    # (a lit interior: clerk, candle) is INDOORS -> no snow there; the brazier flame is a keep-out (flakes melt).
    "b17": dict(plate=str(PLATES / "b17_secondhand_witnesses.png"), plate_md5="b48467066fb2d4832db9139bd0d3efb3", seed=1717, push=[1.0, 1.06], push_center=[0.4, 0.4], wind=-4.0,
                tiers=dict(far=dict(n=221), mid=dict(n=128), near=dict(n=44)),
                faces=[],
                subjects=[[[200, 540], [942, 520], [942, 1160], [690, 1160], [640, 1060], [470, 1060], [400, 900], [300, 800], [200, 740]]],
                keepout=[[[20, 830], [265, 830], [265, 1215], [20, 1215]]],
                interior=[[[65, 330], [280, 330], [280, 840], [65, 840]]],
                land=[[[0, 1150], [200, 1150], [330, 1670], [0, 1670]]], land_gain=0.0, land_feather=70),
}
SHOT_DEFAULTS = dict(seconds=4.0, crf=20, size="1080x1920", pre_roll=60.0, life_s=[6.0, 14.0], env_pow=0.7,
                     auto_faces=True, face_score=0.6, face_pad=[0.6, 0.9, 0.5], keepout_feather=40, depth_soft=0.08, gate_blur=6.0,
                     color_lift=0.5, color_tint=0.35, color_gain=1.0, ambient_sigma=0.05)

def get_cfg(key_or_path):
    """Preset key ('b11'), or a JSON file {"base": "b11", ...overrides}. Tier dicts merge per key."""
    if key_or_path in PRESETS: over, base = {}, key_or_path
    else: over = json.load(open(key_or_path)); base = over.pop("base")
    c = json.loads(json.dumps(SHOT_DEFAULTS)); c.update(json.loads(json.dumps(PRESETS[base]))); c["name"] = over.get("name", f"{base}_snow_v1b")
    tiers = c.pop("tiers"); tiers.update(over.pop("tiers", {}) if over else {}); c.update(over)
    c["tiers"] = {k: {**TIER_DEFAULTS[k], **v} for k, v in tiers.items()}       # tier order = far -> near
    return c

# ============================================================================================ helpers
def smoothstep(a, b, x): x = np.clip((x - a) / (b - a + 1e-9), 0, 1); return x * x * (3 - 2 * x)
def luma(a): return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def load_rgb(p):
    a = cv2.imread(str(p), cv2.IMREAD_COLOR)
    if a is None: raise FileNotFoundError(p)
    return cv2.cvtColor(a, cv2.COLOR_BGR2RGB)
def poly(shape, polys):
    m = np.zeros(shape, np.uint8)
    for p in polys or []: cv2.fillPoly(m, [np.int32(np.round(np.float32(p)))], 1)
    return m > 0
def keepout_fade(protect, feather):
    """0 inside (and 1.5 px around) the keep-out, smoothly -> 1 at `feather` px away."""
    if not protect.any(): return np.ones(protect.shape, np.float32)
    d = cv2.distanceTransform((~protect).astype(np.uint8), cv2.DIST_L2, 5)
    return smoothstep(1.5, max(2.5, feather), d).astype(np.float32)
def cam_matrix(plate_wh, out_wh, u, z0, z1, center):
    """StablePush (identical to flames_v3.push_frame): zoom z0->z1 over smoothstep(u), cover-fit, fixed point `center`."""
    (W, H), (w, h) = plate_wh, out_wh; e = u * u * (3 - 2 * u); z = z0 + (z1 - z0) * e
    s0 = max(w / W, h / H); s = s0 * z; cx, cy = center
    ox, oy = w / 2 + (cx - 0.5) * W * s0, h / 2 + (cy - 0.5) * H * s0
    return np.float32([[s, 0, ox - s * cx * W], [0, s, oy - s * cy * H]])
def ffmpeg_writer(path, w, h, fps, crf=20):
    cmd = ["ffmpeg", "-n", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
           "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(path)]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)
def parse_size(s): w, h = map(int, str(s).lower().split("x")); return w, h

def depth_map(plate_path, P):
    """Depth Anything V2 Small (same preprocessing as depth_v1), normalised 0 far .. 1 near. Cached in snow/cache/."""
    CACHE.mkdir(exist_ok=True); f = CACHE / f"da2s_{md5(plate_path)}.npy"
    if f.exists(): return np.load(f).astype(np.float32)
    import onnxruntime as ort
    sess = ort.InferenceSession(str(DEPTH_MODEL), providers=["CPUExecutionProvider"]); i = sess.get_inputs()[0]
    h, w = P.shape[:2]; s = 518 / min(h, w); W, H = int(round(w * s / 14)) * 14, int(round(h * s / 14)) * 14
    x = cv2.resize(P, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255
    x = ((x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]).transpose(2, 0, 1)[None].astype(np.float32)
    d = np.squeeze(sess.run(None, {i.name: x})[0]); d = cv2.resize(d, (w, h), interpolation=cv2.INTER_CUBIC)
    lo, hi = np.percentile(d, [1, 99]); d = np.clip((d - lo) / (hi - lo + 1e-9), 0, 1)
    np.save(f, d.astype(np.float16)); return d.astype(np.float32)

def detect_faces(P, score=0.6):
    """YuNet at 1x and 2x (painted faces are small); returns [x, y, w, h, score] in plate px (deduped by IoU)."""
    if not FACE_MODEL.exists(): return []
    bgr = cv2.cvtColor(P, cv2.COLOR_RGB2BGR); out = []
    for sc in (1.0, 2.0):
        im = cv2.resize(bgr, None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC) if sc != 1 else bgr
        det = cv2.FaceDetectorYN.create(str(FACE_MODEL), "", (im.shape[1], im.shape[0]), score, 0.3, 5000)
        _, r = det.detect(im)
        for x in (r if r is not None else []): out.append([float(v) / sc for v in x[:4]] + [float(x[-1])])
    keep = []
    for b in sorted(out, key=lambda b: -b[4]):
        def iou(a, c):
            ix = max(0, min(a[0] + a[2], c[0] + c[2]) - max(a[0], c[0])); iy = max(0, min(a[1] + a[3], c[1] + c[3]) - max(a[1], c[1]))
            return ix * iy / (a[2] * a[3] + c[2] * c[3] - ix * iy + 1e-9)
        if all(iou(b, k) < 0.3 for k in keep): keep.append(b)
    return [[round(v, 1) for v in b] for b in keep]

# ============================================================================================ shot
class SnowShot:
    def __init__(self, cfg, size=None, fps=30):
        want = cfg.get("plate_md5")                                   # masks are hand-drawn for ONE image: refuse a swapped plate
        if want and md5(cfg["plate"]) != want:
            raise SystemExit(f"REFUSE: {cfg['plate']} md5 {md5(cfg['plate'])} != preset {want}; re-check faces/keep-out/land, then update plate_md5")
        self.cfg = cfg; self.fps = fps; self.P = load_rgb(cfg["plate"]); H, W = self.P.shape[:2]; self.H, self.W = H, W
        self.out_wh = parse_size(size or cfg["size"]); self.sf = self.out_wh[0] / 1080.0
        self.Pf = self.P.astype(np.float32); self.D = depth_map(cfg["plate"], self.P)
        # ---- keep-out (plate space): faces (auto + hand) | subject / light boxes | interiors
        self.auto_faces = detect_faces(self.P, cfg["face_score"]) if cfg.get("auto_faces") else []
        px, pt, pb = cfg["face_pad"]; boxes = [list(b) for b in cfg.get("faces", [])]
        for x, y, w, h, _ in self.auto_faces: boxes.append([x - px * w, y - pt * h, x + w * (1 + px), y + h * (1 + pb)])
        self.face_boxes = [[int(round(v)) for v in b] for b in boxes]
        face = np.zeros((H, W), bool)
        for x0, y0, x1, y1 in self.face_boxes: face[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = True
        self.protect = face | poly((H, W), cfg.get("subjects")) | poly((H, W), cfg.get("keepout")) | poly((H, W), cfg.get("interior"))
        keep = keepout_fade(self.protect, cfg["keepout_feather"])
        land = poly((H, W), cfg.get("land"))                            # ramp lives ABOVE the ground line: flakes settle into it
        landk = 1.0 - (1.0 - float(cfg.get("land_gain", 0.0))) * (1.0 - keepout_fade(land, float(cfg.get("land_feather", 60))))
        Db = cv2.GaussianBlur(self.D, (0, 0), 3); soft = cfg["depth_soft"]
        # ---- ambient light -> flake colour map (plate space)
        Lp = luma(self.Pf); sat = self.Pf.max(-1) - self.Pf.min(-1)
        hi = (Lp >= np.percentile(Lp, 96)) & (Lp <= np.percentile(Lp, 99.7)) & (sat < np.percentile(sat[Lp >= np.percentile(Lp, 96)], 50) + 1)
        self.snow_white = np.clip((self.Pf[hi].mean(0) if hi.any() else np.float32([235, 238, 242])) * float(cfg["color_gain"]), 0, 250)
        amb = cv2.GaussianBlur(self.Pf, (0, 0), cfg["ambient_sigma"] * W)
        La = np.maximum(luma(amb), 1.0)[..., None]; Lw = float(luma(self.snow_white))
        bright = np.clip(cfg["color_lift"] + (1 - cfg["color_lift"]) * (La / Lw) ** 0.6, 0, 1.05)
        base = self.snow_white[None, None] * bright
        tint = amb / La * luma(base)[..., None]
        self.col = np.clip(base * (1 - cfg["color_tint"]) + tint * cfg["color_tint"], 0, 255).astype(np.float32)
        self.amb = amb.astype(np.float32)
        # ---- per-tier mattes and flakes
        rng = np.random.default_rng(int(cfg["seed"])); w, h = self.out_wh; self.tiers = []
        for name, T in cfg["tiers"].items():
            gate = smoothstep(T["depth"] + soft, T["depth"] - soft, Db) if T["depth"] < 1 else np.ones_like(Db)
            gate = cv2.GaussianBlur(gate.astype(np.float32), (0, 0), cfg["gate_blur"])   # soft occlusion: dissolve, never cut
            M = (gate * keep * landk).astype(np.float32); M[self.protect] = 0
            n = int(T["n"]); s_lo, s_hi = T["sigma"]; v_lo, v_hi = T["speed"]; a_lo, a_hi = T["sway"]; f_lo, f_hi = T["sway_hz"]
            k = rng.uniform(0, 1, n); sig = (s_lo + (s_hi - s_lo) * k) * self.sf
            mg = int(math.ceil(4 * s_hi * 1.15 * self.sf + a_hi * self.sf)) + 8
            self.tiers.append(dict(name=name, T=T, M=M, n=n, mg=mg, sig=sig,
                x0=rng.uniform(-mg, w + mg, n), y0=rng.uniform(-mg, h + mg, n),
                vy=(v_lo + (v_hi - v_lo) * k) * rng.uniform(0.9, 1.1, n) * self.sf,
                vx=float(cfg.get("wind", 0.0)) * (0.5 + k) * rng.uniform(0.7, 1.3, n) * (0.6 + 0.4 * v_lo / 60) * self.sf,
                amp=rng.uniform(a_lo, a_hi, n) * self.sf, f=rng.uniform(f_lo, f_hi, (2, n)), ph=rng.uniform(0, 6.2832, (3, n)),
                op=T["opacity"] * rng.uniform(0.7, 1.0, n), life=rng.uniform(*cfg["life_s"], n), lph=rng.uniform(0, 1, n)))

    # ---- camera
    def M_at(self, i, n):
        z0, z1 = self.cfg["push"]; return cam_matrix((self.W, self.H), self.out_wh, i / max(n - 1, 1), z0, z1, tuple(self.cfg["push_center"]))
    def warp(self, img, A, interp=cv2.INTER_LINEAR):
        return cv2.warpAffine(img, A, self.out_wh, flags=interp, borderMode=cv2.BORDER_REFLECT)

    # ---- flakes (screen space)
    def positions(self, L, t):
        T = t + self.cfg["pre_roll"]; w, h = self.out_wh; mg = L["mg"]; f, ph, a = L["f"], L["ph"], L["amp"]
        sway = a * (np.sin(6.2832 * f[0] * T + ph[0]) + 0.4 * np.sin(6.2832 * f[1] * 2.17 * T + ph[1])) / 1.4
        flutter = 0.22 * a * np.sin(6.2832 * f[0] * T + ph[0] + 1.5708)
        x = -mg + np.mod(L["x0"] + L["vx"] * T + mg, w + 2 * mg) + sway
        y = -mg + np.mod(L["y0"] + L["vy"] * T + mg, h + 2 * mg) + flutter
        env = (0.5 - 0.5 * np.cos(6.2832 * (T / L["life"] + L["lph"]))) ** self.cfg["env_pow"]
        return x, y, env

    def frame(self, i, n, with_info=False):
        A = self.M_at(i, n); t = i / self.fps; w, h = self.out_wh
        base = self.warp(self.P, A, cv2.INTER_CUBIC); out = base.astype(np.float32)
        col = self.warp(self.col, A); prot = self.warp(self.protect.astype(np.uint8), A, cv2.INTER_NEAREST) > 0
        info = {}
        for L in self.tiers:                                             # far -> near, "over" composite
            Ms = self.warp(L["M"], A); x, y, env = self.positions(L, t); c = 0
            xi = np.clip(np.round(x).astype(int), 0, w - 1); yi = np.clip(np.round(y).astype(int), 0, h - 1)
            ins = (x > -L["mg"]) & (x < w + L["mg"]) & (y > -L["mg"]) & (y < h + L["mg"])
            peak = L["op"] * env * ins
            cover = np.clip(np.minimum.reduce([x, w - 1 - x, y, h - 1 - y]) / (3 * L["sig"]) + 0.5, 0, 1)   # part of the dab in frame
            vis = peak * Ms[yi, xi] * cover
            info[L["name"]] = int((vis > 0.08).sum()); info["_vis_" + L["name"]] = vis
            aer = L["T"]["aerial"]
            for k in np.nonzero(peak > 0.01)[0]:
                s = L["sig"][k]; sy = s * 1.12; r = int(math.ceil(3.2 * sy)) + 1; cx, cy = x[k], y[k]
                x0, y0 = max(int(cx) - r, 0), max(int(cy) - r, 0); x1, y1 = min(int(cx) + r + 2, w), min(int(cy) + r + 2, h)
                if x1 <= x0 or y1 <= y0: continue
                gx = np.exp(-0.5 * ((np.arange(x0, x1) - cx) / s) ** 2); gy = np.exp(-0.5 * ((np.arange(y0, y1) - cy) / sy) ** 2)
                a = (peak[k] * gy[:, None] * gx[None, :]).astype(np.float32) * Ms[y0:y1, x0:x1]
                if a.max() < 1e-3: continue
                cc = col[yi[k], xi[k]]
                if aer > 0: cc = cc * (1 - aer) + np.maximum(cc * 0.92, out[yi[k], xi[k]] * 1.08) * aer   # far: sit in the air
                sub = out[y0:y1, x0:x1]; sub += (cc[None, None] - sub) * a[..., None]; c += 1
        o = np.clip(out + 0.5, 0, 255).astype(np.uint8)
        o[prot] = base[prot]                                             # hard reset: keep-out is the pushed plate, bit-exact
        return (o, base, prot, info) if with_info else o

    def info(self):
        return dict(name=self.cfg["name"], plate=self.cfg["plate"], out=list(self.out_wh), auto_faces=self.auto_faces,
                    face_boxes=self.face_boxes, protect_px=int(self.protect.sum()), snow_white=[round(float(v)) for v in self.snow_white],
                    tiers={L["name"]: dict(n=L["n"], matte_px=int((L["M"] > 0.05).sum())) for L in self.tiers})

# ============================================================================================ outputs
def guard(cfg, size, mode="refuse"): return G.check_shot(cfg, None, mode=mode, out_wh=parse_size(size))
def render(cfg, out, seconds=None, size=None, crf=None, writer=None, fps=30):
    size = size or cfg["size"]; guard(cfg, size); sh = SnowShot(cfg, size, fps); w, h = sh.out_wh
    n = int(round((seconds or cfg["seconds"]) * fps))
    print("shot", json.dumps(sh.info(), default=str), file=sys.stderr, flush=True)
    p = writer or ffmpeg_writer(out, w, h, fps, crf or cfg["crf"])
    for i in range(n): p.stdin.write(sh.frame(i, n).tobytes())
    if writer is None: p.stdin.close(); assert p.wait() == 0

def reel(out, keys, seconds=4.0, crf=20, size="1080x1920", fps=30):
    cfgs = [get_cfg(k) for k in keys]
    for c in cfgs: guard(c, size)
    w, h = parse_size(size); p = ffmpeg_writer(out, w, h, fps, crf)
    for c in cfgs: render(c, out, seconds=seconds, size=size, writer=p, fps=fps)
    p.stdin.close(); assert p.wait() == 0

def sheet(out_png, keys, t=2.0, seconds=4.0, fps=30, cell=(540, 960)):
    tiles = []
    for k in keys:
        c = get_cfg(k); sh = SnowShot(c, c["size"], fps); n = int(round(seconds * fps))
        im = cv2.resize(sh.frame(int(round(t * fps)), n), cell, interpolation=cv2.INTER_AREA)
        lab = np.full((44, cell[0], 3), 24, np.uint8)
        cv2.putText(lab, f"{k.upper()}  snow_v1b  t={t:.1f}s", (12, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (230, 230, 230), 1, cv2.LINE_AA)
        tiles.append(np.vstack([im, lab]))
    gap = np.full((tiles[0].shape[0], 8, 3), 24, np.uint8); row = [tiles[0]]
    for tl in tiles[1:]: row += [gap, tl]
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    assert cv2.imwrite(str(out_png), cv2.cvtColor(np.hstack(row), cv2.COLOR_RGB2BGR))

def proof(cfg, out_json, seconds=4.0, fps=30, times=(0.0, 0.9, 1.7, 2.5, 3.3, 3.97)):
    """(1) keep-out (faces / subjects / interiors, pushed): changed px vs the pushed plate == 0 at every time.
    (2) outside the union of tier mattes: changed px == 0 (nothing moves where there is no snow, e.g. land).
    (3) determinism: two fresh SnowShot instances render bit-identical frames. (4) house guardrail (pixel density)."""
    n = int(round(seconds * fps)); a = SnowShot(cfg, cfg["size"], fps); b = SnowShot(cfg, cfg["size"], fps)
    r = dict(name=cfg["name"], plate=cfg["plate"], plate_md5=md5(cfg["plate"]), times=list(times), info=a.info(),
             protect_changed_px=[], outside_matte_changed_px=[], changed_px=[], flakes_on_screen=[], frame_md5=[], det_identical=True,
             guardrails=guard(cfg, cfg["size"], mode="warn"))
    U = np.zeros((a.H, a.W), np.float32)
    for L in a.tiers: U = np.maximum(U, L["M"])
    for t in times:
        i = int(round(t * fps)); o, base, prot, inf = a.frame(i, n, with_info=True); o2 = b.frame(i, n)
        ch = np.abs(o.astype(int) - base.astype(int)).max(-1) > 0
        Us = a.warp(U, a.M_at(i, n)) > 0
        r["protect_changed_px"].append(int((ch & prot).sum())); r["outside_matte_changed_px"].append(int((ch & ~Us).sum()))
        r["changed_px"].append(int(ch.sum())); r["flakes_on_screen"].append({k: v for k, v in inf.items() if not k.startswith("_")})
        r["frame_md5"].append(hashlib.md5(o.tobytes()).hexdigest()); r["det_identical"] &= bool((o == o2).all())
    r["pass_keepout_0px"] = max(r["protect_changed_px"]) == 0; r["pass_outside_0px"] = max(r["outside_matte_changed_px"]) == 0
    r["pass"] = r["pass_keepout_0px"] and r["pass_outside_0px"] and r["det_identical"] and all(g["ok"] for g in r["guardrails"])
    json.dump(r, open(out_json, "x"), indent=1, default=float); print(json.dumps({k: r[k] for k in r if k != "info"}, default=float)); return r

def series_stats(v, fps=30, win=1.0, step=0.5):
    v = np.asarray(v, np.float64); m = int(win * fps); sw = []
    for i in range(0, len(v) - m + 1, int(step * fps)): x = v[i:i + m]; sw.append((x.max() - x.min()) / max(x.mean(), 1e-6))
    x = v - v.mean(); Pw = np.abs(np.fft.rfft(x)) ** 2; f = np.fft.rfftfreq(len(x), 1 / fps)
    return dict(swing_1s_median_pct=round(100 * float(np.median(sw)), 3), swing_1s_max_pct=round(100 * float(np.max(sw)), 3),
                energy_above_5hz=round(float(Pw[f > 5].sum() / max(Pw[1:].sum(), 1e-12)), 4))

def stats(cfg, out_json, seconds=4.0, fps=30):
    """Phone (360x640) metrics on the framed output, snow vs the SAME pushed plate (so the push itself is excluded).
    flakes_on_screen: flakes whose peak alpha x matte at the centre > 0.08 (per tier, mean/min/max over frames).
    flake_alpha_step: per-flake |change| of peak alpha x matte at its centre between frames (max / p99): the real pop test
    (a flake that appears or vanishes in one frame would step by its full opacity ~0.5; fades step << 0.1).
    pop_px: max over frames of phone px whose snow delta jumps >= 12 / >= 8 levels in ONE frame (~0 = no popping).
    read_px_1s: phone px whose snow delta range in the first 1 s >= 6 levels (motion visible at phone size).
    whole_frame: mean-luma swing / >5 Hz energy of the frame (flicker check)."""
    n = int(round(seconds * fps)); sh = SnowShot(cfg, cfg["size"], fps); seq, bas, cnt, vis = [], [], [], []
    ph = lambda im: cv2.resize(im, (360, 640), interpolation=cv2.INTER_AREA)
    for i in range(n):
        o, base, _, inf = sh.frame(i, n, with_info=True); vis.append(np.concatenate([inf.pop(k) for k in [k for k in inf if k.startswith("_vis_")]])); seq.append(luma(ph(o).astype(np.float32))); bas.append(luma(ph(base).astype(np.float32))); cnt.append(inf)
    seq, bas = np.stack(seq), np.stack(bas); d = seq - bas; jump = np.abs(np.diff(d, axis=0))
    fl = {k: dict(mean=round(float(np.mean([c[k] for c in cnt])), 1), min=int(min(c[k] for c in cnt)), max=int(max(c[k] for c in cnt))) for k in cnt[0]}
    tot = [sum(c.values()) for c in cnt]; vs = np.abs(np.diff(np.stack(vis), axis=0))
    r = dict(name=cfg["name"], seconds=seconds, phone="360x640", push=cfg["push"], flakes_on_screen=fl,
             flakes_on_screen_total=dict(mean=round(float(np.mean(tot)), 1), min=int(min(tot)), max=int(max(tot))),
             flake_alpha_step_max=round(float(vs.max()), 4), flake_alpha_step_p99=round(float(np.percentile(vs[vs > 0], 99)), 4),
             pop_px_max_per_frame_jump_ge12=int((jump >= 12).sum((1, 2)).max()), pop_px_max_per_frame_jump_ge8=int((jump >= 8).sum((1, 2)).max()),
             read_px_1s_range_ge6=int(((d[:30].max(0) - d[:30].min(0)) >= 6).sum()), max_abs_delta_phone=round(float(np.abs(d).max()), 1),
             mean_abs_delta_phone=round(float(np.abs(d).mean()), 4), whole_frame=series_stats(seq.mean((1, 2)), fps),
             snow_energy=series_stats(np.abs(d).mean((1, 2)) + 1.0, fps))
    json.dump(r, open(out_json, "x"), indent=1); print(json.dumps(r)); return r

def overlay(cfg, out_png):
    sh = SnowShot(cfg, cfg["size"]); im = sh.P.astype(np.float32); o = im * 0.45
    for L, c in zip(sh.tiers, ([255, 80, 60], [80, 255, 80], [80, 140, 255])):
        o += 0.55 * L["M"][..., None] * np.float32(c) / len(sh.tiers)
    o[sh.protect] = o[sh.protect] * 0.4 + np.float32([255, 0, 255]) * 0.6
    for x, y, w, h, s in sh.auto_faces: cv2.rectangle(o, (int(x), int(y)), (int(x + w), int(y + h)), (255, 255, 0), 2)
    D = np.repeat((sh.D * 255)[..., None], 3, -1)
    assert cv2.imwrite(str(out_png), cv2.cvtColor(np.clip(np.hstack([im, o, D]), 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR))

if __name__ == "__main__":
    a = sys.argv[1:]; cmd = a[0]
    def opt(k, d=None): return a[a.index(k) + 1] if k in a else d
    keys = opt("--presets", "b11,b12,b17").split(",")
    if cmd == "presets": print(json.dumps({k: get_cfg(k) for k in PRESETS}, indent=1)); sys.exit(0)
    out = Path(a[1] if cmd in ("reel", "sheet") else a[2]); assert not out.exists(), f"never overwrite: {out}"
    if cmd == "reel": reel(str(out), keys, seconds=float(opt("--seconds", 4.0)), crf=int(opt("--crf", 20)), size=opt("--size", "1080x1920"))
    elif cmd == "sheet": sheet(str(out), keys, t=float(opt("--t", 2.0)))
    else:
        cfg = get_cfg(a[1])
        if cmd == "render": render(cfg, str(out), seconds=float(opt("--seconds", cfg["seconds"])), size=opt("--size"), crf=opt("--crf"))
        elif cmd == "proof": proof(cfg, str(out))
        elif cmd == "stats": stats(cfg, str(out))
        elif cmd == "overlay": overlay(cfg, str(out))
        else: raise SystemExit(__doc__)
