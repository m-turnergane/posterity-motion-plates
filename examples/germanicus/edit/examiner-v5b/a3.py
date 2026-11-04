import json, numpy as np, soundfile as sf, subprocess
exec(open('../examiner-v1e/audio/e1.py').read().split('O={}')[0])
A5=E+'_build_v5final/audio/'; A5b=E+'_build_v5final/audio_v5b/'
def rd(p):
    x,sr=sf.read(p); assert sr==SR; return x if x.ndim==2 else np.stack([x,x],1)
O={}
b5=rd(A5+'stem_bed_postlim.wav'); bb=rd(A5b+'stem_bed_postlim.wav')
def dB(x): return 10*np.log10(np.mean(x**2)+1e-20)
# nulls
for nm in ('stem_vo_postlim','stem_sfx_postlim','vo_staged'):
    x=rd(A5+nm+'.wav'); y=rd(A5b+nm+'.wav'); n=min(len(x),len(y))
    O['null_'+nm]=dict(maxabs=float(np.abs(x[:n]-y[:n]).max()),rel_db=round(dB(x[:n]-y[:n])-dB(x[:n]),1) if np.any(x[:n]-y[:n]) else '-inf',len=[len(x),len(y)])
def mst(f):
    r=subprocess.run(['ffmpeg','-v','error','-i',f,'-f','f32le','-ac','2','-ar','48000','-'],capture_output=True).stdout
    return np.frombuffer(r,np.float32).reshape(-1,2).astype(np.float64)
R='/workspace/posterity/renders/posterity-germanicus-'
M5=mst(R+'v5-ROUGH.mp4'); Mb=mst(R+'v5b-ROUGH.mp4'); n=min(len(M5),len(Mb))
# bed diff over time
d=b5[:n]-bb[:n]; t,ed=env((d**2).mean(1),0.5,0.1); t,e5=env((b5[:n]**2).mean(1),0.5,0.1)
rel=ed-e5; ch=t[rel>-40]; O['bed_diff_span_gt-40dB']=[float(ch.min()),float(ch.max())] if len(ch) else None
ch=t[rel>-60]; O['bed_diff_span_gt-60dB']=[float(ch.min()),float(ch.max())] if len(ch) else None
O['bed_diff_outside_31_40_maxrel']=round(float(rel[(t<31)|(t>40)].max()),1)
# master diff
dm=M5[:n]-Mb[:n]; t,em=env((dm**2).mean(1),0.5,0.1); t,e5m=env((M5[:n]**2).mean(1),0.5,0.1); r2=em-e5m
O['master_diff_rel_max_outside_31_40']=round(float(r2[(t<31)|(t>40)].max()),1)
k=slice(int(112*SR),n); O['master_112_end_null_rel_db']=round(dB(dm[k])-dB(M5[k]),1); O['master_112_end_maxabs']=float(np.abs(dm[k]).max())
# dip window metrics
for nm,b in (('v5',b5),('v5b',bb)):
    pk=(kw(b)**2).sum(1); tS,eS=env(pk,3.0,0.1); eS-=0.691
    w=(tS>=29.5)&(tS<=38.8); allw=(tS>=4.5)&(tS<=110)
    t1,e1=env(b.mean(1)**2,1.0,0.1); w1=(t1>=29.5)&(t1<=38.8); med=np.median(e1[(t1>=3)&(t1<=111.4)])
    O['dip_'+nm]=dict(st3_range=round(float(np.ptp(eS[w])),2),st3_min=[round(float(eS[w].min()),2),float(tS[w][np.argmin(eS[w])])],st3_med_all=round(float(np.median(eS[allw])),2),mono1s_min=[round(float(e1[w1].min()),2),float(t1[w1][np.argmin(e1[w1])])],mono1s_med=round(float(med),2),mono_under_med=round(float(med-e1[w1].min()),2))
# repetition: x-corr of bed 32.5-38.4 vs whole bed (mono), and source cue
def xc(seg,full):
    from scipy.signal import fftconvolve
    seg=seg-seg.mean(); L=len(seg)
    num=fftconvolve(full,seg[::-1],'valid'); c2=np.cumsum(np.r_[0,full**2]); den=np.sqrt((c2[L:]-c2[:-L])*np.sum(seg**2))+1e-12
    return num/den
ds=4; sr2=SR//ds
from scipy.signal import resample_poly
bm=resample_poly(bb.mean(1),1,ds)
seg=bm[int(32.5*sr2):int(38.4*sr2)]
c=xc(seg,bm); lag=np.arange(len(c))/sr2
mask=np.abs(lag-32.5)>3
O['xcorr_bed_self']=dict(peak_at_self=round(float(c[int(32.5*sr2)]),3),max_elsewhere=round(float(c[mask].max()),3),at=round(float(lag[mask][np.argmax(c[mask])]),2),p99_elsewhere=round(float(np.percentile(c[mask],99.9)),3))
# also chunks of 1.5 s within splice vs whole bed
ch=[]
for s0 in np.arange(32.5,37.0,0.75):
    sg=bm[int(s0*sr2):int((s0+1.5)*sr2)]; cc=xc(sg,bm); lg=np.arange(len(cc))/sr2; mk=np.abs(lg-s0)>2
    ch.append([float(s0),round(float(cc[mk].max()),3),round(float(lg[mk][np.argmax(cc[mk])]),2)])
O['xcorr_chunks_1p5s']=ch
# against the full cue (absolute): where does the spliced segment sit in the cue; window used = 120..244
mus='/workspace/posterity/standalones/germanicus/score/macleod_ossuary6_air_v1c.mp3'
r=subprocess.run(['ffmpeg','-v','error','-i',mus,'-ac','1','-ar',str(sr2),'-f','f32le','-'],capture_output=True).stdout
cue=np.frombuffer(r,np.float32).astype(np.float64)
sgm=resample_poly(rd(A5b+'music_seg_spliced.wav').mean(1),1,ds)[int(33*sr2):int(38*sr2)]
cc=xc(sgm,cue); lg=np.arange(len(cc))/sr2; i=np.argmax(cc); O['splice_src_in_cue']=[round(float(lg[i]),2),round(float(cc[i]),3)]
mk=np.abs(lg-lg[i])>2; O['splice_src_2nd_best_in_cue']=[round(float(lg[mk][np.argmax(cc[mk])]),2),round(float(cc[mk].max()),3)]
O['cue_window_used']=[120.0,244.0]
# chroma around splice edges on bed
from scipy.signal import stft
def chroma(x,t0,t1):
    s=x[int(t0*SR):int(t1*SR)]; f,_,Z=stft(s,SR,nperseg=8192,noverlap=6144); P=np.abs(Z)**2
    k=(f>60)&(f<2000); pc=np.round(12*np.log2(f[k]/440))%12; ch=np.array([P[k][pc==j].sum(0) for j in range(12)]).mean(1); return ch/ch.sum()
names=['A','A#','B','C','C#','D','D#','E','F','F#','G','G#']
bmono=bb.mean(1); b5m=b5.mean(1)
for lab,(a0,a1,c0,c1) in {'entry':(30.7,32.2,32.8,34.3),'exit':(36.9,38.1,38.7,40.2)}.items():
    p=chroma(bmono,a0,a1); q=chroma(bmono,c0,c1)
    O['chroma_'+lab]=dict(before_top3=[names[j] for j in np.argsort(p)[::-1][:3]],after_top3=[names[j] for j in np.argsort(q)[::-1][:3]],cos=round(float(p@q/np.linalg.norm(p)/np.linalg.norm(q)),3))
    # v5 natural progression at same times for reference
    p=chroma(b5m,a0,a1); q=chroma(b5m,c0,c1); O['chroma_'+lab+'_v5ref']=round(float(p@q/np.linalg.norm(p)/np.linalg.norm(q)),3)
# typical cos of adjacent 1.5s windows across v5b bed
cs=[]
for s0 in np.arange(5,108,1.0):
    p=chroma(bmono,s0,s0+1.5); q=chroma(bmono,s0+2.1,s0+3.6); cs.append(p@q/np.linalg.norm(p)/np.linalg.norm(q))
cs=np.array(cs); O['chroma_cos_adjacent_dist']=dict(p5=round(float(np.percentile(cs,5)),3),p25=round(float(np.percentile(cs,25)),3),med=round(float(np.median(cs)),3),min=round(float(cs.min()),3))
# click: HPF 4k transient energy 5ms windows, z-score near splice
from scipy.signal import butter,sosfilt
sos=butter(4,4000,'hp',fs=SR,output='sos'); h=sosfilt(sos,bmono); t5,e5h=env(h**2,0.005,0.0025)
loc=(t5>4)&(t5<110); base=np.median(e5h[loc])
def jump(z):
    k=(t5>z-0.4)&(t5<z+0.4); dd=np.diff(e5h[k]); return round(float(dd.max()),1)
O['click_hf_5ms_maxjump']={str(z):jump(z) for z in (32.5,38.4)}
dd=np.diff(e5h[loc]); O['click_hf_5ms_jump_global']=dict(p99=round(float(np.percentile(dd,99)),1),p999=round(float(np.percentile(dd,99.9)),1),max=round(float(dd.max()),1))
# sample-level discontinuity: max abs 1st diff near splice vs global
d1=np.abs(np.diff(bmono)); g=np.percentile(d1[int(4*SR):int(110*SR)],99.99)
O['diff1_near']={str(z):round(float(d1[int((z-0.4)*SR):int((z+0.4)*SR)].max()/g),2) for z in (32.5,38.4)}
# level 400ms bed stereo around splice
t4,e4=env((bb**2).mean(1),0.4,0.05); t45,e45=env((b5**2).mean(1),0.4,0.05)
O['bed_400ms_around']={f'{x:.2f}':[round(float(y),1),round(float(np.interp(x,t45,e45)),1)] for x,y in zip(t4,e4) if 31.5<=x<=39.5 and abs(x*10-round(x*10))<0.01 and round(x*10)%5==0}
# onset/beat continuity: onset envelope autocorr tempo before vs across
on=np.maximum(0,np.diff(e4)); 
json.dump(O,open('a3.json','w'),indent=1,default=float); print(json.dumps(O,default=float,indent=0))
# ear clip
sf.write('ear_v5b_30-41s.wav',Mb[int(30*SR):int(41*SR)].astype(np.float32),SR,subtype='PCM_16')
