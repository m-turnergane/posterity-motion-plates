# Vellum ruling 11:51 ET: 30 s owner previews from the track position that lands on B04 (arrest entry, storyboard "arrest lands by 12s (B04 to B05)")
# using the DRAFT cue-sheet map at x1.10: B04 video 8.8 s. Ignosi offset 31 -> 39.8 s; Gagool offset 80 -> 88.8 s. Each 30 s window also contains B09 swell.
import subprocess,re,os
def meas(f):
    e=subprocess.run(['ffmpeg','-nostats','-hide_banner','-i',f,'-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True).stderr.split('Summary:')[1]
    return float(re.search(r'I:\s*(-?[\d.]+)',e).group(1)),float(re.search(r'Peak:\s*(-?[\d.]+)',e).group(1))
for src,start,out in [('candidates/macleod_ignosi.mp3',39.8,'ignosi_preview_30s.wav'),('candidates/macleod_gagool.mp3',88.8,'gagool_preview_30s.wav')]:
    tmp=f'r2/_tmp_{out}';subprocess.run(['ffmpeg','-v','error','-n','-ss',str(start),'-t','30','-i',src,'-af','aresample=48000','-c:a','pcm_f32le',tmp],check=True)
    I,_=meas(tmp);g=-14-I
    for _ in range(5):
        t2=f'r2/_tmp2_{out}'
        if os.path.exists(t2): os.remove(t2)
        subprocess.run(['ffmpeg','-v','error','-n','-i',tmp,'-af',f'volume={g:.2f}dB,aresample=192000,alimiter=limit=0.84:attack=5:release=80:level=false,aresample=48000,afade=t=in:d=0.5:curve=qsin,afade=t=out:st=29.5:d=0.5:curve=qsin','-c:a','pcm_f32le',t2],check=True)
        I2,TP=meas(t2)
        if abs(I2+14)<=0.1 and TP<=-1: break
        g+=-14-I2
    subprocess.run(['ffmpeg','-v','error','-n','-i',t2,'-c:a','pcm_s24le',out],check=True)
    d=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',out],capture_output=True,text=True).stdout.strip()
    print(out,'start',start,'gain',round(g,2),'I/TP',meas(out),'dur',d); os.remove(tmp); os.remove(t2)
