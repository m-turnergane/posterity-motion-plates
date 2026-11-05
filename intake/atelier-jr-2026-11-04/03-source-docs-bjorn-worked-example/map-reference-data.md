# Björn Ironside: map reference data for P05 (animated map plate)

**Prepared by:** Archivist, 2026-11-03.

**Map text rule:** labels show place names only. No captions, dates or claims go on the plate. Band and style live in this file for Atelier.

**Line styles:**
- DOCUMENTED = solid
- LEGEND = broken (long dash)
- UNCERTAIN placement or order = dotted

Coordinates are WGS84 decimal degrees, rounded to 4 dp, from Wikidata property P625 fetched 2026-11-03. The raw fetch is in raw/geo/wikidata-p625.json.

**Source files cited**

| Short name | File | What it is |
|---|---|---|
| AB | raw/ab-waitz1883-djvu.txt | Annales Bertiniani, ed. Waitz 1883. A contemporary Frankish annal; this section is by Prudentius of Troyes. |
| SB | raw/sagabook-v5-6-djvu.txt | Stefansson, "The Vikings in Spain", Saga-Book VI, 1909, pp. 40 to 42. English translations of the Arabic and Asturian sources. |
| WP-VI | raw/wp-Vikings_in_Iberia.wikitext line 49 | Wikipedia, summarising Christys, Vikings in the South, 2015. |
| GND | raw/jumieges-guizot1826-djvu.txt | William of Jumièges, Guizot French translation of 1826 (LEGEND material). |

**Reliability caveat:** the Arabic writers (Ibn Idhari, Nowairi, Ibn al-Kutia, Bekri) are compilers from the 11th to 14th centuries. They draw on lost earlier annals, so they are not eyewitnesses. The Asturian chronicle (Sebastian of Salamanca, the Chronicle of Alfonso III) is late 9th century and so near-contemporary. AB is strictly contemporary.

**Dead files:** raw/remacle-annales.htm (0 bytes) and raw/fontanell.html (274-byte stub) are empty. Nothing below relies on them.

## 1. Points

| # | Map label | Lat | Lon | Wikidata | Note |
|---|---|---|---|---|---|
| P1 | Loire | 47.2700 | -2.1844 | Q1469 (P625, qualifier: mouth) | Departure anchor, estuary. Noirmoutier, Q292346, is at 46.9923, -2.2583 if an island base is wanted. |
| P2 | Galicia | 42.8000 | -7.9000 | Q3908 | Region centroid, for the label only. Route the line offshore along the northwest coast. |
| P3 | Asturias | 43.3614 | -5.8478 | Q3934 | Region point. Label optional (realm label, see section 4). |
| P4 | Beja | 38.0167 | -7.8667 | Q321455 (district) | The "harbour in the province of Beja" is unidentified, so do not pin it. Optional. |
| P5 | Guadalquivir | 36.7913 | -6.3567 | Q14309 (P625, qualifier: mouth) | River mouth near Sanlúcar (Q210887, 36.7789, -6.3539). |
| P6 | Seville | 37.3886 | -5.9950 | Q8717 | Disputed (see D2). |
| P7 | Algeciras | 36.1275 | -5.4539 | Q484552 | |
| P8 | Strait of Gibraltar | 35.9739 | -5.5161 | Q36124 | Waypoint, label optional. |
| P9 | Nekor | 35.0898 | -3.8075 | Q3537816 | Medieval site. Wikidata's precision is coarse; the emirate item Q1709337 gives 35.1223, -3.6373. Use P9 for the pin. |
| P10 | Orihuela | 38.0848 | -0.9440 | Q24008496 (town) | Tudmir (Cora de Tudmir, Q1225154) has no P625. Orihuela stands for the Tudmir landing. |
| P11 | Mallorca | 39.6167 | 2.9833 | Q8828 | Disputed order (D4). |
| P12 | Menorca | 39.9667 | 4.0833 | Q52636 | Disputed order (D4). |
| P13 | Formentera | 38.7000 | 1.4500 | Q31916364 | Disputed order (D4). |
| P14 | Camargue | 43.5333 | 4.5000 | Q218151 | Winter camp 859 to 860. |
| P15 | Rhône | 43.3342 | 4.8442 | Q602 (P625, qualifier: mouth) | Entry waypoint. Label "Rhône" optional. |
| P16 | Valence | 44.9325 | 4.8908 | Q8848 | |
| P17 | Pisa | 43.7167 | 10.4000 | Q13375 | |
| P18 | (no label) Luna | 44.0640 | 10.0170 | Q579763 (it: "Luna (colonia romana)") | Roman city site. Wikidata precision is 1 arcsec. Cross-check: the Luni archaeological museum on site, Q3867715, has preferred value 44.0644, 10.0171. Magra mouth is Q692549, 44.0455, 9.9891. Keep the pin UNLABELLED, per brief. |
| P19 | Rome | 41.8931 | 12.4828 | Q220 | Legendary target, never reached. |
| P20 | Medina Sidonia | 36.4577 | -5.9273 | Q642200 | Inland town. The battle was "on the coast of Sidona" (the Cora of Sidonia coast, around Cádiz bay). Place the event offshore, west of P7. Dotted. |
| P21 | Pamplona | 42.8167 | -1.6500 | Q10282 | Disputed (D5). |
| P22 | Nîmes | 43.8383 | 4.3597 | Q42807 | Optional, secondary only (D6). |
| P23 | Arles | 43.6769 | 4.6286 | Q48292 | Optional, secondary only (D6). |

**Not supported:** Narbonne (Q6555, 43.1847, 3.0036) and Roussillon. No primary source in hand names either for 859 to 861. AB 859 says only "depopulatisque quibusdam civitatibus ac monasteriis" (unnamed towns and monasteries) on entering the Rhône. Stefansson's "a monastery on the French border" (SB 25666 to 25667) gives no place. **Recommendation: do NOT plot Narbonne or Roussillon.**

## 2. Route segments (in recommended draw order)

| Seg | From to | Date | Band | Style | Citation |
|---|---|---|---|---|---|
| S1 | Loire (P1) to Galicia coast (P2) | 859 | UNCERTAIN (departure point) | dotted | AB 859 does not name a base. The Loire base is a modern inference (WP-Nekor line 5, "from their base on the Loire"). It is supported indirectly by AB 862, which says those "qui in Hispania fuerant" were back with the fleet attacking the Bretons (AB 3645 to 3647). |
| S2 | Galicia coast (P2) southward to Beja coast and Guadalquivir mouth (P5) | 859 | DOCUMENTED (near-contemporary Asturian chronicle, plus Arabic annal) | solid | Sebastian: "Lordomani attacked our coasts (Galicia) the second time. Then they went to Spain" (SB 25643 to 25644). Ibn Idhari: "62 ships on the Western coasts ... arrived at the mouth of the river by Seville" (SB 25570, 25576 to 25577). "(Galicia)" is Stefansson's gloss. |
| S2a | Guadalquivir mouth (P5) to Seville (P6) | 859 | UNCERTAIN (sources disagree) | dotted, or omit | Ibn Idhari has them only at the river mouth (SB 25577, 25580). Nowairi says they took Seville's capital and burnt its grand mosque (SB 25606 to 25607). See D2. |
| S3 | Guadalquivir mouth (P5) to Algeciras (P7) | 859 | DOCUMENTED (Arabic annals) | solid | Ibn Idhari: "sailed to Algeziras, which they took, and where they burnt the grand mosque" (SB 25580 to 25582). Also eswp-Sitio_de_Algeciras_859 (62 ships, 245 AH, citing Ibn Hayyan and Ibn al-Athir). |
| S4 | Algeciras (P7) through the Strait (P8) to Nekor (P9) | 859 (or 858, see D1) | DOCUMENTED (four independent attestations) | solid | Ibn Idhari: "crossed over to Africa" (SB 25582). Bekri: "landed at Nekor ... stayed eight days" (SB 25633 to 25639). Ibn al-Kutia: "After leaving Seville they went to Nekor" (SB 25623). Sebastian: "After sailing through the straits they took Nachor" (SB 25646, 25657). AB 859 also confirms the sea route: "inter Hispanias videlicet et Affricam navigantes" (AB 3292 to 3293). |
| S5 | Nekor (P9) to Orihuela (P10) | 859 | DOCUMENTED (Arabic annals) | solid | Ibn Idhari: "returned to the coast of Spain, landed on the coast of Todmir, and advanced to the fort of Orihuela" (SB 25583 to 25585). Nowairi: "seized the fort of Orihuela" (SB 25609 to 25610). |
| S6 | Orihuela (P10) to Balearics (P13, P11, P12) | 859 | UNCERTAIN (order and route) | dotted | Sebastian only: "attacked the isles of Majorca, Formentera, and Minorca" (SB 25658 to 25659). Sebastian gives them after Nekor but does not mention Orihuela. See D4. |
| S7 | Balearics (or Orihuela) to Rhône mouth (P15) and Camargue (P14) | 859 | DOCUMENTED (Frankish contemporary) | solid | AB 859: "Rodanum ingrediuntur, depopulatisque quibusdam civitatibus ac monasteriis, in insula quae Camarias dicitur sedes ponunt" (AB 3293 to 3295). Ibn Idhari: "sailed to France, and spent the winter there" (SB 25585 to 25586). |
| S8 | Camargue (P14) up the Rhône to Valence (P16) and back | 860 | DOCUMENTED | solid (out and back along the river) | AB 860: "Dani qui in Rodano morabantur usque ad Valentiam civitatem vastando perveniunt ... ad insulam in qua sedes posuerant redeunt" (AB 3441 to 3444). |
| S9 | Camargue (P14) to Pisa (P17) | 860 | DOCUMENTED | solid (coastal arc) | AB 860: "Dani qui in Rodano fuerant Italiam petunt et Pisas civitatem aliasque capiunt, depraedantur atque devastant" (AB 3455 to 3456). Also Ibn al-Kutia, "the Rum-land" (SB 25628 to 25629). |
| S10 | Coastal arc to Luna (P18, unlabelled) | 860 (as legend) | LEGEND | broken | GND ch. IX: "fut jeté par une / tempête auprès de Luna, ville d'Italie" (GND 953 to 954). Dudo's tale. No annal names Luna for 860. AB's "aliasque" (other towns) is unnamed. AB records a Saracen, not Viking, raid on Luna in 849 (AB 2438 to 2440). |
| S11 | Luna (P18) toward Rome (P19), never reached | legend | LEGEND | broken. Stop short of Rome or fade out; do not touch Rome. | GND 952 to 953: "se rendant par mer à Rome / pour la soumettre à la domination de Bier". GND 964 to 965: "résolus d'aller attaquer à l'improviste [la] ville de / Rome". Ch. XI: they discover the city "non esse Romam" (Latin transcription line 1196). |
| S12 | Italy back west to the Strait, Sidona coast (P20) | 861 | Events DOCUMENTED (Arabic annals). Path UNCERTAIN. | dotted | Ibn Idhari: "returned to the coast of Spain ... lost more than forty of their ships (in a storm) ... battle with the fleet of the Emir Mohammed on the coast of Sidona, they lost two others" (SB 25589 to 25600). Nowairi: lost four ships in the battle "On their way back" (SB 25612 to 25614). The path from Italy is not recorded. |
| S13 | Strait (P8) north to the Loire or Brittany coast (P1) | 861 to 862 | Arrival DOCUMENTED (AB 862). Path UNCERTAIN. | dotted | AB 862: "quibus et illi iunguntur qui in Hispania fuerant" (AB 3646 to 3647). |
| S14 | Pamplona (P21), García's ransom | 859 to 861, placement disputed | UNCERTAIN | dotted marker only. Recommend NO connecting line. | Nowairi: "went all the way to Pampelona, and made prisoner its Frankish lord, Garcia. His ransom was 90,000 dinars (70,000 dinars, Ibn-Khaldun)" (SB 25617 to 25619). Christys: "Banbalūna ... may or may not reflect activities of Vikings" (WP-VI line 49). See D5. |

**Excluded on purpose:**
- Greece and Alexandria. Sebastian says "Finally they sailed to Greece" (SB 25660). Ibn al-Kutia says "Alexandria" and a "fourteen years" expedition (SB 25627 to 25629). These are UNCERTAIN, outside the plate, and would dilute the Rome beat.
- Narbonne and Roussillon (unsupported, see section 1).

## 3. Disputes (where sources disagree)

- **D1. Nekor date.** Bekri dates it to 244 AH (19 April 858 to 7 April 859; SB 25633 to 25634). Ibn Idhari puts the whole voyage in 245 AH (8 April 859 to 27 March 860; SB 25569). WP-VI line 49 says the link of the Nekor raid to Hastein and Björn is "modern extrapolation".
- **D2. Seville.** Ibn Idhari has the fleet at the river mouth only, then Algeciras, where the mosque is burnt. Nowairi has Seville's capital taken and its grand mosque burnt (SB 25606 to 25607). Nowairi may be conflating this with the 844 sack of Seville (my interpretation). Draw the solid line to the river mouth only; Seville is dotted or omitted.
- **D3. Order of Africa and Spain.** The Arabic writers give: river mouth, then Algeciras, then Africa (Nekor), then Todmir/Orihuela, then France. Sebastian gives: Galicia, then Spain, then the straits, then Nachor, then the Balearics, then Greece. These are compatible, but neither has the full sequence.
- **D4. Balearics placement.** Only Sebastian has the Balearics. Whether they come before or after Orihuela is unknown. Stefansson's synthesis puts them before the Rhône (SB 25665 to 25668), so draw dotted.
- **D5. Pamplona.** Nowairi puts it after the battle "on their way back" (SB 25612 to 25617). Stefansson puts it before the Rhône (SB 25665 to 25666), and his footnote says "They could only get to Pampelona from the Bay of Biscay" (SB 25648). Christys doubts it was Vikings at all. Marker only, dotted.
- **D6. Nîmes and Arles.** These come only via Stefansson's synthesis, citing "Chron. Nem." (SB 25668), which I have not seen. AB 859 says only "unnamed towns and monasteries". Optional dotted pins; recommend omit.
- **D7. Frankish vs Arab framing of the winter.** Arab: "sailed to France, and spent the winter there ... masters of a city where they settled" (SB 25585 to 25588). Frankish: the island Camargue (AB 3295). These are compatible. The "city" is unidentified.
- **D8. Leaders.** No 9th-century source names a leader for 859 to 861. Björn and Hastein appear only in Dudo and William, the latter c. 1070 (LEGEND). The map shows no leader names.

## 4. Realm framing c. 860 (loose, low-contrast fills)

The preferred source is OpenHistoricalMap (OHM; data CC0). I queried it via the OHM Overpass API on 2026-11-03 (raw/geo/ohm.json and ohm3.json). The bbox values below are OHM relation extents.

| Realm (label) | Ruler c. 860 | Rough extent | OHM relation (dates) | Wikidata | Note |
|---|---|---|---|---|---|
| West Francia | Charles the Bald | Gaul west of roughly the Scheldt, Meuse, Saône and Rhône. Excludes Brittany. Includes Aquitaine, Septimania and the Spanish March to roughly the Llobregat. | 2750107 (843-08-10 to 867-08). Extent S39.09 W-2.76 N51.45 E5.74. | Q46370 | The southern extent S39.09 looks odd (possibly the Balearics are included). Check before use. |
| Brittany | Salomon (AB 862, "Salomone duce") | The Breton peninsula and the counties east to roughly Rennes and Nantes. | 2805415 (851-09 to 867-08) | Q771193 | Recommended: relevant to S1 and S13. |
| Lotharingia | Lothar II (855 to 869; general knowledge) | Frisia south to the Jura, between the Meuse/Scheldt and the Rhine. | 2806711 (855-09-19 to 870-08-08) | Q6673921 | This is the third part of the 855 division. Not on the user's list but needed for continuity. |
| Provence | Charles of Provence (855 to 863) | Rhône valley from roughly Lyon south to the sea, east to the Alps. Contains the Camargue, Arles and Valence. | **Not in OHM.** | Q33242 ("Lower Burgundy"; Charles is Q333802) | Fallback: trace from Commons "File:Shepherd-c-056.jpg" (Shepherd 1911, "Disruption of the Carolingian Empire, 843 to 888", public domain). Second option: "File:Vertrag von Prüm.svg" (CC BY-SA 4.0, Furfur; attribution plus share-alike). Important: S7, S8 and S9 all happen inside Provence, not West Francia. |
| Kingdom of Italy | Louis II (king and emperor) | Northern and central Italy south to roughly the Papal and Spoletan line. Contains Pisa and Luna. | **Not in OHM.** | Q838931 (Louis II is Q215204) | Same fallback (Shepherd plate 56). |
| East Francia | Louis the German | East of the Rhine. Only the southwest corner (Alamannia) touches the frame. | **Not in OHM for 860.** | Q153080 | Edge of frame only. Shepherd fallback. |
| Papal lands | the pope | Rome, Latium, and the former Exarchate strip to Ravenna. | 2888203 (800 to 988). Extent S41.37 W10.41 N45.15 E13.68. | Q170174 | |
| Southern Lombard and Tyrrhenian states | various | Benevento, Capua and Salerno inland; Naples and Sorrento on the coast. | Benevento 2888914 (851 to 899); Capua 2888915 (861 to 899, starts 861); Naples 2888433; Sorrento 2888516 | Benevento Q131573029, Capua Q1280122, Naples Q1051600, Salerno Q1065299 (Salerno not in OHM) | Optional, small. |
| Emirate of Bari | | The Apulian coast around Bari. | 2860176 (847 to 871) | Q1878022 | Optional. |
| Byzantine southern Italy (Eastern Roman Empire) | Michael III (general knowledge) | Calabria, the Otranto heel, eastern Sicily. | 2860243 (847 to 871). Extent W1.14 suggests the Balearics are included as Byzantine; check. | Q12544 | |
| Aghlabids (Ifriqiya; Sicily in progress) | | Tunisia and eastern Algeria, plus western and central Sicily. | 2860230 (846 to 870). Extent S31.03 W2.18 N40.73 E18.57. | Q207600 | For "in progress", use a hatched or soft edge on Sicily. Palermo held since 831. Conquest finished with Syracuse in 878 (general knowledge, not verified this session; flag). |
| Emirate of Córdoba | Muhammad I (852 to 886; SB footnote 25591) | Most of Iberia south of the Duero and Ebro uplands. Includes Beja, Seville, Algeciras and Tudmir. | 2697816 (756-05-15 to 902). Extent S35.96 W-9.61 N41.71 E0.57. OHM licence tag CC0-1.0. | Q1337854 | |
| Asturias | Ordoño I (850 to 866; SB 25643) | The northern coastal strip, Galicia to roughly Álava. | 2740129 (860 to 909). An earlier relation, 2740130, covers 814 to 859. | Q231392 | Use 2740129. For an 859 frame use 2740130; the two differ only in the southern edge. |
| Pamplona | García Íñiguez (SB footnote 25649, "King of Navarre, A.D. 857-882") | A small western Pyrenean realm around Pamplona. | 2740068 (824 to 904). Extent S42.41 W-2.37 N43.36 E-0.72. | Q3446210 | |
| Nekor | Banu Salih (SB 25626) | The Rif coast strip around Nekor. | **Not in OHM.** | Q1709337 | Loose label only, no hard border. |
| Idrisids | Idrisid princes; the realm was divided c. 860 | Northern Morocco inland: Fez, Tangier hinterland. | **Not in OHM.** | Q431575 | Loose label only. |

Also present in OHM: the Duchy of Venice, 2839584. It is at the frame edge and not needed.

**Fallback map sources (Commons, checked 2026-11-03 via the API):**
- File:Shepherd-c-056.jpg: public domain, Shepherd Historical Atlas 1911, plate "Disruption of the Carolingian Empire, 843-888". Preferred fallback.
- File:Vertrag von Prüm.svg: CC BY-SA 4.0, Furfur. Shows the 855 division. Attribution plus share-alike.
- File:Carolingian territorial divisions, 855.png: CC BY-SA 3.0.

## 5. Plate framing

**Full route bbox (recommended):** W -11.0, E 15.5, S 34.5, N 48.0.
- This covers the Loire (47.27N), Galicia, Nekor (35.09N), the Balearics, Valence, Pisa and Rome, with margin. It includes western Sicily and the Aghlabid coast at the edge.
- At web-mercator, this is roughly 26 by 13.5 degrees, a landscape shape.
- For a 9:16 vertical short, use a pan:
  1. Open on the Iberia frame: W -10.5, E 5.5, S 34.5, N 48.0.
  2. Pan east to the Rhône and Italy frame: W 3.5, E 13.5, S 40.5, N 46.0.

**Luna to Rome inset (legend beat):** W 8.8, E 13.2, S 41.3, N 44.6.

## 6. Label list (place names only)

**Labels:** Loire, Galicia, Guadalquivir, Algeciras, Nekor, Orihuela, Mallorca, Menorca, Formentera, Camargue, Rhône, Valence, Pisa, Rome.

**Optional labels:** Seville, Pamplona, Strait of Gibraltar.

**Unlabelled pin:** Luna (P18).

**Realm labels as needed:** West Francia, Brittany, Provence, Kingdom of Italy, Papal lands, Emirate of Córdoba, Asturias, Pamplona, Nekor, Aghlabids.
