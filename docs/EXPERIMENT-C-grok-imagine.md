# Experiment C — Grok Imagine character gesture (SKIPPED by owner; no cost incurred)

Status: **skipped by owner decision** (no xAI API key is coming). Kept on file only; nothing was generated and **it must never be integrated automatically**.

## Prompt (verbatim)
"Painterly historical illustration brought subtly to life. Augustus's outstretched hand slowly opens and lets a few flower petals drift down toward the covered bier, a small restrained arm and hand movement only. Keep his face, clothing, the sarcophagus, architecture, painting style and composition exactly as in the image. Braziers flicker gently, banners sway very slightly. Camera is locked off, no zoom, no shake, no cuts, no new objects or people."

## Input plate
`day20/alexander-corpse/plates/seq07b_augustus_flowers_crown_OWNER.png` (941x1672 source; read-only, never copied into this repo).

## Settings (if a key ever exists)
- Mode: image-to-video, aspect 9:16, duration 5 s.
- Native 1080p via the xAI API, model `grok-imagine-video-1.5`, when a key exists.
- The in-tool route (GenerateVideo) is 480p/720p only and cannot read box files, so it is not suitable for production-resolution trials.

## QC checklist — REJECT the clip if any of these is true
1. Identity drift: Augustus's face, hair, laurel, clothing, the sarcophagus/bier, architecture or overall composition differs from the plate.
2. Unnatural anatomy: hand/finger count or shape changes, arm length changes, limb warping, melting.
3. Excessive camera motion: any zoom, pan, shake, parallax beyond a few percent, or cuts.
4. Change to the painting's character: photoreal/CG look, style shift, colour grade shift, texture loss, flicker of the whole image.
5. Invented action beyond flowers and the golden crown: new objects/people, extra gestures, text, extra fire/smoke effects.
6. Frame 0 is not (very close to) the plate.

Never integrate automatically: every clip needs a human review against this list and a stored copy of the output + request log; the original still plate stays the automatic fallback. Deterministic lane (this repo's Python engine) is the default.
