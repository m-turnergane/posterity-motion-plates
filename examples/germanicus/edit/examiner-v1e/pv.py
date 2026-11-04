import numpy as np, cv2, subprocess
R='/workspace/posterity/renders/posterity-germanicus-ROUGH-'
def fr(v,f):
    o=subprocess.run(['ffmpeg','-v','error','-ss',f'{f/30+0.001:.4f}','-i',R+v+'.mp4','-frames:v','1','-vf','scale=360:640','-f','rawvideo','-pix_fmt','bgr24','-'],capture_output=True).stdout
    return np.frombuffer(o,np.uint8).reshape(640,360,3)
cols=[]
for f in (40,45,70,1280,1283,1284,1290):
    a,b=fr('v1d',f),fr('v1e',f); d=np.clip(np.abs(a.astype(int)-b.astype(int))*3,0,255).astype(np.uint8)
    c=np.vstack([a,b,d]); cv2.putText(c,f'f{f}',(5,25),0,0.8,(0,255,255),2); cols.append(c)
cv2.imwrite('q/picture_diff_v1d_v1e.jpg',np.hstack(cols),[cv2.IMWRITE_JPEG_QUALITY,70])
