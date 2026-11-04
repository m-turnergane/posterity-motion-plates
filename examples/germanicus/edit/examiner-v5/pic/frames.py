import numpy as np, subprocess, json, cv2, sys
T=json.load(open('/workspace/posterity/standalones/germanicus/edit/_build_v5final/timeline.json'))['segments']
V='/workspace/posterity/renders/posterity-germanicus-v5-ROUGH.mp4'
def fr(f):
    o=subprocess.run(['ffmpeg','-v','error','-ss',f'{f/30+0.001:.4f}','-i',V,'-frames:v','1','-f','rawvideo','-pix_fmt','bgr24','-'],capture_output=True).stdout
    return np.frombuffer(o,np.uint8).reshape(1920,1080,3).copy()
tiles=[]
for s in T:
    f=(s['f0']+s['f1'])//2; im=fr(f); cv2.imwrite(f'pic/mid_{s["id"]}_f{f}.jpg',im,[cv2.IMWRITE_JPEG_QUALITY,92])
    t=cv2.resize(im,(216,384)); cv2.putText(t,f'{s["id"]} {s["start"]:.1f}-{s["end"]:.1f}',(3,16),0,0.45,(0,255,255),1); tiles.append(t)
rows=[np.hstack(tiles[i:i+5]) for i in range(0,20,5)]
cv2.imwrite('q/contact_sheet_v5_mid.jpg',np.vstack(rows),[cv2.IMWRITE_JPEG_QUALITY,80])
