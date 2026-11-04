# ARCHIVIST SCRIPT v3.2 CHECK (delta countersign vs v3). Archivist, Wed 4 Nov 2026, about 12:55pm ET

## Header
- Checked: raw/script-vo-v3.2-PROPOSED.txt, md5 3920ece9ceaa7922641fe991daf6b1bd, wc 1898 words, 101 lines (matches brief).
- Baseline: raw/script-vo-v3-PROPOSED.txt, md5 4e8996e0170ee5a88dd4fb3ca406beee (countersigned, ARCHIVIST-SCRIPT-v3-CHECK.md 71c63a51ec1ebd8e266367088ead8da3).
- Restored-line source: raw/script-vo-v2-DRAFT.txt, md5 852babf5ee00468240c33626f7dc4a26.
- Scriptor diff script-vo-v3.2-diff-vs-v3.md, md5 ab03b6901f01777d3be4121a0c5513f6: not relied on; own diff run.
- Ledger: CLAIM-LEDGER-v3.2.md and .json (64 rows; v3 plus C36, C37, C38).
- Not countersigned: raw/script-vo-v3.1-PROPOSED.txt (8465377ececbf39273821123a3aa2cb4), interim, per Vellum.

## Own diff result
Changed file lines: 6 to 10, 54, 61 to 65, 71 to 73, 97, 98 (new), 100 (new). This matches Vellum's list (L07, L07a, L08, L09, L10, L54, L59, L60, L62, L63, L64, L70, L71, L73, L96, L96a, L97a). No unlisted changes. Below, file line (Vellum label).

## Per-line table
| File line (label) | Text (short) | Rows | Verdict | Note / fix |
|---|---|---|---|---|
| 6 (L07) | youngest son of King Edward the First ... half-brother Edward was already seventeen | NR-1, C36 | PASS | 'Youngest son' grammatically refers to Edmund of Kent, which is correct (sixth and youngest son). Edward II was the fourth son, not the youngest; the line does not say otherwise. Edward born 25 Apr 1284, Kent 5 Aug 1301: 17 years 3 months, so 'already seventeen' is right. |
| 7 (L07a) | By the time Kent was a grown man, that half-brother was king | C37 | PASS | Edward II succeeded 7 July 1307; Kent was under six. True as worded. |
| 8 (L08) | Kent stayed loyal ... Earl of Kent ... even in Gascony | NR-2 | PASS | NR-2: loyal, created earl 1321, besieged at La Réole (War of Saint-Sardos, Gascony). Gascony gloss accurate. |
| 9 (L09) | the reign Kent served was turning bitter ... reached into the king's own family | NR-3 | PASS | Connective rests on L10 (Isabella). No motive for Kent. |
| 10 (L10) | Queen Isabella ... Roger Mortimer | NR-3 | PASS | Restored, byte-identical to v2 line 10. |
| 54 (L54) | one statement in that same parliament roll | C01a, C01b | PASS | Neutral; roll is the source. |
| 61 (L59) | Years after Kent's death, a very different letter was written. | C14 | PASS | Later 1330s, after March 1330. |
| 62 (L60) | Manuel Fieschi ... notary ... addressed to ... Edward the Third | C14b-a | PASS | Signature 'domini Pape notarius'. No place of writing; no Vercelli. |
| 63 (L62) | no date, does not say where it was written | C14, C14b-a | PASS | Restored, byte-identical to v2 line 62. States absence of place only (C14b-b respected). |
| 64 (L63) | copy, made decades later, register of the bishops of Maguelone, near Montpellier | C03d, C14, C14b-a | PASS | Restored, byte-identical to v2 line 63. Copy location, not place of writing or present repository. Not the Vercelli line. |
| 65 (L64) | not the letter Kent carried to Corfe ... nothing connects the two | C17-b | PASS | Separation kept. (Kent's letter to Corfe as in v3 L36, inherited.) |
| 71 (L70) | From Corfe, the letter says ... Ireland ... hermit ... mainland of Europe | C03a, C03b | PASS | Attributed; 'some months', no number. |
| 72 (L71) | it says ... Avignon, where the pope held his court ... more than fifteen days | C03a | PASS | Avignon as stop on the claimed journey, not place of writing (C14b-b ok). |
| 73 (L73) | the letter leaves him ... hermit in Lombardy | C03a, C03c | PASS | Attributed; no Melazzo/Cecima. |
| 97 (L96) | Kent made his choice on the strength of what he had been told | C11-b | FIX | States a cause for his choice, which is a motive (C11-b blocked) and contradicts line 98 ('not why'). Fix: "Kent made his choice, and he paid for it with his head." (v3 wording). |
| 98 (L96a) | the records could tell us what Kent did, but not why | C11-a, C11-b | PASS | States no motive, as required. |
| 100 (L97a) | It reached Roger Mortimer instead. And within the year, according to Kent's widow's petition ... Mortimer ... admitted ... Kent had died wrongfully | C05c, C13, C38, C06, C12 | FIX | Admission source correct (widow's petition, Rot. Parl. ii 55), band CONTEMPORARY CLAIM, dates fine (19 Mar and 29 Nov 1330). Fault: 'It reached Roger Mortimer instead' repeats line 99 as unattributed fact (C05c is a Brut claim). Fix: "Kent's letter was meant for a brother England had already buried. And within the year, according to the petition Kent's widow put before parliament, Roger Mortimer himself, at his own death, admitted before the people that Kent had died wrongfully." |

## Sources for L97a
- Widow's petition, raw/10213330bsb_djvu.txt lines 10666 to 10683: "Margarete Counteffe de Kent" ... "Monfieur Roger de Mortymer, nadgaires Counte de la Marche, reconuft en fon moriant devant le Poeple q Je dit Counte moruft torceonoufement, em priant Mer- ci." (Mortimer at his death acknowledged before the people that the Earl died wrongfully, asking mercy.)
- Son's petition, same file lines 10650 to 10662, same admission ("le dit Counte fon piere torcenoufement moruft").
- Not found in the Brut or Murimuth captures. Dates: Kent 19 Mar 1330 (C06), Mortimer 29 Nov 1330 (C12).

## Byte-identical confirmations
- Lines 1 to 5 byte-identical to v3 (cmp clean).
- Lines 10, 63, 64 (L10, L62, L63) byte-identical to v2 lines 10, 62, 63; each was the countersigned v2 wording (ARCHIVIST-SCRIPT-v1-CHECK.md). None is the Vercelli line.

## Inherited PASS
All other 84 lines are unchanged from v3 and inherit the v3 countersign (0 fixes).

## Global checks
- No em or en dashes in the VO: PASS.
- wc 1898 words, 101 lines: PASS.
- Friar and devil line still attributed to Kent's confession (unchanged): PASS.
- No single 21 or 22 September death date: PASS.
- No supernatural stated as fact: PASS.
- Blocked rows C11-b (FIX at line 97), C14b-b, C16e-b, C17-b: otherwise respected. C02e, C15 not narrated.
- Ledger v3.2 verifier raw/_verify_quotes_v3.2.py: 272/272 quotes found, 64 rows, 0 schema errors.

## Verdict
COUNTERSIGN PENDING: 2 fixes (lines 97 and 100). The v3 countersign stays valid until the owner approves v3.2.

## Re-countersign after fixes (2026-11-04, about 12:48pm ET)

Checked file: raw/script-vo-v3.2-PROPOSED.txt, md5 11f4e6f9ac7d640d006dac33533472f6, wc 1,884 words, 101 lines, no em or en dashes.
Backup of the checked pre-fix file: raw/script-vo-v3.2-PROPOSED.txt.pre-archfix, md5 3920ece9ceaa7922641fe991daf6b1bd.

Diff against the pre-fix file shows exactly two changed lines and nothing else:
- File line 97 (L96): now "Kent made his choice, and he paid for it with his head." FIX 1 applied verbatim. PASS (C11-b respected, v3 wording).
- File line 100 (L97a): now "Kent's letter was meant for a brother England had already buried. And within the year, according to the petition Kent's widow put before parliament, Roger Mortimer himself, at his own death, admitted before the people that Kent had died wrongfully." FIX 2 applied verbatim. PASS (C38, attributed to the petition; no unattributed Brut claim).

All other lines carry their PASS from the table above.

COUNTERSIGNED against md5 11f4e6f9ac7d640d006dac33533472f6 (0 open fixes). The v3 countersign remains valid until the owner approves v3.2. Ledger: CLAIM-LEDGER-v3.2 (md 8e824c980c2f2d3c289a20ae5447e7a9, json c654b495e59d086188bf52162eec587e).
