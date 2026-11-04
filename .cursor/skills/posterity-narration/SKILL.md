---
name: posterity-narration
description: Render approved Oliver Silk narration with timestamps, cache it, and align the timeline. Use when a spoken script is ready or when verifying the voice.
---

# Narration

1. Read `config/narration.yaml`. Do not set `speed`. Do not print `ELEVENLABS_API_KEY`. If the variable is empty, stop and use the cloud secret input. Do not ask for the key in chat.
2. Speak the raw script-vo text, not the display script. Keep pronunciation substitutions out of on-screen captions.
3. Refuse if the text contains an OPEN claim that STATUS says must stay out.
4. One setup line is allowed. A feature pass must stay under `config/budget.yaml` `elevenlabs.ask_before_credits` or stop for approval. Record characters and the returned request id.
5. Call text-to-speech with timestamps. Cache the audio and the alignment next to the script hash. A script change invalidates only the segments whose text changed.
6. Build the timeline from the alignment. Do not time-stretch the whole read to a pre-cut picture.
