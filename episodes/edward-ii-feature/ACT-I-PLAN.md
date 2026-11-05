# Act I operational plan

Current plan for the Edward II feature, written 4 Nov 2026 after 8:25 PM America/Toronto and amended 5 Nov 2026 before production handoff. This file supersedes conflicting motion fields in `inbox/VIDEO-PACK-v2/SHOT-LIST.csv` and the test-two camera freeze. The desk CSV stays as the pack delivered it. Where a cell below disagrees with that CSV, this file is the one to follow. Do not add another plan beside this one.

The opening sample on this branch already follows the rows marked **in the cut**. The rest of Act I is planned and not generated. The amendment pass authorizes this plan, the recovery package, and local work. It does not authorize a Higgsfield submission.

## Rules that bind every shot

A physical action is either in a generated clip or it is not in the picture. The engine can ease a scale-only push, flicker a painted flame, drift smoke, and spill light. It cannot walk a person, hand over a letter, turn a head, or swing an axe. If the shot list's `permitted_action` describes one of those and `preferred_method` is `STILL+ENGINE`, the action text is a copied field and is void.

`i2v_test_candidate: YES` and `preferred_method: HIGGSFIELD_I2V` are void where this plan does not name a clip. S002 copied both from S001. S007 through S009 and S018 copied one "Kent turns his head" sentence onto shots where that is not the picture. The pack copied one procession sentence onto S003, S025, S026, and S028. Nobody walks. S003 and S026 are the stone tomb. S025 is the carved effigy. S028 is the new reign, not the choir.

A shot that uses the scale push does not also use `depth_v1`. Depth stays off until a shot has a reviewed depth pass and no global push. No opening plate has that pass.

The push is `1.00 → 1.04` around the centre, `smoothstep`, floating-point `INTER_CUBIC`, window clamped to the plate. Flame, smoke, and spill are painted on the plate and then resampled, so they move with the painting. A shot with no headroom is not pushed. The S001 clip gets no second move.

Repeated plates are a coverage problem, not a crop problem. Consecutive lines may share a plate when they are the same place. A third hold on the same painting needs a different asset or it is cut.

A still may show an arrival that has already happened. It does not have to animate the walk. A bought clip plays once, for the sentence it covers, and the next shot is a different picture. The clip is not looped, and its last frame is not held to fill the line.

New and replacement pictures use the Recovered Chronicle finish: oil and gouache, visible brushwork, aged varnish, fine craquelure, and the house pigments. A glossy or photographic result is rejected. The accepted opening plates stay as they are. They are not passed through a new grade.

Motion is judged by watching the picture at normal speed. A pixel-change number only supplements that. Atlas shots do not take the opening's scale move. Their motion is the ink route and the holds.

## What the opening cut does now

These choices are already in the renderer. They do not wait on the inventory below.

| Shot | What the viewer understands | Picture | Motion | Asset |
| --- | --- | --- | --- | --- |
| S001 | A brother seals a letter for a king already buried | Wide: Kent, candle, blank letter, signet on the wax. The whole of L01 | The accepted 6 s clip, used only for its own length. No loop, no freeze, no second push | Existing clip |
| S002 | The man at the desk is Edmund, Earl of Kent | "The brother was Edmund, Earl of Kent." Kent's face and the signet hand, from the H06 still, `z` 1.25→1.28, centre `(0.38, 0.48)`. The window does not upscale | Candle and smoke on the plate, then the small push | Existing still |
| S002b | The buried king is his half-brother, Edward the Second | From "The buried king…" through the gap before the funeral. Edward alone on the throne, the accepted S007a plate, full frame, `z` 1.00→1.025 | That plate's torch, on the plate, then the small push. The face is protected and is not relit | Existing still. Not a new portrait, and not the sealing clip |
| S003 | Kent stood at Edward's funeral | The accepted limestone tomb. Kent bareheaded. No procession | Torches and smoke on the plate, then the push. Nobody walks | Existing still |
| S004 | The cost of the plot, before the blow | The raised-axe plate already in the film, until the resting-axe still below is generated and accepted. No swing, no impact | Push only. Rain is painted. The pose does not change | Existing still, pending replacement |
| S005 | The question sits on the sealed letter | The letter, full frame | Offscreen spill on the plate, then the push. The paper is not warped | Existing still |
| SC01 | The film names itself, then the act | Black ink wordmark and the written title on the CB1 interior, then a black card, cream centred `ACT I` | Ink, then a hard cut. No push | Existing leaf |
| S007 | Kent's birth and his age against Edward | Kent alone in the hall. The whole of L07 | One torch on the plate, then the push | Existing still |
| S007a | By the time Kent was grown, Edward was king | Edward alone on the throne. The whole of L07a. This is the same plate as S002b, later and longer, which is the point: the cold open named him, and here he is king | One torch on the plate, face protected, then the push | Existing still |
| S008 | The loyal years, both men | The one wide of recovered N01, through the word before "even" | Two torches on the plate, then the push | Existing still |
| S008a | Even in Gascony | The daylight terrace. No flame | Push only | Existing still |
| S009 | The reign turns, and the king is isolated | The relit court. Face light comes from the torch and the window | Two cressets on the plate, faces and the barons protected, then the push | Existing still |

Penumbra from 0:30 stays. The first cut and its Anabasis I stay. The nine accepted Oliver files in `opening-sample/vo` stay. This cut replaces only L04 and the spoken title, in `opening-sample-test-two/vo`.

L04 uses the house stability 0.5, seed 1611, the same model and the other house settings, with L03 as `previous_text` and L05 as `next_text`. Wording is unchanged. Against L01, L02, L03, L05, L07, L07a, L08, and L09, the raw take sits inside their range for level, brightness, and high-band ratio. The previous L04 was outside that range on all three: louder, brighter, and thinner. A stability 0.72 take was still slightly thinner than the quietest accepted line's high band. A stability 0.85 take dropped below the quietest accepted line. Neither replaced 0.5. Request `I3JpHXFYKbwuvt6CXHQ5`.

The title uses stability 0.72, same seed and model, L05 before it and L07 after it. Wording is unchanged: "Posterity. The Letter for a Buried King." The raw high-band ratio fell from 0.329 to 0.183 and the brightness fell from about 3110 Hz to about 2830 Hz. Level after the compressor is not the reason: both takes land near the same processed level. Stability 0.5 with the same neighbours was thinner (0.490). Stability 0.85 was darker but thinner again (0.245). The kept take is still a little brighter than the long lines. No fourth take. Request `58x9NzCI2LWDDQjQUeCk`. The longer read holds the parchment, and the act card follows the line. The 69.733 s duration is not a requirement.

Character-cost header for the six calls, three per line, is 162. Two of each line were discarded. The 30,000-credit ask is unchanged.

## Review encode

The master stays `var/edward-ii-feature/opening-sample-test-two/opening-sample-test-two.mp4`, sha256 `9b4f84e9a30c290b3717e33db94cabaf42862082ad6a0c159089870d8d15256b`, 172,313,796 bytes. The review file is `opening-sample-test-two-review.mp4` beside it, sha256 `23ea109edcff7a01c42ffcc2f368c505da127abce105d2aa7354f49852e3cc4b`, 63,693,053 bytes. Same picture size, 30 fps, 2,122 frames, AAC, and the same captions. It is a transcode of the master, crf 18 with an 8 Mbps cap, not a new render. An uncapped crf 18 of this cut was about 122 MB and would not copy onto the review volume.

Frames from the master were checked across the cut, and the change from one frame to the next was measured inside each shot. That change stays steady. The ink and the act card sit still. Between 5.3 s and 7.1 s the candle flame stays on the wick while the framing eases. Edward's face on the throne takes the window and the torch. The court face takes the window and the near sconce. S005 varies more than the other stills because the spill on that plate already moves. The recovery package for this cut is `checkpoint/RECOVERY-2026-11-05.md`.

## The rest of Act I, not yet made

Estimates use 2.4 words a second until the lines are recorded. The locked script is unchanged.

| Shot | What the viewer understands | Picture during the line | Motion, method, fallback | Asset |
| --- | --- | --- | --- | --- |
| S010 | Isabella and Mortimer turn against Edward | Both of them, one new medium, before any shore. Isabella about thirty, dark crimson, white veil. Mortimer about forty, dark hair, short dark beard, dark green | Push and whatever flame the painting has. The still is the shot | New still. Not Edward II's court, and not the landing |
| S011 | They land, and Kent lands with them | A wide of the force already ashore. Boats at the strand. Isabella, Mortimer, and Kent standing on the sand, in the same light. The arrival reads with the picture held still | The still is the beat. If the clip is bought, it starts on this picture, camera fixed, no second push, and it plays once across the landing sentence. The cut then goes to S012. The clip is not looped and the last frame is not held. Re-quote the duration to the recorded sentence before buying. Do not stage the still as a frozen step out of a boat | New still. The clip is optional motion on that still |
| S012 | The records say what he did, not why | Kent already on that shore, closer, the company and the ships behind him. Same coast and light as S011. His hands are empty | Push. This is the invasion, and it continues under L12 | New still. The rescue letter stays on S005 |
| S013 | Edward flees west and is taken in South Wales | Britain atlas. Ink runs from the Chepstow pin to the South Wales label. The spoken words are South Wales, so that is the label. No sea route toward Ireland | Engine route. 164.5 px needs 3.03 s inside about 9.2 s, so the shot holds after the line arrives | The atlas, once it exists |
| S014 | He is taken to Kenilworth, in the middle of England | The same atlas. The ink continues inland to the Kenilworth pin, and the sentence ends at "the middle of England." The crown is the next shot | Engine route. South Wales to Kenilworth is 426.5 px and needs 5.94 s. This sentence alone is about 4.6 s, short by 1.34 s. Start that draw during S013. Together the two shots have 13.8 s against 8.97 s of ink. Re-time both after the lines are recorded | The same atlas |
| S015 | There he lost his crown | Edward II bareheaded at Kenilworth, the crown already set down. Cut off the map on "and there he lost his crown." | Push. Nobody lifts the crown | New still. The atlas cannot show this |
| S016 | The boy is crowned. He is Kent's nephew | Edward III at the ceremony. Fourteen, fair-haired, beardless, small in the robes, the crown just set, bishops around him. He does not wear his father's jaw-length hair or beard, and he is not the S007a plate | Push. The crowning gesture stays the held clip | New still. Clip held |
| S017 | Real power stands behind the boy | A different picture of the same ceremony. The boy king, with Isabella and Mortimer a step behind him. Two native faces, not a crop of S016 | Push. They do not step forward | New still. S028 uses this file |
| S018 | Kent helped bring his own brother down | Kent, close. The accepted S007 hall plate | Push and the torch already on that plate | Existing still |
| S019 | The deposed king is moved to Berkeley | The atlas, Kenilworth to Berkeley. Gloucester is not lit. The burial uses that name later | Engine route. 256.5 px needs 4.05 s inside about 5.8 s | The same atlas |
| S020 | Word goes out that the former king is dead | A castle window at night, one light | Push and a practical light. No messenger walks | New still |
| S021 | The news reaches the young king at Lincoln | The atlas. The Lincoln pin only. No route and no date | Engine hold. No scale move. The pin is 12 px inside the pin-safe top, and the label box touches that edge | The same atlas |
| S022 | No record says how he died | The same night window, tighter on the single light | Push. The window stays on the plate. No body | Same still as S020 |
| S023 | Notables are called to see the body | The viewing, wide, people at a distance. A draped form. This is not the tomb and not the effigy | Push. They do not file past | New still |
| S024 | They looked only superficially | The same viewing, from the doorway. The form is farther off and less readable | Push. Nobody leans in | Same master as S023, different window |
| S025 | An effigy was probably displayed | The funeral the line describes. Gloucester choir, candlelit hearse, closed coffin under black cloth, and on it a carved and painted wooden effigy, hands folded, copper-gilt crown. Kent at the left, looking at the carving. No joints, no open coffin. The sentence stays qualified | Candlelight on the plate, then the push. The carving does not move | New funeral master |
| S026 | Buried at Gloucester before Christmas | The accepted stone tomb, held wider. This sentence is the burial. The effigy was the funeral | The same torch treatment as S003 | Existing stone plate |
| S027 | Kent was there, and no record says he saw the body | Kent in that choir, looking toward the effigy. The hall is the wrong room. The tomb is the wrong object for this line | Push. A window of the funeral master, accepted only when that window does not enlarge past the plate. He does not approach a body | The funeral master |
| S028 | England moves on under its new rulers | The S017 ceremony, full frame. Edward III, with Isabella and Mortimer behind him. The funeral is over | Push and the light already in that picture | The S017 still. Not S009, and not S007a |
| S029 | Reports begin to reach Kent that his brother is alive | Kent already holding a paper. The paper is a report. It is not the rescue letter | Push and candle. The handoff stays the held clip | New still. Clip held |

N01 is no longer the picture for S007, S007a, or S018. N02 is not used for S010, S011, or S012. The night window covers S020 and S022. The viewing covers S023 and S024. The atlas shots stay maps.

## The funeral, one set of pictures

The pack assigned one funeral plate to the cold open, the effigy line, the burial, and "England moved on." Those are four different sentences.

- S003 stays the accepted limestone tomb. Its line says Kent stood at the funeral. It does not say a wooden effigy was displayed.
- S025 is a new tableau, the carved effigy already described for this line in the pack's H01 prompt. The rejected jointed figure is not a source, and the script is not rewritten around the stone tomb.
- S026 returns to the stone tomb for the burial at Gloucester.
- S027 is Kent at the effigy. If the funeral file is wide enough, his window is taken from it. If that window would upscale, the one retry for this picture is a separate 2k close of Kent in the same choir, and a second wide is not bought on top of it.
- S023 and S024 stay the earlier viewing of the body. They use neither the tomb nor the effigy.
- S087 and S093, later, still describe the funeral and currently inherit a procession. Nobody walks. They reuse the effigy tableau or the stone tomb, whichever sentence they are actually covering. This pass does not generate an Act III plate.

## The Britain atlas

There is no atlas plate on this machine. "Existing atlas path" is not a state that can be handed to production.

| Item | State |
| --- | --- |
| Base | One clean plate, exactly 3840×2160. No baked text, routes, or icons. Frame `britain_16x9`: centre −2.55, 51.95, width 705 km, 0.36719 km per output pixel. England and Wales oxblood, France royal blue, antique gold, from the house atlas note. The pack prompt's crimson is not the pigment. Routes, when the engine draws them, are oxblood with a parchment keyline |
| Retrieval | The guide is `britain_16x9_ref_tinted_notext.png`, md5 `2519b448ea7a8076d94b7ebf7e9e4bd2`, 257,312 bytes, in `EDWARD-II-VIDEO-PACK-v2-MEDIA-part09-of-10.zip`. Its recorded path is `/workspace/posterity/engine-rnd/maps/atlas/refpack/img_v2/britain_16x9_ref_tinted_notext.png`. It is not in this repo and not on this disk. The bare guide and the realm-id image travel with it |
| Registration | `inbox/VIDEO-PACK-v2/registration/register_atlas_h.py` is in the pack. It has not been run. There is no transform and no registered plate |
| Labels | Chepstow, Kenilworth, Berkeley, and Lincoln are pins. South Wales is a region label at the Glamorgan centroid, with no pin. Gloucester can be labelled on this frame and is left dark on the Berkeley move |
| Route timing | Chepstow to South Wales fits S013. South Wales to Kenilworth starts during S013 because S014 is short. Kenilworth to Berkeley fits S019. Lincoln is a pin only. The 1326–27 line is solid ink and does not join the later dotted route. These times are the pack's 2.4-words-a-second estimate. No Act I map line has been recorded |
| Remaining | Retrieve the guide. Generate the plate only with that guide attached. Accept it only if it measures 3840×2160. Register it and run the pack's pixel check. Time the routes again after the lines are recorded |

The house map class for this episode is still provisional. This plate uses the Recovered Chronicle pigments above. The coasts in the guide image have not been looked at, because the image is not here. What this pass checked is the framing file against the locked narration: Chepstow, South Wales, Kenilworth, Berkeley, and Lincoln fall where those sentences put them, and Lincoln's label sits on the pin-safe edge. A failed plate has no substitute on disk. It is a missing shot.

## What is deliberately not a clip

- The coronation. The crown is already set in the still. The gesture clip stays on the held list.
- The messenger. The report is already in Kent's hands. The handoff clip stays on the held list.
- The seal. Already used once, on its own sentence, and not on S012.
- S002. Its copied clip flag was a mistake. It is two stills.
- S033 copies the handoff. S042, S043, and S044 copy "a clerk reads." S099's mist is an engine treatment. Corfe, Mortimer's letter, and Nottingham stay in later acts.

## Act I inventory

Prices reconfirmed on the morning of 5 November 2026, America/Toronto, with `get_cost` and no job. A 16:9 high still is 2.75 at 2k and 4.25 at 4k, model `gpt_image_2_5`, count 1, `use_unlim` false. The balance was read again the same morning: 26 credits, Plus plan. `unlim` is not available. The test-two remainder is not this budget. Twenty-six credits do not pay the base.

### New and replacement stills

| Still | Serves | What is generated | Credits |
| --- | --- | --- | --- |
| Resting axe | S004, replacing the raised-axe plate | 2k. The owner's shorts frame and the accepted Kent face. He waits, the axe rests, Kent is at the block. No swing, no impact, no readable text | 2.75 |
| The decision | S010 | 2k. Isabella and Mortimer | 2.75 |
| The landing | S011, and the clip's start image if the clip is bought | 2k. The force already ashore | 2.75 |
| Kent in the invasion | S012 | 2k. Same shore and light. No letter | 2.75 |
| The crown set down | S015 | 2k. Edward II bareheaded at Kenilworth | 2.75 |
| The boy king | S016 | 2k. Fourteen, beardless, the crown just set | 2.75 |
| The new regime | S017 and S028 | 2k. The boy, with Isabella and Mortimer behind him | 2.75 |
| The night window | S020 and S022 | 2k | 2.75 |
| The viewing | S023 and S024 | 2k. A draped form, distant | 2.75 |
| The funeral effigy | S025 and S027 | 4k, so Kent's window can stay on the plate. Carved wood, hands folded, no joints. Accepted only if that window does not upscale | 4.25 |
| Britain atlas | S013, S014, S019, S021 | 4k, accepted only at exactly 3840×2160, and only after the guide image is attached | 4.25 |

Base, one generation of each and no clip: **33.25 credits**.

One retry per still, at the same settings: another 33.25. A 2k retry may be the 4.25 size when the picture is right and the file is soft. That replaces the 2.75 retry. It is not added to it. The funeral retry is either one more 4k or, if the wide cannot yield Kent's window, one 2k close. Not both.

### Reused masters

No new spend. H06 clip for S001. H06 still for S002. S007a for S002b and S007a. The stone tomb for S003 and S026. DK1 for S005 only. The ink leaf and the wordmark. S007 for S007 and S018. N01 for S008. N21 for S008a. The relit court for S009 only. S017, once it exists, for S028. The funeral master, once it exists, for S027. The night window for S022. The viewing for S024.

### The selected clip

Compared the same morning for a six-second 16:9 clip from a still. A 720p file is not a candidate. The Seedance 1080p quote is not the only configuration.

| Model | Settings asked | Credits | Fit |
| --- | --- | --- | --- |
| Kling 3.0 | mode `4k`, duration 6, sound off | 36 | Names a 4k resolution, silent, one start image. Selected |
| FLUX 3 Video | resolution `1080p`, duration 6, `generate_audio` false | 48 | Named 1080p and silent. The next configuration if the Kling file measures under 1920×1080 |
| Gemini Omni Flash 1.1 | mode `image-to-video`, resolution `1080p`, duration 6 | 27 | Named 1080p. The request has no audio switch, and the model is described with its own audio. Not used for a silent tableau |
| Seedance 2.5 | mode `omni_reference`, resolution `1080p`, duration 6, `generate_audio` false | 96 | Named 1080p and silent. The known family. Not the buy. The two silent options above cost less |
| Kling 3.0 `pro` and `std` | duration 6, sound off | 10.5 and 9 | Silent, and cheaper. The catalog does not name their pixel size, so they are not the planned file |

The selected clip is Kling 3.0, mode `4k`, 16:9, duration 6, sound off, count 1, `use_unlim` false, the accepted S011 still as the start image. It is accepted only if the file measures at least 1920×1080. A smaller file is not scaled up, and the buy stops. FLUX at 48 is the named-1080p replacement, quoted again on the day, not an automatic submission. The clip covers the landing sentence and then cuts to S012. If the recorded sentence is not six seconds, the duration is re-quoted before the submission. The clip is not looped.

One clip retry at the same settings is 36. The held coronation clip and the held messenger clip are the same unit price if they are ever bought. They are outside the totals below.

### The proposal

| | Credits |
| --- | --- |
| Base, every required still once, no clip | 33.25 |
| One retry of every still | 33.25 |
| The landing clip, once | 36 |
| One retry of that clip | 36 |
| Maximum authorized-work proposal | 138.50 |

The landing package is not the Act I budget. The balance of 26 covers none of the base. This amendment does not authorize a submission.

## Later acts, the consistency pass

The same copied fields show up after Act I. They are void on the same terms.

- S033 copies S029's handoff onto another still. The paper is already in hand, or it is a clip.
- S042, S043, and S044 copy "a clerk reads, one turns away" across three stills of one plate. One plate, one push, no turn. Split them only with a real second picture.
- S087 and S093 follow the funeral rule above. Nobody walks.
- S099's mist-and-ink line is an engine treatment of a still, which the engine can do. It is not a clip.
- S094, S098a, and S098b are marked as clips and are callbacks of plates already marked in Act II. They are not Act I, and a callback does not buy a second clip of the same action.
- Corfe (S038, S039), the letter to Mortimer (S040), and Nottingham (S048) stay later-act candidates. S039 does not give the letter by pushing in.

Atlas shots in every act stay engine maps. A clip never draws the route.
