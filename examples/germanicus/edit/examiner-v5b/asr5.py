import re, json, subprocess, numpy as np, difflib, sys
from faster_whisper import WhisperModel
M=sys.argv[1]; MOD=sys.argv[2]
G='/workspace/posterity/standalones/germanicus/'
W0=json.load(open(G+'edit/_build_v5final/vo_words.json'))['words']
# cut at line gaps, chunks <= 24 s
ls={}
for w in W0: ls.setdefault(w['line'],[w['start'],w['end']]); ls[w['line']][1]=w['end']
L=sorted(ls.values()); cuts=[0.0]
for i in range(1,len(L)):
    mid=(L[i-1][1]+L[i][0])/2
    if i+1<len(L) and L[i+1][0]-cuts[-1]>24: cuts.append(mid)
cuts.append(124.0)
a=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',M,'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True).stdout,np.float32).copy()
m=WhisperModel(MOD,device='cpu',compute_type='int8')
W=[]
for x,y in zip(cuts[:-1],cuts[1:]):
    seg,_=m.transcribe(a[int(x*16000):int(y*16000)],language='en',word_timestamps=True,beam_size=5,condition_on_previous_text=False)
    W+=[(w.word.strip(),round(w.start+x,2),round(w.end+x,2),round(w.probability,3)) for s in seg for w in s.words]
json.dump(dict(cuts=cuts,words=W),open(sys.argv[3],'w'))
norm=lambda s:re.sub(r"[^a-z' ]","",s.lower().replace('-',' ').replace('\n',' ')).split()
script=norm(open(G+'raw/script-vo.txt').read())
asr=norm(' '.join(w[0] for w in W))
sm=difflib.SequenceMatcher(None,script,asr,autojunk=False)
print('cuts',[round(c,2) for c in cuts]); print(len(script),len(asr),[(op,script[i1:i2],asr[j1:j2]) for op,i1,i2,j1,j2 in sm.get_opcodes() if op!='equal'])
