import numpy as np, cv2, json
F=np.load('frames270.npy',mmap_mode='r')
T=json.load(open('../_build_v1/timeline.json'))['segments']
out={}
for s in T:
    f0,f1=s['f0'],s['f1']; acc=np.zeros((480,270),np.float32); n=0; mx=0
    for a in range(f0+2,f1-8,6):
        A=cv2.cvtColor(np.ascontiguousarray(F[a]),cv2.COLOR_RGB2GRAY).astype(np.float32)
        Bm=cv2.cvtColor(np.ascontiguousarray(F[a+6]),cv2.COLOR_RGB2GRAY).astype(np.float32)
        M=np.eye(2,3,dtype=np.float32)
        try:_,M=cv2.findTransformECC(A,Bm,M,cv2.MOTION_AFFINE,(3,100,1e-6))
        except cv2.error: continue
        W=cv2.warpAffine(Bm,M,(270,480),flags=cv2.INTER_LINEAR+cv2.WARP_INVERSE_MAP)
        r=np.abs(cv2.GaussianBlur(W,(0,0),3)-cv2.GaussianBlur(A,(0,0),3))
        r[340:400,:]=0  # caption band
        acc=np.maximum(acc,r); n+=1
    ys,xs=np.where(acc>6)
    cv2.imwrite(f'q/res_{s["id"]}.png',np.clip(acc*20,0,255).astype(np.uint8))
    out[s['id']]=dict(max=round(float(acc[10:-10,10:-10].max()),1),n_gt6=int(len(ys)),bbox=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())] if len(ys) else None)
    print(s['id'],out[s['id']])
