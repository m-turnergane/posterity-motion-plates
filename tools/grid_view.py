"""Authoring helper: crop+zoom a region with a labelled coordinate grid so polygons can be read off. usage: grid_view.py img x0 y0 x1 y1 scale out.png"""
import cv2,sys,numpy as np
def gv(src,x0,y0,x1,y1,s,out,step=50):
    b=cv2.imread(src)[y0:y1,x0:x1]; c=cv2.resize(b,None,fx=s,fy=s,interpolation=cv2.INTER_AREA if s<1 else cv2.INTER_CUBIC)
    for x in range((x0//step+1)*step,x1,step):
        X=int((x-x0)*s); cv2.line(c,(X,0),(X,c.shape[0]),(255,255,255),1); cv2.putText(c,str(x),(X+2,12),0,0.4,(0,255,255),1)
    for y in range((y0//step+1)*step,y1,step):
        Y=int((y-y0)*s); cv2.line(c,(0,Y),(c.shape[1],Y),(255,255,255),1); cv2.putText(c,str(y),(2,Y-2),0,0.4,(0,255,255),1)
    cv2.imwrite(out,c)
if __name__=='__main__':
    a=sys.argv; gv(a[1],*map(int,a[2:6]),float(a[6]),a[7])
