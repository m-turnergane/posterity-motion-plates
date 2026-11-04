#!/usr/bin/env python3
"""TEMP — TIMING GUIDE ONLY, NEVER FOR FINAL. Oliver read of L04 only, from raw/script-vo-v4-LOCKED.txt line 4
(md5 9325809855d0..., = v4c countersigned). Same voice/model/settings/seed as rough_v1/vo_prep/render_vo_bjorn_v3.py.
Words are never changed. Refuses overwrite."""
import base64, json, os, hashlib, urllib.request
from pathlib import Path
D = Path(__file__).parent; SRC = D.parents[2] / 'raw' / 'script-vo-v4-LOCKED.txt'
b = SRC.read_bytes(); m = hashlib.md5(b).hexdigest(); assert m == '9325809855d0aadfa46bcfda9a138689', m
L = [l.strip() for l in b.decode().splitlines() if l.strip()]
text = [l for l in L if l.startswith('A Viking fleet really')][0]
assert text == 'A Viking fleet really sailed past Spain, struck southern France, and raided Italy.', text
VOICE = 'jfIS2w2yJi0grJZPyEsk'; MODEL = 'eleven_multilingual_v2'
SETTINGS = {'stability': 0.5, 'similarity_boost': 0.75, 'style': 0.0, 'use_speaker_boost': True}
mp3 = D / 'TEMP_vo_oliver_L04.mp3'; aln = D / 'TEMP_vo_oliver_L04_alignment.json'
if mp3.exists(): raise SystemExit('refusing overwrite')
body = {'model_id': MODEL, 'seed': 1611, 'text': text, 'voice_settings': SETTINGS}
req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128', data=json.dumps(body).encode(),
    headers={'xi-api-key': os.environ['ELEVENLABS_API_KEY'], 'Content-Type': 'application/json', 'Accept': 'application/json'})
r = json.loads(urllib.request.urlopen(req, timeout=300).read())
mp3.write_bytes(base64.b64decode(r['audio_base64']))
json.dump({**r['alignment'], 'TEMP': 'timing guide only, never final', 'text_sent': text, 'src': str(SRC), 'src_md5': m, 'voice': VOICE, 'model': MODEL, 'voice_settings': SETTINGS, 'seed': 1611}, open(aln, 'w'))
print('ok')
