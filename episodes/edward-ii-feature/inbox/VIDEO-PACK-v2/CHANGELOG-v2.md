# CHANGELOG v2 (2026-11-04): each change mapped to its review item (reviews/gpt-2026-11-04/AMENDMENT-REQUEST.md)

| review item | change | files |
|---|---|---|
| A (override) | Versioned pilot override: precedence, the owner's 10:38 authorization (not asked again), roles, engine reuse made optional, house law preserved | PILOT-OVERRIDE-v1.md, 00-README |
| A (intent) | SHOT INTENT blocks (dramatic_intent, required_invariants, permitted_action, preferred method, fallback) added before all 35 handoffs; the old handoffs are relabelled v1 suggestions | PLATE-PROMPTS.md |
| B | Docs/media boundary stated; 10 independent MEDIA zips with an index (md5, status, route); engine bundle pointed to, not duplicated; Drive folders linked; presets written out; T01 CC0 photos and licence evidence added; MISSING list | ASSET-TRANSFER-INDEX.*, 00-README, sources/commons_imageinfo_T01 |
| B (MAP-PACK claim) | The false "tinted guides copied in" claim fixed; the guides now ship in the MEDIA zips | MAP-PACK.md |
| C | Replaced by the owner's 12:35 rule: sample phase unconstrained → owner gate → full film; guardrail on plan upgrade or account exhaustion | PILOT-OVERRIDE, 00-README, DECISION-BUNDLE |
| D1 | Stale Chronicle Reveal placement removed from H06 | PLATE-PROMPTS.md |
| D2 | Title and ACT I joined into one continuous 7.5 s intro (SC01 4.5 + SC02 3.0); act cards number-only (owner 12:41) | SHOT-LIST, LONGFORM-HOUSE-INTRO-BRIEF, STYLE-SAMPLE, SCORE-PLAN |
| D3 | One authority, homography, with a tested script (euro median 2.47 px, britain 2.10 px) | REGISTRATION-PLAN-v2.1.md, registration/register_atlas_h.py, MAP-PACK §2 |
| D4 | Route timing recomputed; MB2 continuous from S013; ME2 hold into S072; ME3 and ME4 staged pre-ink (ME4 animates 497.5 px = 7.93 s, margin +0.37 s) | MAP-PACK §4b |
| D5 | Not done here (Archivist). The pack cites ledger v3 split scopes (C11-b, C14b-b, C16e-b, C17-b) | sources/CLAIM-LEDGER-v3.* |
| D6 | IMPORTER RULE: VO from the canonical raw script only | 00-README |
| E | Not done here (Scriptor/Archivist). The v3 proposal's impact on the pack is documented; VO is unchanged | V3-PROPOSAL-IMPACT.md |
| F | One owner bundle: approvals, one yes/no plan, title options, small picks | DECISION-BUNDLE.md |
| owner 12:39/12:40 | Long-form intro and matching outro on E01 (9.5 s, final fade); E01 prompt updated | LONGFORM-HOUSE-INTRO-BRIEF, PLATE-PROMPTS E01, SHOT-LIST S099 |
| owner 12:44 | Hybrid map layer rule and test | MAP-PACK §2c, 00-README |

Backups of revised files: /workspace/tmp/vp2/*.v1copy.*, PLATE-PROMPTS.pre-intent.bak. v1 is untouched.


## v2.1 (2026-11-04, after 12:50pm ET): repin to script v3.2 LOCKED

Trigger: owner approved Edward II script v3.2 as is (12:50pm ET). Backup of the v2 state: /workspace/tmp/vp2/pre-v3.2/ (VIDEO-PACK-v2.tar, SHOT-LIST.v2.csv/.json, PLATE-MANIFEST.json). The v2 DOCS zip is kept unchanged. **No VO text edited.**

| step | change | files |
|---|---|---|
| 1 | Locked script copied byte-identical (md5 11f4e6f9ac7d640d006dac33533472f6, 101 lines, 1,884 words); ledger v3.2 (8e824c98 / c654b495), Archivist v3.2 check (480224d8) and the v3->v3.2 diff added. Script v2/v3 and ledger v3 marked SUPERSEDED. | sources/, SOURCES-MANIFEST.csv, 00-README, _inputs (zip) |
| 2 | SHOT-LIST rebuilt on the 101 lines: 110 rows (106 shots + SC01-SC04); new columns vo_word_count, v21_change; split shots carry only their own words, so vo_text concatenates to exactly 1,884 words (asserted). Cuts: S006 (L06), S073 (L72), L61 shot. New: S007a, S008a, S009, S059a, S059b, S074 on L73, S086a, S095-S098d. Claims keyed by line ID (C36 L07, C37 L07a, C38 L97a). C16e-a on L92; L97 = C09, C05c; L97a = C38, C13, C06, C12. Total 805.6 s (13:25.6); title 0:29.5, ACT I 0:34.0, ACT II 3:33.7, ACT III 7:39.6. | SHOT-LIST.csv/.json |
| 2 | Map beats re-timed; ME4 staging kept, moved to S074/L73, fits +2.07 s; MB1+MB2 one continuous draw; label set unchanged. | MAP-PACK §4/§4b |
| 2 | V3 impact items closed. | V3.2-ADOPTION-RESOLVED.md (new), V3-PROPOSAL-IMPACT.md (RESOLVED banner) |
| 3 | Opening sample v3.2 only: L01-L05, intro, ACT I card, L07-L09 (~83.6 s). | STYLE-SAMPLE, 00-README, DECISION-BUNDLE |
| 3 | Every plate carries its verbatim v3.2 VO; new N21 (Gascony, required), N22 (barons/favourites, optional), N23 (L57b, optional); N20 RESERVE. 38 masters, 34 required + 2 optional generations. | PLATE-PROMPTS.md, PLATE-MANIFEST.csv/.json, ASSET-TRANSFER-INDEX |
| 3 | Score spans re-timed (A1 0:00-3:33.7, A2 3:33.7-7:39.6, A3 7:39.6-13:25.6); Memories Of Stone no longer fits A3. | SCORE-PLAN.md |
| 3 | Gurney, Ockley, Gascony, Lincoln added. | PRONUNCIATION.md |
| 4 | DOCS zip EDWARD-II-VIDEO-PACK-v2.1-DOCS.zip. Media unchanged: no MEDIA zip rebuilt. | handoff/ |
