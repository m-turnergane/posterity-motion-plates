# atlas/p1 — three strong-pigment palette concepts of map 2b

Same frame, zoom, borders, relief, labels and route geometry in every treatment (config `configs/edward_map2b_atlas_p1.json` = p0b frame). Rendered by `make_p1.py` with `chronicle_atlas_p1.py` (reuses p0/p0b geometry; new painter, partition and route ink). Generated 2026-10-31 10:03 ET.

## Treatments

### heraldic
Royal Heraldic: flat armorial tinctures (gules, azure, or, purpure, tenne) laid edge-to-edge like a roll of arms; clean pale parchment, crisp sepia ink.

palette RGB: {"england": [176, 30, 40], "england_light": [208, 112, 104], "france": [32, 66, 158], "france_fam": [126, 154, 206], "empire": [208, 154, 42], "castile": [114, 44, 106], "aragon": [206, 108, 40], "scotland": [38, 104, 86], "portugal": [50, 118, 60]}; flanders [147, 148, 157]; sea [62, 92, 108]; parchment [218, 198, 156]; border ink [44, 30, 24]

- noroute: `atlas/p1/stills/p1_map2b_heraldic_noroute_1920x1080.png` md5 `e4921689231984ad08ef67f9c9d336e3`
- route: `atlas/p1/stills/p1_map2b_heraldic_route_1920x1080.png` md5 `c08b347af1d8830ca3f1af5038963474`
- phone: `atlas/p1/phone/p1_map2b_heraldic_route_phone360x640.png` md5 `5c150b09fac3169040da28263b710446`
- full640: `atlas/p1/phone/p1_map2b_heraldic_route_640x360.png` md5 `63d8c6cb5e641c9e18274c5c05194d5c`

### illuminated
Illuminated Manuscript: ground mineral pigments on vellum -- cinnabar/vermilion, lapis ultramarine, gold ochre, folium purple, minium -- with gilt hairlines tracing every inked frontier and coast.

palette RGB: {"england": [200, 56, 36], "england_light": [220, 134, 116], "france": [34, 50, 134], "france_fam": [122, 136, 194], "empire": [204, 154, 58], "castile": [126, 60, 112], "aragon": [218, 118, 58], "scotland": [60, 126, 106], "portugal": [68, 128, 70]}; flanders [157, 153, 161]; sea [48, 96, 82]; parchment [232, 216, 178]; border ink [60, 38, 28]

- noroute: `atlas/p1/stills/p1_map2b_illuminated_noroute_1920x1080.png` md5 `f0a2972c3468eb8f82d2e8e4287745f6`
- route: `atlas/p1/stills/p1_map2b_illuminated_route_1920x1080.png` md5 `87460f6ff8b4c17c87ec7a6466d3d162`
- phone: `atlas/p1/phone/p1_map2b_illuminated_route_phone360x640.png` md5 `6aa457fbf7eba49b5d29fdbe616f20db`
- full640: `atlas/p1/phone/p1_map2b_illuminated_route_640x360.png` md5 `8cddb2af68ea1cf20c92f7251f246ff3`

### campaign
Campaign Chronicle: deep earth-weight grand-strategy colours -- oxblood, slate royal blue, antique gold, plum, sienna -- on darker worn parchment with heavy umber frontiers.

palette RGB: {"england": [126, 26, 30], "england_light": [166, 96, 86], "france": [50, 74, 124], "france_fam": [148, 162, 184], "empire": [130, 92, 30], "castile": [98, 48, 66], "aragon": [164, 92, 44], "scotland": [70, 88, 58], "portugal": [48, 96, 92], "flanders": [180, 172, 186]}; flanders [180, 172, 186]; sea [24, 42, 58]; parchment [204, 174, 126]; border ink [30, 20, 14]

- noroute: `atlas/p1/stills/p1_map2b_campaign_noroute_1920x1080.png` md5 `01c6bf00c5f3d1a24513cd03f0e713ca`
- route: `atlas/p1/stills/p1_map2b_campaign_route_1920x1080.png` md5 `0a31fa1baa7f6c4584e4b2d162804255`
- phone: `atlas/p1/phone/p1_map2b_campaign_route_phone360x640.png` md5 `82add40e8fd91aac84343e78eba79c3c`
- full640: `atlas/p1/phone/p1_map2b_campaign_route_640x360.png` md5 `2b2563432eadcabac196c2206270dc54`

## Comparison sheet

`atlas/p1/sheets/p1_map2b_compare.png` md5 `9da51ffd471b614b206f9b30d0774eac`. No text. Rows top→bottom: heraldic, illuminated, campaign. Columns: no-route still, route still, phone 360x640 crop.

## Phone crop

x0=921 of 1920, width 608 → 360x640; labels whole ['Sluis', 'Avignon', 'Paris', 'Cologne'], cut [] (Milan pin inside, Milan label wholly outside).

## Proofs

`atlas/p1/proofs/p1_map2b_proofs.json` md5 `73a84a18bada6a02a636e5eb2f8fea96`: realm verifier, raster checks, authority refusal, text audit, phone contrast, ΔE00, label collisions.

## Code

- `atlas/p1/chronicle_atlas_p1.py` md5 `34f392c86de13b32ca1ef4a5d99b56c8`
- `atlas/p1/make_p1.py` md5 `501a689d35f6bdea41b862921feaea09`
- `atlas/p1/configs/edward_map2b_atlas_p1.json` md5 `d230d4bb4fb81502791e3127d39fbce1`
