"""Vectorised improved-Perlin gradient noise (3D) + fBm.  Non-periodic over the ranges used here (lattice period 256)."""
import numpy as np
class Perlin3:
    def __init__(self, seed):
        r = np.random.default_rng(seed); p = r.permutation(256); self.p = np.concatenate([p, p]).astype(np.int32)
        # random offsets so different seeds sample unrelated regions
        self.off = r.uniform(0, 200, 3)
    @staticmethod
    def _fade(t): return t * t * t * (t * (t * 6 - 15) + 10)
    @staticmethod
    def _grad(h, x, y, z):
        h = h & 15; u = np.where(h < 8, x, y); v = np.where(h < 4, y, np.where((h == 12) | (h == 14), x, z))
        return np.where(h & 1, -u, u) + np.where(h & 2, -v, v)
    def __call__(self, x, y, z):
        x = x + self.off[0]; y = y + self.off[1]; z = np.broadcast_to(np.asarray(z, np.float64) + self.off[2], np.shape(x))
        xi = np.floor(x).astype(np.int64); yi = np.floor(y).astype(np.int64); zi = np.floor(z).astype(np.int64)
        xf, yf, zf = x - xi, y - yi, z - zi; xi &= 255; yi &= 255; zi &= 255
        u, v, w = self._fade(xf), self._fade(yf), self._fade(zf); p = self.p
        A = p[xi] + yi; AA = p[A] + zi; AB = p[A + 1] + zi; B = p[xi + 1] + yi; BA = p[B] + zi; BB = p[B + 1] + zi
        g = self._grad; L = lambda a, b, t: a + t * (b - a)
        x1 = L(g(p[AA], xf, yf, zf), g(p[BA], xf - 1, yf, zf), u); x2 = L(g(p[AB], xf, yf - 1, zf), g(p[BB], xf - 1, yf - 1, zf), u)
        y1 = L(x1, x2, v)
        x1 = L(g(p[AA + 1], xf, yf, zf - 1), g(p[BA + 1], xf - 1, yf, zf - 1), u); x2 = L(g(p[AB + 1], xf, yf - 1, zf - 1), g(p[BB + 1], xf - 1, yf - 1, zf - 1), u)
        y2 = L(x1, x2, v)
        return L(y1, y2, w)          # ~[-1, 1], std ~0.25-0.3
def fbm(P, x, y, z, octaves=3, lac=2.03, gain=0.5, zlac=1.7):
    a, s, tot, norm = 1.0, 1.0, 0.0, 0.0
    for o in range(octaves):
        tot = tot + a * P(x * s, y * s, z * (zlac ** o)); norm += a; a *= gain; s *= lac
    return tot / norm
class Noise1D:
    """Smooth non-periodic 1D noise: sum of octaves of cubic-interpolated random values (no sines)."""
    def __init__(self, seed, n=4096):
        r = np.random.default_rng(seed); self.v = [r.standard_normal(n) for _ in range(4)]
    def __call__(self, t, hz, octaves=1):
        out, a, norm = 0.0, 1.0, 0.0
        for o in range(octaves):
            i = t * hz * (2.1 ** o) + 37 * o; j = int(np.floor(i)); f = i - j; v = self.v[o]
            p0, p1, p2, p3 = v[(j - 1) % len(v)], v[j % len(v)], v[(j + 1) % len(v)], v[(j + 2) % len(v)]
            # Catmull-Rom
            c = 0.5 * (2 * p1 + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f + (-p0 + 3 * p1 - 3 * p2 + p3) * f ** 3)
            out += a * c; norm += a; a *= 0.5
        return out / norm


class BandNoise:
    """Band-limited, non-periodic (over the 6 s shot) 1D noise: white noise FFT-bandpassed to [lo, hi] Hz (soft edges), unit std.
    Unlike Noise1D(hz) (value noise whose energy sits well BELOW hz), the energy really lands in [lo, hi]."""
    def __init__(self, seed, lo, hi, fps=30.0, n=8192):
        r = np.random.default_rng(seed); w = np.fft.rfft(r.standard_normal(n)); f = np.fft.rfftfreq(n, 1 / fps)
        g = 1 / (1 + np.exp(-(f - lo) / (0.08 * lo + 1e-3))) * (1 / (1 + np.exp((f - hi) / (0.08 * hi + 1e-3))))
        x = np.fft.irfft(w * g, n); self.x = x / x.std(); self.fps = fps; self.off = int(r.integers(0, n // 2))
    def __call__(self, t):
        i = t * self.fps + self.off; j = int(np.floor(i)); f = i - j
        return float(self.x[j % len(self.x)] * (1 - f) + self.x[(j + 1) % len(self.x)] * f)
