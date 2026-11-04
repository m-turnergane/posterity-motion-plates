# LONG-FORM HOUSE INTRO + OUTRO — reusable component brief (v1)

Written 2026-11-04 by the desk, following the owner's notes of 12:37, 12:39 and 12:40pm ET. **First use:** Edward II pilot, where the intro is SC01+SC02 and the outro is S099 on E01.
**Status:**
- The owner approved the direction at 12:39pm ET ("loves the long-form intro direction").
- The final look is checked by the owner in the opening sample (DECISION-BUNDLE item 3).
- Not yet rendered.

**Not the Shorts intro.** This is a separate long-form component. It belongs to the same family as the Shorts' Chronicle Reveal v3.2b: the same wordmark, vellum and ink. Chronicle Reveal v3.2b stays unchanged. It is used here only as the fallback.

---

## Part 1 — LONG-FORM INTRO ("Ink Leaf"), 6–8 s, one unbroken move

### 1.1 Primary treatment (owner, 12:39pm ET)
The whole intro is a single shot on the CB1 aged leaf. There is no cut and no second leaf, and the score runs through it continuously. It should feel elegant and unhurried.

| t (s), Edward II timing 7.5 s = SC01 4.5 + SC02 3.0 | Beat |
|---|---|
| 0.0–1.6 | **Ink spill.** Ink blooms and spreads organically across the aged parchment, wicking into the fibres with darker pooling and feathered edges. It flows toward, but never over, the bare type field. |
| 1.2–3.4 | **Wordmark writes itself in.** POSTERITY writes letter by letter along the stroke paths in a smooth, continuous pen-stroke reveal. This is not a fade or a wipe. The ink load is uneven and darkest where a stroke starts. |
| 2.6–4.5 | **Episode title writes in** beneath the wordmark the same way, a touch quicker, smaller and in the same ink. At 4.5 s the title is fully legible: this is the SC01 boundary. |
| 4.5–5.6 | **The leaf settles into the ACT I card.** The ink fully dries and loses its wet sheen. The wordmark and title lift away as the ink sinks back into the vellum: a reverse bleed, not a cross-dissolve. A very slow settle push of 1.00→1.02 over the whole 7.5 s; no new move starts here. |
| 5.0–7.5 | **'ACT I'** alone, centred, stroke-writes into the same field, then holds (no subtitle, ornament or other text: owner DECIDED 12:41pm ET). At 7.5 s the card ends and S007 (L07) begins: the SC02 boundary. |

- **Score:** A1 runs continuously from the cold open. There are no hits, no dip, no silence and no sound-design swell over the music. Ink and pen sound effects are optional, and only if they are very quiet; Atelier Jr may leave them out.
- **Episode-variable:** title text, total length (6–8 s), ink colour (default iron-gall brown/black, with oxblood allowed for the act numeral).
- **Fixed for every episode:** the wordmark, the leaf base family, the ink behaviour and the beat order.

### 1.2 Invariants (must hold in every frame)
1. **Exact wordmark geometry.** The wordmark is rendered from the locked master (§1.5) as a mask or path. Its letterforms, spacing and proportions are never generated, redrawn or warped by any model.
2. **Legible type.** The wordmark, title and act card are each fully readable for at least 1.2 s at 1080p before they leave.
3. **Physical ink.** The ink reads as absorbed into the parchment, not pasted on top of it:
   - multiply blend
   - paper-texture displacement
   - fibre feathering
   - slight uneven pressure
   - wet sheen that dries off
   - no glow, drop shadow or slide
4. **No blotting over the type.** The bloom layer is masked out of the type field plus a margin. No blot, drip or spread ever crosses a letter.
5. The leaf, border and candle light stay rigid and consistent. Only the ink and the slow settle push move.
6. No other on-screen text: no dates, no quotation marks, no claims. Act cards carry ONLY the centred act numeral label (owner, APPROVED 12:41pm ET).

### 1.3 Method (suggestion; Atelier Jr decides)
- **Recommended: deterministic engine (ENGINE_CARD).**
  - Stroke-reveal: trim-path along centreline strokes derived from the master. You can skeletonise the glyph raster or hand-author stroke paths per letter, then dilate and reveal the mask along the path, multiplied with an ink-texture map.
  - Ink bloom: a reaction-diffusion or noise-advected alpha field limited to the bloom zones, composited with multiply onto CB1.
  - Fonts and the master stay pixel-exact.
- **Allowed hybrid.** A Higgsfield I2V pass may be used on the ink bloom only, on a text-free CB1 plate. The engine then composites the stroke-revealed type over the result. Never let a video model draw or animate the letters.

### 1.4 Base plate (template v2; paste only the IMAGE GENERATION block)
The base is the existing **CB1 prompt** in PLATE-PROMPTS.md, unchanged. It already gives a top-down aged leaf with a bare central field and no letters. A dedicated "intro leaf" variant for reuse across episodes:
```
Horizontal 16:9 full-bleed painterly oil and gouache illustration in Posterity's Recovered Chronicle style: visible brushwork, aged varnish, fine craquelure. Old parchment cream and umber, faded iron-gall brown, warm candle gold, warm darkness at the edges.

Scene: A single large leaf of aged vellum lying flat on a dark oak writing desk, seen from directly above, filling almost the whole frame. The leaf is softly cockled, stained and darkened at its edges, with a faint fold crease and a few tiny worm holes. A simple faded double-line border runs inside the edge. The broad central field is bare, clean vellum with faint dry-point ruling.

Composition: Flat, top-down, the leaf centred and square to the frame. The bare central field spans the middle half of the width and about 45% of the height, perfectly clear; the outer margins of the leaf have room for ink to bloom.

Lighting and animation readiness: Warm candlelight from off-frame left with soft falloff to the right and lower edges; a faint sheen on the vellum. One frozen instant.

Shot-specific constraints: No writing, letters, initials, seals, ink blots or marks anywhere on the leaf (the ink and all type are added later).
```

### 1.5 Fonts and assets
| Asset | Status | Notes |
|---|---|---|
| POSTERITY wordmark master (vector or ≥4K alpha PNG) | **MISSING** | No standalone file found on the box. The wordmark exists only baked into the outro plates, e.g. `standalones/edward-ii/plates-v3b/outro_edward_ii_gloucester_dusk_OWNER.png`: spaced Roman capitals with a fine rule and a centre diamond ornament. Its typeface is UNKNOWN. The owner must supply or approve a master, either a trace of the locked outro lettering or the original file. Until then, exact geometry cannot be guaranteed. |
| Title / act-card face | Proposed: Source Serif Pro Semibold | The face Chronicle Reveal v3.2b uses for Shorts titles. It is on the box at the system font path (OFL); OFL.txt is not on the box. |
| Optional engraved capitals | Repo `fonts/ofl/` | IM Fell DW Pica, IM Fell English SC (the map label faces). Atelier Jr records the licence. |
| CB1 leaf | to generate | See §1.4 / PLATE-PROMPTS CB1. |
| Ink texture / bloom maps | engine-generated | Procedural; no stock assets needed. |

### 1.6 Fallback
Chronicle Reveal v3.2b (the engine's ChronicleHookV3-2b, 4.0 s at 30 fps):
- It exists only at 1080x1920. A 16:9 version would need a new composition, which is UNKNOWN effort.
- In that case: SC01 = static CB1 + Chronicle Reveal title; SC02 = engine ink-in 'ACT I' on the same leaf, still with no cut.

### 1.7 Reusable component spec (for future episodes)
- **Inputs:**
  - `title` (string)
  - `act_label` ('ACT I' / 'ACT II' / 'ACT III' only; no subtitle)
  - `duration_s` (6–8; split title/act around 60/40)
  - `leaf_plate` (CB1-family PNG)
  - `ink_color`
  - `seed` (bloom pattern; fixed per episode for re-renders)
- **Outputs:** ProRes/PNG sequence or H.264 per house encode, 16:9 at 1920x1080 or 3840x2160, with no audio (the score is laid in the edit).
- **Wiring:**
  - It replaces the separate title card and ACT I card: one clip spanning both slots.
  - It cuts in hard from the last cold-open shot. A short 0.3–0.5 s dissolve from the cold open into the leaf is allowed, but there is no dip to black.
  - It cuts out to the first Act I shot.

### 1.8 Alternates (short)
- **A. Seal-and-stroke:** a small wax-seal impression lands, and the ink flows out from it into the wordmark strokes. Same invariants, plus: the seal is plain, with no heraldry and no text.
- **B. Quill-light:** no bloom. A slow, single, candle-lit stroke-write of the wordmark, then the title, then the act. This is the quietest version and the closest to Chronicle Reveal.

---

## Part 2 — LONG-FORM OUTRO ("Ink Close"), the matching bookend (owner, 12:40pm ET)

### 2.1 Treatment
- **Background:** the episode's own unique outro painting. For Edward II this is **E01**, the Corfe lane at first light (empty muddy lane, closed gatehouse, keep on the hill, mist lifting, pale gold sky).
- **The scene's own motion:** mist lifting along the slope, and dawn light slowly growing behind the keep.
- **Ink woven through the scene:** this motion is the same ink-on-parchment family. The edges of the frame carry a parchment-edge vignette in which ink blooms and feathers. The mist dissolves into ink-wash wisps at its edges, so ink and mist read as one substance. No ink ever touches the castle silhouette or the wordmark field.
- **Wordmark:** POSTERITY writes in over the calm middle band of sky and mist with the same smooth pen-stroke reveal as the intro. The fine rule and diamond ornament draw in beneath it as one stroke. This bookends the opening.
- **Tagline:** the narrator reads the standard house tagline verbatim: **"History remembers the victors. We remember the rest."**
  - Source: the house outro docs. Atelier Jr handoff 00-index §2 "Locked: POSTERITY wordmark + narrated tagline"; the baked outro plates; script v2 L98.
  - The tagline is narrated, after the house `<break time="0.8s"/>`, and is not shown on screen. The Shorts outro bakes it into the plate; the long-form house rule is no captions on the outro. Owner look: whether to also stroke-write the tagline beneath the rule, which is a DECISION-BUNDLE item.
- **Score:** A3 runs continuously to a final fade to black at the very end. There is no dip before it.

| t (s), proposed S099 9.5 s (v1 had 3.3 s) | Beat |
|---|---|
| 0.0–1.5 | E01 in. Mist rises; ink feathers in from the frame edges. |
| 1.0–3.8 | The wordmark writes in by pen stroke; the rule and diamond follow. |
| ~3.8–7.4 | Tagline VO, L98: about 3.3 s plus the 0.8 s break. Re-time this to the recorded VO. |
| 7.4–9.5 | Hold. The light grows. The score fades to black, with picture and music ending together. |

### 2.2 Invariants
- Exact wordmark geometry from the same master (MISSING: see §1.5).
- Corfe geometry matches N10, H02 and H04. The lane stays empty: no figures.
- The ink reads as physical (feathered, absorbed). There is no ink over the wordmark or the castle.
- The wordmark is legible for at least 3 s.
- No on-screen text other than the wordmark (plus the tagline only if the owner picks it).

### 2.3 Method
- **Recommended:** a still E01 plus the engine, i.e. a house outro push.
  - Bathory v3c used a push of 1.00→1.06. This pack uses 1.00→1.03 per the editing bible.
  - Add mist as an alpha layer advected upward, with ink-edge feathering, plus the stroke-reveal wordmark.
- **Allowed:** Higgsfield I2V for the mist and light only, on a text-free E01. The engine composites the wordmark.

### 2.4 Fallback
The static house outro: a plate push with dust_v1 and the wordmark ink-in (Bathory v3c builder in the engine repo), with the narrated tagline.

### 2.5 Reusable component spec
- **Inputs:**
  - `outro_plate` (episode-unique, text-free, with a calm middle band)
  - `scene_motion` (mist | candle | water | banners | snow …, chosen to suit the painting)
  - `ink_edge_zones`, `protect_zones` (silhouette, wordmark field)
  - `duration_s` (8–10)
  - `tagline_vo_tc`
- Same wordmark master and ink engine as Part 1, so intro and outro always match.

---

## Wiring in this pack
- **SHOT-LIST SC01+SC02:** `preferred_method` ENGINE_CARD (LONGFORM-HOUSE-INTRO), one continuous clip of 7.5 s.
- **SHOT-LIST S099:**
  - LONGFORM-HOUSE-OUTRO on E01, 9.5 s (estimate)
  - the film total becomes about 735.2 s
- **PLATE-PROMPTS:** CB1 and E01 are updated, and the H06 Chronicle Reveal line is removed.
- **STYLE-SAMPLE:** the opening sample uses the intro.

## Act cards SC02–SC04 (owner DECIDED 12:41pm ET)
Every act card is the same blank aged-parchment CB1 leaf as the intro/outro, with ONLY 'ACT I' / 'ACT II' / 'ACT III' centred, stroke-written in the same smooth ink pen-stroke motion. No subtitles, no ornaments, no extra text. SC02 is the tail of the intro move; SC03 (ACT II) and SC04 (ACT III) are standalone ~3.5 s leaf cards using the same component with `title`=none and no wordmark (ink bloom optional and minimal), with the act crossfade (A1→A2, A2→A3) across the card.
