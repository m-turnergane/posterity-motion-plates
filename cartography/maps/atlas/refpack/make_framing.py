"""Frame solver + framing JSON (deliverable 1).  python make_framing.py  -> framing_refpack_v1.json (refuses to overwrite)."""
import sys; sys.dont_write_bytecode = True
import os, json, math, datetime, numpy as np
from refpack_lib import *

OUT = os.path.join(HERE, "framing_refpack_v1.json")
# --- requirement sets: (lon, lat, why, inset_x, inset_y) insets are fractions of the frame W/H
IRELAND_FULL = [(-10.47, 51.70, "Ireland W coast (Dingle/Kerry)"), (-10.1, 54.25, "Ireland NW (Mayo)"), (-7.33, 55.38, "Ireland N (Malin Head)"),
                (-5.45, 54.45, "Ireland NE (Ards)"), (-9.8, 51.45, "Ireland SW (Mizen Head)")]
PYRENEES = [(-1.6, 42.9, "Pyrenees W"), (0.6, 42.55, "Pyrenees central ridge (Aneto 42.63N)"), (2.6, 42.45, "Pyrenees E (Canigou)")]
ALPS = [(7.0, 45.9, "Alps W (Mont Blanc)"), (10.4, 46.5, "Alps central (Bernina)"), (6.8, 44.3, "Alps SW (Maritime Alps)")]
MEDCOAST = [(4.85, 43.35, "Rhone mouth / Gulf of Lion"), (3.0, 42.5, "Roussillon coast")]
IRISH_EAST = [(-6.12, 52.45, "map 2a Ireland touch anchor off Wexford"), (-6.2, 53.35, "Dublin coast")]

SPECS = {
 "euro_16x9": dict(kind="euro", WH=(1920, 1080), pin_inset=(0.08, 0.10),
    geo=[(p, 0.025, 0.03) for p in IRELAND_FULL] + [(p, 0.02, 0.10) for p in PYRENEES] + [(p, 0.03, 0.03) for p in ALPS + MEDCOAST],
    why="Whole Fieschi route on one plate: Ireland complete, Britain, Sluis, Paris, Cologne, Milan, Avignon with the Gulf of Lion and "
        "the whole Pyrenees chain below it; frame height is set by Malin Head (55.4N) to the Pyrenees (42.4N) plus margins, the 16:9 width "
        "then gives open Atlantic to the west (medallion/label calm zone) and the Alps-Po basin to the east."),
 "britain_16x9": dict(kind="britain", WH=(1920, 1080), pin_inset=(0.08, 0.12),
    geo=[(p, 0.04, 0.05) for p in IRISH_EAST],
    why="Map 1 / Map 2a stations (Severn cluster: Chepstow, Berkeley, Gloucester, Bristol within 45 km; Westminster-Tyburn 2.9 km) need ~3.5x "
        "the euro scale; frame spans Irish east coast (Ireland touch) to Kent/Sandwich and Lincoln to Corfe with the Channel below."),
 "euro_9x16": dict(kind="euro", WH=(1080, 1920), pin_inset=(0.10, 0.08),
    geo=[(p, 0.02, 0.03) for p in IRISH_EAST] + [(p, 0.03, 0.03) for p in PYRENEES + MEDCOAST] + [(p, 0.03, 0.03) for p in ALPS[:2]],
    why="Native portrait: width is set by the Irish east coast (route's Ireland touch) to Milan with label room; Ireland is partial (east half) "
        "by design. The extra height is used north (Scotland, North Sea) and south (Gulf of Lion, Pyrenees, Corsica) so the route sits in the "
        "middle band and the medallion has calm sea above and below."),
 "britain_9x16": dict(kind="britain", WH=(1080, 1920), pin_inset=(0.10, 0.10),
    geo=[(p, 0.0, 0.05) for p in IRISH_EAST[:1]],
    why="Native portrait of England and Wales: width is set by Glamorgan/Chepstow to Sandwich with label room; the Irish coast at the left edge "
        "carries the Ireland touch; the height shows the Channel and Normandy coast below and northern England/Irish Sea above."),
}

def need_width(center, pts, WH):
    """Minimum width_km so every (lon,lat,inset_x,inset_y) sits inside its inset box, for a frame centred at `center`."""
    pr = V1.LAEA(*center); asp = WH[0] / WH[1]; w = 0.0
    for lo, la, ix, iy in pts:
        x, y = pr(np.float64(lo), np.float64(la))
        w = max(w, 2 * abs(float(x)) / (1 - 2 * ix), 2 * abs(float(y)) * asp / (1 - 2 * iy))
    return w

def solve(spec):
    pins, regions, _ = stops_for(spec["kind"])
    pts = [(p["lon"], p["lat"], *spec["pin_inset"]) for p in pins] + [(r["lon"], r["lat"], *spec["pin_inset"]) for r in regions
           if not (r["row"] == "2-06" and spec["kind"] == "britain")]
    if spec["kind"] == "britain":   # Ireland label point inside the visible Irish coast strip, not deep inland
        pts += [(-6.55, 52.75, 0.02, spec["pin_inset"][1])]
    pts += [(g[0], g[1], ix, iy) for g, ix, iy in spec["geo"]]
    best = None; lo_c, la_c, step = 0.0, 50.5, 1.0
    for _ in range(4):                                     # coarse-to-fine grid on the frame centre
        for lo in np.arange(lo_c - 6 * step, lo_c + 6 * step + 1e-9, step):
            for la in np.arange(la_c - 5 * step, la_c + 5 * step + 1e-9, step):
                c = (round(float(lo), 3), round(float(la), 3)); w = need_width(c, pts, spec["WH"])
                if best is None or w < best[0]: best = (w, c)
        lo_c, la_c = best[1]; step /= 4
    # centre the content: the width is often set by one axis only, which leaves the other axis free; put the free slack
    # evenly on both sides (iterate because the projection is centred on the frame centre)
    c = best[1]
    for _ in range(6):
        pr = V1.LAEA(*c); xy = np.float64([pr(np.float64(p[0]), np.float64(p[1])) for p in pts])
        mx, my = (xy.min(0) + xy.max(0)) / 2
        c = tuple(float(v) for v in MM.inverse_laea(pr, np.float64(mx), np.float64(my)))
    c = (round(c[0], 2), round(c[1], 2))
    # then re-balance along the axis that sets the size (insets differ top/bottom, so the content centre is not optimal)
    cands = [(need_width((c[0], round(c[1] + d, 2)), pts, spec["WH"]), (c[0], round(c[1] + d, 2))) for d in np.arange(-1.5, 1.51, 0.02)]
    cands += [(need_width((round(c[0] + d, 2), c[1]), pts, spec["WH"]), (round(c[0] + d, 2), c[1])) for d in np.arange(-1.5, 1.51, 0.02)]
    w, c = min(cands)
    return (w, c), pts

if __name__ == "__main__":
    for k, sp in SPECS.items():
        (w, c), pts = solve(sp); print(k, c, round(w, 1))
