# ARCHIVIST SCRIPT CHECK v3: Edward II / Edmund, Earl of Kent (long-form)
Archivist, Wed 4 Nov 2026, 12:40 EST. Check only. The v2 countersign (raw/script-vo-v2-DRAFT.txt, md5 852babf5ee00468240c33626f7dc4a26) remains valid until the owner approves v3.

## Files checked (md5sum, verified)
- raw/script-vo-v3-PROPOSED.txt: 4e8996e0170ee5a88dd4fb3ca406beee; wc: 1,675 words, 98 lines (incl. L57a, L57b, L86a; L06, L61, L72 cut).
- script-proposal-v3-SURGICAL.md: 383c393ecd00e48b0a2a15b12716388b
- CLAIM-LEDGER-v3.md: 3238bb7d635d5f32fc4a466666cdc8c1; CLAIM-LEDGER-v3.json: ecc9afb6b351729b6801c7685eff98fb
- Baseline: raw/script-vo-v2-DRAFT.txt 852babf5ee00468240c33626f7dc4a26 (1,715 words, 98 lines); ARCHIVIST-SCRIPT-v1-CHECK.md 631a6212f0a995475ac33f6d964e16c1
- Runtime: 1,675 / 2.4 w/s = about 11:38 paced (10:57 raw at 2.55); v2 was about 11:54.

## Opening L01 to L10: full check (per Vellum, owner sample)
| Line | v3 text | Ledger rows | Verdict | Note |
|---|---|---|---|---|
| L01 | The king's own brother sealed a letter for a king that England had already buried. | C09, C10 | PASS | Brut p. 264: letter "closede, & enselede wip his owen seal"; Corfe visit postdates the Gloucester funeral (C10). Brut attribution lands at L36, L38, L97. Unchanged from v2. |
| L02 | The brother was Edmund, Earl of Kent. The buried king was his half-brother, Edward the Second. | NR-1 | PASS | Unchanged. |
| L03 | Kent had stood at Edward's funeral at Gloucester. | C10 | PASS | C10 allows "Kent was at the funeral"; no claim he saw the body. Dropping "announced" removes the C20 dependency; L19 carries the announcement. |
| L04 | Just over two years later, Kent was beheaded for plotting to set his brother free. | C06, C28 | PASS | C06 "just over two years after the funeral"; C28 condemned and executed. Winchester still at L43. |
| L05 | Why would a king's brother risk his life to rescue a man the whole kingdom had mourned? | framing | PASS | Question; no motive asserted (C11-b respected). |
| L06 | (CUT) | framing | PASS (cut safe) | Rhetorical question only; L89 stands alone. |
| L07 | Edmund of Kent was a younger son of King Edward the First, by the old king's second marriage. | NR-1 | PASS | Unchanged, NR-1 wording. |
| L08 | Edward the Second was his much older half-brother, and for years Kent served him as a great lord. | NR-1, NR-2 | PASS | Within NR-2 scope (between "one of the great lords of the realm" and fallback "Kent served him"). |
| L09 | But Edward's reign turned bitter. His favourites had turned England's barons against him. | NR-3 | PASS | Unchanged, INTERPRETATION per NR-3 wording. |
| L10 | In the end his own queen, Isabella, turned against him too, with her ally Roger Mortimer, a lord of the Welsh borderlands. | NR-3 | PASS | Same facts as v2; NR-3 permits the Welsh borderlands description. |

## Changed, new and cut lines (L11 onward)
| Line | v3 text | Ledger rows | Verdict | Note |
|---|---|---|---|---|
| L54 | But one statement in the same record has been read in two ways. | C16 family | PASS | Neutral setup. |
| L57a | The same parliament condemned two of Edward's keepers, Thomas Gurney and William Ockley, for his murder. | C30 | PASS | C30 permitted wording verbatim; no method named (C33). |
| L57b | Early the next year, a jury of knights cleared Lord Berkeley of the king's death. Yet the same record says the king was murdered by keepers Berkeley had appointed. | C31 | PASS | Preceding context is the November parliament (L47, L57a: "the same parliament", Nov 1330). Acquittal at the octave of St Hilary, i.e. January 1331: Rot. Parl. ii (raw/10213330bsb_djvu.txt line 11126) "in Parliamento suo apud Westm', in octabis Sci Hillarii proximo futuri"; "nullo est culpabilis de morte"; "Rex extitit murdratus". "Early the next year" = 1331 is correct. |
| L58 | So the record itself treats the death as a murder. Some historians still read Berkeley's first words as a denial that the king had died at all. Others read them as a lord denying any part in a killing. | C30, C31, C16 rows | PASS (INTERPRETATION) | Fair to C30/C31 (record says "murdrerunt", "murdratus"). Both readings attributed to historians, unnamed; no C16e-b attribution. |
| L59 | Years later, a very different letter was written. | C14 | PASS | |
| L60 | A notary of the pope, an Italian churchman named Manuel Fieschi, wrote to the young king. | C14b-a | PASS | C14b-a wording plus "Italian churchman" (from countersigned v2 L61). No place. |
| L61 | (CUT) Vercelli line | C35 | PASS (cut safe) | No later line references Vercelli; "Italian churchman" moved to L60. |
| L62 | The letter has no date. Historians think it was written roughly a decade after the funeral. | C14, C14b-a | PASS | Dropping "does not say where it was written" is allowed; no place named. |
| L63 | It survives only as a later copy, in a register from Maguelone, in the south of France. | C14b-a, C03d, C14b-b | PASS | Maguelone given as provenance of the register only, not place of writing or present repository. Montpellier dropped. |
| L64 | This is not Kent's letter. It has a different writer and a different reader, and nothing in the record connects the two. | C17-a, C17-b | PASS | Separation kept; L59 and L62 carry the later date. |
| L70 | From there, the letter says, he kept moving: to Ireland for some months, then back to England dressed as a hermit, and across the sea into Europe. | C03a | PASS | Attributed ("the letter says"). |
| L71 | It says he reached Avignon, where Pope John kept him for more than fifteen days. | C03a, C14b-b | PASS | Avignon is the letter's claimed itinerary, attributed, not the place of writing. |
| L72 | (CUT) Paris, Brabant, Cologne, Milan | C03a | PASS (cut safe) | No surviving line names any of these. |
| L73 | And it leaves him living as a hermit in Lombardy, in northern Italy. | C03a | PASS | Attributed ("it leaves him"). |
| L86a | And the same record that holds Berkeley's words also condemns Edward's keepers for his murder. | C30, C31 | PASS | Record fact. |
| L91 | It can establish what Kent did, and that he and others believed the reports that his brother was alive. | C11-a, C09, C02a, C16c | PASS | Actions only, no motive (C11-b). "Others" rests on the archbishop's letter (C02a) and the backers (C16c, confession). |
| L92 | But belief is not proof. None of it shows that Edward survived, and most historians still hold that he died at Berkeley. | C16e-a, C16a, C17-b | PASS | Separates belief from proof; consensus per C16e-a. |
| L96 | Kent made his choice, and he paid for it with his head. | C28 | PASS | |
| L97 | As the Brut tells it, the letter he sealed for his brother never reached him. It went to Roger Mortimer instead. | C09 | PASS | Brut ch. ccxxi p. 264 (raw/brut-brie-1906-part1-archiveorg_djvu.txt lines 15871 to 15883): Kent "toke a lettre vnto pe forsaide Sir Iohn, and praiede him hertly pat he wolde take hit to Kyng Edward his broper"; Deveril "went in al the haste pat he might fro pe castel of Corf, and come to Sir Roger Mortymer, and toke him pe lettre pat Sir Edmund of Wodestoke, Erl of Kent, hade take him closede, & enselede wip his owen seal." Same letter (Kent's to Edward), sent by Kent via Deveril, delivered by Deveril to Mortimer. Line is accurate and attributed; echoes L38. |
Also edited in the hook: L03, L04, L05, L08, L10 (checked above).

## Inherited PASS (unchanged from countersigned v2)
L01, L02, L07, L09, L11 to L53, L55 to L57, L65 to L69, L74 to L90 (excluding L86a), L93 to L95, L98. Byte-identical to v2 per diff; v2 countersign carries over.

## Compression and cuts
- Fieschi apparatus (L59 to L65) and itinerary (L70 to L73): every itinerary line still attributed to the letter; no place of writing; no C17-b link; L74 keeps "that is what the letter claims"; no line implies the letter proves survival.
- Cuts L06, L61, L72 remove no attribution, hedge or context a surviving line needs.
- No -b or OPEN proposition introduced (C02e, C11-b, C14b-b, C15, C16e-b, C17-b all absent).

## Global checks
- Em/en dashes in VO: 0. None in this file.
- wc matches proposal: 1,675 words, 98 lines.
- Supernatural: L31 unchanged, attributed to Kent's confession (C09b).
- Death date: no 21 or 22 Sept stated (L19 "late September"; C20).
- Vercelli: no longer in VO; if restored, yearless (C35).
- No years in VO.

## Final verdict
COUNTERSIGNED against md5 4e8996e0170ee5a88dd4fb3ca406beee (0 fixes). The v2 countersign remains valid until the owner approves v3.
