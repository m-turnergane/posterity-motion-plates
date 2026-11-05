# Pipeline test, 4 Nov 2026

Synthetic. Not the Edward film and not the 03:05–04:55 sample. Higgsfield was not called.

| Item | Result |
| --- | --- |
| File | `var/pipeline-test/pipeline-test.mp4` (gitignored; this disk) |
| md5 | `1e7f9ba4450ec64d61666ef15ba6f2d8` |
| Picture | H.264 High, yuv420p, 1920×1080, 30 fps, 180 frames, 6.000 s |
| Audio | AAC, 48 kHz, stereo. One Oliver Silk line, 70 characters, synthesized once at about 12:13 PM America/Toronto and reused for the encode. Spoken text: "This is a technical test of the archive voice. No story is being told." Silence is padded to the picture length. |
| Loudness | Integrated −14.1 LUFS. True peak −3.6 dBFS. Two-pass loudnorm to −14 LUFS / −1.5 dBTP, then +0.8 dB because the short line landed quiet and the peak had room. |
| Captions | Sidecar only, not burned. Three cues from the timestamp alignment, 0.000–5.480 s. |
| Push | Scale-only, geometric, 1.00→1.06, center. House `check_pixel_density` on a native 1920×1080 plate passed at ratio 1.06. |
| Title | PIL stand-in, "TECHNICAL TEST", first 2 seconds, colors from the title spec. Chronicle Reveal was not rendered: `ChronicleHookV3-2b` is 1080×1920 and its default plate is not in the bundle. |
| Frames looked at | Start (title band on), middle (title gone, arch larger), end (arch larger again). No black frames. The arch and the floor bar stay in place and grow with the push. |
| Build template `--check` | Fails. `templates/build_template_v1.py` still loads `/guardrails.py` at the repo root. Not retargeted. |

Rebuild: `python tools/assemble_pipeline_test.py` with the venv. It calls ElevenLabs when `ELEVENLABS_API_KEY` is set. `PIPELINE_REUSE_VOICE=1` keeps the saved line and does not call again.
