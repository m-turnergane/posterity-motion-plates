import subprocess,re,os
src='candidates/macleod_ignosi.mp3';out='r2/previews/EARCHECK_ignosi_track0-50_to_1-20_video0-19_to_0-49_30s.wav'
def meas(f):
    e=subprocess.run(['ffmpeg','-nostats','-hide_banner','-i',f,'-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True).stderr.split('Summary:')[1]
    return float(re.search(r'I:\s*(-?[\d.]+)',e).group(1)),float(re.search(r'Peak:\s*(-?[\d.]+)',e).group(1))
tmp='r2/previews/_tmp_ex.wav'
subprocess.run(['ffmpeg','-v','error','-n','-ss','50','-t','30','-i',src,'-af','aresample=48000','-c:a','pcm_f32le',tmp],check=True)
I,_=meas(tmp);g=-14-I
for _ in range(4):
    t2='r2/previews/_tmp_ex2.wav'
    if os.path.exists(t2): os.remove(t2)
    subprocess.run(['ffmpeg','-v','error','-n','-i',tmp,'-af',f'volume={g:.2f}dB,aresample=192000,alimiter=limit=0.84:attack=5:release=80:level=false,aresample=48000,afade=t=in:d=0.05,afade=t=out:st=29.7:d=0.3','-c:a','pcm_f32le',t2],check=True)
    I2,_=meas(t2)
    if abs(I2+14)<=0.15: break
    g+=-14-I2
subprocess.run(['ffmpeg','-v','error','-n','-i',t2,'-c:a','pcm_s24le',out],check=True)
print(out,meas(out)); os.remove(tmp); os.remove(t2)
