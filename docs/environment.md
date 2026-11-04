# Environment

Recorded 4 Nov 2026, America/Toronto, on the cloud agent for `m-turnergane/posterity-motion-plates`.

## Machine

| Tool | Seen here |
| --- | --- |
| OS | Linux |
| Python | 3.12.3. Project venv at `.venv` after `python3.12-venv` and `pip install -r requirements.txt` |
| ffmpeg / ffprobe | 6.1.1 |
| Node | v22.23.4 |
| CPU | 4 |
| Disk | about 246 GB free on `/` at session start |
| Memory | 15 GB |
| Egress | unrestricted on this run |
| GitHub | `gh` authenticated for this repo. Engine PR: https://github.com/m-turnergane/posterity-motion-plates/pull/5 |

## Secrets

Names only.

| Name | State |
| --- | --- |
| `ELEVENLABS_API_KEY` | A value is present. ElevenLabs returned 400 `api_key_id_used_as_api_key` on 4 Nov 2026. The stored value is a key ID. A replacement `sk_` key was requested through the secret input. The value is not in the repo. |
| Higgsfield | MCP session is signed in. No API key is stored in the repo. Re-read during this session: Plus, 110 credits. No generation. |

## Providers

| Provider | Use | Auth |
| --- | --- | --- |
| Higgsfield MCP `https://mcp.higgsfield.ai/mcp` | Images and generative video, plan credits only | Connected for read queries. Generation blocked until a cap exists |
| ElevenLabs | Narration with timestamps | Secret name above |
| Remotion 4.0.529 | Chronicle Reveal on the engine branch | Not installed this session. Composition is 1080×1920 and its default plate file is absent |
| Google Drive | Plate archive `1oSSP805SIUXEVhGBA7ytg3vkcpegHR9w`, video dump `11_Rx49M2UUJByXAsZOwUFUjIpD45ncy_`, handoff zips in folder `109Cx5eBBjNwk2uokRHu5_H00ZqyKSC07` | Connected. `download_file` caps at 10 MB, so MEDIA-01 through MEDIA-07 were not retrieved |

## Storage

Text originals: `intake/atelier-jr-2026-11-04/`. Large media stays out of git (`*.mp4`, `*.png` already ignored, plus `var/`). Pipeline test artifacts: `var/pipeline-test/` on this machine, with checksums committed under `episodes/edward-ii-feature/pipeline-test/`. That directory is the retrieval path for a later session on this same disk. It is not a second git remote.

## Renderer

Two trees:

- This branch: `src/motionplates`, Python, synthetic tests, portrait PoC recipes. Unchanged.
- Engine branch: `engine/`, `fx/`, `templates/build_template_v1.py`, `titles/remotion-posterity-motion`, `fonts/ofl/`. Worktree used for checks: `/tmp/engine-wt` at `1cf564e`.
