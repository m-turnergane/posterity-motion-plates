#!/usr/bin/env python3
"""TEMP audition VO only (not the v3 lock). Owner v3 narration, house Oliver settings copied from v2/build_rough_v1/vo/render_vo_bathory_rough_v1.py:
Oliver jfIS2w2yJi0grJZPyEsk, eleven_multilingual_v2, stability 0.5, similarity 0.75, style 0, speaker boost, default speed, with-timestamps. Refuses overwrite."""
import base64, json, os, re, urllib.request
from pathlib import Path
D = Path(__file__).parent; SRC = D.parent / 'OWNER-NARRATION-v3.md'
VOICE = 'jfIS2w2yJi0grJZPyEsk'; MODEL = 'eleven_multilingual_v2'
SETTINGS = {'stability': 0.5, 'similarity_boost': 0.75, 'style': 0.0, 'use_speaker_boost': True}
t = SRC.read_text().split('---')[0]
lines = [l.strip() for l in t.splitlines() if l.strip() and not l.startswith('#')]
text = ' '.join(lines); print(len(text.split()), 'words'); print(text)
mp3 = D / 'tempvo_oliver_v3_owner_AUDITION.mp3'; aln = D / 'tempvo_oliver_v3_owner_AUDITION_alignment.json'
if mp3.exists(): raise SystemExit('refusing overwrite')
body = {'model_id': MODEL, 'seed': 1610, 'text': text, 'voice_settings': SETTINGS}
req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128', data=json.dumps(body).encode(),
    headers={'xi-api-key': os.environ['ELEVENLABS_API_KEY'], 'Content-Type': 'application/json', 'Accept': 'application/json'})
r = json.loads(urllib.request.urlopen(req, timeout=600).read())
mp3.write_bytes(base64.b64decode(r['audio_base64']))
al = r['alignment']; json.dump({**al, 'text_sent': text, 'voice': VOICE, 'model': MODEL, 'voice_settings': SETTINGS, 'seed': 1610}, open(aln, 'w'))
print('ok')
