import numpy as np, soundfile as sf
SR=48000; R='/workspace/posterity/standalones/germanicus/edit/'
def env(p,win,hop):
    c=np.concatenate([[0],np.cumsum(p)]); w=int(win*SR); idx=np.arange(0,len(p)-w,int(hop*SR))
    return idx/SR+win/2, 10*np.log10((c[idx+w]-c[idx])/w+1e-12)
def mr(t,e,lo,hi,span=1.0):
    k=(t>=lo)&(t<=hi); t=t[k]; e=e[k]; best=(0,0); n=0
    for i in range(len(t)):
        j=(t>t[i])&(t<=t[i]+span)
        if j.any():
            r=e[j].max()-e[i]; n+=r>=1.5
            if r>best[0]: best=(round(float(r),2),round(float(t[i]),2))
    return best,n
for lab in ('v1c','v1d'):
    x,_=sf.read(R+f'_build_{lab}/audio/stem_bed_postlim.wav')
    for mname,p in (('mono(L+R)/2',x.mean(1)**2),('stereo power',(x**2).mean(1)),('side',((x[:,0]-x[:,1])/2)**2)):
        t,e=env(p,1.0,0.25); k=(t>=3)&(t<=64)
        print(lab,mname,'1s range',round(float(np.ptp(e[k])),2),'p5-95',round(float(np.subtract(*np.percentile(e[k],[95,5]))),2),'maxrise1s,count',mr(t,e,3,64),
              'zones',[ (z,round(float(np.ptp(e[(t>=z[0])&(t<=z[1])])),1)) for z in ((20,22),(33,36.5),(59,62.5),(63.5,64.5))])
