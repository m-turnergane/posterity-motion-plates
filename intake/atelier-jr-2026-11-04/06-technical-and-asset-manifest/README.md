# 06 · Technical and asset manifest

| File | What it is |
|---|---|
| **`ATELIER-ENGINE-NOTES.md`** (by Atelier; final md5 `8153662a47619da59a42ac794c4aa0af`) | **Authoritative** for the repo, commit, branch, environment, commands, fonts, the map registration pipeline, locked presets, title/outro, captions, the ElevenLabs settings and the audio chain. **It opens with "FIRST TASK: push the engine". Do that first.** |
| **`engine.bundle`** (md5 `5e8a9c2940bb02aea54e5e9d958600c7`, 6,444,170 bytes) | A git bundle of the engine. Branch `engine/consolidate-2026-11-04`, SHA `c3a192dd240bd9c201a4eb7fa2e4abdd982be357`. Target is the existing **private** repo https://github.com/m-turnergane/posterity-motion-plates. **NOT pushed yet.** The owner decided Atelier Jr pushes it from the bundle as its first task. For repo and commit details, see ATELIER-ENGINE-NOTES.md |
| `ASSET-MANIFEST-all-plates-outros-renders.csv` | Every plate, outro plate/clip, final render, other render and engine R&D reel found on the box (box_path, bytes, md5, width, height, duration_s, mtime_et, note). The originals are about 9.4 GB and stay on the box |
| `PACKAGE-CHECKSUMS.csv` | md5 of every file inside this handoff package |
| `rights/` | Music sources and per-episode credits: "Uprising" and "Anabasis I" (Scott Buckley, CC BY 4.0); "Gregorian Chant" (Kevin MacLeod, CC BY 4.0, Edward Short) |

## Complete plate and outro archive
**The owner's Google Drive folder** backs up every plate and every unique outro. Link: **PENDING** (owner to supply). Treat it as the complete archive; the box manifest is partial.

## Missing from the box (get from the Drive or the owner)
- Dracula v3.2 master (ledger md5 c5ebf8ed…)
- Blackbeard v1 master (e942e947…)
- Croatoan Ch I and Ch II masters
- After Troy Ch1 and Ch3 masters
- All serial plates (After Troy, Croatoan). The cause is UNKNOWN
- Owner-painted Edward atlas plate and any feature plates: none exist on the box

## Credentials
- None are included. Keys are read from the environment (for example `ELEVENLABS_API_KEY`, per the engine notes).
- A grep of the package for key patterns found nothing.
- Atelier Jr needs its own access to ElevenLabs, GitHub (push to the private repo) and Higgsfield. The owner provides these.
