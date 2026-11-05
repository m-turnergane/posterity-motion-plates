# Act I operational plan

Current plan for the Edward II feature, written 4 Nov 2026 after 8:25 PM America/Toronto. This file supersedes conflicting motion fields in `inbox/VIDEO-PACK-v2/SHOT-LIST.csv` and the test-two camera freeze. The desk CSV stays as the pack delivered it. Where a cell below disagrees with that CSV, this file is the one to follow. Do not add another plan beside this one.

The opening sample on this branch already follows the rows marked **in the cut**. The rest of Act I is planned and not generated. Nothing in the paid section has been submitted.

## Rules that bind every shot

A physical action is either in a generated clip or it is not in the picture. The engine can ease a scale-only push, flicker a painted flame, drift smoke, and spill light. It cannot walk a person, hand over a letter, turn a head, or swing an axe. If the shot list's `permitted_action` describes one of those and `preferred_method` is `STILL+ENGINE`, the action text is a copied field and is void.

`i2v_test_candidate: YES` and `preferred_method: HIGGSFIELD_I2V` are void where this plan does not name a clip. S002 copied both from S001. S007 through S009 and S018 copied one "Kent turns his head" sentence onto shots where that is not the picture. S003, S025, S026, and S028 copied one procession sentence onto a tomb.

A shot that uses the scale push does not also use `depth_v1`. Depth stays off until a shot has a reviewed depth pass and no global push. No opening plate has that pass.

The push is `1.00 → 1.04` around the centre, `smoothstep`, floating-point `INTER_CUBIC`, window clamped to the plate. Flame, smoke, and spill are painted on the plate and then resampled, so they move with the painting. A shot with no headroom is not pushed. The S001 clip gets no second move.

Repeated plates are a coverage problem, not a crop problem. Consecutive lines may share a plate when they are the same place. A third hold on the same painting needs a different asset or it is cut.

## What the opening cut does now

These choices are already in the renderer. They do not wait on the quote below.

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

## The rest of Act I, not yet made

| Shot | What the viewer understands | Picture during the line | Motion, method, fallback | Asset |
| --- | --- | --- | --- | --- |
| S010 | Isabella and Mortimer turn against Edward | Both of them, one new medium. Not the boats, and not N02 shared with the landing | Push and whatever flame the painting has. Fallback: the accepted court still, Edward absent from the point | New still when this shot is reached. Not a clip |
| S011 | They land, and Kent lands with them | Shore, ships, Kent among the company. This is the one Act I clip worth buying | One 6 s clip of the arrival, camera fixed inside the clip, no second push. Fallback until that clip exists: the new still plus the engine push. Do not fake the landing on N02 | New still, then a clip. See the quote |
| S012 | The records say what he did, not why | The sealed letter, the existing DK1 plate. He is not stepping ashore | Spill and the push. A step is not delivered | Existing still |
| S013 | Edward flees west and is taken in South Wales | Atlas, Chepstow then the South Wales coast. Engine route and labels only | Engine map move. No clip, no painted walk | Existing atlas path |
| S014 | He is taken to Kenilworth | Atlas widens to Kenilworth | Engine map move | Existing atlas path |
| S015 | There he lost his crown | Kenilworth, the crown leaving him. One new wide, or the atlas held if the plate is not ready | Push only. No crowning gesture | New still when reached, else the atlas |
| S016 | The boy is crowned. He is Kent's nephew | The boy, the crown, one wide. Held as the second clip, not bought with the landing | Until a clip is bought: the still and the push. The crowning itself waits for the clip. Do not stage it as a head turn | New still. Clip held |
| S017 | Real power stands behind the boy | Isabella and Mortimer behind the throne, a different framing of the same place | Push. They do not step forward | New still, may share the S016 master if the framing is actually different |
| S018 | Kent helped bring his own brother down | Kent, close, and not another crop of N01. The accepted S007 plate can carry it | Push and the torch already on that plate | Existing still |
| S019 | The deposed king is moved to Berkeley | Atlas, Kenilworth to Berkeley | Engine map move | Existing atlas path |
| S020 | Word goes out that the former king is dead | A castle window at night, one picture for the announcement | Push and a practical light. No messenger walks | New still when reached |
| S021 | The news reaches the young king at Lincoln | Atlas, north to Lincoln | Engine map move | Existing atlas path |
| S022 | No record says how he died | The same night window, tighter on the single light. Same place as S020, so one plate may be shared | Push. Do not add a body | Same still as S020, tighter window |
| S023 | Notables are called to see the body | The viewing, wide, people at a distance. Not the tomb from S003 | Push. They do not file past | New still when reached |
| S024 | They looked only superficially | The same viewing, from the doorway, the body less readable | Push. Nobody leans in | Same master as S023, different window |
| S025 | An effigy was probably displayed | The accepted stone tomb, not a new wooden figure. The locked line says "wooden"; the jointed wooden take was rejected and is not revived | Torches on the plate, then the push | Existing still |
| S026 | Buried at Gloucester before Christmas | The same tomb, wider, one hold. Two lines, one place | Same treatment as S025 | Existing still |
| S027 | Kent was there, and no record says he saw the body | Kent in the church, the accepted S007 hall is the wrong room. A new medium of Kent in the choir, or S003's Kent if he is already in that frame and readable | Push. He does not approach the bier | New still when reached. S003 only if Kent is already clearly present |
| S028 | England moves on | Not a fourth tomb. The relit court, or the letter, for one line | Push and the light that plate already has | Existing still |
| S029 | Reports begin to reach Kent that his brother is alive | Kent with a paper already in his hands. The handoff is not shown unless the held clip is bought | Push and candle. Fallback is this still. A clip would show the paper changing hands and is not bought with the landing | New still when reached. Clip held |

Long holds this resolves: N01 is no longer the picture for S007, S007a, or S018. H01 is not in the opening, and the tomb shots are the stone plate twice (S025, S026), not four processions. N02 is not used three times. N05's two lines share one window. N06's two lines share one viewing. The atlas shots stay maps.

## Paid next, not submitted

Balance re-read this session, before any quote was spent: **26 credits, plan Plus**. `unlim` is not available. `use_unlim` false. No job was submitted. The test-two remainder of 1.50 credits and 0 submission slots is not this budget. The 26 is the account, and this section is a quote, not an authorization.

### S004 resting-axe still, the only image to buy first

Replace the raised-axe plate with a native 16:9 of the owner's shorts frame. The headsman waits. The axe is lowered, head resting, blade on the scaffold. Kent is at the block, held, alive. Rain, crowd, castle, banners. No swing, no impact, no blood, no readable text. If a clip is ever made from it, the pose stays this pose.

| Setting | Value |
| --- | --- |
| Model | `gpt_image_2_5` |
| Aspect | `16:9` |
| Quality | `high` |
| Resolution | `2k` |
| Count | 1 |
| `use_unlim` | false |
| Quoted this session | **2.75** |

References when it is submitted: the owner's resting-axe frame, and Kent's accepted face. Not the raised-axe plate.

Retry allowance, one extra submission only: the same 2.75 settings if the picture is wrong. The high `4k` quote, **4.25**, only if the 2k picture is the right composition and too soft. Do not spend both. Ceiling for this still is **7.00**. It fits in 26. A failed quote retry is not a third submission.

### Act I clips, not bought

Unit price re-quoted this session. Model `seedance_2_5`, mode `omni_reference`, duration 6, aspect `16:9`, `generate_audio` false, `use_unlim` false. No seed was part of the quote.

| Resolution | Credits | Decision |
| --- | --- | --- |
| `1080p` | **96** | The only resolution to buy, and not on this balance |
| `720p` | **42** | Rejected. The seal clip's softness is that size scaled to 1080 |

Buy one clip, not three. The landing (S011) is the one: the shot list has him coming ashore, and the assigned plate is the same N02 as the scene before and the scene after. A push cannot land an army. Coronation (S016) and the messenger (S029) are the held pair. They are not purchased with the landing, and they are not purchased to keep the list tidy.

A landing package is one new still at 2.75, one still retry at 2.75, and one 1080p clip at 96, which is **101.50** before a clip retry. A clip retry is another 96. The 26-credit balance cannot pay it. Do not submit the landing still ahead of the clip and then cover the gap with a push. The fallback until the balance exists is no landing shot at all, not a dishonest one.

Corfe (S038, S039), the letter to Mortimer (S040), and Nottingham (S048) stay later-act candidates. They are not added to Act I and they are not in this quote. The same action rule applies there: S039 does not "give" the letter by pushing in.

## Later acts, the consistency pass

The same copied fields show up after Act I. They are void on the same terms.

- S033 copies S029's handoff onto another still. Same rule: the paper is already in hand, or it is a clip.
- S042, S043, and S044 copy "a clerk reads, one turns away" across three stills of one plate. One plate, one push, no turn. Split them only with a real second picture.
- S087 and S093 copy the Gloucester procession onto Act III. No one walks. Reuse the stone tomb or cut the hold.
- S099's mist-and-ink line is an engine treatment of a still, which the engine can do. It is not a clip.
- S094, S098a, and S098b are marked as clips and are callbacks of plates already marked in Act II. They are not Act I, and a callback does not automatically buy a second clip of the same action.

Atlas shots in every act stay engine maps. A clip never draws the route.
