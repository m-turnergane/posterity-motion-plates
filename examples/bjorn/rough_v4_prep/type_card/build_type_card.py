"""P05 v4 TYPE CARD still + font comparison strip. Reads P05 v4 grab (final frame, variant b); writes type_card_v4.png, font_strip_v4.png."""
import sys, hashlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
BJ = Path("/workspace/posterity/standalones/bjorn"); OUT = BJ / "rough_v4_prep/type_card"
FD = BJ / "rough_v4_prep/p05/fonts"; G = Path("/usr/share/fonts/truetype/sand-box/google")
FONTS = {"Uncial Antiqua": FD/"uncialantiqua/UncialAntiqua-Regular.ttf",
         "IM Fell English SC": G/"IM Fell English SC/IMFellEnglishSC-Regular.ttf",
         "MedievalSharp": FD/"medievalsharp/MedievalSharp.ttf",
         "IM Fell DW Pica Italic": FD/"imfelldwpica/IMFePIit28P.ttf",
         "IM Fell French Canon Italic": G/"IM Fell French Canon/IMFellFrenchCanon-Italic.ttf",
         "Eagle Lake": FD/"eaglelake/EagleLake-Regular.ttf"}
INK, BONE, OX = (26,26,25), (247,216,162), (112,26,20)
RG = sorted((BJ/"rough_v4/scratch/p05_rough").glob("grab_*final_f*.png"))
grab = RG[0] if RG else sorted((BJ/"rough_v4_prep/p05/test_v4").glob("grab_v4b_final_f*.png"))[0]
print("in-situ grab:", grab)
fr = Image.open(grab).convert("RGB")
def patch(box, w, h):
    return fr.crop(box).resize((w, h), Image.LANCZOS)
def text(d, xy, s, font, fill, track=0.0, anchor_c=False, shadow=None):
    # tracked text, drawn glyph by glyph
    x, y = xy; widths = [font.getlength(c) + track*font.size for c in s]; tot = sum(widths) - track*font.size
    if anchor_c: x -= tot/2
    for c, w in zip(s, widths):
        if shadow: d.text((x+2, y+2), c, font=font, fill=shadow)
        d.text((x, y), c, font=font, fill=fill); x += w
W = 1080
def strip(rows, title, h_row=150):
    H = 70 + h_row*len(rows); im = Image.new("RGB", (W, H), BONE); d = ImageDraw.Draw(im)
    d.text((40, 18), title, font=ImageFont.truetype(str(FONTS["IM Fell English SC"]), 36), fill=INK)
    for i, (name, word, size, track, choose) in enumerate(rows):
        y0 = 70 + i*h_row
        land = patch((640, 700, 1000, 760), W//2, h_row-10)  # Italy/Provence land
        sea = patch((560, 1150, 920, 1210), W//2, h_row-10)  # Mediterranean
        im.paste(land, (0, y0)); im.paste(sea, (W//2, y0))
        f = ImageFont.truetype(str(FONTS[name]), size)
        dl = ImageDraw.Draw(im)
        text(dl, (W//4, y0+50), word, f, INK, track, True)
        text(dl, (3*W//4, y0+50), word, f, BONE, track, True, shadow=(10,14,22))
        lab = f"{name}" + (f"  — {choose}" if choose else "")
        dl.rectangle((0, y0, 520, y0+30), fill=BONE); dl.text((10, y0+2), lab, font=ImageFont.truetype(str(FONTS["IM Fell English SC"]), 24), fill=OX if (choose and "only" not in choose) else INK)
    return im
realms = strip([("Uncial Antiqua", "CÓRDOBA", 40, 0.14, "v4 test only (E reads as C)"), ("IM Fell English SC", "CÓRDOBA", 44, 0.10, "RECOMMENDED"),
                ("MedievalSharp", "CÓRDOBA", 40, 0.10, False)], "Realms: ink on land  |  bone on sea")
water = strip([("IM Fell DW Pica Italic", "Mediterranean Sea", 44, 0.10, "CHOSEN"), ("IM Fell French Canon Italic", "Mediterranean Sea", 44, 0.10, False),
               ("Eagle Lake", "Mediterranean Sea", 36, 0.06, False)], "Water: ink on land  |  bone on sea")
s = Image.new("RGB", (W, realms.height + water.height), BONE); s.paste(realms, (0, 0)); s.paste(water, (0, realms.height))
s.save(OUT/"font_strip_v4.png")
# type card: in-situ grab (top), 1/3-scale legibility inset, strip below
card = Image.new("RGB", (W, 1920), BONE); d = ImageDraw.Draw(card)
d.text((40, 24), "P05 v4 type card (samples at rough size)", font=ImageFont.truetype(str(FONTS["IM Fell English SC"]), 34), fill=INK)
insitu = fr.crop((0, 560, 1080, 1300)).resize((760, 521), Image.LANCZOS); card.paste(insitu, (20, 80))
third = fr.resize((360, 640), Image.LANCZOS).crop((0, 186, 360, 434)); card.paste(third, (W-300-10, 80)) if False else None
third = fr.resize((360, 640), Image.LANCZOS); card.paste(third.crop((0, 186, 280, 434)), (790, 80))
d.text((790, 335), "1/3 scale", font=ImageFont.truetype(str(FONTS["IM Fell English SC"]), 24), fill=INK)
sm = s.resize((W, int(s.height * W / s.width))); card.paste(sm.crop((0, 0, W, min(sm.height, 1920-620))), (0, 620))
card.save(OUT/"type_card_v4.png")
for p in (OUT/"type_card_v4.png", OUT/"font_strip_v4.png"): print(p, hashlib.md5(p.read_bytes()).hexdigest())
