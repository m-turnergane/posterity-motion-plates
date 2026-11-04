import cv2,glob,sys,numpy as np
# args: out id x0 y0 x1 y1 [id x0 y0 x1 y1 ...]  -> side-by-side, each scaled to height 700
a=sys.argv; out=a[1]; ims=[]
for k in range(2,len(a),5):
    p=glob.glob(f'mid_{a[k]}_f*.jpg') if not a[k].endswith('.jpg') else [a[k]]
    im=cv2.imread(p[0]); x0,y0,x1,y1=map(int,a[k+1:k+5]); c=im[y0:y1,x0:x1]
    h=700; c=cv2.resize(c,(int(c.shape[1]*h/c.shape[0]),h),interpolation=cv2.INTER_CUBIC); ims.append(c)
cv2.imwrite(out,np.hstack(ims),[cv2.IMWRITE_JPEG_QUALITY,88])
