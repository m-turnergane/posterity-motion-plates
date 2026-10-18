# Cartography v0.2: narration-aware storyboard layer (spec + as-built)

Status: implemented on `feature/cartography-v0.2` (internal PoC tier; **not** production). Owner of historical accuracy: **the Archivist**. Owner of narrative intent: **Vellum**. The renderer checks *structure and legibility*, never historical truth.

## 1. Pipeline and ownership

```
Vellum: narrative intent (what the viewer should understand, per beat)
   -> Archivist: historical verification (claims, sources, confidence, approximate flags)
      -> storyboard YAML (schema 2: events anchored to narration words, each with claim + purpose)
         -> motionplates.cartography check   (static + timing + render-level QC; exit 5 on errors)
            -> render (silent MP4 + VO mux with tail-aware fade) -> manifest (status stays DRAFT)
               -> human playback review (approvals/<mp4_sha256>.json, committed by a person)
```
Nothing in this chain may set `qc.playback_approved`. A clip containing any claim not `VERIFIED` by the Archivist is stamped `INTERNAL_POC_DRAFT_UNVERIFIED_CLAIMS` and the check emits `claims.unverified` (warning). Static plates / the existing static map stay the fallback.

## 2. Storyboard schema (schema: 2)

Top level: `output`, `base` (+`fallback`), `georef`, `vo{alignment,offset_s}`, `limits`, `sources[]`, `claims[]`, `locations{}`, `events[]`.

- `sources[]`: `id, title, url, retrieved, license` (required fields; ids unique).
- `claims[]`: `id, text, band` (`DOCUMENTED | QUALIFIED | UNKNOWN`), `confidence` (`high|medium|low`), `approximate` (bool, mandatory), `sources[]` (ids; **required unless band UNKNOWN**), `status` (`DRAFT | VERIFIED`; only the Archivist flips this).
- `locations`: `{px:[x,y]}` (legacy, warned when the map has a georef) or `{lonlat:[lon,lat]}` (preferred; projected through the georef - no hand-placed city pixels).
- Every event needs: `claim` (id), `purpose` (one line, geographic/historical reason it is on screen) and a **narration anchor** `at: {word, offset?}` (word looked up in the VO alignment JSON; `offset` seconds, default 0). Optional `until` anchor for held items.
- Label `kind`: `geo` (place names), `event` (annotations), `title` (narrative titles). Each has its own treatment (section 4).

## 3. Checks (all return `level, code, message`; errors block `render` with exit 5 unless `--allow-qc-errors`)

| Code | Level | Meaning |
|---|---|---|
| `sources.*`, `claims.*` | error | missing/duplicate ids, bad band/confidence/approximate, unknown source id, DOCUMENTED claim with no source |
| `claims.unverified` | warning | any claim not VERIFIED (clip is DRAFT/internal) |
| `event.claim/purpose/anchor` | error | event lacks claim, purpose or word anchor |
| `label.kind`, `label.until` | error/warn | unknown kind; held label with no end |
| `location.hand_placed` | warning | `px` location on a georeferenced map |
| `anchor.sync` | error | event starts more than the allowed window from its anchor word (default 0.7 s before to 1.0 s after) |
| `time.range` | error | event outside the clip |
| camera overlap / back-to-back | error / warning | two camera moves overlapping; moves with no settle gap |
| `dominant.overlap` | warning | two "dominant" actions (camera move + route reveal) at once |
| `annot.labels`, `annot.simultaneous`, `annot.titles` (+ `max_dominant`) | error | more than `limits.max_labels` (3), `max_annotations` (4) or `max_titles` (1) visible at once (sampled every 0.1 s) |
| `label.safe_area` | error | label leaves the caption-safe region (`safe_x` 5-95 %, `safe_y` 14-78 %) at any sampled time, camera included |
| `label.overlap` | error | two visible labels overlap |
| `route.endpoint` | error | route end outside the map |
| `base.baked_text` | warning | heuristic found baked pins/words in the base map (never proof) |
| `narration.tail` | error | the audio window cuts a word, or the fade-out cannot fit between the last word and the next |

Not checked, by design: whether the claim is true, whether a date is right, whether a border is correct. That is the Archivist's job; the check only guarantees every shown fact is *attached* to a claim with sources and a confidence/approximate flag.

## 4. Visual treatment (replaces the heavy dark plates for schema 2)

| Kind | Look | Used for |
|---|---|---|
| `geo` | small-caps ivory text with a soft dark halo (no plate), tiny label, hairline leader | city / sea / region names |
| `event` | bold ivory line + italic sub-line, same halo, optional chevron/route; no box | annotations ("TO BERLIN", "UZBEK SSR / Soviet Union, 1941") |
| `title` | large ivory serif title, wider halo, top safe zone | narrative titles |

Sizes (px at 1080x1920): geo 36, event 40, title 66 - all >= ~13 px on a 390 px-wide phone. Labels edge-fade (`edge_fade`) near the frame edge instead of popping off. The legacy dark `text_plate` stays only for schema-1 recipes (the original PoC) so old recipes still render identically.

## 5. Narration tail (the truncated-word fix)

`tail_plan(words, offset, dur, margin, fade)` replaces "fade the last 0.35 s of the clip". The VO window must start and end *between* words; the fade-out begins `tail_margin_s` (0.25 s) after the last included word ends and must finish before the next word starts. Violations are `narration.tail` errors, and the manifest stores the plan (`last_word`, `fade_start`, ...). Regression test: `test_old_behaviour_would_truncate_a_word`.

## 6. Limits / not done
- No automated historical truth checking. No effect-library growth. No engine rewrite (the v0.2 layer is additive; schema 1 still works).
- `base.baked_text` is a heuristic; a human still looks at the base at 100 %.
- Georeferencing is approximate (see CARTOGRAPHY-GEOREF-REPORT.md): labels/routes may be shown only as "approximate" on this painted map.
