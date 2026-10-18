# PoC C: animated cartography (Tamerlane) — design and plan

Status: DESIGN ONLY, INTERNAL PoC. Never posted. Historical accuracy is out of scope; the goal is look/feel and workflow numbers (authoring time, render time, reuse). Branch `dev/poc-c-cartography`, design doc only; no code beyond an optional spike.

## 1. The owner's base map (observations)
File: `assets/basemaps/tamerlane_eurasia_painted.png` (owner-supplied, 941x1672, aspect 0.563 = 9:16 within 0.1%, 3.5 MB, md5 `1004379863d6234fce808a05654cd055`; gitignored, md5 recorded in `assets/basemaps/README.md`).
- Style: painted parchment atlas; deep-blue seas with faint graticule arcs, ochre/olive/rust land tints per region, hillshaded mountains (Himalaya/Tian Shan/Pamir snow ridges, Zagros), thin pale internal borders, a burnt/torn parchment frame. Fits the Posterity warm-amber palette.
- Coverage: Black Sea/Anatolia, Levant, Egypt/Arabia, Persia, Central Asia, India, Horn of Africa; Caspian/Aral in the middle, Russia and Siberia in the top third. Samarkand sits near the centre (about 62% x, 40% y), which suits a hinge.
- Baked in (not clean): glowing orange pins plus small serif labels CONSTANTINOPLE (~x 40/461, y 289/819), BAGHDAD (~139,380), DELHI (~354,437), SAMARKAND (~287,328, larger, with glow rays). Small labels (about 18 px tall at full res) would be soft/blurry once cropped and zoomed; "Constantinople" is at the far-left edge, so a 9:16 crop at 1.0x barely keeps it.
- Text/glyph issues: labels are raster, slightly smeared; any other tiny text is painted noise. Place names are from the image generator, so spellings must be eyeballed. Borders are painterly and are not real political borders, so they must not be treated as territory.
- Margins: the map is already 9:16, so zoom 1.0 = the full map. Camera zoom > 1 crops inward; keep the burnt border out of frame at zoom >= 1.15 or accept it as a vignette. Edge cities (Constantinople) need zoom <= 1.6 with a pan to stay clear of the border.
- Treatment of baked pins/labels (choose one, spike both): (a) inpaint them out with a mask (OpenCV Telea/patch fill over ~40x20 px boxes; terrain is noisy so this works) and re-add live markers and type; (b) leave them and overlay animated markers exactly on top, accepting a double-pin at the frame start. Recommendation: (a), because an animated pin that grows out of a clean map reads better and avoids the doubled glow. Keep the original as fallback.
- Questions for the owner: is a clean (no pins/labels) variant available? Higher resolution (2x) for zooms? Should Samarkand's label be kept as the "hero" baked marker?

## 2. Layer architecture (Python/OpenCV, same engine family as Motion Plates)
1. base: painted map, optional inpainted clean variant (static, 2x upscaled for zoom).
2. political: soft territory tints (hand-drawn polygons, feathered, animated fill/spread).
3. tactical: route paths (Bezier/polyline, solid or dashed "approximate"), moving glow head, army icon, arrows, city pins with pulse.
4. annotation: labels (own font, ink-on-parchment shadow), dates, small captions.
5. camera: keyframed pan/zoom/rotate-free move with easing and slight parallax of a mist/dust layer; vignette.
6. fx: ink-stain reveal, burn edge, glow, dust motes.
Everything is resolution independent (coordinates in map-normalised units 0..1), rendered at 1080x1920 from a 2x map.

## 3. Recipe primitives (YAML, timing keyed to the VO)
```
map: {base: tamerlane_clean, size: [1080,1920], fps: 30}
vo:  {alignment: vo_alignment_tamerlane_rev6.json}
events:
  - {at: {word: "Samarkand", occ: 1}, do: pin, id: samarkand, label: "SAMARKAND", style: hero}
  - {at: {word: "Delhi"}, do: route, from: samarkand, to: delhi, via: [[.5,.4],[.55,.5]], style: dashed_approx, dur: 2.0}
  - {do: region_fill, polygon: ..., color: ember, dur: 1.5}
  - {do: camera, to: {center: [.62,.4], zoom: 1.6}, dur: 2.0, ease: inout}
```
`at` can be seconds, a word from the alignment json (so retimed VO re-times the map), or `after: <event>`. Primitives: pin, label, route(solid|dashed_approx), region_fill, arrow, icon_move, camera, vignette, dust. Presets: ink_reveal, glow_route, pulse_pin.

## 4. Narration-keyed storyboard (loose; from VERIFY-REV6 + alignment)
Word times (s): Soviet 0.2, tomb 1.5, cities 3.8, Days later 5.4, Hitler invaded 6.8, Timur 8.9, Central Asian conqueror 10.0-11.3, Tamerlane 12.3, Samarkand 17.9, kilometers east of Berlin 21.3-22.4, Directive 41.9, closer 50.7-54.6.
- Deliverable A, vertical hinge (8-12 s, VO 8.0-18.5): wide map at 1.0 -> "That man was Timur" (8.9) Samarkand pin pulses and the camera eases in to 1.5 on Samarkand by 11 -> "Central Asian conqueror" (10.0) faint territory glow spreads -> "Samarkand" (17.9) hero label ink-in. Ends on a held composition (cuts to a documentary beat).
- Deliverable B, multi-event prototype (20-30 s, VO ~3.5-30): a) "destroyed cities" (2.8-3.8): dashed approximate red routes from Samarkand toward Delhi (1398), Baghdad (1401), Anatolia; pins ignite as each city is touched (loose reading of the verified list: Delhi ruined, Baghdad destroyed, Damascus burned, Astrakhan). b) Camera tours Delhi -> Baghdad -> Constantinople region in ~6 s each. c) "Samarkand lay in Soviet Uzbekistan, 4,000 km east of Berlin" (17.9-22.4): camera pulls out west, a thin measuring line Samarkand -> (approx) Berlin off-map, labelled as an arrow "-> Berlin" at the top-left edge. d) Closer: vignette darkens, all routes fade except the Samarkand pin.
The map has no Berlin; (c) uses an off-map arrow. Anything uncertain uses the dashed "approximate" style, nothing else is sourced for this internal PoC.

## 5. Workflow numbers (estimates, to be measured by the spike)
| Item | Estimate |
|---|---|
| One-time: clean base + 2x upscale, label font, 4 city coords | 1-2 h |
| Authoring A (8-12 s): ~6 events, camera, tuning | 1.5-2.5 h first, ~45 min once presets exist |
| Authoring B (20-30 s): ~15 events, 4 camera moves | 4-6 h first, ~1.5-2 h from a template |
| Render 1080x1920x30 | ~6-10 fps CPU full-res (simple 2D layers, one cached base): A ~1 min, B ~2-4 min; proxy 270x480 ~10x faster |
| Reuse | base, icon set, presets, camera moves and map coordinates reused across any Eurasia episode; per-episode work is the event list (30-60 min once the library exists) |
| Storage | base 3.5 MB (not in git), clips ~15-25 MB each |

## 6. Risks
- Painterly map = soft zoom detail (mitigate: 2x upscale + paper-grain overlay, cap zoom at 1.8).
- Baked pins/labels (see above). Labels vs painted noise legibility (mitigate: ink shadow plate).
- Dashed-route readability at 9:16 mobile sizes (mitigate: 6 px+ stroke, glow).
- Over-animating: keep 2-3 simultaneous elements.

## 7. Minimal spike (optional, ~3 s)
Route reveal Samarkand -> Delhi (dashed) with a glowing head plus a 1.0 -> 1.5 camera push on the owner's map, overlaid on top (option b), caption "INTERNAL POC". Pass criteria: smooth sub-pixel camera, dashed pattern without crawling, legible at 1080x1920.

## 8. Scaling from "selected" to "most sequences"
- Effect/preset library: pin/route/region/camera presets keyed by name so each video is a short event list.
- Auto-suggestion: city/region anchors from a gazetteer (lat/lon -> map UV via 4-6 control points fitted once per base map); routes auto-curved between anchors; the author edits only.
- Per-sequence-type templates: "campaign map", "territory spread", "timeline hop".
- Batch and proxy: render all maps of a video at 270x480 for review (about 10x faster), then final render only approved ones overnight.
- QC automation limits: can check bounds, label overlap, safe zones, frame-to-frame jitter and determinism hash; cannot judge taste, label sense or whether motion looks right, so the human playback gate stays.
- Budget per video (12-14 plates, maybe 2-3 map plates): authoring ~20-40 min per plate once presets exist; render ~2-4 min per plate, ~1 h for a full video including retries; storage ~0.3 GB/video of final MP4 plus clean cache.
- Adoption path: spike (internal) -> A+B internal review -> 1 pilot video with static fallback -> templates -> opt-in per sequence; static fallbacks always kept.

## 9. Requests
Clean basemap (no pins/labels) if one exists; a 2x version; confirmation to inpaint labels (a) vs overlay (b); target look for route style (ink dashed vs glowing).
