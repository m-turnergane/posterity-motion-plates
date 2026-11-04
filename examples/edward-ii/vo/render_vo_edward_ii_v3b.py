#!/usr/bin/env python3
"""Edward II v3b VO: ONE ElevenLabs request for the whole script (raw/script-vo-v3-DRAFT.txt, md5-locked), incl. the L17 tagline.
Settings copied from Germanicus (render_vo_germanicus_v5.py / VO-NOTES.md): Oliver jfIS2w2yJi0grJZPyEsk, eleven_multilingual_v2,
stability 0.5, similarity_boost 0.75, style 0.0, use_speaker_boost true, default speed, /with-timestamps, mp3_44100_128; next_text anti-wind-down (not spoken).
<break> before the L17 tagline (as Germanicus v5 break before last line). Refuses overwrite. Usage: render_vo_edward_ii_v3b.py NAME:SEED[:BREAK_S] ..."""
import base64, json, os, subprocess, sys, urllib.request, hashlib
from pathlib import Path
ROOT = Path('/workspace/posterity/standalones/edward-ii'); OUT = ROOT / 'vo'; SCRIPT = ROOT / 'raw' / 'script-vo-v3-DRAFT.txt'
assert hashlib.md5(SCRIPT.read_bytes()).hexdigest() == 'b30ce609e7ae1b62216e124ace1bdc94', 'script md5 changed'
VOICE = 'jfIS2w2yJi0grJZPyEsk'; MODEL = 'eleven_multilingual_v2'
SETTINGS = {'stability': 0.5, 'similarity_boost': 0.75, 'style': 0.0, 'use_speaker_boost': True}
NEXT = 'Tomorrow, we open another forgotten page of history, and we follow the people who lived it.'
LINES = [l.strip() for l in SCRIPT.read_text().strip().splitlines() if l.strip()]; assert len(LINES) == 17 and LINES[-1].startswith('History remembers')
spoken = ' '.join(LINES)
for spec in sys.argv[1:]:
    parts = spec.split(':'); name = parts[0]; seed = int(parts[1]); brk = parts[2] if len(parts) > 2 else '0.8'
    script = ' '.join(LINES[:16]) + f' <break time="{brk}s"/> ' + LINES[16]
    mp3 = OUT / f'vo_edward_ii_oliver_{name}.mp3'; wav = OUT / f'cand-vo-oliver-edward-ii-{name}.wav'; aln = OUT / f'cand-vo-oliver-edward-ii-{name}_alignment.json'
    for p in (mp3, wav, aln):
        if p.exists(): raise SystemExit(f'refusing overwrite {p}')
    body = {'model_id': MODEL, 'seed': seed, 'text': script, 'voice_settings': SETTINGS, 'next_text': NEXT}
    req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128', data=json.dumps(body).encode(),
                                 headers={'xi-api-key': os.environ['ELEVENLABS_API_KEY'], 'Content-Type': 'application/json', 'Accept': 'application/json'})
    r = json.loads(urllib.request.urlopen(req, timeout=600).read())
    mp3.write_bytes(base64.b64decode(r['audio_base64'])); al = r['alignment']
    json.dump({**{k: al[k] for k in ('characters', 'character_start_times_seconds', 'character_end_times_seconds')}, 'seed': seed, 'voice_settings': SETTINGS, 'model': MODEL,
               'voice': VOICE, 'next_text': NEXT, 'text_sent': script, 'method': 'single full-script request, with-timestamps, SSML break before L17', 'speed': 'default'}, open(aln, 'w'), indent=1)
    subprocess.check_call(['ffmpeg', '-v', 'error', '-n', '-i', str(mp3), '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', str(wav)])
    atext = ' '.join(''.join(al['characters']).split())
    print('take', spec, 'ok; alignment==sent:', atext == ' '.join(script.split()), flush=True)
