#!/usr/bin/env python3
"""refpack_p05 - Björn Ironside P05 animated-map registration reference (native 9:16).
Run with /workspace/mpvenv/bin/python (numpy, scipy, shapely, PIL, pyshp).
Authority: ../../map-reference-data.md (Archivist). Coordinates below are copied from its section 1 verbatim.
Writes only inside this folder; refuses to overwrite (pass --force to rebuild into an empty img/)."""
import json, os, sys, math, hashlib, heapq
import numpy as np, shapefile
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from shapely.geometry import LineString, Point, shape, MultiPolygon, Polygon
from shapely.ops import polygonize, unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
BJ = os.path.abspath(os.path.join(HERE, '..', '..'))
NE = '/workspace/posterity/engine-rnd/maps/sources/naturalearth'
OHM = os.path.join(BJ, 'map', 'sources', 'ohm_860_geom.json')
FELL = '/usr/share/fonts/truetype/sand-box/google/IM Fell English SC/IMFellEnglishSC-Regular.ttf'
DJV = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
DJVB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
IMG = os.path.join(HERE, 'img')
FORCE = '--force' in sys.argv

def outpath(name):
    p = os.path.abspath(os.path.join(HERE, name))
    assert p.startswith(HERE + os.sep), p
    if os.path.exists(p) and not FORCE:
        raise SystemExit(f'refusing to overwrite {p}')
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p

# ---------------- frame ----------------
W, H, S = 1080, 1920, 2           # out px; S = supersample (plate scale 2160x3840)
LON0, LAT0, WKM = 3.0, 40.7, 2260.0
R = 6371000.0
MPP = WKM * 1000 / W               # metres per out px
PROJ4 = f'+proj=laea +lat_0={LAT0} +lon_0={LON0} +x_0=0 +y_0=0 +R=6371000 +units=m +no_defs'
PUSH = 1.06

def fwd(lon, lat):
    l = np.radians(np.asarray(lon, float)); p = np.radians(np.asarray(lat, float))
    l0, p0 = math.radians(LON0), math.radians(LAT0)
    k = np.sqrt(2 / (1 + math.sin(p0) * np.sin(p) + math.cos(p0) * np.cos(p) * np.cos(l - l0)))
    return R * k * np.cos(p) * np.sin(l - l0), R * k * (math.cos(p0) * np.sin(p) - math.sin(p0) * np.cos(p) * np.cos(l - l0))

def inv(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    rho = np.hypot(x, y); c = 2 * np.arcsin(rho / (2 * R))
    p0 = math.radians(LAT0)
    with np.errstate(invalid='ignore', divide='ignore'):
        lat = np.arcsin(np.cos(c) * math.sin(p0) + np.where(rho == 0, 0, y * np.sin(c) * math.cos(p0) / np.where(rho == 0, 1, rho)))
        lon = LON0 + np.degrees(np.arctan2(x * np.sin(c), rho * math.cos(p0) * np.cos(c) - y * math.sin(p0) * np.sin(c)))
    return lon, np.degrees(lat)

def px(lon, lat):
    x, y = fwd(lon, lat)
    return x / MPP + W / 2, H / 2 - y / MPP

def unpx(u, v):
    return inv((np.asarray(u, float) - W / 2) * MPP, (H / 2 - np.asarray(v, float)) * MPP)

TITLE_SAFE = [54, 96, 1026, 1824]
PIN_SAFE = [64, 96, 1015, 1824]
PUSH_CROP = [round(W / 2 - W / 2 / PUSH, 1), round(H / 2 - H / 2 / PUSH, 1), round(W / 2 + W / 2 / PUSH, 1), round(H / 2 + H / 2 / PUSH, 1)]
CAPTION_Y_OUT = 1280                                   # v2b: no labels/markers below y=1280 (after push)
CAPTION_Y_SRC = H / 2 + (CAPTION_Y_OUT - H / 2) / PUSH # same line before push (centred push)
PUSH_TITLE_SAFE = [W / 2 + (TITLE_SAFE[0] - W / 2) / PUSH, H / 2 + (TITLE_SAFE[1] - H / 2) / PUSH,
                   W / 2 + (TITLE_SAFE[2] - W / 2) / PUSH, H / 2 + (TITLE_SAFE[3] - H / 2) / PUSH]

# ---------------- places: map-reference-data.md section 1 (verbatim) ----------------
PLACES = [  # code, key, name, lat, lon, wikidata, data status, P05 role
 ('P1','loire','Loire',47.2700,-2.1844,'Q1469','departure anchor (S1 UNCERTAIN)','not drawn in P05'),
 ('P2','galicia','Galicia',42.8000,-7.9000,'Q3908','region centroid, label only','optional (S2)'),
 ('P3','asturias','Asturias',43.3614,-5.8478,'Q3934','region point, realm label optional','not drawn'),
 ('P4','beja','Beja',38.0167,-7.8667,'Q321455','do not pin','not drawn'),
 ('P5','guadalquivir','Guadalquivir',36.7913,-6.3567,'Q14309','river mouth','optional (S2/S3)'),
 ('P6','seville','Seville',37.3886,-5.9950,'Q8717','disputed (D2)','not drawn'),
 ('P7','algeciras','Algeciras',36.1275,-5.4539,'Q484552','documented','P05 route start'),
 ('P8','strait','Strait of Gibraltar',35.9739,-5.5161,'Q36124','waypoint','P05 waypoint (no dot)'),
 ('P9','nekor','Nekor',35.0898,-3.8075,'Q3537816','documented','P05 stop'),
 ('P10','orihuela','Orihuela',38.0848,-0.9440,'Q24008496','documented (stands for Tudmir landing)','P05 stop'),
 ('P11','mallorca','Mallorca',39.6167,2.9833,'Q8828','disputed order (D4)','not drawn'),
 ('P12','menorca','Menorca',39.9667,4.0833,'Q52636','disputed order (D4)','not drawn'),
 ('P13','formentera','Formentera',38.7000,1.4500,'Q31916364','disputed order (D4)','not drawn'),
 ('P14','camargue','Camargue',43.5333,4.5000,'Q218151','documented, winter camp 859-860','P05 stop'),
 ('P15','rhone','Rhône',43.3342,4.8442,'Q602','river mouth, entry waypoint','P05 waypoint'),
 ('P16','valence','Valence',44.9325,4.8908,'Q8848','documented (S8)','optional (S8)'),
 ('P17','pisa','Pisa',43.7167,10.4000,'Q13375','documented (AB 860)','P05 END-MARK (unlabelled per storyboard)'),
 ('P18','luna','(no label) Luna',44.0640,10.0170,'Q579763','legend only (GND); UNLABELLED','NO mark, NO label in P05 (storyboard v3)'),
 ('P19','rome','Rome',41.8931,12.4828,'Q220','legendary target, never reached','legend leg aims here; line stops short'),
 ('P20','medina_sidonia','Medina Sidonia',36.4577,-5.9273,'Q642200','event offshore, dotted','not drawn'),
 ('P21','pamplona','Pamplona',42.8167,-1.6500,'Q10282','disputed (D5)','not drawn'),
 ('P22','nimes','Nîmes',43.8383,4.3597,'Q42807','optional secondary (D6), recommend omit','not drawn'),
 ('P23','arles','Arles',43.6769,4.6286,'Q48292','optional secondary (D6), recommend omit','not drawn'),
]
PL = {p[0]: p for p in PLACES}

# ---------------- legs: map-reference-data.md section 2 ----------------
# chain: list of place codes; 'river:<name>' legs follow the NE river centreline.
LEGS = [
 dict(id='S1', chain=['P1','P2'], type='uncertain', style='dotted', year='859', p05=False, src='AB 859 / WP-Nekor line 5 (Loire base is inference)'),
 dict(id='S2', chain=['P2','P5'], type='documented', style='solid', year='859', p05=False, src='Sebastian (SB 25643-25644); Ibn Idhari (SB 25570, 25576)'),
 dict(id='S2a', chain=['P5','P6'], river='Guadalquivir', type='uncertain', style='dotted', year='859', p05=False, src='Ibn Idhari vs Nowairi (D2)'),
 dict(id='S3', chain=['P5','P7'], type='documented', style='solid', year='859', p05=False, src='Ibn Idhari (SB 25580-25582)'),
 dict(id='S4', chain=['P7','P8','P9'], type='documented', style='solid', year='859', p05=True, src='Ibn Idhari, Bekri, Ibn al-Kutia, Sebastian; AB 859 "inter Hispanias et Affricam"'),
 dict(id='S5', chain=['P9','P10'], type='documented', style='solid', year='859', p05=True, src='Ibn Idhari (SB 25583-25585); Nowairi (SB 25609-25610)'),
 dict(id='S6', chain=['P10','P13','P11','P12'], type='uncertain', style='dotted', year='859', p05=False, src='Sebastian only (SB 25658-25659); D4'),
 dict(id='S7', chain=['P10','P15','P14'], type='documented', style='solid', year='859', p05=True, src='AB 859 (AB 3293-3295); Ibn Idhari (SB 25585-25586). Drawn from Orihuela, the data allows "Balearics (or Orihuela)"'),
 dict(id='S8', chain=['P14','P16'], river='Rhône', type='documented', style='solid (out and back along river)', year='860', p05=False, src='AB 860 (AB 3441-3444)'),
 dict(id='S9', chain=['P14','P17'], type='documented', style='solid (coastal arc)', year='860', p05=True, src='AB 860 (AB 3455-3456); Ibn al-Kutia (SB 25628-25629)'),
 dict(id='S10', chain=['S9*','P18'], type='legendary', style='broken', year='legend', p05=False, src='GND ch. IX (GND 953-954). Not drawn: storyboard v3 says no Luna label or mark'),
 dict(id='S11', chain=['P18','P19~'], type='legendary', style='broken, stop short of Rome', year='legend', p05=False, src='GND 952-953, 964-965'),
 dict(id='P05-LEG', chain=['P17','P19~'], type='legendary', style='broken, paler; stops at the coast short of Rome', year='legend', p05=True, src='Storyboard v3 P05 "broken lighter line for the legendary leg to Rome" from the end-mark; geometry rule from data S11 (stop short, do not touch Rome)'),
 dict(id='S12', chain=['P17','P8','P20~'], type='uncertain', style='dotted', year='861', p05=False, src='Ibn Idhari (SB 25589-25600); path UNCERTAIN'),
 dict(id='S13', chain=['P8','P1'], type='uncertain', style='dotted', year='861-862', p05=False, src='AB 862 (AB 3646-3647); path UNCERTAIN'),
]
P05_ORDER = ['S4', 'S5', 'S7', 'S9', 'P05-LEG']

# ---------------- realms: map-reference-data.md section 4, OHM geometry ----------------
REALM_STYLE = {  # pigment suggestion (owner style: crimson / weathered royal blue / deep antique gold lead)
 2750107: ('West Francia', 'weathered royal blue', (63, 92, 150)),
 2697816: ('Emirate of Córdoba', 'crimson', (158, 38, 44)),
 2888203: ('Papal lands', 'deep antique gold', (176, 132, 38)),
 2806711: ('Lotharingia', 'ochre (gold family, lighter)', (196, 160, 82)),
 2805415: ('Brittany', 'slate blue-grey', (110, 128, 140)),
 2740129: ('Asturias', 'sage green', (112, 138, 96)),
 2740068: ('Pamplona', 'umber', (136, 104, 74)),
 2860230: ('Aghlabids', 'sienna', (170, 98, 56)),
 2860243: ('Eastern Roman Empire', 'imperial purple, muted', (112, 78, 120)),
 2888914: ('Benevento', 'olive', (128, 128, 70)),
 2888433: ('Naples', 'teal', (70, 120, 120)),
 2888516: ('Sorrento', 'teal, lighter', (100, 146, 140)),
 2860176: ('Emirate of Bari', 'rose madder', (170, 90, 100)),
 2839584: ('Venice', 'grey-blue', (100, 116, 140)),
}
BALEARIC_BOX = (1.0, 38.5, 4.6, 40.2)   # lon/lat box: claimed by BOTH West Francia and Eastern Roman Empire in OHM

def realm_polys():
    els = json.load(open(OHM))['elements']
    out = {}
    for e in els:
        if e['id'] not in REALM_STYLE: continue
        ls = [LineString([(p['lon'], p['lat']) for p in m['geometry']]) for m in e['members']
              if m['type'] == 'way' and m.get('geometry') and len(m['geometry']) > 1]
        pg = unary_union(list(polygonize(unary_union(ls))))
        parts = [g for g in getattr(pg, 'geoms', [pg])]
        kept = []
        for g in parts:
            c = g.representative_point()
            if BALEARIC_BOX[0] <= c.x <= BALEARIC_BOX[2] and BALEARIC_BOX[1] <= c.y <= BALEARIC_BOX[3]:
                continue
            kept.append(g)
        out[e['id']] = dict(geom=unary_union(kept), tags=e['tags'], dropped=len(parts) - len(kept))
    return out

# ---------------- natural earth ----------------
def read_shp(path):
    return shapefile.Reader(path)

def proj_ring(pts, s=S):
    a = np.asarray(pts, float)
    u, v = px(a[:, 0], a[:, 1])
    return list(zip((u * s).tolist(), (v * s).tolist()))

def frame_lonlat_box(margin_px=200):
    us = np.r_[np.linspace(-margin_px, W + margin_px, 60), np.full(60, W + margin_px), np.linspace(W + margin_px, -margin_px, 60), np.full(60, -margin_px)]
    vs = np.r_[np.full(60, -margin_px), np.linspace(-margin_px, H + margin_px, 60), np.full(60, H + margin_px), np.linspace(H + margin_px, -margin_px, 60)]
    lo, la = unpx(us, vs)
    return lo.min(), la.min(), lo.max(), la.max()

def raster_polys(shapes_iter, s=S):
    im = Image.new('L', (W * s, H * s), 0); d = ImageDraw.Draw(im)
    bx = frame_lonlat_box()
    for shp in shapes_iter:
        if shp.bbox[2] < bx[0] or shp.bbox[0] > bx[2] or shp.bbox[3] < bx[1] or shp.bbox[1] > bx[3]: continue
        pts = shp.points; parts = list(shp.parts) + [len(pts)]
        for i in range(len(parts) - 1):
            ring = pts[parts[i]:parts[i + 1]]
            if len(ring) < 3: continue
            # pyshp: outer rings clockwise, holes counter-clockwise
            a = np.asarray(ring); area = 0.5 * np.sum(a[:-1, 0] * a[1:, 1] - a[1:, 0] * a[:-1, 1])
            d.polygon(proj_ring(ring, s), fill=255 if area <= 0 else 0)
    return np.array(im) > 127

def raster_shapely(geom, s=S):
    im = Image.new('L', (W * s, H * s), 0); d = ImageDraw.Draw(im)
    for g in getattr(geom, 'geoms', [geom]):
        if g.is_empty: continue
        d.polygon(proj_ring(g.exterior.coords, s), fill=255)
        for r in g.interiors: d.polygon(proj_ring(r.coords, s), fill=0)
    return np.array(im) > 127

def river_lines(names):
    r = read_shp(os.path.join(NE, 'ne_10m_rivers_lake_centerlines', 'ne_10m_rivers_lake_centerlines'))
    out = []
    bx = frame_lonlat_box(0)
    for sr in r.iterShapeRecords():
        rec = sr.record.as_dict(); shp = sr.shape
        if shp.bbox[2] < bx[0] or shp.bbox[0] > bx[2] or shp.bbox[3] < bx[1] or shp.bbox[1] > bx[3]: continue
        nm = rec.get('name') or ''
        if names is not None and nm not in names: continue
        if names is None and (rec.get('scalerank') or 99) > 6 and nm not in ('Guadalquivir', 'Tevere'): continue
        pts = shp.points; parts = list(shp.parts) + [len(pts)]
        for i in range(len(parts) - 1):
            seg = pts[parts[i]:parts[i + 1]]
            if len(seg) > 1: out.append((nm, rec.get('scalerank'), seg))
    return out

# ---------------- build ----------------
def main():
    log = []
    bx = frame_lonlat_box(0)
    land_s = raster_polys(read_shp(os.path.join(NE, 'ne_10m_land', 'ne_10m_land')).shapes())
    lakes_s = raster_polys(read_shp(os.path.join(NE, 'ne_10m_lakes', 'ne_10m_lakes')).shapes())
    land_s &= ~lakes_s
    # realms
    RP = realm_polys()
    rid_s = np.zeros(land_s.shape, np.int16); cnt = np.zeros(land_s.shape, np.int16)
    keys = list(REALM_STYLE)
    # overlapping OHM claims (Pamplona inside West Francia; a West Francia/Lotharingia strip): the smaller,
    # more specific realm wins. Balearics were already removed from both claimants (see BALEARIC_BOX).
    order = sorted([k for k in keys if k in RP], key=lambda k: -RP[k]['geom'].area)
    for k in keys:
        if k not in RP: log.append(f'realm {k} missing in OHM file')
    for k in order:
        i = keys.index(k) + 1
        m = raster_shapely(RP[k]['geom']); cnt += m; rid_s[m] = i
    overlap = (cnt > 1) & land_s
    rid_s[~land_s] = 0
    # coastal snap: unassigned land within 3 out px of sea AND of a realm -> nearest realm (NE vs OHM coastline mismatch only)
    sea_d = ndimage.distance_transform_edt(land_s)
    rd, (ri, rj) = ndimage.distance_transform_edt(rid_s == 0, return_indices=True)
    snap = land_s & (rid_s == 0) & (sea_d <= 3 * S) & (rd <= 3 * S)
    rid_s[snap] = rid_s[ri[snap], rj[snap]]
    log.append(f'overlap px (out) resolved smaller-realm-wins: {int(overlap.sum() / S / S)}; coastal-snap px (out): {int(snap.sum() / S / S)}')
    # borders: realm id change on land (incl. realm vs no-realm), not along the sea
    b = np.zeros_like(land_s)
    for dy, dx in ((0, 1), (1, 0)):
        a1 = rid_s[:H * S - dy, :W * S - dx]; a2 = rid_s[dy:, dx:]
        l1 = land_s[:H * S - dy, :W * S - dx]; l2 = land_s[dy:, dx:]
        e = (a1 != a2) & l1 & l2
        b[:H * S - dy, :W * S - dx] |= e
    border_s = ndimage.binary_dilation(b, iterations=1)
    coast_s = land_s ^ ndimage.binary_erosion(land_s, iterations=2)

    # ---- base (clean) render at plate scale ----
    SEA = np.array((198, 210, 206), float); LAND = np.array((236, 224, 196), float)
    INK = np.array((52, 40, 30), float); RIVER = np.array((96, 128, 150), float)
    img = np.empty((H * S, W * S, 3), float); img[:] = SEA
    img[land_s] = LAND
    for i, k in enumerate(keys, 1):
        m = rid_s == i
        if m.any(): img[m] = LAND * 0.55 + np.array(REALM_STYLE[k][2]) * 0.45
    base = Image.fromarray(img.astype(np.uint8))
    d = ImageDraw.Draw(base)
    for nm, sr, seg in river_lines(None):
        w = 4 if nm in ('Rhône', 'Loire', 'Guadalquivir', 'Rhine', 'Rhein', 'Rhin', 'Tevere') else 3
        d.line(proj_ring(seg), fill=tuple(RIVER.astype(int)), width=w, joint='curve')
    arr = np.array(base).astype(float)
    arr[lakes_s] = SEA * 0.9 + RIVER * 0.1
    arr[border_s] = INK * 0.85 + arr[border_s] * 0.15
    arr[coast_s] = INK
    clean = Image.fromarray(arr.astype(np.uint8)).resize((W, H), Image.LANCZOS)

    # ---- sea routing grid (half out res) ----
    G = 2
    land_g = np.array(Image.fromarray(land_s.astype(np.uint8) * 255).resize((W // G, H // G), Image.BOX)) > 64
    gh, gw = land_g.shape
    dist = ndimage.distance_transform_edt(~land_g)              # sea cells: distance to land (grid cells)
    pen = 1 + 3.0 * np.clip((4.0 - dist) / 4.0, 0, 1)          # prefer ~4 cells (~17 km) offshore
    idx = np.arange(gh * gw).reshape(gh, gw)
    rows, cols, wts = [], [], []
    sea = ~land_g
    for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
        ys0, ys1 = 0, gh - dy
        xs0, xs1 = max(0, -dx), gw - max(0, dx)
        a = (slice(ys0, ys1), slice(xs0, xs1)); bsl = (slice(ys0 + dy, ys1 + dy), slice(xs0 + dx, xs1 + dx))
        ok = sea[a] & sea[bsl]
        w = math.hypot(dy, dx) * 0.5 * (pen[a] + pen[bsl])
        rows.append(idx[a][ok]); cols.append(idx[bsl][ok]); wts.append(w[ok])
    rows = np.concatenate(rows); cols = np.concatenate(cols); wts = np.concatenate(wts)
    graph = coo_matrix((np.r_[wts, wts], (np.r_[rows, cols], np.r_[cols, rows])), shape=(gh * gw, gh * gw)).tocsr()
    _, (si, sj) = ndimage.distance_transform_edt(land_g, return_indices=True)

    def place_px(code):
        p = PL[code]; u, v = px(p[4], p[3]); return float(u), float(v)
    def sea_cell(u, v):
        gi, gj = int(round(v / G)), int(round(u / G))
        gi = min(max(gi, 0), gh - 1); gj = min(max(gj, 0), gw - 1)
        if land_g[gi, gj]: gi, gj = int(si[gi, gj]), int(sj[gi, gj])
        return gi, gj
    def sea_path(c0, c1):
        a, bnode = idx[c0], idx[c1]
        _, pred = dijkstra(graph, indices=a, return_predecessors=True)
        path = [bnode]
        while path[-1] != a:
            p = pred[path[-1]]
            if p < 0: raise RuntimeError('no sea path')
            path.append(p)
        path = path[::-1]
        return [((n % gw) * G + G / 2 - 0.5, (n // gw) * G + G / 2 - 0.5) for n in path]

    def simplify_smooth(pts, keep_ends=True):
        ls = LineString(pts).simplify(1.5)
        c = list(ls.coords)
        for _ in range(3):
            if len(c) < 3: break
            n = [c[0]]
            for p, q in zip(c[:-1], c[1:]):
                n += [(0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]), (0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1])]
            n.append(c[-1]); c = n
        return c

    rivers_named = {}
    for nm, sr, seg in river_lines(['Rhône', 'Guadalquivir']):
        u, v = px(np.array(seg)[:, 0], np.array(seg)[:, 1])
        rivers_named.setdefault(nm, []).append(list(zip(u.tolist(), v.tolist())))
    def river_path(name, p0, p1):
        # pick vertices nearest to both endpoints across merged parts, walk along the merged line
        best = None
        for part in rivers_named[name]:
            a = np.array(part)
            i0 = int(np.argmin(np.hypot(*(a - p0).T))); i1 = int(np.argmin(np.hypot(*(a - p1).T)))
            dd = np.hypot(*(a[i0] - p0)) + np.hypot(*(a[i1] - p1))
            if best is None or dd < best[0]: best = (dd, part, i0, i1)
        dd, part, i0, i1 = best
        seg = part[min(i0, i1):max(i0, i1) + 1]
        if i0 > i1: seg = seg[::-1]
        log.append(f'river {name}: endpoint snap error {dd:.1f} px')
        return [p0] + seg + [p1]

    legs_out = {}; s9_line = None
    for L in LEGS:
        ch = L['chain']; pts = []
        if 'river' in L:
            pts = river_path(L['river'], place_px(ch[0]), place_px(ch[1]))
            poly = pts
        else:
            start = None
            if ch[0] == 'S9*':
                lu, lv = place_px('P18')
                arr9 = np.array(s9_line); k = int(np.argmin(np.hypot(arr9[:, 0] - lu, arr9[:, 1] - lv)))
                start = tuple(arr9[k]); seq = ch[1:]
                poly = [start]
            else:
                seq = ch; poly = []
            for a_, b_ in zip(([None] if start else []) + seq[:-1], seq if start else seq[1:]):
                pass
            nodes = ([('pt', start)] if start else []) + [('pl', c) for c in seq]
            prev = None
            for kind, val in nodes:
                stop_short = kind == 'pl' and val.endswith('~')
                code = val.rstrip('~') if kind == 'pl' else None
                pu = place_px(code) if code else val
                cell = sea_cell(*pu)
                if prev is None:
                    if not stop_short: poly.append(pu) if not poly else None
                    cur = cell
                else:
                    seg = sea_path(prev, cell)
                    poly += seg
                    if not stop_short: poly.append(pu)
                prev = cell
            poly = simplify_smooth(poly)
        if L['id'] == 'S9': s9_line = poly
        legs_out[L['id']] = poly

    # ---- QA: land crossing of each leg (excluding spurs within 8 px of a place) ----
    land_out = np.array(Image.fromarray(land_s.astype(np.uint8) * 255).resize((W, H), Image.BOX)) > 127
    qa = {}
    allp = np.array([place_px(c) for c in PL])
    for k, poly in legs_out.items():
        ls = LineString(poly); n = max(2, int(ls.length)); onland = 0; tot = 0
        for t in np.linspace(0, ls.length, n):
            p = ls.interpolate(t); u, v = p.x, p.y
            if np.min(np.hypot(allp[:, 0] - u, allp[:, 1] - v)) < 14: continue
            tot += 1
            if 0 <= int(v) < H and 0 <= int(u) < W and land_out[int(v), int(u)]: onland += 1
        qa[k] = dict(length_px=round(ls.length, 1), length_km=round(ls.length * MPP / 1000, 0), land_px_outside_spurs=onland)

    # ---------------- outputs ----------------
    os.makedirs(IMG, exist_ok=True)
    p_clean = outpath('img/bjorn_p05_9x16_ref_clean.png'); clean.save(p_clean, optimize=True)

    # zones
    fell40 = ImageFont.truetype(FELL, 40)
    allow = ['P7', 'P9', 'P10', 'P14', 'P15']
    route_pts = np.vstack([np.array(legs_out[k]) for k in P05_ORDER])
    dots = {c: place_px(c) for c in ['P7', 'P9', 'P10', 'P14', 'P15', 'P17', 'P19']}
    boxes = {}
    def collides(bb):
        x0, y0, x1, y1 = bb
        if x0 < PUSH_TITLE_SAFE[0] or x1 > PUSH_TITLE_SAFE[2] or y0 < PUSH_TITLE_SAFE[1] or y1 > CAPTION_Y_SRC: return True
        m = (route_pts[:, 0] > x0 - 6) & (route_pts[:, 0] < x1 + 6) & (route_pts[:, 1] > y0 - 6) & (route_pts[:, 1] < y1 + 6)
        if m.any(): return True
        for c, (u, v) in dots.items():
            if x0 - 10 < u < x1 + 10 and y0 - 10 < v < y1 + 10: return True
        for o in boxes.values():
            if not (x1 + 6 < o[0] or x0 - 6 > o[2] or y1 + 6 < o[1] or y0 - 6 > o[3]): return True
        return False
    for c in allow:
        name = PL[c][2]; tb = fell40.getbbox(name); tw, th = tb[2] - tb[0], tb[3] - tb[1]
        u, v = dots[c]
        cands = []
        for g in (14, 26, 40):
          cands += [('E', u + g, v - th / 2), ('W', u - g - tw, v - th / 2), ('N', u - tw / 2, v - g - th), ('S', u - tw / 2, v + g),
                 ('NE', u + g * .7, v - g * .7 - th), ('NW', u - g * .7 - tw, v - g * .7 - th), ('SE', u + g * .7, v + g * .7), ('SW', u - g * .7 - tw, v + g * .7),
                 ('W^', u - g - tw, v - th - 4), ('E^', u + g, v - th - 4)]   # raised W/E: keep box above the caption line
        for side, x0, y0 in cands:
            bb = [round(x0), round(y0), round(x0 + tw), round(y0 + th)]
            if not collides(bb): boxes[c] = bb + [side]; break
        else:
            log.append(f'label zone: no clean slot for {name}')
    # compass search: 190 px square, all sea, inside push title-safe, above caption line, away from route/labels
    sea_out = ~land_out; integ = sea_out.astype(np.int32).cumsum(0).cumsum(1)
    def all_sea(x0, y0, s):
        x1, y1 = x0 + s - 1, y0 + s - 1
        tot = integ[y1, x1] - (integ[y0 - 1, x1] if y0 else 0) - (integ[y1, x0 - 1] if x0 else 0) + (integ[y0 - 1, x0 - 1] if x0 and y0 else 0)
        return tot == s * s
    compass = None; CS = 190
    for y0 in range(int(PUSH_TITLE_SAFE[1]) + 40, int(CAPTION_Y_SRC) - CS, 8):
        for x0 in range(int(PUSH_TITLE_SAFE[0]), int(PUSH_TITLE_SAFE[2]) - CS, 8):
            if all_sea(x0, y0, CS) and not collides([x0, y0, x0 + CS, y0 + CS]):
                compass = [x0, y0, x0 + CS, y0 + CS]; break
        if compass: break
    log.append(f'compass zone: {compass}')

    def zones_layer(im, alpha=255):
        dz = ImageDraw.Draw(im, 'RGBA')
        dz.rectangle(TITLE_SAFE, outline=(0, 160, 0, alpha), width=3)
        dz.rectangle(PIN_SAFE, outline=(240, 140, 0, alpha), width=2)
        dz.rectangle([round(v) for v in PUSH_CROP], outline=(90, 90, 90, alpha), width=2)
        dz.line([0, CAPTION_Y_SRC, W, CAPTION_Y_SRC], fill=(200, 0, 160, alpha), width=3)
        if im.mode == 'RGB':
            for yy in range(int(CAPTION_Y_SRC) + 6, H, 18): dz.line([0, yy, W, yy], fill=(200, 0, 160, 90), width=1)
        else:
            dz.rectangle([0, int(CAPTION_Y_SRC), W, H], fill=(200, 0, 160, 28))
        for c, bb in boxes.items():
            dz.rectangle([bb[0] - 10, bb[1] - 10, bb[2] + 10, bb[3] + 10], outline=(30, 90, 230, alpha), width=3)
        if compass: dz.rectangle(compass, outline=(220, 0, 0, alpha), width=3)
        return im
    zim = zones_layer(Image.new('RGBA', (W, H), (0, 0, 0, 0)))
    p_z = outpath('img/bjorn_p05_9x16_zones_overlay.png'); zim.quantize(64, method=Image.Quantize.FASTOCTREE).save(p_z, optimize=True)

    # annotated reference
    ann = clean.copy().convert('RGB')
    hatch = Image.new('RGBA', (W, H), (0, 0, 0, 0)); hd = ImageDraw.Draw(hatch)
    for k in range(-H, W, 14): hd.line([k, 0, k + H, H], fill=(90, 70, 50, 70), width=1)
    rid_out = np.array(Image.fromarray(rid_s.astype(np.uint8)).resize((W, H), Image.NEAREST))
    gapmask = Image.fromarray(((rid_out == 0) & land_out).astype(np.uint8) * 255)
    ann.paste(hatch, (0, 0), Image.fromarray((np.array(gapmask) // 255 * np.array(hatch)[:, :, 3]).astype(np.uint8)))
    da = ImageDraw.Draw(ann, 'RGBA')
    def dash(poly, on, off, fill, width):
        ls = LineString(poly); t = 0.0
        while t < ls.length:
            seg = [ls.interpolate(s) for s in np.linspace(t, min(t + on, ls.length), 6)]
            da.line([(p.x, p.y) for p in seg], fill=fill, width=width); t += on + off
    for L in LEGS:
        poly = legs_out[L['id']]
        if L['p05']: continue
        col = (90, 90, 90, 150) if L['type'] == 'uncertain' else ((40, 40, 40, 170) if L['type'] == 'documented' else (120, 60, 60, 150))
        if L['type'] == 'uncertain': dash(poly, 2, 6, col, 2)
        elif L['type'] == 'legendary': dash(poly, 12, 8, col, 2)
        else: dash(poly, 6, 4, col, 2)   # documented but not in P05: thin dashed grey-black
    for k in P05_ORDER:
        L = next(l for l in LEGS if l['id'] == k); poly = legs_out[k]
        if L['type'] == 'documented': da.line(poly, fill=(25, 18, 12, 255), width=5, joint='curve')
        else: dash(poly, 18, 11, (95, 70, 55, 190), 4)
    small = ImageFont.truetype(DJVB, 17)
    for c, p in PL.items():
        u, v = place_px(c)
        if not (-20 < u < W + 20 and -20 < v < H + 20): continue
        if c == 'P18':
            da.ellipse([u - 6, v - 6, u + 6, v + 6], outline=(150, 0, 0, 255), width=2)
        elif c in ('P7', 'P9', 'P10', 'P14', 'P15'):
            da.ellipse([u - 7, v - 7, u + 7, v + 7], fill=(25, 18, 12, 255), outline=(250, 245, 230, 255), width=2)
        elif c == 'P17':
            da.rectangle([u - 7, v - 7, u + 7, v + 7], outline=(25, 18, 12, 255), width=3)   # end-mark position
        elif c == 'P19':
            da.ellipse([u - 6, v - 6, u + 6, v + 6], fill=(240, 232, 210, 255), outline=(120, 100, 80, 255), width=2)
        else:
            da.ellipse([u - 4, v - 4, u + 4, v + 4], fill=(110, 110, 110, 255))
        da.text((u + 8, v - 22), c, font=small, fill=(150, 0, 0, 255) if c == 'P18' else (20, 20, 120, 255),
                stroke_width=2, stroke_fill=(255, 255, 255, 220))
    zones_layer(ann)
    lg = ImageFont.truetype(DJV, 21)
    lines = ['P05 refpack (reference only - NOT the plate)', 'solid black = documented P05 legs S4 S5 S7 S9',
             'broken brown = legendary P05-LEG (stops short of Rome)', 'thin dashes = other data legs (not drawn in P05)',
             'square = end-mark (AB 860 raid, at Pisa, unlabelled)', 'red ring = P18 site: NO mark/label on screen',
             'hatch = land with no c.860 realm in data', 'green title-safe  orange pin-safe  grey 1.06 push crop',
             'magenta = caption third (below y=%d pre-push)' % round(CAPTION_Y_SRC), 'blue = label zones (+10)  red = compass zone']
    y = 1440
    da.rectangle([70, y - 12, 700, y + 26 * len(lines) + 6], fill=(255, 255, 255, 200))
    for t in lines: da.text((82, y), t, font=lg, fill=(20, 20, 20, 255)); y += 26
    annq = ann.convert('RGB').quantize(256, method=Image.Quantize.MEDIANCUT)
    p_ann = outpath('img/bjorn_p05_9x16_ref_annotated.png'); annq.save(p_ann, optimize=True)

    # realm ids (index image for engine QA / tint; 0 = no realm in data)
    p_rid = outpath('img/bjorn_p05_9x16_realm_ids.png'); Image.fromarray(rid_out.astype(np.uint8)).save(p_rid, optimize=True)

    # contact
    cs = Image.new('RGB', (1080 + 12, 960 + 40), (250, 250, 250))
    cs.paste(clean.resize((540, 960), Image.LANCZOS), (0, 40)); cs.paste(ann.convert('RGB').resize((540, 960), Image.LANCZOS), (552, 40))
    dc = ImageDraw.Draw(cs); f = ImageFont.truetype(DJVB, 20)
    dc.text((10, 9), 'ref_clean (plate guide)', font=f, fill=(0, 0, 0)); dc.text((562, 9), 'ref_annotated (route, places, zones)', font=f, fill=(0, 0, 0))
    p_cs = outpath('img/bjorn_p05_contact.png'); cs.quantize(256, method=Image.Quantize.MEDIANCUT).save(p_cs, optimize=True)

    # ---------------- JSON ----------------
    def realm_at(u, v, c):
        pt = Point(PL[c][4], PL[c][3])
        inside = [REALM_STYLE[k][0] for k in order if RP[k]['geom'].contains(pt)]
        if inside: return inside[-1] + (' (also inside ' + ', '.join(inside[:-1]) + ')' if len(inside) > 1 else '')
        near = [(RP[k]['geom'].distance(pt) * 111, REALM_STYLE[k][0]) for k in order if RP[k]['geom'].distance(pt) * 111 < 5]
        return f'none (within {min(near)[0]:.1f} km of {min(near)[1]} polygon edge)' if near else None
    corners = {n: [round(float(a), 4) for a in unpx(u, v)] for n, (u, v) in dict(TL=(0, 0), TR=(W, 0), BL=(0, H), BR=(W, H), C=(W / 2, H / 2)).items()}
    places = []
    for c, p in PL.items():
        u, v = place_px(c)
        inf = 0 <= u < W and 0 <= v < H
        places.append(dict(code=c, key=p[1], name=p[2], lat=p[3], lon=p[4], wikidata=p[5], data_status=p[6], p05_role=p[7],
                           out_px=[round(u, 1), round(v, 1)], plate_px=[round(u * S, 1), round(v * S, 1)], in_frame=inf,
                           in_push_title_safe=bool(PUSH_TITLE_SAFE[0] <= u <= PUSH_TITLE_SAFE[2] and PUSH_TITLE_SAFE[1] <= v <= PUSH_TITLE_SAFE[3]),
                           above_caption_line=bool(v <= CAPTION_Y_SRC), realm_under_point_ohm=realm_at(u, v, c),
                           label=('ALLOWED' if c in allow else ('NEVER' if c == 'P18' else 'not allowed in P05')),
                           label_zone_bbox=boxes.get(c)))
    legs = []
    for L in LEGS:
        poly = legs_out[L['id']]
        legs.append(dict(id=L['id'], chain=L['chain'], leg_type=L['type'], style=L['style'], year=L['year'], p05_draw=L['p05'],
                         p05_order=(P05_ORDER.index(L['id']) + 1) if L['id'] in P05_ORDER else None, source=L['src'],
                         polyline_out_px=[[round(a, 1), round(b, 1)] for a, b in poly], qa=qa[L['id']]))
    realms = []
    for i, k in enumerate(keys, 1):
        if k not in RP: continue
        share = float((rid_out == i).sum()) / float(land_out.sum())
        t = RP[k]['tags']
        realms.append(dict(index=i, ohm_relation=k, name=REALM_STYLE[k][0], ohm_name=t.get('name:en') or t.get('name'), start=t.get('start_date'), end=t.get('end_date'),
                           pigment=REALM_STYLE[k][1], ref_rgb=REALM_STYLE[k][2], land_share_in_frame=round(share, 4), balearic_parts_dropped=RP[k]['dropped']))
    J = dict(frame=dict(id='bjorn_p05_9x16', proj4=PROJ4, out_size=[W, H], plate_size=[W * S, H * S], km_per_out_px=round(MPP / 1000, 5), width_km=WKM, height_km=round(WKM * H / W, 2),
                        projected_bounds_m=dict(x=[-W / 2 * MPP, W / 2 * MPP], y=[-H / 2 * MPP, H / 2 * MPP]), corners_lonlat=corners,
                        px_formula='x_px=X/m_per_px+540, y_px=960-Y/m_per_px (LAEA X,Y in metres); plate px = 2 x out px', push=PUSH,
                        push_crop_src_px=PUSH_CROP, title_safe=TITLE_SAFE, pin_safe=PIN_SAFE, push_title_safe_src_px=[round(v, 1) for v in PUSH_TITLE_SAFE],
                        caption_line_out_px=CAPTION_Y_OUT, caption_line_src_px=round(CAPTION_Y_SRC, 1)),
             zones=dict(label_zones_bbox_nopad={PL[c][2]: bb for c, bb in boxes.items()}, label_pad_px=10, compass_ornament_reserved=compass, medallion=None),
             places=places, legs=legs, p05_draw_order=P05_ORDER, end_mark=dict(code='P17', out_px=places[16]['out_px'], meaning='AB 860 Italian raid ("Pisas civitatem aliasque"), unlabelled per storyboard v3'),
             label_allow_list=[PL[c][2] for c in allow], realms=realms, log=log)
    p_j = outpath('route_places_p05.json'); json.dump(J, open(p_j, 'w'), ensure_ascii=False, indent=1)
    for p in (p_clean, p_ann, p_z, p_rid, p_cs, p_j):
        print(hashlib.md5(open(p, 'rb').read()).hexdigest(), os.path.getsize(p), os.path.relpath(p, HERE))
    print('\n'.join(log)); print(json.dumps(qa, indent=0)); print('boxes', boxes)

if __name__ == '__main__':
    main()
