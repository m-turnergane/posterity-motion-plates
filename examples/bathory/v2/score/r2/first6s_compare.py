import librosa,numpy as np,json,glob,subprocess,re,os
names='C C# D D# E F F# G G# A A# B'.split()
KS_maj=np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88]);KS_min=np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])
res={}
for f in sorted(glob.glob('r2/previews/*_bedonly.wav')):
    e=subprocess.run(['ffmpeg','-nostats','-hide_banner','-t','6','-i',f,'-af','ebur128','-f','null','-'],capture_output=True,text=True).stderr
    T=[float(x) for x in re.findall(r't:\s*([\d.]+)\s+TARGET',e)];M=[float(x) for x in re.findall(r'TARGET.*?M:\s*(-?[\d.]+)',e)]
    Mh=[round(M[min(range(len(T)),key=lambda i:abs(T[i]-s))],1) for s in np.arange(0.5,6.01,0.5)]
    S6=re.search(r'I:\s*(-?[\d.]+) LUFS',e.split('Summary:')[1]).group(1)
    y,sr=librosa.load(f,sr=44100,duration=6)
    S=np.abs(librosa.stft(y,n_fft=4096,hop_length=1024));fr=librosa.fft_frequencies(sr=sr,n_fft=4096)
    band=lambda a,b:round(100*float((S[(fr>=a)&(fr<b)]**2).sum()/(S**2).sum()),1)
    c=librosa.feature.chroma_cqt(y=y,sr=sr).mean(1);c/=c.sum()
    kf,key=max([(np.corrcoef(np.roll(KS_maj,k),c)[0,1],names[k]+' maj') for k in range(12)]+[(np.corrcoef(np.roll(KS_min,k),c)[0,1],names[k]+' min') for k in range(12)])
    top=[names[i] for i in np.argsort(c)[::-1][:4]]
    clus=float(sum(c[i]*c[(i+1)%12] for i in range(12))/(c**2).sum()); trit=float(sum(c[i]*c[(i+6)%12] for i in range(6))/(c**2).sum())
    flux=librosa.onset.onset_strength(y=y,sr=sr)
    res[os.path.basename(f)]=dict(I_first6s=float(S6),M_every_0p5s=Mh,M_min=min(Mh),M_max=max(Mh),centroid_Hz=int(np.median(librosa.feature.spectral_centroid(S=S,sr=sr))),
      band_pct={'<120Hz':band(0,120),'120-500':band(120,500),'500-2k':band(500,2000),'2k-8k':band(2000,8000),'>8k':band(8000,22050)},
      chroma_top4=top,key_est=key,key_fit=round(float(kf),2),semitone_cluster=round(clus,2),tritone=round(trit,2),onset_flux_mean=round(float(flux.mean()),2))
    print(os.path.basename(f),json.dumps(res[os.path.basename(f)]))
json.dump(res,open('r2/first6s_compare.json','x'),indent=1)
