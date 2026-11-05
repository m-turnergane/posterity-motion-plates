# Claims v2 countersign: Björn / Luna coffin ruse (Archivist)

Written 2026-11-03 by Archivist. Research only. No messages were sent. Only public pages were used, and no Google account was accessed.

## 0. Version pin (countersigned target)

| File | md5 | mtime (America/Toronto, EST) | wc -w |
|---|---|---|---|
| raw/script-vo-v2b-DRAFT.txt (TARGET, the Vellum storyboard version) | 680db8ead6eccfeef963ef994ae7e5e0 | 2026-11-03 05:59:08 -0500 | 223 (matches Scriptor) |
| script-v2.md (claim list plus v2b section) | a0cf80c32ec89c248c2c1161f40a8687 | 2026-11-03 05:59:15 -0500 | n/a |

- U+2013 and U+2014 grep of the v2b VO finds no en or em dashes. "Mid-funeral" uses an ASCII hyphen, which is fine.
- This countersign is void if the v2b md5 changes.
- FINAL FIX set (section E supersedes the earlier FIX wording in sections A and C): `wc -w` = 225, at the cap. With the optional L04 tweak it is still 225. Verified with `wc -w` on a patched temp copy; no en or em dashes.

## Bands
- DOCUMENTED: in a contemporary or near-contemporary record, or in hard archaeology.
- CONTEMPORARY CLAIM: a contemporary source says it, but nothing corroborates it.
- INTERPRETATION: a reading or inference by us or by scholars.
- UNCERTAIN: the evidence conflicts or is weak.
- LEGEND: told only by later narrative sources (Dudo c. 996 to 1015, William of Jumièges c. 1050 to 1070, and later writers).

## Source keys (all paths under raw/)
- **DUDO-L**: dudo-latin-augustana-02.txt, the Bibliotheca Augustana Latin.
- **DUDO-T**: dudo-lifshitz-fordham.txt, Felice Lifshitz's translation (Fordham Medieval Sourcebook) and her introduction.
- **GND**: jumieges-guizot1826-djvu.txt. This is Guizot's 1826 French translation of William of Jumièges, OCR'd. I did not read the Latin of van Houts' edition.
- **AB**: ab-waitz1883-djvu.txt, the Annales Bertiniani edited by Waitz in 1883. Prudentius writes to 861.
- **FONT**: mgh-ss2-pertz1829-djvu.txt, the Chronicon Fontanellense.
- **STEF**: sagabook-v5-6-djvu.txt, Stefansson 1909, "The Vikings in Spain", which translates Arabic sources.
- **FAI**: fai-celt-T100017.txt, the Fragmentary Annals of Ireland (CELT).
- **WP-***: local wikitext snapshots. Revids are in wp-revids.txt.
- **Web**: public pages read this session. See section 9.

The OCR is noisy. All quotes are copied verbatim from the files, OCR errors included ("Jenrs", "cerçnueil"). Line breaks are shown as "/".

---

## A. Steering questions (answered first)

### L04. Do AB 859/860 record the Italy raid, and do they never name a leader?

**Yes on both. DOCUMENTED.**

- **AB 859** (year header at line 3276; Prudentius), lines 3292 to 3295: "Pyratae Danorum longo maris circuitu, inter Hispanias videlicet et Affricam navigantes, Rodanum ingrediuntur, depo-/pulatisque quibusdam civitatibus ac monasteriis, in insula / quae Camarias6 dicitur sedes ponuntk". The "6" and "k" are OCR footnote marks.
- **AB 860** (header at 3390; the 861 header is at 3467, so these lines fall inside 860):
  - 3441 to 3444: "Hi vero Dani qui in Rodano morabantur usque ad Valentiam / civitatem vastando perveniunt ... ad insulam in qua sedes po-/suerant redeunt."
  - 3455 to 3456: "Dani qui in Rodano fuerant Italiam petunt et Pisas civi-/tatem aliasque capiunt, depraedanturb atque devastant." The "b" is a footnote mark.
- **No leader is named** in the 859 or 860 Rhône and Italy entries.
  - The 862 entry (Hincmar, lines 3645 to 3647: "quibus et illi iunguntur qui in Hispania fuerant") names no one either.
  - The Arabic sources in STEF 25566 to 25661 call the raiders only "Madjus" and name no leader.
- **Two cautions:**
  - AB names **Pisa**, not Luna. Luna appears in AB only in **849**, as a **Saracen** raid. Lines 2438 to 2440 read: "Mauri / et Saraceni Lunam Italiae civitatem adpredantes b, nullo ob-/sistente maritima omnia usque ad Provinciam devastant."
  - The Irish FAI (lines 4199 to 4251) does attach names to a fleet raiding Spain and Mauritania: the sons of Ragnall son of Albdan. FAI is a much later compilation and does not name Björn or Hastein. A pedant could still say "annals" do name leaders.
- **Verdict:** PASS. Optional tightening that removes the FAI quibble: "Frankish annals of the time record a Viking fleet raiding Italy, but name no leader."

### L07. Is "He chose mercy" OK as a framed reading? Who baptises and who sponsors?

**"He chose mercy" is INTERPRETATION. It is acceptable only as our reading; no source states the bishop's motive.**

- The word "mercy" comes from **Hastein's request**, not the bishop. DUDO-L 167 to 168: "uestra misericordia uestraque pietate hac / ciuitate sepeliri". DUDO-T 2014: "through your mercy and your compassion".
- Dudo's bishop and count answer with a treaty. DUDO-L 168 to 170: "Hoc audientes praesul et comes. responderunt / internuntio dicentes. Perpetui foederis pactum uobiscum agimus. / uestrumque seniorem christianum facimus."
- Dudo then frames them as **deceived**. DUDO-L 194: "tali sophismate decepti".
- In GND the bishop and count react with **joy and make peace**, which is what opens the city. GND 989 to 994: "l'évêque et le comte se livrèrent aux trans-/ports de leur joie, conclurent la paix avec ce détes-/table ennemi de toute paix, et le peuple normand / fut admis à entrer dans la ville".
- So "could have kept the gates shut" fits GND's sequence of barred gates, peace, then admission (976, 991 to 993).
- **Baptism.** Neither source explicitly names the officiant.
  - DUDO: the bishop prepares the font (DUDO-L 175: "Interim praeparatur ab episcopo balneum"; DUDO-T 2024: "the bath is being readied by the bishop").
  - DUDO: Hastein is **received from the font by bishop and count**, which is the godparent role (DUDO-L 180 to 181: "Suscipitur de sacrosancto / baptismate ab episcopo et comite"; DUDO-T 2030).
  - DUDO: hence "Noster senior uester filiolus", "our lord your godson" (DUDO-L 191; DUDO-T 2043).
  - GND 1011 to 1012: "l'évêque et le comte le présentèrent sur les / fonts du baptême". Again they are **sponsors**, and the baptiser is unnamed.
- "Baptised Hastein" is therefore an inference. It is reasonable, since the bishop prepared the font, but the role the texts actually give the bishop is **godfather**.
- **Verdict: FIX.** Final wording is in section E: "The bishop and count could have kept the gates shut. They chose mercy, and Hastein was baptised." This supersedes the earlier godfather wording, which was too long for the 225 cap.
- If the owner keeps "baptised Hastein", downgrade to FLAG (inference) rather than error.

### L11. Does the sack precede the discovery in both? Is "an old Roman town" fair?

**Yes in both. LEGEND for the narrative.**

- **DUDO.** The sack and massacre come first (DUDO-L 227 to 243). Then:
  - DUDO-L 244 to 247: "Gloriabatur astignus / cum suis. ratus coepisse romam caput mundi ... Hanc non esse romam postquam didicit".
  - He then orders the province plundered and the town burned (247 to 249).
  - DUDO-T 2107 and 2110: "supposing that they have captured Rome" ... "After he has learned that it is not Rome".
- **GND.** The destruction comes first (1028 to 1035, "la ville dévastéé, et les remparts renverse"). Then 1051 to 1053: "La ruine de cette ville ainsi accomplie, les Païens / ayant découvert qu'ils ne s'étaient point emparés de / Rome".
- **"An old Roman town" is fair. DOCUMENTED.**
  - Luna was a Roman colony founded in 177 BC (WP-Luni_Italy line 70; it.wikipedia "Luna (colonia romana)", citing Livy XLI 13).
  - By 860 it was a shrunken episcopal and comital town (see section 4).
- **Caution:** the identification of the sacked town as **Luna** comes only from Dudo and GND (LEGEND). The contemporary AB names Pisa.

### L12. Is Dudo the first known teller, naming only Hastein? Is "Norman churchman" accurate?

- **First known teller: yes. INTERPRETATION, matching standard scholarship.**
  - None of AB, FONT, the Arabic sources (STEF) or FAI tell the ruse.
  - Abbott, "Hasting", English Historical Review 13 (1898) 439 to 463: "There seems to be no definite contemporary authority either for or against a Norse raid on Luna in the ninth century, and no document before Dudo connecting Hasting's name with a Mediterranean expedition." This is quoted from a public search snippet; see section 9.
- **Names only Hastein: yes. DOCUMENTED (textual).**
  - Throughout DUDO-L 135 to 250 the leader is "alstignus" (136, 146, 150), "anstignus" (178, 199, 214) and "astignus" (227, 243, 244).
  - No Bier or Björn appears in the passage.
  - A grep of the whole Lifshitz translation finds no Bier, Bero, Berno, Björn, Lodbrok or Ironside.
- **"Norman churchman": FIX.**
  - Dudo was a **Picard/Vermandois** cleric, canon and later dean of **Saint-Quentin**, who wrote for the Norman dukes.
  - Sources: DUDO-T intro, lines 108 to 114 ("decanus" of "St. Quentin in the Vermandois") and lines 118 to 121 (a 1015 charter in which Dudo calls himself "capellanus" (chaplain) of duke Richard II).
  - WP-Dudo line 2: "a Picard historian, and dean of Saint-Quentin".
  - The owner's suggested wording is accurate.
- **FIX.** Final wording is in section E (adopts Vellum's "the churchman Dudo" for the word cap): "The first known writer to tell the funeral story, the churchman Dudo, names only Hastein." "A churchman at the Norman court" is also accurate but costs 3 more words.

### L13. Is William (c. 1070) Björn's first appearance on the voyage, "decades" after Dudo?

**Yes. "First" is INTERPRETATION; the dates are DOCUMENTED as scholarly consensus.**

- **GND names Bier.**
  - 534 to 536: "le fils de / . leur roi Lothroc, qui se nommait Bier, à la côte de / fer, et avec Hastings".
  - Chapter IX heading, 952 to 953: "Hastings se rendant par mer à Rome / pour la soumettre à la domination de Bier".
  - 1056 to 1058: "Bier, / sous les drapeaux duquel se commettarent .ces dé-/vastations et qui était le roi de ces armées".
- **Earliest surviving source linking Björn to the raid.**
  - Abbott (EHR 1898) says William "adds that Hasting was given charge of Biorn Ironside" (snippet).
  - STEF 25663 to 25664 lists only William, Wace and Benoît (both later, 12th century) as naming Björn.
  - WP-Björn_Ironside line 18: "The oldest text that details his origins is the Norman history of William of Jumièges (c. 1070)".
- **Dates.**
  - Dudo: c. 996 to 1015. DUDO-T intro, lines 59 and 86 to 115; WP-Dudo line 6. Lifshitz notes the end date "is not iron clad".
  - One public page (mondes-normands.caen.fr) says "c. 1025". Treat that as an outlier.
  - William: van Houts (Oxford 1992 to 1995) dates most of the GND to 1050 to 1060, with a continuation after 1066 and before c. 1070. Sources: Persée review of van Houts vol. 1; Bouet on mondes-normands.caen.fr; WP-William_of_Jumièges line 5.
  - The gap is roughly 35 to 75 years, so **"decades later" PASSES**.
- **Nuance for captions:** Book I, where Bier appears, belongs to the 1050s to 1060 layer. "c. 1070" is the completion date, so a caption should say "c. 1050 to 1070" or "by c. 1070", not "in 1070".
- "A monk": DOCUMENTED. He is a monk of Jumièges, per his dedicatory letter (WP-WJ line 3).
- **Verdict:** PASS.

### L02. Is there any source for a NIGHT setting?

**No source puts the coffin procession or the attack at night. Keep "how". PASS.**

- Night appears only twice:
  - DUDO-L 186 to 187: "Imminenti nocte / me mortuum nuntiate" (DUDO-T 2039: "When night is falling, notify..."). This is the false death announcement.
  - GND 1014 to 1015: "au milieu du silence de la nuit, / s'étant cuirassé, Hastings se fait déposer dans un cer-/cueïl". This is the arming and coffining aboard ship.
- The funeral itself has bells, clergy, a procession with "candelabra et cruces" (DUDO-L 213) and a full mass (DUDO-L 217 to 224; GND 1022 to 1025). No time of day is given.
- **Storyboard guidance:** night is fine for the ship scene (GND). Do not label the church attack as night.

### L09. Armour under tunics (GND) vs arms in the bier (Dudo). Is the VO consistent?

- **GND 1016 to 1017:** "donne ordre à ses compagnons de revêtir / leurs cuirasses sous Jenrs tuniques" (OCR "Jenrs" for "leurs"). Hastein himself is "cuirassé" (1015).
- **DUDO-L 200 to 201:** "Arma / mecum in ipso collocate" (DUDO-T 2055: "Place my arms in it with me"). Dudo has no armour under clothing.
  - In Dudo the reinforcements are the ship crews, who arrive at the open gates (DUDO-L 238 to 239: "Gens quae preerat nauibus. adest portis / bipatentibus").
- The VO is **consistent as a composite legend**:
  - L01 (a sword inside the coffin) follows Dudo's arms in the bier.
  - L09 (armour under tunics) follows GND.
  - The two do not contradict each other, since GND's Hastein also kills with "son glaive" (1029).
- **Verdict:** PASS (LEGEND, GND). **Storyboard FLAG for Vellum:** any frame captioned as Dudo should show weapons in the bier and not mourners in mail.

---

## B. Required answers (1) to (6)

### (1) Dudo: date, names in the Luna ruse, and the passage
- **Date:** c. 996 to 1015 (Lifshitz intro, DUDO-T 59 and 86 to 115; WP-Dudo 6).
  - The commission came two years before Richard I's death, dated 996 (or 1002 in the oldest manuscripts).
  - The work is dedicated to Bishop Adalbero of Laon.
  - Completion is usually put at about 1015.
  - The brief's range of "c. 994 to 1015" is close. The commission is c. 994, and writing ran c. 996 to 1015.
  - Christiansen's 1998 introduction was not read directly; it is in Google Books, which I did not open.
- **Name:** Hastein only, as Alstignus, Anstignus or Astignus. Björn is absent.
- **Key passage, DUDO-L:**
  - 143 to 144: "romam dominam gentium uolentes clam / adipisci Lux urbem quae Luna dicitur. nauigio sunt congressi."
  - 146 to 148: "Decernens alstignus / blasphemus. ab omnibus non posse ciuitatem capi armis; dolosum / repperit consilium nefandissimae fraudis."
  - 227 to 229: "Tunc astignus feretro desiluit. ensemque fulgentem / uagina deripuit. Inuasit funestus presulem. librum manu tenentem. / Iugulat presulem prostrato et comite."
  - Translation, DUDO-T 2083: "Then Anstign has jumped down from" (the line breaks there).
- Band: LEGEND for the events. DOCUMENTED (textual) that Dudo names only Hastein.

### (2) William of Jumièges: date, Bier as pupil, and was he first?
- **Date:** c. 1050 to 1060 for the main text, completed by c. 1070 (van Houts, via the Persée review and Bouet).
- **Bier côte de fer, with Hastein as tutor: yes.**
  - GND 729 to 730 (chapter heading): "Comment Bier, fils de Lothroc, roi de Dacie, fat chassé de sa / patrie, selon la coutume, avec Hastings son gouverneur."
  - 737: "son fils nommé Bier, à la côte de fer".
  - 754 to 755: "Hastings ... exilé de sa patrie avec son jeune élève".
  - Motive, 959 to 962: "desirant / élever son seigneur à une plus haute fortune ... diadême impérial".
  - 751 to 753: the invulnerability tale, "il était invul-/nérable ... frotté par sa mère". This is supernatural-adjacent, so keep it out of the VO.
- **First surviving source to link Björn to the raid:** yes, as far as standard scholarship and our corpus show (Abbott 1898; STEF 25663 to 25664). Band: INTERPRETATION (high confidence). The honest wording is "earliest known" or "first surviving", not "first ever".

### (3) The funeral ruse, step by step

| # | Step | Dudo (DUDO-L line) | GND line | Band |
|---|---|---|---|---|
| 1 | Aims at Rome; reaches Luna | 138 to 139 "Si uobis non displicet romam eamus"; 143 to 144 sails deliberately to "Lux urbem quae Luna dicitur" | 952 to 954; 973 to 974 driven to Luna by a storm ("tempête") | LEGEND |
| 2 | Thinks Luna is Rome | Implied at 143 to 144; explicit at 245 "ratus coepisse romam" | 979 to 980 "crut qu'il avait devant / lui la ville de Rome" | LEGEND |
| 3 | City defended or gates barred | 145 to 146 "munierunt urbem quampluribus armigeris" (no gates) | 976 "barricadèrent les portes de leur ville" | LEGEND |
| 4 | Envoy: peace, illness, wish to convert | 148 to 149, 163 to 166 ("Noster senior infirmatus ... christianumque sese fieri") | 982 to 989 ("acçablé d'une / maladie mortelle ... le faire chrétien") | LEGEND |
| 5 | Bishop and count agree, make peace | 168 to 170 "Perpetui foederis pactum" | 989 to 994, joy, peace, Normans admitted | LEGEND |
| 6 | Baptism; bishop and count sponsor | 175 to 181 | 1005 to 1012 (at "l'église") | LEGEND |
| 7 | Back to the ship; death announced by night | 183, 186 to 191 | 1013 to 1019 | LEGEND |
| 8 | Men weep and ask burial in the city | 187 to 195 ("in uestro monasterio") | 1017 to 1021, mourning (the burial request is implicit) | LEGEND |
| 9 | Weapons hidden | 200 to 201, arms in the bier | 1015 to 1017, armour under tunics | LEGEND (the sources differ) |
| 10 | Procession into church; mass | 208 to 224 | 1021 to 1027 | LEGEND |
| 11 | Leaps out; kills bishop and count | 227 to 229, after the mass, at the burial | 1027 to 1029, during the prayers | LEGEND |
| 12 | Doors shut, massacre, ship crews at gates | 230 to 241 | 1029 to 1035 | LEGEND |
| 13 | Discovers it is not Rome | 244 to 247 | 1051 to 1053 | LEGEND |

- **Literary motif.** Supported. Band: DOCUMENTED that parallel texts exist; INTERPRETATION that it is a topos.
  - Abbott (EHR 1898): "the stratagem of feigned death, is a device common to Northern tradition, and by no means distinctively characteristic of Hasting. By such a trick did the legendary Frode ... capture ... London; the device was used by Harald Hardrada in Sicily and by Robert in Calabria." This is quoted from the public search snippet, with ellipses. The snippet OCR has errors such as "Bussian" and "Bobert", so verify it against the journal before any on-screen use.
  - **Robert Guiscard:** William of Apulia, Gesta Roberti Wiscardi (1096 to 1099), translated by G. A. Loud. A "body" on a bier with "Swords ... hidden on the bier" is carried to a monastery to be buried.
  - **Harald Hardrada:** Snorri, Heimskringla, Haralds saga ch. 10, where a feigned funeral procession opens a Sicilian castle. I saw this only via a summary page and did not read the saga text.
  - The it.wikipedia Luna article, note 111 (citing Frasson 2019), says: "Lo stratagemma della falsa morte è un topos della letteratura nordica."
  - Note that Dudo (c. 1000) is earlier than all of these parallels.

### (4) Luna c. 860
- **Site.** A low promontory or coastal plain at the mouth of the Magra, about 20 m above sea level.
  - In antiquity it sat on the estuary, with a lagoon behind a sand bar. It was not a hilltop.
  - Sources: it.wikipedia "Luna (colonia romana)", Topografia, citing Delano Smith et al., PBSR 54 (1986); WP-Luni_Italy 50 and 81.
- **State by 860.** A shrunken town. Band: DOCUMENTED (archaeology) unless noted otherwise.
  - Monumental buildings were abandoned in the later 4th century.
  - The forum was abandoned as a public space by the end of the 6th century, its decorative marbles removed, and small wooden houses built on it (WP-Luni_Italy 96, citing Ward-Perkins 1997).
  - A **reduced late-antique wall circuit** enclosed the SW "Cittadella" around the **cathedral**.
  - The cathedral was rebuilt in the 8th and 9th centuries with a crypt and side apses (Treccani; it.wiki, citing Dadà 2009). It is first named **S. Maria** in a document of **879** (Treccani, "Luni", Enciclopedia dell'Arte Antica).
  - It was a county seat under Charlemagne from 773/774 and a bishopric (WP-Luni 85).
  - The **amphitheatre** stood outside the walls and the theatre at the north corner, both in ruin (it.wiki; WP-Luni 99 and 103).
  - AB records a Saracen raid in 849 (AB 2438 to 2440).
  - The final abandonment is later: the 1016 Saracen attack, malaria and the silting of the port, the see moved to Sarzana in 1204, and the site abandoned in the early 13th century. **Do not paint 860 as a ghost town.**
- **"Roman coastal-plain settlement" as a painting brief.** It works if it means a small walled core with a church, set amid older Roman ruins (a marble-clad amphitheatre shell outside the walls, a colonnade stub) on a flat estuary with a lagoon harbour and ships. Mountains (the Apuan Alps) sit behind.
  - Avoid a gleaming intact imperial Rome, a hilltop citadel, or a Gothic cathedral (the extant apse is Romanesque, 12th century).
  - Band: INTERPRETATION built on DOCUMENTED archaeology.
  - The VO phrase "a walled city by the sea" is fair: the walls were reduced but present, and GND has "remparts" (977).
- **Was there a bishop in 860?** A see is DOCUMENTED. The bishop's **name in 860 is UNCERTAIN.**
  - Neither Dudo nor GND names him.
  - The diocesan list (diocesilaspezia.it) gives Petroaldo (attested 826), Teodolasio (attested **867**), S. Ceccardo ("+ 895?") and Gualterio (to 884).
  - Formentini argues that Ceccardo was the bishop killed in 860, while the Bollandists favour 892. it.wiki calls Ceccardo's historical existence "incerta".
  - **Do not name the bishop in VO or on-screen text.**

### (5) Chronology, and do the annals name the leaders?
- **855 to 858, Seine.**
  - FONT 33470 to 33478 (the 855 entry): "Berno Normannus cum valida classe ingressus est". 33476 to 33477: "Berno in quadam insula castrum aedificat ... anno 859" (the OCR is damaged).
  - Coupland (via the WP article on Bjørn, fl. 856 to 858) notes FONT misdates these events.
- **858, AB (Prudentius) 3153 to 3155, on Berno:** "Berno dux partis pyratarum Sequanae insistentium ad Karlum regem in Vermeria palatio venit, eiusque se manibus dedens, fidelitatem statim iurat." DOCUMENTED. This is Seine only, with no Mediterranean link.
  - The Berno = Björn Ironside identification is UNCERTAIN (the WP Bjørn (fl. 856 to 858) article: "may be identified").
  - Since the owner cut Berno and Verberie from the VO, nothing here depends on it.
- **858/859, al-Bakri.** Nekor in the year 244 AH ("19 April, 858 to 7 April, 859"); "Madjus stayed eight days in Nekor" (STEF 25633 to 25639).
- **859, Arabic (Ibn Idhari and others, STEF 25566 to 25610: 25570, 25582, 25585, 25592, 25598).** 62 ships; Algeciras and its mosque burnt; Africa; Orihuela; wintering in France; more than 40 ships lost in a storm. CONTEMPORARY CLAIM transmitted in later compilations.
- **859, AB.** Into the Rhône, a base on the Camargue (3292 to 3295).
- **860, AB.** Valence (3441 to 3444); then Italy, with **Pisa** "and others" taken (3455 to 3456).
- **861 to 862.** Return; AB 862 (3645 to 3647) mentions "illi ... qui in Hispania fuerant".
- **Leaders named in contemporary annals: none** for the Mediterranean raid.
  - Hastein and Björn are attached to it only by Dudo (Hastein) and GND (both).
  - Christys, Vikings in the South (2015) pp. 60 to 61, as cited on WP-Vikings_in_Iberia (line 49), says the identification is "based on modern extrapolation from unreliable medieval sources". I read this via Wikipedia, not the book.

### (6) Safe VO phrasings (no em or en dashes; none implies Björn's absence is proven or that William invented him)
1. "The earliest account names only Hastein. Björn enters the story decades later."
2. "Dudo, the first known teller, does not mention Björn. A later chronicle adds him."
3. "In the oldest surviving telling, there is no Björn. He first appears in a chronicle written decades later."
4. "No record from the time puts Björn on this voyage. A monk writing generations later is the first known to name him."

---

## C. Line-by-line countersign of v2b (md5 680db8ea…)

| L | Text (v2b) | Verdict | Band | Source / note |
|---|---|---|---|---|
| 01 | A coffin is carried into a Christian church. Inside, the dead man is holding a sword. | PASS | LEGEND (framed by L02) | Arms in bier, DUDO-L 200 to 201; sword drawn, 227 to 228; church: "aecclesia" 230, GND "à l'église" 1022. "Holding" is visual licence. |
| 02 | Legend says this was how Björn Ironside, son of Ragnar Lothbrok, tried to take Rome. | PASS | LEGEND | GND 534 ("fils de ... Lothroc ... Bier"), 952 to 953. "Ragnar" is the later saga name (UNCERTAIN), covered by "Legend says". No night claim (see L02 above). |
| 03 | His tutor, the raider Hastein, planned to make Björn emperor there. | PASS | LEGEND | GND 730, 739 ("son gouverneur"), 755, 959 to 962 ("diadême impérial"). In Dudo, Hastein seeks the empire for himself (245 to 246), which is worth knowing for L12. |
| 04 | Annals of the time record a Viking fleet raiding Italy, but never name its leader. | PASS (optional FIX) | DOCUMENTED | AB 860, 3455 to 3456; 859, 3292 to 3295. Optional: "Frankish annals of the time record a Viking fleet raiding Italy, but name no leader." |
| 05 | At a walled city by the sea, Hastein believed he had found Rome. But the gates were barred. | PASS | LEGEND | GND 976, 977, 979 to 980; Dudo 146 (fortified, no gates). |
| 06 | So Hastein sent word that he was dying, and wished to become a Christian. | PASS | LEGEND | GND 987 to 989 ("maladie mortelle"); Dudo 164 to 166 ("infirmatus", ill rather than dying). |
| 07 | The bishop could have kept the gates shut. He chose mercy, and baptised Hastein. | **FIX** | INTERPRETATION + LEGEND | Mercy is our reading. Bishop AND count decide (DUDO-L 168; GND 990) and sponsor (DUDO-L 180 to 181; GND 1011 to 1012). **"The bishop and count could have kept the gates shut. They chose mercy, and Hastein was baptised."** |
| 08 | Then Hastein's men came weeping. Their leader was dead, and had asked to be buried in the city. | PASS | LEGEND | DUDO-L 186 to 192 ("deposcite nimium flentes ut faciant me neophitum sua urbe sepeliri"; "dixerunt eiulantes"). |
| 09 | The bishop let the funeral in. Behind the coffin, the mourners wore armour under their tunics. | PASS + storyboard FLAG | LEGEND (GND only for the armour) | Burial agreed, DUDO-L 195; GND 1016 to 1017. Dudo puts the arms in the bier instead (200 to 201). |
| 10 | Mid-funeral, Hastein leapt from the coffin and struck the bishop down. | PASS | LEGEND | DUDO-L 227 to 229 (after mass, at burial); GND 1028 to 1029 (during prayers; also kills the count). |
| 11 | Only after the city fell did the raiders learn the truth. This was not Rome. It was Luna, an old Roman town. | PASS | LEGEND (sequence); DOCUMENTED (Roman colony 177 BC) | DUDO-L 244 to 247; GND 1051 to 1053; WP-Luni 70. AB names Pisa, not Luna. |
| 12 | The first known writer to tell the coffin story, the Norman churchman Dudo, names only Hastein. | **FIX** | INTERPRETATION ("first known") + DOCUMENTED ("only Hastein") | Dudo was a Saint-Quentin (Vermandois) canon and dean, and ducal chaplain. Dudo has a bier ("feretrum"), not a coffin. **"The first known writer to tell the funeral story, the churchman Dudo, names only Hastein."** |
| 13 | Björn first joins the voyage decades later, in a chronicle by a monk, William of Jumièges. | PASS | INTERPRETATION ("first", earliest surviving) | GND 534 to 536, 952 to 953; Dudo c. 996 to 1015 vs GND c. 1050 to 1070. |
| 14 | So the city may not be the only thing this legend got wrong. | PASS | INTERPRETATION | Hedged with "may", and it does not say William invented Björn. Matches the owner's ending direction. |
| 15 | History remembers the victors. We remember the rest. | PASS | n/a (tagline) | House line, no claim. |

**Summary:**
- 13 PASS (L04 with an optional tweak, L09 with a storyboard flag), 2 FIX (L07, L12), 0 hard FLAG.
- `wc -w`: v2b = 223. With the final two FIXes (section E) = 225. With the optional L04 tweak as well = 225.

---

## E. Vellum rulings (STORYBOARD-v2.md section 4), added 2026-11-03 06:08 EST. These supersede earlier FIX wording.

### E1. L12 "Norman churchman Dudo"
- Ruling: **FIX. Accept Vellum's "the churchman Dudo".**
- Dudo was a canon, later dean, of Saint-Quentin in the Vermandois (DUDO-T 111 to 114). He was chaplain ("capellanus") to Richard II in the 1015 charter (DUDO-T 120 to 121). WP-Dudo line 2: "a Picard historian, and dean of Saint-Quentin".
- He wrote for the Norman dukes but was not a Norman.

### E2. Coffin vs bier; where the arms are
- **Dudo has a bier ("feretrum"), not a coffin.** He uses no "sarcophagus" or "loculus" (grep of the passage, DUDO-L 130 to 260).
  - DUDO-L 200: "Mihi modo facite feretrum. et superponite me quasi mortuum." Hastein lies ON the bier.
  - DUDO-L 214: "uiuus super feretrum positus".
  - DUDO-L 227: "feretro desiluit".
  - The only enclosed burial place is the prepared tomb at the monastery (DUDO-L 216: "monasterium quo sepulchrum eius erat paratum").
  - Lifshitz translates it "bier" (DUDO-T 2054, 2071, 2083).
- **Arms in Dudo:**
  - On the bier with him: DUDO-L 200 to 201, "Arma / mecum in ipso collocate".
  - Treasure and weapons displayed before it: DUDO-L 204 to 206, "Armillas et balteos / ante feretrum facite ferri ... secures / ensesque exponite".
  - He draws a sword from its scabbard when he leaps up (227 to 228). The mourners are not said to be armoured.
- **GND has the coffin and the armour.**
  - "cercueil" (GND 1015 to 1016, "se fait déposer dans un cer-/cueïl"; 1026 to 1027, "déjà enfermé / dans le cercueil"; 1028, "cerçnueil").
  - Hastein himself is "cuirassé" (1015).
  - His companions wear "leurs cuirasses sous Jenrs tuniques" (1016 to 1017).
  - He kills "de son glaive" (1028 to 1029).
- **Ruling:**
  - L01 (coffin, sword inside) and L09 (armour under tunics) are the GND version. They PASS under L02's "Legend says" frame.
  - "The coffin story" in L12 is unfair to Dudo. **FIX: "the funeral story"** (same word count). This is accurate for both: a feigned death, a funeral mass, a burial request.
  - Storyboard: any frame tied to Dudo shows a bier with the body on top and weapons alongside.

### E3. Bishop alone vs bishop and count
- **L07: not acceptable as written. FIX.**
  - Both sources make the decision joint.
  - DUDO-L 168: "Hoc audientes praesul et comes. responderunt"; the treaty "Perpetui foederis pactum uobiscum agimus" follows at 169.
  - GND 989 to 991: "l'évêque et le comte se livrèrent aux trans-/ports de leur joie, conclurent la paix".
  - Both also sponsor the baptism (DUDO-L 180 to 181; GND 1011 to 1012).
  - **FIX: "The bishop and count could have kept the gates shut. They chose mercy, and Hastein was baptised."** (+3 words.) The passive "was baptised" also avoids the unstated identity of the baptiser.
- **L09: the bishop alone is ACCEPTABLE. PASS.** He is the one who runs the funeral.
  - DUDO-L 208 to 209: "Conuocat presul campaniis / gentem".
  - DUDO-L 217: "missam pro suo filiolo celebraturus".
  - DUDO-L 224: "iussit praesul corpus ad sepulturam deferri".
  - GND 1022 to 1024: "L'évé-/que se couvre de ses vêtamens sacrés" (OCR, i.e. vêtemens).
  - Dudo's promise to receive the body is plural (DUDO-L 195: "spoponderunt corpus recipi"), so "The city let the funeral in" is an optional zero-word alternative.
  - L10 "struck the bishop down" PASSES. Both sources kill the bishop and the count; Dudo attacks the prelate first (DUDO-L 228 to 229; GND 1028 to 1029).

### E4. L07 "could have kept the gates shut" vs the sequence
- **GND sequence:**
  1. Gates barred (976).
  2. Envoy: peace and conversion (982 to 989).
  3. Bishop and count make peace, and "le peuple normand / fut admis à entrer dans la ville" (991 to 993).
  4. Baptism at the church (1005 to 1012).
  5. Back to the ship (1013 to 1014).
  6. Night: coffin and armour (1014 to 1017).
  7. Funeral to the church (1021 to 1022).
- **Dudo sequence:**
  1. Town garrisoned (146).
  2. Envoy (148 to 167).
  3. Treaty (168 to 170).
  4. Mutual trading under the truce (172 to 175: "multisque comptionibus atque mutuis conuentionibus cootuntur perfidi pagani. uicissim et christiani").
  5. Baptism (175 to 181).
  6. Back to the ships (183).
  7. Death announced and burial requested (186 to 195).
  8. Procession; Christians meet the pagans "in exitu ciuitatis" (214).
  9. Ship crews at the open gates, "portis bipatentibus", after the attack (238 to 239).
- **Ruling: PASS, no misstatement.**
  - The gates open at the peace, before the baptism, which is exactly the choice L07 describes ("could have kept the gates shut. They chose mercy").
  - L09 "let the funeral in" is a second admission, which both sources support (GND: from the ship to the church; Dudo: met at the city's exit and carried to the monastery for burial "sua urbe").
  - Dudo never mentions shut gates, only a garrison. The barred gates of L05 and L07 are GND, under the legend frame.

### E5. "chose mercy"
- **Ruling: acceptable as framed INTERPRETATION** (it sits inside L02's "Legend says").
- It is grounded in Hastein's own plea for "uestra misericordia uestraque pietate" (DUDO-L 167; DUDO-T 2014).
- **Caveat:** neither chronicler credits the bishop with mercy.
  - GND says joy ("transports de leur joie", 990 to 991).
  - At the burial stage Dudo says they were deceived and "quasi excecati", as if blinded, by the promised gifts (DUDO-L 194 to 195: "tali sophismate decepti. dandisque et accipiendis muneribus / quasi excecati").
  - So do not put "mercy" in an on-screen quote or attribute it to a source.

### E6. "first known writer" (L12) and "first joins" (L13)
- **Confirmed. INTERPRETATION, high confidence; scope "known/surviving".**
- **For the coffin ruse at Luna:**
  - No earlier text was found. Contemporary records (AB 859 to 862; FONT; the Arabic accounts in STEF 25566 to 25664; FAI 4199 to 4251) have no ruse and no Luna sack.
  - Abbott 1898: "no document before Dudo connecting Hasting's name with a Mediterranean expedition" (snippet).
- **For Björn on the voyage:**
  - Dudo names no Björn (grep of the full Latin passage and the full Lifshitz translation).
  - GND is the earliest surviving text (Abbott 1898; WP-Björn_Ironside line 18).
  - STEF 25663 to 25664 lists only William, Wace and Benoît, and the latter two are 12th century.
  - Berno in AB 858 (3153 to 3155) and FONT is on the Seine and has no Mediterranean link.

### E7. Bishop and count at Luna c. 860, and Luna's look; replacing the placeholder citation
- **A see and a county: DOCUMENTED. A named bishop or count in 860: NOT documented. Only Dudo and GND put a bishop and a count in the story.**
- **Bishops before and after** (it.wikipedia "Diocesi di Luni", bishop table; diocesilaspezia.it list):
  - Petroaldo: in an 816 Lucca grant, and at Eugene II's Roman synod of 826 (MGH Conc. 2,2, Conc. Romanum a. 826).
  - Teodolasio: an **867** Lucca document names Fraiperto as executor of the will of "Teudilascio (o Teodolasio) vescovo di Luni". He was evidently dead by 867, so he is a plausible but unproven bishop around the 850s to 860.
  - Gualterio I: elected by 872 (a John VIII letter) and consecrated Aulla in 884.
  - S. Ceccardo "? - 860", "martirizzato dai Vichinghi", is hagiographic tradition (UNCERTAIN; the diocesan list dates him "+ 895?").
- **Roman synods:**
  - Regesta Imperii's database (personspopes9c.regesta-imperii.de) summarises the 8 December 853 synod (89 named participants) and the November 861 synod (about 92). In what I could see, it lists no Luna bishop, but I did not see the full subscription lists. Treat this as "not found", not "absent".
  - So there is no synod evidence for a Luna bishop c. 853 or 861 from what I checked.
- **County:** "a countship and see under Charlemagne" (WP-Luni_Italy line 85). No count of Luna c. 860 is named in anything I read.
- **Safe phrasing:** a bishop and a count at Luna c. 860 are plausible under the legend frame. Never name them.
- **Luna's look c. 860:** see section B(4). Coastal plain at the Magra mouth, with the estuary and lagoon; a reduced walled core around the cathedral of S. Maria; the ruined forum built over with small wooden houses; the theatre and amphitheatre in ruin outside or at the edge of the walls; Apuan mountains behind.
  - WP-Luni_Italy 85 ("reduced to a small village by the time of ... Liutprand") supports "a few dozen roofs" as INTERPRETATION. Note that this is an encyclopedia line.
- **Replacing the placeholder.** WP-Luni_Italy line 88 reads "It was repeatedly sacked by sea pirates, Saracens in 849, and Vikings who settled there in 860." Its only ref is "CELESIA E 1847 ... [no title cited]". **Do not use "settled there in 860"; no source supports a settlement.** Replace it with:
  - Saracen raid 849: Annales Bertiniani a. 849, ed. G. Waitz, MGH SRG 5 (Hannover 1883), p. 37: "Mauri et Saraceni Lunam Italiae civitatem adpredantes, nullo obsistente maritima omnia usque ad Provinciam devastant." (AB file 2425 page header, 2438 to 2440.)
  - Viking raid in Italy 860: Annales Bertiniani a. 860, ed. Waitz, MGH SRG 5, p. 54: "Dani qui in Rodano fuerant Italiam petunt et Pisas civitatem aliasque capiunt, depraedantur atque devastant." (AB file 3438 page header, 3455 to 3456.) **Luna is not named.**
  - Luna as the town of the ruse: Dudo of Saint-Quentin, De moribus et actis primorum Normannorum ducum (c. 996 to 1015), Hastingus section. The Bibliotheca Augustana text "Capitulum 2" (fol. 8v to 12v), at DUDO-L 144: "Lux urbem quae Luna dicitur". Translated by Christiansen (Woodbridge 1998); Lifshitz translation lines 1991 ff. Band LEGEND.
  - William of Jumièges, Gesta Normannorum Ducum I.9 to 11 (Guizot 1826 translation, chs. IX to XI, GND 951 to 1063); ed. van Houts (Oxford 1992 to 1995). Band LEGEND.
  - For the scholarly doubt: it.wikipedia "Luna (colonia romana)", citing Frasson 2019.
  - Suggested claim line: "AB records Saracens raiding Luna in 849 and Rhône Vikings taking Pisa and other towns in 860; the Viking sack of Luna itself is told only by Dudo and William (LEGEND)."
- I did NOT edit STORYBOARD-v2.md.

### E8. Paste-ready FIX list for Scriptor (v2b md5 680db8ea… to v2c)
- L07: "The bishop could have kept the gates shut. He chose mercy, and baptised Hastein." **becomes** "The bishop and count could have kept the gates shut. They chose mercy, and Hastein was baptised."
- L12: "The first known writer to tell the coffin story, the Norman churchman Dudo, names only Hastein." **becomes** "The first known writer to tell the funeral story, the churchman Dudo, names only Hastein."
- Optional L04: "Annals of the time record a Viking fleet raiding Italy, but never name its leader." **becomes** "Frankish annals of the time record a Viking fleet raiding Italy, but name no leader." (Net 0 words.)
- All other lines PASS unchanged (L09 and L01 PASS as the GND version; storyboard note in E2).
- **Projected `wc -w`: 225** (223 + 3 - 1 + 0), with or without the L04 option. Verified on a patched temp copy; no en or em dashes.

## D. Open risks
1. **OCR noise.**
   - The GND is a French translation of 1826 (Guizot), not van Houts' Latin. Wording like "sous leurs tuniques" should be checked against van Houts' Latin before any on-screen quote.
   - AB and FONT are OCR with footnote marks.
2. **Not read directly:**
   - Christiansen's Dudo (1998) and van Houts' GND (1992 to 1995) are known only via reviews and Wikipedia.
   - Christys (2015) is known only via Wikipedia.
   - Wace and Benoît are known only via Stefansson.
   - Heimskringla ch. 10 is known only via a summary page.
   - Abbott (EHR 1898) is known only from a search snippet; the DOI fetch timed out.
3. **The bishop's identity in 860 is unresolved.** The Ceccardo link is conjecture, and the diocesan list's dating conflicts.
4. **The Viking sack of Luna itself is not in any contemporary record.**
   - AB 860 says Pisa "and others".
   - AB 849 (2438 to 2440) records a **Saracen** raid on Luna.
   - Some scholars (it.wiki, citing Frasson 2019) think the Luna story may echo the 849 raid.
   - The VO treats the whole episode as legend, which is fine, but any on-screen "860, Luna sacked" caption should be attributed.
5. **Night appears only for the death announcement (Dudo) and the arming (GND).** Do not put the church attack at night.
6. **"Annals ... never name its leader"** could be challenged via FAI. The optional "Frankish annals" FIX removes this.
7. **The Luna bishop list and the synod check rest on it.wikipedia, the diocesan site and the Regesta Imperii summaries**, not the MGH subscription lists themselves.
8. **v2b may still be edited.** This countersign is pinned to md5 680db8ead6eccfeef963ef994ae7e5e0.

## 9. Web sources consulted (public pages, 2026-11-03)
- Persée, review of van Houts, GND vol. 1 (1992): https://www.persee.fr/doc/ccmed_0007-9731_1995_sup_38_152_2632_t1_0090_0000_2
- P. Bouet, "William of Jumièges (c. 1070/71)": https://mondes-normands.caen.fr/angleterre/ensavoirplus/sources/guiljumieges.htm
- W. C. Abbott, "Hasting", EHR 13 (1898) 439 to 463 (snippet only): https://doi.org/10.1093/ehr/xiii.li.439
- William of Apulia, Deeds of Robert Guiscard, translated by G. A. Loud: https://ahc.leeds.ac.uk/download/downloads/id/965/the-deeds-of-robert-guiscard-by-william-of-apulia.pdf
- Heimskringla summary (Harald ch. 10): https://loregraph.org/sources/heimskringla-harald-sigurdson
- it.wikipedia, Luna (colonia romana): https://it.wikipedia.org/wiki/Luna_(colonia_romana)
- Treccani, "Luni", Enciclopedia dell'Arte Antica: https://www.treccani.it/enciclopedia/luni_(Enciclopedia-dell'-Arte-Antica)/
- Diocesi della Spezia, list of bishops of Luni: https://www.diocesilaspezia.it/serie-cronologica-dei-vescovi-diocesani-luni/
- it.wikipedia, Ceccardo di Luni; katolsk.no, Ceccardus; Formentini PDF (esolibri.it)

## F. FINAL LOCK CONFIRMATION (Archivist, 2026-11-03)

**File:** standalones/bjorn/raw/script-vo-v3-LOCKED.txt
**md5:** c4683d2b846a026498a830c57e3853dc (matches Vellum)
**wc -w:** 225 (cap 225, OK)
**Dash grep** (U+2013, U+2014): 0
**mtime:** 2026-11-03 06:35:09 EST

**Diff check:** compared with v2b (raw/script-vo-v2b-DRAFT.txt, md5 680db8ead6eccfeef963ef994ae7e5e0, unchanged) plus the two section E fixes (L07, L12). Only L02 and L03 differ. The L07 and L12 fix wording is present verbatim. No other line changed.

**Sources used for L02/L03:**
- William of Jumièges, GND, Guizot French translation of 1826: raw/jumieges-guizot1826-djvu.txt.
- Latin vulgate transcription: raw/allabouthistory-bjorn-gnd-latin.txt, saved from a public secondary site (allabouthistory.co.uk). It is a Migne/Duchesne-type vulgate text and NOT the van Houts critical edition. WP (raw/wp-Bjorn_Ironside, line 27, citing McTurk) gives the van Houts spellings "Bier Costae ferreae" and "Lotbroci regis filio".

### L02: "Legend says Björn Ironside, son of Ragnar Lothbrok, led a fleet intent on conquering Rome."

**Band: LEGEND. Verdict: PASS.**

**Son of Lothbroc.** William calls Bier the son of King "Lothroc" (Guizot spelling) or "Lothrocus/Lothroci" (Latin). He never uses "Ragnar".
- Guizot 533 to 535: "avec le fils de / . leur roi Lothroc, qui se nommait Bier, à la côte de / fer"
- Guizot 729 to 730 (ch. V heading): "Comment Bier, fils de Lothroc , roi de Dacie, fat chassé de sa / patrie, selon la coutume, avec Hastings son gouverneur."
- Latin 1156: "cum Lothroci regis filio, nomine Bier, costa quidem ferreæ"
- Latin 1170: "Lothrocus rex ... filium, nomine Bier Costa Ferreæ, a suo abdicat regno"

**"Ragnar Lothbrok".** This is the later Scandinavian composite name.
- Saxo (raw/saxo-elton-gutenberg1150.txt 14045 to 14049) gives Regner the nickname "Lodbrog". At 14055 to 14056 the sons include "Biorn".
- Ragnars saga loðbrókar: ch. 7 "Annarr sonr þeira hét Björn"; ch. 15 and 16 "Björn járnsíða".
- It is acceptable because the line opens "Legend says". Residual risk: a pedant can say William's father figure is a nameless "Lothroc, king of Dacia" and that "Ragnar" first attaches in 12th to 13th century Scandinavian texts. No change is needed for a Legend-framed line.

**Led a fleet.**
- Bier is "le roi de ces armées" (Guizot 1056 to 1058). The Latin calls him "Nam Bier totius excidii singnifer, exercituumque rex" (1205; "singnifer" sic in the transcription).
- Hastein "dirigeait cette expédition" (Guizot 536), and the Latin says "procurante ejus expeditionem Hastingo" (1156).
- So command is shared, with Bier as the nominal king. "Led" is fair under the Legend frame.

**Intent on conquering Rome.** Fair.
- Guizot 952 to 953 (ch. IX heading): "Hastings se rendant par mer à Rome / pour la soumettre à la domination de Bier"
- Guizot 964 to 965: "résolus d'aller attaquer à l'improviste kville [la ville, OCR] de / Rome et de s'en rendre maîtres"
- Latin 1177: "Hastingus navigans Romam ut cam [eam, OCR] subderet Bier domino suo"
- Latin 1188: "Romam deliberant clandestina irruptione obtinere"

### L03: "His tutor, the raider Hastein, planned to crown him emperor there."

**Band: LEGEND. Verdict: PASS.**

**Tutor.**
- Guizot 730 and 739: "Hastings son gouverneur", "Hastings , son gouverneur"
- Guizot 754 to 755: "avec son jeune élève"
- Latin 1170: "cum ejus pædagogo Hastingo"; "Hastingus vero a patria cum suo adolescente exsul proscriptus"
- The Latin word in this text is "pædagogus", not "nutritor". I did not find "nutritor" in either text in hand. Modern WP renders it "foster-father". "Tutor" is an accurate rendering of pædagogus/gouverneur.

**The raider.** Guizot 535 to 536: "Hastings, le plus méchant de tous les / Païens". Fair.

**Planned to crown him emperor.**
- Guizot 959 to 962: "Hastings, desirant / élever son seigneur à une plus haute fortune, com- / mença avec une troupe de complices à viser plus sé- / rieusement au diadême impérial."
- Latin 1188: "Hastingus dominum suum ad altiora cupiens provehere de imperiali diademate cum agmine complicum cœ pit attentius tractare."
- An imperial diadem means crown plus emperor. "Lord of Rome" is supported by "s'en rendre maîtres" and "subderet Bier domino suo".

**There.** The place is Rome (references above).

**Note.** Dudo (the earlier source) has no Björn. L12 and L13 already disclose this, so the new L02/L03 do not conflict with them.

### Verdict
- L02: PASS
- L03: PASS
- No FIX required.
- **STATUS: LOCKED** (raw/script-vo-v3-LOCKED.txt, md5 c4683d2b846a026498a830c57e3853dc, 225 words, 0 dashes)

**Open risk (non-blocking):** the Latin was checked against a vulgate transcription on a secondary website, not against van Houts (OMT 1992 to 1995) directly. Spellings differ (Lothrocus vs Lotbrocus), but the substance (son of the king, pædagogus, imperial diadem, Rome) matches the Guizot translation and the WP/McTurk summary.
