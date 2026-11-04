#!/usr/bin/env python3
"""Germanicus 'They Found His Name in the Walls' v1 VO (copy of serials/croatoan/ch3/vo/render_vo_croatoan_ch3_v4.py; only paths, script, word count, NEXT changed):
the WHOLE raw/script-vo-tts.txt (146 words, script-final.md LOCKED 26 Oct 5:34pm ET) at natural pace in ONE request per take (never spliced, no added pauses,
not sped up). Oliver jfIS2w2yJi0grJZPyEsk, eleven_multilingual_v2, stability 0.5, similarity 0.75, style 0, speaker boost, /with-timestamps.
Anti-wind-down = API next_text context only (NOT spoken, NOT in the audio). Key from env ELEVENLABS_API_KEY. Refuses overwrite.
Usage: render_vo_germanicus_v1.py NAME[:SEED[:N|-]]   e.g. t1:11:N"""
import base64, json, os, subprocess, sys, urllib.request
from pathlib import Path
ROOT = Path('/workspace/posterity/standalones/germanicus'); OUT = ROOT / 'vo'
VOICE = 'jfIS2w2yJi0grJZPyEsk'; MODEL = 'eleven_multilingual_v2'
SETTINGS = {'stability': 0.5, 'similarity_boost': 0.75, 'style': 0.0, 'use_speaker_boost': True}
NEXT = 'Tomorrow, we open another forgotten page of history, and we follow the people who lived it.'
script = (ROOT / 'raw' / 'script-vo-tts.txt').read_text().strip()
assert len(script.split()) == 146 and script.startswith("Rome's favourite prince") and script.endswith('Murder is not one of them.')
for spec in sys.argv[1:]:
    parts = spec.split(':'); name = parts[0]; seed = int(parts[1]) if len(parts) > 1 else 11; nxt = (parts[2] if len(parts) > 2 else 'N') == 'N'
    mp3 = OUT / f'vo_germanicus_oliver_{name}.mp3'; wav = OUT / f'vo_germanicus_oliver_{name}.wav'; aln = OUT / f'vo_germanicus_oliver_{name}_alignment.json'
    for p in (mp3, wav, aln):
        if p.exists(): raise SystemExit(f'refusing overwrite {p}')
    body = {'model_id': MODEL, 'seed': seed, 'text': script, 'voice_settings': SETTINGS}
    if nxt: body['next_text'] = NEXT
    req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128', data=json.dumps(body).encode(),
                                 headers={'xi-api-key': os.environ['ELEVENLABS_API_KEY'], 'Content-Type': 'application/json', 'Accept': 'application/json'})
    r = json.loads(urllib.request.urlopen(req, timeout=600).read())
    mp3.write_bytes(base64.b64decode(r['audio_base64'])); al = r['alignment']
    assert ' '.join(''.join(al['characters']).split()) == ' '.join(script.split()), 'alignment text != script'
    json.dump({'characters': al['characters'], 'character_start_times_seconds': al['character_start_times_seconds'],
               'character_end_times_seconds': al['character_end_times_seconds'], 'seed': seed, 'voice_settings': SETTINGS, 'model': MODEL, 'voice': VOICE,
               'next_text': NEXT if nxt else None, 'method': 'single full-script request, with-timestamps', 'script': 'raw/script-vo-tts.txt', 'speed': 'default (no speed-up)'}, open(aln, 'w'), indent=1)
    subprocess.check_call(['ffmpeg', '-v', 'error', '-n', '-i', str(mp3), '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', str(wav)])
    print('take', spec, 'ok', flush=True)
