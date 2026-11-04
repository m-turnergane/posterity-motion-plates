import json, numpy as np, soundfile as sf, subprocess
from scipy.signal import butter, sosfiltfilt
exec(open('e1.py').read().split('O={}')[0])
B=E+'_build_v1e/'
W=json.load(open(B+'vo_words.json'))['words']; words=[(w['word'],w['start'],w['end']) for w in W]
out={}
masters={v:mast(v) for v in ('v1c','v1d','v1e')}
vo,_=sf.read(B+'audio/stem_vo_postlim.wav'); bed,_=sf.read(B+'audio/stem_bed_postlim.wav')
if vo.ndim==1: vo=np.stack([vo,vo],1)
m=masters['v1e']; n=min(len(vo),len(bed),len(m)); res=m[:n]-vo[:n]-bed[:n]
out['stem_resid_db']=round(float(10*np.log10(np.mean(res**2)/np.mean(m[:n]**2))),1)
# master VO gaps: K-weighted level per gap
gaps=[(words[i][2]+0.05,words[i+1][1]-0.05) for i in range(len(words)-1) if words[i+1][1]-words[i][2]>=0.4]
G={}
for v,x in masters.items():
    y=(kw(x)**2).sum(1); G[v]=[round(float(-0.691+10*np.log10(y[int(a*SR):int(b*SR)].mean())),1) for a,b in gaps]
out['gaps']=[(round(a,2),round(b-a,2),G['v1c'][i],G['v1d'][i],G['v1e'][i]) for i,(a,b) in enumerate(gaps)]
for v in G: a=np.array(G[v]); out[f'gap_stats_{v}']=dict(n=len(a),range=round(float(np.ptp(a)),1),sd=round(float(a.std()),2),min=float(a.min()),max=float(a.max()))
# margins
vL=vo.mean(1); bm=bed.mean(1)
def pk(x,a,b): return 20*np.log10(np.abs(x[max(0,int(a*SR)):int(b*SR)]).max()+1e-12)
rows=[]
for w,s_,e in words:
    v=pk(vL,s_,e); rows.append((w,round(s_,2),round(v-pk(bm,s_-.3,e+.3),2),round(v-max(pk(bed[:,0],s_-.3,e+.3),pk(bed[:,1],s_-.3,e+.3)),2)))
out['house_min']=sorted(rows,key=lambda r:r[2])[:5]; out['sm_min']=sorted(rows,key=lambda r:r[3])[:8]
out['under12_house']=[r for r in rows if r[2]<12]; out['under12_sm']=[r for r in rows if r[3]<12]; out['under9_sm']=[r for r in rows if r[3]<9]
out['line13']=[r for r in rows if r[1]>62.9]
sos=butter(4,[1000,4000],btype='band',fs=SR,output='sos'); vb=sosfiltfilt(sos,vL); bb=sosfiltfilt(sos,bm); bL=sosfiltfilt(sos,bed[:,0]); bR=sosfiltfilt(sos,bed[:,1])
def rf(x,h=0.05):
    k=int(h*SR); q=len(x)//k; return np.arange(q)*h,10*np.log10(np.mean(x[:q*k].reshape(q,k)**2,1)+1e-12)
t,v50=rf(vb); _,b50=rf(bb); _,vr=rf(vL); _,l50=rf(bL); _,r50=rf(bR)
sp=np.zeros(len(t),bool)
for w,s_,e in words: sp|=(t>=s_)&(t+0.05<=e)
sp&=vr>-35
for nm,bx in (('house_mono',b50),('stereo_max',np.maximum(l50,r50))):
    d=v50[sp]-bx[sp]; out['band_'+nm]=dict(n=int(sp.sum()),median=round(float(np.median(d)),1),p5=round(float(np.percentile(d,5)),1),pct_lt6=round(100*float((d<6).mean()),2),pct_lt0=round(100*float((d<0).mean()),2))
json.dump(out,open('e4.json','w'),indent=1,default=float)
for k,v in out.items(): print(k,v)
