import json, numpy as np, soundfile as sf, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
exec(open('e1.py').read().split('O={}')[0])
B=E+'_build_v1e/'; W=json.load(open(B+'vo_words.json'))['words']
# pumping: stereo-power 400ms delta at phrase onsets/offsets vs random
bed,_=sf.read(B+'audio/stem_bed_postlim.wav'); t,e=env((bed**2).mean(1),0.4,0.05)
ph=[];s0=W[0]['start'];pe=W[0]['end']
for w in W[1:]:
    if w['start']-pe>0.25: ph.append((s0,pe)); s0=w['start']
    pe=w['end']
ph.append((s0,pe))
def d(x): return float(np.interp(x+0.2,t,e)-np.interp(x-0.2,t,e))
on=[d(a) for a,b in ph if a>3]; off=[d(b) for a,b in ph if b>3]
rng=np.random.default_rng(1); rr=[d(x) for x in rng.uniform(4,63,300)]
P=dict(n_on=len(on),onset_mean=round(np.mean(on),2),onset_absmax=round(np.max(np.abs(on)),2),offset_mean=round(np.mean(off),2),offset_absmax=round(np.max(np.abs(off)),2),random_absmean=round(np.mean(np.abs(rr)),2),random_p95=round(float(np.percentile(np.abs(rr),95)),2))
print(P); json.dump(P,open('e5_pumping.json','w'))
z=np.load('env.npz'); C={'v1c':'tab:gray','v1d':'tab:blue','v1e':'tab:red'}
fig,ax=plt.subplots(5,1,figsize=(14,15),sharex=True)
for v,c in C.items():
    for i,k in enumerate(['mono_1s','stereo_1s','L_1s','M','S']):
        a=z[f'{v}_{k}']; ax[i].plot(a[0],a[1],color=c,lw=1.1 if v=='v1e' else .8,label=v)
    a=z[f'{v}_R_1s']; ax[2].plot(a[0],a[1],color=c,lw=.6,ls='--')
for a_,ttl in zip(ax,['bed mono (L+R)/2 1s RMS dBFS','bed stereo power (L²+R²)/2 1s RMS','bed L (solid) / R (dashed) 1s RMS','bed K-weighted momentary 400ms LUFS','bed K-weighted short-term 3s LUFS']):
    a_.set_title(ttl,fontsize=10); a_.grid(alpha=.3)
    for w in W: a_.axvspan(w['start'],w['end'],color='green',alpha=.05,lw=0)
    for x in (20.4,25.6,15.5,61.0): a_.axvline(x,color='k',ls=':',lw=.6)
ax[0].legend(); ax[-1].set_xlim(0,69); ax[-1].set_xlabel('s (green = VO words; dotted = 15.5/20.4/25.6/61.0)')
plt.tight_layout(); plt.savefig('../q/bed_envelopes_v1c_v1d_v1e.png',dpi=80)
