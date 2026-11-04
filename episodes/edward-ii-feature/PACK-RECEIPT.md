# Edward pack receipt, 4 Nov 2026, 1:28 PM America/Toronto

Drive folder `post-1-edward pack`, id `1mXJMAlaffw-n0UYBfnboj5xE_ZYEMRzG`. Twelve zips. The current text pack is v2.1. The v2 docs zip was read and not stored. v2.1 supersedes it.

## On disk and in git

`inbox/VIDEO-PACK-v2/` is the v2.1 docs zip, 77 files. Four reference PNGs in `sources/atlas-refpack-v2/` are on disk and gitignored. Locked script md5 `11f4e6f9ac7d640d006dac33533472f6` matches the README (101 lines, 1,884 words).

`inbox/VIDEO-PACK-v2-MEDIA/` is media part 10 only (159,885 bytes). It includes `geodata/realms/realms_1327_v1.geojson` (md5 `df3715dba36767682ae0183d387ac32e`) and five OHM realm JSON files. Two realm-id PNGs are gitignored. `ne_10m_lakes.shx` is only the index of a shapefile whose other parts are in the unretrieved zips.

## On this disk, not in git

`var/edward-ii-feature/retrieved/`

| File | Check |
| --- | --- |
| Tomb photos 01, 03, 04 | sha1 matches `commons_imageinfo_T01_2026-11-04.json`. Sizes 5,093,908 / 5,288,271 / 1,881,548. Fetched from Wikimedia Commons because their Drive zips are over 10 MB. CC0 |
| Anabasis I, Katabasis I, Penumbra, Unraveling, Memories Of Stone | md5 matches `SCORE-PLAN.md`. Fetched from the Scott Buckley URLs saved in the pack's licence pages. CC BY 4.0 |

## Not retrieved

Drive media parts 01–09. Sizes 13.8–24.8 MB. The connector stops at 10 MB (`provider_response_too_large`). Those zips hold the 40 atlas guide images, the 21 Edward Short plates, most of the geodata, and two small required coordinate files (`waypoint_coords_wikidata_2026-10-30.json`, `wikipedia_coords_2026-10-30.json`).

Still missing from the pack's own index: the POSTERITY wordmark master, and Short plate b06.

Nothing was generated.
