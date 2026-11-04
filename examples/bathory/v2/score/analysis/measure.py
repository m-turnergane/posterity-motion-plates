import subprocess,re,json,glob,os,numpy as np
res={}
for f in sorted(glob.glob('candidates/*.mp3')):
    dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]).decode())
    p=subprocess.run(['ffmpeg','-nostats','-hide_banner','-i',f,'-filter_complex','ebur128=peak=true','-f','null','-'],capture_output=True,text=True).stderr
    M=[];T=[]
    for m in re.finditer(r't:\s*([\d.]+)\s+TARGET.*?M:\s*(-?[\d.]+|-inf)',p):
        T.append(float(m.group(1)));v=m.group(2);M.append(-70.0 if 'inf' in v else float(v))
    T=np.array(T);M=np.array(M)
    per=[]
    for s in range(int(dur)):
        sel=M[(T>s)&(T<=s+1)]
        # energy-mean of momentary
        per.append(round(float(10*np.log10(np.mean(10**(sel/10)))) if len(sel) else -70,1))
    I=float(re.search(r'I:\s*(-?[\d.]+) LUFS',p.split('Summary:')[1]).group(1))
    LRA=float(re.search(r'LRA:\s*([\d.]+) LU',p.split('Summary:')[1]).group(1))
    TP=re.search(r'Peak:\s*(-?[\d.]+|-inf) dBFS',p.split('Summary:')[1]).group(1)
    first=next((i for i,v in enumerate(per) if v>-40),None)
    res[os.path.basename(f)]={'dur':round(dur,2),'I':I,'LRA':LRA,'TP':TP,'first_sec_above_-40':first,'M_per_s':per}
    print(os.path.basename(f),round(dur,1),'I',I,'LRA',LRA,'TP',TP,'first',first)
json.dump(res,open('analysis/loudness.json','w'))
