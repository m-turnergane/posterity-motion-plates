import numpy as np, subprocess, cv2, sys
V='/workspace/posterity/renders/posterity-germanicus-v5-ROUGH.mp4'
def fr(f):
    o=subprocess.run(['ffmpeg','-v','error','-ss',f'{f/30+0.001:.4f}','-i',V,'-frames:v','1','-f','rawvideo','-pix_fmt','bgr24','-'],capture_output=True).stdout
    return np.frombuffer(o,np.uint8).reshape(1920,1080,3).copy()
for f in map(int,sys.argv[1:]): cv2.imwrite(f'f{f}.jpg',fr(f),[cv2.IMWRITE_JPEG_QUALITY,90])
