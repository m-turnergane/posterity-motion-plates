import re, json, subprocess, numpy as np
from faster_whisper import WhisperModel
M='/workspace/posterity/renders/posterity-germanicus-ROUGH-v1.mp4'
a=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',M,'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True).stdout,np.float32).copy()
m=WhisperModel('medium.en',device='cpu',compute_type='int8')
seg,_=m.transcribe(a,language='en',word_timestamps=True,beam_size=5,condition_on_previous_text=False,initial_prompt='Germanicus, Piso, Tacitus, Syria.')
W=[(w.word.strip(),round(w.start,2)) for s in seg for w in s.words]
json.dump(W,open('asr_master_medium.json','w'))
norm=lambda s:re.sub(r"[^a-z' ]","",s.lower().replace('-',' ')).split()
script=norm(open('/workspace/posterity/standalones/germanicus/raw/script-vo-OWNER-v3.txt').read().replace(chr(10),' '))
srt=open('/workspace/posterity/standalones/germanicus/edit/germanicus_rough_v1.srt').read()
cues=re.findall(r'\d+\n([\d:,]+) --> ([\d:,]+)\n(.*?)(?:\n\n|\Z)',srt,re.S)
srtw=norm(' '.join(c[2] for c in cues))
asr=norm(' '.join(w for w,_ in W))
import difflib
print('script',len(script),'srt',len(srtw),'asr',len(asr))
for nm,x in (('srt',srtw),('asr',asr)):
    sm=difflib.SequenceMatcher(None,script,x,autojunk=False)
    print(nm,[ (op,script[i1:i2],x[j1:j2]) for op,i1,i2,j1,j2 in sm.get_opcodes() if op!='equal'])
print('first cue',cues[0][:2],cues[0][2]); print('last',cues[-1])
