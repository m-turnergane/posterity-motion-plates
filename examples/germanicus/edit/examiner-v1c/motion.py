import numpy as np, cv2, json
F=np.load('frames270.npy',mmap_mode='r')
T=json.load(open('../_build_v1c/timeline.json'))['segments']
d=np.array([np.abs(F[i+1].astype(np.int16)-F[i]).mean() for i in range(len(F)-1)])
cuts=[i+1 for i in np.where(d>18)[0]]
print('cuts',cuts)
print('expected',[s['f0'] for s in T][1:])
res={}
for s in T:
    f0,f1=s['f0'],s['f1']; out=[]
    for a in range(f0+1,f1-6,6):
        A=cv2.cvtColor(np.ascontiguousarray(F[a]),cv2.COLOR_RGB2GRAY).astype(np.float32)
        Bm=cv2.cvtColor(np.ascontiguousarray(F[a+6]),cv2.COLOR_RGB2GRAY).astype(np.float32)
        M=np.eye(2,3,dtype=np.float32)
        try: _,M=cv2.findTransformECC(A,Bm,M,cv2.MOTION_AFFINE,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,100,1e-6))
        except cv2.error: out.append(None); continue
        W=cv2.warpAffine(Bm,M,(270,480),flags=cv2.INTER_LINEAR+cv2.WARP_INVERSE_MAP)
        r=np.abs(W-A)[20:-20,20:-20]
        sx=np.hypot(M[0,0],M[1,0]); sy=np.hypot(M[0,1],M[1,1]); rot=np.degrees(np.arctan2(M[1,0],M[0,0]))
        ys,xs=np.where(r>25)
        out.append(dict(sx=sx,sy=sy,rot=rot,shear=float(M[0,1]+M[1,0]),res_mean=float(r.mean()),n_gt25=int(len(ys)),bbox=[int(xs.min())+20,int(ys.min())+20,int(xs.max())+20,int(ys.max())+20] if len(ys) else None))
    ok=[o for o in out if o]
    res[s['id']]=dict(n=len(out),sx_rng=[round(min(o['sx'] for o in ok),5),round(max(o['sx'] for o in ok),5)],aniso_max=round(max(abs(o['sx']-o['sy']) for o in ok),5),rot_max=round(max(abs(o['rot']) for o in ok),4),res_mean_max=round(max(o['res_mean'] for o in ok),2),n_gt25_max=max(o['n_gt25'] for o in ok),bboxes=[o['bbox'] for o in ok if o['n_gt25']>20][:6])
    print(s['id'],res[s['id']])
json.dump(dict(cuts=cuts,motion=res),open('motion.json','w'),indent=1)
