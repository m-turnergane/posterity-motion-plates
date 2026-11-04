#!/usr/bin/env python3
"""Germanicus v5c OUTRO VO line (owner note 2): "History remembers the victors. We remember the rest."
Same voice/model/settings as final-vo-oliver-germanicus-v5.wav (render_vo_germanicus_v5.py): Oliver jfIS2w2yJi0grJZPyEsk,
eleven_multilingual_v2, stability 0.5, similarity 0.75, style 0, speaker boost, default speed, /with-timestamps, mp3_44100_128 -> 48k mono s16.
Context for a matching read: previous_text = last two script lines (L22, L23; not spoken). No next_text (this is the closing line).
Key from env ELEVENLABS_API_KEY (never printed). Refuses overwrite. Usage: render_vo_germanicus_v5c_outro.py SEED [SEED...]"""
import base64, json, os, subprocess, sys, urllib.request
from pathlib import Path
OUT = Path('/workspace/posterity/standalones/germanicus/vo')
VOICE = 'jfIS2w2yJi0grJZPyEsk'; MODEL = 'eleven_multilingual_v2'
SETTINGS = {'stability': 0.5, 'similarity_boost': 0.75, 'style': 0.0, 'use_speaker_boost': True}
TEXT = 'History remembers the victors. We remember the rest.'
PREV = 'The man Germanicus saved was condemned as a rebel. Whether he had also been his killer remained unproved.'
for s in sys.argv[1:]:
    seed = int(s); name = f'v5c_outro_s{seed}'
    mp3 = OUT / f'vo_germanicus_oliver_{name}.mp3'; wav = OUT / f'vo_germanicus_oliver_{name}.wav'; aln = OUT / f'vo_germanicus_oliver_{name}_alignment.json'
    for p in (mp3, wav, aln):
        if p.exists(): raise SystemExit(f'refusing overwrite {p}')
    body = {'model_id': MODEL, 'seed': seed, 'text': TEXT, 'voice_settings': SETTINGS, 'previous_text': PREV}
    req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128', data=json.dumps(body).encode(),
                                 headers={'xi-api-key': os.environ['ELEVENLABS_API_KEY'], 'Content-Type': 'application/json', 'Accept': 'application/json'})
    r = json.loads(urllib.request.urlopen(req, timeout=300).read())
    mp3.write_bytes(base64.b64decode(r['audio_base64'])); al = r['alignment']
    json.dump({'characters': al['characters'], 'character_start_times_seconds': al['character_start_times_seconds'],
               'character_end_times_seconds': al['character_end_times_seconds'], 'seed': seed, 'voice_settings': SETTINGS, 'model': MODEL, 'voice': VOICE,
               'previous_text': PREV, 'text_sent': TEXT, 'speed': 'default (no speed-up)'}, open(aln, 'w'), indent=1)
    subprocess.check_call(['ffmpeg', '-v', 'error', '-n', '-i', str(mp3), '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', str(wav)])
    print('take', seed, 'ok; alignment==text:', ''.join(al['characters']).strip() == TEXT, 'end', al['character_end_times_seconds'][-1], flush=True)
