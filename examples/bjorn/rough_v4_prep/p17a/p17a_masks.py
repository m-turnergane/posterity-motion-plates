#!/workspace/mpvenv/bin/python
"""P17A masks (plate px, plate 941x1672). Writes masks/*.png + masks/p17a_masks.json (water as polygons = outer contours, protect = holes).
Plate read-only (md5 fa286390... asserted)."""
import json, hashlib, numpy as np, cv2
from pathlib import Path
HERE = Path(__file__).resolve().parent; BJ = HERE.parents[1]; PL = BJ / 'plates/P17A_unnamed_captain.png'
assert hashlib.md5(PL.read_bytes()).hexdigest() == 'fa2863906d7648c30406adc27d738670'
P = cv2.cvtColor(cv2.imread(str(PL)), cv2.COLOR_BGR2RGB); H, W = P.shape[:2]; M = HERE / 'masks'; M.mkdir(exist_ok=True)
def poly(pts): m = np.zeros((H, W), np.uint8); cv2.fillPoly(m, [np.int32(pts)], 1); return m > 0
def line(a, b, w): m = np.zeros((H, W), np.uint8); cv2.line(m, a, b, 1, w); return m > 0
f = P.astype(np.float32); r, g, b = f[..., 0], f[..., 1], f[..., 2]; L = 0.299 * r + 0.587 * g + 0.114 * b
# sunlit water region (right of the hull + below the hull line), geometric
WATER0 = poly([[560, 690], [941, 690], [941, 1672], [0, 1672], [0, 1440], [220, 1420], [320, 1330], [720, 1145], [770, 1060], [700, 880], [640, 800], [600, 720]])
# guards
CAPTAIN = poly([[200, 300], [480, 300], [480, 660], [200, 660]])                           # hooded captain + steering hand (face must stay hidden)
STEER = line((470, 585), (232, 1425), 64)                                                  # steering oar (shaft + blade)
wood = ((r - b) > 28) & (L < 168) & ~((r > 200) & (g > 150))                               # brown wood, not sun-gold glare
wood = cv2.morphologyEx(wood.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
OARZONE = poly([[600, 840], [941, 900], [941, 1260], [600, 1180]])
OARS = np.zeros((H, W), bool)   # v2 of the mask: colour 'wood' test dropped (sun-gold water read as wood); oars traced by hand from a 2x grid crop, 24 px wide
for a, bb in [((700, 873), (915, 956)), ((675, 898), (912, 987)), ((662, 947), (912, 1025)), ((618, 982), (938, 1097)), ((600, 1000), (932, 1187))]:
    OARS |= line(a, bb, 24)
HULL = poly([[0, 300], [560, 640], [720, 880], [770, 1060], [720, 1145], [320, 1330], [220, 1420], [0, 1440]])
GUARD = CAPTAIN | STEER | OARS | HULL
WATER = WATER0 & ~GUARD
# new-motion masks (proof only, awaiting approval)
SAIL0 = poly([[0, 0], [795, 0], [640, 290], [520, 400], [300, 450], [210, 300], [0, 250]])   # stops above the carved prow
mast = line((205, 0), (205, 700), 46)
ropes = np.zeros((H, W), bool)
for a, bb in [((150, 0), (60, 330)), ((330, 0), (430, 560)), ((560, 300), (640, 0)), ((600, 0), (480, 640)), ((700, 0), (560, 470))]:
    ropes |= line(a, bb, 14)                                                               # main rigging lines crossing the sail (hand-traced, approx.)
sky = (b > r * 0.9) & (L > 110)                                                            # pale sky between sail and ropes
PROW = poly([[0, 235], [235, 235], [235, 1440], [0, 1440]])                          # carved prow/stem post
SAIL = SAIL0 & ~mast & ~ropes & ~sky & ~CAPTAIN & ~PROW
FLEET = poly([[690, 515], [941, 515], [941, 700], [690, 700]])
NOWARP = CAPTAIN | STEER | OARS | mast | ropes | PROW | HULL
for n, m in dict(water=WATER, guard=GUARD, captain=CAPTAIN, oars=OARS | STEER, hull=HULL, sail=SAIL, fleet=FLEET, nowarp=NOWARP).items():
    cv2.imwrite(str(M / f'p17a_mask_{n}.png'), m.astype(np.uint8) * 255)
ov = P.copy().astype(np.float32)
for m, c in ((WATER, (40, 160, 255)), (GUARD, (255, 40, 40)), (SAIL, (40, 255, 80)), (FLEET, (255, 230, 0))): ov[m] = ov[m] * 0.55 + np.float32(c) * 0.45
cv2.imwrite(str(M / 'p17a_mask_overlay.png'), cv2.cvtColor(ov.astype(np.uint8), cv2.COLOR_RGB2BGR))
cs, hier = cv2.findContours(WATER.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE); outer, holes = [], []
for c, h in zip(cs, hier[0]):
    pts = c[:, 0, :].tolist()
    if len(pts) < 3: continue
    (holes if h[3] >= 0 else outer).append(pts)
# round-trip check: polygons reproduce the mask
rt = np.zeros((H, W), np.uint8); cv2.fillPoly(rt, [np.int32(p) for p in outer], 1); hm = np.zeros((H, W), np.uint8)
if holes: cv2.fillPoly(hm, [np.int32(p) for p in holes], 1)
rt = (rt > 0) & ~(hm > 0); diff = int((rt ^ WATER).sum())
json.dump(dict(plate=str(PL), water=outer, protect=holes, roundtrip_diff_px=diff, water_px=int(WATER.sum()), guard_px=int(GUARD.sum()), sail_px=int(SAIL.sum())), open(M / 'p17a_masks.json', 'w'))
print('water px', int(WATER.sum()), 'outer', len(outer), 'holes', len(holes), 'roundtrip diff', diff, 'sail', int(SAIL.sum()))
