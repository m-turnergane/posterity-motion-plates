"""Phone-size legibility stills (batch 3): downscale a QC still (e.g. *_after_mid.png) to 360x640 (INTER_AREA). New file only.
Usage: qc_phone.py in.png [in2.png ...]  -> writes <name>_phone360.png next to each input"""
import sys, os, cv2
for p in sys.argv[1:]:
    o = p[:-4] + "_phone360.png"
    if os.path.exists(o): print("exists, not rewritten:", o); continue
    cv2.imwrite(o, cv2.resize(cv2.imread(p), (360, 640), interpolation=cv2.INTER_AREA)); print("wrote", o)
