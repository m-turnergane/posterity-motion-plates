---
name: posterity-render
description: Assemble a Posterity film, check picture and loudness, and rebuild only the outputs a change invalidates. Use for a sample, a full cut, or a revision.
---

# Render

1. Read `config/delivery.yaml`. Long-form is 1920×1080, 30 fps, stereo, selectable captions, −14 LUFS, true peak ≤ −1 dBTP.
2. Dry-run first. `templates/build_template_v1.py --check` on the engine branch still imports guardrails from the wrong path. If that import fails, report it. Do not claim the check passed.
3. Render with `--size 1920x1080`. Captions are SRT and VTT sidecars, not burned in. One brand outro.
4. Probe streams and measure ebur128. Look at frames. A zero encode exit is not approval.
5. Write the mp4 outside git (`var/` is ignored). Commit the checksum, duration, and known issues under the episode folder.
6. A changed line rebuilds its voice segment and the shots that use it. Accepted assets with the same input hash stay.
7. Do not publish and do not upload to a channel.
