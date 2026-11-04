# POSTERITY — Living Chronicle Atlas (owner brief, Sat 10/31 9:01am ET)
Owner: "i still dont love the map." This brief supersedes the A-vs-B style pick.

Summary of owner direction (verbatim brief pasted in Vellum chat t2208u; key points):
1. North star: CK3/EU/Total War + Kings and Generals/HistoryMarche inspiration, NOT imitation. A forgotten chronicle narrating its own contents. Communicate where, how, and how certain. Keep Recovered Chronicle look (gouache/tempera, parchment, restrained pigments).
2. Hybrid atlas: one map, layered states. Default "Chronicle Atlas" = current ochre/rust/slate political + subtle relief under translucent realm pigment, fine ink borders. Terrain emphasis and Political emphasis are smooth transitions of the same map. Zoom-aware detail. Period borders; no false precision where ambiguous.
3. Choreography: unit = narration beat. Establish geography first; reveal only the narrated segment; traveller marker advances with route; meaningful arrival holds (major destinations weigh more than waypoints); completed segments persist at reduced emphasis; easing; camera widens before long transitions; no simultaneous unconnected routes.
4. Markers: portrait medallion / heraldic cameo, zoom-aware (portrait+name close, emblem far), never covers labels. Later: banners, ships, convoys, factions — painted, not HUD.
5. Chronicle Reveal: atlas unfolds/unrolls once at open; later: city marker expands into a painted plate and back.
6. Evidence grammar: documented = confident continuous ink; reported/disputed = broken lighter route; approximate = shaded area; competing accounts = separate, only narrated one emphasized. Edward II: at Berkeley, transition into a Fieschi Letter layer while the earlier account recedes.
7. Legibility pass: label hierarchy (region/kingdom/city/castle/landmark), collision-aware labels, borders subordinate, route in vermilion/iron-red/oxblood with ink texture (less saturated). Separate controls for motion, labels, colours, borders.
8. 16:9 primary for long-form, native 9:16 too (not a crop) from the same episode spec: independent camera, labels, marker scale, safe areas.
9. Sequence: P0 three identical frames (political-forward, terrain-forward, hybrid) -> pick style; P0 narration-driven choreography; P0 camera + legibility + 16:9/9:16 configs; P0 evidence states with source/status metadata per segment; P1 character token; P1 Chronicle Reveal; P2 territory changes, multi-army, sieges, branching, plate transitions. Don't delay the long-form pilot.
10. Acceptance test: short Edward II excerpt with establishing view, character following slow route, arrival pause, responsive labels, camera move, evidence-status change; both 16:9 and 9:16; reviewed WITH real narration. Pass = viewer knows who moves, where, and what the source claims without pausing; synced; mobile-legible labels; no speculative journey shown as fact.
Final principle: every motion orients, advances the story, or reveals information — otherwise it's decoration.

Vellum house-rule reconciliations:
- No on-screen status/disclaimer text (standing law). Evidence state is shown by line/area styling only; the narration names the source ("according to Fieschi's letter"). Place names remain the only text, plus optional character name on the medallion at close zoom.
- No title card ("The letter's route") unless owner asks.
- Data stays on Natural Earth/ETOPO1/OHM REALMS-1327-v1/MAP-PLACES-v1 authority check; Ireland and Glamorgan stay label-only.

## Roadmap additions (owner, 9:03am ET) — AFTER the two core breakthroughs (hybrid look + narration-driven routes)
1. The atlas remembers: revisited locations keep earlier events as faint ink ghost layers; later campaigns unfold over earlier ones (serials).
2. Live borders: realm pigment spreads, fractures, fades or recedes with narration (conquest, collapse).
3. Evidence on the geography: manuscript fragment / find / quotation briefly emerges as a marginal annotation, then recedes. NOTE: quotation text would break the place-names-only rule; owner sign-off needed before use in an episode (fragment imagery without text is fine).
Owner priority: get the hybrid appearance and true narration-driven route animation right first; icons, political transitions and manuscript effects are enhancements after.

## Owner art-direction note on P0 (9:44am ET) — base map NOT approved; narration test PAUSED
Hybrid reads as a terrain map with faint colour washed over it. Wants a substantial change:
1. Strong deliberate realm pigments: rich oxblood/crimson England, pronounced weathered royal blue France, deep antique gold for the continental realm, distinct pigments elsewhere where historically appropriate. Hand-painted political regions, not watercolor stains.
2. Political readability first: territories + borders dominant; detailed relief underneath enriches, never overpowers. Viewer distinguishes realms before mountains/rivers.
3. Crisp, organically imperfect inked medieval-atlas borders (no glowing game borders); pigment stops decisively at the border, no bleed.
4. Age comes from texture/craft (parchment grain, pigment wear, ink imperfection, painted relief), NOT from desaturating everything.
5. Hierarchy: active narrative elements > relevant territories/borders > relief > decorative texture.
6. Hybrid = ~75% political character / 25% terrain by default; terrain can rise temporarily when geography matters.
7. Routes adaptive contrast: restrained parchment keyline (or similar) so oxblood never vanishes on rust/red realms or reads as scribbles; no neon.
Deliverable: THREE genuinely different strong-pigment colour treatments of the SAME frame (identical borders, zoom, relief). Show each WITHOUT routes first, then WITH routes. Include actual-size mobile previews. Owner approves base map before any animation/choreography/narrated test resumes.

## ARCHITECTURE CHANGE (owner, 11:07am ET) — separate map ILLUSTRATION from map ANIMATION
Owner: procedural palettes still don't reach the quality of our generated map plates (refs: Roman Empire, eastern Mediterranean, Virginia/Roanoke, candlelit map). Engine is NOT abandoned; it just stops owning final illustration quality.
Workflow:
1. Desk supplies geography: exact framing, boundaries, required locations, route data, and a geographically reliable REFERENCE image with period boundaries annotated.
2. Owner generates the illustrated atlas plate against it in Recovered Chronicle style and approves the art.
3. Clean plates: no routes, moving icons or narration-dependent labels baked in. Static geography (mountains, forests, coastlines, terrain, settlement vignettes) is fine.
4. Atelier registers the approved plate to the geographic reference (control points/warp), sets coordinates, overlays animation.
5. Engine does camera, routes, markers, highlights, labels, environmental FX on top of the plate.
6. Realms that change during a story keep separate geographic masks so pigment can animate without wrecking the art.
7. Separate 16:9 and 9:16 camera comps; reuse art + event data, but generate a separately composed plate when a crop compromises it.
Truth rule: illustrations are never the source of historical truth. Desk keeps verified geodata independently; any generation distortion (coastline, river, place, border) must be flagged in a registration/distortion QA before the scene is approved.
If the Edward II PoC works -> maps become their own class of generated production plate.

## Map classes (owner, 11:07am ET) — three art treatments in the same generation workflow
- Imperial Atlas: territorial expansion, dynastic holdings, campaigns (Roman Empire ref): rich realm colours, pronounced borders, detailed geography.
- Explorer's Chart: expeditions, voyages, migrations, mysteries (Virginia/Roanoke ref): detailed waterways, coastal illustration, fine engraved features.
- Chronicle Artifact: atmospheric reveals/transitions (candlelit map ref): paper folds, physical lighting, shadow, discovery.
Edward II PoC: Explorer's Chart proposed by Vellum (journey + disputed claim); owner may override.
