"""Build sources/realms/realms_1327_v1.geojson from OpenHistoricalMap (CC0) relations
plus hand-coarse areas, strictly following longform/edward-ii-feature/REALMS-1327-v1.md.

Raw OHM captures (Overpass `rel(<id>);out geom;`, fetched 2026-10-30 19:44 EDT) live in
sources/realms/ohm_raw/r<id>.json.  No aourednik / world_1300 geometry is used anywhere.
Run:  python build_realms_1327.py   (writes the GeoJSON; deterministic)
"""
import json, os
from shapely.geometry import LineString, Polygon, Point, mapping, shape
from shapely.ops import polygonize, unary_union, linemerge

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "sources/realms/ohm_raw")
OUT = os.path.join(HERE, "sources/realms/realms_1327_v1.geojson")
SIMPLIFY_DEG = 0.008          # ~0.6-0.9 km; well under 1 output px at either framing


def ohm(rid):
    d = json.load(open(os.path.join(RAW, f"r{rid}.json")))
    rel = [e for e in d["elements"] if e["type"] == "relation"][0]
    outer, inner = [], []
    for m in rel["members"]:
        if m["type"] != "way" or "geometry" not in m:
            continue
        ls = LineString([(p["lon"], p["lat"]) for p in m["geometry"]])
        (inner if m["role"] == "inner" else outer).append(ls)
    if not outer:
        raise ValueError(f"r{rid} has no area geometry in OHM")
    po = unary_union(list(polygonize(unary_union(outer))))
    if inner:
        pi = unary_union(list(polygonize(unary_union(inner))))
        po = po.difference(pi)
    po = po.buffer(0)
    return po, rel["tags"].get("name:en", rel["tags"].get("name"))


def poly(pts):
    return Polygon(pts).buffer(0)


# ---------------- hand-coarse shapes (lon, lat), each cites its REALMS row ----------------
HAND = {
    # R07: coastal Bordeaux -> Bayonne band only, feathered inland at render; not Agenais/Saintonge
    "gascony": poly([(-1.30, 45.20), (-0.75, 45.12), (-0.30, 44.95), (-0.22, 44.70), (-0.45, 44.30),
                      (-0.80, 43.95), (-1.05, 43.62), (-1.15, 43.38), (-1.62, 43.30), (-1.60, 43.70),
                      (-1.40, 44.40), (-1.30, 45.20)]),
    # R04: English lordship, east & south-east only (Dublin, Meath, coastal Leinster)
    "ireland_eng": poly([(-6.30, 54.02), (-5.95, 53.70), (-6.02, 53.10), (-6.15, 52.55), (-6.35, 52.15),
                          (-6.95, 52.08), (-7.20, 52.30), (-7.05, 52.80), (-7.25, 53.30), (-7.00, 53.75),
                          (-6.60, 54.02), (-6.30, 54.02)]),
    # R06: France family envelope (OHM r2956030 carries only a label node, no area); higher-priority
    #      OHM/hand shapes are subtracted, so Imperial lands, Flanders, Majorca etc. come out.
    "france": poly([(1.40, 51.40), (2.60, 51.30), (3.10, 51.20), (3.90, 50.95), (3.55, 50.40), (4.20, 50.00),
                     (4.80, 49.80), (5.10, 49.30), (5.40, 48.70), (5.60, 48.10), (5.40, 47.60), (5.05, 46.80),
                     (4.95, 46.10), (4.86, 45.62), (4.78, 45.20), (4.72, 44.80), (4.66, 44.25), (4.62, 43.95),
                     (4.45, 43.55), (4.30, 43.30), (3.30, 43.00), (3.05, 42.50), (1.50, 42.35),
                     (0.50, 42.60), (-0.50, 42.85), (-1.40, 43.10), (-1.90, 43.35), (-2.20, 43.70),
                     (-1.70, 45.20), (-1.70, 46.20), (-2.60, 47.00), (-5.40, 48.30), (-4.80, 49.00),
                     (-1.90, 48.85), (-2.00, 49.80), (0.10, 49.80), (1.30, 50.30), (1.40, 51.40)]),
    # R09/R12/R13 (+Imperial rim to frame edge): one Imperial hue, no internal lines
    "empire_low": poly([(3.85, 51.05), (4.25, 51.32), (3.55, 51.42), (3.35, 51.75), (3.90, 52.10),
                         (4.40, 53.60), (7.20, 53.70), (9.00, 54.60), (12.0, 56.0), (24.0, 56.0), (24.0, 46.70), (14.0, 46.70),
                         (10.50, 46.60), (9.00, 46.30), (8.00, 46.00), (7.00, 45.90), (6.20, 46.30),
                         (6.00, 46.80), (6.50, 47.40), (5.90, 47.80), (5.70, 48.30), (5.40, 48.90),
                         (5.00, 49.50), (4.60, 49.90), (4.20, 50.10), (3.70, 50.35), (3.75, 50.80),
                         (3.85, 51.05)]),
}
# R06: Lyon French since 1312 (OHM Arles shape still holds it) -> carved out to France
HAND["lyonnais"] = poly([(4.30, 46.05), (4.86, 46.00), (4.93, 45.78), (4.88, 45.55), (4.60, 45.45), (4.30, 45.60), (4.30, 46.05)])
# R17/R18: Rhone east-bank gap left by OHM (Comtat/Orange holes) folded into Provence softness
HAND["rhone_east"] = poly([(4.70, 44.60), (5.15, 44.60), (5.15, 43.80), (4.70, 43.80), (4.70, 44.60)])
AVIGNON = (4.80833, 43.94861)        # MAP-PLACES authority point
AVIGNON_DISC_KM = 6.0                # R19 override: Avignon city folded into Provence fill

# (id, family, sources, rows, status, feather_km, alpha, note)
SPEC = [
    ("france_lyon", "france", ["hand-coarse"], "R06", "VERIFIED", 18, 1.0, "Lyon/Lyonnais French (1312 treaty); overrides OHM Arles."),
    ("empire_provence", "empire", ["r2892600 (southern part)", "r2851366 (Comtat, folded)", "hand-coarse: Avignon disc + Rhone east-bank fill"],
     "R17,R18,R19", "COARSE", 14, 0.62, "Provence/Arles south; Imperial hue softened. Avignon + Comtat inside (R18 safest option); NO papal fill (R19 overrides OHM)."),
    ("empire_arles", "empire", ["r2892600", "r2892602"], "R14,R15,R16", "VERIFIED", 14, 1.0,
     "Kingdom of Burgundy/Arles: Savoy, County of Burgundy, Dauphine. Imperial, not French."),
    ("flanders", "flanders", ["r2891983"], "R08,R09", "COARSE", 18, 0.85,
     "Royal Flanders; rendered as a France->Empire gradient across the Scheldt, no hard line."),
    ("scotland", "scotland", ["r2869806"], "R03", "VERIFIED", 10, 1.0, "Own hue; soft border; Berwick Scottish."),
    ("brittany", "france_fam", ["r2805398"], "R10", "COARSE", 16, 0.80, "France-family tint, different value."),
    ("burgundy_duchy", "france_fam", ["r2893764"], "R11", "COARSE", 16, 0.80, "France-family tint; NOT merged with the County."),
    ("gascony", "england", ["hand-coarse"], "R07", "COARSE", 22, 0.70, "Coastal Bordeaux-Bayonne band, feathered inland."),
    ("navarre", "france_fam", ["r2803894"], "R22", "VERIFIED", 14, 0.65, "France-linked tint (Charles IV); no Evreux."),
    ("aragon", "aragon", ["r2750772", "r2860660 (Majorca folded: Roussillon, Montpellier)"], "R24,R26", "VERIFIED", 14, 0.55,
     "Muted edge hue; Montpellier NOT French."),
    ("castile", "castile", ["r2803896"], "R23", "VERIFIED", 14, 0.55, "Muted edge hue."),
    ("portugal", "portugal", ["r2692924"], "R25", "VERIFIED", 14, 0.50, "Muted edge hue."),
    ("england", "england", ["r2802023"], "R01,R02", "VERIFIED", 10, 1.0, "England + Wales one fill, no Welsh/March line."),
    ("ireland_eng", "england_light", ["hand-coarse"], "R04", "COARSE", 30, 0.66, "Lighter England-family, east/south-east only; Gaelic Ireland neutral (R05)."),
    ("empire_low", "empire", ["hand-coarse", "r2831646", "r2840561", "r2958280", "r2812125", "r2831144"], "R09,R12,R13", "COARSE", 18, 1.0,
     "Imperial rim (Low Countries, Brabant, Cologne, Rhineland, Lorraine, Alsace, Swiss). OHM Holland/Zeeland/Hainaut/Namur/Cambresis unioned in."),
    ("france", "france", ["hand-coarse"], "R06", "COARSE", 18, 1.0,
     "Royal domain + fiefs as one family; outer edge coarse; Lyon inside (1312)."),
]
GAUSS = [("milan_fringe", "empire", ["hand-coarse"], "R20", "COARSE", (9.25, 45.55), 75, 0.30,
          "No polygon: a soft Gaussian fade of the Imperial hue over Lombardy.")]
NEUTRAL = "R05 Gaelic Ireland, R21 rest of Italy (incl. Papal States r2888199 - deliberately NOT used), R27 Granada"


def build():
    km_deg = 111.32
    geoms, names = {}, {}
    def src(r):
        g, n = ohm(r); names[r] = n; return g
    arles = src(2892600).union(src(2892602))
    comtat = src(2851366)
    av = Point(AVIGNON).buffer(AVIGNON_DISC_KM / km_deg / 0.72)
    south = Polygon([(4.55, 43.0), (8.0, 43.0), (8.0, 44.45), (4.55, 44.45)])
    geoms["france_lyon"] = HAND["lyonnais"]
    geoms["empire_provence"] = arles.intersection(south).union(comtat).union(HAND["rhone_east"]).union(av)
    geoms["empire_arles"] = arles.difference(south)
    geoms["flanders"] = src(2891983)
    geoms["scotland"] = src(2869806)
    geoms["brittany"] = src(2805398)
    geoms["burgundy_duchy"] = src(2893764)
    geoms["gascony"] = HAND["gascony"]
    geoms["navarre"] = src(2803894)
    geoms["aragon"] = src(2750772).union(src(2860660))
    geoms["castile"] = src(2803896)
    geoms["portugal"] = src(2692924)
    geoms["england"] = src(2802023)
    geoms["ireland_eng"] = HAND["ireland_eng"]
    lowc = [src(r) for r in (2831646, 2840561, 2958280, 2812125, 2831144)]
    geoms["empire_low"] = unary_union([HAND["empire_low"]] + lowc)
    geoms["france"] = HAND["france"]
    # exclusive by priority (SPEC order)
    taken = Polygon()
    feats = []
    for (fid, fam, srcs, rows, status, fk, a, note) in SPEC:
        gs = geoms[fid].simplify(SIMPLIFY_DEG, preserve_topology=True).buffer(0)
        g = gs.difference(taken).buffer(0)
        taken = taken.union(gs).buffer(0)
        if g.is_empty:
            continue
        prov = []
        for s in srcs:
            if s.startswith("r"):
                rid = int(s[1:].split()[0])
                prov.append({"source": "OpenHistoricalMap", "relation": f"r{rid}", "name": names.get(rid),
                             "url": f"https://www.openhistoricalmap.org/relation/{rid}", "licence": "CC0",
                             "qualifier": s[len(f'r{rid}'):].strip() or None})
            else:
                prov.append({"source": s, "licence": "own work (Posterity), hand-coarse"})
        feats.append({"type": "Feature", "geometry": mapping(g), "properties": {
            "id": fid, "family": fam, "render": "fill", "realms_rows": rows, "status": status,
            "feather_km": fk, "alpha": a, "provenance": prov, "note": note}})
    for (fid, fam, srcs, rows, status, c, sig, a, note) in GAUSS:
        feats.append({"type": "Feature", "geometry": mapping(Point(c)), "properties": {
            "id": fid, "family": fam, "render": "gaussian", "sigma_km": sig, "realms_rows": rows,
            "status": status, "alpha": a, "provenance": [{"source": "hand-coarse", "licence": "own work (Posterity), hand-coarse"}],
            "note": note}})
    fc = {"type": "FeatureCollection", "name": "realms_1327_v1",
          "spec": "longform/edward-ii-feature/REALMS-1327-v1.md",
          "sources": "OpenHistoricalMap relations (CC0), Overpass out geom fetched 2026-10-30 19:44 EDT, raw in sources/realms/ohm_raw/; hand-coarse areas own work. No aourednik/world_1300 geometry.",
          "neutral": NEUTRAL, "priority": [s[0] for s in SPEC],
          "simplify_deg": SIMPLIFY_DEG, "features": feats}
    json.dump(fc, open(OUT, "w"), indent=0)
    return fc


if __name__ == "__main__":
    fc = build()
    for f in fc["features"]:
        g = shape(f["geometry"]); print(f["properties"]["id"], g.geom_type, round(g.area, 3))
    print("wrote", OUT, os.path.getsize(OUT))
