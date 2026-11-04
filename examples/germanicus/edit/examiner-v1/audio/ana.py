import sys, json, numpy as np, soundfile as sf, subprocess
sys.path.insert(0,'/workspace/posterity/serials/croatoan/ch1/score/harness')
import opt3_harness as H
from scipy.signal import butter, sosfiltfilt, correlate
B='/workspace/posterity/standalones/germanicus/edit/_build_v1/'
SR=48000
W=json.load(open(B+'vo_words.json'))['words']
words=[(w['word'],w['start'],w['end']) for w in W]
vo,_=sf.read(B+'audio/vo_staged.wav'); bd,_=sf.read(B+'audio/bed_ridden.wav'); bf,_=sf.read(B+'audio/bed_flat.wav')
orig=H.limited
H.limited=lambda vo,bed,mg=None,limit_db=-2.5,**k: orig(vo,bed,mg,limit_db=-4.0,**k)
S,rows,L=H.evaluate(words,vo,bd,bf,64.045,68.5667,master_gain_db=3.0,name='germ',key_words=(),name_accent_window=None)
out={'summary':S}
m=[(r['word'],r['start'],r['vo_pk_minus_bed_pk_pm300']) for r in rows]
out['lowest10']=sorted(m,key=lambda x:x[2])[:10]
out['opening_0_5']=[x for x in m if x[1]<5.2]
out['line13']=[x for x in m if x[1]>62.9]
# stereo-max variant
bS=L['bS']; vL=L['vL']
def pk(x,a,b): return 20*np.log10(np.abs(x[int(a*SR):int(b*SR)]).max()+1e-12)
out['line13_stereomax']=[(w,s,round(pk(vL,s,e)-max(pk(bS[:,0],s-.3,e+.3),pk(bS[:,1],s-.3,e+.3)),1)) for w,s,e in words if s>62.9]
# 1-4k band
sos=butter(4,[1000,4000],btype='band',fs=SR,output='sos')
vb=sosfiltfilt(sos,vL); bb=sosfiltfilt(sos,bS.mean(1))
t,v50=H.rf(vb); _,b50=H.rf(bb); _,vr=H.rf(vL)
sp=np.zeros(len(t),bool)
for w,s,e in words: sp|=(t>=s)&(t+0.05<=e)
sp&=vr[:len(t)]>-35
d=v50[sp]-b50[sp]
out['band1_4k']={'speech_frames':int(sp.sum()),'median_vo_minus_bed_db':round(float(np.median(d)),1),'p10':round(float(np.percentile(d,10)),1),'p5':round(float(np.percentile(d,5)),1),'frac_lt6':round(float((d<6).mean()),3),'frac_lt0':round(float((d<0).mean()),3)}
bw=[]
for w,s,e in words:
    mk=(t>=s)&(t+0.05<=e)&(vr[:len(t)]>-35)
    if mk.any(): bw.append((w,s,round(float((v50[mk]-b50[mk]).min()),1)))
out['band_word_min_lowest8']=sorted(bw,key=lambda x:x[2])[:8]
# bed level per 2s window (post-limiter bed, L/R mean RMS, and full-band) + band
_,bfull=H.rf(bS.mean(1))
win=[]
for a in np.arange(0,68,2.0):
    mk=(t>=a)&(t<a+2)
    win.append((a,round(float(10*np.log10(np.mean(10**(bfull[mk]/10)))),1),round(float(10*np.log10(np.mean(10**(b50[mk]/10)))),1)))
out['bed_2s_rms_full_band']=win
# ride gain trace
_,fl=H.rf(bf.mean(1)); _,rd=H.rf(bd.mean(1)); g=rd-fl
out['ride_gain']={f'{a}':round(float(np.median(g[(t>=a)&(t<a+1)])),2) for a in [0,0.3,1,10,30,50,60,63,64,64.5,65,65.5,66,67,68]}
# music hit around 63
out['bed_around_63']=[(round(float(a),2),round(float(bfull[(t>=a)&(t<a+0.25)].mean()),1)) for a in np.arange(61.5,65.5,0.25)]
json.dump(out,open('ana.json','w'),indent=1,default=float)
print(json.dumps({k:out[k] for k in out if k!='bed_2s_rms_full_band'},default=float,indent=0)[:6000])
print(win)
