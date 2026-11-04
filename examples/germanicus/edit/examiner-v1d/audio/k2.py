import numpy as np, soundfile as sf
exec(open('k.py').read().split('for name in')[0])
R='/workspace/posterity/standalones/germanicus/edit/'
for lab,f in (('v1d',R+'_build_v1d/audio/stem_bed_postlim.wav'),('v1c',R+'_build_v1c/audio/stem_bed_postlim.wav')):
    x,_=sf.read(f)
    for win in (1.0,0.4):
        t,L=st(x,win,0.1); tc=t+win/2; live=(tc>=3)&(tc<=64)
        Ll=L[live]; tl=tc[live]
        # max rise within 1s
        mr=(0,0)
        for i in range(len(Ll)):
            j=slice(i+1,min(len(Ll),i+11)); 
            if j.start<len(Ll):
                r=Ll[j].max()-Ll[i]
                if r>mr[0]: mr=(round(float(r),2),round(float(tl[i]),1))
        cnt=sum(1 for i in range(len(Ll)) if i+1<len(Ll) and Ll[i+1:i+11].max()-Ll[i]>=1.5)
        print(lab,f'K-ST{win}s','range',round(float(Ll.min()),2),round(float(Ll.max()),2),'p5-p95',np.percentile(Ll,[5,95]).round(2),'maxrise<=1s',mr,'n_start_rise>=1.5',cnt)
        if win==1.0:
            for z in [(20,22),(33,36.5),(59,62.5),(63.5,66)]:
                k=(tc>=z[0])&(tc<=z[1]); print('   zone',z,round(float(L[k].min()),1),round(float(L[k].max()),1))
