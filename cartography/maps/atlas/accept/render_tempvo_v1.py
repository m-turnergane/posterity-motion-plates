#!/usr/bin/env python3
"""TEMP VO for the Chronicle Atlas acceptance test, Part 2 (2b continental jump).  NOT FOR PUBLICATION -- placeholder narration.
Voice/settings copied verbatim from standalones/edward-ii/vo/render_vo_edward_ii_v3b.py (final v3b = take t1, seed 11):
Oliver jfIS2w2yJi0grJZPyEsk, eleven_multilingual_v2, stability 0.5, similarity_boost 0.75, style 0.0, use_speaker_boost true,
default speed, /with-timestamps, mp3_44100_128, same next_text (anti-wind-down, not spoken).  previous_text = v3b L15 for
prosodic continuity (context only, not spoken).  Lines: CLAIM-LEDGER-v1 C03a order + DECISION-PACKET-v1 ch.6, every line
attributed to the letter.  Key: env ELEVENLABS_API_KEY (as the v3b build).  Refuses overwrite."""
import base64, json, os, subprocess, urllib.request
from pathlib import Path
OUT = Path(__file__).resolve().parent / "audio"
VOICE = 'jfIS2w2yJi0grJZPyEsk'; MODEL = 'eleven_multilingual_v2'; SEED = 11
SETTINGS = {'stability': 0.5, 'similarity_boost': 0.75, 'style': 0.0, 'use_speaker_boost': True}
NEXT = 'Tomorrow, we open another forgotten page of history, and we follow the people who lived it.'
PREV = 'Most historians believe Edward died at Berkeley.'
LINES = ["According to Fieschi's letter, Edward then crossed to Ireland, and came back to England as a hermit, landing at Sandwich.",
         "The letter says he crossed the sea at Sluys, then went through Normandy and Languedoc to Avignon, where the pope kept him more than fifteen days.",
         "From there, it claims, he went by Paris, Brabant and Cologne, and across Germany to Milan."]
text = ' '.join(LINES)
mp3, wav, aln = OUT / 'edward_atlas_TEMPVO_v1_oliver.mp3', OUT / 'edward_atlas_TEMPVO_v1_oliver.wav', OUT / 'edward_atlas_TEMPVO_v1_oliver_alignment.json'
for p in (mp3, wav, aln):
    if p.exists(): raise SystemExit(f'refusing overwrite {p}')
body = {'model_id': MODEL, 'seed': SEED, 'text': text, 'voice_settings': SETTINGS, 'next_text': NEXT, 'previous_text': PREV}
req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128', data=json.dumps(body).encode(),
                             headers={'xi-api-key': os.environ['ELEVENLABS_API_KEY'], 'Content-Type': 'application/json', 'Accept': 'application/json'})
r = json.loads(urllib.request.urlopen(req, timeout=600).read())
mp3.write_bytes(base64.b64decode(r['audio_base64'])); al = r['alignment']
json.dump({**{k: al[k] for k in ('characters', 'character_start_times_seconds', 'character_end_times_seconds')}, 'temp_vo': True, 'lines': LINES, 'seed': SEED,
           'voice_settings': SETTINGS, 'model': MODEL, 'voice': VOICE, 'voice_name': 'Oliver', 'next_text': NEXT, 'previous_text': PREV, 'text_sent': text, 'speed': 'default'}, open(aln, 'w'), indent=1)
subprocess.check_call(['ffmpeg', '-v', 'error', '-n', '-i', str(mp3), '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', str(wav)])
print('ok; alignment==sent:', ' '.join(''.join(al['characters']).split()) == ' '.join(text.split()))
