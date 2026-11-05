# Posterity playbook

Working summary for production. The desk files in `intake/atelier-jr-2026-11-04/` are the source. This page does not add approvals.

## Identity

Posterity is an existing history channel. The public name on the current YouTube handle is Posterity Archive. The form is Recovered Chronicle: a narrated story told with painterly scenes, purposeful geography, evidence the viewer can see, and motion that has a job. It is not a trivia list and not a glossy reconstruction presented as a photograph.

Last published Short in the desk record: #34 Björn, "Wrong Rome, Wrong Viking? The Coffin Trick", 3 Nov 2026. The active job after this setup is the Edward II / Edmund of Kent feature, native 16:9. The Edward Short (#31, "The Letter to a Dead King") is a different film.

## Story

Grip in the opening seconds with a situation, contradiction, or question. Name who wants what, what stops them, and what their choice changes. A new fact has to change the situation. A map earns its place by making an action or a constraint readable. The ending answers the opening promise or leaves the exact uncertainty the evidence supports.

Reference, not a template: Edward Short #31 is the desk's best-hook example (a concrete contradiction in the first seconds). Ugarit v1c-B5 is the weak opening (the first line names nothing concrete). Björn v2b → v4d is the worked correction for map pace, water, title, and score. Croatoan Ch III is the desk's payoff example. Those judgments are in `05-reference-renders-and-owner-feedback/REFERENCE-PICKS.md`.

## Evidence

Separate documented events, contemporary reports, later accounts, disputed readings, legend, and visual reconstruction. A claim ledger links lines to sources and status. Six Edward claim IDs stay out of narration until the ledger file arrives: C02e, C11, C14b, C15, C16e, C17. Do not invent their wording. Quotations keep their attribution. Reconstructions look like paintings, not like recovered photographs. No status stamp and no "ILLUSTRATIVE RECONSTRUCTION" line on screen.

## Art

Painterly gouache, tempera, fresco, or engraving. Visible surface, readable depth, period-coherent clothes and objects, the same person and place when they return. Masters are unlettered. The engine adds titles, labels, and captions. Palette foundations are parchment, charcoal, bronze, and chiaroscuro. Accent hex by episode is unknown. Prompt law is template v2: scene first, one to four constraints, no blanket avoid list.

16:9 masters are generated or outpainted for 16:9. A 941×1672 Short plate cropped into 1920×1080 is 2.04 output pixels per source pixel. The guardrail refuses anything over 1.5. Do not do that crop.

## Maps

The owner paints terrain, coast, parchment, and realm color. Routes, labels, markers, and highlights are editor layers registered to geodata. Ink: continuous for documented, broken or lighter for reported, shaded for approximate. Procedural base maps are not approved. Procedural Edward maps from 30 Oct are superseded research. There is no owner-painted Edward atlas plate yet.

## Narration and sound

Voice is Oliver Silk, `jfIS2w2yJi0grJZPyEsk`. Model `eleven_multilingual_v2`. Settings and the unknown speed are in `config/narration.yaml`. Spoken text and on-screen text stay separate. Timing follows the recording. Do not stretch a read to a picture duration chosen first.

Delivery loudness is −14 LUFS integrated and true peak at or under −1 dBTP. Long-form picture stays clean. Captions are SRT or VTT, selectable, not burned. Music may be as many as three related sections. Gregorian Chant is not approved for the feature. Score restarts were an owner complaint on Björn; one continuous bed is the correction on that Short.

## Editing and motion

Choose per shot. Deterministic moves (crop, the locked push, parallax, titles, routes, document masks) when the painting should hold. Generative video only when the shot needs new physical motion. Every lit plate gets a locked flicker preset. A plain push does not satisfy that rule. depth_v1 stays off. Faces, hands, geography, text, and evidence objects are protected. Frame 0 of a motion render matches the plate in the motion-plates engine. If a motion file is missing or fails QC, the still plate is the fallback.

## Owner judgment

The owner approves the export file by name and md5, not a preview, and posts it. The agent does not publish. One compact style/motion sample precedes the main Higgsfield spend, then one full review cut, not a plate-by-plate approval loop. Specialists do not message the owner directly. Material creative conflicts get one recommendation and a stop.
