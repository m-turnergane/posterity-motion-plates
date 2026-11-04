import numpy as np, soundfile as sf
from scipy.ndimage import gaussian_filter1d
exec(open('e1.py').read().split('O={}')[0])
x0,_=sf.read(E+'_build_v1e/audio/bed_dipped.wav'); x0=x0 if x0.ndim==2 else np.stack([x0,x0],1)
real,_=sf.read(E+'_build_v1e/audio/stem_bed_postlim.wav')
H=SR//100
def env100(p,win=1.0):
    c=np.concatenate([[0],np.cumsum(p)]); w=int(win*SR); n=len(p)//H
    i=np.clip(np.arange(n)*H-w//2,0,len(p)-w); return 10*np.log10((c[i+w]-c[i])/w+1e-12)
def slopecap(g,cap):
    m=cap/100; f=g.copy()
    for i in range(1,len(f)): f[i]=np.clip(f[i],f[i-1]-m,f[i-1]+m)
    b=g.copy()
    for i in range(len(b)-2,-1,-1): b[i]=np.clip(b[i],b[i+1]-m,b[i+1]+m)
    return (f+b)/2
def ride(x,metric,tc,cap=3.0,it=4,clamp=6):
    g=np.zeros(len(x)//H); tt=np.arange(len(g))/100; live=(tt>=2.5)&(tt<=64.5)
    for _ in range(it):
        y=apply(x,g); p={'mono':y.mean(1)**2,'stereo':(y**2).mean(1)}[metric]
        e=env100(p); e=gaussian_filter1d(e,tc*100/2) if tc>0 else e
        dev=e-np.median(e[live]); dev[~live]=0
        g=np.clip(g-dev,-clamp,clamp); g=slopecap(g,cap)
    return apply(x,g),g
def apply(x,g):
    gi=np.interp(np.arange(len(x))/SR,np.arange(len(g))/100,g); return x*10**(gi/20)[:,None]
def ms(x,sdb):
    m=(x[:,0]+x[:,1])/2; s=(x[:,0]-x[:,1])/2*10**(sdb/20); return np.stack([m+s,m-s],1)
def report(nm,y):
    r={}
    for k,p in (('mono',y.mean(1)**2),('stereo',(y**2).mean(1)),('L',y[:,0]**2)):
        t,e=env(p,1.0,0.1); r[k]=(stats(t,e)['range'],stats(t,e)['p95_p5'])
    pk=(kw(y)**2).sum(1); tS,eS=env(pk,3.0,0.1); eS-=0.691; tM,eM=env(pk,0.4,0.05); eM-=0.691
    r['Kst3']=(stats(tS,eS,4.5,62.5)['range'],stats(tS,eS,4.5,62.5)['p95_p5'],maxmove(tS,eS,3.0,4.5,62.5)[0])
    r['Kmom']=(stats(tM,eM)['p95_p5'],maxmove(tM,eM,1.0)[0],len(events(tM,eM,3.0,3.0,3,63.5)))
    r['width_corr']=round(float(np.corrcoef(y[:,0],y[:,1])[0,1]),2)
    print(f'{nm:38s} mono(rng,p95-5)={r["mono"]} stereo={r["stereo"]} L={r["L"]} Kst3(rng,p95-5,max3s)={r["Kst3"]} Kmom(p95-5,max1s,ev>3/3s)={r["Kmom"]} corr={r["width_corr"]}')
report('v1e actual stem',real)
report('unridden bed_dipped',x0)
for nm,(sdb,metric,tc) in {'A slope-cap stereo-power (sim of v1e)':(0,'stereo',0),'B slow mono rider tc4s cap3':(0,'mono',4),'C slow stereo rider tc4s cap3':(0,'stereo',4),'D S-4dB + slow mono tc4s':(-4,'mono',4),'E S-4dB + slow stereo tc4s':(-4,'stereo',4),'F S-6dB + slow mono tc3s':(-6,'mono',3),'G S-6dB + mono tc1s cap3':(-6,'mono',1)}.items():
    y,g=ride(ms(x0,sdb),metric,tc); report(nm,y)
