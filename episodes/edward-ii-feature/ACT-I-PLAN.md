# Act I operational plan

Current plan for the Edward II feature, written 4 Nov 2026 after 8:25 PM America/Toronto, amended on the morning of 5 Nov 2026, and closed for Higgsfield at 12:33 PM America/Toronto the same day. This file supersedes conflicting motion fields in `inbox/VIDEO-PACK-v2/SHOT-LIST.csv` and the test-two camera freeze. The desk CSV stays as the pack delivered it. Where a cell below disagrees with that CSV, this file is the one to follow. Do not add another plan beside this one.

Production is back with Vellum and Atelier. No further Higgsfield spending is authorized. New stills are made in ordinary ChatGPT chats. The desk edits and assembles them with the existing engine. Purchased assets stay, including the sealing clip.

The opening sample already follows the rows marked **in the cut**. The rest of Act I is planned and not generated.

## Rules that bind every shot

A physical action is either in a generated clip or it is not in the picture. The engine can ease a scale-only push, flicker a painted flame, drift smoke, and spill light. It cannot walk a person, hand over a letter, turn a head, or swing an axe. If the shot list's `permitted_action` describes one of those and `preferred_method` is `STILL+ENGINE`, the action text is a copied field and is void.

`i2v_test_candidate: YES` and `preferred_method: HIGGSFIELD_I2V` are void where this plan does not name a clip. S002 copied both from S001. S007 through S009 and S018 copied one "Kent turns his head" sentence onto shots where that is not the picture. The pack copied one procession sentence onto S003, S025, S026, and S028. Nobody walks. S003 and S026 are the stone tomb. S025 is the carved effigy. S028 is the new reign, not the choir.

A shot that uses the scale push does not also use `depth_v1`. Depth stays off until a shot has a reviewed depth pass and no global push. No opening plate has that pass.

The push is `1.00 → 1.04` around the centre, `smoothstep`, floating-point `INTER_CUBIC`, window clamped to the plate. Flame, smoke, and spill are painted on the plate and then resampled, so they move with the painting. A shot with no headroom is not pushed. The S001 clip gets no second move.

Repeated plates are a coverage problem, not a crop problem. Consecutive lines may share a plate when they are the same place. A third hold on the same painting needs a different asset or it is cut.

A still may show an arrival that has already happened. It does not have to animate the walk. The sealing clip is the only generated clip in Act I. It plays once, for its own sentence, and it is not looped or held. Every other beat is a still plus the engine.

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
| S011 | They land, and Kent lands with them | A wide of the force already ashore. Boats at the strand. Isabella, Mortimer, and Kent standing on the sand, in the same light. The arrival reads with the picture held still | Engine push. No second picture is required to show the walk. Do not stage the still as a frozen step out of a boat | New still |
| S012 | The records say what he did, not why | Kent already on that shore, closer, the company and the ships behind him. Same coast and light as S011. His hands are empty | Push. This is the invasion, and it continues under L12 | New still. The rescue letter stays on S005 |
| S013 | Edward flees west and is taken in South Wales | Britain atlas. Ink runs from the Chepstow pin to the South Wales label. The spoken words are South Wales, so that is the label. No sea route toward Ireland | Engine route. 164.5 px needs 3.03 s inside about 9.2 s, so the shot holds after the line arrives | The atlas, once it exists |
| S014 | He is taken to Kenilworth, in the middle of England | The same atlas. The ink continues inland to the Kenilworth pin, and the sentence ends at "the middle of England." The crown is the next shot | Engine route. South Wales to Kenilworth is 426.5 px and needs 5.94 s. This sentence alone is about 4.6 s, short by 1.34 s. Start that draw during S013. Together the two shots have 13.8 s against 8.97 s of ink. Re-time both after the lines are recorded | The same atlas |
| S015 | There he lost his crown | Edward II bareheaded at Kenilworth, the crown already set down. Cut off the map on "and there he lost his crown." | Push. Nobody lifts the crown | New still. The atlas cannot show this |
| S016 | The boy is crowned. He is Kent's nephew | Edward III at the ceremony. Fourteen, fair-haired, beardless, small in the robes, the crown just set, bishops around him. He does not wear his father's jaw-length hair or beard, and he is not the S007a plate | Push. The crown is already set | New still |
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
| S029 | Reports begin to reach Kent that his brother is alive | A portrait of Kent already holding a folded report. The paper has no readable writing. It is not the rescue letter, and nobody is handing it to him | Push and candlelight on the plate | New still |

N01 is no longer the picture for S007, S007a, or S018. N02 is not used for S010, S011, or S012. The night window covers S020 and S022. The viewing covers S023 and S024. The atlas shots stay maps.

## The funeral, one set of pictures

The pack assigned one funeral plate to the cold open, the effigy line, the burial, and "England moved on." Those are four different sentences.

- S003 stays the accepted limestone tomb. Its line says Kent stood at the funeral. It does not say a wooden effigy was displayed.
- S025 is a new tableau, the carved effigy already described for this line in the pack's H01 prompt. The rejected jointed figure is not a source, and the script is not rewritten around the stone tomb.
- S026 returns to the stone tomb for the burial at Gloucester.
- S027 is Kent at the effigy. If the funeral file is wide enough, his window is taken from it. If that window would upscale, ChatGPT makes a separate portrait of Kent in the same choir. It does not make a second wide as well.
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
| Remaining | Retrieve the guide. Generate the plate in ChatGPT only with that guide attached. Accept it only if it measures 3840×2160. Register it and run the pack's pixel check. Time the routes again after the lines are recorded |

The house map class for this episode is still provisional. This plate uses the Recovered Chronicle pigments above. The coasts in the guide image have not been looked at, because the image is not here. What this pass checked is the framing file against the locked narration: Chepstow, South Wales, Kenilworth, Berkeley, and Lincoln fall where those sentences put them, and Lincoln's label sits on the pin-safe edge. A failed plate has no substitute on disk. It is a missing shot.

## No further clips

The sealing clip stays on S001. It is not replayed on S002 or S012. S002 is two stills. The landing, the coronation, and the report are stills. Nobody walks ashore, nobody sets the crown in motion, and nobody hands Kent a paper. A morning quote for a new clip is not a plan to buy one.

## Act I inventory

Two lists. The first is already paid for or recovered, and the desk reuses it. The second is what ChatGPT still has to make. Do not send either list to Higgsfield.

### Accepted assets, available for reuse

| Asset | Serves | Where the bytes are |
| --- | --- | --- |
| Sealing clip, H06 | S001 only | First-cut archive. sha256 `f5b0f5c4e295eaf4cb3a8433c763d209e0326f4c61d93490c3d73a8d65939f3f` |
| H06 still | S002 | First-cut archive. sha256 `858cfd6360003e33f66ec8d11d0a4b6e61f261e2735618715157a6595e31fcab` |
| Edward on the throne, S007a | S002b and S007a | 5 Nov archive. sha256 `2b4be0ee8de365a077553bfe81d53b73f5e1bbe2c96c87654df621003fbf58f8` |
| Stone tomb, S003 | S003 and S026 | 5 Nov archive. sha256 `275da1328ac5ea4a5f86280d3a14629b15a521dc06f7f17f90c64bb758495d77` |
| Raised axe, S004 | S004 until the resting-axe still is accepted | 5 Nov archive. sha256 `d962f1d96f9b574954126cffda40d31589c298e6938c29712571d0b179582064` |
| Sealed letter, DK1 | S005 only | First-cut archive. sha256 `64eb734d7a75c973aa64786b12a8fc9ee302622dcb8583067147ad3fd67dcb41` |
| Ink leaf, CB1, and the wordmark | The title and the act card | First-cut archive |
| Kent in the hall, S007 | S007 and S018 | 5 Nov archive. sha256 `7f97c800f23b658faf6e71a06659f9741d2e2004edfab8d9c3602e1a44da515d` |
| Both men, N01 | S008 | First-cut archive. sha256 `877b7136eeb8f8ba139a2cf6e1f08934674721857ee0a9062f82506369dc12fd` |
| Gascony terrace, N21 | S008a | First-cut archive. sha256 `b07690c28d1c0bd469e7dfa92ff67e8cb8316b17b5e1d16a85ffcf220fe6ae52` |
| Relit court, S009 | S009 only | 5 Nov archive. sha256 `aaf697d251dc249116dea4550e077626c3617a8101f3a84db9fddd7a3c86354f` |
| Penumbra | This cut, from 0:30 | 5 Nov archive. md5 `2acea4098213d02c944d57a2faa19a51` |
| Anabasis I | The first cut only | First-cut archive |
| The nine original Oliver takes | The first cut, and this cut except L04 and the title | First-cut archive |
| L04 and the spoken title | This cut | 5 Nov archive |

The jointed funeral attempt is not on this list. Its hash is in the 5 Nov manifest, and it stays unused.

### Generate in ChatGPT

Horizontal 16:9. Recovered Chronicle finish: oil and gouache, visible brushwork, aged varnish, fine craquelure. Attach the accepted face when that person is in the picture. A glossy or photographic result is rejected. No readable text. No Higgsfield job.

| Picture | Serves | What the chat makes |
| --- | --- | --- |
| Resting axe | S004, once it is accepted in place of the raised-axe plate | The owner's shorts frame and the accepted Kent face. He waits. The axe rests. Kent is at the block. No swing, no impact |
| The decision | S010 | Isabella and Mortimer, one medium, before any shore |
| The landing | S011 | The force already ashore. Boats at the strand. Isabella, Mortimer, and Kent standing |
| Kent in the invasion | S012 | The same shore and light, closer. His hands are empty |
| The crown set down | S015 | Edward II bareheaded at Kenilworth. The crown is already set down |
| The boy king | S016 | Edward III at fourteen, fair-haired, beardless, small in the robes, the crown just set, bishops around him |
| The new regime | S017 and S028 | A different framing. The boy, with Isabella and Mortimer a step behind him |
| The night window | S020 and S022 | One light in a dark castle window. S022 is a tighter window of the same file when that window stays on the plate |
| The viewing | S023 and S024 | People at a distance, a draped form. S024 is the doorway of the same picture |
| The funeral effigy | S025, and S027 when the file is wide enough | Carved wood, hands folded, copper-gilt crown, closed coffin, Kent at the left. No joints. If his window would upscale, a separate choir portrait of Kent replaces that crop |
| The report | S029 | A portrait of Kent already holding a folded report. Candle or lantern light. No readable writing. Nobody is handing him the paper |
| Britain atlas | S013, S014, S019, S021 | One clean plate, exactly 3840×2160, and only after the guide image is attached. England and Wales oxblood, France royal blue, antique gold. No baked text, routes, or icons |

S017, the funeral master, the night window, and the viewing move onto the reuse list once the chat has made them and the desk has accepted them. Later-act plates are not in this list.

## Later acts, the consistency pass

The same copied fields show up after Act I. They are void on the same terms.

- S033 does not inherit a handoff. The report is already in Kent's hands on S029. A friar, if that later sentence needs one, is its own still.
- S042, S043, and S044 copy "a clerk reads, one turns away" across three stills of one plate. One plate, one push, no turn. Split them only with a real second picture.
- S087 and S093 follow the funeral rule above. Nobody walks.
- S099's mist-and-ink line is an engine treatment of a still, which the engine can do.
- S094, S098a, and S098b are marked as clips in the pack and are callbacks of Act II plates. They are not Act I, and a callback does not become a new clip.
- Corfe (S038, S039), the letter to Mortimer (S040), and Nottingham (S048) stay later-act candidates. S039 does not give the letter by pushing in.

Atlas shots in every act stay engine maps. The engine draws the route.
