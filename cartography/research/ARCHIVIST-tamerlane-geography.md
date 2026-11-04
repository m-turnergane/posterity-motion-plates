# ARCHIVIST: Tamerlane geography brief (internal PoC, not for posting)
Date 2026-10-17 (ET). Public pages only. Captures in cartography/raw/ (new, wp_*) and micro-anomaly/tamerlane/raw/ (reused, wp_Uzbek_SSR.txt etc.). Quotes verbatim from the named capture.

## TOP SUMMARY
1. Samarkand was in the Uzbek SSR (a USSR republic) in 1941; label it "Uzbek SSR", never "Uzbekistan". DOCUMENTED.
2. Coordinates: Samarkand 39.65472 N, 66.97583 E; Gur-e-Amir 39.64833 N, 66.96889 E (Wikipedia coordinates API). Gur-e-Amir is about 1 km from the centre point: show approximate.
3. 22 June 1941 start line (Molotov-Ribbentrop partition line plus 1940 annexations) and the three axes (North, Centre, South) are DOCUMENTED for a map; exact line trace is approximate (we draw it).
4. Berlin to Samarkand = 4,260 km great circle (COMPUTED, haversine, below). VO "over four thousand kilometers" is SAFE. Road or rail is longer and not claimed.
5. Brest to Samarkand 3,563 km, Moscow to Samarkand 2,798 km (computed).
6. Do not show any later frontline. Not captured: Finland/Hungary/Slovakia roles, railways, a distance calculator page (all UNKNOWN here).

## 1. Samarkand in the Uzbek SSR
| Claim | Band | Map | Source |
|---|---|---|---|
| Uzbek SSR created 27 Oct 1924, in USSR the next year: "The next year Uzbekistan became one of the republics of the Union of Soviet Socialist Republics (Soviet Union)." | DOCUMENTED | label Uzbek SSR | [wp_Uzbek_SSR.txt L16] |
| Capital: "In 1930, the Uzbek SSR capital was relocated from Samarkand to Tashkent" (Samarkand's page says capital 1925 to 1930) | DOCUMENTED | n/a | [wp_Uzbek_SSR.txt L18], [wp_Samarkand_full.txt L110] |
| Karakalpak ASSR inside the Uzbek SSR from 5 Dec 1936: "On 5 December 1936, it was moved from the Russian SFSR to the Uzbek SSR." | DOCUMENTED (Wikipedia pages disagree on the previous owner: the Uzbek SSR page says Kazakh SSR; irrelevant to 1941) | show as part of Uzbek SSR, approximate edge | [wp_karakalpak_assr.txt] |
| Tajik SSR separate: "Uzbekistan included the Tajik ASSR until 1929, when the Tajik ASSR was upgraded to an equal status." | QUALIFIED (Wikipedia, upgrade to SSR 1929; Tajik SSR a separate republic in 1941) | draw separate, approximate | [wp_Uzbek_SSR.txt L18] |
| Modern borders differ little; "Further bits and pieces of territory were transferred several times between Kazakhstan and Uzbekistan after World War II." | QUALIFIED | use approximate outline; do not claim an exact 1941 border | [wp_Uzbek_SSR.txt L18] |
| Gur-e-Amir: "a mausoleum of the Turco-Mongol conqueror Timur (also known as Tamerlane) in Samarkand"; "built in the southeastern part of medieval Samarkand" | DOCUMENTED | pin at city, approximate | [wp_gur_e_amir.txt] |
| Coordinates: Samarkand lat 39.65472222, lon 66.97583333; Gur-e-Amir lat 39.64833333, lon 66.96888889 | DOCUMENTED as Wikipedia values | approximate (one pin; at map scale they coincide) | [coords_Samarkand.json], [coords_Gur-e-Amir.json] |
Karakalpakstan since 1992 is an autonomous republic in Uzbekistan [wp_karakalpak_assr.txt]. Karakalpak ASSR to be labelled as part of Uzbek SSR, if labelled at all.

## 2. Front line, 22 June 1941
- Partition: "Poland was to be partitioned ... the areas east of the Pisa, Narew, Vistula, and San rivers would go to the Soviet Union, and Germany would occupy the west." [wp_mrp.txt L58]. DOCUMENTED; the 22 June line was roughly this, drawn by us: approximate.
- 1940 annexations: "The Soviet annexation of Estonia, Latvia, Lithuania and parts of Romania (Bessarabia, Northern Bukovina and the Hertsa region) followed." [wp_mrp.txt L4]. DOCUMENTED; show inside the USSR in a 1941 frame.
- Start: "At around 03:15 on 22 June 1941, the Axis Powers commenced the invasion of the Soviet Union with the bombing of major cities in Soviet-occupied Poland" [wp_barbarossa.txt L84]. DOCUMENTED.
- Axes: "Army Group North was to march through Latvia and Estonia into northern Russia, then either take or destroy the city of Leningrad"; "Army Group Centre ... was to strike from Poland into Belorussia ... and advance to Smolensk and then Moscow"; "Army Group South was to strike the heavily populated and agricultural heartland of Ukraine, taking Kiev" [wp_barbarossa.txt L56]. DOCUMENTED as planned axes: draw as arrows from the start line toward Leningrad, Moscow, Kyiv (labelled "planned axes"), approximate.
- Allies: "Finland slated 14 divisions for the invasion, and Romania offered 13 divisions and eight brigades over the course of Barbarossa." [wp_barbarossa.txt L55]. DOCUMENTED for Finland and Romania. Hungary and Slovakia: UNKNOWN (not captured), do not show as combatants.
- Brest as border point: a representative point of the Centre axis only (our choice, not a sourced claim); Brest coordinates lat 52.13472222, lon 23.65694444 [micro-anomaly/tamerlane/raw/wp_Brest,_Belarus.json]. Approximate.
- Railways (Trans-Caspian reached Samarkand 1888, Turkestan-Siberia, Moscow-Tashkent): UNKNOWN, not captured. Do not draw a rail line. A great-circle line is a computed distance, not a route.
- Do not show 1941 to 1945 advances (Kyiv, Smolensk, Leningrad siege, Moscow offensive appear in the capture's summary, not for the frame).
- USHMM and IWM pages: not captured in this pass (scope cut).

## 3. Distance (computed)
Script cartography/haversine.py. R = 6371.0088 km. a = sin^2(dphi/2) + cos(phi1) cos(phi2) sin^2(dlambda/2); d = 2 R asin(sqrt(a)).
Berlin (52.5200 N, 13.4050 E, wp_Berlin.json) to Samarkand (39.65472222 N, 66.97583333 E): a = 0.1076924, d = 4260.4 km (about 4,260 km; about 2,650 miles).
Brest to Samarkand: a = 0.0761912, d = 3563.4 km. Moscow (55.75583333, 37.61777778; coords_Moscow.json) to Samarkand: about 2,798 km.
Label all "straight line, computed". No public calculator page was captured, so no external cross-check (UNKNOWN). The earlier VERIFY-REV5.md run gave the same 4260.4 and 3563.4.
VO "over four thousand kilometers": SAFE (4,260 straight line exceeds 4,000; road or rail longer). Do not state 4,260 as a sourced figure.

## 4. Labels for a 1941 frame (short)
Use: Soviet Union (USSR), Uzbek SSR, Tajik SSR, German Reich, General Government (the occupied part of Poland; source for this term not captured, so UNKNOWN, label "German-occupied Poland" if unsure). Avoid: Uzbekistan, Belarus, Ukraine, Russia as a state name for the USSR, Kazakhstan, Karakalpakstan, Moldova, any post-1945 borders or NATO/EU labels. Istanbul, Baghdad (Iraq), Delhi (British India): not captured, only needed if the map extends there.

## 5. Sources (access 2026-10-17 ET unless noted)
| Source | URL | License | Capture |
|---|---|---|---|
| Wikipedia, Gur-e-Amir | https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1&redirects=1&format=json&titles=Gur-e-Amir | CC BY-SA | wp_gur_e_amir.json/.txt |
| Wikipedia, Karakalpak ASSR | same API, titles=Karakalpak_Autonomous_Soviet_Socialist_Republic | CC BY-SA | wp_karakalpak_assr.json/.txt |
| Wikipedia, Operation Barbarossa | same API, titles=Operation_Barbarossa | CC BY-SA | wp_barbarossa.json/.txt |
| Wikipedia, Molotov-Ribbentrop Pact | same API, titles=Molotov%E2%80%93Ribbentrop_Pact | CC BY-SA | wp_mrp.json/.txt |
| Wikipedia coordinates (Samarkand, Gur-e-Amir, Moscow) | https://en.wikipedia.org/w/api.php?action=query&prop=coordinates&format=json&titles=Samarkand (also Gur-e-Amir, Moscow) | CC BY-SA | coords_*.json |
| Reused: Wikipedia Uzbek SSR, Samarkand, Berlin, Brest | see micro-anomaly/tamerlane/raw/ | CC BY-SA | wp_Uzbek_SSR, wp_Samarkand_full, wp_Berlin, wp_Brest,_Belarus |
Rights (brief): internal only. For any base map, use Natural Earth (public domain, https://www.naturalearthdata.com, not captured here) and draw 1941 overlays ourselves; do not copy others' maps.
