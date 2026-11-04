import json, numpy as np, soundfile as sf, subprocess, librosa
B='/workspace/posterity/standalones/germanicus/'
W=json.load(open(B+'edit/_build_v1/vo_words.json'))['words']
R=json.load(open(B+'vo/final-vo-oliver-germanicus-v2_words.json')); R=R.get('words',R)
print('raw words',len(R),R[0],R[-1])
# wps per line
from collections import defaultdict
L=defaultdict(list)
for w in W: L[w['line']].append(w)
for k,v in L.items(): print('L%02d'%k,len(v),'w',round(v[-1]['end']-v[0]['start'],2),'s',round(len(v)/(v[-1]['end']-v[0]['start']),2),'wps', ' syl/s',round(sum(librosa.util.normalize(np.array([1]))[0]*0+max(1,len([c for c in w['word'].lower() if c in 'aeiouy'])) for w in v)/(v[-1]['end']-v[0]['start']),2))
tot=len(W)/(W[-1]['end']); print('overall wps',round(tot,2))
# speed: master vs raw VO envelopes
def load(p):
    a=subprocess.run(['ffmpeg','-v','error','-i',p,'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True).stdout
    return np.frombuffer(a,np.float32)
m=load("/workspace/posterity/renders/posterity-germanicus-ROUGH-v1.mp4"); r=load(B+"vo/final-vo-oliver-germanicus-v2.wav"); print(len(m),len(r))
def env(x):
    h=160; n=len(x)//h; e=np.sqrt((x[:n*h].reshape(n,h)**2).mean(1)); return np.log(e+1e-4)
em,er=env(m),env(r)
for a in [2,20,40,58]:
    seg=er[a*100:(a+4)*100]; best=None
    for lag in range(-100,101):
        s=em[a*100+lag:(a+4)*100+lag]; c=np.corrcoef(seg,s)[0,1]
        if best is None or c>best[0]: best=(c,lag)
    print('win',a,'lag_ms',best[1]*10,'r',round(best[0],3))
# ffmpeg ebur on master
p=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',"/workspace/posterity/renders/posterity-germanicus-ROUGH-v1.mp4","-af",'ebur128=peak=true','-f','null','-'],capture_output=True,text=True).stderr
print(p[p.find('Summary'):])
