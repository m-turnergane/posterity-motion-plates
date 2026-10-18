"""Georeferencing for painted maps: explicit projection + fitted warp from control points (no hand-placed city pixels).

pixel = warp( project(lon, lat) )
  project: 'equirect' (x=lon*cos(lat0), y=lat), 'mercator', or 'lcc' (Lambert conformal conic, 2 standard parallels) - plain numpy, no pyproj needed.
  warp:    'affine' (6 params), 'poly2' (12 params), 'tps' (thin-plate spline through the control points, smoothing optional; scipy RBFInterpolator).
Everything is deterministic. `fit()` returns a Georef with residuals; `loo()` gives leave-one-out errors (honest accuracy for NEW points);
`deviation_report()` summarises how far the painted map is from real geography. The painted AI concept map is NOT an atlas: report, never hide, the deviation."""
import json, math
import numpy as np

R_EARTH_KM = 6371.0088

def project(lon, lat, kind="equirect", lat0=40.0, lon0=60.0, p1=30.0, p2=55.0):
    lon = np.asarray(lon, np.float64); lat = np.asarray(lat, np.float64)
    if kind == "equirect": return np.stack([np.radians(lon - lon0) * math.cos(math.radians(lat0)), np.radians(lat)], -1)
    if kind == "mercator": return np.stack([np.radians(lon - lon0), np.log(np.tan(np.pi / 4 + np.radians(np.clip(lat, -85, 85)) / 2))], -1)
    if kind == "lcc":
        a1, a2, f0, l0 = map(math.radians, (p1, p2, lat0, lon0))
        n = math.log(math.cos(a1) / math.cos(a2)) / math.log(math.tan(math.pi / 4 + a2 / 2) / math.tan(math.pi / 4 + a1 / 2))
        F = math.cos(a1) * math.tan(math.pi / 4 + a1 / 2) ** n / n; rho0 = F / math.tan(math.pi / 4 + f0 / 2) ** n
        rho = F / np.tan(np.pi / 4 + np.radians(lat) / 2) ** n; th = n * (np.radians(lon) - l0)
        return np.stack([rho * np.sin(th), rho0 - rho * np.cos(th)], -1)
    raise ValueError(f"unknown projection {kind!r}")

def _poly_terms(P, deg):
    x, y = P[:, 0], P[:, 1]
    cols = [np.ones_like(x), x, y]
    if deg >= 2: cols += [x * x, x * y, y * y]
    if deg >= 3: cols += [x ** 3, x * x * y, x * y * y, y ** 3]
    return np.stack(cols, 1)

class Georef:
    def __init__(self, proj, warp, params, size):
        self.proj, self.warp, self.params, self.size = proj, warp, params, tuple(size); self._fit = None; self.cp = None
    def _P(self, lonlat):
        ll = np.atleast_2d(np.asarray(lonlat, np.float64)); P = project(ll[:, 0], ll[:, 1], **self.proj)
        return P
    def to_px(self, lonlat):
        P = self._P(lonlat); sh = np.atleast_2d(np.asarray(lonlat)).shape
        if self.warp == "tps": out = self._fit(P)
        else: out = _poly_terms(P, self.params["degree"]) @ self._coef
        return out[0] if np.asarray(lonlat).ndim == 1 else out
    def to_lonlat(self, px, iters=40):
        """inverse by Gauss-Newton on the forward map (smooth, near-affine => converges fast)."""
        px = np.atleast_2d(np.asarray(px, np.float64)); out = []
        for p in px:
            ll = np.array([60.0, 40.0])
            for _ in range(iters):
                f = self.to_px(ll); e = f - p
                if np.abs(e).max() < 1e-4: break
                J = np.zeros((2, 2))
                for k in range(2):
                    d = np.zeros(2); d[k] = 1e-4; J[:, k] = (self.to_px(ll + d) - f) / 1e-4
                ll = ll - np.linalg.solve(J, e)
            out.append(ll)
        return np.array(out)
    def to_dict(self): return dict(proj=self.proj, warp=self.warp, params=self.params, size=list(self.size), control_points=self.cp)

def fit(control_points, size, proj=None, warp="affine", smooth=0.0):
    """control_points: [{id, lon, lat, px:[x,y], weight?}] -> Georef. Needs >=3 (affine), >=6 (poly2), >=4 (tps)."""
    proj = dict(proj or {"kind": "equirect"}); cp = control_points
    ll = np.array([[c["lon"], c["lat"]] for c in cp], float); px = np.array([c["px"] for c in cp], float)
    P = project(ll[:, 0], ll[:, 1], **proj)
    g = Georef(proj, warp, {}, size); g.cp = cp
    if warp in ("affine", "poly2", "poly3"):
        deg = {"affine": 1, "poly2": 2, "poly3": 3}[warp]; A = _poly_terms(P, deg)
        if len(cp) < A.shape[1]: raise ValueError(f"{warp} needs >= {A.shape[1]} control points (got {len(cp)})")
        w = np.array([c.get("weight", 1.0) for c in cp])[:, None] ** 0.5
        g._coef, *_ = np.linalg.lstsq(A * w, px * w, rcond=None); g.params = {"degree": deg}
    elif warp == "tps":
        from scipy.interpolate import RBFInterpolator
        if len(cp) < 4: raise ValueError("tps needs >= 4 control points")
        g._fit = RBFInterpolator(P, px, kernel="thin_plate_spline", smoothing=smooth, degree=1); g.params = {"smoothing": smooth}
    else: raise ValueError(f"unknown warp {warp!r}")
    return g

def residuals(g, control_points=None):
    cp = control_points or g.cp; ll = np.array([[c["lon"], c["lat"]] for c in cp]); px = np.array([c["px"] for c in cp], float)
    return np.linalg.norm(g.to_px(ll) - px, axis=1)

def loo(control_points, size, proj, warp, smooth=0.0):
    """leave-one-out error in px for each control point (accuracy for points NOT used in the fit)."""
    errs = []
    for i in range(len(control_points)):
        rest = [c for j, c in enumerate(control_points) if j != i]
        try: g = fit(rest, size, proj, warp, smooth)
        except ValueError: errs.append(float("nan")); continue
        c = control_points[i]; errs.append(float(np.linalg.norm(g.to_px([c["lon"], c["lat"]]) - np.array(c["px"], float))))
    return errs

def px_per_km(g, lonlat):
    """local scale: pixels per km east and north at a point."""
    lon, lat = lonlat; dk = 100.0; dlat = dk / 111.195; dlon = dk / (111.195 * math.cos(math.radians(lat)))
    p0 = g.to_px([lon, lat]); pe = g.to_px([lon + dlon, lat]); pn = g.to_px([lon, lat + dlat])
    return float(np.linalg.norm(pe - p0) / dk), float(np.linalg.norm(pn - p0) / dk)

def haversine_km(a, b):
    p1, p2 = math.radians(a[1]), math.radians(b[1]); dl = math.radians(b[0] - a[0]); dp = p2 - p1
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_EARTH_KM * math.asin(math.sqrt(h))

def geodesic(a, b, n=64):
    """great-circle points (lon, lat) from a to b, slerp on the unit sphere."""
    def v(p): lo, la = math.radians(p[0]), math.radians(p[1]); return np.array([math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la)])
    va, vb = v(a), v(b); om = math.acos(np.clip(va @ vb, -1, 1)); out = []
    for t in np.linspace(0, 1, n):
        x = (math.sin((1 - t) * om) * va + math.sin(t * om) * vb) / math.sin(om); out.append([math.degrees(math.atan2(x[1], x[0])), math.degrees(math.asin(np.clip(x[2], -1, 1)))])
    return np.array(out)

def clip_polyline_to_rect(pts, W, H, margin=0.0):
    """keep the leading part of a polyline (in px) up to where it leaves [margin, W-margin] x [margin, H-margin]; the exit point is interpolated onto the edge."""
    out = [pts[0]]
    inside = lambda p: margin <= p[0] <= W - margin and margin <= p[1] <= H - margin
    for p0, p1 in zip(pts[:-1], pts[1:]):
        if inside(p1): out.append(p1); continue
        lo, hi = 0.0, 1.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if inside(p0 + (p1 - p0) * mid): lo = mid
            else: hi = mid
        out.append(p0 + (p1 - p0) * lo); break
    return np.array(out)

def load(path_or_dict, size=None):
    d = json.load(open(path_or_dict)) if isinstance(path_or_dict, str) else path_or_dict
    return fit(d["control_points"], size or d["size"], d.get("proj"), d.get("warp", "affine"), d.get("smooth", 0.0))
