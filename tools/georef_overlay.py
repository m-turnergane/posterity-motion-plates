"""Overlay Natural Earth (public domain) coastlines/lakes/rivers on the painted map through a Georef, for control-point picking and deviation review.
usage: georef_overlay.py GEOREF.json MAP.png OUT.png [--geodata DIR] [--crop x0,y0,x1,y1] [--scale S] [--grid]
Needs the optional extra: pip install -e .[geo]  (pyshp). Natural Earth 50m (public domain) shapefiles from https://www.naturalearthdata.com/ unzipped under $MOTIONPLATES_GEODATA (default /workspace/geodata): ne_50m_coastline, ne_50m_lakes, ne_50m_rivers_lake_centerlines"""
import sys, os, json, argparse, numpy as np, cv2
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from motionplates.cartography import georef as G

def lines(geodata, name, bbox):
    import shapefile
    sf = shapefile.Reader(os.path.join(geodata, f"ne_50m_{name}", f"ne_50m_{name}.shp")); out = []
    for s in sf.shapes():
        parts = list(s.parts) + [len(s.points)]
        for a, b in zip(parts[:-1], parts[1:]):
            pts = np.array(s.points[a:b])
            if len(pts) > 1 and pts[:, 0].max() > bbox[0] and pts[:, 0].min() < bbox[2] and pts[:, 1].max() > bbox[1] and pts[:, 1].min() < bbox[3]: out.append(pts)
    return out

def draw(img, g, geodata, scale=1.0, crop=None, grid=True):
    bbox = (0, 0, 120, 70); H, W = img.shape[:2]
    for name, col, th in (("coastline", (0, 255, 255), 1), ("lakes", (255, 255, 0), 1), ("rivers_lake_centerlines", (255, 128, 255), 1)):
        for pts in lines(geodata, name, bbox):
            px = g.to_px(pts) * scale
            cv2.polylines(img, [np.round(px * 8).astype(np.int32).reshape(-1, 1, 2)], False, col, th, cv2.LINE_AA, 3)
    if grid:
        for lon in range(10, 110, 10):
            pts = g.to_px(np.stack([np.full(60, lon), np.linspace(5, 65, 60)], 1)) * scale; cv2.polylines(img, [np.round(pts).astype(np.int32).reshape(-1, 1, 2)], False, (200, 200, 200), 1, cv2.LINE_AA)
            p = g.to_px([lon, 22]) * scale; cv2.putText(img, f"{lon}E", (int(p[0]) - 12, int(p[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
        for lat in range(10, 70, 10):
            pts = g.to_px(np.stack([np.linspace(0, 120, 60), np.full(60, lat)], 1)) * scale; cv2.polylines(img, [np.round(pts).astype(np.int32).reshape(-1, 1, 2)], False, (200, 200, 200), 1, cv2.LINE_AA)
            p = g.to_px([22, lat]) * scale; cv2.putText(img, f"{lat}N", (int(p[0]), int(p[1]) - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
    for c in (g.cp or []):
        p = np.array(c["px"]) * scale; q = g.to_px([c["lon"], c["lat"]]) * scale
        cv2.circle(img, tuple(np.round(p).astype(int)), 5, (0, 0, 255), 1, cv2.LINE_AA); cv2.circle(img, tuple(np.round(q).astype(int)), 3, (0, 255, 0), -1, cv2.LINE_AA)
        cv2.line(img, tuple(np.round(p).astype(int)), tuple(np.round(q).astype(int)), (0, 0, 255), 1, cv2.LINE_AA)
    return img

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("georef"); ap.add_argument("map"); ap.add_argument("out"); ap.add_argument("--geodata", default=os.environ.get("MOTIONPLATES_GEODATA", "/workspace/geodata"))
    ap.add_argument("--crop"); ap.add_argument("--scale", type=float, default=1.0); ap.add_argument("--no-grid", action="store_true"); a = ap.parse_args()
    d = json.load(open(a.georef)); g = G.load(d); img = cv2.imread(a.map); img = cv2.resize(img, None, fx=a.scale, fy=a.scale, interpolation=cv2.INTER_CUBIC); draw(img, g, a.geodata, a.scale, grid=not a.no_grid)
    if a.crop: x0, y0, x1, y1 = [int(float(v) * a.scale) for v in a.crop.split(",")]; img = img[y0:y1, x0:x1]
    cv2.imwrite(a.out, img)
