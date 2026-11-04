import json, numpy as np, soundfile as sf, subprocess
from scipy.signal import butter, sosfiltfilt
exec(open('../examiner-v1e/audio/e1.py').read().split('O={}')[0])
B=E+'_build_v5final/'
W=json.load(open(B+'vo_words.json'))['words']
bed,_=sf.read(B+'audio_v5b/stem_bed_postlim.wav'); vo,_=sf.read(B+'audio_v5b/stem_vo_postlim.wav'); sfx,_=sf.read(B+'audio_v5b/stem_sfx_postlim.wav')
if vo.ndim==1: vo=np.stack([vo]*2,1)
if sfx.ndim==1: sfx=np.stack([sfx]*2,1)
raw=subprocess.run(['ffmpeg','-v','error','-i','/workspace/posterity/renders/posterity-germanicus-v5b-ROUGH.mp4','-f','f32le','-ac','2','-ar','48000','-'],capture_output=True).stdout
M=np.frombuffer(raw,np.float32).reshape(-1,2).astype(np.float64)
O={}
vL=vo.mean(1); bm=bed.mean(1); sm_=sfx.mean(1)
def pk(x,a,b): return 20*np.log10(np.abs(x[max(0,int(a*SR)):int(b*SR)]).max()+1e-12)
rows=[]
for i,w in enumerate(W):
    s_,e=w['start'],w['end']; v=pk(vL,s_,e)
    h=v-pk(bm,s_-.3,e+.3); smx=v-max(pk(bed[:,0],s_-.3,e+.3),pk(bed[:,1],s_-.3,e+.3))
    sf_=v-max(pk(sfx[:,0],s_-.3,e+.3),pk(sfx[:,1],s_-.3,e+.3)); bs=v-max(pk(bed[:,0]+sfx[:,0],s_-.3,e+.3),pk(bed[:,1]+sfx[:,1],s_-.3,e+.3))
    rows.append(dict(i=i,w=w['word'],t=round(s_,2),line=w['line'],house=round(h,2),smax=round(smx,2),sfx=round(sf_,2) if sf_<200 else None,bed_sfx_smax=round(bs,2)))
O['n_words']=len(rows)
O['house_min5']=sorted(rows,key=lambda r:r['house'])[:5]
O['house_lt12']=[r for r in rows if r['house']<12]
O['smax_lt12']=[(r['w'],r['t'],r['smax']) for r in rows if r['smax']<12]
O['smax_lt9']=[(r['w'],r['t'],r['smax']) for r in rows if r['smax']<9]
O['seqC_words']=[r for r in rows if 60.8<=r['t']<=65.7]
# 1-4k masking
sos=butter(4,[1000,4000],btype='band',fs=SR,output='sos')
def rf(x,h=0.05):
    k=int(h*SR); q=len(x)//k; return np.arange(q)*h,10*np.log10(np.mean(x[:q*k].reshape(q,k)**2,1)+1e-12)
t,v50=rf(sosfiltfilt(sos,vL)); _,vr=rf(vL)
_,b50=rf(sosfiltfilt(sos,bm)); _,l50=rf(sosfiltfilt(sos,bed[:,0]+sfx[:,0])); _,r50=rf(sosfiltfilt(sos,bed[:,1]+sfx[:,1])); _,s50=rf(sosfiltfilt(sos,sm_))
sp=np.zeros(len(t),bool)
for w in W: sp|=(t>=w['start'])&(t+0.05<=w['end'])
sp&=vr>-35
for nm,bx in (('house_mono',b50),('stereo_max_bed+sfx',np.maximum(l50,r50))):
    d=v50[sp]-bx[sp]; O['band_'+nm]=dict(n=int(sp.sum()),median=round(float(np.median(d)),1),p5=round(float(np.percentile(d,5)),1),pct_lt6=round(100*float((d<6).mean()),2),pct_lt0=round(100*float((d<0).mean()),2))
kC=sp&(t>=60.9)&(t<=65.6); d=v50[kC]-s50[kC]; O['band_vs_sfx_seqC']=dict(n=int(kC.sum()),min=round(float(d.min()),1),median=round(float(np.median(d)),1),pct_lt6=round(100*float((d<6).mean()),1))
# per-line VO level (K-weighted integrated-ish, gated), last two lines
lines={}
for w in W: lines.setdefault(w['line'],[w['start'],w['end']]); lines[w['line']][1]=w['end']
kv=kw(vo); km=kw(M); kb=kw(bed)
def lufs(x,a,b): y=x[int(a*SR):int(b*SR)]; return round(float(-0.691+10*np.log10((y**2).sum(1).mean()+1e-15)),1)
L=sorted(lines.items()); O['line_lufs_vo']={l:(round(a,2),round(b,2),lufs(kv,a,b)) for l,(a,b) in L}
body=[lufs(kv,a,b) for l,(a,b) in L[:-2]]
O['vo_line_stats']=dict(body_median=float(np.median(body)),body_min=min(body),body_max=max(body),L22=O['line_lufs_vo'][L[-2][0]],L23=O['line_lufs_vo'][L[-1][0]])
O['pause_L22_L23']=round(L[-1][1][0]-L[-2][1][1],3); O['pause_L21_L22']=round(L[-2][1][0]-L[-3][1][1],3)
O['all_line_gaps']=[round(L[i][1][0]-L[i-1][1][1],2) for i in range(1,len(L))]
O['last_words']=[(r['w'],r['t'],r['house'],r['smax']) for r in rows if r['line']>=L[-2][0]]
O['bed_lufs_windows']={k:lufs(kb,a,b) for k,(a,b) in dict(body=(3,111.4),taildip=(113.5,119.4),L22=tuple(L[-2][1]),L23=tuple(L[-1][1]),fade=(119.9,123.9)).items()}
O['master_lufs_windows']={k:lufs(km,a,b) for k,(a,b) in dict(body=(0,112.4),L22=tuple(L[-2][1]),L23=tuple(L[-1][1])).items()}
# pumping: stereo 400ms bed delta at phrase on/offsets vs random
tt,e=env((bed**2).mean(1),0.4,0.05)
ph=[];s0=W[0]['start'];pe=W[0]['end']
for w in W[1:]:
    if w['start']-pe>0.25: ph.append((s0,pe)); s0=w['start']
    pe=w['end']
ph.append((s0,pe))
dd=lambda x: float(np.interp(x+0.2,tt,e)-np.interp(x-0.2,tt,e))
on=[dd(a) for a,b in ph if 3<a<111]; off=[dd(b) for a,b in ph if 3<b<111]; rr=[dd(x) for x in np.random.default_rng(1).uniform(4,110,400)]
O['pumping']=dict(n=len(on),on_mean=round(np.mean(on),2),on_absmax=round(max(map(abs,on)),2),off_mean=round(np.mean(off),2),off_absmax=round(max(map(abs,off)),2),rand_absmean=round(np.mean(np.abs(rr)),2),rand_p95=round(float(np.percentile(np.abs(rr),95)),2))
json.dump(dict(O,rows=rows),open('a2.json','w'),indent=1,default=float)
for k,v in O.items(): print(k,json.dumps(v,default=float))
