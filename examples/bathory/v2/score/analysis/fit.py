import json,numpy as np
r=json.load(open('analysis/loudness.json'))
# storyboard energies (est. t, s) -> target dB rel
segs=[(0,1.8,'I'),(1.8,3.5,'S'),(3.5,8.5,'U'),(8.5,10.5,'I'),(10.5,27.1,'U'),(27.1,29.4,'P'),(29.4,33.5,'P'),(33.5,39.2,'S'),(39.2,43.5,'I'),(43.5,43.9,'S'),(43.9,59.2,'U'),(59.2,60.8,'S'),(60.8,63.9,'U'),(63.9,69.4,'S'),(69.4,73.0,'O')]
val={'U':-2,'I':3,'P':6,'S':-6,'O':-5}
def target(scale):
    L=int(np.ceil(73*scale)); t=np.zeros(L)
    for a,b,e in segs:
        t[int(a*scale):int(np.ceil(b*scale))]=val[e]
    return t
out={}
for name,d in r.items():
    m=np.array(d['M_per_s'],float); m=np.maximum(m,-60)
    sm=np.convolve(m,np.ones(3)/3,'same')
    best=[]
    for scale in (1.0,1.15):
        tg=target(scale); L=len(tg)
        for off in range(0,len(sm)-L-10+1):
            w=sm[off:off+L]
            c=np.corrcoef(w,tg)[0,1]
            # penalties: deep holes (< median-15) and min level at start
            holes=int(np.sum(w<np.median(w)-15))
            best.append((round(c,3),scale,off,holes,round(float(w.max()-w.min()),1)))
    best.sort(reverse=True)
    out[name]=best[:5]
    print(name, best[:3])
json.dump(out,open('analysis/fit_top.json','w'))
