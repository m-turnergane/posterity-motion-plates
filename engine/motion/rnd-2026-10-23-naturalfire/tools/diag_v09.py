"""Zoom diagnostics for a v09 iteration: c0 extension, c1 top (guard edges), c0 base, at the 6 most ext-active frames."""
import sys, numpy as np, cv2
sys.path.insert(0, 'tools'); from flame_v09 import load_masks_v09
tag = sys.argv[1]; c, e = load_masks_v09()
S = np.load('iter/v09_static/crop_frames.npy'); F = np.load(f'iter/{tag}/crop_frames.npy')
def act(E): return sorted(np.argsort(np.abs(F.astype(np.float32) - S).mean(3)[:, E].mean(1))[-6:])
E0 = e[0][540:962, 366:574] > 0.3; fr = act(E0)
z = lambda im: cv2.resize(im[6:130, 20:75], None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST)
cv2.imwrite(f'iter/{tag}/diag_ext0.png', cv2.cvtColor(np.hstack([z(S[fr[0]])] + [z(F[i]) for i in fr]), cv2.COLOR_RGB2BGR))
E1 = e[1][540:962, 366:574] > 0.3; fr = act(E1)
z = lambda im: cv2.resize(im[205:275, 28:132], None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
cv2.imwrite(f'iter/{tag}/diag_c1top.png', cv2.cvtColor(np.vstack([z(S[fr[0]])] + [z(F[i]) for i in fr[:4]]), cv2.COLOR_RGB2BGR))
print("ok")
