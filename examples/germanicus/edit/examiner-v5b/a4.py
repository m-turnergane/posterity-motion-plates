import json, numpy as np, soundfile as sf
exec(open('../examiner-v1e/audio/e1.py').read().split('O={}')[0])
A5=E+'_build_v5final/audio/'; A5b=E+'_build_v5final/audio_v5b/'
O={}
def rd(p):
    x,_=sf.read(p); return x if x.ndim==2 else np.stack([x,x],1)
for nm in ('stem_vo_postlim','stem_sfx_postlim','stem_bed_postlim'):
    x=rd(A5+nm+'.wav'); y=rd(A5b+nm+'.wav')
    g=float(np.sum(x*y)/np.sum(x*x)); r=y-g*x
    t,ex=env((x**2).mean(1),0.5,0.1); t,ed=env(((y-x)**2).mean(1),0.5,0.1); t,ey=env((y**2).mean(1),0.5,0.1)
    live=ex>-60; gd=(ey-ex)[live]
    O[nm]=dict(global_gain_db=round(20*np.log10(g),3),resid_after_gain_db=round(10*np.log10(np.mean(r**2)/np.mean(x**2)),1),
      level_diff_500ms_db=dict(med=round(float(np.median(gd)),3),min=round(float(gd.min()),2),max=round(float(gd.max()),2),
      at_max=float(t[live][np.argmax(np.abs(gd))])),
      outside_31_40_absmax_db=round(float(np.abs(gd[(t[live]<31)|(t[live]>40)]).max(initial=0)),2),
      inside_31_40_absmax_db=round(float(np.abs(gd[(t[live]>=31)&(t[live]<=40)]).max(initial=0)),2))
# VO diff per 1s windows list where >0.1 dB
x=rd(A5+'stem_vo_postlim.wav'); y=rd(A5b+'stem_vo_postlim.wav')
t,ex=env((x**2).mean(1),1.0,0.5); t,ey=env((y**2).mean(1),1.0,0.5)
O['vo_1s_windows_absdiff_gt0.1']=[[float(a),round(float(b),2)] for a,b,c in zip(t,ey-ex,ex) if c>-50 and abs(b)>0.1]
# chroma around crossfade
from scipy.signal import stft
bb=rd(A5b+'stem_bed_postlim.wav').mean(1)
names=['A','A#','B','C','C#','D','D#','E','F','F#','G','G#']
def chroma(t0,t1):
    s=bb[int(t0*SR):int(t1*SR)]; f,_,Z=stft(s,SR,nperseg=8192,noverlap=6144); P=np.abs(Z)**2
    k=(f>60)&(f<2000); pc=np.round(12*np.log2(f[k]/440))%12; ch=np.array([P[k][pc==j].sum(0) for j in range(12)]).mean(1); return ch/ch.sum()
for a,b in ((31.0,32.2),(32.2,32.8),(32.8,34.0),(37.2,38.1),(38.1,38.7),(38.7,39.9)):
    c=chroma(a,b); O[f'chroma_{a}-{b}']={names[j]:round(float(c[j]),2) for j in np.argsort(c)[::-1][:5]}
# where are other low adjacent-chroma cos in the bed (natural harmony changes)
cs=[]
for s0 in np.arange(5,108,0.5):
    p=chroma(s0,s0+1.5); q=chroma(s0+2.1,s0+3.6); cs.append([float(s0+1.8),float(p@q/np.linalg.norm(p)/np.linalg.norm(q))])
cs=np.array(cs); O['adjacent_cos_lt0.5']=[[round(a,1),round(b,2)] for a,b in cs if b<0.5]
json.dump(O,open('a4.json','w'),indent=1); print(json.dumps(O,indent=0))
