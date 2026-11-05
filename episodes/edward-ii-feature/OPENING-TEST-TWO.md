# Opening sample, test two — pending

Status: the second pass was encoded. This file is the 3:00 PM brief. Where it freezes the camera, crops S002 to the hands, or keeps the axe raised, `ACT-I-PLAN.md` supersedes it. It still does not authorize a new generation, a merge, or the full film.

The first cut stays intact. Its file is `opening-sample.mp4`, 69.733 seconds, recorded in `OPENING-SAMPLE.md` and `CHECKPOINT.md`. The future export, when a pass is authorized, is a separate file named `opening-sample-test-two.mp4`.

Received 4 Nov 2026, about 3:00 PM America/Toronto. The text below is that brief.

---

# Posterity — opening sample, test two

Prepared 4 November 2026. This is a production correction brief for Atelier Jr in Cursor, combining the owner's latest feedback with inspection of PR #6 and its renderer. Treat it as the current creative direction for this sample. Preserve other approved decisions unless explicitly changed below.

## Assignment and scope

Redo the same opening sample for **The Letter for a Buried King**. The first cut proves that the workflow can produce a film, but it does not meet Posterity's established visual and motion standard. The promising part is the restrained subject movement, flame and smoke in the sealing shot. The failures are camera jitter, soft close crops, absent environmental effects, repeated coverage, a weaker lighting treatment, the wrong execution image, and an intro that misses the intended ink treatment.

The owner should review a finished second sample and make creative decisions. You own the shot planning, prompting, generation, compositing, editing, checking and correction within the authorized budget. Do not make the owner operate a prompt-by-prompt production line. Do not deliver known, repairable defects as a list for the owner to discover again.

This assignment covers the existing opening only. It does not authorize generating the rest of the feature, buying a plan, enabling auto-refill, publishing, or merging unrelated work. Preserve the first sample for comparison and produce a separately named test-two version.

## Start from the actual production state

- Repository: https://github.com/m-turnergane/posterity-motion-plates
- Existing PR: https://github.com/m-turnergane/posterity-motion-plates/pull/6
- Production branch: `cursor/atelier-jr-intake-596c`.
- Reviewed commit: `0b2f0efb96337765f3207e5a9f23a5bfd313795a`. Inspect subsequent commits before assuming this is still the head.
- Read `AGENTS.md`, the documentation index, `docs/decisions.md`, `docs/production-workflow.md`, `config/budget.yaml`, episode `STATUS.md`, `OPENING-SAMPLE.md`, and the current desk pack. Use the accepted v2.1 amendments and locked script v3.2. Do not revert to the superseded v1 pack.
- Script: `episodes/edward-ii-feature/inbox/VIDEO-PACK-v2/sources/raw/script-vo-v3.2-LOCKED.txt`, MD5 `11f4e6f9ac7d640d006dac33533472f6`.
- Current assembly: `tools/assemble_opening_sample.py`.
- Current film: `var/edward-ii-feature/opening-sample/opening-sample.mp4`, outside Git. It is linked from PR #6 through the previous Cursor agent's artifacts.
- PR #5 contains separate engine work and remains unmerged. Inspect and reuse the relevant working implementation without turning this task into an unrelated consolidation or conflict-resolution project.

The existing sample is reported as 69.733 seconds, 1920×1080, 30 fps, stereo, −14.0 LUFS, −1.3 dBTP, with selectable captions. Those technical measurements come from the existing production record. They do not establish creative acceptance.

## Preserve these decisions

- Title: **The Letter for a Buried King**.
- Locked narration and wording. Reuse the nine existing Oliver recordings and their alignment data: L01–L05, L07, L07a, L08 and L09. Do not regenerate voice merely to change pictures. L08 is already one recording with an internal visual cut.
- **Anabasis I** starts at the beginning and remains the Act I score. Preserve the approved mix unless a specific defect is demonstrated.
- Keep the cold-open structure. Redesign the existing brand/title passage in its current narrative position rather than adding a second branded opening.
- Keep the established POSTERITY letterforms from the shared master. The change is black ink on parchment and the manner of revelation, not a newly invented logo.
- The final feature's tagline remains both spoken and written in the outro. The outro and full feature remain outside this sample's scope.
- The Recovered Chronicle remains the visual direction: carefully composed historical tableaux, painterly material texture, strong motivated light, readable faces and objects, and restrained motion that serves the story.

Identity matters: the man sealing the letter and later condemned is **Edmund, Earl of Kent**. Edward II is his older half-brother, the king. Labels such as “King and advisor” must not cause Kent's identity or their relationship to drift. Check images and filenames against the locked script, not casual player chapter labels.

## Owner's references and visual standard

Use the two attached historical paintings as references, not as portraits to stretch into landscape:

1. **Nobleman Sealing a Letter by Candlelight(1).png**: the approved short reference has a bright, motivated candle, warm modelling on the face and hands, deep cool shadows, a cool window contribution, and rich cloth, fur, metal, wood and wax detail. Preserve readable shadow detail. Do not flatten the contrast, apply a global orange wash, or simply darken the new plates to imitate it.
2. **Rain-Swept Medieval Castle Execution(1).png**: the desired narrative beat is Kent kneeling at the block, restrained, with the executioner poised and axe raised. Rain, the scaffold and the watching crowd establish the situation. It is a pre-strike tableau, without impact or gore. An empty platform or discarded royal robe does not carry the same meaning.

The other supplied images are visual inspiration for ink spreading into aged paper. They are not approved finished backgrounds or licenses to copy a stock asset. The current ornate, neatly bordered title card is not the target.

Compose replacements natively for 16:9. Do not obtain widescreen coverage by aggressively cropping the portrait references. Keep each character's established face, age, costume, hair and role consistent across replacement plates.

## Shot corrections

The owner's approximate 32–54 second reference describes the repeated N01 coverage. Derive final timecodes from the actual audio and edit; do not treat these approximate timestamps as exact cut points.

| Shot / passage | Problem | Required second-pass behavior |
| --- | --- | --- |
| S001, sealing wide, H06 second take | Flame, smoke and slight body movement are promising. The owner sees a softening zoom and unstable motion. The source is a 6-second 720p Seedance clip scaled to 1080p. | Compare the raw generated clip with the assembled shot before spending. Keep the useful restrained movement. Prefer a locked camera and stable composition. Diagnose source motion, decoding cadence and assembly separately. Do not add a second camera move. If replacement is necessary, quote its exact settings and cost first, seek a genuinely higher-resolution source where supported, and request a fixed camera, no zoom, no pan or orbit, stable face/hands/letter, restrained movement and localized flame/smoke. A prompt alone is not a guarantee; inspect the result. |
| S002, sealing hands | It is a cropped still, not the animated clip. A large crop loses detail and has no environmental motion in the current renderer. | Use a crisp dedicated insert if the current master lacks enough pixels. Keep camera locked for this pass. Animate candle spill on the relevant hand, wax, paper and desk areas, with restrained local flame/smoke where visible. Preserve the folded blank letter and seal continuity. |
| S003, mourning at Gloucester, H01 | The fast lateral move is unmotivated. Candles and ambient light are static. Existing notes also flag a crowned mourner and an effigy that reads as a real body. | Remove the pan. Use stable composition, local flame movement, restrained rising smoke and candle spill. Correct the extra crown. Where an effigy is intended, make it visibly a crafted figure rather than presenting an identified corpse. Do not turn the film's historical uncertainty into a visual assertion. |
| S004, execution beat, currently N14 | The empty platform/mantle treatment misses the owner's intended image. | Restore the reference's pre-execution tableau of Kent at the block. Fit it to the locked line about his beheading. Keep identities and wardrobe consistent. Use rain or fabric movement only if they can be rendered cleanly. No invented strike or new narration. |
| S005, sealed-letter detail, DK1 | Nearby candlelight has no moving influence on the paper and desk. | Add source-motivated, spatially limited warmth and luminance variation. Keep text, wax, envelope edges and geometry stable. Do not substitute a whole-frame brightness pulse. |
| Brand / feature-title passage | The current reveal reads as a left-to-right letter wipe over ornamental parchment. It lacks the requested black bleeding ink. | Rebuild as the ink treatment described below. Preserve exact typography and title spelling. |
| ACT I and future act cards | The current act text is animated on parchment. | Solid black background, centered **ACT I**, using the established readable house typography in cream or off-white. No parchment, ornament, camera move or paid generation. Use the same system for subsequent acts. Set duration to the edit; roughly two seconds is a starting proposal, not a new locked requirement. |
| S007 / S007a / S008, N01 sequence | Multiple enlargements of one picture create repetitive coverage, soft detail and camera jitter. S007 still catches the king at its edge. | Build real coverage of the relevant subjects and story beats. A wide, a dedicated Kent medium and a dedicated Edward medium/detail must be visually distinct compositions if used. Do not simulate a conversation by sweeping between the same two faces. Keep camera locked initially and use the house torch, smoke and spill effects where relevant. |
| S008a, N21 insert | It is the existing change of image during L08. | Keep it if it matches the narrated Gascony beat and meets the same art and motion standard. Do not discard usable coverage merely to regenerate everything. |
| S009, later return to N01 | A cooled crop returns to the same image without enough new visual information. N22 was not generated. | Give the line a purposeful visual change. Use an approved alternative from the current pack, a sufficiently distinct existing asset, or a justified replacement within budget. Do not assume N22 is automatically required or approved for generation. A grade change alone is not fresh coverage. |

For the repetitive section, a new picture roughly every 5–10 seconds is a useful pacing target. It is not a command to cut mechanically. A longer hold must sustain a deliberate dramatic beat; repeated crops of one static image are not an adequate substitute for coverage.

## Fix the rendering causes

The following are findings from the reviewed source, not guesses about the agent's effort or the model's reasoning:

1. `sample()` converts crop boundaries to integers on every frame, then resizes the changing crop with `INTER_LINEAR` (lines 165–173). This can turn a slow intended move into pixel-sized steps and changing resampling softness. Easing the trajectory does not remove that quantization. Use a stable, floating-point transform sampled from the original master, with appropriate filtering and a single geometric resample. For test two, a locked camera is the default and a useful diagnostic baseline.
2. Several N01 crops use zooms from 2.05 to 2.20. That retains only about 49% to 45% of the source width. “2K” is not proof that the crop supports 1080p output. Calculate source pixels remaining after the real aspect-ratio fit and crop, then compare with output dimensions. Avoid aggressive crop enlargement and edge-clamped framing. Use dedicated compositions when needed.
3. The still-shot path calls crop/resize and an optional cool grade. It does not call the house candle, torch or smoke effects. Wire the relevant established effects into the actual path that produces the film. A note saying “candlelight” or a still painting of a flame does not animate it.
4. S001 follows a separate video path. When decoding succeeds, it returns the resized video directly and bypasses the configured zoom/pan. Therefore the opening zoom cannot simply be attributed to the still-camera settings. Inspect the source clip first. The code also seeks by milliseconds for every output frame and silently falls back to the still if a read fails. Check source frame rate/timestamps, decode sequentially or resample by presentation timestamps into a defined 30 fps timeline, log failures, and eliminate unexplained fallback jumps. Cadence problems are a risk to check, not a measured diagnosis from this review.
5. `write_stills()` passes `video=None`. Its S001 preview therefore shows the still path, not the animated video used in the final export. Extract review frames from the finished film, and review the actual moving export at normal speed.
6. The intro's `stroke_alpha()` performs a horizontal wipe inside successive raster glyphs. Its `bloom_field()` excludes a broad central text region. These choices explain the mechanical reveal and weak central ink interaction. They need replacement, not just a stronger opacity slider.
7. The font path points into `/tmp/engine-wt/`. Make fonts and dependencies reproducible in a fresh environment, with the required licenses and repo-relative configuration. Do not assume the previous VM still exists.

Use the tested house effects and their plate-specific masks where available: `fx_candle`, `torch_v1c`, `smoke_v2`, or their actual current equivalents. Locate the real implementation rather than inventing an import from these names. Preserve established seeds, scale and protected-image rules wherever they apply. Restrained body or hand animation is permitted for the selected generative shot; it does not justify warping every still.

Environmental motion must be spatially coherent: a flame moves at its source, smoke rises from that source, and nearby surfaces receive related light variation. Keep it subtle and asynchronous between separate candles. Do not animate stonework, make all lights pulse together, add smoke through faces, or make the whole painting wobble. Avoid accidental loops, discontinuities and abrupt effect resets at cuts.

## Intro art direction

The intended impression is **wet black ink entering aged parchment and resolving into the exact POSTERITY wordmark**.

- Use tactile, restrained aged parchment with room around the wordmark. Manuscript traces, staining and a few irregular splashes may support the frame; a decorative certificate border should not dominate it.
- Ink should pool and spread unevenly into the paper, with feathered edges, subtle variation in density and a few secondary blooms. Keep the word legible as it resolves.
- Where a writing action is visible, reveal along credible stroke paths or use organic ink propagation through the glyph shapes. Do not run a rectangular mask across each letter and call it writing.
- Use black or near-black ink, not the current warm brown treatment. Preserve exact letterforms, spelling and spacing. If the raster master is too coarse, reconstruct or trace it carefully and compare at delivery size rather than asking an image model to invent the logo again.
- Keep **The Letter for a Buried King** readable in the feature-title passage, with clear hierarchy and enough hold to read it. Then cut to the separate black ACT I card.
- Prefer a controlled compositor implementation for typography. If a generated ink-motion background genuinely adds value, generate ink/paper behavior separately and composite exact lettering over it. Do not entrust final readable brand text to a video model.
- First make a short local preview that demonstrates the ink behavior. Review and correct it yourself before integrating. A Seedance generation is an optional costed technique, not a requirement or an automatic solution to the intro.

## Image-model choice

The owner prefers the lighting and finish of the supplied short references and is open to returning to Higgsfield's **GPT Image 2.5** listing for this pass. Use that as the first candidate for a replacement anchor plate if current access and the authorized budget permit. Name the verified catalog ID explicitly; do not rely on a default.

Do not claim that this sample establishes a universal ranking between Nano Banana Pro and GPT Image 2.5. Lighting direction, prompts, references, composition, crop enlargement and rendering differ. First judge one native-resolution anchor against the supplied reference, before expanding replacement generation. If an actual model comparison is needed, use the same art direction, reference inputs, aspect ratio and comparable resolution for both; do not run an open-ended model survey.

Keep accepted Nano Banana Pro plates when they meet the standard. Changing the agent chat or buying a plan will not, by itself, repair camera sampling or missing effects. Seedance 2.5 is the video model here; Seedream and the GPT Image listings are still-image options. Verify actual capabilities rather than inferring them from similar names.

## Budget and account facts

The previous pass spent **62 credits**: ten stills × 2 = **20**, plus one 6-second clip = **42**. The two rejected wordmark stills account for **4** of those 20 credits. The actual intro animation was rendered locally in code. It was not a separate expensive generated-video job.

The last recorded balance was **48**, not a current account read. The owner is considering the shown $49/month, 1,000-credit plan. Do not assume purchase, renewal timing, new balance or benefits have already taken effect. Read current account state when connected.

Higgsfield's official help page, checked on 4 November 2026, says Unlimited and free generations apply only on its website; MCP, CLI and other automated generation calls deduct credits regardless of plan. Treat website promotion labels as distinct from MCP entitlement. Source: https://higgsfield.ai/creator-hub/help-center/credits/how-credits-work

The card's “67 videos” is not a quote for this sample's exact configuration. At the observed 42-credit setting, 1,000 credits covers 23 complete six-second clips before any stills or retries. Obtain the current price for the exact model, duration, resolution and options before submission.

Proceed autonomously with asset inspection, timeline design, renderer fixes, effect masks, intro work and local previews. Before paid work, respect the latest explicit spending cap. If no numeric cap exists, prepare one aggregate plan identifying required replacements, estimated total, maximum submissions and fallback choices; ask once for the missing cap. Do not convert this into approval requests for every image. Do not silently use website “unlimited” as a zero-cost MCP assumption. Reuse cached VO, images and jobs wherever appropriate. Track estimated and actual spend, job IDs, failed/rejected outputs and remaining balance.

## Execution order

1. Inventory and recover the existing media, cached VO/alignment, score, wordmark, source I2V clip, references and fonts. Check hashes and current branch. Recover prior outputs before paying to replace missing local files.
2. Inspect S001 source versus assembly; reproduce the still-shot issue and establish a locked-camera baseline. Fix the common render path and connect the existing house effects.
3. Make a shot plan tied to the current narration. Identify the smallest set of genuinely necessary replacement plates, including the execution beat and distinct coverage for the repeated N01 passage.
4. Rebuild the intro and black act card locally. Prepare the costed generation plan and resolve any missing numeric cap before paid submissions.
5. Generate only the justified replacements under that cap, inspect them at native size, reject anatomy/identity/history/lighting failures yourself, and assemble the corrected sample using the cached soundtrack and captions.
6. Watch the complete export at normal speed and inspect the relevant shots closely. Correct defects before asking the owner to review. Report a real blocker if you cannot meet a requirement; do not quietly lower the standard.

## Acceptance and delivery

Before delivery, verify:

- No visible camera micro-jitter, unexpected pan, bouncing reframing, decode jump, geometric warping or soft enlarged close-up. Fixed backgrounds remain stable during effects.
- Candle and torch scenes have restrained, localized flame/light behavior and appropriate smoke. Source placement and illumination agree.
- The execution image communicates the intended pre-strike situation. Mourning images have no unintended crown or misleading body/effigy treatment. Kent and Edward remain distinguishable and consistent.
- The repeated N01 section now has purposeful coverage. No long passage relies on bouncing around a single painting to simulate new shots.
- POSTERITY resolves as ink in paper, with exact letters; the title is readable; ACT I is centered on a plain black screen.
- The sample meets the supplied short reference's lighting and material-detail standard at normal viewing size. Use side-by-side native plate checks to distinguish source quality from export softness.
- Narration wording and cached takes are preserved; timing, sync, music ducking and selectable captions survive the recut. Verify output duration, 1920×1080, 30 fps and audio measurements again. Do not report first-pass measurements as if they measured the new file.
- Review frames and contact sheets are extracted from the actual final export, including the generated-video shot. Automated checks supplement watching the complete moving film; they do not replace it.

Deliver **opening-sample-test-two.mp4**, a compact contact sheet with actual timecodes, a shot/source/effects manifest, the change list, remaining known issues if any, exact spend and remaining balance, and reproducible commands. Keep large media outside Git with durable artifact links and checksums; commit the relevant code, decisions and production records on the working branch. Keep the first cut intact. Return the sample for creative review and wait before full-feature production.

Record the reusable lessons in the existing Posterity rules and motion documentation: use floating-point camera sampling, avoid unnecessary camera movement, validate real crop resolution, apply house environmental effects, make genuinely distinct coverage, keep exact branding separate from generated motion, and inspect final exports. Update the existing source of truth rather than creating several competing rule files.

## Review evidence and limits

The source findings above refer to the reviewed commit's [assembly script](https://github.com/m-turnergane/posterity-motion-plates/blob/0b2f0efb96337765f3207e5a9f23a5bfd313795a/tools/assemble_opening_sample.py). Relevant areas are `build_timeline()` at line 83, `sample()` at 165, `stroke_alpha()` at 216, `bloom_field()` at 252, `render_frame()` at 332 and `write_stills()` at 353. Production metadata and spend are recorded in [OPENING-SAMPLE.md](https://github.com/m-turnergane/posterity-motion-plates/blob/0b2f0efb96337765f3207e5a9f23a5bfd313795a/episodes/edward-ii-feature/OPENING-SAMPLE.md) and PR #6.

Review included owner-supplied images and feedback, visible frames in the hosted sample, and source inspection. It did not include independent listening to the soundtrack or frame-by-frame measurements of the source clip. Integer crop quantization is a concrete implementation issue and a plausible jitter contributor; source video camera movement, decode cadence and their relative contribution still need direct isolation by the production agent.
