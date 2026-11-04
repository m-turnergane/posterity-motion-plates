import sys, subprocess, re, json, numpy as np, librosa
f = sys.argv[1]; tag = sys.argv[2]
SR = 22050
# ---- loudness (ebur128 framelog, 48k native)
p = subprocess.run(['ffmpeg','-nostats','-hide_banner','-i',f,'-af','ebur128=framelog=info:peak=true','-f','null','-'],capture_output=True,text=True)
err = p.stderr
rows = re.findall(r't:\s*([\d.]+)\s+TARGET.*?M:\s*(-?[\d.inf]+)\s+S:\s*(-?[\d.inf]+)', err)
T = np.array([float(r[0]) for r in rows]); M = np.array([float(r[1]) for r in rows]); S = np.array([float(r[2]) for r in rows])
summ = err[err.rfind('Summary:'):]
I = float(re.search(r'I:\s*(-?[\d.]+) LUFS', summ).group(1)); LRA = float(re.search(r'LRA:\s*(-?[\d.]+) LU', summ).group(1))
pk = re.search(r'Peak:\s*(-?[\d.inf]+) dBFS', summ); TP = pk.group(1) if pk else 'n/a'
# ---- audio
y = subprocess.run(['ffmpeg','-v','error','-i',f,'-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
y = np.frombuffer(y, dtype=np.float32).copy(); dur = len(y)/SR
n_fft=2048; hop=512
Sp = np.abs(librosa.stft(y,n_fft=n_fft,hop_length=hop))**2
fr = librosa.fft_frequencies(sr=SR,n_fft=n_fft); ft = librosa.frames_to_time(np.arange(Sp.shape[1]),sr=SR,hop_length=hop)
cent = librosa.feature.spectral_centroid(S=np.sqrt(Sp),sr=SR)[0]
tot = Sp.sum(0)+1e-12
low = Sp[(fr<150)].sum(0); mid = Sp[(fr>=200)&(fr<=4000)].sum(0); hi = Sp[fr>4000].sum(0)
oenv = librosa.onset.onset_strength(y=y,sr=SR,hop_length=hop)
on = librosa.frames_to_time(librosa.onset.onset_detect(onset_envelope=oenv,sr=SR,hop_length=hop,delta=0.12),sr=SR,hop_length=hop)
H,P = librosa.decompose.hpss(np.sqrt(Sp)); Pr = (P**2).sum(0)/((H**2).sum(0)+(P**2).sum(0)+1e-12)
def lmean(x): x=x[np.isfinite(x)&(x>-70)]; return float(10*np.log10(np.mean(10**(x/10)))) if len(x) else -70.0
B=5; nb=int(np.ceil(dur/B)); bins=[]
for i in range(nb):
    a,b=i*B,(i+1)*B; m=(ft>=a)&(ft<b); lm=(T>a)&(T<=b)
    bins.append(dict(t0=a, S=round(lmean(S[lm]),1) if lm.any() else -70, Mmax=round(float(np.max(M[lm])),1) if lm.any() else -70,
      cent=int(np.median(cent[m])) if m.any() else 0,
      low=round(float(low[m].sum()/tot[m].sum()),3), mid=round(float(mid[m].sum()/tot[m].sum()),3),
      mid_db=round(float(10*np.log10(mid[m].mean()+1e-12)),1),
      ons=int(((on>=a)&(on<b)).sum()), perc=round(float(np.median(Pr[m])),3)))
Sv=np.array([b['S'] for b in bins])
# ---- window search: 90s, 1s step, on per-second short-term
sec = np.arange(int(dur)); Ss = np.array([lmean(S[(T>s)&(T<=s+1)]) if ((T>s)&(T<=s+1)).any() else -70 for s in sec])
Ss = np.maximum(Ss,-60)
midsec = np.array([float(mid[(ft>=s)&(ft<s+1)].sum()/tot[(ft>=s)&(ft<s+1)].sum()) for s in sec])
W=90; cands=[]
for s in range(0, max(1,len(sec)-W+1)):
    w=Ss[s:s+W]
    if len(w)<W: break
    op=lmean(w[:12]); bodym=lmean(w[12:60]); pay=lmean(w[66:88]); peakt=int(np.argmax(w[40:89]))+40; endf=w[88:90].mean()
    build = np.polyfit(np.arange(12,80),w[12:80],1)[0]*68  # dB rise across body
    score = (pay-op) + 0.5*build + (3 if 66<=peakt<=88 else 0) - max(0,op-(I-2))*1.0 - 8*max(0,midsec[s:s+W].mean()-0.6)
    cands.append(dict(start=s, score=round(float(score),2), open=round(op,1), body=round(bodym,1), payoff=round(pay,1), peak_at=peakt, rise_dB=round(float(build),1), mid=round(float(midsec[s:s+W].mean()),3), wLUFS=round(lmean(w),1)))
cands.sort(key=lambda c:-c['score']); pick=[]
for c in cands:
    if all(abs(c['start']-p['start'])>=45 for p in pick): pick.append(c)
    if len(pick)==4: break
# swells / quiet sections (on per-second, smoothed 5s)
sm = np.convolve(Ss,np.ones(5)/5,mode='same')
peaks=[int(i) for i in librosa.util.peak_pick(sm,pre_max=15,post_max=15,pre_avg=15,post_avg=15,delta=2,wait=20)]
quiet=[]; thr=I-8; inq=False
for i,v in enumerate(sm):
    if v<thr and not inq: inq=True; q0=i
    if (v>=thr or i==len(sm)-1) and inq:
        inq=False
        if i-q0>=8: quiet.append([q0,i])
out=dict(tag=tag,file=f,duration=round(dur,2),I=I,LRA=LRA,TP=TP,onsets_total=len(on),onsets_per_min=round(len(on)/dur*60,1),
  mid_overall=round(float(mid.sum()/tot.sum()),3), low_overall=round(float(low.sum()/tot.sum()),3), cent_median=int(np.median(cent)),
  perc_median=round(float(np.median(Pr)),3), peaks=[[p,round(float(sm[p]),1)] for p in peaks], quiet=quiet, windows=pick, bins=bins)
json.dump(out,open(f'{tag}_analysis.json','w'),indent=1)
print(f"{tag}: dur {dur:.1f}s  I {I} LUFS  LRA {LRA}  TP {TP}  onsets/min {out['onsets_per_min']}  mid {out['mid_overall']} low {out['low_overall']} cent {out['cent_median']}Hz perc {out['perc_median']}")
print("peaks(s,LUFS-S):",out['peaks']); print("quiet(<I-8):",quiet)
for w in pick: print("WIN",w)
print("t0  S   Mmax cent  low   mid   midDb ons perc")
for b in bins: print(f"{b['t0']:4d} {b['S']:6.1f} {b['Mmax']:6.1f} {b['cent']:5d} {b['low']:.3f} {b['mid']:.3f} {b['mid_db']:6.1f} {b['ons']:3d} {b['perc']:.3f}")
