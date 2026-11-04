import json, numpy as np, soundfile as sf, subprocess
from scipy.signal import lfilter, butter, sosfiltfilt
E='/workspace/posterity/standalones/germanicus/edit/'; SR=48000
def kw(x):
    b1=[1.53512485958697,-2.69169618940638,1.19839281085285]; a1=[1,-1.69065929318241,0.73248077421585]
    b2=[1,-2,1]; a2=[1,-1.99004745483398,0.99007225036621]
    return lfilter(b2,a2,lfilter(b1,a1,x,axis=0),axis=0)
def env(p,win,hop):
    c=np.concatenate([[0],np.cumsum(p)]); w=int(win*SR); idx=np.arange(0,len(p)-w,int(hop*SR))
    return idx/SR+win/2, 10*np.log10((c[idx+w]-c[idx])/w+1e-12)
def mast(v):
    raw=subprocess.run(['ffmpeg','-v','error','-i',f'/workspace/posterity/renders/posterity-germanicus-ROUGH-{v}.mp4','-f','f32le','-ac','2','-ar','48000','-'],capture_output=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).astype(np.float64)
def stats(t,e,lo=3,hi=64):
    k=(t>=lo)&(t<=hi); x=e[k]
    return dict(range=round(float(np.ptp(x)),2),p95_p5=round(float(np.subtract(*np.percentile(x,[95,5]))),2),sd=round(float(x.std()),2),med=round(float(np.median(x)),2))
def maxmove(t,e,span,lo=3,hi=64):
    # max (max-min) within any window of length span, window start in [lo,hi-span]
    best=(0,0); hop=t[1]-t[0]; n=int(round(span/hop))
    k=np.where((t>=lo)&(t<=hi))[0]
    for i in k:
        seg=e[i:i+n+1]
        if t[min(i+n,len(t)-1)]>hi: break
        r=seg.max()-seg.min()
        if r>best[0]: best=(round(float(r),2),round(float(t[i]),2))
    return best
def events(t,e,span,thr,lo=3,hi=64):
    hop=t[1]-t[0]; n=int(round(span/hop)); out=[]
    for i in np.where((t>=lo)&(t<=hi-span))[0]:
        seg=e[i:i+n+1]; r=seg.max()-seg.min()
        if r>thr:
            a=int(np.argmin(seg)); b=int(np.argmax(seg))
            out.append((float(t[i]),float(r),float(t[i+a]),float(seg[a]),float(t[i+b]),float(seg[b])))
    # cluster
    cl=[]
    for ev in out:
        if cl and ev[0]-cl[-1][-1][0]<=0.5: cl[-1].append(ev)
        else: cl.append([ev])
    res=[]
    for c in cl:
        m=max(c,key=lambda z:z[1]); res.append(dict(span=[round(c[0][0],1),round(c[-1][0]+span,1)],max_move=round(m[1],2),low=[round(m[2],1),round(m[3],1)],high=[round(m[4],1),round(m[5],1)],dir='up' if m[4]>m[2] else 'down'))
    return res
O={}; ENV={}
for v in ('v1c','v1d','v1e'):
    x,_=sf.read(E+f'_build_{v}/audio/stem_bed_postlim.wav'); y=kw(x)
    d={}
    for nm,p in (('mono',x.mean(1)**2),('L',x[:,0]**2),('R',x[:,1]**2),('stereo',(x**2).mean(1)),('side',((x[:,0]-x[:,1])/2)**2)):
        t1,e1=env(p,1.0,0.1); t4,e4=env(p,0.4,0.05)
        d[nm]=dict(s1=stats(t1,e1),s400=stats(t4,e4),move1s_in1s=maxmove(t1,e1,1.0),move400_in1s=maxmove(t4,e4,1.0))
        ENV[(v,nm,'1s')]=(t1,e1)
    pk=(y**2).sum(1)
    tM,eM=env(pk,0.4,0.05); eM-=0.691; tS,eS=env(pk,3.0,0.1); eS-=0.691
    ENV[(v,'M')]=(tM,eM); ENV[(v,'S')]=(tS,eS)
    d['K_mom400']=dict(s=stats(tM,eM),move_in1s=maxmove(tM,eM,1.0),move_in3s=maxmove(tM,eM,3.0))
    d['K_st3s']=dict(s=stats(tS,eS,4.5,62.5),move_in3s=maxmove(tS,eS,3.0,4.5,62.5),events_gt2dB_in3s=events(tS,eS,3.0,2.0,4.5,62.5))
    # slow wander: 5s moving average of 1s mono / stereo / K
    for nm in ('mono','stereo'):
        t1,e1=ENV[(v,nm,'1s')]; k=int(5/0.1); sm=np.convolve(e1,np.ones(k)/k,'same'); live=(t1>=5.5)&(t1<=61.5)
        d[nm]['slow5s']=dict(range=round(float(np.ptp(sm[live])),2),p95_p5=round(float(np.subtract(*np.percentile(sm[live],[95,5]))),2),min=[round(float(t1[live][np.argmin(sm[live])]),1),round(float(sm[live].min()),2)],max=[round(float(t1[live][np.argmax(sm[live])]),1),round(float(sm[live].max()),2)])
        res=e1-sm; d[nm]['fast_resid_sd']=round(float(res[live].std()),2)
    O[v]=d
# v1e mono drift profile + K ST profile (every 1s)
t1,e1=ENV[('v1e','mono','1s')]; tS,eS=ENV[('v1e','S')]
O['v1e_mono1s_profile']={f'{a:.0f}':round(float(b),1) for a,b in zip(t1,e1) if abs(a-round(a))<0.01 and 2<=a<=66}
O['v1e_Kst3s_profile']={f'{a:.0f}':round(float(b),1) for a,b in zip(tS,eS) if abs(a-round(a))<0.01 and 2<=a<=66}
O['v1d_Kst3s_profile']={f'{a:.0f}':round(float(b),1) for a,b in zip(*ENV[('v1d','S')]) if abs(a-round(a))<0.01 and 2<=a<=66}
O['v1c_Kst3s_profile']={f'{a:.0f}':round(float(b),1) for a,b in zip(*ENV[('v1c','S')]) if abs(a-round(a))<0.01 and 2<=a<=66}
# Atelier-claim zones on v1e
for v in ('v1c','v1d','v1e'):
    z={}
    for lo,hi in ((19.8,21.6),(59,62.5),(24.5,27)):
        for nm in ('mono','L','R','stereo'):
            t,e=ENV[(v,nm,'1s')]; k=(t>=lo)&(t<=hi); z[f'{lo}-{hi}_{nm}_1s_range']=round(float(np.ptp(e[k])),2)
        tM,eM=ENV[(v,'M')]; k=(tM>=lo)&(tM<=hi); z[f'{lo}-{hi}_Kmom_range']=round(float(np.ptp(eM[k])),2)
    tM,eM=ENV[(v,'M')]; z['Kmom_at_61.0']=round(float(np.interp(61.0,tM,eM)),2); z['Kmom_max_59-62.5']=round(float(eM[(tM>=59)&(tM<=62.5)].max()),2)
    k=(tM>=19.9)&(tM<=21.4); z['Kmom_20.4_swing(19.9-21.4)']=round(float(np.ptp(eM[k])),2)
    O[v]['zones']=z
json.dump(O,open('e1.json','w'),indent=1)
np.savez_compressed('env.npz',**{f'{a}_{b}_{c}' if len(k)==3 else f'{k[0]}_{k[1]}':np.stack(ENV[k]) for k in ENV for a,b,c in [ (k+('',))[:3] ]})
for v in ('v1c','v1d','v1e'):
    d=O[v]; print('==',v)
    for nm in ('mono','L','R','stereo','side'): print(' ',nm,d[nm])
    print('  Kmom',d['K_mom400']); print('  Kst3',{k:v_ for k,v_ in d['K_st3s'].items() if k!='events_gt2dB_in3s'},'n_events',len(d['K_st3s']['events_gt2dB_in3s']))
    print('  zones',d['zones'])
print('v1e events',O['v1e']['K_st3s']['events_gt2dB_in3s'])
print('v1e mono',O['v1e_mono1s_profile']); print('v1e Kst3',O['v1e_Kst3s_profile']); print('v1d Kst3',O['v1d_Kst3s_profile'])
