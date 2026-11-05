# Edward II feature: MAP PLACE-ID LIST v1 (for Atelier)

Prepared by Archivist (research hand), Fri 30 Oct 2026, 18:27 EDT. Companion to CLAIM-LEDGER-v1.md (claim IDs below point there).
Coordinates: every lat/long is Wikidata property P625, fetched live from https://www.wikidata.org/wiki/Special:EntityData/<QID>.json on 30 Oct 2026, about 18:20 EDT. Raw JSON and a summary are saved in raw/wikidata/ (wikidata-P625-2026-10-30.txt). Decimal degrees, WGS84; west and south are negative. Nothing else was used for coordinates.
Status key: VERIFIED = modern identification is unambiguous in the captured sources; UNCERTAIN = sources disagree or identification is inference; OMIT = region only, not a point (region label or tint at most).
On-screen rule: plate text is the modern English place name only. No claim or band labels (no LEGEND, DOCUMENTED, etc.) on plates. Double quotes in this file are verbatim source strings only (checked by raw/_verify_quotes.py).

## MAP 1. Edward's English and Welsh stations, and the 1330 places (ledger-supported only)

| # | stop (as in source) | claim ID | status | modern site | Q-ID | lat, long (P625) | on-screen text OK? | notes |
|---|---|---|---|---|---|---|---|---|
| 1-01 | Chepstow (castle of the Earl Marshal; letter: "Gesosta") | C25 | VERIFIED | Chepstow Castle, Monmouthshire | Q1070187 | 51.64390, -2.67570 | yes: Chepstow | Sailing point, October 1326. |
| 1-02 | Glamorgan (capture, Nov 1326) | C26 | OMIT (as point) | Glamorgan, historic county | Q870815 | (centroid 51.66667, -3.66667: do not pin) | label only: Glamorgan, or South Wales | Disputed spot: Wikipedia says north of Caerphilly (Q909119, 51.57800, -3.21800); Warner's blog says near Neath (Q2003342, 51.66000, -3.81000). Llantrisant is in none of my captures. Use a region label, no pin. |
| 1-03 | Kenilworth | C25 | VERIFIED | Kenilworth Castle, Warwickshire | Q1738764 | 52.34700, -1.59111 | yes: Kenilworth | Held there; loses the crown, Jan 1327. |
| 1-04 | Berkeley | C01a, C12, C25 | VERIFIED | Berkeley Castle, Gloucestershire | Q4891993 | 51.68861, -2.45694 | yes: Berkeley | From about April 1327. |
| 1-05 | Gloucester (abbey, now cathedral; funeral and burial) | C04, C06, C10 | VERIFIED | Gloucester Cathedral | Q262500 | 51.86730, -2.24654 | yes: Gloucester | Burial date 20 Dec 1327 is secondary (C06). |
| 1-06 | Bristol (notables called to view the body) | C04 | VERIFIED | Bristol | Q23154 | 51.45361, -2.59750 | yes: Bristol | Optional; only if the viewing beat is mapped. |
| 1-07 | Lincoln (Edward III receives the news) | C20 | VERIFIED | Lincoln | Q180057 | 53.25000, -0.55000 | yes: Lincoln | Optional. Date of the news is disputed (C20); do not put a date on the plate. |
| 1-08 | Corfe (where friars told Kent Edward was held) | C09 | VERIFIED (place) | Corfe Castle, Dorset | Q1236511 | 50.63990, -2.05890 | yes: Corfe | The place is certain; Edward being there is a claim (C09, and Fieschi C03a). Do not draw a line from Berkeley to Corfe on Map 1. |
| 1-09 | Winchester (parliament, Kent condemned and executed, March 1330) | C05a, C28 | VERIFIED (city) | Winchester, Hampshire | Q172157 | 51.06333, -1.30861 | yes: Winchester | City point only; no captured source places the execution at a specific site in the city. |
| 1-10 | Westminster (parliament of Nov 1330: Berkeley's statement, widow's petition) | C01a, C13 | VERIFIED | Palace of Westminster, London | Q62408 | 51.49944, -0.12417 | yes: Westminster | Modern palace sits on the medieval site; plate name Westminster, not Houses of Parliament. |
| 1-11 | Tyburn ("apud Elmes"; Mortimer hanged 29 Nov 1330) | C12 | VERIFIED (area) | Tyburn, former village near Marble Arch, London | Q1362341 | 51.51286, -0.16400 | yes: Tyburn | Wikidata point is the former village; the exact gallows spot is not in my captures. |
| 1-12 | Nottingham Castle (Mortimer seized, 1330) | C27 | VERIFIED | Nottingham Castle | Q17642916 | 52.94917, -1.15472 | yes: Nottingham | Include only if the script uses the coup (secondary only). Note: Wikidata Q1799649 is the later Ducal Mansion; do not use. |
| 1-13 | "apud Bradeleye" (Berkeley's illness) | C01a | OMIT | not identified in captures | none | none | no | No captured source identifies which Bradley. |
| 1-14 | Avignon (Kent hears Edward is alive) | C09 | OMIT from Map 1 | Avignon | Q6397 | 43.94861, 4.80833 | n/a | Outside England and Wales. Inset only if needed. |

Map 1 line suggestion: Chepstow to Glamorgan (label) to Kenilworth to Berkeley to Gloucester is the documented 1326 to 1327 sequence (C25, C26, C06). Corfe, Winchester, Westminster, Tyburn, Nottingham are 1330 places: separate colour, no connecting route.

## MAP 2. The route Fieschi's letter claims (C03a order)

Latin forms are Germain's print (raw/memoiressociarcheomontpel7_djvu.txt), checked against Stubbs 1883.

| # | stop (as in source) | status | modern site | Q-ID | lat, long (P625) | on-screen text OK? | notes and competing identifications |
|---|---|---|---|---|---|---|---|
| 2-01 | "quod vocatur Gesosta." | VERIFIED | Chepstow Castle | Q1070187 | 51.64390, -2.67570 | yes: Chepstow | Germain glosses it as "deGesosta (Chepstow)"; Stubbs: "not an improbable form"; Mortimer's translation: Chepstow. |
| 2-02 | "aplicuit in Glomorgam supra mare" | OMIT | Glamorgan (region) | Q870815 | do not pin | label only: Glamorgan | Region. |
| 2-03 | "in castro Chilon-" "gurda" (line break in print) | VERIFIED | Kenilworth Castle | Q1738764 | 52.34700, -1.59111 | yes: Kenilworth | Germain's French: "Kenelworth"; Mortimer: Kenilworth. |
| 2-04 | "ad castrum de Berchelee." | VERIFIED | Berkeley Castle | Q4891993 | 51.68861, -2.45694 | yes: Berkeley | |
| 2-05 | "in castro de Corf" | VERIFIED | Corfe Castle | Q1236511 | 50.63990, -2.05890 | yes: Corfe | |
| 2-06 | "transivit in Yrlandam" | OMIT | Ireland (island) | Q22890 | do not pin | tint or label only: Ireland | Months there vary by edition (C03b); no number on the plate. |
| 2-07 | "aplicuit ad portum de Sandvic" | VERIFIED | Sandwich, Kent | Q26163 | 51.27472, 1.33889 | yes: Sandwich | |
| 2-08 | "transivit mare apud Sclusam." | VERIFIED | Sluis, Zeeland | Q2065987 | 51.30890, 3.38830 | yes: Sluis | Recommend modern Sluis on plates (Wikidata label). VO may say Sluys if Archivist prefers the period form; keep the plate modern. Do not use Q10080 (the wider municipality). |
| 2-09 | "in Normandiam" | OMIT | Normandy (region) | Q15878 | do not pin | tint or label only | |
| 2-10 | "per Linguam Occitanam" | OMIT | Languedoc (historical province) | Q206221 | do not pin | tint or label only | |
| 2-11 | "venit Avinionem" | VERIFIED | Avignon | Q6397 | 43.94861, 4.80833 | yes: Avignon | City point, not the Palais des Papes (Q143463): ledger C14b says no captured source ties the papal palace to this story. |
| 2-12 | "ivit Parisius" | VERIFIED | Paris | Q90 | 48.85667, 2.35222 | yes: Paris | |
| 2-13 | "in Braybantiam" | OMIT | Duchy of Brabant (region) | Q159856 | do not pin | tint or label only: Brabant | |
| 2-14 | "in Coloniam" (to see the Three Kings) | VERIFIED | Cologne | Q365 | 50.94222, 6.95778 | yes: Cologne | Alternative pin: Cologne Cathedral Q4176 (50.94139, 6.95833); the city point is safer, the letter names only the city and the Kings. |
| 2-15 | "peresit Mediolanum in Lombardiam" | VERIFIED | Milan | Q490 | 45.46694, 9.19000 | yes: Milan | Last pinned stop. |
| 2-16 | "rium castri Milasci" (hermitage of the castle Milasci) | UNCERTAIN | competing: Milazzo, Sicily (Germain: "Milazzo en Sicile"), Q487929, 38.21700, 15.23700; Melazzo, Piedmont (Mortimer's translation: "castle of Melazzo"), Q17380, 44.64500, 8.42611, castle Q111015164, 44.64394, 8.42607 | see left | see left | no | Desk observation (mine, not a source): the letter says he went from Milan into this hermitage, and Sicily is far from Lombardy. Do not pin either. |
| 2-17 | "mutavit se in castro Cecinie, in alio heremitorio" ... "diocesis Papiensis" | UNCERTAIN | competing: Cecina, Tuscany (Germain: "Cecina, au diocèse de Pavie"), Q157762, 43.31389, 10.52500; Cecima, Lombardy (Mortimer's translation: "castle of Cecima"), Q41049, 44.85000, 9.08333 | see left | see left | no | Germain's own gloss is inconsistent (Cecina is in Tuscany, not the diocese of Pavia). Do not pin. |
| 2-18 | Sant'Alberto di Butrio (not named in the letter) | UNCERTAIN | Eremo di Sant'Alberto di Butrio, Ponte Nizza | Q3731350 | 44.85493, 9.14934 | no | Identification by Warner's blog ("ended up at the hermitage of Sant'Alberto di Butrio"). Wikipedia notes a local "tradition that a king of England was buried there" at Cecima: that is a do-not-say (Edward buried in Italy). Do not pin, do not show the tomb. |

Not on Map 2: Gloucester. The letter's Gloucester sentence is the substitute-body passage, which is out under the no-gore rule.

## Recommended framing for Map 2
1. It is the letter's claim, not Edward's route. Title or VO should make that plain, e.g. the route Fieschi's letter describes (plate text: a neutral title such as The letter's route, with no band label).
2. Draw the route only as far as Milan. Show the hermitages as a soft unlabelled tint over the hills south of Milan, or leave them off. Pin neither hermitage, and do not pin Sant'Alberto di Butrio.
3. Ireland, Normandy, Languedoc and Brabant: region tints or labels only, no pins. Glamorgan likewise.
4. Use a different line style from Map 1 (e.g. dotted) so the documented 1326 to 1327 stations and the claimed journey never read as one route. Shared pins (Chepstow, Kenilworth, Berkeley, Corfe) can reuse Map 1 coordinates.
5. No dates and no durations on the plates (Ireland 8 vs 9 months is unresolved, C03b; the letter is undated, C14).
6. Keep Kent off Map 2 (law §3, C17).

## Sources checked for this list
raw/memoiressociarcheomontpel7_djvu.txt (Germain, Latin and French); raw/stubbs-chronicles-edw-i-ii-vol2-1883_djvu.txt; raw/mortimer-death-of-edward-ii.txt (Mortimer's translation); raw/warner-blog-search-fieschi.txt; raw/warner-blog-search-melton.txt; raw/wikipedia-Edward_II.noref.txt; raw/wikipedia-Fieschi_Letter.noref.txt; raw/10213330bsb_djvu.txt (Rot. Parl. ii); raw/admurimuthconti00robegoog_djvu.txt (Murimuth); raw/wikidata/ (32 entity JSON files plus summary).
