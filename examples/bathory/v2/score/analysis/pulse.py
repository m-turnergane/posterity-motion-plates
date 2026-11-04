import librosa,numpy as np,json,glob,os
out={}
for f in sorted(glob.glob('candidates/*.mp3')):
    y,sr=librosa.load(f,sr=22050,mono=True)
    oe=librosa.onset.onset_strength(y=y,sr=sr)
    fps=sr/512
    def pulse(seg):
        seg=seg-seg.mean()
        ac=np.correlate(seg,seg,'full')[len(seg)-1:]; ac/=ac[0]+1e-9
        lo,hi=int(fps*0.3),int(fps*2.0)
        return float(ac[lo:hi].max())
    win=int(10*fps)
    p=[round(pulse(oe[i:i+win]),2) for i in range(0,len(oe)-win,win)]
    tempo=float(np.atleast_1d(librosa.beat.beat_tempo(onset_envelope=oe,sr=sr))[0]) if hasattr(librosa.beat,'beat_tempo') else float(np.atleast_1d(librosa.feature.rhythm.tempo(onset_envelope=oe,sr=sr))[0])
    out[os.path.basename(f)]={'pulse_whole':round(pulse(oe),2),'pulse_per_10s':p,'tempo':round(tempo,1)}
    print(os.path.basename(f),out[os.path.basename(f)])
json.dump(out,open('analysis/pulse.json','w'))
