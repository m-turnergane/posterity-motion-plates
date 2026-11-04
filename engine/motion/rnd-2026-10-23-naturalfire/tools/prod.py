"""Read-only re-use of the v2c P05 production path (helpers copied verbatim from
day21/atahualpa/edit/build_rough_atahualpa_v2c_p05static.py; engine = locked animate_b3_cb9e2b88.py; config = configs_v2c p05static)."""
import importlib.util, json, math, hashlib
from pathlib import Path
import numpy as np, cv2
from PIL import Image
FPS, W, H, UP = 30, 1080, 1920, 2
ROOT = Path("/workspace/posterity/day21/atahualpa")
ENG_PATH = Path("/workspace/posterity/motion/presets/locked/engine/animate_b3_cb9e2b88.py")
CFG_PATH = ROOT / "motion" / "configs_v2c" / "atahualpa_P05_candle_v2c_p05static.json"
PLATE = ROOT / "plates" / "atahualpa_p05_gold_melted_OWNER.png"
MASKS = ROOT / "masks_v2b2"
ENC_INTER = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "0", "-preset", "ultrafast", "-g", "1", "-keyint_min", "1", "-x264-params", "keyint=1:min-keyint=1:scenecut=0"]
ENC_FINAL = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "medium", "-profile:v", "high"]
def md5f(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def detect_bars(arr, maxscan=40, margin=4):   # verbatim
    lum = arr.astype(np.float32).mean(2); res, info = {}, {}
    for side in "LRTB":
        L = {"L": lum.T, "R": lum.T[::-1], "T": lum, "B": lum[::-1]}[side]
        nn = min(200, len(L)); m = L[:nn].mean(1); s = L[:nn].std(1); br = (L[:nn] > 225).mean(1)
        d = np.abs(np.diff(L[:nn], axis=0)).mean(1); ref_m = float(np.median(m[60:120])); ref_d = float(np.median(d[20:150]))
        k = 0
        while k < maxscan and (br[k] > 0.35 or (s[k] < 5 and abs(m[k] - ref_m) > 20)): k += 1
        ext = k; c = int(np.argmax(d[:30]))
        if d[c] > 4 * ref_d and (m[:c + 1] > ref_m + 25).all(): ext = max(ext, c + 1)
        res[side] = ext + margin if ext else 0
        info[side] = {"bar_px": ext, "crop_px": res[side]}
    return res, info
def prepare_cover(im, up=UP):   # verbatim
    im = im.convert("RGB"); tw, th = W * up, H * up; sw, sh = im.size
    sc = max(tw / sw, th / sh); nw, nh = int(math.ceil(sw * sc)), int(math.ceil(sh * sc))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS); l, t = (nw - tw) // 2, (nh - th) // 2
    return im.crop((l, t, l + tw, t + th))
def cam(seg, u, t):   # verbatim
    z0, z = seg["z_start"], seg["z_end"]; s = z0 * (z / z0) ** u; ax, ay = seg["anchor"]
    cx = ax * W * (1 - 1 / s) + W / (2 * s); cy = ay * H * (1 - 1 / s) + H / (2 * s); hw, hh = W / (2 * s), H / (2 * s)
    return s, min(max(cx, hw), W - hw), min(max(cy, hh), H - hh)
def cam_frame(base, seg, u, t):   # verbatim
    bw, bh = base.size; s, cx, cy = cam(seg, u, t); k = bw / W; ww, wh = bw / s, bh / s; l, tp = cx * k - ww / 2, cy * k - wh / 2
    big = base.transform((W * 2, H * 2), Image.Transform.AFFINE, (ww / (2 * W), 0, l, 0, wh / (2 * H), tp), resample=Image.Resampling.BICUBIC)
    return Image.fromarray(cv2.resize(np.asarray(big), (W, H), interpolation=cv2.INTER_AREA))
def to_out(seg, x, y, u, t):
    s, cx, cy = cam(seg, u, t); return (x - (cx - W / (2 * s))) * s, (y - (cy - H / (2 * s))) * s
def plate_box():
    im = Image.open(PLATE).convert("RGB"); arr = np.asarray(im); crop, _ = detect_bars(arr); w, h = im.size
    return (crop["L"], crop["T"], w - crop["R"], h - crop["B"])
def plate_to_cover(box, x, y):
    l, t = box[0], box[1]; cw, ch = box[2] - box[0], box[3] - box[1]; sc = max(W / cw, H / ch)
    return (x - l) * sc - (cw * sc - W) / 2, (y - t) * sc - (ch * sc - H) / 2
def load_engine():
    assert md5f(ENG_PATH).startswith("cb9e2b88")
    spec = importlib.util.spec_from_file_location("animate_b3_locked", str(ENG_PATH)); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def load_cfg(): return json.load(open(CFG_PATH))
SEG_P05 = dict(id="P05", z_start=1.0, z_end=1.04, anchor=[0.5, 0.5], frames=153)
SEG_POC = dict(id="P05poc", z_start=1.0, z_end=1.04, anchor=[0.5, 0.5], frames=180)
def frame_out(img, box, seg, fi):
    nfr = seg["frames"]; u = fi / max(nfr - 1, 1); t = fi / FPS
    lit = Image.fromarray(np.clip(np.rint(img), 0, 255).astype(np.uint8)).crop(box)
    return cam_frame(prepare_cover(lit), seg, u, t)
