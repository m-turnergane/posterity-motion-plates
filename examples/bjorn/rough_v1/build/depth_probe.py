"""Scratch probe: depth maps (cached in rough_v1/scratch/cache/depth) + threshold overlays for picking depth_min. Writes scratch only."""
import sys, importlib.util, numpy as np, cv2
from pathlib import Path
R = Path(__file__).resolve().parents[1]; PL = R.parent / "plates"; ENG = Path("/workspace/posterity/engine-rnd")
def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); sys.modules[n] = m; s.loader.exec_module(m); return m
DP = _load("depth_v1", ENG / "depth/depth_v1.py"); DP.CACHE = R / "scratch/cache/depth"
SN = _load("snow_v1b", ENG / "snow/snow_v1b.py")
for n in sys.argv[1:]:
    p = PL / f"{n}_KEEP.png"; P = DP.load_rgb(p); D, _ = DP.depth_map(p, P); H, W = D.shape
    f = SN.detect_faces(P, 0.6); print(n, "faces", [[int(v) for v in b[:4]] for b in f])
    s = 560 / H; rs = lambda x: cv2.resize(x, (int(W * s), 560), interpolation=cv2.INTER_AREA)
    tiles = [rs(P), cv2.cvtColor(cv2.applyColorMap(rs((D * 255).astype(np.uint8)), cv2.COLORMAP_TURBO), cv2.COLOR_BGR2RGB)]
    for th in (0.45, 0.55, 0.65, 0.75):
        o = P.astype(np.float32) * 0.5; m = D >= th; o[m] = o[m] * 0.4 + np.float32([255, 60, 60]) * 0.6
        for x, y, w, h, _ in f: cv2.rectangle(o, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 0), 3)
        t = rs(o.astype(np.uint8)); cv2.putText(t, str(th), (8, 30), 0, 1, (255, 255, 0), 2); tiles.append(t)
    cv2.imwrite(str(R / f"scratch/probe/{n}_depth.jpg"), cv2.cvtColor(np.hstack(tiles), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 75])
