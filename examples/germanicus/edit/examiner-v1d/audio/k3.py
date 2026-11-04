import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt
exec(open('k.py').read().split('for name in')[0])
x,_=sf.read('/workspace/posterity/standalones/germanicus/edit/_build_v1d/audio/stem_bed_postlim.wav')
t,L=st(x,1.0,0.25); tc=t+0.5
m=None
bands={'<150':butter(4,150,'low',fs=SR,output='sos'),'150-900':butter(4,[150,900],'band',fs=SR,output='sos'),'900-4.5k':butter(4,[900,4500],'band',fs=SR,output='sos'),'>4.5k':butter(4,4500,'high',fs=SR,output='sos')}
E={}
for k,s in bands.items():
    y=sosfiltfilt(s,m); w=SR; c=np.concatenate([[0],np.cumsum(y**2)]); idx=(t*SR).astype(int)
    E[k]=10*np.log10((c[idx+w]-c[idx])/w+1e-12)
y=m; c=np.concatenate([[0],np.cumsum(y**2)]); idx=(t*SR).astype(int); E['RMS']=10*np.log10((c[idx+SR]-c[idx])/SR+1e-12)
print('centre  Kst1s  RMS  <150 150-900 900-4.5k >4.5k')
for i in range(len(tc)):
    if (19<=tc[i]<=23 or 33<=tc[i]<=37 or 57<=tc[i]<=66) and abs(tc[i]*2-round(tc[i]*2))<1e-6:
        print(f'{tc[i]:5.1f} {L[i]:6.1f} {E["RMS"][i]:6.1f} '+' '.join(f'{E[k][i]:6.1f}' for k in bands))
live=(tc>=3)&(tc<=64)
for k in ['RMS']+list(bands): print(k,'live p5-p95 span',round(float(np.subtract(*np.percentile(E[k][live],[95,5]))),2),'range',round(float(np.ptp(E[k][live])),2))
