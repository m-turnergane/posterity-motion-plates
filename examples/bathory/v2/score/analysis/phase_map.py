import json,numpy as np,csv
r=json.load(open('analysis/loudness.json')); P=json.load(open('analysis/pulse.json'))
beats=[('B01a',0,1.8,'INTRUSION'),('B01b',1.8,3.5,'ISOLATION'),('B02',3.5,5.9,'UNEASE'),('B03',5.9,8.5,'UNEASE (MAP)'),('B04',8.5,10.5,'INTRUSION'),('B05',10.5,12.2,'UNEASE'),('B06',12.2,17.3,'UNEASE'),('B07',17.3,21.2,'UNEASE'),('B08',21.2,27.1,'UNEASE'),('B09',27.1,29.4,'INTRUSION (arrest, peak)'),('B10',29.4,33.5,'INTRUSION (peak)'),('B11',33.5,35.7,'ISOLATION'),('B12',35.7,39.2,'ISOLATION'),('B13',39.2,43.5,'INTRUSION blocked'),('B14',43.5,43.9,'ISOLATION (+pause)'),('B15',43.9,49.8,'UNEASE'),('B16',49.8,55.7,'UNEASE'),('B17',55.7,59.2,'UNEASE'),('B18',59.2,60.8,'ISOLATION'),('B19',60.8,63.9,'UNEASE'),('B20',63.9,69.4,'ISOLATION (closing reveal)'),('Outro',69.4,73.0,'card / tail')]
SC=1.15
cands=[('macleod_ignosi.mp3',29),('macleod_gagool.mp3',77),('sb_eyes_in_the_void.mp3',161)]
out={}
for n,off in cands:
    m=np.maximum(np.array(r[n]['M_per_s']),-60); L=int(np.ceil(73*SC)); w=m[off:off+L]; med=float(np.median(w))
    rows=[]
    for b,a,e,en in beats:
        va,ve=a*SC,e*SC; ta,te=off+va,off+ve
        seg=m[int(ta):max(int(np.ceil(te)),int(ta)+1)]
        lv=10*np.log10(np.mean(10**(seg/10)))
        rows.append(dict(beat=b,energy=en,video_s=f'{va:.1f}-{ve:.1f}',track=f'{int(ta)//60}:{ta%60:04.1f}-{int(te)//60}:{te%60:04.1f}',M_LUFS=round(float(lv),1),rel_dB=round(float(lv-med),1)))
    out[n]=dict(offset=off,window_median=round(med,1),rows=rows)
    with open(f'analysis/phasemap_{n[:-4]}_off{off}.csv','x',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=rows[0].keys()); wr.writeheader(); wr.writerows(rows)
    with open(f'analysis/energy_curve_{n[:-4]}.csv','x',newline='') as f:
        wr=csv.writer(f); wr.writerow(['track_s','M_LUFS_1s','video_s_at_offset_%d'%off])
        for s,v in enumerate(r[n]['M_per_s']): wr.writerow([s,v,s-off if s>=off else ''])
    print('\n##',n,'offset',off,'median',round(med,1))
    for x in rows: print(x)
json.dump(out,open('analysis/phasemap.json','x'),indent=1)
