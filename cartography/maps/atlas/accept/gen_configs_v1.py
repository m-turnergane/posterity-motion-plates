#!/usr/bin/env python3
"""Acceptance-test v1 configs: four NATIVE plates (2a/2b x 16:9/9:16), each with its own framing, marker scale and label
sizes; derived from the p0b configs (same stops, seeds, basemap, evidence grammar).  Writes new files only."""
import copy, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); CFG = os.path.join(os.path.dirname(HERE), "configs")
A = json.load(open(f"{CFG}/edward_map2a_atlas_p0b.json")); B = json.load(open(f"{CFG}/edward_map2b_atlas_p0b_w50.json"))

def mk(base, name, center, width_km, plate, out, push, cps, search, chains_fn, about):
    c = copy.deepcopy(base); c["name"] = name; c["map"] = dict(center_lonlat=center, width_km=width_km)
    c["plate_wh"] = plate; c["out_wh"] = out; c["push"] = push; c["about"] = about
    c["control_points"] = [dict(cp, search_px=search) for cp in base["control_points"] if cp["ref"] in cps]
    chains_fn(c); return c

def ch(c, cid): return next(x for x in c["chains"] if x["id"] == cid)
def stop(chn, row): return next(s for s in chn["stops"] if s["row"] == row)

def a_chains(doc_w, doc_r, doc_rw, cl_w, cl_r, cl_rw, dash, lpx):
    def f(c):
        d, k = ch(c, "britain_documented"), ch(c, "britain_fieschi")
        d.update(width=doc_w, ring_r=doc_r, ring_w=doc_rw); k.update(width=cl_w, ring_r=cl_r, ring_w=cl_rw, dash=dash)
        k["stops"] = [s for s in k["stops"] if s["row"] != "2-08"]      # Part 1 never reaches Sluis (drawn on 2b)
        for s in d["stops"] + k["stops"]:
            if s.get("label"): s["label_px"] = lpx[s["label"]]
        c["drop_note"] = "2-08 Sluis omitted from the 2a accept plate: Part 1 stops at the Corfe departure; Sluis is reached on 2b."
    return f

def b_chains(bw, br, brw, bdash, cw, cr, crw, cdash, sl_r, sl_w, lpx):
    def f(c):
        d, k, n = ch(c, "britain_documented"), ch(c, "britain_fieschi"), ch(c, "continent")
        d.update(width=bw, ring_r=br, ring_w=brw); k.update(width=bw, ring_r=br, ring_w=brw, dash=bdash)
        n.update(width=cw, ring_r=cr, ring_w=crw, dash=cdash)
        stop(k, "2-05")["label"] = "Corfe"; stop(k, "2-07")["label"] = "Sandwich"
        s8 = stop(k, "2-08"); s8.update(ring_r=sl_r, ring_w=sl_w)
        stop(n, "2-13")["label"] = "Brabant"; stop(n, "2-13")["label_note"] = "MAP-PLACES 2-13: OMIT, tint or label only: Brabant"
        for s in d["stops"] + k["stops"] + n["stops"]:
            if s.get("label"): s["label_px"] = lpx[s["label"]]
        c["label_note"] = "Normandy (2-09) and Languedoc (2-10) stay unlabelled: MAP-PLACES allows no on-screen text for them."
    return f

ab = "Acceptance test v1 (step 2). "
out = {
 "accept_v1_map2a_16x9": mk(A, "accept_v1_map2a_16x9", [-2.3, 52.0], 1060, [2880, 1620], [1920, 1080], [1.0, 2.2],
        ["Land's End", "Lizard Point, Cornwall", "Portland Bill", "Selsey Bill", "Hartland Point", "Cap Gris-Nez", "Great Orme"], 35,
        a_chains(8.4, 25.0, 6.2, 6.4, 25.0, 4.8, [31.0, 21.0], dict(Chepstow=46, Kenilworth=46, Berkeley=44, Corfe=44, Sandwich=46, Glamorgan=40, Ireland=40)),
        ab + "Native 16:9 plate for Part 1 (map 2a), same framing as p0b at 1.41x plate resolution (push up to 2.2x, density <= 1.5)."),
 "accept_v1_map2b_16x9": mk(B, "accept_v1_map2b_16x9", [0.9, 48.7], 2300, [3840, 2160], [1920, 1080], [1.0, 2.95],
        ["Land's End", "Pointe du Raz", "Cap de la Hague", "Cap Gris-Nez", "Mizen Head", "Den Helder", "Portofino", "Cape Finisterre"], 38,
        b_chains(5.2, 16.0, 4.0, [26.0, 17.0], 9.5, 26.0, 6.0, [44.0, 30.0], 20.0, 5.0,
                 dict(Corfe=38, Sandwich=40, Sluis=40, Ireland=36, Avignon=72, Paris=72, Brabant=64, Cologne=72, Milan=72)),
        ab + "Native 16:9 plate for Part 2 (map 2b), same framing as p0b at 1.875x plate resolution (Britain viewed at ~2.2-2.9x push, continent at ~1.1-1.4x)."),
 "accept_v1_map2a_9x16": mk(A, "accept_v1_map2a_9x16", [-2.4, 51.9], 760, [1620, 2880], [1080, 1920], [1.0, 2.2],
        ["Land's End", "Lizard Point, Cornwall", "Portland Bill", "Selsey Bill", "Hartland Point", "Cap Gris-Nez", "Great Orme"], 28,
        a_chains(8.0, 24.0, 6.0, 6.2, 24.0, 4.6, [28.0, 19.0], dict(Chepstow=48, Kenilworth=48, Berkeley=46, Corfe=46, Sandwich=48, Glamorgan=42, Ireland=42)),
        ab + "Native 9:16 portrait plate for Part 1 (map 2a): own framing (760 km wide), own marker and label scale."),
 "accept_v1_map2b_9x16": mk(B, "accept_v1_map2b_9x16", [1.6, 48.7], 1500, [2160, 3840], [1080, 1920], [1.0, 2.95],
        ["Land's End", "Pointe du Raz", "Cap de la Hague", "Cap Gris-Nez", "Den Helder", "Portofino"], 32,
        b_chains(4.6, 14.0, 3.6, [22.0, 15.0], 8.0, 22.0, 5.2, [36.0, 24.0], 17.0, 4.4,
                 dict(Corfe=36, Sandwich=36, Sluis=36, Ireland=34, Avignon=60, Paris=60, Brabant=54, Cologne=60, Milan=60)),
        ab + "Native 9:16 portrait plate for Part 2 (map 2b): own framing (1500 km wide), own marker and label scale."),
}
for k, c in out.items():
    p = f"{HERE}/configs/{k}.json"; assert not os.path.exists(p), p
    json.dump(c, open(p, "w"), indent=1); print(p)
