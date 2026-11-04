#!/usr/bin/env python3
"""Single-authority atlas registration (VIDEO-PACK-v2, REGISTRATION-PLAN-v2.1).
ORB + RANSAC HOMOGRAPHY (primary) -> sanity gate -> AFFINE fallback (estimateAffine2D) -> optional MANUAL 4-point.
Writes a JSON transform and a warped plate; never overwrites (refuses if outputs exist).
Usage:
  register_atlas_h.py REF.png PLATE.png OUT_PREFIX [--manual points.json]
  points.json = {"ref":[[x,y]x4], "plate":[[x,y]x4]}  (deterministic fallback)
QA thresholds and NCC/TPS refinement stay as in REGISTRATION-PLAN-v2 sections 3-6 (run make_regplan QA after this).
Validated here only on the refpack synthetic-warp plates; MUST be validated on the real generated map."""
import sys, os, json, numpy as np, cv2
def gate_h(H, w, h):
    if H is None: return False, 'no H'
    Hn = H / H[2, 2]
    persp = float(np.abs(Hn[2, :2]).max() * max(w, h))   # projective strength over the frame
    A = Hn[:2, :2]; s = np.sqrt(abs(np.linalg.det(A)))
    cond = np.linalg.cond(A)
    ok = persp < 0.05 and 0.5 < s < 2.5 and cond < 1.3
    return ok, f'persp={persp:.4f} scale={s:.4f} cond={cond:.4f}'
def main():
    a = sys.argv[1:]
    if len(a) < 3: print(__doc__); sys.exit(2)
    ref_p, pl_p, out = a[:3]; manual = a[a.index('--manual') + 1] if '--manual' in a else None
    for f in (out + '_transform.json', out + '_registered.png'):
        if os.path.exists(f): sys.exit('refuse to overwrite ' + f)
    ref = cv2.imread(ref_p); pl = cv2.imread(pl_p)
    h, w = ref.shape[:2]
    rec = dict(ref=ref_p, plate=pl_p, method=None)
    if manual:
        P = json.load(open(manual)); M = cv2.getPerspectiveTransform(np.float32(P['plate']), np.float32(P['ref']))
        rec.update(method='MANUAL_4PT', H=M.tolist())
    else:
        orb = cv2.ORB_create(6000)
        k1, d1 = orb.detectAndCompute(cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY), None)
        k2, d2 = orb.detectAndCompute(cv2.cvtColor(pl, cv2.COLOR_BGR2GRAY), None)
        m = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(d2, d1)
        src = np.float32([k2[x.queryIdx].pt for x in m]); dst = np.float32([k1[x.trainIdx].pt for x in m])
        H, inl = cv2.findHomography(src, dst, cv2.RANSAC, 6.0)
        ok, why = gate_h(H, w, h); ni = int(inl.sum()) if inl is not None else 0
        rec.update(matches=len(m), h_inliers=ni, h_gate=why)
        if ok and ni >= 40:
            M = H; rec['method'] = 'HOMOGRAPHY'
        else:
            A, ia = cv2.estimateAffine2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=6.0)
            if A is None or ia.sum() < 30: sys.exit('affine failed: use --manual 4-point registration')
            M = np.vstack([A, [0, 0, 1]]); rec.update(method='AFFINE_FALLBACK', a_inliers=int(ia.sum()))
        res = cv2.perspectiveTransform(src.reshape(-1, 1, 2), M).reshape(-1, 2) - dst
        e = np.linalg.norm(res, axis=1); sel = e < 6
        rec.update(H=M.tolist(), inlier_resid_median_px=float(np.median(e[sel])), inlier_resid_p95_px=float(np.percentile(e[sel], 95)))
    warped = cv2.warpPerspective(pl, np.array(rec['H']), (w, h), flags=cv2.INTER_CUBIC)
    cv2.imwrite(out + '_registered.png', warped)
    json.dump(rec, open(out + '_transform.json', 'w'), indent=1); print(json.dumps({k: v for k, v in rec.items() if k != 'H'}))
if __name__ == '__main__': main()
