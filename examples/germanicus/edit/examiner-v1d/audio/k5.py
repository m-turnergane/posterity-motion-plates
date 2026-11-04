import numpy as np, soundfile as sf, json
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
exec(open('k4.py').read().split('for lab in')[0])
exec(open('k.py').read().split('for name in')[0])
B=R+'_build_v1d/'
W=json.load(open(B+'vo_words.json'))['words']
x,_=sf.read(B+'audio/stem_bed_postlim.wav')
on=[w['start'] for i,w in enumerate(W) if i>0 and w['start']-W[i-1]['end']>=0.3 and w['start']>3]
off=[w['end'] for i,w in enumerate(W) if i<len(W)-1 and W[i+1]['start']-w['end']>=0.3 and w['end']>3]
t4,e4=env((x**2).mean(1),0.4,0.05)
d=lambda xs:np.array([np.interp(a+0.35,t4,e4)-np.interp(a-0.35,t4,e4) for a in xs])
rnd=np.random.default_rng(1).uniform(3,63,400)
for n,v in (('onsets',d(on)),('offsets',d(off)),('random',d(rnd))): print('stereo-power 400ms delta',n,len(v),round(float(v.mean()),2),round(float(v.std()),2))
fig,ax=plt.subplots(2,1,figsize=(14,7),sharex=True)
for lab,c in (('v1c','tab:gray'),('v1d','tab:red')):
    y,_=sf.read(R+f'_build_{lab}/audio/stem_bed_postlim.wav')
    t,e=env((y**2).mean(1),1.0,0.25); ax[0].plot(t,e,c,label=f'{lab} stereo power 1s')
    t,e=env(y.mean(1)**2,1.0,0.25); ax[0].plot(t,e,c,ls='--',lw=.8,label=f'{lab} mono-mean 1s (Atelier metric)')
tk,Lk=st(x,0.4,0.05); ax[1].plot(tk+0.2,Lk,'tab:red',label='v1d K-weighted ST 400ms (LUFS)')
for a in (ax[0],ax[1]):
    for w in W: a.axvspan(w['start'],w['end'],color='b',alpha=0.04)
    a.legend(fontsize=8); a.grid(alpha=.3)
ax[0].set_ylim(-40,-24); ax[1].set_ylim(-36,-22); ax[1].set_xlim(0,69); ax[1].set_xlabel('s (blue = VO words)')
plt.tight_layout(); plt.savefig('../q/bed_envelopes_v1c_v1d.png',dpi=80)
