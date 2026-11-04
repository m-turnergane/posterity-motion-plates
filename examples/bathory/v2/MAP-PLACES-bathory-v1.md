# MAP-PLACES-bathory-v1 (Archivist, 2026-10-31 ~11:55 ET)
For the B03 Upper Hungary reference (9:16). Coordinates are from Wikidata P625 (WGS84), pulled live today. Map text is place names only, with spelling matched to the VO.

## Pins (story)
| On-screen name | Wikidata | Lat, Lon | Band | Note |
|---|---|---|---|---|
| Csejte (fortress) | Q612364 Čachtice Castle | 48.7247, 17.7608 | VERIFIED | Hilltop ruin where she was confined. Pin this one. |
| Csejte (manor, village) | Q337440 Čachtice | 48.7122, 17.7872 | COARSE | This is the village coordinate. The manor where she was arrested stood in the village, below the castle, and has no separate Wikidata point of its own. Use one "Csejte" label and keep the castle/manor split for the inset. |
| Bytča | Q1968071 Bytča Castle | 49.2200, 18.5592 | VERIFIED | Thurzó's seat, where the servants were tried in Jan 1611. The town is Q27907 at 49.2228, 18.5581. |

## Frame anchors (unlabelled, or labelled only if the owner wants them)
| Name | Wikidata | Lat, Lon | Note |
|---|---|---|---|
| Vienna | Q1741 | 48.2083, 16.3725 | West edge anchor. |
| Pozsony (today Bratislava) | Q1780 | 48.1517, 17.1093 | Royal Hungary's capital and coronation town in 1610. If labelled, use "Pozsony"; never "Bratislava" on a 1610 map. |
| Vágújhely (today Nové Mesto nad Váhom) | Q376987 | 48.7833, 17.8333 | Váh town just east of Csejte; optional. |
| Trencsén (today Trenčín) | Q145002 | 48.8942, 18.0406 | Optional midpoint up the Váh between Csejte and Bytča. |
| Zsolna (today Žilina) | Q25797 | 49.2167, 18.7333 | Optional NE anchor beside Bytča. |

## Rivers
- Váh (Hungarian Vág), Q202598: runs NE to SW past Bytča, Trenčín and Csejte (just east of the castle), then south to the Danube near Komárom. Take the geometry from Natural Earth or OSM, not from the painting.
- Danube, Q1653: the southern frame line, from Vienna through Pozsony eastward.

## Suggested frame (9:16)
About 47.9 to 49.5 N and 16.3 to 19.0 E. That fits Vienna to Bytča, with the Danube along the bottom and the Little and White Carpathians between Pozsony and Csejte. The distance from Csejte to Bytča is about 80 km in a straight line, up the Váh valley.

## Realms in 1610 (fills only, coarse)
- Kingdom of Hungary (Royal Hungary; the king was Matthias II from 1608): the whole frame east of the March/Morava river. VERIFIED.
- Archduchy of Austria: west of the March/Morava, including Vienna. VERIFIED.
- Margraviate of Moravia (Bohemian Crown): north-west of the White Carpathians. COARSE.
- Poland: only if the frame reaches past the Beskids north of Bytča. COARSE.
- The Ottoman frontier lies south of the Danube bend and is out of frame. Don't paint it in.
- Boundary source: OpenHistoricalMap (CC0), the same recommendation as the Edward realms file.

## Must-nots
- No modern borders or names (Slovakia, Bratislava, Austria-Hungary).
- No pin at Sárvár or Vienna for the arrest. The arrest was at the Csejte manor, and the confinement in the Csejte fortress.
- No label besides the place names. No dates or status words on the map.

## Correction (12:10 ET), after Atelier's taller 9:16 frame
- Ottoman frontier: I was wrong that it lies "out of frame" once the frame reaches 47.8 N. Esztergom was retaken by the Ottomans in 1605 and held until 1683 (Wikipedia, Esztergom), so in 1610 there's Ottoman ground on the Danube in the far SE corner. OHM's single 1540 to 1669 polygon is generalized across the whole period, so its northern reach to about 48.3 N is not reliable for 1610 specifically. Ruling: leave it untinted (the plate has no painted borders anyway). If it ever gets a tint, keep it to the Danube bank around Esztergom, banded COARSE.
- Missing Hungary counties (Komárom, Esztergom, Hont, Győr): fine for a fills-only mask; mark it COARSE.

## B03 v2 refpack verification (12:25 ET): PASS
- Pins match exactly: Csejte Q612364 48.72472, 17.76083; Bytča Q1968071 49.22000, 18.55917; the manor is the COARSE stand-in Q337440. Csejte = Čachtice, Slovakia (Wikidata) is CONFIRMED.
- Váh (OSM rel 3509398, Q202598): its nearest point is about 6.5 km east of the Csejte castle and about 0.6 km south of Bytča Castle, so the refpack's claim that it "passes east of Csejte, SW of Bytča" holds.
- 1610 border: the Hungary/Moravia line along the White Carpathians and Javorníky is the long-standing frontier, essentially today's SK/CZ line there. The 20% Moravia wedge is correct and unavoidable.
- Ottoman overlap is 0%, so the earlier corner issue is gone. Pozsony and Vienna are off-frame, which is correct.
- Label caveat: present-day names (Slovakia, Bratislava) must not sit in the 1610 label layer. If present-day context is wanted, use one separate overlay worded as today ("Csejte, today Čachtice, Slovakia"). Bratislava/Pozsony is off-frame in v2, so don't label it.
