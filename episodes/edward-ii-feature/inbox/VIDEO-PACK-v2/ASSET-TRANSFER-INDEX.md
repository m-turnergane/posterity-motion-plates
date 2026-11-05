# ASSET TRANSFER INDEX (VIDEO-PACK-v2)

- The DOCS zip is **docs only**; media ships separately as 10 independent MEDIA zips, each under 24 MiB with the prefix `VIDEO-PACK-v2-MEDIA/` and its own PART-NN-MANIFEST.txt (md5, bytes).
- The full per-file list, with md5s, is in ASSET-TRANSFER-INDEX.csv (128 rows).
- Statuses: REQUIRED, OPTIONAL, REGENERABLE (can be rebuilt or downloaded), MISSING.

## Pointers and gaps

| status | item | how Atelier Jr gets it | notes |
|---|---|---|---|
| REQUIRED | engine.bundle (posterity-motion-plates, branch engine/consolidate-2026-11-04, HEAD c3a192dd) | Atelier Jr handoff DOCS/package (already delivered); git clone engine.bundle | code, PRESETS.md, ChronicleHookV3-2b, outro builder, register_b03/b13, cartography/maps scripts, fonts/ofl; NOT duplicated here |
| REQUIRED | Source Serif Pro (Semibold etc.) | install from the official Adobe source-serif release (OFL); not redistributed here | house Shorts title face; OFL.txt not on box |
| REQUIRED | IM Fell / EagleLake / MedievalSharp / UncialAntiqua | engine.bundle | map labels, optional engraved caps |
| REQUIRED | VO / mix / delivery presets | DOCS zip + engine.bundle | ElevenLabs Oliver jfIS2w2yJi0grJZPyEsk; key from env, never recorded |
| MISSING | POSTERITY wordmark master (vector or >=4K alpha) | owner supplies or approves a trace of the baked outro lettering | needed for exact-geometry stroke reveal (LONGFORM-HOUSE-INTRO) |
| MISSING | b06 (referenced once in PLATE-PROMPTS) | owner plate archive https://drive.google.com/drive/folders/1oSSP805SIUXEVhGBA7ytg3vkcpegHR9w if it exists | else regenerate from PLATE-PROMPTS |
| OPTIONAL | posterity-edward-ii-v3b-ROUGH-v1c.mp4 | owner Drive (not readable by the bot connector) | Short rough reference |
| OPTIONAL | owner video dump folder | owner Drive | prior renders |
| REGENERABLE | v2.1: 34 required new/hero/card/atlas plates (H01-H06, N01-N19, N21, DK1, DR1, DF2, DM1, CB1, E01, AB, AE) + 2 optional (N22, N23); N20 RESERVE | Atelier Jr generates from PLATE-PROMPTS (v2.1, script v3.2) | none exist yet |
| REGENERABLE | VO renders, 101 line IDs of script v3.2 LOCKED | Atelier Jr renders via ElevenLabs per README presets | one render per canonical v3.2 line (sources/raw/script-vo-v3.2-LOCKED.txt) |

## MEDIA parts (box: /workspace/posterity/handoff/edward-ii-v2-media/)

| part | files | contents |
|---|---|---|
| EDWARD-II-VIDEO-PACK-v2-MEDIA-part01-of-10.zip | 16 | atlas-refpack-img_v2 x1, geodata x14, score x1 |
| EDWARD-II-VIDEO-PACK-v2-MEDIA-part02-of-10.zip | 5 | geodata x3, score x1, short-plates-v3b x1 |
| EDWARD-II-VIDEO-PACK-v2-MEDIA-part03-of-10.zip | 4 | geodata x3, score x1 |
| EDWARD-II-VIDEO-PACK-v2-MEDIA-part04-of-10.zip | 3 | geodata x2, score x1 |
| EDWARD-II-VIDEO-PACK-v2-MEDIA-part05-of-10.zip | 5 | atlas-refpack-img_v2 x1, geodata x3, score x1 |
| EDWARD-II-VIDEO-PACK-v2-MEDIA-part06-of-10.zip | 9 | T01-tomb-photos x2, geodata x3, short-plates-v3b x4 |
| EDWARD-II-VIDEO-PACK-v2-MEDIA-part07-of-10.zip | 11 | atlas-refpack-img_v2 x1, geodata x3, short-plates-v3b x7 |
| EDWARD-II-VIDEO-PACK-v2-MEDIA-part08-of-10.zip | 15 | T01-tomb-photos x1, atlas-refpack-img_v2 x1, geodata x4, short-plates-v3b x9 |
| EDWARD-II-VIDEO-PACK-v2-MEDIA-part09-of-10.zip | 40 | atlas-refpack-img_v2 x34, geodata x6 |
| EDWARD-II-VIDEO-PACK-v2-MEDIA-part10-of-10.zip | 10 | T01-tomb-photos x1, atlas-refpack-img_v2 x2, geodata x7 |

## T01 tomb photos (Wikimedia Commons, CC0, by Poliphilo; sha1 values match Commons)

| file | page | px | bytes |
|---|---|---|---|
| Tomb_of_Edward_II,_Gloucester_Cathedral_01.jpg | https://commons.wikimedia.org/wiki/File:Tomb_of_Edward_II,_Gloucester_Cathedral_01.jpg | 5184x3888 | 5093908 |
| Tomb_of_Edward_II,_Gloucester_Cathedral_03.jpg | https://commons.wikimedia.org/wiki/File:Tomb_of_Edward_II,_Gloucester_Cathedral_03.jpg | 5184x3888 | 5288271 |
| Tomb_of_Edward_II,_Gloucester_Cathedral_04.jpg | https://commons.wikimedia.org/wiki/File:Tomb_of_Edward_II,_Gloucester_Cathedral_04.jpg | 3217x2413 | 1881548 |

The Commons imageinfo JSON is shipped alongside as licence evidence.

Short plates b11, b16 and b17 are not on the box and are not referenced by this pack. rejected/ is excluded.
