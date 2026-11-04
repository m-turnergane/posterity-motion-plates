# Opening sample

Cut 4 Nov 2026, about 2:10 PM America/Toronto. Owner picks from 1:44 PM are in force. The film is `var/edward-ii-feature/opening-sample/opening-sample.mp4` and is not in git.

## What was locked

| Item | Decision |
| --- | --- |
| Title | The Letter for a Buried King |
| Act I score | Anabasis I, from 0:00, no dip. Overrides the Penumbra recommendation |
| Tagline | Narrated and also written on screen in the outro. The outro is not in this sample |
| Rest of the v2.1 yes/no plan | Approved as recommended. N22 was left out. S009 is the N01 close crop with a cooled grade |
| Wordmark | No master file was coming. Two Nano Banana Pro tries are on disk and were not used. The master in the cut is the dusk-outro lettering, isolated on a clear background |

## Picture

69.733 s, 1920×1080, 30 fps, H.264, AAC stereo 48 kHz, selectable `mov_text` captions. Integrated −14.0 LUFS. True peak −1.3 dBTP.

Timings follow the Oliver recording, not the 2.4 words/s estimate. The nine locked lines were each rendered once. L08 is one recording, split at "even" onto N21. Anabasis I plays from the start and is ducked under the voice. The unducked bed sits 12 LU under the processed voice.

| Shot | Plate | Method |
| --- | --- | --- |
| S001 | H06, second take | Seedance 2.5, 6 s, 720p, no generated audio. Scaled to 1080p at 1.5×. The hand lifts off the wax. The letter stays folded and blank |
| S002 | H06 still | Engine crop on the hands. The 2k still, so the close view is not the 720p clip |
| S003 | H01 | Slow drift toward Kent |
| S004 | N14 | Slow push. Empty platform, mantle, no body |
| S005 | DK1 | Slow push on the sealed letter |
| SC01+SC02 | CB1 | Intro, 7.5 s, after the cold open. Ink, then the wordmark and the title, then ACT I. The wordmark is the shared master used as an ink mask |
| S007 | N01 | Kent, with the king still at the left edge |
| S007a | N01 | The king alone |
| S008 | N01 | Pull back across the first 26 words of L08 |
| S008a | N21 | The Gascony half of L08 |
| S009 | N01 | Closer crop, cooled. N22 was not generated |

## For the review

- The Gloucester effigy on H01 can read as a body rather than a carved wooden figure. A mourner behind Kent also wears a crown.
- The first H06 take showed writing on the letter and was rejected. The take in the cut does not.
- The generated wordmarks are not the outro face. The first was nearly black. The second spelled POSTERITY in a boxed bold serif. The cut uses the lettering from `outro_edward_ii_gloucester_dusk_OWNER.png`.
- The intro bloom is light. The stroke is a left-to-right reveal of the raster master, letter by letter. Source Serif is not on this machine. The title and ACT I are IM Fell DW Pica.
- S007 does not get Kent fully clear of the king.
- The seal clip is 720p. It is used only on the wide shot.

## Spend

Higgsfield Plus. Balance before this pass 110, after 48. Ten Nano Banana Pro stills at 2 credits, and one Seedance clip at 42. No second clip was submitted.

ElevenLabs: 1,013 characters on L01, L02, L03, L04, L05, L07, L07a, L08, and L09, plus the earlier 70-character test line. The `character-cost` header on the nine lines summed to 446. The subscription endpoint still returns 401, so that header is not treated as a credit balance.

Rebuild: `python tools/assemble_opening_sample.py`. It does not call ElevenLabs or Higgsfield.
