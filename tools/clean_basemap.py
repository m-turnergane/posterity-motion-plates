"""Build the CLEAN base map from the owner's painted map (baked pins/labels removed). The original stays untouched as the fallback.
usage: clean_basemap.py ORIGINAL.png CLEAN_OUT.png [--items items.json] ; default items = the four baked markers of tamerlane_eurasia_painted.png."""
import sys, os, json, hashlib, cv2
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from motionplates.cartography import cleanmap as C
ITEMS = [dict(pin=[82, 591, 11], glow=34, label=[90, 593, 220, 613]),
         dict(pin=[284, 776, 9], glow=30, label=[294, 782, 370, 806]),
         dict(pin=[724, 894, 9], glow=30, label=[734, 888, 796, 918]),
         dict(pin=[583, 672, 14], glow=34, rays=100, label=[600, 654, 740, 692])]
if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]; items = json.load(open(sys.argv[4])) if len(sys.argv) > 4 and sys.argv[3] == "--items" else ITEMS
    img = cv2.imread(src); clean, dbg = C.remove_items(img, items); cv2.imwrite(dst, clean); cv2.imwrite(os.path.splitext(dst)[0] + "_mask.png", dbg)
    print(json.dumps(dict(original_md5=hashlib.md5(open(src, "rb").read()).hexdigest(), clean_md5=hashlib.md5(open(dst, "rb").read()).hexdigest(), before=C.detect_baked(img), after=C.detect_baked(clean))))
