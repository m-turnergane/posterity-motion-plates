import numpy as np, subprocess, json
R='/workspace/posterity/renders/posterity-germanicus-ROUGH-'
def P(v): return subprocess.Popen(['ffmpeg','-v','error','-i',R+v+'.mp4','-vf','scale=540:960','-f','rawvideo','-pix_fmt','gray','-'],stdout=subprocess.PIPE)
a,b=P('v1d'),P('v1e'); n=540*960; rows=[]; i=0
while True:
    x=a.stdout.read(n); y=b.stdout.read(n)
    if len(x)<n or len(y)<n: break
    d=np.abs(np.frombuffer(x,np.uint8).astype(int)-np.frombuffer(y,np.uint8).astype(int)).reshape(960,540)
    m=d>12
    if m.sum()>20:
        ys,xs=np.where(m); rows.append((i,int(m.sum()),int(d.max()),[int(xs.min()*2),int(ys.min()*2),int(xs.max()*2),int(ys.max()*2)]))
    i+=1
print('frames',i,'changed',len(rows))
# group contiguous
g=[]
for r in rows:
    if g and r[0]-g[-1][-1][0]<=1: g[-1].append(r)
    else: g.append([r])
for c in g:
    bb=[min(r[3][0] for r in c),min(r[3][1] for r in c),max(r[3][2] for r in c),max(r[3][3] for r in c)]
    print(f'f{c[0][0]}-f{c[-1][0]} n={len(c)} maxpix={max(r[1] for r in c)} maxdiff={max(r[2] for r in c)} bbox(full-res)={bb}')
json.dump(rows,open('picture_diff_v1d_v1e.json','w'))
