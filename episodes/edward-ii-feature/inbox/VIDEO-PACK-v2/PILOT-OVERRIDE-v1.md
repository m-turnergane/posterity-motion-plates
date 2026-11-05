# PILOT-OVERRIDE v1 — Edward II / Edmund, Earl of Kent (long-form pilot ONLY)

Prepared 2026-11-04 ~12:40pm ET by the desk, per the GPT review (reviews/gpt-2026-11-04/AMENDMENT-REQUEST.md §A, §C) as accepted by Vellum, and the owner's messages of 12:33–12:37pm ET.
Scope: this pilot only. `sources/STANDING-LAW-longform.md` is kept byte-unchanged; where it conflicts with this file it is SUPERSEDED for this pilot. Future episodes revert to house law unless the owner extends this override.

## 1. Precedence
owner messages > PILOT-OVERRIDE-v1.md > 00-README.md (v2) > house law (sources/STANDING-LAW-longform.md and the Atelier Jr handoff bibles) > older docs (v1 pack, packets).

## 2. Authorization (already given — do not ask again)
- Owner directive 2026-11-04 10:38am ET: Atelier Jr (Cursor) is authorized to generate images and video with Higgsfield (Nano Banana Pro for stills; image-to-video) and narration with ElevenLabs.
- Credentials are Atelier Jr's own access, supplied by the owner. None are in this pack.

## 3. Review roles (replaces per-plate KEEP/REDO)
| Stage | Who reviews |
|---|---|
| Every generated still / clip, retries | Atelier Jr, self-review against `required_invariants` (SHOT-LIST v2) |
| Opening sample (primary) and optional Act II sample | Owner (look) + Vellum (editorial note) |
| Rough cut | Owner + Vellum (editorial note) |
| Final | Owner only. Final approval and publishing are the owner's, done manually. |
No per-plate KEEP/REDO round with the owner.

## 4. Production sequence and budget (owner 12:35pm ET; supersedes the 12:33/12:34 rules and §C of the review)
1. **Sample first.** Atelier Jr produces the 1–2 minute draft/style sample (STYLE-SAMPLE.md: primary = the episode OPENING; optional second = the L26–L39 Act II entrance).
2. **Owner gate.** The owner reviews the sample. The full film proceeds only after the owner's go-ahead.
3. **Full film** after the go-ahead. **Full-film budgeting is decided at the go-ahead gate**, not here.
- **No budget constraints for the sample phase.**
- **One guardrail only:** ask the owner before a plan upgrade or anything that would exhaust the account.
- Good practice (not a gate): read the live Higgsfield balance and the model quotes first, keep a simple log of balance / quote / pending jobs, and inventory reusable media (ASSET-TRANSFER-INDEX) before generating. Running one image-to-video test early is recommended so the still slate is shaped by what I2V can do.

## 5. Engine reuse and shot intent
- The engine (repo `posterity-motion-plates`, branch engine/consolidate-2026-11-04, carried as engine.bundle in the Atelier Jr handoff) is reused **selectively**: assembly, maps (ENGINE_ATLAS), titles and cards (ENGINE_CARD, Chronicle Reveal v3.2b, LONGFORM-HOUSE-INTRO), effects (e.g. fx_candle, dust_v1, as named in the handoff ENGINE notes), mix and captions. No rebuild of the old motion presets is required.
- Each shot carries `dramatic_intent`, `required_invariants`, `permitted_action`, `preferred_method` (HIGGSFIELD_I2V | ENGINE_PRESET | ENGINE_ATLAS | ENGINE_CARD | STILL+ENGINE — a suggestion only) and `fallback`. The v1 `motion_brief` is a suggestion; intent and invariants govern.
- Identity, costume, geometry and historical constraints are FIXED. Deliberate physical action (sealing, handing over, reading, seizing, walking) is ALLOWED where `permitted_action` says so.
- Atlas, route and label shots stay deterministic (engine only, geodata is truth).
- Image-to-video TEST CANDIDATES (not an obligation to buy all four): H06 wax seal, H02 Corfe handover, N12 Mortimer reading, H03 Nottingham seizure.
- PLATE-PROMPTS.md carries a ready-to-paste Nano Banana Pro image prompt per plate (the IMAGE GENERATION block). Atelier Jr writes the Higgsfield I2V motion prompts itself from each shot's `dramatic_intent`, `required_invariants` and `permitted_action`.

## 6. House law still in force (non-conflicting)
- Evidence limits; OPEN/blocked claims never as fact — ledger v3: C02e, C11-b, C14b-b, C15, C16e-b, C17-b (CLAIM-LEDGER-v3.md 3238bb7d). C20 disputed: no date on screen.
- No devil visual (L31). Vercelli stays yearless. L65 is a translation, never in quotes on screen. No archive name (C14b-b); no Hérault/Montpellier as an archive.
- Non-graphic violence direction (see each shot's required_invariants).
- One continuous score per act, crossfades on act cards, no dips, no silence.
- On-screen text: place names only (plus the house title/intro, act cards, wordmark and outro tagline).
- House title and the narrated tagline outro over E01 are mandatory.
- No secrets in any file.
- VO: canonical script v2 (raw/script-vo-v2-DRAFT.txt 852babf5). v3 (4e8996e0) is PROPOSED, not approved. No VO edits by Atelier Jr; any VO change voids the countersign.
