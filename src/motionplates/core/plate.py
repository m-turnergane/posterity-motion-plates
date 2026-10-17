"""Plate loading: identical bar detection + cover-fit to the production build scripts (read-only use)."""
import math, os
import numpy as np
from PIL import Image
from .util import md5_file

def plates_root():
    return os.environ.get("MOTIONPLATES_PLATES", "/workspace/posterity/day20/alexander-corpse/plates")

def detect_bars(arr, maxscan=40, margin=4):
    lum = arr.astype(np.float32).mean(2); res = {}
    for side in "LRTB":
        L = {"L": lum.T, "R": lum.T[::-1], "T": lum, "B": lum[::-1]}[side]
        nn = min(200, len(L)); m = L[:nn].mean(1); s = L[:nn].std(1); br = (L[:nn] > 225).mean(1)
        d = np.abs(np.diff(L[:nn], axis=0)).mean(1); ref_m = float(np.median(m[60:120])); ref_d = float(np.median(d[20:150]))
        k = 0
        while k < maxscan and (br[k] > 0.35 or (s[k] < 5 and abs(m[k] - ref_m) > 20)):
            k += 1
        ext = k; c = int(np.argmax(d[:30]))
        if d[c] > 4 * ref_d and (m[:c + 1] > ref_m + 25).all():
            ext = max(ext, c + 1)
        res[side] = ext + margin if ext else 0
    return res

def load_cover(path, W=1080, H=1920):
    """Returns (uint8 RGB HxWx3, info). Crops detected bars, cover-fits with LANCZOS, centre-crops."""
    im = Image.open(path).convert("RGB"); arr = np.asarray(im)
    crop = detect_bars(arr); w, h = im.size
    if any(crop.values()):
        im = im.crop((crop["L"], crop["T"], w - crop["R"], h - crop["B"]))
    sw, sh = im.size; sc = max(W / sw, H / sh)
    nw, nh = int(math.ceil(sw * sc)), int(math.ceil(sh * sc))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    l, t = (nw - W) // 2, (nh - H) // 2
    out = np.asarray(im.crop((l, t, l + W, t + H))).copy()
    return out, {"src_size": [w, h], "bar_crop": crop, "scale": sc, "md5": md5_file(path)}
