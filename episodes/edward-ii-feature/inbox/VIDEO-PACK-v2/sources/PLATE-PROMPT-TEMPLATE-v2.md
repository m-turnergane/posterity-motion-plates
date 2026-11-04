# Posterity plate prompt template v2 (OWNER, 2026-10-31 1:40pm ET). HOUSE STANDARD

Supersedes the long-boilerplate and long-avoid-list format in PLATE-PROMPT-BOILERPLATE.md for every future plate.
It's tuned for current image models: describe the scene first, keep it natural and specific, and use only 1–4 shot-specific constraints. No blanket avoid lists.
Only the IMAGE GENERATION block gets pasted to the image model. The ATELIER HANDOFF block is production notes and never goes in the image prompt.
The violence and horror direction from 2026-10-31 still applies: the subject decides how intense the image is.

## Standing instruction (owner, 2026-10-31 1:43pm ET)
Write image prompts like an art director briefing a painter, not an engineer configuring a rendering pipeline. Decide the motion beforehand and build it into the scene naturally, for example by keeping clear space between near and far subjects or painting flames whole. Put the engineering requirements only in the ATELIER HANDOFF. Don't give the owner avoid laundry lists: his image-prompt assistant already has the Posterity context, the info packet and the script. A shot gets constraints only when they really matter.

---

[PLATE ID] — [SHOT NAME]

VO: "[Exact narration being illustrated]"

Narrative purpose: [What the audience should understand or feel when this image appears. One sentence.]

IMAGE GENERATION

Visual identity
Vertical 9:16, full-bleed painterly oil and gouache illustration. Posterity's archival Recovered Chronicle aesthetic: visible brushwork, aged varnish, fine craquelure, historically grounded [period / region] visual language. [Specific palette and atmospheric direction.]

Scene
[Describe the precise frozen moment being depicted: location, characters, actions, expressions, and the important environmental details. Prioritize what is happening rather than listing objects.]

Continuity
[Identify any supplied reference images and exactly what should remain consistent: facial features, clothing, architecture, lighting, established objects or previous shot.]

Composition
[Camera angle, framing, foreground/middle ground/background, focal point, approximate subject placement.]

[For DEPTH plates: explicitly separate NEAR and FAR subjects with clean outlines and sufficient open space for parallax.]

Keep important faces and hands safely within the frame. Preserve a visually calm lower third for captions.

Lighting and animation readiness
[Describe the actual lighting sources and their effect on the scene.]

[Specify which flames, windows, smoke sources, dust shafts, or environmental elements must be painted clearly enough for animation. Include spatial separation where relevant.]

The image is a single coherent, frozen moment. [Specify any lighting or physical movement that must already be painted rather than animated.]

Shot-specific constraints
[Only 1–4 restrictions that materially matter to THIS plate. Omit when unnecessary.]

ATELIER HANDOFF — NOT VISUAL CONTENT

- Motion: [FLAT / DEPTH_v1 / other approved preset]
- Camera: [Push, drift, anchor, zoom range, timing]
- Near layer: [Subjects and boundaries]
- Far layer: [Subjects and boundaries]
- Effects: [Approved FX presets, intensity, placement]
- Masks / protection: [Faces, hands, flames, letters, geography]
- Special handling: [Transitions, matched frames, required continuity, engine limitations]

---

## Reference example (owner, B09 rewritten in the v2 format; format reference only, not a regeneration request)

B09 — The Arrest

VO: "Now his men were arresting her."

Narrative purpose: Báthory's aristocratic composure fractures as armed men enter her home. The audience should feel the sudden loss of control.

IMAGE GENERATION

Vertical 9:16 painterly oil and gouache illustration in Posterity's Recovered Chronicle style. Early seventeenth-century Hungarian manor, visible brush texture, aged varnish, fine craquelure. Historical gothic chiaroscuro, deep shadows, black velvet, candle gold, torch orange and dark oak.

Scene: Inside the same candlelit manor dining room established in B05, Elizabeth Báthory has just risen from supper. Use the attached B01b reference to preserve her face, pearl headdress, lace collar, black velvet gown and gold chain.

Her expression shows restrained alarm beneath aristocratic defiance. Her brows tighten, jaw sets, one hand grips the chair, and her body turns sharply toward the doorway.

Three armed retainers enter through the distant doorway, their fur caps and heavy cloaks silhouetted against orange torchlight. Their swords remain sheathed. The confrontation is tense but not physically violent.

Composition: Medium-wide, eye-level cinematic framing. Báthory dominates the left foreground, with the retainers framed in the upper-right background. A clear stretch of floor separates them for depth animation. A supper table and three-branched candlestick occupy the lower foreground, without obstructing her hands.

Keep her face around 35–42% of frame height, with the lower third relatively calm for captions.

Lighting: The three candle flames and two distant torches are completely visible and sharply defined. Warm light falls across Báthory's face while the soldiers remain largely silhouetted. A bright wedge of torchlight is already painted across the floor toward her.

The entire composition is a frozen instant immediately after the intrusion.

Shot-specific constraints: No physical struggle, no fabricated heraldry, no drawn weapons.

ATELIER HANDOFF

- Motion: DEPTH_v1, 1.00→1.06 push toward the doorway.
- Near: Báthory, chair, foreground table and candlestick.
- Far: Doorway, guards and torches.
- Effects: fx_candle on near candlestick; torch_v1c on distant torches.
- Protection: Faces and hands rigid. Torch spill excluded from faces with 6px padding and 18px feather.
- Technical: Preserve clean depth separation; no crossing silhouettes. The torchlight sweep is painted, not physically animated.
