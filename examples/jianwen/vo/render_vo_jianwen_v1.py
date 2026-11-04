#!/usr/bin/env python3
"""Jianwen v1 VO: ONE ElevenLabs request for the whole script (raw/script-vo-tts.txt, md5-locked), incl. the L16 tagline.
Settings copied verbatim from Edward II v3b (edward-ii/vo/render_vo_edward_ii_v3b.py / VO-NOTES.md): Oliver jfIS2w2yJi0grJZPyEsk,
eleven_multilingual_v2, stability 0.5, similarity_boost 0.75, style 0.0, use_speaker_boost true, default speed, /with-timestamps,
mp3_44100_128; next_text anti-wind-down guard (not spoken); SSML break before the tagline. Refuses overwrite.
Usage: render_vo_jianwen_v1.py NAME:SEED[:BREAK_S] ..."""
import base64, json, os, subprocess, sys, urllib.request, hashlib
from pathlib import Path
ROOT = Path('/workspace/posterity/standalones/jianwen'); OUT = ROOT / 'vo'; SCRIPT = ROOT / 'raw' / 'script-vo-tts.txt'
assert hashlib.md5(SCRIPT.read_bytes()).hexdigest() == '3b027865e5549fad6790de43668c6f08', 'script md5 changed'
VOICE = 'jfIS2w2yJi0grJZPyEsk'; MODEL = 'eleven_multilingual_v2'
SETTINGS = {'stability': 0.5, 'similarity_boost': 0.75, 'style': 0.0, 'use_speaker_boost': True}
NEXT = 'Tomorrow, we open another forgotten page of history, and we follow the people who lived it.'
LINES = [l.strip() for l in SCRIPT.read_text().strip().splitlines() if l.strip()]; assert len(LINES) == 16 and LINES[-1].startswith('History remembers')
for spec in sys.argv[1:]:
    parts = spec.split(':'); name = parts[0]; seed = int(parts[1]); brk = parts[2] if len(parts) > 2 else '0.8'
    script = ' '.join(LINES[:15]) + f' <break time="{brk}s"/> ' + LINES[15]
    mp3 = OUT / f'vo_jianwen_oliver_{name}.mp3'; wav = OUT / f'cand-vo-oliver-jianwen-{name}.wav'; aln = OUT / f'cand-vo-oliver-jianwen-{name}_alignment.json'
    for p in (mp3, wav, aln):
        if p.exists(): raise SystemExit(f'refusing overwrite {p}')
    body = {'model_id': MODEL, 'seed': seed, 'text': script, 'voice_settings': SETTINGS, 'next_text': NEXT}
    req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128', data=json.dumps(body).encode(),
                                 headers={'xi-api-key': os.environ['ELEVENLABS_API_KEY'], 'Content-Type': 'application/json', 'Accept': 'application/json'})
    r = json.loads(urllib.request.urlopen(req, timeout=600).read())
    mp3.write_bytes(base64.b64decode(r['audio_base64'])); al = r['alignment']
    json.dump({**{k: al[k] for k in ('characters', 'character_start_times_seconds', 'character_end_times_seconds')}, 'seed': seed, 'voice_settings': SETTINGS, 'model': MODEL,
               'voice': VOICE, 'next_text': NEXT, 'text_sent': script, 'method': 'single full-script request, with-timestamps, SSML break before L16 tagline', 'speed': 'default'}, open(aln, 'w'), indent=1)
    subprocess.check_call(['ffmpeg', '-v', 'error', '-n', '-i', str(mp3), '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', str(wav)])
    atext = ' '.join(''.join(al['characters']).split())
    print('take', spec, 'ok; alignment==sent:', atext == ' '.join(script.split()), flush=True)
