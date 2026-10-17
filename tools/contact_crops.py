"""Labelled crop contact sheet from stills_raw PNGs: contact_crops.py <stills_dir> <name> x0 y0 x1 y1 scale out.png t1 t2 ... [--cols N]"""
import sys, cv2, numpy as np, glob, os
def main():
    a = sys.argv[1:]; d, name = a[0], a[1]; x0, y0, x1, y1 = map(int, a[2:6]); sc = float(a[6]); out = a[7]; rest = a[8:]; cols = 4
    if "--cols" in rest: i = rest.index("--cols"); cols = int(rest[i + 1]); rest = rest[:i] + rest[i + 2:]
    tiles = []
    for t in rest:
        p = os.path.join(d, f"{name}_t{float(t):.2f}.png"); im = cv2.imread(p)[y0:y1, x0:x1]
        im = cv2.resize(im, None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC if sc > 1 else cv2.INTER_AREA).copy()
        cv2.rectangle(im, (0, 0), (im.shape[1], 22), (0, 0, 0), -1); cv2.putText(im, f"t={float(t):.2f}s", (6, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA); tiles.append(im)
    while len(tiles) % cols: tiles.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]; cv2.imwrite(out, np.vstack(rows))
main()
