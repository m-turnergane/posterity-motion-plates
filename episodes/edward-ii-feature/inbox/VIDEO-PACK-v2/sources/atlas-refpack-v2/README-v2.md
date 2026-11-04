# refpack - Edward II atlas reference pack (README v2)

Written 2026-10-31 11:32 ET. Architecture (owner, 11:07am): the owner paints the plate; the engine owns registration, routes, markers, camera, labels, effects, narration sync. Geodata is the truth, never the painting.

## Use these (v2)
- `framing_refpack_v2.json` - 4 frames (euro_16x9, britain_16x9, euro_9x16, britain_9x16): LAEA proj4, lon/lat + projected bounds, km/px, pin/title safe areas, per-stop safe-area check, label zones, medallion zone, **ornament_reserved** (compass) zone, realm-id legend, authority/verifier results, 9:16 own-plate decision.
- `img_v2/<frame>_ref_tinted_notext.png` - **attach this to the plate prompt** (layout guide, no text).
- `img_v2/<frame>_ref_bare / _ref_notext / _ref_labels / _ref_graticule / _ref_tinted_labels / _zones_overlay / _realm_ids` - reference variants; realm_ids = engine realm masks (from geodata).
- `PLATE-PROMPTS-v2.md` - paste-ready prompts, one per frame.
- `REGISTRATION-PLAN-v2.md` + `control_points_refpack_v2.json` + `img_v2/<frame>_regproto_*` - registration method, QA, deviation policy, CP tables, synthetic-warp prototype.
- Scripts: `make_framing.py`, `refpack_lib.py`, `make_refs.py` (REFPACK_TAG / REFPACK_OUT env), `make_regplan.py`.

## Superseded (kept; nothing is overwritten)
- `framing_refpack_v1.json`, `img/` - first pass made by an earlier script state (Berkeley label dropped, a data-edge border line across Austria, missing realm names, Pyrenees on the bottom edge). The scripts were edited in place afterwards, so re-running them gives v2 behaviour, not v1.

## Errata to REGISTRATION-PLAN-v2.md (file is write-once)
- section 7 'Reading': "the TPS ... roughly halves p95" holds for the 16:9 frames only (euro 3.65 vs 7.0 px, britain 5.37 vs 10.62). In the 9:16 frames p95 is 8.04 vs 10.28 (euro) and 7.94 vs 7.79 (britain, no gain): there the p95 is dominated by the synthetic bulge and frame-edge coast far from any CP. The median gain holds in all four (0.6-1.2 px vs 3.0-3.4 px).
- CP 'Elbe mouth' is the NE10m centreline end (at Hamburg, 9.82E 53.54N), not the estuary mouth at Cuxhaven; it is a valid geodata point but is inland - treat as a river-feature CP, weight it low.

## Files and md5
| md5 | path |
|---|---|
| 931301b42bdb94189cb3693b330da220 | PLATE-PROMPTS-v2.md |
| b8002aff5209e5c4a1103f9c3524c7e6 | REGISTRATION-PLAN-v2.md |
| 8081580a3824b013bf2d83c36749ea94 | control_points_refpack_v2.json |
| a158a1d187ceab52da4ff83577068289 | framing_refpack_v1.json |
| 8db7392a7264eb5630af95eb38471a47 | framing_refpack_v2.json |
| 00b0abd9c0f4626f69c73fdff8e5cba6 | img/britain_16x9_realm_ids.png |
| 56f07d5fd43f874ef0465ad4b28f116c | img/britain_16x9_ref_bare.png |
| 678431c33d128c04c65a508a1207086a | img/britain_16x9_ref_graticule.png |
| b280955b50b4208c1064a95f1380666b | img/britain_16x9_ref_labels.png |
| 89b4ca4978c017afb3f83c7ff310cb46 | img/britain_16x9_ref_notext.png |
| 571298472d9febcc4ccced12919d36b0 | img/britain_16x9_ref_tinted_labels.png |
| 1aee9a0e0714c91128fdf352472db877 | img/britain_16x9_ref_tinted_notext.png |
| cdb2b8f393fa17b4394ddb3d2cb5d2f0 | img/britain_16x9_zones_overlay.png |
| 743358f4c808f0a4b27a6868a8d25036 | img/britain_9x16_realm_ids.png |
| 730655ce0e18f8cebb4b3e99bbe08772 | img/britain_9x16_ref_bare.png |
| 7a27f3197be66a91ef278dc7063c3c9a | img/britain_9x16_ref_graticule.png |
| 4b92381d03e46924c165a881e2a82008 | img/britain_9x16_ref_labels.png |
| a8a0cae2736fead9ca5cd021bd4a0636 | img/britain_9x16_ref_notext.png |
| 383913a2deb8b41c7bb8a22b25c46387 | img/britain_9x16_ref_tinted_labels.png |
| 6332b6ae135fdc4fbf0f924fa9ee62fc | img/britain_9x16_ref_tinted_notext.png |
| aa3b2ba863837658da54205b078d2187 | img/britain_9x16_zones_overlay.png |
| 405b6de35f6e58f418b4f1f823b45027 | img/euro_16x9_realm_ids.png |
| cc795bba7225785ff2791c7423b7a6a6 | img/euro_16x9_ref_bare.png |
| 4ba5eb702a9d1c4e8724403d380b2437 | img/euro_16x9_ref_graticule.png |
| e3da9a0c4014f118b7cfa98412c9419d | img/euro_16x9_ref_labels.png |
| 7528629c91d831c76af3aae4dc3c0ded | img/euro_16x9_ref_notext.png |
| 8ffe6e8c4f758f8a1efe45b8b768c275 | img/euro_16x9_ref_tinted_labels.png |
| 8ecfd1a46c21aacebd47082b72a5bb48 | img/euro_16x9_ref_tinted_notext.png |
| 144e986c6471f7ee1a0477d423f8a1c8 | img/euro_16x9_zones_overlay.png |
| 7c877141b4568bd3ea032531914ca2a4 | img/euro_9x16_realm_ids.png |
| 15489bb5dae9e28da686f510373fa874 | img/euro_9x16_ref_bare.png |
| 5ad6d8e01b10894e2cad4efee864341a | img/euro_9x16_ref_graticule.png |
| d5169fc785c4d361aa03d6260de3ee09 | img/euro_9x16_ref_labels.png |
| 4878552ed18b44e907f0b2e272e06cfa | img/euro_9x16_ref_notext.png |
| 797625c0edfa5201748807e88fd9759d | img/euro_9x16_ref_tinted_labels.png |
| e3da62ae8158dce1b8a2d5805a93f8db | img/euro_9x16_ref_tinted_notext.png |
| af31acc2eb68096ced23e0723dbb4e73 | img/euro_9x16_zones_overlay.png |
| 638dce06f75b343c5a5ec6a9d4f66356 | img_v2/britain_16x9_realm_ids.png |
| b11a986672cd335fa2b9b2f748831237 | img_v2/britain_16x9_ref_bare.png |
| 9c767981500ea9e765f8e577a229fc7b | img_v2/britain_16x9_ref_graticule.png |
| afd8e50d49209c9d9ff6041ea40828b9 | img_v2/britain_16x9_ref_labels.png |
| fde49fa5ae6d8057122a5c00d032a98f | img_v2/britain_16x9_ref_notext.png |
| e1582995d7140e9fe6823a51e58b3697 | img_v2/britain_16x9_ref_tinted_labels.png |
| 2519b448ea7a8076d94b7ebf7e9e4bd2 | img_v2/britain_16x9_ref_tinted_notext.png |
| 975945507ffc7440e2fb645f76c23a97 | img_v2/britain_16x9_regproto_qa_overlay.png |
| 9ce82c86dcc421dd67ca25a23c850020 | img_v2/britain_16x9_regproto_synthetic_plate.png |
| 210bfedf0e57d745453c738c8333065a | img_v2/britain_16x9_zones_overlay.png |
| 10485c12eada6c982856abf952b0c443 | img_v2/britain_9x16_realm_ids.png |
| e79540cdd12b1a270939b3f6d2f60c25 | img_v2/britain_9x16_ref_bare.png |
| f9287c5975cacb431e8179f513f0a2db | img_v2/britain_9x16_ref_graticule.png |
| 3dc1ef1e273c557db0a6cfe3711a25cb | img_v2/britain_9x16_ref_labels.png |
| b90c9613a9a6bc5abd7e58fef4894f81 | img_v2/britain_9x16_ref_notext.png |
| 2c69b7a2cbaf1531d40de44f6a2622dd | img_v2/britain_9x16_ref_tinted_labels.png |
| e2b13d0547d0b74a09f5bac88c1b572e | img_v2/britain_9x16_ref_tinted_notext.png |
| 569f342f95a484e32af8712429f78244 | img_v2/britain_9x16_regproto_qa_overlay.png |
| 3c41ede7c24e8d3818d65bb2723cce6b | img_v2/britain_9x16_regproto_synthetic_plate.png |
| 66c6e6f66bab3a2bab7f4919c546ecc3 | img_v2/britain_9x16_zones_overlay.png |
| b290f41a273e5b9f48bbb3615286a592 | img_v2/euro_16x9_realm_ids.png |
| 51712532e7a52dc298225d54a4213e5b | img_v2/euro_16x9_ref_bare.png |
| 81fe01f957240ca5e1895b211f742116 | img_v2/euro_16x9_ref_graticule.png |
| 022ccec8bffb0e0b76a664e5fbd6588d | img_v2/euro_16x9_ref_labels.png |
| 9bc48839cf5e423b80f73673d4fdb6dc | img_v2/euro_16x9_ref_notext.png |
| cabe265158a8fce8a4aaeb8a198d43bb | img_v2/euro_16x9_ref_tinted_labels.png |
| 141caa4281f1b2ff20d1d9806ec39770 | img_v2/euro_16x9_ref_tinted_notext.png |
| db1b97769365937d121e9b6e6a8f1151 | img_v2/euro_16x9_regproto_qa_overlay.png |
| 189481701c8e41ad94335cf7de1ff846 | img_v2/euro_16x9_regproto_synthetic_plate.png |
| 3dad2b62ba1e50ec4e9175e8112f2cdb | img_v2/euro_16x9_zones_overlay.png |
| 313e667400b421b61b3bfaf52471178a | img_v2/euro_9x16_realm_ids.png |
| 716fc94e087ba65fcdfd9b2c1af1a2bf | img_v2/euro_9x16_ref_bare.png |
| 84ce32a5be08a4bd2498080c3d5ba1cd | img_v2/euro_9x16_ref_graticule.png |
| 29cc1f53f63ec25d22f8d2794d6229ed | img_v2/euro_9x16_ref_labels.png |
| 2186f54da24e62cabd9c2840fa790f6a | img_v2/euro_9x16_ref_notext.png |
| caa080c426021fa0ae0b75b5d4ddedfb | img_v2/euro_9x16_ref_tinted_labels.png |
| ac6f6f820ddab74d7f9d6c83fbf1b3a5 | img_v2/euro_9x16_ref_tinted_notext.png |
| 2ae0acc47b3687aca193e9ca5f0b835e | img_v2/euro_9x16_regproto_qa_overlay.png |
| ae2bdb630aa1c1316e201feb4d59dd62 | img_v2/euro_9x16_regproto_synthetic_plate.png |
| 22f37fbafe6e1b8c03d3014b56f1505d | img_v2/euro_9x16_zones_overlay.png |
| a3f98642d89d936a6644989b92a8dd9a | make_framing.py |
| c24fb6c362ce8db2b179f7c34ccfff3b | make_refs.py |
| e270727c7b307d5eedfc819250c295a6 | make_regplan.py |
| d0dabe59ffeebb1f1c0cedb2e0ad3f58 | refpack_lib.py |
