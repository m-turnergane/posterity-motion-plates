# audio/

Audio is built per episode; there is no shared audio module yet. Where the code lives:

- VO generation (ElevenLabs text-to-speech with-timestamps API): `examples/bjorn/rough_v4/vo/render_vo_bjorn_v4.py`, and the same pattern in `examples/{edward-ii,jianwen,germanicus,bathory}/**/render_vo_*.py`. The API key comes from the `ELEVENLABS_API_KEY` environment variable. Never commit it.
- Mixing (VO + score bed, sidechain duck, bus compression, loudness): `examples/bjorn/rough_v4/build/mix_bjorn_v4d.py` (latest), plus `mix_bjorn_v4.py` and `mix_bjorn_v4b.py`.
- Music source register: `music-sources-2026-10-16.md`.

Stems, WAVs and MP3s are not in git. See ATELIER-ENGINE-NOTES.md (handoff pack) for their locations.
