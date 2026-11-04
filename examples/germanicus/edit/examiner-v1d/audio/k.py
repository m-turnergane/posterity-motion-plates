import numpy as np, soundfile as sf
from scipy.signal import lfilter
B='/workspace/posterity/standalones/germanicus/edit/_build_v1d/audio/'
SR=48000
def kw(x):
    b1=[1.53512485958697,-2.69169618940638,1.19839281085285]; a1=[1,-1.69065929318241,0.73248077421585]
    b2=[1,-2,1]; a2=[1,-1.99004745483398,0.99007225036621]
    return lfilter(b2,a2,lfilter(b1,a1,x,axis=0),axis=0)
def st(x,win=0.4,hop=0.1):
    y=kw(x); p=(y**2).sum(1); w=int(win*SR); h=int(hop*SR)
    c=np.concatenate([[0],np.cumsum(p)]); idx=np.arange(0,len(p)-w,h)
    return idx/SR, -0.691+10*np.log10((c[idx+w]-c[idx])/w+1e-12)
for name in ('stem_bed_postlim.wav','music_seg.wav','bed_flat.wav'):
    x,_=sf.read(B+name); x=x if x.ndim==2 else np.stack([x,x],1)
    t,L=st(x)
    k=(t>=19.5)&(t<=22.5)
    print(name,'ST400 19.5-22.5 (window start, LUFS):'); print(' '.join(f'{a:.1f}:{b:.1f}' for a,b in zip(t[k],L[k])))
    live=(t>=2.5)&(t<=64)
    # rise rate: max (L[i+j]-L[i])/dt over j in 1..10 hops, live
    rr=[];
    for i in np.where(live)[0]:
        for j in range(1,11):
            if i+j<len(L): rr.append(((L[i+j]-L[i])/(j*0.1),L[i+j]-L[i],t[i],j*0.1))
    rr=np.array(rr); big=rr[rr[:,1]>=1.5]
    print(' live ST400 p5/p50/p95',np.percentile(L[live],[5,50,95]).round(2),' n rises>=1.5dB within <=1s:',len(np.unique(big[:,2])) if len(big) else 0, ' max rise',rr[:,1].max().round(2),'at',rr[np.argmax(rr[:,1]),2])
