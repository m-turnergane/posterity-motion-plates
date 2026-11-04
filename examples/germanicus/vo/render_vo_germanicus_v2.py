#!/usr/bin/env python3
"""Germanicus v2 VO (owner script v3, 13 lines) - copy of render_vo_germanicus_v1.py; changes: script = raw/script-vo-OWNER-v3.txt with
<break time="0.9s"/> inserted before L13 "But not for murder." (per raw/script-vo-tts-v3-break.txt). ONE request for the whole script (never spliced, not sped up).
Oliver jfIS2w2yJi0grJZPyEsk, eleven_multilingual_v2, stability 0.5, similarity 0.75, style 0, speaker boost, default speed, /with-timestamps.
Anti-wind-down = API next_text only (not spoken). Key from env ELEVENLABS_API_KEY (never printed). Refuses overwrite.
Usage: render_vo_germanicus_v2.py NAME[:SEED[:BREAK_S]]  (BREAK_S default 0.9; attempt 3 used 0.7 after 0.9 gave 1.17-1.23 s RMS pauses)"""
import base64, json, os, subprocess, sys, urllib.request
from pathlib import Path
ROOT = Path('/workspace/posterity/standalones/germanicus'); OUT = ROOT / 'vo'
VOICE = 'jfIS2w2yJi0grJZPyEsk'; MODEL = 'eleven_multilingual_v2'
SETTINGS = {'stability': 0.5, 'similarity_boost': 0.75, 'style': 0.0, 'use_speaker_boost': True}
NEXT = 'Tomorrow, we open another forgotten page of history, and we follow the people who lived it.'
BREAK = '<break time="0.9s"/>'
LINES = [l.strip() for l in (ROOT / 'raw' / 'script-vo-OWNER-v3.txt').read_text().strip().splitlines() if l.strip()]
assert len(LINES) == 13 and LINES[-1] == 'But not for murder.'
spoken = ' '.join(LINES)
for spec in sys.argv[1:]:
    parts = spec.split(':'); name = parts[0]; seed = int(parts[1]) if len(parts) > 1 else 11
    brk = f'<break time="{parts[2]}s"/>' if len(parts) > 2 else BREAK
    script = ' '.join(LINES[:12]) + ' ' + brk + ' ' + LINES[12]
    mp3 = OUT / f'vo_germanicus_oliver_{name}.mp3'; wav = OUT / f'vo_germanicus_oliver_{name}.wav'; aln = OUT / f'vo_germanicus_oliver_{name}_alignment.json'
    for p in (mp3, wav, aln):
        if p.exists(): raise SystemExit(f'refusing overwrite {p}')
    body = {'model_id': MODEL, 'seed': seed, 'text': script, 'voice_settings': SETTINGS, 'next_text': NEXT}
    req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128', data=json.dumps(body).encode(),
                                 headers={'xi-api-key': os.environ['ELEVENLABS_API_KEY'], 'Content-Type': 'application/json', 'Accept': 'application/json'})
    r = json.loads(urllib.request.urlopen(req, timeout=600).read())
    mp3.write_bytes(base64.b64decode(r['audio_base64'])); al = r['alignment']
    atext = ''.join(al['characters'])
    json.dump({'characters': al['characters'], 'character_start_times_seconds': al['character_start_times_seconds'],
               'character_end_times_seconds': al['character_end_times_seconds'], 'seed': seed, 'voice_settings': SETTINGS, 'model': MODEL, 'voice': VOICE,
               'next_text': NEXT, 'text_sent': script, 'method': 'single full-script request, with-timestamps, SSML break before L13',
               'script': 'raw/script-vo-OWNER-v3.txt + break', 'speed': 'default (no speed-up)'}, open(aln, 'w'), indent=1)
    subprocess.check_call(['ffmpeg', '-v', 'error', '-n', '-i', str(mp3), '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', str(wav)])
    print('take', spec, 'ok; alignment text == script-with-break:', ' '.join(atext.split()) == ' '.join(script.split()),
          '; == spoken:', ' '.join(atext.split()) == spoken, flush=True)
