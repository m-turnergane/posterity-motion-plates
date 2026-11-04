#!/usr/bin/env python3
"""doc_reveal_v1 -- candle-light DOCUMENT REVEALS on existing Edward II plates (Posterity engine R&D).

One shot = one JSON config in ./configs. Per frame, in PLATE space:
  1. locked look  : fx_v1c.PlateFX (fx_candle flicker + spill, torch_v1c) rendered with its own camera/parallax OFF
  2. + smoke_v2   : candle wick wisps (SmokeScene delta over the plate; its push_frame is never used)
  3. x document   : a smooth, low-frequency multiplicative gain field inside the feathered document mask.
                    'reveal'     -> the page starts dim and a soft candle-light front sweeps it up to EXACTLY the
                                    locked look (gain 1.0) -- a gain field cannot draw marks.
                    'later_copy' -> static register-copy surface (DOC-F1): cooler vellum tone, faded iron-gall ink,
                                    low-frequency foxing and a gutter shadow, then the same reveal. Only existing plate
                                    detail is kept (scaled down) -- no new lines, no seal, no flourish, no text.
  4. protect      : faces / land / water polygons are restored to the plate bit-exactly (0 changed px).
Then ONE camera transform: flat shots -> one cv2.warpAffine (uniform scale about an anchor, push 1.00 -> 1.06);
action plates -> depth_v1.DepthShot, the plate-space result passed as plate_fx (depth's single transform per layer).

Locked files are imported read-only by path and never edited. Usage:
  python doc_reveal_v1.py configs/*.json --reel final/doc_reveal_v1_reel_9x16.mp4
"""
import argparse, hashlib, importlib.util, json, math, os, subprocess, sys
from pathlib import Path
import cv2, numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent                                   # /workspace/posterity

def _load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

G     = _load("guardrails", ROOT / "motion/guardrails.py")
FX    = _load("fx_v1c",     ROOT / "standalones/edward-ii/edit/fx_v1c.py")
SMOKE = _load("smoke_v2",   ROOT / "engine-rnd/smoke/smoke_v2.py")
# LOCKED b10 full stack (PRESETS 'Stacking: depth_v1 + torch_v1c + smoke_v2', 2026-10-30 7:11pm ET): imported read-only and
# used as-is for stacked torch shots (depth = the only camera, torch_v1c as plate_fx with the face keep-out, smoke_v2 x0.4 on
# the near layer). Its own md5 asserts refuse to load if a locked file changed. Its depth_v1 module object is shared.
FS    = _load("fullstack_v1", ROOT / "engine-rnd/hero/fullstack_v1.py")
DEPTH = FS.DEPTH
LOCKED = {p: None for p in ["motion/guardrails.py", "standalones/edward-ii/edit/fx_v1c.py", "engine-rnd/smoke/smoke_v2.py",
                            "engine-rnd/depth/depth_v1.py", "motion/presets/locked/engine/animate_b3_cb9e2b88.py", "motion/PRESETS.md",
                            "engine-rnd/hero/fullstack_v1.py", "engine-rnd/smoke/configs/b10_wall_torch.json"]}

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""): h.update(c)
    return h.hexdigest()

def smoothstep(x): x = np.clip(x, 0.0, 1.0); return x * x * (3 - 2 * x)
def lum(a): return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]

def poly_bin(shape, polys):
    m = np.zeros(shape, np.uint8)
    for p in polys: cv2.fillPoly(m, [np.int32(np.round(p))], 1)
    return m.astype(bool)

# ----------------------------------------------------------------------------------------------- document effects
class DocumentLight:
    """Low-frequency gain field over the document. All spatial structure is either the feathered page mask or
    smooth functions of one coordinate along the sweep axis, so it cannot add text-like (high-frequency) marks."""

    def __init__(s, cfg, shape):
        H, W = shape; r = cfg["reveal"]; s.r = r
        bin_ = poly_bin(shape, [cfg["doc_poly"]]); s.bin = bin_
        s.M = cv2.GaussianBlur(bin_.astype(np.float32), (0, 0), float(r.get("feather", 5.0)))
        ys, xs = np.nonzero(bin_); a = np.float32(r["axis"]); a /= np.linalg.norm(a)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); proj = xx * a[0] + yy * a[1]
        pv = xs * a[0] + ys * a[1]; s.s = (proj - pv.min()) / max(pv.max() - pv.min(), 1.0)  # 0 at the light side
        s.tint = np.float32(r.get("tint", [1.0, 0.95, 0.85]))
        s.copy_gain = None

    def gain(s, t):
        """per-pixel RGB gain (plate space). 1.0 everywhere outside the page and everywhere after the sweep."""
        r = s.r; u = smoothstep((t - r["t0"]) / r["dur"])
        front = -r["soft"] + (1 + 2 * r["soft"]) * u                       # sweep from before the page to past it
        lit = smoothstep((front - s.s) / r["soft"] + 0.5)                   # 0 ahead of the front, 1 behind it
        glint = r["glint"] * np.exp(-((s.s - front) / r["glint_w"]) ** 2) * math.sin(math.pi * u)
        g = r["g0"] + (1 - r["g0"]) * lit                                   # dim page -> native level
        G = 1 + ((g + glint)[..., None] * (1 + (s.tint - 1) * glint[..., None] / max(r["glint"], 1e-6)) - 1) * s.M[..., None]
        if s.copy_gain is not None: G = G * s.copy_gain
        return G.astype(np.float32)

    def build_later_copy(s, P, c):
        """DOC-F1 register-copy surface: a STATIC gain map = target / plate, computed in the log domain as
        new_tone(low-freq) + k * existing_detail. Detail is only scaled (k<1), never created."""
        Pf = P.astype(np.float32) + 1.0; L = np.log(Pf); m = s.bin.astype(np.float32)
        sig = float(c.get("tone_sigma", 14))
        den = cv2.GaussianBlur(m, (0, 0), sig)[..., None] + 1e-6
        def nblur(x): return cv2.GaussianBlur(x * m[..., None], (0, 0), sig) / den   # mask-normalised blur (page only)
        T = nblur(L)                                                        # local paper tone (log), low-freq
        D = L - T                                                           # existing detail (ink, fibres)
        Dl = lum(D)
        hue = np.float32(c.get("ink_hue", [0.78, 0.92, 1.18]))              # iron-gall brown: ink loses blue first
        Dn = c.get("ink_keep", 0.62) * Dl[..., None] * hue + c.get("fibre_keep", 0.7) * (D - Dl[..., None])
        Tl = lum(T)
        vel = np.float32(c.get("vellum", [228, 220, 200])); vel = np.log(vel / lum(vel[None])[0])
        lift = float(c.get("tone_lift", 0.10))
        a = float(c.get("vellum_mix", 0.5))                                 # keep part of the candle colour cast of the room
        Tn = Tl[..., None] + (1 - a) * (T - Tl[..., None]) + a * vel + lift  # same light falloff, register-vellum colour
        H, W = P.shape[:2]; rng = np.random.default_rng(int(c.get("seed", 1368)))
        mot = cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), 16); mot /= mot.std() + 1e-6
        Tn = Tn + float(c.get("mottle", 0.05)) * mot[..., None]
        fox = np.zeros((H, W), np.float32); ys, xs = np.nonzero(s.bin)
        for _ in range(int(c.get("foxing_n", 9))):
            i = rng.integers(len(xs)); cv2.circle(fox, (int(xs[i]), int(ys[i])), int(rng.integers(3, 8)), float(rng.uniform(0.5, 1)), -1)
        fox = cv2.GaussianBlur(fox, (0, 0), 6.0)
        Tn = Tn + np.log(np.float32(c.get("fox_col", [0.92, 0.86, 0.76]))) * fox[..., None] * float(c.get("foxing", 1.0))
        gx0, gx1 = c["gutter_x"]; gut = smoothstep((np.arange(W, dtype=np.float32) - gx0) / max(gx1 - gx0, 1))  # 0 at spine
        Tn = Tn + np.log(c.get("gutter_min", 0.72) + (1 - c.get("gutter_min", 0.72)) * gut)[None, :, None]
        out = np.exp(Tn + Dn)
        gm = out / Pf
        s.copy_gain = (1 + (gm - 1) * s.M[..., None]).astype(np.float32)   # feathered into the page only

# ----------------------------------------------------------------------------------------------- one shot
class Shot:
    def __init__(s, path):
        s.cfg = c = json.load(open(path)); s.name = c["name"]; s.n = int(round(c["seconds"] * c.get("fps", 30)))
        s.fps = c.get("fps", 30); s.W, s.H = c.get("out_wh", [1080, 1920])
        key = FX.plate_key(c["plate"]); spec = dict(FX.SPECS[key])
        for k in c.get("fx_drop", []): spec.pop(k, None)                    # in-memory only (e.g. mist on land); file untouched
        FX.SPECS[key] = spec
        s.fx = FX.PlateFX(c["plate"], seed=c.get("seed", 0)); s.fx.par = None  # its own parallax camera OFF: one camera
        s.P = s.fx.P; s.Pf = s.P.astype(np.float32); H, W = s.P.shape[:2]
        sm = c.get("smoke")
        s.smoke = SMOKE.SmokeScene(s.P, sm) if sm else None
        s.doc = DocumentLight(c, (H, W))
        if c.get("treatment") == "later_copy": s.doc.build_later_copy(s.P, c["later_copy"])
        s.prot = {k: poly_bin((H, W), [p]) for k, p in c.get("protect", {}).items()}
        s.prot_all = np.zeros((H, W), bool)
        for m in s.prot.values(): s.prot_all |= m
        s.keep = np.zeros((H, W), np.float32); fby = c.get("protect_feather_by_region", {})
        for k, m in s.prot.items():                                           # feather OUTWARD only: inside stays exact
            d = cv2.distanceTransform((~m).astype(np.uint8), cv2.DIST_L2, 5)
            s.keep = np.maximum(s.keep, np.clip(1 - d / float(fby.get(k, c.get("protect_feather", 18))), 0, 1).astype(np.float32))
        cam = c["camera"]; s.mode = cam["mode"]
        s.stack = None
        if s.mode == "fullstack":                                           # locked b10 stack, unchanged except seconds
            s.stack = FS.Stack(seconds=c["seconds"], fps=s.fps, smoke_gain=float(cam.get("smoke_gain", 0.4)))
            assert Path(c["plate"]).resolve() == FS.PLATE.resolve()
            s.depth = s.stack.sh; s.o = s.depth.overscan((s.W, s.H), s.n); s.E = s.stack.E; s.mode = "depth"
            s.guard = s.depth.guard((s.W, s.H), mode="refuse", n=s.n); s.density = s.guard[0]["pixel_density"]
        elif s.mode == "depth":
            dc = json.load(open(ROOT / cam["config"])); dc["seconds"] = c["seconds"]; dc["name"] = s.name
            s.depth = DEPTH.DepthShot(dc); s.o = s.depth.overscan((s.W, s.H), s.n)
            s.E = DEPTH.smooth_progress(s.n, fps=s.fps, **s.depth.cam().get("ease", {}))
            s.guard = s.depth.guard((s.W, s.H), mode="refuse", n=s.n)
            s.density = s.guard[0]["pixel_density"]
        else:
            s.E = DEPTH.smooth_progress(s.n, fps=s.fps); cz = float(cam.get("crop_zoom", 1.0)); z0, z1 = cam["push"]
            assert 1.0 <= z0 <= z1 <= 1.06, "house rule: push 1.00 -> 1.06 at most"
            s.density = G.check_pixel_density(c["plate"], (s.W, s.H), (z0, z1), crop_zoom=cz, mode="refuse")
            cover = max(s.W / W, s.H / H); s.s0 = cover * cz
            vw, vh = s.W / s.s0, s.H / s.s0; al = cam.get("crop_align", [0.5, 0.5])
            s.win0 = ((W - vw) * al[0], (H - vh) * al[1])                   # frame-0 window origin (plate px)
            s.A = np.float32(cam["anchor"]); s.As = (s.A - np.float32(s.win0)) * s.s0
            s.warps = 0

    def _finish(s, img):
        k = s.keep[..., None]; img = img * (1 - k) + s.Pf * k
        out = np.clip(np.rint(img), 0, 255).astype(np.uint8)
        out[s.prot_all] = s.P[s.prot_all]                                   # bit-exact
        return out

    def plate_frame(s, t, with_ref=False):
        """delivered plate frame = locked looks (fx + smoke) x document gain. with_ref also returns the same
        locked-look frame WITHOUT the document gain (proof reference that isolates the document effect)."""
        if s.stack is not None:                                             # torch_v1c with the locked face keep-out
            img = s.stack.torch(t) * 255.0; s._S = s.stack.smoke(t); s._t = t     # smoke rides the near layer (to_output)
        else:
            img = s.fx.render(t, 0.0).astype(np.float32)
            if s.smoke is not None: img += s.smoke.frame(t).astype(np.float32) - s.Pf
        out = s._finish(img * s.doc.gain(t))
        return (out, s._finish(img)) if with_ref else out

    def cam_M(s, e):
        z0, z1 = s.cfg["camera"]["push"]; S = s.s0 * (z0 + (z1 - z0) * e)
        return np.float32([[S, 0, s.As[0] - S * s.A[0]], [0, S, s.As[1] - S * s.A[1]]])

    def to_output(s, pf, i, fid=None):
        if s.mode == "depth":
            return s.dframe(pf, i, fid)
        s.warps += 1                                                        # the ONE resample of a flat shot
        return cv2.warpAffine(pf, s.cam_M(s.E[i]), (s.W, s.H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)

    def dframe(s, pf, i, fid, smoke=True):
        """depth_v1 frame: pf (plate-space uint8 or None = untouched plate) as plate_fx; locked-stack smoke on the near layer."""
        kw = {}
        if pf is not None: kw["plate_fx"] = lambda _t: pf.astype(np.float32) / 255.0
        if s.stack is not None and smoke: S = s._S; kw["layer_fx"] = {"near": lambda _t: S}; kw["t"] = s._t
        return DEPTH.to8(s.depth.frame(s.E[i], (s.W, s.H), s.o, fid=fid, **kw))

    def window_ok(s):
        if s.mode == "depth": return True
        for e in (0.0, 1.0):
            M = s.cam_M(e); S = M[0, 0]; x0, y0 = -M[0, 2] / S, -M[1, 2] / S; x1, y1 = x0 + s.W / S, y0 + s.H / S
            if x0 < -1e-3 or y0 < -1e-3 or x1 > s.P.shape[1] + 1e-3 or y1 > s.P.shape[0] + 1e-3: return False
        return True

# ----------------------------------------------------------------------------------------------- proofs
def legibility(P, out, docbin, interior_px=12, lo_ok=40.0, hi_ok=250.0):
    """No new high-frequency, text-like marks inside the document (plate space), out vs reference P.
    Measured on the page INTERIOR (mask eroded by interior_px, past the soft mask edge, where fabricated writing
    would have to sit); the boundary band (soft page-edge falloff) is reported separately.
    hp: p99 |high-pass of log(out/ref)| on pixels the 8-bit ratio can measure (ref luma 40..250: below, rounding of
        dimmed ink dominates; above, clipping) -- a smooth gain field leaves ~0, painted marks do not.
    new_edges: (ref luma 40..250 only; dark-shadow flips reported as new_edges_in_dark_px) Canny on LOCAL-CONTRAST images (L / blur8(L)) so a smooth gain cannot create or remove edges but a
        new stroke does; edges >2px from any reference edge. new_edges_abs (absolute Canny 60/140) reported too."""
    inner = cv2.erode(docbin.astype(np.uint8), np.ones((2 * interior_px + 1,) * 2, np.uint8)).astype(bool)
    band = cv2.dilate(docbin.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & ~inner
    Lp, Lo = lum(P.astype(np.float32)), lum(out.astype(np.float32))
    ok = inner & (Lp >= lo_ok) & (Lp <= hi_ok) & (Lo <= hi_ok)
    r = np.log((Lo + 0.5) / (Lp + 0.5)); w = ok.astype(np.float32)
    rb = cv2.GaussianBlur(r * w, (0, 0), 3.0) / (cv2.GaussianBlur(w, (0, 0), 3.0) + 1e-6); hp = r - rb
    lp, lo = np.log(Lp + 1), np.log(Lo + 1)
    hpp, hpo = lp - cv2.GaussianBlur(lp, (0, 0), 3.0), lo - cv2.GaussianBlur(lo, (0, 0), 3.0)
    A, B = hpo[inner], hpp[inner]; ncc = float(((A - A.mean()) * (B - B.mean())).mean() / (A.std() * B.std() + 1e-9))
    def lc(L): return np.uint8(np.clip(128 * (L + 4) / (cv2.GaussianBlur(L, (0, 0), 8.0) + 4), 0, 255))
    def edges(a, b, lo_t, hi_t):
        ep = cv2.Canny(a, lo_t, hi_t) > 0; eo = cv2.Canny(b, lo_t, hi_t) > 0
        return ep, eo & ~cv2.dilate(ep.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    ep, new = edges(lc(Lp), lc(Lo), 60, 140)
    meas = (Lp >= lo_ok) & (Lp <= hi_ok)               # where 8 bits can measure contrast; below, dimmed shadow pixels flip
    _, new_abs = edges(np.uint8(np.clip(Lp, 0, 255)), np.uint8(np.clip(Lo, 0, 255)), 60, 140)
    lvp = float(cv2.Laplacian(lp, cv2.CV_32F)[inner].var()); lvo = float(cv2.Laplacian(lo, cv2.CV_32F)[inner].var())
    return dict(interior_px_area=int(inner.sum()), hp_measured_px=int(ok.sum()),
                hp_logratio_p99=round(float(np.percentile(np.abs(hp[ok]), 99)), 4) if ok.sum() > 100 else 0.0,
                detail_ncc_vs_plate=round(ncc, 4), new_edges_px=int((new & inner & meas).sum()), plate_edges_px=int((ep & inner).sum()),
                new_edges_in_dark_px=int((new & inner & ~meas).sum()),
                new_edges_abs_px=int((new_abs & inner).sum()),
                lapvar_log_ratio=round(lvo / max(lvp, 1e-12), 4), boundary_new_edges_px=int((new & band).sum()))

def series(v, fps):
    v = np.asarray(v, np.float64); n = fps; sw = []
    for i in range(0, len(v) - n + 1, fps // 2): w = v[i:i + n]; sw.append((w.max() - w.min()) / max(w.mean(), 1e-6))
    x = v - v.mean(); Pw = np.abs(np.fft.rfft(x)) ** 2; f = np.fft.rfftfreq(len(x), 1 / fps)
    return dict(swing_1s_max_pct=round(100 * float(max(sw)), 3), energy_above_5hz=round(float(Pw[f > 5].sum() / max(Pw[1:].sum(), 1e-12)), 5))

# ----------------------------------------------------------------------------------------------- IO
def writer(path, W, H, fps, crf):
    return subprocess.Popen(["ffmpeg", "-n", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                             "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(path)], stdin=subprocess.PIPE)

def run_shot(s, reel_w=None, poc=True, still_t=None):
    c = s.cfg; fps = s.fps; prot_changed = {k: 0 for k in s.prot}; leg = []; lf, ld, lr, lk, ldoc = [], [], [], [], []; vis = {}
    pw = writer(HERE / "poc" / f"{s.name}_540p.mp4", 540, 960, fps, 23) if poc else None
    docb = s.doc.bin
    if s.mode == "depth": DEPTH.WARP_LOG.clear()
    for i in range(s.n):
        t = i / fps; pf, rf = s.plate_frame(t, with_ref=True)
        for k, m in s.prot.items(): prot_changed[k] += int((pf[m] != s.P[m]).any(-1).sum())
        if i % 15 == 0 or i == s.n - 1:
            leg.append(dict(t=round(t, 2), **legibility(rf, pf, docb), vs_untouched_plate=legibility(s.P, pf, docb)))
        o = s.to_output(pf, i, fid=i)
        if reel_w: reel_w.stdin.write(o.tobytes())
        if pw: pw.stdin.write(cv2.resize(o, (540, 960), interpolation=cv2.INTER_AREA).tobytes())
        if still_t is not None and i == int(round(still_t * fps)):
            cv2.imwrite(str(HERE / "final" / f"{s.name}_still.png"), cv2.cvtColor(o, cv2.COLOR_RGB2BGR))
        # phone 360x640 (proof-only renders; the delivered frame above used exactly one camera transform):
        # effect-only = out vs the same camera over the untouched plate, and the document ROI
        ph = cv2.resize(o, (360, 640), interpolation=cv2.INTER_AREA).astype(np.float32); Lo = lum(ph); lf.append(float(Lo.mean()))
        if s.mode == "depth":
            ref = s.dframe(rf, i, ("ref", i)); base = s.dframe(None, i, ("base", i), smoke=False)
            M = s.depth.layer_affine(len(s.depth.cards) - 1, s.E[i], (s.W, s.H), s.o)       # the letter rides the near card
        else:
            M = s.cam_M(s.E[i]); base = cv2.warpAffine(s.P, M, (s.W, s.H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
            ref = cv2.warpAffine(rf, M, (s.W, s.H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
        dm = cv2.resize(cv2.warpAffine(docb.astype(np.uint8) * 255, M, (s.W, s.H)), (360, 640), interpolation=cv2.INTER_AREA) > 127
        Lb = lum(cv2.resize(base, (360, 640), interpolation=cv2.INTER_AREA).astype(np.float32)); lr.append(float(Lo.mean() / max(Lb.mean(), 1e-6)))
        Lr = lum(cv2.resize(ref, (360, 640), interpolation=cv2.INTER_AREA).astype(np.float32)); lk.append(float(Lr.mean() / max(Lb.mean(), 1e-6)))
        ldoc.append(float(Lo.mean() / max(Lr.mean(), 1e-6)))
        if i in (0, fps): vis[i] = Lo - Lr
        ld.append(float(Lo[dm].mean()) if dm.any() else 0.0)
    if pw: pw.stdin.close(); pw.wait()
    vis1 = int((np.abs(vis[fps] - vis[0]) > 12).sum()) if fps in vis else None
    full, docs, eff, looks, deff = series(lf, fps), series(ld, fps), series(lr, fps), series(lk, fps), series(ldoc, fps)
    single = (dict(kind="flat: one cv2.warpAffine per delivered frame (uniform scale + translate, LANCZOS4); no fx camera, no smoke push_frame",
                   delivered_warps=s.warps, frames=s.n, window_inside_plate=s.window_ok(), pass_=bool(s.warps == s.n and s.window_ok()))
              if s.mode != "depth" else _depth_single(s))
    lmax = dict(hp_logratio_p99=max(x["hp_logratio_p99"] for x in leg), new_edges_px=max(x["new_edges_px"] for x in leg),
                lapvar_log_ratio=max(x["lapvar_log_ratio"] for x in leg), detail_ncc_min=min(x["detail_ncc_vs_plate"] for x in leg),
                boundary_new_edges_px=max(x["boundary_new_edges_px"] for x in leg))
    # gate calibrated by legibility_control.py (proofs/legibility_positive_control.json): real reveal frames hp <= ~0.018,
    # a painted 2-11 letter word on the page 0.023-0.29. Canny new-edge counts did NOT separate real from fake (8-bit
    # threshold flips under dimming), so they are reported, and gated only on the static later-copy surface.
    copy = c["treatment"] != "reveal"
    leg_gate = dict(hp_logratio_p99_max=None if copy else 0.02, lapvar_log_ratio_max=1.0 if copy else 1.05, detail_ncc_min=0.9,
                    new_edges_px_max=max(5, int(0.005 * leg[0]["plate_edges_px"])) if copy else None)
    leg_pass = (lmax["lapvar_log_ratio"] <= leg_gate["lapvar_log_ratio_max"] and lmax["detail_ncc_min"] >= 0.9
                and (copy or lmax["hp_logratio_p99"] <= 0.02) and (not copy or lmax["new_edges_px"] <= leg_gate["new_edges_px_max"]))
    pr = dict(shot=s.name, document=c["document"], treatment=c["treatment"], plate=c["plate"], plate_md5=md5(c["plate"]),
              seconds=c["seconds"], camera=c["camera"], pixel_density=s.density,
              looks=dict(plate_fx="fx_v1c.PlateFX (fx_candle flicker+spill / torch_v1c), own parallax OFF", fx_drop=c.get("fx_drop", []),
                         smoke_v2=bool(s.smoke) or s.stack is not None, depth_v1=s.mode == "depth",
                         locked_stack=("engine-rnd/hero/fullstack_v1.Stack (PRESETS 'Stacking: depth_v1 + torch_v1c + smoke_v2'): torch_v1c face "
                                       f"keep-out pad 6 / feather 18, smoke_v2 alpha x{s.stack.sg}, smoke on the near layer, depth the only camera; "
                                       f"smoke_v2.push_frame calls {FS.CAM_CALLS['smoke_v2.push_frame']}") if s.stack is not None else None),
              protected_pixels=dict(note="plate space, every frame, changed px inside face/land/water polygons", by_region=prot_changed,
                                    total=sum(prot_changed.values()), pass_=sum(prot_changed.values()) == 0),
              legibility=dict(note="plate space, page interior (mask eroded 12px), out vs the same locked-look frame without the document gain "
                                   "(vs_untouched_plate also listed per sample); hp = p99 |log(out/ref) - blur3| on ref luma 40..250 (a gain field leaves ~0); "
                                   "detail_ncc = correlation of the high-pass of out vs ref (marks are the plate's own); new edges = local-contrast Canny edges >2px "
                                   "from any ref edge (abs-threshold count reported); lapvar = var(Laplacian(log L)) out/plate (<=1: never sharper/more marks). Boundary band reported only.", samples=leg, worst=lmax, gate=leg_gate, pass_=bool(leg_pass), text_added=False),
              phone_360x640=dict(note="all at 360x640, same camera. document_effect = mean luma(out) / mean luma(locked-look frame without the "
                                      "document gain): the new effect alone, gated swing<8%/1s and >5Hz<0.05. locked_looks = locked-look frame / untouched "
                                      "plate (fx_candle / torch_v1c / smoke_v2 as locked; reported, not re-tuned). all_effects = out / untouched plate. "
                                      "document_roi swing is the one-way reveal (dim -> native), gated on >5 Hz only. first_second = px whose "
                                      "document-effect luma changes >12 between t=0 and t=1s.",
                                 first_second_effect_px_gt12=vis1, first_second_pass=bool(vis1 and vis1 >= 150),
                                 full_frame_with_camera=full, document_effect_full_frame=deff, locked_looks_full_frame=looks,
                                 all_effects_full_frame=eff, document_roi=docs,
                                 pass_=bool(full["energy_above_5hz"] < 0.05 and eff["energy_above_5hz"] < 0.05 and docs["energy_above_5hz"] < 0.05
                                            and deff["energy_above_5hz"] < 0.05 and deff["swing_1s_max_pct"] < 8)),
              single_camera=single)
    pr["pass"] = bool(pr["protected_pixels"]["pass_"] and leg_pass and pr["phone_360x640"]["pass_"] and pr["phone_360x640"]["first_second_pass"]
                      and s.density.get("pass", False) and (single.get("pass_", True) and single.get("window_inside_plate", True)))
    json.dump(pr, open(HERE / "proofs" / f"{s.name}.json", "w"), indent=1, default=float)
    return pr

def _depth_single(s):
    cnt = {}
    for tag in DEPTH.WARP_LOG:
        if isinstance(tag[0], int): cnt[tag] = cnt.get(tag, 0) + 1
    ncard = len(s.depth.cards); frames = {t[0] for t in cnt}
    ok = all(v == 1 for v in cnt.values()) and len(cnt) == len(frames) * ncard
    ids = [0, s.n // 2, s.n - 1]
    rig = DEPTH.rigidity(s.depth, (s.W, s.H), s.o, s.E, ids)
    return dict(kind="depth_v1: one warp per layer card per frame (WARP_LOG), effects passed as plate_fx", frames=len(frames), cards=ncard,
                max_warps_per_layer_frame=max(cnt.values()), overscan=round(s.o, 5),
                rigidity=[dict(name=r["name"], layer=r["layer"], pass_=r["pass_"]) for r in rig],
                pass_=bool(ok and all(r["pass_"] for r in rig)))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("configs", nargs="+"); ap.add_argument("--reel"); ap.add_argument("--no-poc", action="store_true")
    a = ap.parse_args()
    if a.reel and os.path.exists(a.reel): sys.exit(f"refusing to overwrite {a.reel}")
    pre = {p: md5(ROOT / p) for p in LOCKED}
    shots = [Shot(c) for c in a.configs]
    rw = writer(a.reel, shots[0].W, shots[0].H, shots[0].fps, 20) if a.reel else None
    res = []
    for s in shots:
        pr = run_shot(s, rw, poc=not a.no_poc, still_t=s.cfg.get("still_t", s.cfg["seconds"] * 0.6)); res.append(pr)
        print(s.name, "PASS" if pr["pass"] else "FAIL", "density", s.density.get("ratio"), "prot", pr["protected_pixels"]["total"],
              "leg", pr["legibility"]["worst"], "phone", pr["phone_360x640"]["first_second_effect_px_gt12"], pr["phone_360x640"]["document_effect_full_frame"], pr["phone_360x640"]["locked_looks_full_frame"],
              pr["phone_360x640"]["document_roi"], flush=True)
    if rw:
        rw.stdin.close(); rw.wait()
        post = {p: md5(ROOT / p) for p in LOCKED}
        cuts, t = [], 0.0
        for s in shots: cuts.append(dict(shot=s.name, document=s.cfg["document"], start_s=round(t, 3), frames=s.n, transition_in="hard cut")); t += s.n / s.fps
        man = dict(reel=a.reel, md5=md5(a.reel), seconds=round(t, 3), size=[shots[0].W, shots[0].H], fps=shots[0].fps, cuts=cuts,
                   dissolves=0, c17_note="DOC-K1 block then DOC-F1 block; hard cuts only, no dissolve/morph between documents; distinct surfaces",
                   all_shots_pass=all(r["pass"] for r in res), locked_md5_unchanged=pre == post, locked_md5=post)
        json.dump(man, open(HERE / "proofs" / "reel_manifest.json", "w"), indent=1); print("reel", a.reel, man["md5"], man["seconds"], "s")

if __name__ == "__main__":
    main()
