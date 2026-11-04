import numpy as np, subprocess, json, cv2
T=json.load(open('/workspace/posterity/standalones/germanicus/edit/_build_v5final/timeline.json'))['segments']
p=subprocess.Popen(['ffmpeg','-v','error','-i','/workspace/posterity/renders/posterity-germanicus-v5-ROUGH.mp4','-vf','scale=540:960','-f','rawvideo','-pix_fmt','gray','-'],stdout=subprocess.PIPE)
n=540*960; prev=None; i=0
seg_of=np.zeros(3719,int)
for j,s in enumerate(T): seg_of[s['f0']:s['f1']]=j
acc={j:np.zeros((960,540)) for j in range(len(T))}; cnt={j:0 for j in range(len(T))}
cuts=[]; top=[]; gm=[]
while True:
    b=p.stdout.read(n)
    if len(b)<n: break
    f=np.frombuffer(b,np.uint8).reshape(960,540).astype(np.int16)
    top.append(float(f[:60].mean()))
    if prev is not None:
        d=np.abs(f-prev); gm.append(float(d.mean()))
        if seg_of[i]==seg_of[i-1]: acc[seg_of[i]]+=d; cnt[seg_of[i]]+=1
    prev=f; i+=1
print('frames',i)
gm=np.array(gm); big=np.where(gm>8)[0]+1; print('big consecutive diffs (frame,mean):',[(int(k),round(float(gm[k-1]),1)) for k in big])
tiles=[]; out={}
for j,s in enumerate(T):
    m=acc[j]/max(cnt[j],1)
    # region stats: fraction of pixels with mean consecutive diff >3 (moving), excluding caption band y 1350-1650 full-res -> 675-825 here
    mm=m.copy(); mm[640:860]=0
    if s['id']=='R': mm[100:330]=0
    out[s['id']]=dict(mean=round(float(m.mean()),2),p99=round(float(np.percentile(mm,99)),2),pct_gt3=round(100*float((mm>3).mean()),2),max=round(float(mm.max()),1))
    ys,xs=np.where(mm>3); 
    if len(ys): out[s['id']]['bbox_gt3_fullres']=[int(xs.min()*2),int(ys.min()*2),int(xs.max()*2),int(ys.max()*2)]
    t=cv2.resize(np.clip(m*40,0,255).astype(np.uint8),(180,320)); cv2.putText(t,s['id'],(4,20),0,0.6,255,1); tiles.append(t)
for k,v in out.items(): print(k,v)
print('top band mean f0-40:',[round(x) for x in top[:40]])
g=[np.hstack(tiles[r*10:(r+1)*10]+[np.zeros((320,180),np.uint8)]*(10-len(tiles[r*10:(r+1)*10]))) for r in range(2)]
cv2.imwrite('../q/motion_heatmaps_per_plate.jpg',np.vstack(g),[cv2.IMWRITE_JPEG_QUALITY,75])
json.dump(out,open('motion.json','w'),indent=1)
