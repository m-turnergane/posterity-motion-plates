# REALMS-1327-v1: political fills for the c.1327 realms map (Atelier, maps v2)

Prepared by Archivist's research hand, Fri 30 Oct 2026, 19:41 EDT. For Atelier's realms mode: soft colour fills, Western Europe frame, no realm names on screen. Place names are the only on-screen text (owner rule).

Conventions. Text in double quotes is verbatim from a capture in raw/ and is machine-checked by raw/_verify_quotes.py. Everything else is my wording. Wikipedia is used for political-status basics only and is cited as such. Statuses:
- VERIFIED: fill with confidence (edge may still be soft where noted).
- COARSE: fill, but soft, blended or partial edge; do not imply a precise line.
- NEUTRAL: leave unfilled or flat grey.

Reference moment: spring to autumn 1327 (Edward II deposed January 1327; Edward III's reign begins 1 February 1327). Where something changes in 1328 or later, the 1327 state is given.

## 1. Polity list, c.1327

### British Isles

| # | Polity | Status | Fill guidance | Reason and source |
|---|---|---|---|---|
| R01 | Kingdom of England | VERIFIED | England hue (the feature's home colour). | Crown of Edward III from 1 February 1327: "At the beginning of Edward III's reign on 1 February 1327" (raw/realms-wp-Hundred_Years_War.txt). OpenHistoricalMap (OHM) has a live 1327 polity, relation r2802023, Kingdom of England, 1283 to 1513 (raw/realms-ohm-relations-1327.txt), and it contains Carlisle, Cardiff and Caernarfon in a 1327 point test (raw/realms-ohm-isin-1327.txt). |
| R02 | Wales (Principality plus marcher lordships) | VERIFIED, filled with England, no internal line | Same England hue. No border between England and Wales, and no line between the Principality and the March. If Atelier wants nuance, at most a very slightly lighter tint of the England hue over the March, blended, never a line. | Principality: under the Statute of Rhuddlan it became "effectively an annexed territory of the English crown" and was "annexed and united" to the crown (raw/realms-wp-Principality_of_Wales.txt). March: marcher lords held rights "exercised to some extent independently of the king of England" (raw/realms-wp-Welsh_Marches.txt). Both are under the English crown, so one fill; the March nuance is why no sub-border should be drawn. |
| R03 | Kingdom of Scotland | VERIFIED as a separate fill; border COARSE | Its own hue, clearly distinct from England. Border soft. Berwick sits on the Scottish side in 1327. | Robert I's kingdom; in 1324 "the Pope recognised Robert I as king of an independent Scotland" (raw/realms-wp-Robert_the_Bruce.txt). In 1327 "the Scots invaded northern England and defeated the English at the Battle of Stanhope Park in Weardale" (raw/realms-wp-Treaty_of_Edinburgh-Northampton.txt). English recognition only came in 1328, which fixed the border "as that recognised under the reign of Alexander III" (same file). Berwick: Scots captured it "in April 1318" and "England retook Berwick the day after the Battle of Halidon Hill in 1333" (raw/realms-wp-Berwick-upon-Tweed.txt). OHM 1327 point test puts Berwick in r2869806 Kingdom of Scotland (raw/realms-ohm-isin-1327.txt). |
| R04 | Ireland: English lordship | COARSE, partial | England-family tint (lighter than England), only over the east and south-east (Dublin and its hinterland, Meath, coastal Leinster) and feathered outward. Do NOT reach the west or north-west. | Kings claimed the whole island "but in reality the king's rule only ever extended to parts of the island" (raw/realms-wp-Lordship_of_Ireland.txt). The lordship was in decline after the Bruce invasion, the campaign ending "in 1318 at the Battle of Faughart" (raw/realms-wp-Bruce_campaign_in_Ireland.txt). In 1327 itself Robert I was in Ulster: "Before this, Bruce invaded Ulster in Ireland" (raw/realms-wp-Treaty_of_Edinburgh-Northampton.txt). Exact 1327 extent is not established in my captures, hence COARSE. |
| R05 | Ireland: Gaelic lordships | NEUTRAL | Leave unfilled or flat grey; no hue. | The rest of the island "remained under the control of various Gaelic Irish kingdoms or chiefdoms" (raw/realms-wp-Lordship_of_Ireland.txt). Many small polities; filling them would require borders no source here supports. |

### France and its great fiefs

| # | Polity | Status | Fill guidance | Reason and source |
|---|---|---|---|---|
| R06 | Kingdom of France, royal domain | VERIFIED as a fill; outer edge COARSE | France hue. | Charles IV was "King of France and King of Navarre (as Charles I) from 1322 to 1328" (raw/realms-wp-Charles_IV_of_France.txt). Lyon belongs inside: its incorporation into France was formalized "in a 1312 treaty" (raw/realms-wp-Kingdom_of_Arles.txt). The royal domain versus fiefs patchwork is not mapped precisely in any open source I checked (see section 2), so the domain and its fiefs should read as one France family. |
| R07 | Gascony (English-held duchy under French suzerainty) | COARSE | England hue, soft and smaller than any default dataset shape: a coastal band around Bordeaux and down toward Bayonne, feathered inland. Not Agenais, not Saintonge. | After Saint-Sardos the English king's continental holdings "were limited roughly to provinces in Gascony (and Bordeaux)", and "the only part of Aquitaine that remained in his hands was the Duchy of Gascony" (raw/realms-wp-Hundred_Years_War.txt). Charles IV would drop total forfeiture "if Edward II ceded the Agenais to him" (raw/realms-wp-War_of_Saint-Sardos.txt). The 1325 truce allowed "nominal occupation of what was left of the Duchy of Aquitaine" while "real control would remain with Edward II's garrisons" (same file). The status is legally murky in 1327, hence COARSE. The final peace of 1327 is not captured (no Wikipedia article exists at Treaty_of_Paris_(1327); I fetched it and it was empty), so its terms are a GAP here. |
| R08 | County of Flanders (Royal Flanders, French fief) | COARSE, blended | Blend of the France hue and a neutral, or a soft gradient between France and Empire. No hard line anywhere around Flanders. | "the core area under French suzerainty was west of the Scheldt" (raw/realms-wp-County_of_Flanders.txt). |
| R09 | Imperial Flanders (east of the Scheldt, Imperial fief of the same count) | COARSE, blended | Let the Flanders blend fade into the Imperial hue across the Scheldt. | It was "held in fief of the Holy Roman Emperor by the Count of Flanders" (raw/realms-wp-Imperial_Flanders.txt). Same count, two overlords: the reason for no hard border. |
| R10 | Duchy of Brittany | COARSE | France-family tint (slightly different value from the domain), soft edge. Not a separate realm colour. | Duke John III ruled until he "died in 1341 without a succession plan" (raw/realms-wp-Duchy_of_Brittany.txt). A French fief in 1327; its autonomy is real but it was not a kingdom, so a France-family tint is the honest fill. OHM has r2805398 Duchy of Brittany live in 1327 (raw/realms-ohm-relations-1327.txt). |
| R11 | Duchy of Burgundy | COARSE | France-family tint, soft edge. Do NOT merge with the County of Burgundy in 1327. | "Hugh V died in 1315; his brother Odo IV succeeded" (raw/realms-wp-Duchy_of_Burgundy.txt). Union with the county only begins later: "From 1330 to 1361 and again from 1405 to 1477, there was a personal union between the county (part of the HRE) and the adjacent duchy (part of France)" (raw/realms-wp-Free_County_of_Burgundy.txt). |

### Holy Roman Empire (western rim)

General rule: one Imperial hue for the whole western Empire, soft, with no internal lines. The constituent states below are listed so Atelier knows they sit INSIDE that hue, not so they get their own colours. Context: Louis IV was "King of the Romans from 1314, King of Italy from 1327, and Holy Roman Emperor from 1328" (raw/realms-wp-Louis_IV,_Holy_Roman_Emperor.txt).

| # | Polity | Status | Fill guidance | Reason and source |
|---|---|---|---|---|
| R12 | Duchy of Brabant | VERIFIED as Imperial | Imperial hue; no own fill. | "The Duchy of Brabant was a state of the Holy Roman Empire, established in 1183" (raw/realms-wp-Duchy_of_Brabant.txt). |
| R13 | Archbishopric (Electorate) and city of Cologne | VERIFIED as Imperial; city-versus-archbishop split COARSE | Imperial hue; do not separate the city. | After Worringen (1288) the archbishop was "forced to grant the city near-complete autonomy" (raw/realms-wp-Electorate_of_Cologne.txt), but the same article says "The Free Imperial City of Cologne was recognized after 1475". OHM dates the free city from 1288 (raw/realms-ohm-relations-1327.txt). Sources differ on the formal status, so no separate fill. |
| R14 | County of Savoy | VERIFIED as Imperial | Imperial hue. | "In 1313, Count Amadeus V the Great officially gained the status of Imperial immediacy from Emperor Henry VII" (raw/realms-wp-County_of_Savoy.txt). |
| R15 | County of Burgundy (Franche-Comte) | VERIFIED as Imperial; edge with the duchy COARSE | Imperial hue. | Held in her own right by Joan II, "the countess of Burgundy from 1303" and "queen of France by marriage to Philip V from 1316 to 1322" (raw/realms-wp-Joan_II,_Countess_of_Burgundy.txt). So the brief's check holds: in 1327 it is the widowed French queen's own county, not French royal land. Besancon was a free imperial city (raw/realms-wp-Free_County_of_Burgundy.txt). |
| R16 | Dauphine of Viennois | VERIFIED as Imperial | Imperial hue. Not French in 1327. | "It became a state of the Holy Roman Empire in the 11th century" and "In 1349, the Dauphiné was transferred" to the future Charles V (raw/realms-wp-Dauphiné.txt). OHM r2892602 Dauphiné of Viennois, 1282 to 1349, contains Grenoble (raw/realms-ohm-isin-1327.txt). |
| R17 | County of Provence (Kingdom of Arles, held by the Angevins of Naples) | COARSE | Imperial hue, softened or slightly blended toward neutral. Includes the city of Avignon. | Robert of Anjou was "Count of Provence and Forcalquier from 1309 to 1343" (raw/realms-wp-Robert,_King_of_Naples.txt). The Arles article: "since the 14th century the imperial rule over the kingdom became mainly nominal" (raw/realms-wp-Kingdom_of_Arles.txt). The Provence article says Provence was an Imperial fief "which it remained until 1246" (raw/realms-wp-County_of_Provence.txt), which conflicts with the Arles framing. A conflict between sources, so COARSE. |

### Papal enclave and Avignon

| # | Polity | Status | Fill guidance | Reason and source |
|---|---|---|---|---|
| R18 | Comtat Venaissin (papal) | COARSE (tiny) | At Western Europe scale it is a few pixels. Either NEUTRAL or a barely visible papal tint, and only if it can be drawn WITHOUT the city of Avignon. Safest: leave it inside the Provence/Imperial softness. | "a part of the Papal States from 1274 to 1791"; it surrounded Avignon, "itself always a separate comtat" (raw/realms-wp-Comtat_Venaissin.txt). |
| R19 | City of Avignon | VERIFIED as NOT papal territory in 1327 | Same fill as Provence (R17). No papal tint. It may carry the place-name label Avignon, nothing more. | "Avignon was sold to the papacy by Joanna I, Queen of Naples and Countess of Provence, in 1348" (raw/realms-wp-Comtat_Venaissin.txt). Popes resided there but did not own it: "Between 1309 and 1377, during the Avignon Papacy, seven successive popes resided in Avignon and in 1348 Pope Clement VI bought the town from Joanna I of Naples" (raw/realms-wp-Avignon.txt). Robert's article: "the papal enclave within Robert's Provence" (raw/realms-wp-Robert,_King_of_Naples.txt). WARNING: OHM's 1327 point test puts Avignon inside r2851366 Comtat Venaissin and r2888199 Papal States (raw/realms-ohm-isin-1327.txt). That is wrong for 1327; override it. See also ledger C14b (do not show the papal palace). |

### Northern Italy

| # | Polity | Status | Fill guidance | Reason and source |
|---|---|---|---|---|
| R20 | Milan (Visconti lordship) | COARSE | No distinct Milan fill. Treat Lombardy as the soft southern fringe of the Imperial hue, or NEUTRAL. | In 1327 the lordship was in suspension. Louis IV was crowned in Milan at Pentecost 1327, and "the Lord of Milan Galeazzo I Visconti was deposed since he was suspected of conspiring with the pope" (raw/realms-wp-Louis_IV,_Holy_Roman_Emperor.txt). "In 1327, his father Galeazzo and all of the other leading members of the Visconti family were arrested" (raw/realms-wp-Azzone_Visconti.txt). Azzone then "bought the title of imperial vicar of Milan from the emperor Louis IV" in 1329 (same file). Source discrepancy: the Galeazzo article dates the imprisonment to 1328 ("In 1328, after accusations of betrayal"), and the Lordship of Milan article has Azzone buying the vicariate "In 1327, with the death of his father", while Galeazzo died in 1328 (raw/realms-wp-Galeazzo_I_Visconti.txt, raw/realms-wp-Lordship_of_Milan.txt). Wikipedia contradicts itself here, so COARSE. |
| R21 | Rest of north and central Italy (Venice, Genoa, Papal States, etc.) | NEUTRAL | Edge of frame; grey or very faint. | Outside the story; many polities; no need to fill. |

### Iberian edge

| # | Polity | Status | Fill guidance | Reason and source |
|---|---|---|---|---|
| R22 | Kingdom of Navarre | VERIFIED, own soft fill (or France-family tint); edge COARSE | In 1327 it is in personal union with France under Charles IV. A France-family tint is defensible; a separate muted hue is also fine. Do not show Evreux rule yet. | Navarre "remained in personal union with the Kingdom of France until the death of King Charles I (Charles IV of France) in 1328" (raw/realms-wp-Kingdom_of_Navarre.txt). Joan II "was Queen of Navarre from 1328" (raw/realms-wp-Joan_II_of_Navarre.txt). |
| R23 | Crown of Castile | VERIFIED (edge of frame) | Muted edge hue. | Alfonso XI "was King of Castile and León" (raw/realms-wp-Alfonso_XI_of_Castile.txt). OHM r2803896 Crown of Castile, 1301 to 1402 (raw/realms-ohm-relations-1327.txt). |
| R24 | Crown of Aragon | VERIFIED (edge of frame) | Muted edge hue. | James II was King of Aragon "from 1291 to 1327" (raw/realms-wp-James_II_of_Aragon.txt); he died in November 1327. OHM r2750772 Crown of Aragon, 1323 to 1344. |
| R25 | Kingdom of Portugal | VERIFIED (edge of frame) | Muted edge hue, or NEUTRAL if cropped. | Afonso IV "was King of Portugal from 1325 until his death in 1357" (raw/realms-wp-Afonso_IV_of_Portugal.txt). |
| R26 | Kingdom of Majorca (Roussillon, Montpellier) | COARSE | Fold into the Aragon edge hue or NEUTRAL; do not give Montpellier a French fill. | Montpellier passed to the Majorcan line, whose king "sold the city to the French king Philip VI in 1349" (raw/realms-wp-Montpellier.txt). Majorca had "bonds of vassalage with the crowns of France (through Montpellier) and Aragon" (raw/realms-wp-Kingdom_of_Majorca.txt). Too small and mixed for a clean fill. |
| R27 | Granada | NEUTRAL | Edge; grey. | Outside frame purpose. |

Status tally (27 rows): VERIFIED 14 (R01, R02, R03, R06, R12, R13, R14, R15, R16, R19, R22, R23, R24, R25), COARSE 10 (R04, R07, R08, R09, R10, R11, R17, R18, R20, R26), NEUTRAL 3 (R05, R21, R27). Where a VERIFIED row notes a COARSE edge or split, the fill is safe and only the line is soft.

## 2. Boundary data sources

### 2a. aourednik/historical-basemaps (evaluated live this session, 30 Oct 2026)

- Repo: https://github.com/aourednik/historical-basemaps (GitHub API reports licence GPL-3.0; last push 2026-09-15, which is 08:38 EDT that day).
- LICENSE file: https://raw.githubusercontent.com/aourednik/historical-basemaps/master/LICENSE. It is the "GNU GENERAL PUBLIC LICENSE" "Version 3, 29 June 2007" (raw/realms-gh-LICENSE.txt).
- Nearest file: https://raw.githubusercontent.com/aourednik/historical-basemaps/master/geojson/world_1300.geojson (237 features; sha256 a27985e60d936611d7933f0c30f1b52c36ef4a17225dfac25fb96abe40fa496f; local copy raw/basemaps/world_1300.geojson). There is no 1327 file; the neighbours are world_1279 and world_1400.
- Stated precision: polygons are "adapted for mapping data on world/continent scale"; BORDERPRECISION is "1 (approximate), 2 (moderately precise) and 3 (determined by international law)"; the README advises that "historical boundaries are even more disputed than contemporary ones" (raw/realms-gh-README.txt). In world_1300, every feature carries BORDERPRECISION 1 (raw/realms-basemaps-world_1300-features.txt).
- Accuracy for 1327, from my point-in-polygon test (raw/realms-basemaps-pip-world_1300.txt). It is too coarse for this map:
  - One polygon, English territory, covers all of Ireland (Donegal falls inside) and a Gascony block from latitude 42.7 to 46.3, far larger than the 1327 holding.
  - Bruges, Ghent, Lille and Sluis fall in Holy Roman Empire. That is wrong: Royal Flanders was a French fief.
  - Avignon, Carpentras, Grenoble and Aix fall in France. That is wrong for 1327: they were papal, Imperial or Angevin-Imperial.
  - There is no separate Milan, Savoy, Dauphine or Provence; the whole Empire is one shape.
  - Coastline gaps: Galway, Berwick, Caernarfon and Calais fall in no polygon.
- Licence note: GPL-3.0 is a software copyleft licence. Whether it attaches to a rendered video frame drawn from the geometry is a legal question I cannot settle. Flag it to the owner before shipping any traced aourednik geometry. Use it as a visual reference only.

### 2b. OpenHistoricalMap (recommended primary reference)

- Licence: "Except where otherwise noted, OpenHistoricalMap data is dedicated to the public domain under a Creative Commons CC0 dedication." (raw/realms-lic-ohm-copyright.txt). Features with other licences carry license tags. For any material under a share-alike licence, the copyright page says you "should respect the terms of this license in your own adaptation". None of the 102 relations live in 1327 in my query carries a license tag (raw/realms-ohm-relations-1327.txt).
- Query used: Overpass at https://overpass-api.openhistoricalmap.org/api/interpreter, administrative relations at admin levels 1 to 4 in bbox 42N to 56N, 11W to 10E, filtered to start_date at or before 1327 and end_date after it. This produced 102 relations, including:
  - r2802023 Kingdom of England, r2869806 Kingdom of Scotland, r2956030 Kingdom of France;
  - r2891983 County of Flanders, r2805398 Duchy of Brittany, r2893764 Duchy of Burgundy;
  - r2892600 Kingdom of Burgundy (1307 to 1349, the Arles realm), r2892602 Dauphine of Viennois;
  - r2851366 Comtat Venaissin, r2888199 Papal States, r2751478 Lordship of Milan, r2803894 Kingdom of Navarre;
  - r2803896 Castile, r2750772 Aragon, r2692924 Portugal, r2860660 Majorca.
- Viewing URL pattern, checked HTTP 200 for nine of these IDs: https://www.openhistoricalmap.org/relation/2802023 (swap in the ID).
- Accuracy for 1327 (raw/realms-ohm-isin-1327.txt):
  - Better than aourednik: Flanders is correct (Bruges, Lille and Sluis in the County of Flanders), Dauphine and the Arles kingdom are correct, and Berwick is Scottish.
  - Patchy elsewhere. Bordeaux, Bayonne and Agen fall in no 1327 polity (no Gascony shape). Paris and Lyon return no polity (the France relation is probably incomplete as an area). Milan returns nothing, although r2751478 exists. Galway and Donegal return nothing, so Gaelic Ireland is unmapped, while Dublin falls in Lordship of Eastern Meath.
  - Avignon is wrongly placed in the Comtat and the Papal States (see R19).
- Recommendation: Atelier hand-paints soft fills, using OHM shapes (CC0) as the tracing reference where they exist, and these overrides where they do not. A precise line is not the goal.

### 2c. Others checked (not recommended)

- Euratlas: commercial. The 1300 dataset is sold at "Price : 140 € by direct download"; the licence page lists a simple licence and, for 1300, an extended licence at "Price: 560 € + VAT" (raw/realms-lic-euratlas-gis_1300.txt). The French licence reserves film and TV use to the extended licence: "par procédés cinématographiques, notamment pour une émission télévisée" (raw/realms-lic-euratlas-licence_gis_fr.txt). It is centennial (1300), not 1327. It does include a fuzzy_borders layer, "polygons representing the uncertainty of some countries boundaries". Only worth it if the owner wants a paid, cleared source; it would need the extended licence for video.
- Centennia: a desktop atlas. Only the 1789 to 1939 edition is free; GIS data is a paid institutional product: "CRE: Historical Vector Data ($$)" (raw/realms-lic-centennia-editions.txt). No open licence. Not usable.
- GeaCron: the terms say "All products are property of GeaCron" and grant "no right or license to reproduce" beyond the copyright notice (raw/realms-lic-geacron-terms.txt). Not usable.
- Not evaluated: Atlas Pi, which the aourednik README links. I did not check its licence, so I make no claim about it.

### 2d. Borders to override or blur (all sources)

1. Gascony: shrink to a coastal Bordeaux to Bayonne band and feather it; exclude the Agenais and Saintonge; never use the 1259 or 1360 extents (R07).
2. Flanders: no hard line on any side. Use a France-to-Empire gradient across the Scheldt (R08, R09); override aourednik, which puts Flanders in the Empire.
3. Franco-Imperial frontier, from the Scheldt to the Rhone: soft gradient, never a crisp line. Lyon sits on the French side (1312). The Dauphine, Savoy, the County of Burgundy and Provence sit on the Imperial side. Override aourednik's French fill of the Dauphine and Provence.
4. Ireland: partial English tint in the east only, feathered; the rest neutral. Override aourednik's whole-island fill.
5. Scottish border: soft; Berwick on the Scottish side in 1327.
6. Wales: no line with England; one England fill.
7. Italy: no Milan polygon. Let the Imperial hue fade out over Lombardy, or leave it neutral.
8. Avignon: carve it out of any papal or Comtat fill and fold it into Provence (override OHM).

## 3. Must-nots

1. No realm, duchy, county or region names on screen. Place names only (owner rule). No legend text naming realms either.
2. Do not show Avignon as papal territory in 1327. It belonged to the Angevin counts of Provence until the 1348 sale (R19), and no papal palace or skyline appears (ledger C14b).
3. No hard Flanders border, and no hard Franco-Imperial line.
4. Do not fill all of Ireland as English.
5. Do not draw Gascony at its 1259 extent (after the Treaty of Paris) or its 1360 extent (Bretigny), and do not use aourednik's 1300 Gascony block.
6. Do not fill the Dauphine, Provence or the County of Burgundy as French in 1327.
7. Do not merge the Duchy and County of Burgundy (union from 1330).
8. Do not give Milan a crisp Visconti polygon in 1327.
9. Do not draw a separate Wales border, or any line between the Principality and the March.
10. Do not show Navarre under Evreux rule (that begins 1328).
11. No BORDERPRECISION, VERIFIED or COARSE labels, and no dates on the plate.

## 4. Open items

- GAP: the terms of the 1327 Anglo-French peace and the exact Gascon extent in 1327. Wikipedia has no Treaty_of_Paris_(1327) article. A scholarly source (Chaplais, The War of Saint-Sardos, 1954, cited in raw/realms-wp-War_of_Saint-Sardos.txt) was not consulted. COARSE until then.
- Exact 1327 extent of the English lordship in Ireland: not established. COARSE.
- Milan 1327 versus 1328 arrest date: Wikipedia contradicts itself. COARSE.
- GPL-3.0 implications for using aourednik geometry in video: an owner decision. Not legal advice.
