"""Spherical Lambert Conformal Conic (2SP), numpy. Matches proj4 '+proj=lcc +lat_1 +lat_2 +lat_0 +lon_0 +R=6371000'."""
import numpy as np, math
R = 6371000.0
class LCC:
    def __init__(s, lat1, lat2, lat0, lon0):
        s.lat1, s.lat2, s.lat0, s.lon0 = lat1, lat2, lat0, lon0
        p1, p2, p0 = map(math.radians, (lat1, lat2, lat0))
        s.n = math.log(math.cos(p1) / math.cos(p2)) / math.log(math.tan(math.pi/4 + p2/2) / math.tan(math.pi/4 + p1/2))
        s.F = math.cos(p1) * math.tan(math.pi/4 + p1/2) ** s.n / s.n
        s.rho0 = R * s.F / math.tan(math.pi/4 + p0/2) ** s.n
    def fwd(s, lon, lat):
        lon = np.asarray(lon, float); lat = np.asarray(lat, float)
        rho = R * s.F / np.tan(np.pi/4 + np.radians(lat)/2) ** s.n
        th = s.n * np.radians(lon - s.lon0)
        return rho * np.sin(th), s.rho0 - rho * np.cos(th)
    def inv(s, x, y):
        x = np.asarray(x, float); y = np.asarray(y, float)
        dy = s.rho0 - y; rho = np.sign(s.n) * np.hypot(x, dy); th = np.arctan2(x, dy)
        lat = np.degrees(2 * np.arctan((R * s.F / rho) ** (1 / s.n)) - np.pi/2)
        return s.lon0 + np.degrees(th / s.n), lat
    def proj4(s):
        return f"+proj=lcc +lat_1={s.lat1} +lat_2={s.lat2} +lat_0={s.lat0} +lon_0={s.lon0} +x_0=0 +y_0=0 +R=6371000 +units=m +no_defs"
