import json, numpy as np, soundfile as sf, subprocess
from scipy.signal import butter, sosfiltfilt
B='/workspace/posterity/standalones/germanicus/edit/_build_v1d/'
M='/workspace/posterity/renders/posterity-germanicus-ROUGH-v1d.mp4'
SR=48000
W=json.load(open(B+'vo_words.json'))['words']; words=[(w['word'],w['start'],w['end']) for w in W]
vo,_=sf.read(B+'audio/stem_vo_postlim.wav'); bed,_=sf.read(B+'audio/stem_bed_postlim.wav')
raw=subprocess.run(['ffmpeg','-v','error','-i',M,'-f','f32le','-ac','2','-ar','48000','-'],capture_output=True).stdout
mst=np.frombuffer(raw,np.float32).reshape(-1,2).astype(np.float64)
if vo.ndim==1: vo=np.stack([vo,vo],1)
n=min(len(vo),len(bed),len(mst)); s=vo[:n]+bed[:n]
# alignment check
c=[np.dot(s[24000:24000*40,0],mst[24000+k:24000*40+k,0]) for k in range(-2000,2001,1)] if False else None
res=mst[:n]-s; out={'len':[len(vo),len(bed),len(mst)],'stems_sum_vs_master_resid_db':round(float(10*np.log10(np.mean(res**2)/np.mean(mst[:n]**2))),1)}
out['bed_ch_corr']=round(float(np.corrcoef(bed[:,0],bed[:,1])[0,1]),3)
def env(x,win,hop=0.05):
    w=int(win*SR); h=int(hop*SR); m=x.mean(1) if x.ndim==2 else x
    p=np.convolve(m**2,np.ones(w)/w,'valid')[::h]; t=np.arange(len(p))*hop+win/2
    return t,10*np.log10(p+1e-12)
t1,e1=env(bed,1.0,0.25); t4,e4=env(bed,0.4,0.05)
out['env1s']={f'{a:.2f}':round(float(v),2) for a,v in zip(t1,e1)}
live=(t1>=3.0)&(t1<=64.0)
out['env1s_live']=dict(median=round(float(np.median(e1[live])),2),min=round(float(e1[live].min()),2),max=round(float(e1[live].max()),2),maxdev=round(float(np.abs(e1[live]-np.median(e1[live])).max()),2))
# max rise over any 1s / 2s / 3s span in live
def maxrise(t,e,span,lo,hi):
    best=(0,0)
    for i in range(len(t)):
        if t[i]<lo or t[i]>hi: continue
        j=(t>t[i])&(t<=t[i]+span)&(t<=hi)
        if j.any():
            r=e[j].max()-e[i]
            if r>best[0]: best=(round(float(r),2),round(float(t[i]),2))
    return best
out['maxrise_1s_env_within']={str(sp):maxrise(t1,e1,sp,3,64) for sp in (1,2,3,5)}
live4=(t4>=3)&(t4<=64)
out['env400_live']=dict(median=round(float(np.median(e4[live4])),2),p5=round(float(np.percentile(e4[live4],5)),2),p95=round(float(np.percentile(e4[live4],95)),2),min=round(float(e4[live4].min()),2),max=round(float(e4[live4].max()),2))
out['maxrise_400ms']={str(sp):maxrise(t4,e4,sp,3,64) for sp in (0.4,1,2)}
# slope dB/s of 400ms env smoothed
sl=np.gradient(e4,t4); out['env400_slope_p99_abs']=round(float(np.percentile(np.abs(sl[live4]),99)),2)
# 20.4-21.4 detail
out['zone_18_24_env400']=[(round(float(a),2),round(float(b),2)) for a,b in zip(t4,e4) if 18<=a<=24 and abs(a*10-round(a*10))<1e-6 and round(a*10)%2==0]
for z in [(20.0,22.0),(33,36.5),(59,62.5),(63.5,66)]:
    k=(t1>=z[0])&(t1<=z[1]); out[f'zone_{z[0]}_{z[1]}_1s']=dict(min=round(float(e1[k].min()),2),max=round(float(e1[k].max()),2),rise=maxrise(t1,e1,3,z[0],z[1]))
# fade
out['tail_1s']=[(round(float(a),2),round(float(b),1)) for a,b in zip(t1,e1) if a>=62]
# rider gain curve
G=np.load(B+'audio/bed_rider_db_100hz.npy').astype(float); tg=G[0]; g=G[1]+G[2]
gl=(tg>=3)&(tg<=64)
dg=np.gradient(g,tg)
out['rider']=dict(range=[round(float(g[gl].min()),2),round(float(g[gl].max()),2)],slope_p99=round(float(np.percentile(np.abs(dg[gl]),99)),2),slope_max=round(float(np.abs(dg[gl]).max()),2),at=round(float(tg[gl][np.argmax(np.abs(dg[gl]))]),2))
z=(tg>=20)&(tg<=22); out['rider_20_22']=[(round(float(a),2),round(float(b),2)) for a,b in zip(tg[z][::10],g[z][::10])]
# pumping: rider gain/env change around VO starts/stops (phrase onsets after gaps>=0.3)
on=[s for i,(w,s,e) in enumerate(words) if i==0 or s-words[i-1][2]>=0.3]
offs=[e for i,(w,s,e) in enumerate(words) if i==len(words)-1 or words[i+1][1]-e>=0.3]
def trig(times):
    d=[]
    for x in times:
        a=np.interp(x-0.3,t4,e4); b=np.interp(x+0.4,t4,e4); d.append(b-a)
    return round(float(np.mean(d)),2),round(float(np.std(d)),2),len(d)
rnd=np.random.default_rng(0).uniform(3,63,300)
out['pump_env400_delta_onsets(mean,sd,n)']=trig(on); out['pump_offsets']=trig(offs); out['pump_random']=trig(rnd)
gr=lambda xs:[float(np.interp(x+0.4,tg,g)-np.interp(x-0.3,tg,g)) for x in xs]
out['rider_delta_onsets']=round(float(np.mean(gr(on))),2); out['rider_delta_offsets']=round(float(np.mean(gr(offs))),2); out['rider_delta_rand']=round(float(np.mean(gr(rnd))),2)
# master in VO gaps >=0.4s
gaps=[(words[i][2]+0.05,words[i+1][1]-0.05) for i in range(len(words)-1) if words[i+1][1]-words[i][2]>=0.45]
mg=[]
for a,b in gaps:
    x=mst[int(a*SR):int(b*SR)]; mg.append((round(a,2),round(b-a,2),round(float(10*np.log10(np.mean(x**2)+1e-12)),1)))
out['master_vo_gaps']=mg
gv=np.array([m[2] for m in mg if m[0]>3 and m[0]<64]); out['master_gap_stats']=dict(n=len(gv),min=float(gv.min()),max=float(gv.max()),median=float(np.median(gv)))
# margins: house = VO peak - bed mono-mean peak within +-300ms; stereo-max = VO peak - max(L,R)
vL=vo.mean(1); bm=bed.mean(1)
def pk(x,a,b): return 20*np.log10(np.abs(x[max(0,int(a*SR)):int(b*SR)]).max()+1e-12)
rows=[]
for w,s_,e in words:
    v=pk(vL,s_,e); rows.append((w,s_,round(v-pk(bm,s_-.3,e+.3),1),round(v-max(pk(bed[:,0],s_-.3,e+.3),pk(bed[:,1],s_-.3,e+.3)),1)))
out['margin_min_house']=sorted(rows,key=lambda r:r[2])[:6]; out['margin_min_stereomax']=sorted(rows,key=lambda r:r[3])[:6]
out['n_under9_house']=sum(r[2]<9 for r in rows); out['n_under9_sm']=sum(r[3]<9 for r in rows)
out['line13']=[r for r in rows if r[1]>62.9]
# 1-4k masking
sos=butter(4,[1000,4000],btype='band',fs=SR,output='sos'); vb=sosfiltfilt(sos,vL); bb=sosfiltfilt(sos,bm)
def rf(x,h=0.05):
    k=int(h*SR); m=len(x)//k; return np.arange(m)*h,10*np.log10(np.mean(x[:m*k].reshape(m,k)**2,1)+1e-12)
t,v50=rf(vb); _,b50=rf(bb); _,vr=rf(vL)
sp=np.zeros(len(t),bool)
for w,s_,e in words: sp|=(t>=s_)&(t+0.05<=e)
sp&=vr>-35; d=v50[sp]-b50[sp]
out['band']=dict(n=int(sp.sum()),median=round(float(np.median(d)),1),p10=round(float(np.percentile(d,10)),1),p5=round(float(np.percentile(d,5)),1),frac_lt6=round(float((d<6).mean()),4),frac_lt0=round(float((d<0).mean()),4))
json.dump(out,open('a.json','w'),indent=1,default=float)
for k,v in out.items():
    if k not in ('env1s',): print(k,v)
# ear-check clip
sf.write('../clip_18-24s_master.wav',mst[int(18*SR):int(24*SR)].astype(np.float32),SR,subtype='PCM_16')
sf.write('../clip_18-24s_bedstem.wav',bed[int(18*SR):int(24*SR)].astype(np.float32),SR,subtype='PCM_16')
