"""Masks for batch-2 plates (thresholds + polygons; no AI).  Writes into batch2/masks/ (new folder, own files only)."""
import os, numpy as np, cv2
ROOT = "/workspace/posterity"; OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "batch2", "masks")
def load(p): return cv2.cvtColor(cv2.imread(os.path.join(ROOT, p)), cv2.COLOR_BGR2RGB)
def poly(shape, polys):
    m = np.zeros(shape[:2], np.uint8)
    for p in polys: cv2.fillPoly(m, [np.int32(p)], 255)
    return m
def save(name, m):
    p = os.path.join(OUT, name); cv2.imwrite(p, np.clip(m, 0, 255).astype(np.uint8)); print("wrote", p, "coverage %.1f%%" % (100 * (m > 127).mean()))

def candle_seq14():
    im = load("serials/croatoan/ch2/plates/seq14_white_ireland_letter_candle_OWNER.png"); H, W = im.shape[:2]
    hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV); h, s, v = [hsv[..., i].astype(int) for i in range(3)]
    # window (night exterior + panes): excluded from the relight so the rain/night outside never flickers
    win_region = poly(im.shape, [[[712, 20], [941, 20], [941, 800], [712, 800]]])
    win = ((win_region > 0) & (h >= 90) & (h <= 135)).astype(np.uint8) * 255
    win = cv2.morphologyEx(win, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)); win = cv2.dilate(win, np.ones((5, 5), np.uint8))
    relight = 255 - win
    relight = cv2.GaussianBlur(relight.astype(np.float32), (0, 0), 3)
    # painted candle flame: bright warm core inside a tight polygon around the flame
    fpoly = poly(im.shape, [[[50, 962], [68, 962], [70, 1004], [48, 1004]]])
    flame = ((fpoly > 0) & (v >= 200)).astype(np.uint8) * 255
    flame = cv2.GaussianBlur(flame.astype(np.float32), (0, 0), 0.8)
    save("seq14_relight.png", relight); save("seq14_flame.png", flame)
    save("seq14_window.png", win); save("seq14_full.png", np.full((H, W), 255, np.uint8))

def light_p06_v2():
    im = load("micro-anomaly/ugarit/plates/p06_burnt_city_doorway_OWNER.png"); H, W = im.shape[:2]
    sky1 = cv2.imread(os.path.join(os.path.dirname(OUT), "..", "batch1", "masks", "p06_sky.png"), 0)
    # strict sky for heat shimmer: batch-1 sky minus every skyline silhouette (tall ruins, spires) and anything below y=586
    excl = poly(im.shape, [[[240, 555], [352, 555], [352, 640], [240, 640]], [[355, 575], [390, 575], [390, 640], [355, 640]],
                           [[605, 545], [668, 545], [668, 640], [605, 640]], [[148, 586], [830, 586], [830, 700], [148, 700]]])
    lum = im.mean(2); strict = ((sky1 > 127) & (excl == 0) & (lum > 105)).astype(np.uint8) * 255
    strict = cv2.morphologyEx(strict, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    save("p06_sky_strict_v2.png", strict)
    save("p06_protect_nonsky_v2.png", 255 - strict)       # every non-sky pixel (stone, walls, rubble, frame): displacement must be 0

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); candle_seq14(); light_p06_v2()
