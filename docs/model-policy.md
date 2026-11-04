# Model policy

Discover ids and prices at call time. Do not hardcode a credit price from the November screenshots in the handoff. Those screenshots are not a quote.

## Routing

| Job | Route | Status |
| --- | --- | --- |
| Plate stills for this long-form experiment | Higgsfield MCP, plan credits, after a cap and a named model | Blocked. Nano Banana Pro is a candidate, not a lock |
| Generative motion (cloth, water that must move, gesture, weather) | Higgsfield video models, shot by shot, after the still is accepted | Blocked with the same cap |
| Held paintings, push, titles, maps, document reveals | Deterministic engine. Locked presets only. depth_v1 off | Allowed without Higgsfield |
| Narration | ElevenLabs `eleven_multilingual_v2`, Oliver Silk | Allowed inside the 30,000 credit ask-first cap once the secret is set |
| Agent reasoning | The session model | Not a generation charge. Do not poll job status with a fresh reasoning turn |
| Developer API for Higgsfield | Do not use | Separate billing route. Not authorized |

## Spend rules

- Higgsfield balance is not a cap. With no cap in `config/budget.yaml`, generation count is zero.
- ElevenLabs: record characters per call. Stop and ask before the running draft total would pass about 30,000 credits. One short setup line does not need a fresh ask.
- Do not buy a plan, add credits, or turn on auto top-up.
- Cache by input hash. A timeout resumes the saved job id. It does not submit a second job.
- The lead owns the ledger. A subagent does not submit paid work.

## Acceptance

An API success is not an accepted take. Picture review checks identity, anatomy, text, geography, and paint surface at the start, middle, and end. Motion review uses the QC rules already in this repo for deterministic renders. Feature plates wait for gate 4.
