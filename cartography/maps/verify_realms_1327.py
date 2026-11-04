"""Verifier for the REALMS-1327-v1 must-nots.
Geometry checks run on sources/realms/realms_1327_v1.geojson.
Raster checks (`check_raster`) run on the rendered per-family fill weights of a still
(called from map_route_v2 when rendering; results land in the proofs JSON).
CLI: python verify_realms_1327.py  -> prints JSON, exit 1 on any failure.
"""
import json, os, sys
from shapely.geometry import shape, Point

HERE = os.path.dirname(os.path.abspath(__file__))
GJ = os.path.join(HERE, "sources/realms/realms_1327_v1.geojson")
FRANCE_FAMS = {"france", "france_fam"}

# (name, lon, lat, rule, arg)  rule: in_ids / not_fams / no_fill / fam
POINTS = [
    ("Avignon", 4.80833, 43.94861, "not_fams", FRANCE_FAMS | {"papal"}),
    ("Avignon", 4.80833, 43.94861, "fam", "empire"),
    ("Berwick", -2.0035, 55.7708, "in_ids", {"scotland"}),
    ("Grenoble (Dauphine)", 5.7245, 45.1885, "not_fams", FRANCE_FAMS),
    ("Grenoble (Dauphine)", 5.7245, 45.1885, "fam", "empire"),
    ("Besancon (County of Burgundy)", 6.0241, 47.2378, "not_fams", FRANCE_FAMS),
    ("Besancon (County of Burgundy)", 6.0241, 47.2378, "fam", "empire"),
    ("Dole (County of Burgundy)", 5.4897, 47.0925, "not_fams", FRANCE_FAMS),
    ("Chambery (Savoy)", 5.9178, 45.5646, "fam", "empire"),
    ("Aix (Provence)", 5.4474, 43.5297, "fam", "empire"),
    ("Dijon (Duchy, not merged)", 5.0415, 47.3220, "in_ids", {"burgundy_duchy"}),
    ("Lyon", 4.8357, 45.7640, "fam", "france"),
    ("Paris", 2.35222, 48.85667, "fam", "france"),
    ("Montpellier", 3.8767, 43.6108, "not_fams", FRANCE_FAMS),
    ("Bordeaux", -0.5792, 44.8378, "in_ids", {"gascony"}),
    ("Bayonne", -1.4748, 43.4929, "in_ids", {"gascony"}),
    ("Agen (Agenais)", 0.6176, 44.2033, "not_fams", {"england", "england_light"}),
    ("Saintes (Saintonge)", -0.6328, 45.7464, "not_fams", {"england", "england_light"}),
    ("Dublin", -6.2603, 53.3498, "in_ids", {"ireland_eng"}),
    ("Galway", -9.0568, 53.2707, "no_fill", None),
    ("Donegal", -8.1100, 54.6538, "no_fill", None),
    ("Cardiff", -3.1791, 51.4816, "in_ids", {"england"}),
    ("Caernarfon", -4.2706, 53.1393, "in_ids", {"england"}),
    ("Carlisle", -2.9416, 54.8925, "in_ids", {"england"}),
    ("Sluis", 3.3883, 51.3089, "in_ids", {"flanders"}),
    ("Bruges", 3.2247, 51.2093, "in_ids", {"flanders"}),
    ("Brussels (Brabant)", 4.3517, 50.8503, "fam", "empire"),
    ("Cologne", 6.95778, 50.94222, "fam", "empire"),
    ("Milan (no polygon)", 9.19, 45.46694, "no_fill", None),
    ("Pamplona", -1.6440, 42.8125, "in_ids", {"navarre"}),
    ("Granada", -3.5986, 37.1773, "no_fill", None),
    ("Bologna (Papal States neutral)", 11.3426, 44.4949, "no_fill", None),
]


def load(path=GJ):
    fc = json.load(open(path))
    return fc, [(f["properties"], shape(f["geometry"])) for f in fc["features"]]


def hits(feats, lon, lat):
    p = Point(lon, lat)
    return [pr for pr, g in feats if pr["render"] == "fill" and g.covers(p)]


def check_geometry(path=GJ):
    fc, feats = load(path)
    res = []
    for name, lon, lat, rule, arg in POINTS:
        h = hits(feats, lon, lat)
        ids = {x["id"] for x in h}; fams = {x["family"] for x in h}
        if rule == "in_ids": ok = bool(ids & arg) and len(h) == 1
        elif rule == "not_fams": ok = not (fams & arg)
        elif rule == "no_fill": ok = not h
        elif rule == "fam": ok = fams == {arg}
        res.append({"check": f"{name}: {rule} {sorted(arg) if isinstance(arg, set) else arg}",
                    "found_ids": sorted(ids), "ok": bool(ok)})
    ids_all = [p["id"] for p, _ in feats]
    fams_all = {p["family"] for p, _ in feats}
    def add(c, ok, info=""): res.append({"check": c, "ok": bool(ok), "info": info})
    add("no papal family/feature anywhere", "papal" not in fams_all and not any("papal" in i for i in ids_all))
    add("no Wales/March feature (England+Wales one fill)", not any(("wales" in i or "march" in i) for i in ids_all))
    add("Milan has no polygon (gaussian fringe only)",
        all(p["render"] == "gaussian" for p, g in feats if "milan" in p["id"]))
    ire = [g for p, g in feats if p["id"] == "ireland_eng"][0]
    add("Ireland English tint east only (west edge east of -7.4 lon)", ire.bounds[0] > -7.4, f"bounds {tuple(round(b,2) for b in ire.bounds)}")
    gas = [g for p, g in feats if p["id"] == "gascony"][0]
    add("Gascony coastal band only (east edge west of 0.0 lon, north edge south of 45.3)",
        gas.bounds[2] < 0.0 and gas.bounds[3] < 45.3, f"bounds {tuple(round(b,2) for b in gas.bounds)}")
    add("no aourednik/world_1300 source", "aourednik" not in json.dumps([p["provenance"] for p, _ in feats]).lower())
    add("every feature has provenance + REALMS row",
        all(p.get("provenance") and p.get("realms_rows") for p, _ in feats))
    add("no exclusive-fill overlaps", _no_overlap(feats))
    return res


def _no_overlap(feats):
    fl = [(p, g) for p, g in feats if p["render"] == "fill"]
    for i in range(len(fl)):
        for j in range(i + 1, len(fl)):
            if fl[i][1].intersection(fl[j][1]).area > 1e-6:
                return False
    return True


def check_raster(weights, lonlat_to_px, shape_hw, label_texts, realm_words):
    """weights: dict family -> float array (H,W) of rendered fill weight (pre-paint)."""
    res = []
    H, W = shape_hw
    for name, lon, lat, rule, arg in POINTS:
        x, y = lonlat_to_px(lon, lat)
        xi, yi = int(round(x)), int(round(y))
        if not (0 <= xi < W and 0 <= yi < H):
            continue
        w = {f: float(a[yi, xi]) for f, a in weights.items()}
        tot = sum(w.values())
        dom = max(w, key=w.get) if tot > 0.05 else None
        if rule == "not_fams": ok = sum(w.get(f, 0) for f in arg) < 0.5 * max(tot, 1e-6) and dom not in arg
        elif rule == "no_fill": ok = tot < 0.30
        elif rule == "fam": ok = dom == arg
        elif rule == "in_ids": continue   # id-level is a geometry fact; raster keeps family only
        res.append({"check": f"raster {name}: {rule}", "dominant": dom,
                    "weights": {k: round(v, 3) for k, v in w.items() if v > 0.01}, "ok": bool(ok)})
    bad = [t for t in label_texts if any(r in t.lower() for r in realm_words)]
    res.append({"check": "raster: no realm names/legend/dates on plate", "labels": label_texts, "ok": not bad})
    return res


if __name__ == "__main__":
    r = check_geometry()
    fails = [x for x in r if not x["ok"]]
    print(json.dumps({"n": len(r), "fails": fails, "all": r}, indent=1))
    sys.exit(1 if fails else 0)
