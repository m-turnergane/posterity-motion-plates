"""v09: R&D protect (masks_v09/P05_rnd_protect.png) | face_hand_polys. Decoded-lossless check on the camera-mapped protected set (P05_protect | face_hand_polys): POC vs v2c static."""
import sys, json, subprocess, numpy as np, cv2
sys.path.insert(0, 'tools'); import prod as P
def dec(p):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"], capture_output=True, check=True).stdout
    return np.frombuffer(r, np.uint8).reshape(-1, P.H, P.W, 3)
A, S = dec("work/final_v09_poc_lossless.mp4"), dec("work/final_v09_v2cstatic_lossless.mp4")
pr = cv2.imread("masks_v09/P05_rnd_protect.png", 0) > 0   # v09: R&D protected set
cand = json.load(open(P.MASKS / "P05_candles.json"))
fh = np.zeros(pr.shape, np.uint8); cv2.fillPoly(fh, [np.array(p, np.int32) for p in cand["face_hand_polys"]], 1); prot = (pr | (fh > 0)).astype(np.float32)
box = P.plate_box(); seg = dict(P.SEG_POC); seg["frames"] = 180; img = np.repeat(prot[..., None] * 255, 3, 2)
mx, n, area = 0, 0, 0
for fi in range(len(A)):
    om = np.asarray(P.frame_out(img, box, seg, fi))[..., 0] > 127; area += int(om.sum())
    d = np.abs(A[fi].astype(int) - S[fi]).max(-1)[om]; mx = max(mx, int(d.max())); n += int((d > 0).sum())
r = dict(protected_out_px_per_frame_mean=area // len(A), decoded_lossless_protected_px_changed=n, decoded_lossless_protected_maxabs=mx); print(r)
json.dump(r, open("qc/final_v09_decoded_protected_check.json", "x"))
