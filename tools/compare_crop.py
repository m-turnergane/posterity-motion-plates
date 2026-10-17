"""Authoring helper: side-by-side zoomed crop (static | animated). usage: compare_crop.py static.png animated.png x0 y0 x1 y1 scale out.png"""
import cv2,sys,numpy as np
st=cv2.imread(sys.argv[1]); an=cv2.imread(sys.argv[2]); x0,y0,x1,y1=map(int,sys.argv[3:7]); s=float(sys.argv[7])
a=cv2.resize(st[y0:y1,x0:x1],None,fx=s,fy=s,interpolation=cv2.INTER_CUBIC); b=cv2.resize(an[y0:y1,x0:x1],None,fx=s,fy=s,interpolation=cv2.INTER_CUBIC)
cv2.imwrite(sys.argv[8],np.hstack([a,np.full((a.shape[0],6,3),255,np.uint8),b]))
