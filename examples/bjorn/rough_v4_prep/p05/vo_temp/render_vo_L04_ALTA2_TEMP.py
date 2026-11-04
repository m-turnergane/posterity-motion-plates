#!/usr/bin/env python3
"""TEMP — TIMING GUIDE ONLY, NEVER FOR FINAL. Oliver read of Scriptor's PROPOSED L04 ALT-A2 (pending Archivist + Vellum),
read VERBATIM from raw/script-vo-v4-LOCKED.txt line 4 (md5 ff97caaa20d2238fddc30c7bdb4a0c8a; Archivist PASS; pending owner via Vellum). Same voice/model/settings/seed 1611 as render_vo_L04_TEMP.py. Refuses overwrite."""
import base64, json, os, urllib.request, hashlib
from pathlib import Path
D = Path(__file__).parent
SRC = D.parents[2] / 'raw' / 'script-vo-v4-LOCKED.txt'; b = SRC.read_bytes(); m = hashlib.md5(b).hexdigest(); assert m == 'ff97caaa20d2238fddc30c7bdb4a0c8a', m
text = [l.strip() for l in b.decode().splitlines() if l.strip().startswith('A Viking fleet really')][0]
assert text == 'A Viking fleet really did sail, past Spain, into the Mediterranean, then struck southern France, and finally raided Italy.', text
VOICE = 'jfIS2w2yJi0grJZPyEsk'; MODEL = 'eleven_multilingual_v2'
SETTINGS = {'stability': 0.5, 'similarity_boost': 0.75, 'style': 0.0, 'use_speaker_boost': True}
mp3 = D / 'TEMP_vo_oliver_L04_ALTA2.mp3'; aln = D / 'TEMP_vo_oliver_L04_ALTA2_alignment.json'
if mp3.exists(): raise SystemExit('refusing overwrite')
body = {'model_id': MODEL, 'seed': 1611, 'text': text, 'voice_settings': SETTINGS}
req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128', data=json.dumps(body).encode(),
    headers={'xi-api-key': os.environ['ELEVENLABS_API_KEY'], 'Content-Type': 'application/json', 'Accept': 'application/json'})
r = json.loads(urllib.request.urlopen(req, timeout=300).read())
mp3.write_bytes(base64.b64decode(r['audio_base64']))
json.dump({**r['alignment'], 'TEMP': 'timing guide only, never final', 'text_sent': text, 'src': str(SRC), 'src_md5': m, 'status': 'ALT-A2, Archivist PASS, pending owner via Vellum', 'voice': VOICE, 'model': MODEL, 'voice_settings': SETTINGS, 'seed': 1611}, open(aln, 'w'))
# words
c = r['alignment']['characters']; s = r['alignment']['character_start_times_seconds']; e = r['alignment']['character_end_times_seconds']
W = []; cur = None
for ch, a, b in zip(c, s, e):
    if ch == ' ':
        if cur: W.append(cur); cur = None
        continue
    if cur is None: cur = [ch, a, b]
    else: cur[0] += ch; cur[2] = b
if cur: W.append(cur)
json.dump([dict(w=w, start=round(a, 3), end=round(b, 3)) for w, a, b in W], open(D / 'TEMP_L04_ALTA2_words_raw.json', 'w'), indent=0)
for w, a, b in W: print(f'{w:16s} {a:6.3f} {b:6.3f}')
