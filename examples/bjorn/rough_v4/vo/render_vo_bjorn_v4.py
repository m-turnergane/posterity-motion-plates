#!/usr/bin/env python3
"""ROUGH v4 VO. Oliver read of LOCKED raw/script-vo-v4-LOCKED.txt (md5 ff97caaa20d2238fddc30c7bdb4a0c8a; authorised for the rough by the
parent's relayed Vellum instruction 2026-11-03 11:03 EST). House Oliver settings (same as rough_v1 render_vo_bjorn_v3.py): voice jfIS2w2yJi0grJZPyEsk,
eleven_multilingual_v2, stability 0.5, similarity 0.75, style 0, speaker boost, seed 1611; 0.8 s break before the tagline.
STOPS on any other script md5. Words are never changed. Refuses overwrite."""
import base64, json, os, hashlib, urllib.request
from pathlib import Path
D = Path(__file__).parent; SRC = D.parents[1] / 'raw' / 'script-vo-v4-LOCKED.txt'
b = SRC.read_bytes(); m = hashlib.md5(b).hexdigest()
if m != 'ff97caaa20d2238fddc30c7bdb4a0c8a': raise SystemExit(f'STOP: script md5 {m} != ff97caaa20d2238fddc30c7bdb4a0c8a')
VOICE = 'jfIS2w2yJi0grJZPyEsk'; MODEL = 'eleven_multilingual_v2'
SETTINGS = {'stability': 0.5, 'similarity_boost': 0.75, 'style': 0.0, 'use_speaker_boost': True}
L = [l.strip() for l in b.decode().splitlines() if l.strip()]; assert len(L) == 17 and L[-1].startswith('History remembers')
text = ' '.join(L[:-1]) + ' <break time="0.8s"/> ' + L[-1]
mp3 = D / 'vo_oliver_bjorn_v4.mp3'; aln = D / 'vo_oliver_bjorn_v4_alignment.json'
if mp3.exists(): raise SystemExit('refusing overwrite')
body = {'model_id': MODEL, 'seed': 1611, 'text': text, 'voice_settings': SETTINGS}
req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128', data=json.dumps(body).encode(),
    headers={'xi-api-key': os.environ['ELEVENLABS_API_KEY'], 'Content-Type': 'application/json', 'Accept': 'application/json'})
r = json.loads(urllib.request.urlopen(req, timeout=600).read())
mp3.write_bytes(base64.b64decode(r['audio_base64']))
json.dump({**r['alignment'], 'text_sent': text, 'src_md5': m, 'voice': VOICE, 'model': MODEL, 'voice_settings': SETTINGS, 'seed': 1611}, open(aln, 'w'))
# words (same tokeniser as rough_v1/build/vo_words.py)
ch, st, en = r['alignment']['characters'], r['alignment']['character_start_times_seconds'], r['alignment']['character_end_times_seconds']
s = ''.join(ch); b0 = s.find('<break'); b1 = s.find('/>', b0) + 2; toks = []; cur = None
for i, c in enumerate(ch):
    if b0 <= i < b1 or c.isspace():
        if cur: toks.append(cur); cur = None
        continue
    if cur is None: cur = dict(word='', start=st[i], end=en[i])
    cur['word'] += c; cur['end'] = en[i]
if cur: toks.append(cur)
DISP = [(w, li + 1) for li, l in enumerate(L) for w in l.split()]
assert [t['word'] for t in toks] == [w for w, _ in DISP], 'token mismatch'
for t, (_, li) in zip(toks, DISP): t['line'] = li
json.dump(dict(words=toks), open(D / 'vo_oliver_bjorn_v4_words_raw.json', 'x'), indent=0)
print('ok words', len(toks), 'end', toks[-1]['end'], 'md5', hashlib.md5(mp3.read_bytes()).hexdigest())
