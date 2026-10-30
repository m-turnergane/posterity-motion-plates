"""Phone-size legibility stills (batch 3): downscale a QC still preserving aspect ratio.
For portrait images (h > w): 360-wide, scaled height.
For landscape images (w >= h): 640-wide, scaled height.
Usage: qc_phone.py in.png [in2.png ...]  -> writes <name>_phone.png next to each input"""
import sys, os, cv2


def phone_size(w, h, target_short=360):
    """Calculate phone QC size preserving aspect ratio.

    For portrait (h > w): target_short-wide, scaled height.
    For landscape (w >= h): 640-wide equivalent, scaled height.
    """
    if h > w:
        gw = target_short
        gh = int(round(target_short * h / w))
    else:
        gw = 640
        gh = int(round(640 * h / w))
    return (gw, gh)


for p in sys.argv[1:]:
    o = p[:-4] + "_phone.png"
    if os.path.exists(o):
        print("exists, not rewritten:", o)
        continue
    img = cv2.imread(p)
    if img is None:
        print("cannot read:", p)
        continue
    h, w = img.shape[:2]
    gw, gh = phone_size(w, h)
    cv2.imwrite(o, cv2.resize(img, (gw, gh), interpolation=cv2.INTER_AREA))
    print(f"wrote {o} ({w}x{h} -> {gw}x{gh})")
