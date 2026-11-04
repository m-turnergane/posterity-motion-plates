#!/usr/bin/env python3
"""Oliver FINAL read of the EIC-fixed LOCKED VO v3/raw/script-vo-v3.txt (230 words, md5 9db405e1...). House Oliver settings
(jfIS2w2yJi0grJZPyEsk, eleven_multilingual_v2, stab 0.5, sim 0.75, style 0, speaker boost, default speed, seed 1611), 0.8 s SSML break
before the tagline (as v2). Refuses overwrite and refuses any other script md5."""
import base64, json, os, hashlib, urllib.request
from pathlib import Path
D = Path(__file__).parent; SRC = D.parent / 'raw' / 'script-vo-v3.txt'
m = hashlib.md5(SRC.read_bytes()).hexdigest(); assert m.startswith('9db405e1'), m
assert 'Nothing was ever proven against her in court.' in SRC.read_text()
VOICE = 'jfIS2w2yJi0grJZPyEsk'; MODEL = 'eleven_multilingual_v2'
SETTINGS = {'stability': 0.5, 'similarity_boost': 0.75, 'style': 0.0, 'use_speaker_boost': True}
L = [l.strip() for l in SRC.read_text().splitlines() if l.strip()]; assert L[-1].startswith('History remembers')
text = ' '.join(L[:-1]) + ' <break time="0.8s"/> ' + L[-1]
mp3 = D / 'vo_oliver_v3_final.mp3'; aln = D / 'vo_oliver_v3_final_alignment.json'
if mp3.exists(): raise SystemExit('refusing overwrite')
body = {'model_id': MODEL, 'seed': 1611, 'text': text, 'voice_settings': SETTINGS}
req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128', data=json.dumps(body).encode(),
    headers={'xi-api-key': os.environ['ELEVENLABS_API_KEY'], 'Content-Type': 'application/json', 'Accept': 'application/json'})
r = json.loads(urllib.request.urlopen(req, timeout=600).read())
mp3.write_bytes(base64.b64decode(r['audio_base64']))
json.dump({**r['alignment'], 'text_sent': text, 'src_md5': m, 'voice': VOICE, 'model': MODEL, 'voice_settings': SETTINGS, 'seed': 1611}, open(aln, 'w'))
print('ok', len(text.split()))
