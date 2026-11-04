# ARCHIVIST CHECK: script-proposal-v1.md (Edward II / Edmund of Kent long-form)

- Checked: Wed 4 Nov 2026 (EST, UTC-5), Archivist (research hand). Public sources only; no existing file edited.
- Proposal: `script-proposal-v1.md`, md5 `ba366cf96fda6340590e0ce4324f76d5` (expected ba366cf9: MATCH). 98 numbered VO lines across 8 movements.
- VO text: `raw/script-vo-v1-DRAFT.txt`, md5 `34a6180c00fe61cee910a5ad1adb4e55` (expected 34a6180c: MATCH); `wc -w` = 1682 (MATCH); 98 lines, identical to the proposal's numbered lines once line numbers and ID tags are stripped (diff clean).
- Dash check (`grep -P '[\x{2013}\x{2014}]'`): 0 hits in the proposal, 0 in the VO text, 0 in this file.
- Companion: `INFO-PACKET-LONGFORM-v1.md` (same folder) holds the OPEN/RISKS list and full source tables.
- Convention: double quotes in this file hold ONLY verbatim strings from saved captures in `raw/` (path given). Replacement VO wording is in italics, never in double quotes.
- Bands: DOCUMENTED / CONTEMPORARY CLAIM / INTERPRETATION / UNCERTAIN / LEGEND. Where a line is spoken with its attribution, the band is the band of the underlying claim; the attribution in the line is what makes it safe.

## Summary

- PASS 90, FIX 7, CUT 1 (line 31, with a fallback FIX if Vellum wants to keep it).
- FIX: 21, 29, 38, 75, 82, 90, 97. CUT: 31.
- Two FIXes are factual: line 29 (the Brut does not say Kent first heard the news at Avignon; it says Kent himself told the pope of a common report in England) and line 31 (the confession says the friar claimed to have raised the devil, not a spirit; supernatural, so cut).
- New ledger rows needed for the NR lines (proposed wording at the end).

## NR and special checks

| Item | Finding | Verdict |
|---|---|---|
| NR-1 (lines 02, 07, 08) | Kent's mother was Edward I's second wife, Margaret of France; Kent born 5 August 1301; Edward II born 1284. raw/wikipedia-Edmund_of_Woodstock__1st_Earl_of_Kent.noref.txt: "was the sixth and youngest son of King [[Edward I]] of England, and the second son of his second wife [[Margaret of France, Queen of England|Margaret of France]], and was a younger half-brother of King [[Edward II]]"; same file: "the future [[Edward II]] (born 1284)". Line 08 has the direction right: Edward is the much older one (about 17 years). | PASS (DOCUMENTED, via secondary) |
| NR-2 (line 08) | Same file: "Edmund remained loyal to his brother, and in 1321 he was created [[Earl of Kent]]." He also served in the Saint-Sardos war: "Edmund was besieged at [[La Réole]]". Great lord is fair for an earl and the king's brother. | PASS (DOCUMENTED, via secondary) |
| NR-3 (lines 09, 10) | raw/wikipedia-Edward_II.noref.txt: "Opposition also grew around Edward's treatment of his royal favourites". Mortimer: Roger Mortimer of Wigmore was a Marcher lord ("one of the most prominent of the imprisoned Marcher Lords", raw/wikipedia-Edward_II.noref.txt). An English baron is accurate (baron of Wigmore) and safe; a lord of the Welsh borderlands would be more exact. Optional, not required. | PASS (INTERPRETATION for 09; DOCUMENTED for 10) |
| NR-4 (lines 15, 16) | raw/realms-wp-Edward_III_of_England.txt: "The new king was crowned as Edward III at Westminster Abbey on 1 February at the age of 14." Teenage is right. Real power with Isabella and Mortimer: same file, "Edward was crowned at age fourteen after his father was deposed by his mother, Isabella of France, and her lover, Roger Mortimer." Real power is a historian's judgement. | PASS (DOCUMENTED for 15; INTERPRETATION for 16) |
| NR-5 (lines 21, 90) | Only source: Kathryn Warner, raw/warner-blog-2013-04-death-afterlife-2.txt: "no cause of Edward's supposed death on 21 September 1327 was ever stated in any official government source". This is an argument from silence about surviving records; the announcement itself is not in our files. Line 90 says the evidence can establish it, which is too strong. | FIX 21 and 90 (INTERPRETATION, Warner) |
| NR-6 (line 61) | Appointed bishop of Vercelli 16 June 1343: https://www.catholic-hierarchy.org/bishop/bfieschie.html (seen in a web search result this session, which listed the 16 June 1343 appointment; the page itself was not captured to raw, so treat it as secondary); Negro 2021 (iris.unito.it, Fieschi Vercellese) gives Emanuele 1343 to 1348. Warner is inconsistent: raw/warner-blog-search-fieschi.txt "he himself became bishop of Vercelli in 1343"; raw/warner-blog-search-melton.txt "Bishop of Vercelli from 1342". Line 61 gives no date, so it is safe. Use 1343 if a date is ever needed. | PASS (DOCUMENTED, via secondary) |
| INF-1 (line 75) | It is a general principle in the narrator's voice, not a finding, but "really written by a papal notary" sounds like an established fact about this letter, which survives only as a later copy. | FIX (INTERPRETATION, ours) |
| Line 29 | Avignon as the pope's seat is correct background (raw/realms-wp-Avignon.txt: "Between 1309 and 1377, during the Avignon Papacy, seven successive popes resided in Avignon"), and the line is about Kent's visit, not the Fieschi letter, so C14b is not breached. But the Brut does not say Kent first heard the news there. Brut ch. ccxxi p. 263 (raw/brut-brie-1906-part1-archiveorg_djvu.txt): Kent "spake vnto pe Pope5 lohfi pe xxij at Auy[n]on" and asked his counsel "sip pat a commune fame is 17 prou^-out al Engelawd pat he was alif" (de-hyphenated OCR). Kent brought the report to the pope. | FIX |
| Line 34 | Confession (Thompson's translation, raw/admurimuthconti00robegoog_djvu.txt app.): the archbishop sent "a letter of credence" that he would aid him "with five thousand" pounds; French "v. mille livres". Stronger than C02c's safe line but it is the confession's own claim and it is attributed in the line. Naming him as William Melton is a fair identification (archbishop of York, C02a). | PASS (CONTEMPORARY CLAIM) |
| Line 36 | Brut ch. ccxxi p. 264: "til fat he come to2 pe castel of Corf*"; the letter "closede, & enselede28 wip his owen seal". Kent did go to Corfe in person in the Brut's telling, and the line attributes it. C09 should be extended to say this. | PASS (CONTEMPORARY CLAIM) |
| Line 62 | Funeral 20 Dec 1327 (C06); letter c.1336 (Ian Mortimer EHR abstract: "Fieschi letter of c.1336") to the late 1330s (C14). That is about 8 to 11 years: roughly a decade is fair and it is attributed to historians. | PASS (UNCERTAIN, attributed) |
| Line 63 | Stubbs 1883 (raw/stubbs-chronicles-edw-i-ii-vol2-1883_djvu.txt): "leaf of the Cartulary of the ancient bishopric of Mague-" "lonne, among the departmental archives of the Herault." and "in 1368 by order of Gaucelin de Deaux, bishop of" Maguelone. A church register from Maguelone describes where the copy was made, not where it is kept now, so it does not breach C14b; the south of France is correct. C03d's Montpellier wording and C14b's no-archive rule conflict in the ledger; the script sidesteps both. Optional sharper wording: *in a register of the bishops of Maguelone, near Montpellier, in the south of France.* | PASS (DOCUMENTED) |
| Line 65 | Germain p. (118) (raw/memoiressociarcheomontpel7_djvu.txt): "Ea que audivi ex confessione patris vestri, manu propria" "scripsi". The line is a fair English rendering (Latin: the things I heard from your father's confession I have written in my own hand), not a quotation. Never put it in quotation marks on screen. | PASS (CONTEMPORARY CLAIM) |
| Line 72 | Germain: "in Braybantiam"; Brabant was a duchy (raw/realms-wp file: "The Duchy of Brabant was a state of the Holy Roman Empire, established in 1183."); the confession also mentions "the duke" of Brabant. | PASS (CONTEMPORARY CLAIM for the route; gloss DOCUMENTED) |
| Line 82 | Melton's letter is dated 14 January (C02a). Its year is UNCERTAIN (C02b): 1330 per Haines and Warner (raw/warner-blog-search-melton.txt: "almost certainly in 1330 (though 1329 is also possible)"). In the months before the arrest is true only if 1330, and it is stated as fact. Haines's abstract (raw/crossref-openalex-abstracts-2026-10-30.txt) gives "Two months afterwards" for Kent's death. Attribute it. | FIX |
| Dashes | None in the proposal or the VO text. | PASS |

## Line-by-line

| Line | Verdict | Band | Evidence | Note / replacement |
|---|---|---|---|---|
| 01 | PASS | CONTEMPORARY CLAIM | C09, C10; Brut p. 264 "closede, & enselede28" | Hook; the source is named at line 36. |
| 02 | PASS | DOCUMENTED | NR-1 (Wikipedia, Kent) | |
| 03 | PASS | DOCUMENTED | C10, C20 | |
| 04 | PASS | DOCUMENTED | C06, C28 | |
| 05 | PASS | framing | | Question. |
| 06 | PASS | framing | | Question. |
| 07 | PASS | DOCUMENTED | NR-1 | |
| 08 | PASS | DOCUMENTED | NR-1, NR-2 | The direction is correct. |
| 09 | PASS | INTERPRETATION | NR-3 | |
| 10 | PASS | DOCUMENTED | NR-3 | An English baron is safe. |
| 11 | PASS | DOCUMENTED | C11 safe wording; raw/wikipedia-Edward_II.noref.txt "accompanied by King Edward's half-brother Edmund of Woodstock, landed in Orwell on 24 September with a small force of men" | 24 Sept is (just) autumn. |
| 12 | PASS | framing | C11 | |
| 13 | PASS | DOCUMENTED; UNCERTAIN for capture site | C25, C26 | South Wales only; no town. |
| 14 | PASS | DOCUMENTED | C25 | |
| 15 | PASS | DOCUMENTED | NR-4 | Aged 14. |
| 16 | PASS | INTERPRETATION | NR-4 | |
| 17 | PASS | DOCUMENTED (actions) | C11 | No motive stated. |
| 18 | PASS | DOCUMENTED | C25 | |
| 19 | PASS | UNCERTAIN (date) | C20 | Late September is the safe wording. |
| 20 | PASS | INTERPRETATION-level secondary | C20; Carpenter "on 23 September at Lincoln" (raw/lrb-carpenter-2007-what-happened.txt) | |
| 21 | FIX | INTERPRETATION (Warner) | NR-5 | Replace with: *No surviving official record says how he had died.* |
| 22 | PASS | CONTEMPORARY CLAIM | C04; Murimuth p. 53 "Et licet multi abbates, priores, milites, bur-" | Attributed to Murimuth. |
| 23 | PASS | CONTEMPORARY CLAIM | C04; Murimuth p. 54 "perficialiter conspexissent" | |
| 24 | PASS | INTERPRETATION | C04; Carpenter "probably a wooden effigy" | |
| 25 | PASS | DOCUMENTED | C06, C20 | 20 Dec. |
| 26 | PASS | DOCUMENTED (per historian) | C10 | Body not claimed seen. |
| 27 | PASS | framing | | |
| 28 | PASS | CONTEMPORARY CLAIM | C09 | |
| 29 | FIX | CONTEMPORARY CLAIM | C09; Brut p. 263 (see special checks) | Replace with: *According to an English chronicle called the Brut, Kent went to see the pope at Avignon, where the pope held his court, and spoke of a common report in England that Edward was alive.* |
| 30 | PASS | CONTEMPORARY CLAIM | C09; confession tr. "the pope charged him, on his" then "benison" | Blessing is a fair rendering of benison. |
| 31 | CUT | CONTEMPORARY CLAIM (supernatural) | Confession tr.: "told him that he had raised up" "the devil, which declared unto him for certain that Edward," | The source says the devil, not a spirit, and the no-supernatural rule applies. If Vellum must keep it, fallback FIX: *He also said a friar had assured him that Edward was alive, claiming that the devil had told him so.* |
| 32 | PASS | CONTEMPORARY CLAIM | C09; Brut "alyf in pe 23Castel of Corf" | Attributed to the Brut. |
| 33 | PASS | CONTEMPORARY CLAIM | C08 (safe wording verbatim) | |
| 34 | PASS | CONTEMPORARY CLAIM | C02c (see special checks) | |
| 35 | PASS | INTERPRETATION | C07 | Around seventy, attributed. |
| 36 | PASS | CONTEMPORARY CLAIM | C09; Brut p. 264 | |
| 37 | PASS | CONTEMPORARY CLAIM | C09 | No office named. Deveril is also in the Nov 1330 record (Rot. Parl. ii, "Johan Deveroill"). |
| 38 | FIX | CONTEMPORARY CLAIM | C09; Brut p. 264 "fro pe castel of Corf, and come 26to Sir* Roger26" | Unattributed as written, and that the letter never reached Edward is the Brut's account. Replace with: *The Brut says the letter never reached Edward. Deveril took it to Roger Mortimer instead.* |
| 39 | PASS | CONTEMPORARY CLAIM | C05c | |
| 40 | PASS | UNCERTAIN (staging) | C05f, C28 | Safe wording. |
| 41 | PASS | DOCUMENTED | C05a (around 1400) | About seventy years is consistent with 1330 to around 1400. |
| 42 | PASS | DOCUMENTED | C05d | |
| 43 | PASS | DOCUMENTED | C28 | |
| 44 | PASS | CONTEMPORARY CLAIM | C18; Murimuth p. 60 "licet hoc totum falsum et phantasma fuisset" and "etsi verse essent, deberent" | Unjust is supported: none of the confessions or letters, even if true, should have caused his death. |
| 45 | PASS | DOCUMENTED | C13; Rot. Parl. ii 55 "Margarete Counteffe de Kent, pur lui et pur" | |
| 46 | PASS | DOCUMENTED | C27; raw/realms-wp-Edward_III_of_England.txt "captured him at Nottingham Castle on 19 October 1330" | |
| 47 | PASS | DOCUMENTED | C12 | |
| 48 | PASS | DOCUMENTED | C12; Rot. Parl. ii 52 "Chaftell de Berkle" | |
| 49 | PASS | DOCUMENTED (record) / CONTEMPORARY CLAIM (content) | C05e | |
| 50 | PASS | DOCUMENTED | C12; Rot. Parl. ii "ou il fu mort grant temps devant" | |
| 51 | PASS | DOCUMENTED | C12; Murimuth p. 62 "apud Elmes" | |
| 52 | PASS | DOCUMENTED | C13 (safe wording verbatim) | |
| 53 | PASS | INTERPRETATION (summary of the record) | C12, C05e | |
| 54 | PASS | framing | C01a | |
| 55 | PASS | DOCUMENTED | C01a; Rot. Parl. ii 57 "in cuftodia ipfius Thome" | |
| 56 | PASS | DOCUMENTED | C01a (safe wording verbatim) | |
| 57 | PASS | DOCUMENTED | C01a; "fuit ipfe tali & tanta infirmitate apud Bradeleye extra" | |
| 58 | PASS | INTERPRETATION | C01b | |
| 59 | PASS | UNCERTAIN (date) | C14 | |
| 60 | PASS | DOCUMENTED | C14b (permitted wording verbatim) | No place of writing. |
| 61 | PASS | DOCUMENTED (secondary) | NR-6 | |
| 62 | PASS | UNCERTAIN, attributed | C14 | |
| 63 | PASS | DOCUMENTED | C14, C03d; Stubbs | Optional sharper wording in the special checks. |
| 64 | PASS | INTERPRETATION | C17 | |
| 65 | PASS | CONTEMPORARY CLAIM | C03a | A rendering, not a quotation. |
| 66 | PASS | CONTEMPORARY CLAIM | C03a; Germain "dabo vobis raubas meas, ut melius evadere possitis" | |
| 67 | PASS | CONTEMPORARY CLAIM | C03a; "secrete fuit per annum cum dimidio" | |
| 68 | PASS | CONTEMPORARY CLAIM | C03a; "quia dixerat" "eum vivere, fuerat decapitatus" | |
| 69 | PASS | framing | C17 | |
| 70 | PASS | CONTEMPORARY CLAIM | C03a, C03b; "aplicuit ad portum de Sandvic"; "transivit mare apud Sclusam" | Some months, with no number. |
| 71 | PASS | CONTEMPORARY CLAIM | C03a; "transeundo per Linguam Occitanam, venit Avinionem"; "ultra xv dies" | Avignon is the letter's route claim, not where it was written. |
| 72 | PASS | CONTEMPORARY CLAIM | C03a; "de Braybantia in Coloniam" | |
| 73 | PASS | INTERPRETATION (identification) | C03c (safe wording) | |
| 74 | PASS | framing | | |
| 75 | FIX | INTERPRETATION (ours) | INF-1, C16d | Replace with: *Here is the hard part. A letter can be genuinely old, and genuinely written by the man who signed it, and still tell a story that is not true.* |
| 76 | PASS | INTERPRETATION | C16e safe wording | |
| 77 | PASS | INTERPRETATION | C16a | |
| 78 | PASS | INTERPRETATION | C16b | Disambiguation from Roger is good. |
| 79 | PASS | framing | | |
| 80 | PASS | INTERPRETATION | C10, C09, C28 | |
| 81 | PASS | INTERPRETATION | C16c | |
| 82 | FIX | CONTEMPORARY CLAIM; date UNCERTAIN | C02a, C02b, C02d | Replace with: *Third, a letter from the archbishop of York, which still survives, reported news that the former king was alive. Its modern editor dates it to about two months before Kent's death.* |
| 83 | PASS | INTERPRETATION | C01b, C16b | Hedged with can be read. |
| 84 | PASS | framing | | |
| 85 | PASS | DOCUMENTED (record) / INTERPRETATION (Haines) | C05e, C02d | |
| 86 | PASS | CONTEMPORARY CLAIM | C04 | |
| 87 | PASS | DOCUMENTED (per historian) | C10 | |
| 88 | PASS | UNCERTAIN / INTERPRETATION | C14, C16d | |
| 89 | PASS | framing | | |
| 90 | FIX | INTERPRETATION (Warner) / DOCUMENTED (1330 charge) | NR-5, C12 | Replace with: *It can establish that no surviving official record of the time said how he died, and that the new government later called it murder.* |
| 91 | PASS | DOCUMENTED | C09, C28 | |
| 92 | PASS | INTERPRETATION (ours) | C16a, C16b, C16e | |
| 93 | PASS | DOCUMENTED (actions) | C11 | |
| 94 | PASS | DOCUMENTED (per historian) | C10 | |
| 95 | PASS | DOCUMENTED | C06, C28 | |
| 96 | PASS | DOCUMENTED (execution) / framing | C28 | With his head is an idiom, not gore. |
| 97 | FIX | CONTEMPORARY CLAIM | C09, C05c | It never reached Edward is the Brut's account. Replace with: *As the Brut tells it, his letter never reached the brother it was meant for, and the question it carried has never been settled.* |
| 98 | PASS | tagline | | |

## Word count after fixes

With line 31 cut and the seven FIXes applied, the VO is 1686 words (was 1682), computed on the box from raw/script-vo-v1-DRAFT.txt.

## Proposed ledger rows for NR lines (recommend; not applied)

- NR-1: Kent born 5 Aug 1301, son of Edward I and Margaret of France; Edward II born 1284. DOCUMENTED via raw/wikipedia-Edmund_of_Woodstock__1st_Earl_of_Kent.noref.txt.
- NR-2: Kent loyal, created earl 1321, served in Gascony 1324. Same source.
- NR-3: favourites and opposition; Mortimer a Marcher lord. raw/wikipedia-Edward_II.noref.txt.
- NR-4: Edward III crowned 1 Feb 1327 aged 14. raw/realms-wp-Edward_III_of_England.txt.
- NR-5: no cause stated in any official source (Warner). INTERPRETATION.
- NR-6: Fieschi appointed bishop of Vercelli 16 June 1343 (catholic-hierarchy.org; Negro 2021). Not captured to raw this session; Warner's two posts disagree (1342, 1343).
- C09 correction: the Brut has Kent tell the pope of a common report in England (not hear it at Avignon), and has Kent go to Corfe in person.

## Re-check (2026-11-04 11:05am ET): VO md5 f35f7f3f, proposal md5 39c5921a, 1,693 words by wc
- I diffed both files against .pre-archfix. The seven fixes and both optionals are applied verbatim, with no other changes and no dashes. All of them PASS.
- L31: Vellum ruled KEEP, attributed (11:02am). The cut must be reversed. Restore it after L30 exactly as: "According to Kent's own confession, a friar had assured him that Edward was alive, claiming that the devil had told him so." It is banded as a CONTEMPORARY CLAIM (Kent's confession).
- Verdict: everything except L31 is countersigned. The full countersign waits on the file with L31 restored, and that check covers only the L31 diff.

## FULL COUNTERSIGN v2 (2026-11-04 11:06am ET)
- raw/script-vo-v2-DRAFT.txt md5 **852babf5ee00468240c33626f7dc4a26**, wc 1,715. script-proposal-v2.md md5 **6ae937e95835650b042267f341325def**.
- Diffed against v1 (34a6180c). Only L10, L21, L29, L31, L38, L63, L75, L82, L90 and L97 changed, each exactly as ruled. L31 matches the attributed KEEP wording. No dashes.
- **Verdict: COUNTERSIGNED, all 98 lines.** Any edit voids this countersign. OPEN rows (C02e, C11, C14b, C15, C16e, C17) remain out of the narration.
