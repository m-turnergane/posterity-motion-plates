import numpy as np, cv2, json, subprocess
M='/workspace/posterity/renders/posterity-germanicus-ROUGH-v1d.mp4'
T=json.load(open('../_build_v1d/timeline.json'))['segments']
p=subprocess.Popen(['ffmpeg','-v','error','-i',M,'-vf','scale=270:480','-f','rawvideo','-pix_fmt','gray','-'],stdout=subprocess.PIPE)
N=480*270; frames=[]; prev=None; diffs=[]; edge=[]
i=0
# also need color edge stats -> use gray
seg_iter=iter(T); cur=next(seg_iter); buf=[]; out={}
def analyse(s,buf):
    f0=s['f0']; acc=np.zeros((480,270),np.float32); geo=[]
    for k in range(2,len(buf)-8,6):
        A=buf[k].astype(np.float32); B=buf[k+6].astype(np.float32); Mx=np.eye(2,3,dtype=np.float32)
        try:_,Mx=cv2.findTransformECC(A,B,Mx,cv2.MOTION_AFFINE,(3,100,1e-6))
        except cv2.error: continue
        sx=np.hypot(Mx[0,0],Mx[1,0]); sy=np.hypot(Mx[0,1],Mx[1,1]); rot=np.degrees(np.arctan2(Mx[1,0],Mx[0,0])); geo.append((sx,sy,rot))
        W=cv2.warpAffine(B,Mx,(270,480),flags=cv2.INTER_LINEAR+cv2.WARP_INVERSE_MAP)
        r=np.abs(cv2.GaussianBlur(W,(0,0),3)-cv2.GaussianBlur(A,(0,0),3)); r[340:400,:]=0; acc=np.maximum(acc,r)
    g=np.array(geo); ys,xs=np.where(acc[10:-10,10:-10]>6)
    cv2.imwrite(f'q/res_{s["id"]}.png',np.clip(acc*20,0,255).astype(np.uint8))
    d=dict(rot_max=round(float(np.abs(g[:,2]).max()),4),aniso_max=round(float(np.abs(g[:,0]-g[:,1]).max()),5),res_max=round(float(acc[10:-10,10:-10].max()),1),n_gt6=int(len(ys)),bbox=[int(xs.min())+10,int(ys.min())+10,int(xs.max())+10,int(ys.max())+10] if len(ys) else None)
    if s['id']=='7B':
        # oil stream roi (1080 coords x440-490,y880-1430 -> /4)
        d['oil_res_max']=round(float(acc[220:357,110:123].max()),2); d['oil_res_mean']=round(float(acc[220:357,110:123].mean()),2)
        d['flame_res_max']=round(float(acc[130:215,105:130].max()),2)
        # raw temporal std in oil roi after alignment: compare first and last aligned
        np.save('q/7B_acc.npy',acc)
    return d
while True:
    b=p.stdout.read(N)
    if len(b)<N: break
    f=np.frombuffer(b,np.uint8).reshape(480,270)
    if prev is not None: diffs.append(float(np.abs(f.astype(np.int16)-prev).mean()))
    edge.append((float(f[:,:2].mean()),float(f[:,-2:].mean()),float(f[:2,:].mean()),float(f[-2:,:].mean())))
    prev=f
    if i>=cur['f1']:
        out[cur['id']]=analyse(cur,buf); print(cur['id'],out[cur['id']],flush=True); cur=next(seg_iter); buf=[]
    buf.append(f); i+=1
out[cur['id']]=analyse(cur,buf); print(cur['id'],out[cur['id']])
d=np.array(diffs); cuts=[int(k+1) for k in np.where(d>18)[0]]
E=np.array(edge)
res=dict(n=i,cuts=cuts,expected=[s['f0'] for s in T][1:],edge_max=E.max(0).round(1).tolist(),edge_gt200=(E>200).sum(0).tolist(),motion=out)
json.dump(res,open('motion_v1c.json','w'),indent=1)
print({k:res[k] for k in ('n','cuts','expected','edge_max','edge_gt200')})
