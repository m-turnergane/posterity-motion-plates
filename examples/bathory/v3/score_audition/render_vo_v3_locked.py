#!/usr/bin/env python3
"""Oliver read of the LOCKED VO v3/raw/script-vo-v3.txt (audio for audition/previews), house Oliver settings copied from
v2/build_rough_v1/vo/render_vo_bathory_rough_v1.py (jfIS2w2yJi0grJZPyEsk, eleven_multilingual_v2, stab 0.5, sim 0.75, style 0, boost, default speed).
SSML break 0.8s before the tagline, as in v2. Refuses overwrite."""
import base64, json, os, hashlib, urllib.request
from pathlib import Path
D = Path(__file__).parent; SRC = D.parent / 'raw' / 'script-vo-v3.txt'
VOICE = 'jfIS2w2yJi0grJZPyEsk'; MODEL = 'eleven_multilingual_v2'
SETTINGS = {'stability': 0.5, 'similarity_boost': 0.75, 'style': 0.0, 'use_speaker_boost': True}
L = [l.strip() for l in SRC.read_text().splitlines() if l.strip()]; assert L[-1].startswith('History remembers')
text = ' '.join(L[:-1]) + ' <break time="0.8s"/> ' + L[-1]
mp3 = D / 'vo_oliver_v3_locked.mp3'; aln = D / 'vo_oliver_v3_locked_alignment.json'
if mp3.exists(): raise SystemExit('refusing overwrite')
body = {'model_id': MODEL, 'seed': 1611, 'text': text, 'voice_settings': SETTINGS}
req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128', data=json.dumps(body).encode(),
    headers={'xi-api-key': os.environ['ELEVENLABS_API_KEY'], 'Content-Type': 'application/json', 'Accept': 'application/json'})
r = json.loads(urllib.request.urlopen(req, timeout=600).read())
mp3.write_bytes(base64.b64decode(r['audio_base64']))
json.dump({**r['alignment'], 'text_sent': text, 'src_md5': hashlib.md5(SRC.read_bytes()).hexdigest(), 'voice': VOICE, 'model': MODEL, 'voice_settings': SETTINGS, 'seed': 1611}, open(aln, 'w'))
print('ok', len(text.split()))
