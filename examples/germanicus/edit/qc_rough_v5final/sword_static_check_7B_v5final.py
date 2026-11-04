import json, subprocess, math, numpy as np, cv2
from pathlib import Path
from PIL import Image
G = Path("/workspace/posterity/standalones/germanicus"); E = G/"edit"; B = E/"_build_v5final"; M = "/workspace/posterity/renders/posterity-germanicus-v5-ROUGH.mp4"
src = open(E/"build_rough_germanicus_v5.py").read(); ns = dict(np=np, cv2=cv2, Image=Image, math=math, FPS=30, W=1080, H=1920, UP=2)
for fn in ("prepare_cover", "cam", "cam_frame"):
    a = src.index(f"def {fn}("); b = src.index("\ndef ", a + 5); exec(src[a:b], ns)
seg = [s for s in json.load(open(B/"timeline.json"))["segments"] if s["id"] == "7B"][0]
p = Path(seg["prepped"]) if Path(seg["prepped"]).exists() else Path(seg["plate"]); base = ns["prepare_cover"](Image.open(p).convert("RGB"))
sw = ns["prepare_cover"](Image.open(G/"masks/v5/G7b5_persons_v5.png").convert("RGB"))
fl = ns["prepare_cover"](Image.open(G/"masks/v5/G7b5_flame_c0.png").convert("RGB"))
proc = subprocess.Popen(["ffmpeg","-v","error","-ss",f"{seg['start']:.4f}","-i",M,"-frames:v",str(seg["frames"]),"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
prev=None
for k in range(seg["frames"]):
    fr = np.frombuffer(proc.stdout.read(1080*1920*3),np.uint8).reshape(1920,1080,3)
    if k % 5 and k not in (76,77,78,79,81,82,83,84,86,87,88,89): continue
    u = k/max(seg["frames"]-1,1); ref = np.asarray(ns["cam_frame"](base, seg, u, k/30)).astype(np.int16)
    m = np.asarray(ns["cam_frame"](sw, seg, u, 0))[...,0] > 127
    f = np.asarray(ns["cam_frame"](fl, seg, u, 0))[...,0] > 127
    y,x = np.where(m); y0,y1,x0,x1 = y.min()-20,y.max()+20,x.min()-20,x.max()+20
    a_=cv2.cvtColor(fr[y0:y1,x0:x1],cv2.COLOR_RGB2GRAY).astype(np.float32); b_=cv2.cvtColor(ref[y0:y1,x0:x1].astype(np.uint8),cv2.COLOR_RGB2GRAY).astype(np.float32)
    (sx,sy),_=cv2.phaseCorrelate(b_,a_)
    yf,xf=np.where(f); a2=cv2.cvtColor(fr[700:1300,:],cv2.COLOR_RGB2GRAY).astype(np.float32); b2=cv2.cvtColor(ref[700:1300,:].astype(np.uint8),cv2.COLOR_RGB2GRAY).astype(np.float32)
    (gx,gy),_=cv2.phaseCorrelate(b2,a2)
    d=np.abs(fr.astype(np.int16)-ref).max(2)
    print(k, "sword_bbox_shift", round(sx,3), round(sy,3), "wide_band_shift", round(gx,3), round(gy,3), "sword_absdiff_mean", round(float(d[m].mean()),2), "sword_mean_signed", round(float((fr.astype(np.int16)-ref)[m].mean()),2), "flame_y", int(yf.mean()))
