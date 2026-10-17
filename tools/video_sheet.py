"""Contact sheet straight from a delivered MP4 (decoded frames, so codec effects are visible): video_sheet.py in.mp4 out.png x0 y0 x1 y1 scale cols t1 t2 ..."""
import sys, subprocess, numpy as np, cv2
def frame_at(mp4, t, W, H):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", mp4, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(H, W, 3)
def main():
    a = sys.argv[1:]; mp4, out = a[0], a[1]; x0, y0, x1, y1 = map(int, a[2:6]); sc = float(a[6]); cols = int(a[7]); ts = [float(t) for t in a[8:]]
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", mp4], capture_output=True, text=True).stdout.strip().split(","); W, H = int(pr[0]), int(pr[1])
    tiles = []
    for t in ts:
        im = frame_at(mp4, t, W, H)[y0:y1, x0:x1]; im = cv2.resize(im, None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC if sc > 1 else cv2.INTER_AREA).copy()
        cv2.rectangle(im, (0, 0), (im.shape[1], 20), (0, 0, 0), -1); cv2.putText(im, f"t={t:.2f}s", (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA); tiles.append(im)
    while len(tiles) % cols: tiles.append(np.zeros_like(tiles[0]))
    cv2.imwrite(out, np.vstack([np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]))
main()
