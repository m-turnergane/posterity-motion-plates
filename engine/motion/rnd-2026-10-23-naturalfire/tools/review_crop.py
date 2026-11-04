import sys, subprocess, numpy as np, cv2
sys.path.insert(0, 'tools'); import prod as P
src, x0, y0, x1, y1, sc, f0, n, cols, out = sys.argv[1], *map(int, sys.argv[2:10]), sys.argv[10]
r = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"], capture_output=True, check=True).stdout
A = np.frombuffer(r, np.uint8).reshape(-1, P.H, P.W, 3)
t = []
for i in range(f0, f0 + n):
    im = cv2.resize(A[i][y0:y1, x0:x1], None, fx=sc, fy=sc, interpolation=cv2.INTER_NEAREST).copy()
    cv2.putText(im, f"f{i}", (3, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1); t.append(im)
rows = [np.hstack(t[k:k + cols]) for k in range(0, len(t), cols)]
cv2.imwrite(out, cv2.cvtColor(np.vstack(rows), cv2.COLOR_RGB2BGR))
