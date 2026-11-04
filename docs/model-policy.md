# Model policy

Discover ids and prices at call time. Do not hardcode a credit price from the November screenshots in the handoff. Those screenshots are not a quote.

## Routing

| Job | Route | Status |
| --- | --- | --- |
| Plate stills for this long-form experiment | Higgsfield MCP, model `nano_banana_pro` | Sample phase is authorized and the reference hold is cleared. Name `nano_banana_pro` on the call. The MCP general default is `gpt_image_2_5` |
| Opening test-two replacement stills | Higgsfield MCP, model `gpt_image_2_5` | This pass only, and only after a numeric cap. Quote on 4 Nov 2026 at 3:49 PM America/Toronto: 16:9, quality `high`, resolution `2k`, 2.75 credits. A 4k high still was 4.25. `use_unlim` false. Changing the still model does not repair an accepted clip |
| Generative motion (cloth, water that must move, gesture, weather) | Higgsfield video, after the still is accepted | One Seedance 2.5 clip was spent on the accepted H06 still. I2V prompts come from each shot's intent, invariants, and permitted action |
| Held paintings, push, titles, document reveals | Deterministic engine. depth_v1 off | Allowed without Higgsfield |
| Maps | Engine routes, labels, and markers on a registered plate | Owner rule, 12:44 PM America/Toronto. I2V never draws routes, labels, or markers. An atmosphere layer under those engine layers is an optional test |
| Narration | ElevenLabs `eleven_multilingual_v2`, Oliver Silk | Allowed inside the 30,000 credit ask-first cap once the secret is set |
| Agent reasoning | The session model | Not a generation charge. Do not poll job status with a fresh reasoning turn |
| Developer API for Higgsfield | Do not use | Separate billing route. Not authorized |

## Spend rules

- Higgsfield balance is not a cap. The sample phase has no numeric cap. Ask before a plan upgrade or any spend that would exhaust the account. The opening pass left 48 credits. A reread at 3:49 PM America/Toronto was still 48, and test two has spent 0. A model's `supports_unlim` flag and a website Unlimited label do not make an MCP call free when `unlim.available` is false.
- ElevenLabs: record characters per call. Stop and ask before the running draft total would pass about 30,000 credits. One short setup line does not need a fresh ask.
- Do not buy a plan, add credits, or turn on auto top-up.
- Cache by input hash. A timeout resumes the saved job id. It does not submit a second job.
- The lead owns the ledger. A subagent does not submit paid work.

## Acceptance

An API success is not an accepted take. Picture review checks identity, anatomy, text, geography, and paint surface at the start, middle, and end. Motion review uses the QC rules already in this repo for deterministic renders. Feature plates wait for gate 4.
