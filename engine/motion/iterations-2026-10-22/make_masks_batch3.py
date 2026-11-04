"""Masks for batch-3 plates (thresholds + polygons; no AI).  Writes into batch3/masks/ (new folder, own files only)."""
import os, numpy as np, cv2
ROOT = "/workspace/posterity"; OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "batch3", "masks")
def load(p): return cv2.cvtColor(cv2.imread(os.path.join(ROOT, p)), cv2.COLOR_BGR2RGB)
def poly(shape, polys):
    m = np.zeros(shape[:2], np.uint8)
    for p in polys: cv2.fillPoly(m, [np.int32(p)], 255)
    return m
def save(name, m):
    p = os.path.join(OUT, name)
    if os.path.exists(p): print("exists, not rewritten:", p); return      # never overwrite
    cv2.imwrite(p, np.clip(m, 0, 255).astype(np.uint8)); print("wrote", p, "coverage %.1f%%" % (100 * (m > 127).mean()))

def croatoan_outro_ch1():
    im = load("serials/croatoan/ch1/plates/outro_OWNER.png"); H, W = im.shape[:2]
    Y, X = np.mgrid[0:H, 0:W]
    lum = im.mean(2)
    # water = everything below the shoreline band; the shoreline/pier/huts row (y < ~818) is excluded with a margin
    water = (Y > 822).astype(np.uint8) * 255
    # left of the island the open water starts higher (horizon ~ y 745): include it, but not the pier posts (x 60-180, y 760-800)
    left = poly(im.shape, [[[0, 752], [60, 752], [60, 822], [0, 822]]])
    water = np.maximum(water, left)
    # brand title + tagline baked into the plate: never touched
    text = poly(im.shape, [[[100, 1130], [840, 1130], [840, 1360], [100, 1360]]])
    text = cv2.GaussianBlur(text.astype(np.float32), (0, 0), 6); water = water.astype(np.float32) * (1 - text / 255.0)
    water = cv2.GaussianBlur(water, (0, 0), 1.5) * (water > 0)
    save("outro_ch1_water.png", water); save("outro_ch1_protect_all.png", np.full((H, W), 255, np.uint8))
    save("outro_ch1_textbox.png", text)

def ugarit_p07():
    H, W = 1672, 941; save("p07_protect_all.png", np.full((H, W), 255, np.uint8))

def candle_seq14_v2():
    """Flame-warp zone (flame mask dilated 6 px) and its complement: the protect mask (face, hands, paper, room: 0 px)."""
    fm = cv2.imread(os.path.join(os.path.dirname(OUT), "..", "batch2", "masks", "seq14_flame.png"), 0)
    zone = cv2.dilate((fm > 2).astype(np.uint8) * 255, np.ones((13, 13), np.uint8))
    save("seq14_flamezone_v2.png", zone); save("seq14_protect_nonflame_v2.png", 255 - zone)
    # v2b: same threshold as the engine's flame-warp zone (any non-zero flame pixel), so protect never overlaps the zone
    zone_b = cv2.dilate((fm > 0).astype(np.uint8) * 255, np.ones((13, 13), np.uint8))
    save("seq14_flamezone_v2b.png", zone_b); save("seq14_protect_nonflame_v2b.png", 255 - zone_b)

if __name__ == "__main__":
    import sys
    os.makedirs(OUT, exist_ok=True)
    which = sys.argv[1:] or ["glint", "candle"]
    if "glint" in which: croatoan_outro_ch1(); ugarit_p07()
    if "candle" in which: candle_seq14_v2()
