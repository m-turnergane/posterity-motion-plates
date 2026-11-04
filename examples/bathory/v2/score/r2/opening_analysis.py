import librosa,numpy as np,json
y,sr=librosa.load('candidates/macleod_ignosi.mp3',sr=44100,mono=True)
H=2048;hop=1024
S=np.abs(librosa.stft(y,n_fft=4096,hop_length=hop))
f=librosa.fft_frequencies(sr=sr,n_fft=4096)
cent=librosa.feature.spectral_centroid(S=S,sr=sr)[0]
flat=librosa.feature.spectral_flatness(S=S)[0]
chroma=librosa.feature.chroma_cqt(y=y,sr=sr,hop_length=hop)
yh,yp=librosa.effects.hpss(y)
rms_h=librosa.feature.rms(y=yh,frame_length=4096,hop_length=hop)[0]
rms_p=librosa.feature.rms(y=yp,frame_length=4096,hop_length=hop)[0]
low=(S[f<250]**2).sum(0)/((S**2).sum(0)+1e-12)
t=librosa.frames_to_time(np.arange(S.shape[1]),sr=sr,hop_length=hop)
KS_maj=np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88]);KS_min=np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])
names='C C# D D# E F F# G G# A A# B'.split()
def win(a,b):
    sel=(t>=a)&(t<b); c=chroma[:,sel[:chroma.shape[1]]].mean(1); c=c/c.sum()
    best=max([(np.corrcoef(np.roll(KS_maj,k),c)[0,1],names[k]+' maj') for k in range(12)]+[(np.corrcoef(np.roll(KS_min,k),c)[0,1],names[k]+' min') for k in range(12)])
    ent=float(-(c*np.log2(c+1e-12)).sum())
    # semitone-cluster tension: product of adjacent chroma bins
    clus=float(sum(c[i]*c[(i+1)%12] for i in range(12))/ (c**2).sum())
    return dict(centroid_Hz=round(float(np.median(cent[sel]))),low_lt250_pct=round(100*float(np.mean(low[sel])),1),flatness=round(float(np.mean(flat[sel])),4),
      perc_to_harm_dB=round(float(20*np.log10(np.mean(rms_p[sel])/np.mean(rms_h[sel]))),1),chroma_entropy_bits=round(ent,2),semitone_cluster=round(clus,2),key_fit=round(float(best[0]),2),key=best[1],
      top3=[names[i] for i in np.argsort(c)[::-1][:3]])
out={}
for lab,a in [('A_offset31',31),('B_offset0',0),('A_alt_offset29',29),('A_alt_offset35',35)]:
    out[lab]={'whole_0-6s':win(a,a+6)}
    for s in range(0,6,2): out[lab][f'{s}-{s+2}s']=win(a+s,a+s+2)
# reference: the window overall
out['ref_window_31-111']=win(31,111); out['ref_peak_60-68']=win(60,68)
on=librosa.onset.onset_detect(y=y,sr=sr,units='time',backtrack=True)
out['onsets_24_40']=[round(float(x),2) for x in on if 24<=x<=40]
out['onsets_0_8']=[round(float(x),2) for x in on if x<=8]
json.dump(out,open('r2/opening_analysis.json','x'),indent=1)
print(json.dumps(out,indent=1))
