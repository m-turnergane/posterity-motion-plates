import json
from shapely.geometry import LineString, Polygon, MultiPolygon
from shapely.ops import linemerge, polygonize, unary_union
d = json.load(open('sources/ohm_860_geom.json'))
out = {}
for e in d['elements']:
    if e['type'] != 'relation': continue
    outer, inner = [], []
    for m in e['members']:
        if m['type'] != 'way' or 'geometry' not in m: continue
        ls = LineString([(g['lon'], g['lat']) for g in m['geometry'] if g])
        (inner if m.get('role') == 'inner' else outer).append(ls)
    po = list(polygonize(linemerge(outer))) if outer else []
    pi = list(polygonize(linemerge(inner))) if inner else []
    g = unary_union(po)
    if pi: g = g.difference(unary_union(pi))
    t = e['tags']
    out[e['id']] = dict(name=t.get('name'), name_en=t.get('name:en'), start=t.get('start_date'), end=t.get('end_date'), wikidata=t.get('wikidata'), geom=g.__geo_interface__ if not g.is_empty else None)
    print(e['id'], t.get('name:en') or t.get('name'), t.get('start_date'), t.get('end_date'), 'outer ways', len(outer), 'area', round(g.area, 2), 'bounds', [round(b, 2) for b in g.bounds] if not g.is_empty else None)
json.dump(out, open('sources/ohm_860_polygons.json', 'w'))
