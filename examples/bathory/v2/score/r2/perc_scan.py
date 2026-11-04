import librosa,numpy as np,json,csv
y,sr=librosa.load('candidates/macleod_ignosi.mp3',sr=44100,mono=True)
D=librosa.stft(y,n_fft=4096,hop_length=1024); H,P=librosa.decompose.hpss(D,margin=2.0)
fr=librosa.fft_frequencies(sr=sr,n_fft=4096); t=librosa.frames_to_time(np.arange(D.shape[1]),sr=sr,hop_length=1024)
Pa=np.abs(P)**2; Ha=np.abs(H)**2
low=Pa[fr<200].sum(0); mal=Pa[(fr>=400)&(fr<3000)].sum(0); harm=Ha.sum(0)+1e-12
# pitchedness of the percussive mid band (marimba = pitched mallet): peak-to-mean ratio of the percussive spectrum 400-3k
band=Pa[(fr>=400)&(fr<3000)]
pitched=band.max(0)/(band.mean(0)+1e-12)
rows=[]
for s in range(31,113):
    sel=(t>=s)&(t<s+1)
    rows.append(dict(track_s=s,video_s_at_off31=s-31,low_drum_dB=round(float(10*np.log10(low[sel].mean()/harm[sel].mean())),1),
                     mallet_band_dB=round(float(10*np.log10(mal[sel].mean()/harm[sel].mean())),1),mallet_pitchedness=round(float(np.median(pitched[sel])),1)))
with open('r2/perc_scan_ignosi_0-31_1-53.csv','x',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
ld=np.array([r['low_drum_dB'] for r in rows]); ml=np.array([r['mallet_band_dB'] for r in rows])
print('low_drum median',np.median(ld),'p80',np.percentile(ld,80),' mallet median',np.median(ml),'p80',np.percentile(ml,80))
for r in rows:
    flag=('DRUM ' if r['low_drum_dB']>=np.percentile(ld,80) else '')+('MALLET' if r['mallet_band_dB']>=np.percentile(ml,80) else '')
    if flag: print(r, flag)
