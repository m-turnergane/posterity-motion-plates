# Pipeline test, 4 Nov 2026

Synthetic. Not the Edward film and not the 03:05–04:55 sample. Higgsfield was not called.

| Item | Result |
| --- | --- |
| File | `var/pipeline-test/pipeline-test.mp4` (gitignored; this disk) |
| md5 | `fa37062a5f805d2342b4a9880e8b5574` |
| Picture | H.264 High, yuv420p, 1920×1080, 30 fps, 180 frames, 6.000 s |
| Audio | None. ElevenLabs rejected the stored secret as a key ID (`api_key_id_used_as_api_key`) on the first try and again at 12:07 PM America/Toronto on 4 Nov 2026. The value is 64 hex characters, not an `sk_` secret. No credits recorded. |
| Loudness | Not measured. There is no audio stream. |
| Captions | Sidecar only, not burned. One cue for the on-screen title. |
| Push | Scale-only, geometric, 1.00→1.06, center. House `check_pixel_density` on a native 1920×1080 plate passed at ratio 1.06. |
| Title | PIL stand-in, "TECHNICAL TEST", first 2 seconds, colors from the title spec. Chronicle Reveal was not rendered: `ChronicleHookV3-2b` is 1080×1920 and its default plate is not in the bundle. |
| Frames looked at | Start (title band on), middle (title gone, arch larger), end (arch larger again). No black frames. The arch and the floor bar stay in place and grow with the push. |
| Build template `--check` | Fails. `templates/build_template_v1.py` still loads `/guardrails.py` at the repo root. Not retargeted. |

Rebuild: `python tools/assemble_pipeline_test.py` with the venv. It will mix Oliver only when `ELEVENLABS_API_KEY` is a real `sk_` key.
