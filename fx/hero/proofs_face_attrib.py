"""Face screen-space attribution: is any 1080 face residual vs warpAffine(plate, near matrix) caused by the effects,
or by locked depth_v1 itself? Compares all-on vs depth-only (both effects off) on the same frames. Writes proofs/face_attrib_fullstack_v1.json."""
import sys, json; sys.argv = ['x']; sys.path.insert(0, '.')
import numpy as np, cv2
import fullstack_v1 as F
S = F.Stack(seconds=7.0, face_keep=True, torch_gain=1.0, smoke_gain=1.0); big = (1080, 1920); oB = S.sh.overscan(big, S.n)
out = []
for i in range(0, S.n, 15):
    M = S.sh.layer_affine(S.near, S.E[i], big, oB)
    ref = F.DEPTH.to8(cv2.warpAffine(S.Pf, M, big, flags=F.DEPTH.INTERP, borderMode=cv2.BORDER_REPLICATE)).astype(int)
    al = F.DEPTH.to8(S.frame(i, big, torch=True, smoke=True, o=oB)).astype(int)
    de = F.DEPTH.to8(S.frame(i, big, torch=False, smoke=False, o=oB)).astype(int)
    rec = dict(frame=i)
    for fk, m in S.faces.items():
        me = cv2.erode((m & S.sh.hard[S.near]).astype(np.uint8), F.DEPTH.disk(4)).astype(np.float32)
        mm = cv2.warpAffine(me, M, big, flags=cv2.INTER_LINEAR) > 0.999
        dd = np.abs(de - ref)[mm].max(-1); da = np.abs(al - de)[mm].max(-1)
        rec[fk] = dict(px=int(mm.sum()), depth_only_vs_ref_changed=int((dd > 0).sum()), depth_only_vs_ref_max=int(dd.max()),
                       all_on_vs_depth_only_changed=int((da > 0).sum()), all_on_vs_depth_only_max=int(da.max()))
    out.append(rec); print(rec, flush=True)
tot = {fk: sum(r[fk]["all_on_vs_depth_only_changed"] for r in out) for fk in S.faces}
json.dump(dict(frames=out, effects_changed_face_px_total=tot, camera_calls=dict(F.CAM_CALLS)), open('proofs/face_attrib_fullstack_v1.json', 'w'), indent=1)
print(tot, dict(F.CAM_CALLS))
