import hashlib, math
import numpy as np

def md5_file(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()

def md5_bytes(b):
    return hashlib.md5(b).hexdigest()

def smoothstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)

def smootherstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * x * (x * (x * 6 - 15) + 10)

def ease_in_out(x):
    return smootherstep(x)

class Noise1D:
    """Seeded smooth 1-D value noise (cubic interpolated), zero-mean-ish in [-1,1]. Irregular, band-limited."""
    def __init__(self, rng, freq=3.0, n=256):
        self.v = rng.uniform(-1, 1, n); self.f = freq; self.n = n
    def __call__(self, t):
        t = np.asarray(t, dtype=np.float64); u = t * self.f; i = np.floor(u).astype(np.int64); fr = u - i
        a, b, c, d = (self.v[(i + k) % self.n] for k in (-1, 0, 1, 2))
        r = 0.5 * ((2 * b) + (-a + c) * fr + (2 * a - 5 * b + 4 * c - d) * fr ** 2 + (-a + 3 * b - 3 * c + d) * fr ** 3)
        return float(r) if r.ndim == 0 else r.astype(np.float32)

def multi_flicker(rng, bands=((1.7, 0.30), (3.9, 0.30), (7.3, 0.25), (13.1, 0.15))):
    """Irregular multi-frequency flicker: sum of seeded smooth-noise bands, normalised to roughly [-1,1]."""
    ns = [(Noise1D(rng, f), a) for f, a in bands]
    tot = sum(a for _, a in ns)
    return lambda t: sum(n(t) * a for n, a in ns) / tot * 1.6

def polygon_mask(shape, pts, feather=0.0):
    import cv2
    m = np.zeros(shape[:2], np.uint8)
    cv2.fillPoly(m, [np.round(np.array(pts, np.float64)).astype(np.int32)], 255)
    m = m.astype(np.float32) / 255.0
    if feather > 0:
        m = cv2.GaussianBlur(m, (0, 0), feather)
    return m

def remap(img, mx, my, interp, **kw):
    import cv2
    return cv2.remap(img, np.ascontiguousarray(mx, np.float32), np.ascontiguousarray(my, np.float32), interp, **kw)
