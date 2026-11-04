import sys, numpy as np, cv2
F = np.load(sys.argv[1], mmap_mode='r'); idx = [int(a) for a in sys.argv[2].split(',')]; x0, y0, x1, y1 = [int(a) for a in sys.argv[3].split(',')]; sc = int(sys.argv[4]); out = sys.argv[5]
CX0, CY0 = 368, 672
ims = [cv2.resize(np.ascontiguousarray(F[i][y0 - CY0:y1 - CY0, x0 - CX0:x1 - CX0]), None, fx=sc, fy=sc, interpolation=cv2.INTER_LANCZOS4) for i in idx]
ims = [np.pad(im, ((0, 0), (0, 4), (0, 0))) for im in ims]
cv2.imwrite(out, cv2.cvtColor(np.concatenate(ims, 1), cv2.COLOR_RGB2BGR))
