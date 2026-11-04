import json,sys,cv2,numpy as np
sys.path.insert(0,'/workspace/posterity/motion/iterations-2026-10-22'); import animate as A
cfg=json.load(open(sys.argv[1])); n=int(sys.argv[2]) if len(sys.argv)>2 else 60
E=A.Engine(cfg); F=[P for L,P in E.layers if L['preset']=='fire-torchlight'][0]
H,W=E.H,E.W; S=np.zeros((H,W),np.float32); fz=np.zeros((H,W),bool)
for L_ in F.bspill['L']:
    xa,ya,xb,yb=L_['bb']; S[ya:yb,xa:xb]+=L_['map']
for B in F.beds:
    x0,y0,x1,y1=B['bb']; fz[y0:y1,x0:x1]|=B['D']<2.2*B['b']['height']
fz=cv2.dilate(fz.astype(np.uint8),np.ones((9,9),np.uint8))>0
sky=A.load_mask('batch2/masks/p06_sky_strict_v2.png',(H,W))>0.5
regs={'spill_strong':(S>0.5)&~fz&~sky,'spill_mid':(S>0.2)&(S<=0.5)&~fz&~sky,'ground_below_clumps':np.zeros((H,W),bool),'frame':np.ones((H,W),bool)}
for B in F.beds:
    if B['b']['height']<60: continue
    pts=np.int32(B['b']['points']); m=np.zeros((H,W),np.uint8); cv2.polylines(m,[pts+[0,40]],False,1,40); regs['ground_below_clumps']|=(m>0)&~fz
regs['ground_below_clumps']&=~sky
lum=lambda z:(0.299*z[...,0]+0.587*z[...,1]+0.114*z[...,2])
L0=lum(E.plate); rows={k:[] for k in regs}
ts=[i/30 for i in range(n)]
for t in ts:
    L=lum(E.render(t)[0])
    for k,m in regs.items(): rows[k].append(float(L[m].mean()))
out={}
for k,m in regs.items():
    v=np.float64(rows[k]); b=float(L0[m].mean()); mid=float(v.max()+v.min())/2
    out[k]=dict(px=int(m.sum()),plate=round(b,1),after_mean=round(float(v.mean()),1),lift_pct=round(float(100*(v.mean()/b-1)),1),min=round(float(v.min()),1),max=round(float(v.max()),1),
                p2p=round(float(v.max()-v.min()),1),p2p_pct_of_mean=round(float(100*(v.max()-v.min())/v.mean()),1),half_swing_pct=round(float(100*(v.max()-v.min())/2/mid),1),
                max_step_pct=round(float(100*np.abs(np.diff(v)).max()/v.mean()),2),first1s_p2p_pct=round(float(100*(v[:30].max()-v[:30].min())/v[:30].mean()),1))
print(json.dumps(dict(frames=n,fps=30,t_span=[0,float(ts[-1])],regions=out),indent=1))
if len(sys.argv)>3:
    vis=cv2.cvtColor(np.round(E.plate).astype(np.uint8),cv2.COLOR_RGB2BGR)//2
    for k,c in zip(['spill_strong','spill_mid','ground_below_clumps'],[(0,0,255),(0,200,255),(255,120,0)]): vis[regs[k]]=(vis[regs[k]]*0.4+np.uint8(c)*0.6).astype(np.uint8)
    cv2.imwrite(sys.argv[3],vis)
