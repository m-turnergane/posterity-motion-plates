import json, numpy as np, soundfile as sf
exec(open('e1.py').read().split('O={}')[0])
W=json.load(open(E+'_build_v1e/vo_words.json'))['words']
w0=json.load(open(E+'_build_v1d/vo_words.json'))['words']
print('vo words identical v1d/v1e:',[ (a['start'],a['end']) for a in W]==[(a['start'],a['end']) for a in w0])
for a in W:
    if 13.8<a['start']<16.6 or 24.3<a['start']<27.5: print(a['word'],a['start'],a['end'])
# Kmom events >3dB in 3s, v1d and v1e, and source comparison
for v in ('v1d','v1e'):
    x,_=sf.read(E+f'_build_{v}/audio/stem_bed_postlim.wav'); p=(kw(x)**2).sum(1); t,e=env(p,0.4,0.05); e-=0.691
    ev=events(t,e,3.0,3.0,3,63.5); print(v,'Kmom >3dB/3s events',len(ev),[(z['span'],z['max_move'],z['dir'],z['low'],z['high']) for z in ev])
s,_=sf.read(E+'_build_v1e/audio/music_seg.wav'); s=s if s.ndim==2 else np.stack([s,s],1)
p=(kw(s)**2).sum(1); ts,es=env(p,0.4,0.05); es-=0.691
x,_=sf.read(E+'_build_v1e/audio/stem_bed_postlim.wav'); p=(kw(x)**2).sum(1); t,e=env(p,0.4,0.05); e-=0.691
n=min(len(t),len(ts))
for lo,hi in ((13.8,16.8),(24.3,27.3),(19.8,21.6),(59,62.5)):
    k=(t[:n]>=lo)&(t[:n]<=hi)
    print(lo,hi,'v1e Kmom range',round(float(np.ptp(e[:n][k])),2),'source range',round(float(np.ptp(es[:n][k])),2),' v1e-src diff range',round(float(np.ptp((e[:n]-es[:n])[k])),2))
    print('   v1e',[round(float(a),1) for a in e[:n][k][::4]]); print('   src',[round(float(a),1) for a in es[:n][k][::4]])
# rider curve slope
G=np.load(E+'_build_v1e/audio/bed_rider_db_100hz.npy').astype(float); print('rider shape',G.shape)
g=G[1:].sum(0) if G.ndim==2 and G.shape[0]>1 else G; tg=G[0] if G.ndim==2 else np.arange(len(G))/100
dg=np.gradient(g,tg); k=(tg>=3)&(tg<=64); print('rider range',g[k].min().round(2),g[k].max().round(2),'slope p99',np.percentile(abs(dg[k]),99).round(2),'max',abs(dg[k]).max().round(2))
