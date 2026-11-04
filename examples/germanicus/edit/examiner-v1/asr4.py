import numpy as np, subprocess
b=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i','/workspace/posterity/standalones/germanicus/edit/_build_v1/audio/bed_ridden.wav','-ac','1','-ar','16000','-f','f32le','-'],capture_output=True).stdout,np.float32).copy()
from faster_whisper import WhisperModel
m=WhisperModel('large-v3',device='cpu',compute_type='int8')
for x,y in ((0,30),(30,69)):
    seg,_=m.transcribe(b[int(x*16000):int(y*16000)]*8,language='en',word_timestamps=True,condition_on_previous_text=False)
    print(x,[(w.word,round(w.start+x,2)) for s in seg for w in s.words])
