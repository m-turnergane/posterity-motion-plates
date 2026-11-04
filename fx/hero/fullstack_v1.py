"""b10 Corfe full-stack stress test (engine-rnd/hero).  NO body motion.

Stack (all LOCKED modules imported read-only by path, md5-checked at import):
  depth_v1  (engine-rnd/depth/depth_v1.py)      -- THE camera: 2 rigid cards, one uniform-scale+translate warp each per frame
  torch_v1c (standalones/edward-ii/edit/fx_v1c.py) -- PlateFX('b10', seed=10) exactly as Edward II S10: torch glow pulse,
                                                   static spill x one scalar per group, mist + warm haze, 34 embers
  smoke_v2  (engine-rnd/smoke/smoke_v2.py)      -- SmokeScene(configs/b10_wall_torch.json): wall_torch + wisp from the torch

Composition (inside depth_v1's layer matrix; there is no second camera anywhere):
  torch_v1c -> depth_v1 plate_fx  : its plate-space delta is split across far/near by exclusive coverage and rides each
                                    card's single warp (the glow/spill/mist sit ON the surfaces they light).
  smoke_v2  -> depth_v1 layer_fx['near'] : the plume's own premultiplied (colour*alpha, alpha), composited from
                                    smoke_v2.Emitter.render exactly as SmokeScene.frame does, laid over the NEAR card
                                    (the torch's card) before its warp.  So the whole plume moves with the torch at one depth;
                                    where it rises past the arch silhouette over the sky it is NOT torn in two by parallax.
  face keep-out (this file)       : torch_v1c spill/mist would change the two faces by up to 41/57 levels.  The brief demands
                                    faces at 0 changed px apart from the transform, so the torch delta is zeroed on the face
                                    polys (+6 px for the Lanczos footprint) and faded back in over 18 px.  smoke_v2's own
                                    protect rects already keep smoke off both faces and off the flame.
smoke_v2.push_frame (its StablePush camera) is trapped and counted: must be 0.  fx_v1c's parallax camera is unused
(b10 has no 'parallax' spec: fx.par is None; render(t, u=0)).
"""
import sys, json, math, hashlib, importlib.util, subprocess, argparse, time
from pathlib import Path
import numpy as np, cv2

HERE = Path(__file__).resolve().parent; ROOT = HERE.parent.parent
LOCKED = {  # path -> md5 (import read-only; refuse to run if any changed)
    ROOT / "engine-rnd/depth/depth_v1.py": "dd5cd5011c88b3b56528b96fedae5494",
    ROOT / "standalones/edward-ii/edit/fx_v1c.py": "f31394f82a890b94d7670b009e984ce8",
    ROOT / "engine-rnd/smoke/smoke_v2.py": "80bb28695757f7568b005e8ba8327bde",
    ROOT / "standalones/edward-ii/plates-v3b/b10_corfe_kent_hands_letter_OWNER.png": "386d4c426bfc75da9d72eca768057228",
}
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
for p, h in LOCKED.items(): assert md5(p) == h, f"locked file changed: {p}"
def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
DEPTH = _load("depth_v1", ROOT / "engine-rnd/depth/depth_v1.py")
FXM = _load("fx_v1c", ROOT / "standalones/edward-ii/edit/fx_v1c.py")
SM = _load("smoke_v2", ROOT / "engine-rnd/smoke/smoke_v2.py")
G = DEPTH.G
PLATE = ROOT / "standalones/edward-ii/plates-v3b/b10_corfe_kent_hands_letter_OWNER.png"
DEPTH_CFG = ROOT / "engine-rnd/depth/configs/b10_corfe_letter_drift_v1.json"
SMOKE_CFG = ROOT / "engine-rnd/smoke/configs/b10_wall_torch.json"
FX_SEED = 10            # build_rough_edward_ii_v3b_v1c.py: PlateFX(plate, seed=int(seg id digits)) -> S10 = 10

# ---- camera trap: smoke_v2's own camera must never run
CAM_CALLS = {"smoke_v2.push_frame": 0}
_push = SM.push_frame
def _trapped_push(*a, **k):
    CAM_CALLS["smoke_v2.push_frame"] += 1; return _push(*a, **k)
SM.push_frame = _trapped_push

# ---- face keep-out polys (plate px; skin + beard of each face, drawn from 3x crops of the plate)
FACES = {
    "kent_face": [(305, 600), (330, 585), (380, 590), (400, 610), (405, 660), (398, 700), (370, 725), (330, 722), (300, 690), (292, 640)],
    "gaoler_face": [(778, 560), (810, 540), (850, 548), (868, 580), (870, 640), (860, 690), (830, 716), (800, 712), (775, 680), (768, 630)],
}
FACE_PAD, FACE_FEATHER = 6, 18

def face_masks(H, W):
    m = {k: cv2.fillPoly(np.zeros((H, W), np.uint8), [np.int32(p)], 1).astype(bool) for k, p in FACES.items()}
    allm = np.any(list(m.values()), 0)
    zero = cv2.dilate(allm.astype(np.uint8), DEPTH.disk(FACE_PAD)).astype(bool)
    d = cv2.distanceTransform((~zero).astype(np.uint8), cv2.DIST_L2, 5)
    w = SM.smoothstep(0.0, FACE_FEATHER, d).astype(np.float32); w[zero] = 0.0
    return m, w          # w = weight of the torch delta (0 on faces)

class Stack:
    def __init__(self, seconds=7.0, fps=30, face_keep=True, torch_gain=1.0, smoke_gain=1.0):
        cfg = DEPTH._cfg(DEPTH_CFG); cfg["seconds"] = seconds; self.cfg = cfg
        assert Path(cfg["plate"]).resolve() == PLATE.resolve()
        self.sh = DEPTH.DepthShot(cfg); self.fps = fps; self.n = int(round(seconds * fps))
        self.E = DEPTH.smooth_progress(self.n, fps=fps, **self.sh.cam().get("ease", {}))
        self.P = self.sh.P; self.Pf = self.sh.Pf; self.H, self.W = self.P.shape[:2]
        self.fx = FXM.PlateFX(str(PLATE), seed=FX_SEED); assert self.fx.par is None and self.fx.key == "b10"
        self.scfg = json.load(open(SMOKE_CFG)); self.sm = SM.SmokeScene(SM.load_plate(PLATE), self.scfg)
        assert not self.sm.billows and self.sm.ease_in == 0
        self.near = [c["name"] for c in self.sh.cards].index("near")
        self.faces, self.wface = face_masks(self.H, self.W)
        if not face_keep: self.wface = np.ones_like(self.wface)
        self.tg, self.sg = float(torch_gain), float(smoke_gain)
        self._cache = {}

    # plate space -----------------------------------------------------------------------------------------------
    def torch(self, t, Pf255=None):
        """torch_v1c plate-space RGB [0,1] with the face keep-out applied to its delta."""
        if Pf255 is not None: save = self.fx.Pf; self.fx.Pf = Pf255
        try: f = np.asarray(self.fx.render(t, 0.0), np.float32) / 255.0
        finally:
            if Pf255 is not None: self.fx.Pf = save
        base = self.Pf if Pf255 is None else Pf255 / 255.0
        return base + (f - base) * (self.wface * self.tg)[..., None]

    def smoke(self, t):
        """smoke_v2 premultiplied RGBA [0,1] (plate space): same emitter loop/order as SmokeScene.frame, premultiplied."""
        H, W = self.H, self.W; C = np.zeros((H, W, 3), np.float32); A = np.zeros((H, W, 1), np.float32)
        tt = t + self.sm.preroll
        for e in self.sm.emitters:
            x0, y0, x1, y1 = e.bb; a, col = e.render(tt); a = (a * self.sg)[..., None]
            C[y0:y1, x0:x1] = C[y0:y1, x0:x1] * (1 - a) + (col / 255.0) * a
            A[y0:y1, x0:x1] = A[y0:y1, x0:x1] * (1 - a) + a
        return np.concatenate([C, A], -1)

    def plate_composite(self, t, torch=True, smoke=True):
        """zero-camera plate-space look (for proofs): torch layer then smoke over it."""
        img = self.torch(t) if torch else self.Pf.copy()
        if smoke: ov = self.smoke(t); img = img * (1 - ov[..., 3:]) + ov[..., :3]
        return img

    # screen ----------------------------------------------------------------------------------------------------
    def frame(self, i, size, torch=True, smoke=True, o=None, T=None, S=None, return_layers=False):
        t = i / self.fps; o = self.sh.overscan(size, self.n) if o is None else o
        pfx = None; lfx = None
        if torch:
            T = self.torch(t) if T is None else T; pfx = lambda _t: T
        if smoke:
            S = self.smoke(t) if S is None else S; lfx = {"near": lambda _t: S}
        return self.sh.frame(self.E[i], size, o, fid=i, plate_fx=pfx, layer_fx=lfx, t=t, return_layers=return_layers)

def luma(a): return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
def phone(img, ph=(360, 640)): return (luma(cv2.resize(img, ph, interpolation=cv2.INTER_AREA)) * 255).astype(np.float32)
def writer(path, w, h, fps, crf):
    assert not Path(path).exists(), f"refusing to overwrite {path}"
    return DEPTH.ffmpeg_writer(str(path), w, h, fps, crf)   # ffmpeg -n, rgb24 -> libx264 yuv420p, no audio stream

# ================================================================================================ main pass
BLOCK = 40                      # phone block (px at 360x640) for local luma swing: 9 x 16 blocks
ZONES = {                       # named plate-px windows for local phone stats (x0, y0, x1, y1)
    "torch_flame": (640, 360, 712, 560), "smoke_column": (560, 0, 760, 400), "arch_wall_lit": (712, 200, 941, 480),
    "kent_face": (300, 590, 405, 725), "gaoler_face": (770, 545, 870, 715), "sky_castle": (0, 0, 460, 360),
    "valley_mist": (0, 385, 280, 575), "letter": (560, 900, 660, 1000), "ground": (0, 1450, 941, 1672),
}

def block_series(frames, b=BLOCK):
    F_ = np.stack(frames); n, h, w = F_.shape
    return F_[:, : h // b * b, : w // b * b].reshape(n, h // b, b, w // b, b).mean((2, 4))   # n x 16 x 9

def zone_series(frames, rect, plate_wh=(941, 1672)):
    h, w = frames[0].shape; sx, sy = w / plate_wh[0], h / plate_wh[1]; x0, y0, x1, y1 = rect
    xa, xb, ya, yb = int(x0 * sx), max(int(x0 * sx) + 1, int(x1 * sx)), int(y0 * sy), max(int(y0 * sy) + 1, int(y1 * sy))
    return [float(f[ya:yb, xa:xb].mean()) for f in frames]

def local_stats(frames, fps):
    B = block_series(frames); n, R, C = B.shape; out = []
    for r in range(R):
        for c in range(C): s = DEPTH.series_stats(B[:, r, c], fps); s["rc"] = [r, c]; out.append(s)
    return out

def summarize_local(L, ref=None):
    sw = np.array([s["swing_1s_max_pct"] for s in L]); hz = np.array([s["energy_above_5hz"] for s in L])
    act = sw > 1.0
    r = dict(blocks=len(L), swing_1s_max_pct=dict(max=round(float(sw.max()), 3), p95=round(float(np.percentile(sw, 95)), 3), median=round(float(np.median(sw)), 3)),
             energy_above_5hz_active_blocks=dict(n_active=int(act.sum()), max=round(float(hz[act].max()), 4) if act.any() else 0.0,
                                                 p95=round(float(np.percentile(hz[act], 95)), 4) if act.any() else 0.0))
    if ref is not None:
        d = sw - np.array([s["swing_1s_max_pct"] for s in ref]); k = int(np.argmax(d))
        r["swing_excess_vs_ref_pp"] = dict(max=round(float(d.max()), 3), p95=round(float(np.percentile(d, 95)), 3), median=round(float(np.median(d)), 3),
                                           worst_block_rc=L[k]["rc"], blocks_over_1pp=int((d > 1).sum()), blocks_over_3pp=int((d > 3).sum()))
    return r

def run(args):
    t_start = time.time(); S = Stack(seconds=args.seconds, face_keep=not args.no_face_keep, torch_gain=args.torch_gain, smoke_gain=args.smoke_gain)
    n, fps = S.n, S.fps; tag = args.tag
    big = (1080, 1920); sm_ = (540, 960); oB = S.sh.overscan(big, n); oS = S.sh.overscan(sm_, n)
    outs = {}
    outs["final"] = (HERE / "final" / f"b10_corfe_{tag}.mp4", big, dict(torch=True, smoke=True), args.crf)
    if not args.final_only:
        outs["poc"] = (HERE / "poc" / f"b10_corfe_{tag}_poc540.mp4", sm_, dict(torch=True, smoke=True), 23)
        outs["torch_off"] = (HERE / "ab" / f"b10_corfe_{tag}_ab540_torch_off.mp4", sm_, dict(torch=False, smoke=True), 23)
        outs["smoke_off"] = (HERE / "ab" / f"b10_corfe_{tag}_ab540_smoke_off.mp4", sm_, dict(torch=True, smoke=False), 23)
        outs["both_off"] = (HERE / "ab" / f"b10_corfe_{tag}_ab540_both_off_depth_only.mp4", sm_, dict(torch=False, smoke=False), 23)
    W = {k: writer(p, s[0], s[1], fps, c) for k, (p, s, _, c) in outs.items()}
    ph = {k: [] for k in outs}; plate_ph = {k: [] for k in ("none", "torch", "smoke", "all")}
    dsum = {k: np.zeros((960, 540), np.float64) for k in ("torch", "smoke")}; dmax = {k: np.zeros((960, 540), np.float32) for k in dsum}
    face_plate_max = {k: 0.0 for k in S.faces}; face_screen = []; warp_bad = 0; warps = 0
    # face screen-space reference masks (plate poly -> near matrix), checked on the 1080 final every 15 frames
    for i in range(n):
        t = i / fps; T = S.torch(t); SS = S.smoke(t); fr = {}
        for k, (p, size, fl, _) in outs.items():
            L0 = len(DEPTH.WARP_LOG)
            img = S.frame(i, size, o=oB if size == big else oS, T=T if fl["torch"] else None, S=SS if fl["smoke"] else None, **fl)
            new = DEPTH.WARP_LOG[L0:]; warps += len(new)
            if sorted(new) != sorted([(i, "far"), (i, "near")]): warp_bad += 1
            b8 = DEPTH.to8(img); W[k].stdin.write(b8.tobytes()); fr[k] = img
            ph[k].append(phone(img))
            if k == "final" and i in (0, n // 2, n - 1) or (k == "final" and i == args.grab):
                cv2.imwrite(str(HERE / ("final" if i == args.grab else "scratch") / f"b10_corfe_{tag}_f{i:03d}.png"), cv2.cvtColor(b8, cv2.COLOR_RGB2BGR))
            if k == "final" and i % 15 == 0:
                M = S.sh.layer_affine(S.near, S.E[i], big, oB)
                ref = DEPTH.to8(cv2.warpAffine(S.Pf, M, big, flags=DEPTH.INTERP, borderMode=cv2.BORDER_REPLICATE)).astype(int)
                rec = dict(frame=i)
                for fk, m in S.faces.items():   # face poly ∩ near card's solid interior, eroded 4 px (silhouette AA excluded, as depth_v1.rigidity)
                    me = cv2.erode((m & S.sh.hard[S.near]).astype(np.uint8), DEPTH.disk(4)).astype(np.float32)
                    mm = cv2.warpAffine(me, M, big, flags=cv2.INTER_LINEAR) > 0.999
                    d = np.abs(b8.astype(int) - ref)[mm].max(-1)
                    rec[fk] = dict(px=int(mm.sum()), changed_px=int((d > 0).sum()), max_abs=int(d.max()))
                face_screen.append(rec)
        if "poc" in fr:
            for e, off in (("torch", "torch_off"), ("smoke", "smoke_off")):   # effect contribution = all-on minus all-without-it
                d = np.abs(fr["poc"] - fr[off]).max(-1) * 255; dsum[e] += d; np.maximum(dmax[e], d, out=dmax[e])
        pa = T * (1 - SS[..., 3:]) + SS[..., :3]; ps = S.Pf * (1 - SS[..., 3:]) + SS[..., :3]
        for k, im in (("none", S.Pf), ("torch", T), ("smoke", ps), ("all", pa)): plate_ph[k].append(phone(im))
        for fk, m in S.faces.items(): face_plate_max[fk] = max(face_plate_max[fk], float(np.abs(pa - S.Pf)[m].max() * 255))
        if i % 30 == 0: print(f"frame {i}/{n}  {time.time() - t_start:.0f}s", flush=True)
    for w in W.values(): w.stdin.close(); assert w.wait() == 0
    res = dict(tag=tag, seconds=args.seconds, fps=fps, frames=n, args=vars(args), locked_md5={str(p.relative_to(ROOT)): h for p, h in LOCKED.items()},
               outputs={k: dict(path=str(p.relative_to(ROOT)), size=list(s), md5=md5(p), bytes=p.stat().st_size, **fl) for k, (p, s, fl, _) in outs.items()},
               single_transform=dict(renders=n * len(outs), warps_logged=warps, expected=2 * n * len(outs), renders_not_exactly_one_warp_per_layer=warp_bad,
                                     camera_calls=dict(CAM_CALLS), fx_v1c_par_is_none=S.fx.par is None),
               faces=dict(plate_space_max_abs_delta_levels=face_plate_max, screen_1080_vs_plate_warped_by_near_matrix=face_screen,
                          keepout=dict(pad_px=FACE_PAD, feather_px=FACE_FEATHER, enabled=not args.no_face_keep)))
    # ---- phone stats
    PH = {}
    PH["final_1080_whole_frame"] = DEPTH.series_stats([f.mean() for f in ph["final"]], fps)
    if "poc" in ph:
        var = dict(all="poc", torch_only="smoke_off", smoke_only="torch_off", depth_only="both_off")
        PH["screen_540_whole_frame"] = {k: DEPTH.series_stats([f.mean() for f in ph[v]], fps) for k, v in var.items()}
        loc = {k: local_stats(ph[v], fps) for k, v in var.items()}
        PH["screen_540_local_blocks"] = {k: summarize_local(loc[k], loc["torch_only"] if k == "all" else loc["depth_only"] if k != "depth_only" else None) for k in var}
        PH["screen_540_zones"] = {z: {k: DEPTH.series_stats(_screen_zone(S, ph[v], z, sm_, oS), fps) for k, v in var.items()} for z in ZONES}
    PH["plate_space_whole_frame"] = {k: DEPTH.series_stats([f.mean() for f in v], fps) for k, v in plate_ph.items() if k != "none"}
    locp = {k: local_stats(v, fps) for k, v in plate_ph.items()}
    PH["plate_space_local_blocks"] = {k: summarize_local(locp[k], locp["torch"] if k == "all" else None) for k in ("torch", "smoke", "all")}
    PH["plate_space_zones"] = {z: {k: DEPTH.series_stats(zone_series(plate_ph[k], ZONES[z]), fps) for k in ("torch", "smoke", "all")} for z in ZONES}
    res["phone_360x640"] = PH
    # ---- busy-ness: motion energy share (mean |frame-to-frame luma change| per phone px, in levels)
    if "poc" in ph:
        def me(seq): return float(np.mean([np.abs(seq[i] - seq[i - 1]).mean() for i in range(1, len(seq))]))
        Dt = [a - b for a, b in zip(ph["poc"], ph["torch_off"])]
        Ds = [a - b for a, b in zip(ph["poc"], ph["smoke_off"])]
        e = dict(camera_depth_only=me(ph["both_off"]), torch=me(Dt), smoke=me(Ds)); tot = sum(e.values())
        pe = dict(torch=me([a - b for a, b in zip(plate_ph["torch"], plate_ph["none"])]), smoke=me([a - b for a, b in zip(plate_ph["all"], plate_ph["torch"])]))
        res["busyness_phone"] = dict(note="screen: camera = depth-only frame-diff energy; effect = frame-diff energy of its on/off contribution (all - all_without_it). levels/px/frame",
                                     screen_levels=e, screen_share={k: round(v / tot, 4) for k, v in e.items()}, all_on_total_levels=me(ph["poc"]),
                                     plate_space_no_camera_levels=pe, plate_space_share={k: round(v / sum(pe.values()), 4) for k, v in pe.items()})
        for k in dsum:
            mean = dsum[k] / n
            for nm, a, sc in (("max", dmax[k], 255.0 / max(dmax[k].max(), 1)), ("mean", mean, 255.0 / max(mean.max(), 1e-6))):
                hm = cv2.applyColorMap(np.clip(a * sc, 0, 255).astype(np.uint8), cv2.COLORMAP_INFERNO)
                cv2.imwrite(str(HERE / "proofs" / f"deltamap_{tag}_{k}_{nm}.png"), hm)
            res.setdefault("delta_maps", {})[k] = dict(max_levels=round(float(dmax[k].max()), 2), mean_levels_max=round(float(mean.max()), 3),
                                                       frac_px_ever_changed_ge2=round(float((dmax[k] >= 2).mean()), 4), frac_px_mean_ge2=round(float((mean >= 2).mean()), 4),
                                                       pngs=[f"proofs/deltamap_{tag}_{k}_max.png", f"proofs/deltamap_{tag}_{k}_mean.png"])
    res["elapsed_s"] = round(time.time() - t_start, 1)
    pj = HERE / "proofs" / f"run_{tag}.json"; json.dump(res, open(pj, "x"), indent=1, default=float); print(json.dumps(res, default=float)[:4000])

def _screen_zone(S, frames, z, size, o):
    """zone tracked through the camera: plate rect corners -> near-card matrix at each frame -> phone px."""
    x0, y0, x1, y1 = ZONES[z]; out = []
    for i, f in enumerate(frames):
        M = S.sh.layer_affine(S.near if z not in ("sky_castle", "valley_mist") else 0, S.E[i], size, o); s = f.shape[1] / size[0]
        xa, ya = (M @ [x0, y0, 1]) * s; xb, yb = (M @ [x1, y1, 1]) * s
        xa, ya = max(0, int(xa)), max(0, int(ya)); xb, yb = min(f.shape[1], max(xa + 1, int(xb))), min(f.shape[0], max(ya + 1, int(yb)))
        out.append(float(f[ya:yb, xa:xb].mean()))
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run"]); ap.add_argument("--tag", default="fullstack_v1"); ap.add_argument("--seconds", type=float, default=7.0)
    ap.add_argument("--crf", type=int, default=20); ap.add_argument("--grab", type=int, default=105)
    ap.add_argument("--torch-gain", type=float, default=1.0); ap.add_argument("--smoke-gain", type=float, default=1.0)
    ap.add_argument("--no-face-keep", action="store_true"); ap.add_argument("--final-only", action="store_true")
    a = ap.parse_args(); run(a)
