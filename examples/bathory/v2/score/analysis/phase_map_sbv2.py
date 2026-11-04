# storyboard-v2.md (11:43 ET DRAFT/HOLD) energies + est. timings
import json,numpy as np,csv,sys
r=json.load(open('analysis/loudness.json'))
beats=[('B01a',0,1.8,'INTRUSION'),('B01b',1.8,3.5,'ISOLATION'),('B02',3.5,5.9,'UNEASE'),('B03',5.9,8.0,'MAP'),('B04',8.0,10.4,'INTRUSION'),('B05',10.4,12.2,'UNEASE'),('B06',12.2,17.3,'UNEASE'),('B07',17.3,21.2,'INTRUSION'),('B08',21.2,27.1,'UNEASE'),('B09',27.1,29.4,'INTRUSION'),('B10',29.4,33.5,'INTRUSION'),('B11',33.5,35.7,'ISOLATION'),('B12',35.7,39.2,'ISOLATION'),('B13',39.2,43.5,'INTRUSION'),('B14',43.5,45.0,'ISOLATION'),('B15',45.0,49.4,'UNEASE'),('B16',49.4,55.3,'ISOLATION'),('B17',55.3,58.8,'UNEASE'),('B18',58.8,60.4,'ISOLATION'),('B19a',60.4,62.0,'ISOLATION'),('B19b',62.0,63.5,'UNEASE'),('B20',63.5,69.0,'ISOLATION'),('Outro',69.0,72.2,'OUTRO')]
val={'UNEASE':-2,'MAP':-2,'INTRUSION':3,'ISOLATION':-6,'OUTRO':-5}
peak={'B09':6,'B10':6}
def target(sc):
    t=np.zeros(int(np.ceil(72.2*sc)))
    for b,a,e,en in beats: t[int(a*sc):int(np.ceil(e*sc))]=peak.get(b,val[en])
    return t
names=sorted(r)
print('FIT vs storyboard-v2 (corr, best offset) per read-speed scale')
fits={}
for n in names:
    m=np.maximum(np.array(r[n]['M_per_s']),-60); sm=np.convolve(m,np.ones(3)/3,'same'); row=[]
    for sc in (1.0,1.1,1.15,1.25):
        tg=target(sc);L=len(tg)
        cs=[(np.corrcoef(sm[o:o+L],tg)[0,1],o) for o in range(0,len(sm)-L-10)]
        c,o=max(cs) if cs else (float('nan'),-1); row.append((sc,o,round(float(c),3)))
    fits[n]=row; print(n,row)
json.dump(fits,open('analysis/fit_storyboard_v2.json','x'),indent=1)
SC=1.1
for n,off in [('macleod_ignosi.mp3',31),('macleod_gagool.mp3',80),('sb_eyes_in_the_void.mp3',162)]:
    m=np.maximum(np.array(r[n]['M_per_s']),-60); L=int(np.ceil(72.2*SC)); med=float(np.median(m[off:off+L])); rows=[]
    for b,a,e,en in beats:
        va,ve=a*SC,e*SC; ta,te=off+va,off+ve
        seg=m[int(ta):max(int(np.ceil(te)),int(ta)+1)]; lv=10*np.log10(np.mean(10**(seg/10)))
        rows.append(dict(beat=b,energy=en,video_s=f'{va:.1f}-{ve:.1f}',track=f'{int(ta)//60}:{ta%60:04.1f}-{int(te)//60}:{te%60:04.1f}',M_LUFS=round(float(lv),1),rel_dB=round(float(lv-med),1)))
    with open(f'analysis/phasemap_sbv2_{n[:-4]}_off{off}_x1.1.csv','x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    print('\n##',n,off,'median',round(med,1)); [print(x['beat'],x['energy'],x['video_s'],x['track'],x['M_LUFS'],x['rel_dB']) for x in rows]
