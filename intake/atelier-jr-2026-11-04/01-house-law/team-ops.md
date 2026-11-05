# Posterity Desk — team ops
EIC: **Vellum** (id 2801856)
Channel: **Posterity Desk**

## Specialists
| Bot | Id | Owns | Hands off to |
|-----|-----|------|----------------|
| Archivist | 2972944 | Discovery, scoring, fact-check, source records | Scriptor (pack) + Vellum (selection) |
| Scriptor | 2972950 | VO script, hooks, titles/captions/thumb copy | Atelier |
| Atelier | 2972958 | VO, visuals, edit, QA, masters | Vellum (rough cut for user) |
| Pulse | 2972961 | Analytics, ledger, growth hypotheses, promo flags | Vellum (briefs) |
| Examiner | 0eac0731-80d5-48d4-85e6-c4b7801100a0 | Story context & rough-cut review after Rough v1 | Vellum (adjudication) |

## Daily loop (1 short/day)
1. **Pulse** — morning metrics → Desk + Vellum
2. **Archivist** — discovery + scored shortlist → Vellum selects
3. **Archivist** — deep pack on greenlit story → **Scriptor**
4. **Scriptor** — script + metadata package → **Atelier**
5. **Atelier** — Rough Cut v1 → **Examiner** → **Vellum** adjudication → accepted patches → Rough Cut v2 → **Vellum** → **user** (approval gate)
6. User notes → Vellum updates edit-preferences.md → route patches (may re-run Examiner) → **Atelier** revises if needed
7. User greenlight → **Atelier** publish YT→TikTok→IG (or Vellum publishes) → **Pulse** logs experiment
8. **Pulse** — EOD analytics → Vellum → user

## Rules
- One owner per stage; no duplicate research/script/produce.
- Specialists talk on Posterity Desk; user is not the router.
- Vellum escalates: approvals, credentials, spend, strategy, unusual risk.
- Until full-auto: never publish without user rough-cut OK.
- Shared files under `/workspace/posterity/` (ledger, dayN folders, growth-strategy, edit-preferences).

## Editorial ownership
**Vellum owns content direction** for YouTube/TikTok/IG: story selection, lane mix, growth hypotheses, and what ships. Phase A is exploratory by design (learn what sticks). Specialists advise with research/scripts/production/analytics; they do not override EIC selection. Owner (Muhammad) gates rough-cut quality, credentials, spend, and strategy — not daily topic picks.

## Publish account gate (HARD — 2026-09-14 owner)
- YouTube Studio must be on **Posterity** channel (@PosterityArchive), signed in as `posterity.codex@gmail.com` — NEVER the owner’s personal Google/YouTube account.
- Before upload: confirm account switcher shows Posterity / Posterity Archive. If personal account is active, switch first; do not start upload.
- TikTok: `@posterity.archive` only. Instagram: `@posterityarchive` only.
- “Verify it’s you” after a wrong-account session often means the wrong profile was selected — treat as account-check failure, not just 2FA.

## Owner review window (HARD — 2026-09-14)
- Rough cuts are for the **6am America/New_York** daily loop review — not evening/same-day rush.
- Desk may pre-produce research/script/rough overnight; **do not surface rough cuts to the owner for review until morning** unless owner explicitly asks.
- Evening: finish same-day publish chain + analytics; prep next day quietly.

## Analytics cadence (owner 2026-09-14)
- **Once daily at 6am ET** with rough-cut review. 10pm digest **cancelled**.
- Pulse may research growth ideas overnight and brief Vellum (Desk OK) without owner pings; owner-facing analytics land in the 6am pack only.

## Pulse analysis scope (owner 2026-09-14)
**Own accounts:** YT/TT/IG metrics, retention, distribution diagnoses, monetization distance, packaging/cadence, promo flags.
**Competitive (NEW):** overnight peer scan of faceless history/facts Shorts channels — thumbs, titles, topics, length, captions/engagement patterns — brief to Vellum before 6am; Vellum folds into editorial. Tools: VidIQ/TubeBuddy if free/installable, else public YT signals. No paid sub without owner OK.

## Creative production — Recovered Chronicle (HARD 2026-09-16)
Source of truth: `/workspace/posterity/brand/recovered-chronicle.md` + Art Bible.

**Handoffs change (next cycle onward):**
1. Archivist: fact-pack + evidence assets (provenance/rights) + reconstruction constraints
2. Scriptor: VO + **visual beat sheet** (with Archivist) before Atelier edits
3. Atelier: ~3 style frames → Vellum picks → full assets inherit; continuity record; sound-off QA; System E; IGSAFE
4. Pulse: name **one** primary experimental variable per upload when practical; Engaged/stay/AVD gates for densify

**Day 4 Zimbabwe:** hardening pass only (not full upstream redesign). No publish without Vellum→owner rough OK.

## Pulse experiment labeling (2026-09-16)
Tag each upload **controlled test** (one primary variable) or **exploratory package** (multiple variables → hypotheses only). Day 4 Zimbabwe = exploratory.

## Owner communication gate (HARD — 2026-09-16)
- **Owner speaks only with Vellum** for routine status, progress, rough/polish notes, and packaging updates.
- Archivist / Scriptor / Atelier / Pulse: **do not DM the owner** with parallel updates. Post to Posterity Desk and/or message Vellum.
- Exceptions (still usually via Vellum first): credentials, 2FA/captcha handoff, spend approval, or when Vellum explicitly asks a specialist to contact the owner.
- Rationale: token/usage efficiency; single owner thread. (Same spirit as 2026-09-14 Day 2 upload-status-through-Vellum rule.)

## Runtime + music (2026-09-16)
Target 60–90s. Per-episode on-theme music bed (no same-track reuse). Free/rights-clean unless spend approved.

## Owner communication gate (RECONFIRMED 2026-09-19 owner — HARD)
- Specialists **may** message each other 1:1 or via Desk to coordinate — no requirement to only use Desk/Vellum as a hub.
- **Do NOT DM the owner** with status, progress, discovery, or parallel updates. Owner receives owner-facing comms **only from Vellum**.
- Dual-messaging owner + Vellum burns weekly usage — banned.
- Exceptions still: Vellum asks you to contact owner, or true credential/2FA/spend that cannot wait (prefer Vellum first).

## HARD — Visual storyboard gate (owner 2026-09-19)
Atelier must not render a rough until Vellum clears a numbered visual storyboard/contact sheet against mute-video standard. Insufficient assets → stop + report to Vellum; never pad with recycled plates. Owner should not be the person who finds repeated images.

## TEMP — Early owner storyboard gate (2026-09-19)
Next 3–5 uploads incl. Aksum: script→Vellum→storyboard/contact sheet→**owner quick look**→render→owner publish. After #5 publishes, Vellum reminds owner to re-eval. Drop early gate only after that re-eval (or earlier if owner says Atelier has it). See edit-preferences.md.

## HARD — Sequence board before contact sheet (owner 2026-09-19)
Atelier/Scriptor: before contact sheet, deliver ~5–7 named visual sequences with idea + shot list + system class (A/B/C) per shot. Vellum mute-gates sequence board then contact sheet. No Short assemble until owner clears sheet under early gate.

## HARD — Contact-sheet gate v2 + asset-reuse (owner 2026-09-19)
Sequence-organized sheets only. Per-cell: narration · purpose · A/B/C · new info · source. Crop/zoom/label on same source ≠ new asset unless continuity teaches. Vellum rejects “shows what VO said” frames. No Short assemble until sheet clears mute + owner early gate.

## HARD — Vellum APPROVED gate (owner 2026-09-20)
Never escalate contact sheets / roughs Vellum would fail. Owner receives only VELLUM APPROVED artifacts (or true owner-decision questions).

## HARD — INFO PACKET gate (owner 2026-09-20)
Pre-rough owner deliverable is an **INFO PACKET** (story + arc + sequence generation briefs), not a contact sheet. Atelier does **not** GenerateImage plate pools for owner mute. Owner returns plates → then assemble. See `ledger/info-packet-template.md` + edit-preferences.


## Instagram publish gate (locked 2026-09-21)
- IG web Create **defaults crop to 1:1** and letterboxes true 9:16 masters.
- Before Share: force **9:16** full-bleed; preview must fill frame with **no** top/bottom black bars.
- After Share: open Reels player and verify playback (not just the composer preview).
- Thonis incident: deleted `DdjcntUKyXp` → re-up `DdjlT9yKCaw`.


## Engagement ops (Pulse 2026-09-21 overnight)
- After pin: **first-hour reply pass** (60–120 min) — creator replies on early comments; Aksum elite hold but under-commented.
- **Pre-publish warm-up:** reply on last 3–5 Shorts 2–5 min before next upload.
- Pin discussion Q remains standing; spoken narrator Q still optional later.

## Owner delivery rule (UPDATED 2026-09-27 · was LOCKED 2026-09-22)
For each new video brief: deliver **one markdown file each** — attach (or path) `INFO-PACKET.md` and `script-final.md` at Thonis depth in the files. Short prose note in chat is enough; **do not** paste full file contents duplicated in chat.

## Standing law — Retention / Motion / Score (LOCKED 2026-09-27 · Day 11+)
See `ledger/STANDING-LAW-retention-motion-score.md`. HOOK HERO before sequence approval; motion 0–3s; optional Recovered Chronicle Reveal; SEQ fields RETENTION FUNCTION / NEW INFORMATION / MOTION OPPORTUNITY / VISUAL DELTA; music ENERGY ARC; hard rough opening gate; Pulse opening diagnostics.

## Standing law — Serials (LOCKED 2026-10-02 · ADDITIVE)
See `ledger/STANDING-LAW-serials.md`. Serials are event-programming between lanes, not a replacement. Serial Bible before Ch I; Examiner §XV continuity on Ch II+. Pulse (=Quartermaster in Serial Law XII) surfaces continuation signals; does not rewrite history. Imagewright Character Continuity Sheet when serials follow people (Atelier owns production continuity under current roster until Imagewright role exists).

## Standing law — Examiner Gate (LOCKED 2026-10-02 · ADDITIVE)
See `ledger/STANDING-LAW-examiner.md` + `ledger/EXAMINER-AGENT-SPEC.md`. After Rough Cut v1 → Examiner → Vellum adjudication → patches → Rough v2 → Owner. 0–4 findings; owner-note validation; Cut Evidence; TRANSCRIPT-ONLY mode when no playable media; not QC#2; sourcing law on targeted verify. Serial §XV continuity on Ch II+.

