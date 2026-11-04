import re, json, subprocess, numpy as np, difflib
from faster_whisper import WhisperModel
M='/workspace/posterity/renders/posterity-germanicus-ROUGH-v1.mp4'
a=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',M,'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True).stdout,np.float32).copy()
m=WhisperModel('small.en',device='cpu',compute_type='int8')
cuts=[0,11.0,21.1,30.6,42.6,54.4,69]
W=[]
for x,y in zip(cuts[:-1],cuts[1:]):
    seg,_=m.transcribe(a[int(x*16000):int(y*16000)],language='en',word_timestamps=True,beam_size=5,condition_on_previous_text=False)
    W+=[(w.word.strip(),round(w.start+x,2)) for s in seg for w in s.words]
json.dump(W,open('asr_master_small_chunks.json','w'))
norm=lambda s:re.sub(r"[^a-z' ]","",s.lower().replace('-',' ').replace('\n',' ')).split()
script=norm(open('/workspace/posterity/standalones/germanicus/raw/script-vo-OWNER-v3.txt').read())
asr=norm(' '.join(w for w,_ in W))
sm=difflib.SequenceMatcher(None,script,asr,autojunk=False)
print(len(asr),[(op,script[i1:i2],asr[j1:j2]) for op,i1,i2,j1,j2 in sm.get_opcodes() if op!='equal'])
