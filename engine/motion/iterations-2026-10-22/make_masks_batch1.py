"""Hand-built masks for batch-1 plates (colour/luminance thresholds + polygons, no AI).
Writes 8-bit soft masks (0..255, plate resolution 941x1672) into batch1/masks/. Never overwrites an existing file."""
import os, sys, numpy as np, cv2
ROOT = "/workspace/posterity"; OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "batch1", "masks")

def load(p):
    return cv2.cvtColor(cv2.imread(os.path.join(ROOT, p)), cv2.COLOR_BGR2RGB)

def poly(shape, polys):
    m = np.zeros(shape[:2], np.uint8)
    for p in polys: cv2.fillPoly(m, [np.int32(p)], 255)
    return m

def save(name, m):
    p = os.path.join(OUT, name)
    # only files this script itself created live here (batch1/masks is new today); regenerating them is allowed
    cv2.imwrite(p, np.clip(m, 0, 255).astype(np.uint8)); print("wrote", p, "coverage %.1f%%" % (100 * (m > 127).mean()))

def clean(m, open_k=3, close_k=5):
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((open_k, open_k), np.uint8))
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((close_k, close_k), np.uint8))

def map_seq09a():
    im = load("serials/croatoan/ch2/plates/seq09a_map_roanoke_croatoan_UNLABELED_OWNER.png")
    hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV); h, s, v = [hsv[..., i].astype(int) for i in range(3)]
    sea = ((h >= 55) & (h <= 130) & (s >= 18) & (v >= 70)).astype(np.uint8) * 255
    sea = clean(sea, 3, 7)
    # keep only big connected sea bodies (drop specks inside land)
    n, lab, st, _ = cv2.connectedComponentsWithStats(sea); keep = np.zeros_like(sea)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] > 4000: keep[lab == i] = 255
    sea = keep
    ship = poly(sea.shape, [[[812, 1015], [905, 1015], [905, 1115], [812, 1115]]])
    sea[ship > 0] = 0
    land = 255 - sea                                  # land + ink coastline + ship = protect (geometry must stay static)
    coast = cv2.dilate(land, np.ones((7, 7), np.uint8))
    save("seq09a_sea.png", sea); save("seq09a_protect_land_coast.png", coast)
    save("seq09a_full.png", np.full(sea.shape, 255, np.uint8))

def env_p07():
    im = load("micro-anomaly/ugarit/plates/p07_abandoned_match02_OWNER.png")
    hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV); h, s, v = [hsv[..., i].astype(int) for i in range(3)]
    Y = np.mgrid[0:im.shape[0], 0:im.shape[1]][0]
    sky = (Y < 215) & (((h >= 95) & (h <= 125) & (s > 40)) | ((s < 60) & (v > 200)))
    sky = clean(sky.astype(np.uint8) * 255, 3, 9)
    # sky = connected to the top row only
    n, lab, st, _ = cv2.connectedComponentsWithStats(sky); keep = np.zeros_like(sky)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_TOP] < 5: keep[lab == i] = 255
    sky = keep
    sea = (Y > 180) & (Y < 520) & (h >= 80) & (h <= 125) & (s > 50) & (v > 90)
    sea = clean(sea.astype(np.uint8) * 255, 3, 7)
    n, lab, st, _ = cv2.connectedComponentsWithStats(sea); keep = np.zeros_like(sea)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] > 3000: keep[lab == i] = 255
    sea = keep; sea[sky > 0] = 0
    fol = (Y > 230) & (h >= 22) & (h <= 75) & (s > 70) & (v > 40) & (v < 235)
    fol = clean(fol.astype(np.uint8) * 255, 3, 5)
    fol[(sea > 0) | (sky > 0)] = 0
    n, lab, st, _ = cv2.connectedComponentsWithStats(fol); keep = np.zeros_like(fol)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] > 150: keep[lab == i] = 255
    fol = keep
    land = 255 - np.maximum(sky, sea)
    stone = land.copy(); stone[fol > 0] = 0            # walls/ground/paths: protect from displacement
    save("p07_sky.png", sky); save("p07_sea.png", sea); save("p07_foliage.png", fol)
    save("p07_land.png", land); save("p07_protect_stone.png", stone)

def light_p06():
    im = load("micro-anomaly/ugarit/plates/p06_burnt_city_doorway_OWNER.png")
    lum = im.mean(2)
    opening = poly(lum.shape, [[[152, 162], [826, 168], [826, 600], [812, 1590], [150, 1600], [148, 600]]])
    # the burnt door frame is dark: trim the opening where the frame intrudes (very dark + near edges)
    sky = opening.copy(); Y = np.mgrid[0:lum.shape[0], 0:lum.shape[1]][0]
    sky[(Y > 600)] = 0
    sky[(lum < 90)] = 0; sky = clean(sky, 3, 9)
    scene = opening.copy()
    char = ((lum < 48) & (opening > 0) & (Y > 820)).astype(np.uint8) * 255
    char = clean(char, 3, 3)
    save("p06_opening.png", opening); save("p06_sky.png", sky); save("p06_char.png", char)
    save("p06_full.png", np.full(lum.shape, 255, np.uint8))
    save("p06_protect_frame.png", 255 - opening)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); map_seq09a(); env_p07(); light_p06()
