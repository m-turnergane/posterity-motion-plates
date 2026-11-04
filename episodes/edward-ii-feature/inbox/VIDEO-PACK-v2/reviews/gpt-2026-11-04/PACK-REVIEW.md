# Edward II video pack v1: review before Cursor production

Reviewed November 4, 2026. Input: `EDWARD-II-VIDEO-PACK-v1-DOCS.zip`, extracted without changing the supplied files. This is an editorial and production-readiness review of documents and manifests, with limited external historical corroboration. No paintings, animation, recorded VO, score audio or finished film were included, so their actual quality has not been reviewed.

## Verdict

**Useful for Cursor intake and setup; needs amendments before full paid production.** The research structure and machine-readable planning are substantial. The package is still designed largely around the earlier owner-generated-paintings/locked-engine workflow, with Higgsfield permission added in the README. That permission has not been made consistent across its governing documents and shot instructions.

Keep the central story, evidence distinctions, character anchors, native widescreen plan, structured manifests and continuous sample. Repair the operational conflicts and perform a focused storytelling pass rather than restarting the research.

## What was verified

| Check | Result |
| --- | --- |
| Archive inventory | 39 files; no source files changed during review |
| Authoritative raw narration | 98 lines, 1,715 whitespace-delimited words |
| Raw narration MD5 | `852babf5ee00468240c33626f7dc4a26`, matches the pack |
| Shot list | 103 rows: 99 VO shots plus four silent cards |
| Shot JSON versus CSV | No substantive differences |
| Master manifest | 35 masters; no undefined plate IDs in shot list |
| Plate JSON versus CSV | No substantive differences after treating JSON null as an empty CSV cell |
| Estimated timeline | Shot durations total 730.0 seconds, matching 12:10.0 |
| Source manifest | All 24 present files match recorded MD5 values; nine listed binary assets are absent |

These checks establish internal document consistency, not historical truth or visual quality. Supporting research captures and the claimed quote-verification program are not included in this docs-only export, so the research team's complete verification cannot be reproduced here.

## 1. Resolve the generation and motion authority conflict

**High priority before generation.** `sources/STANDING-LAW-longform.md` sections 1, 5, 6 and 7 still require the owner to generate plates, prohibit autonomous image/API generation, require Vellum's KEEP/REDO on each plate, restrict motion to named locked presets, and treat depth/camera extensions as R&D. The README explicitly records that current owner direction permits Higgsfield and leaves shot sourcing to Atelier Jr, but says the conflict is not resolved there.

The current owner direction in this conversation already permits Cursor to generate images/video and perform production. Carry that into a versioned pilot override/revised operative rule; do not request the same permission again. Preserve the historical law as a superseded source rather than destructively rewriting it.

The replacement needs to state:

- Atelier Jr generates and reviews media within the approved budget; owner reviews the calibration/full cut rather than every individual plate.
- Higgsfield image-to-video is available as a first option for narrative scene animation.
- Existing engine code is inspected and reused for assembly, maps, titles and useful effects; reimplementing all old motion machinery is not a prerequisite.
- Identity, costume, geometry and historical constraints must remain stable, while deliberate physical action is permitted.
- Actual job/account/cost verification precedes paid generation. Publishing remains a separate owner action.

This is primarily a precedence correction. It should not reopen unrelated editorial approvals.

## 2. Replace implementation prescriptions with shot intent

The JSON has **88 `ENGINE_PRESET`, four `ENGINE_CARD`, and eleven `ENGINE_ATLAS` rows**. No row currently specifies a Higgsfield video type. The generic sourcing field says Atelier Jr can choose Higgsfield, but the detailed motion briefs repeatedly instruct slow pushes, drifts, fixed faces/hands and named engine effects.

That is a risk of reproducing the earlier motion style rather than testing the new capability. For narrative shots, separate `dramatic_intent`, `required_invariants`, `permitted_action`, `preferred_method`, and `fallback`. Let the production agent translate those into provider-specific prompts after checking available tools and prices.

Examples of candidate motion tests, subject to the approved scene and reference image:

| Moment | Useful action to test | Preserve |
| --- | --- | --- |
| H06, sealing the letter | Ring presses into wax and lifts; candle and cloth movement | Kent's identity, hand anatomy, ring and seal design |
| H02, Corfe handover | Letter passes between hands; a measured guard reaction | Letter continuity, gate architecture, character identity |
| N12, Mortimer receives/reads it | Small controlled hand, eye or head movement | Unreadable document text and historically permitted staging |
| H03, Nottingham seizure | Restrained physical confrontation supported by the scene | Non-graphic action, cast/architecture and evidence limits |

These are test candidates, not a requirement to buy four videos. Select the highest-value example after live cost checks. Precise route/label animation should remain deterministic.

### Reuse needs deliberate attention

Reusing a painting is not inherently a defect; it needs a reason and enough visual development. Current contiguous allocations include:

| Painting | Shots | Estimated uninterrupted exposure |
| --- | --- | ---: |
| N01, the brothers | S007–S009 | 22.5 s |
| N02, the landing | S010–S012 | 25.9 s |
| N11, supporters | S035–S037 | 20.0 s |
| H05, Fieschi writing | S061–S063 | 24.9 s |
| DF2, register copy | S064–S065 | 21.7 s |

Different crop names do not automatically create new narrative information. In particular, the Fieschi introduction holds writing/register imagery for about 46.6 consecutive seconds before returning to H05. Reassess those passages after VO: physical action, a purposeful reveal, a different asset, or a script trim may help. This is a pacing concern, not a blanket duration prohibition.

## 3. Make the docs-only asset boundary explicit

The archive name honestly identifies a docs-only package. However, the README and map/score instructions sometimes speak as though binary dependencies are already inside it. They are not.

Nine source-manifest entries are absent:

- `sources/atlas-refpack-v2/britain_16x9_ref_bare.png`
- `sources/atlas-refpack-v2/britain_16x9_ref_tinted_notext.png`
- `sources/atlas-refpack-v2/euro_16x9_ref_bare.png`
- `sources/atlas-refpack-v2/euro_16x9_ref_tinted_notext.png`
- Five `score/candidates/*.mp3` files: Anabasis I, Katabasis I, Unraveling, Penumbra, MemoriesOfStone.

Other referenced dependencies also need delivery or a reproducible retrieval/build route: approved Short reference paintings such as b20/b01/b03/b04/b05/b12/b15/b18; realm-ID raster masks; actual map generator/registration code and geodata; `motion/PRESETS.md` and required presets; Chronicle Reveal v3.2b; house typography/fonts; T01 tomb photographs and their provenance; exact VO/audio presets; and any private reference renders.

The source machine's `/workspace/posterity/...` paths and short hash prefixes are provenance, not locations Cursor can necessarily access. Supply a separate asset/code archive or an accessible repository/object-store location. For publicly downloadable audio, exact URLs and file hashes can work if retrieval is supported. Distinguish REQUIRED, OPTIONAL, REGENERABLE and MISSING assets in one manifest.

This episode pack is not a replacement for the channel-wide desk handoff. The separate editorial/visual/technical bible is still needed.

## 4. Budget motion before spending on all paintings

The README reports 110 trial credits as observed by the desk. That is a supplied account observation, not independently verified against Higgsfield here.

At the desk's rough 2–3 credits per image assumption, **34 generations consume 68–102 credits**, leaving **42–8 credits** before failed candidates, rerolls, video or upscaling. Some required resolutions may change those quotes. This is arithmetic for planning, not a live provider price.

The representative sample requires eleven generated masters if none of its references/bases are available: around 22–33 credits at the same simplified image assumption, before motion.

Recommended sequence: inventory reusable media, query actual prices, reserve a defined motion/retry allowance, and produce a representative sample before committing to the full slate. Preserve the owner's actual chosen credit cap. Replace vague instructions to ask before spending the last credits with explicit accounting for queued jobs, a reserve and a stop condition.

No reason to buy every painting before discovering whether image-to-video preserves the art. No full-film cost promise can be made while clip length/model/resolution and acceptance rates are unknown.

## 5. Fix the stale title instruction

The README and shot list move the title to SC01 after L06. The H06 MOTION HANDOFF in `PLATE-PROMPTS.md` still says Chronicle Reveal v3.2b rides over S001–S002. This is a concrete conflict and could produce a duplicate or misplaced title.

Remove the stale H06 placement from the active instructions; keep the current owner-approved placement. Transfer the real house title component, duration and font. Placeholder times should remain estimates until it exists and recorded narration is available.

The existing plan has a 5-second title followed by a 3.5-second Act I card, around 42 seconds in. The acts revision is described as owner-requested; do not remove it without approval. Edit the transition so these do not feel like two consecutive starts. Decide the feature title and card wording together with the owner when the desk presents its concrete recommendation.

## 6. Recalculate map timing and nominate one method authority

ME4/S073 has 8.3 seconds for Avignon → Paris → Brabant → Cologne → Milan. Using the supplied full-frame coordinates, even straight segments total about **1,033.6 output pixels**. At the prescribed 90 px/s maximum, drawing alone needs about **11.48 seconds**. Four 1.2-second arrival holds bring it to approximately **16.28 seconds**.

This is a full-frame planning lower bound. Final camera transforms, partial pre-drawn paths, label treatment and actual route curves can change the calculation; the rendered shot has not been tested. The current combination of complete route, speed, holds and allocated duration needs reconciliation. Recalculate every map beat against the actual VO and camera transform, then shorten route detail, use staged cuts or adjust picture timing instead of simply accelerating unreadable labels.

The map pack describes ORB + RANSAC homography; the detailed registration plan describes an affine initialization. Pick one authoritative implementation and reference it correctly. Its reported prototype uses a synthetic warp of the reference rendering, which does not demonstrate that feature matching will work equally well against a painterly AI reinterpretation. The missing code/reference assets prevent reproduction here. Validate on the actual generated map and keep a usable deterministic fallback.

## 7. A focused story pass would improve the film

### Preserve the human center

Kent helping depose his brother, attending the funeral, and later risking his life to rescue him is the strongest dramatic spine. The first line's buried-king/letter contradiction works. The distinction between Kent's missing letter and the separate Fieschi letter is carefully protected and should stay.

### Tighten the opening's repeated promise

L01–L06 take about 42.1 seconds before the title. They explain the relationship, funeral and execution, then ask two framing questions. The hook is strong; the repeated framing and explicit evidence-audit question slow its conversion into action.

Ask Scriptor for a surgical version that moves more quickly from the contradiction into the story. Preserve essential orientation and the human stakes. L06's method question is the first trim candidate; do not automatically delete every necessary relationship explanation. Any changed VO requires updated countersign and dependent timing, not an untracked edit by Cursor.

### Reduce the research-apparatus detour

L59–L65 spend substantial time introducing the notary, future bishopric, date uncertainty, copy/register provenance and document separation before the letter's central action arrives. Keep the distinctions but deliver only what the viewer needs at that moment. The long run of writing/register images compounds the issue.

L70–L73 then become an itinerary. The narrative point is the letter's claim of escape, concealment, travel and a hermit's life. Most place names can remain in map labels rather than forcing each into VO, if Scriptor and Archivist approve a shorter text. Geography should sharpen the mystery rather than become a travel checklist.

### Protect proportional evidence and the payoff

The script already states the majority view at L76 and presents opposing interpretations. It is not simply asserting survival. However, the ending's “what it cannot establish” and “never been settled” wording can leave the impression that the alternatives have equal support or that uncertainty itself supports survival.

Make the conclusion explicit about the distinction: Kent's actions and circulating belief can be documented; they do not independently prove his brother survived. Preserve the human tragedy as the emotional payoff. Do not replace uncertainty with invented certainty, or assert that all historians agree.

The Berkeley passage also needs fuller context: the pack's own C30/C31 record material concerning the keepers and the jury's treatment is stronger context than presenting an isolated ambiguous phrase. Ask the Archivist/Scriptor to decide a concise, fair contextual addition. The research team already gathered the relevant evidence; this request does not require inventing new motive or dialogue.

External spot checks found Warner's 2011 journal abstract corroborates the central Kent paradox and around-seventy supporter finding. Haines's 2009 abstract explicitly concludes Melton's letter rested on misleading information. Those support retaining both the seriousness of contemporary belief and the distinction between belief and proof. Full paywalled articles and the complete primary-source set were not independently reviewed.

## 8. Normalize the ledger rather than misreading OPEN

C11 is OPEN for Kent's motives but permits stated actions. C14b is OPEN for writing place/repository but permits a generic notary description. C16e is OPEN for unread historians' books but permits a consensus statement supported through C16a. C17 blocks an unsupported link between letters while permitting the Fieschi letter's own mention of Kent's execution.

This is not evidence that every shot carrying those IDs is forbidden. It is a mixed-granularity data problem: a naive OPEN blocker could reject approved narration, while another agent might treat permissive prose as allowing too much.

Split blocked propositions from permitted/narrowed claims, or add structured `allowed_scope`, `blocked_scope` and `supporting_claim_id` fields. Connect the consensus line to its actual support and keep blocked inferences blocked. Recheck the final script/shot links after editorial amendments.

## 9. Generate VO from the canonical script, not repeated shot text

The raw script is 1,715 words. Concatenating all voiced rows in the shot list yields **1,818 words**, because split shots repeat full lines. The README explains this, but the production importer must enforce it.

Generate narration once per canonical line/segment from the raw script, then map multiple shots to aligned time spans. Do not create an artificial L29a/L29b text split by cutting a recording in half on a word-count percentage. The definitive split point must follow the actual recorded phrase. Store generated narration separately from on-screen display forms and pronunciation aliases.

## Suggested handoff order

1. Send the amendment request to the desk; preserve v1 for reference.
2. Give Cursor this pack plus the ChatGPT handoff and this review for read-only intake/environment setup now.
3. Desk supplies a resolved operative override, corrected active manifests, concrete editorial recommendations and the asset/code transfer route.
4. Confirm current approved script and budget; inventory available media and live quotes.
5. Produce the actual continuous sample and examine animation/style/continuity. The 47-second minimum variant does not test the map or act-card crossfade and should not alone certify the whole workflow.
6. Expand into the complete review cut once the sample passes.

## External references used for limited corroboration

- Kathryn Warner, *The Adherents of Edmund of Woodstock, Earl of Kent, in March 1330*, English Historical Review (2011), abstract: https://academic.oup.com/ehr/article-abstract/CXXVI/521/779/421465
- Roy Martin Haines, *Sumptuous Apparel for a Royal Prisoner: Archbishop Melton's Letter, 14 January 1330*, English Historical Review (2009), abstract retrieved through search: https://doi.org/10.1093/ehr/cep186
- The direct LRB Carpenter page was not accessible through the research tool; discussion of Berkeley context above is based on the supplied ledger/packet, not a claim to have newly read that full article.

Companion: `edward-ii-pack-audit.json` contains reproducible counts, missing manifest files, same-plate runs, trial arithmetic and the map timing calculation. Review recommendations are advisory; the original script and approval records were not altered.
