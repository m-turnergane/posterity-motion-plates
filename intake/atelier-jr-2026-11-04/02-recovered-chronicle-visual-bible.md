# 02 · Recovered Chronicle visual bible

Tags follow 01: [CURRENT · owner · date/source] / [EPISODE] / [PROVISIONAL] / [SUPERSEDED] / [UNKNOWN].

**Folder contents**
- Verbatim house sources:
  - `02-reference-paintings-and-prompts/HOUSE__art-bible.md`
  - `HOUSE__recovered-chronicle.md`
  - `prompts/HOUSE__PLATE-PROMPT-TEMPLATE-v2.md`
- Curated owner plates (27): `02-reference-paintings-and-prompts/plates/`
- Episode prompt files: `prompts/`
- Every plate on the box is listed in `06-…/ASSET-MANIFEST-all-plates-outros-renders.csv`.
- The owner's Google Drive holds the complete plate and outro archive. Link: **PENDING**, to be supplied by the owner.

## 1. Core look [CURRENT · owner · locked 16 Sep, Aksum reset 19 Sep]
- **The frame.** "Recovered Chronicle / recovered archive". Reconstructions are painterly, tactile and historically material: gouache or tempera archaeological plates on aged fibrous material, illuminated chronicle, fresco, engraving.
  - They are **never** glossy generic photoreal.
- **Three-layer grammar:**
  1. **Evidence:** real surviving material, with provenance verified by the Archivist.
  2. **Reconstruction:** owner-painted plates.
  3. **Editorial graphics:** maps, dates and typography that add information. They never paraphrase the VO.
- **Sequences, not slides.** Plan about 5–7 visual ideas per Short. A storyboard or contact sheet comes before any render, and evidence comes before reconstruction.
- **Prohibited generic-AI shortcuts** unless the story justifies them:
  - fantasy armour, random hooded figures, hero stares
  - ubiquitous torches, magic particles, glowing dust filler
  - generic ruins, impossible architecture
  - orange-teal grade, polished concept art, unmotivated burning cities
- **Also prohibited:**
  - TEMP watermarks, vignettes and letterboxing
  - literal archive props, and fake generated manuscripts or sources (20 Sep)
- **Sound-off test.** Mute the VO and check that the story still reads. This is mandatory before rough escalation.

## 2. Palette
- **Foundations [CURRENT · owner · 16 Sep]:** parchment/bone, charcoal/soot, bronze and deep muted tones. Episode accents are allowed. Use chiaroscuro in reconstructions.
- **Age comes from texture and craft** (grain, pigment wear, ink imperfection), **not from desaturating everything**. **[CURRENT · owner · atlas brief 31 Oct]**
- **Atlas realm pigments:** oxblood for England, royal blue for France, antique gold. Mix is 75/25 political/terrain. **[CURRENT · owner · atlas brief 31 Oct 9:44am]**
- **Title band colours** (Chronicle Reveal v3.2b): #5A1A18 / #3A0E0C / #6E2A1C; title text RGB (243,237,224). **[CURRENT · owner-approved on published Shorts; engine notes §7]**
- **Exact per-episode accent hex values: UNKNOWN.** They live in each episode's prompt file, not in a house table.

## 3. Continuity
- **Continuity record.** Keep one for every recurring person, building, location and object: age, appearance, clothing, armour, architecture, props, geography. **[CURRENT · owner · 16 Sep]**
- **Style frames → Vellum picks → all plates inherit them.** Use image, style or character references; seeds or prompt wording alone are not continuity. **[CURRENT · owner · 16 Sep]**
- **Anchors first.** Generate and approve character anchors before pairs and the remaining shots.
  - Example: `prompts/bjorn__PASTE-ORDER_anchors-first.md`, 3 Nov.
  - **[EPISODE: Björn. Treat it as current practice; it was not filed as house law]**
- **Callbacks reuse a recognisable composition.** Example: Edward's Corfe composition returns for the letter's revelation. **[CURRENT · owner · asset-reuse 19 Sep; Edward v3b 29 Oct]**
- **Long-form continuity references.** All 21 approved Edward Short plates, plus the Kent and older-Edward character blocks. **[PROVISIONAL · DECISION-PACKET-v1 (e), pending owner answer to (i)]**

## 4. Sizes and safe areas
| Format | Output | Plate source | Status |
|---|---|---|---|
| Shorts 9:16 | 1080x1920, 30 fps | Owner plates are about 941x1672 (measured: 22 of 27 curated are 941x1672, the others are within ±2 px; 1 is 1080x1920) | [CURRENT · owner] |
| Long-form 16:9 | 1920x1080, 30 fps, stereo | New owner generations: outpaint to 2976x1674 (0.645 plate px per output px) or regenerate at ≥2560x1440 | Output [CURRENT · owner · law §2]. Plate routes [PROVISIONAL · HERO_16x9_PROMPTS_v1 DRAFT] |

**The 1.5x crop guardrail [CURRENT · law §6/§11]**
- Measure it in output px per plate px.
- A Short plate cropped to 16:9 needs 2.04 px/px, which is over the ~1.72 ceiling. **No Short plate can be reused at 16:9 by cropping.**
- `check_crop_zoom` measures against cover-fit, so it can pass a crop incorrectly. The 16:9 build must also check `output_px_per_plate_px`. This is **[PROPOSED · not yet written]**.

**Safe areas**

*Shorts*
- Captions sit bottom-centre at MarginV 400 (PlayRes 1080x1920), with per-shot overrides: P07 615, P13 860.
- On maps, output y ≥1280 is caption territory.
- The title sits at topPercent 16 by default; Björn used 31.
- Source: engine notes §7–8. **[CURRENT · owner-approved on published Shorts]**

*Long-form*
- The picture stays clean. Subtitles are a selectable CC track (law §10), so no burned-caption safe band applies.
- The atlas brief requires independent camera, labels, marker scale and **safe areas** for 16:9 and for native 9:16 (not a crop).
- Numeric 16:9 title-safe and action-safe margins: **UNKNOWN** (not specified anywhere on the box).

## 5. Unlettered masters
- **Plates carry no baked text.** All text is added by the engine: titles, captions and map place names.
- **Map plates are "clean plates".** No routes, moving icons or narration-dependent labels are baked in. Static geography is fine. Place names are the **only** text on maps. **[CURRENT · owner · atlas brief 31 Oct]**
- **Document surfaces must be illegible and never a real archive image.** This covers the sealed letter, the Nov 1330 roll and the cartulary copy. **[PROVISIONAL · packet (e), rights-risks §2]**
- **No generated fake manuscripts.** **[CURRENT · owner · 20 Sep]**
- **On-screen quotation text** (an "evidence emerges" annotation) breaks the place-names-only rule. It needs owner sign-off before use. **[OPEN · atlas brief]**

## 6. Essential vs flexible
| Essential (do not change without the owner) | Flexible (Atelier's judgement) |
|---|---|
| Painterly Recovered Chronicle medium. Owner generates every plate (law §1/§6) | Per-episode accent palette and lighting motif |
| Character continuity across a film (anchors, references) | Camera move choice within the motion presets |
| Clean, unlettered plates; text only from the engine | Plate count within the budget (30–36 masters per 12 min, law §6) |
| No status labels or IR text on picture (long-form law §1) | Which preset is used on a lit plate (every lit plate gets flicker) |
| Geodata-true maps; place names are the only map text | Map class per episode (Imperial Atlas / Explorer's Chart / Chronicle Artifact). Vellum proposed Explorer's Chart for Edward [PROVISIONAL] |
| Brand outro: wordmark + narrated tagline over a unique background | Outro background subject |

## 7. Plate prompts
- **PLATE-PROMPT-TEMPLATE-v2** **[CURRENT · owner · 31 Oct 1:40pm; standing instruction 1:43pm]**
  - Write like an art director briefing a painter.
  - Scene first, then 1–4 shot-specific constraints, with **no blanket avoid lists**.
  - The owner pastes **only the IMAGE GENERATION block**. The ATELIER HANDOFF block stays separate.
- **Episode prompt files** in `prompts/`:
  - edward-ii v3b, bjorn v2 + p05 atlas, jianwen v2b, germanicus v5, ugarit v3
  - Báthory: only a storyboard with prompts exists; no standalone v2/v3 plate-prompt file
- **Long-form hero prompts** (episode prep, kept outside this package: `/workspace/posterity/longform/edward-ii-feature/prep/HERO_16x9_PROMPTS_v1.md`, 30 Oct) **predate template v2** and use long avoid lists.
  - They must be **rewritten in v2 format** before the owner pastes them.
  - **[PROVISIONAL / DRAFT · pending packet (i) item 1 and gate 4]**
- **Image tooling** (Nano Banana Pro / Higgsfield):
  - There is **no desk record** of which model the owner uses: **UNKNOWN**.
  - Long-form law §6 says "no autonomous image generation and no image API". Any automation plan conflicts with this and needs an **owner decision**.

## 8. Curated plates in this package (why each)
| Episode | Files | Why |
|---|---|---|
| Edward II (#31) | b01 funeral wide with Kent, b10 Corfe handover, b20 Kent seals, p14 Corfe dusk, outro Gloucester dusk | Candle and dusk lighting. Kent continuity. Four of these are the long-form hero sources |
| Björn (#34) | P01, P05 atlas, P06, P13, OUTRO (KEEP) | The map worked example and the v4d plates |
| Báthory (#33) | b01b, b03 atlas clean, b18, outro first light | Gothic chiaroscuro; a clean atlas plate |
| Jianwen (#32) | k01, k08, k17, outro | Night and fire; the single-candle interior |
| Germanicus | seqG, seqR, outro | Crowd and sea action |
| Atahualpa (#28) | p01 hook, p08 payoff, outro | Hook and payoff pair |
| Ugarit (MA2) | p01, p03 map, outro | Map plate. p01 pairs with the weak-opening example in 05 |
| House | AVATAR_LOCKED, BANNER_LOCKED | Brand |

Serial plates (After Troy, Croatoan I–III) and the Dracula and Blackbeard plates are **not on the box**. See the Drive archive (PENDING).
