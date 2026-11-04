import subprocess,re,os,sys
SRC='candidates/macleod_ignosi.mp3'; OUT='r2/previews'
def meas(f):
    e=subprocess.run(['ffmpeg','-nostats','-hide_banner','-i',f,'-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True).stderr.split('Summary:')[1]
    return float(re.search(r'I:\s*(-?[\d.]+)',e).group(1)),float(re.search(r'Peak:\s*(-?[\d.]+)',e).group(1))
def run(args): subprocess.run(['ffmpeg','-nostdin','-v','error','-n']+args,check=True)
graphs={
 'A_ignosi_off0-31_15s': f"[0:a]atrim=31:46,asetpts=N/SR/TB[o]",
 'B_ignosi_off0-00_15s': f"[0:a]atrim=0:15,asetpts=N/SR/TB[o]",
 # C: Ignosi's own low register (its 0:00-0:04.5 intro, low-passed <280 Hz) as head drone, equal-power crossfade 3.0-4.5 s
 # into Ignosi at the SAME map alignment as A (video t = track t - 31), so beat map is unchanged.
 'C_drone-xfade_ignosi_off0-31_15s': "[0:a]atrim=0:4.5,asetpts=N/SR/TB,lowpass=f=280:p=2,lowpass=f=280:p=2,volume=4dB,afade=t=out:st=3:d=1.5:curve=qsin[d];"
                                   "[0:a]atrim=34:46,asetpts=N/SR/TB,afade=t=in:st=0:d=1.5:curve=qsin,adelay=3000:all=1[m];"
                                   "[d][m]amix=inputs=2:normalize=0:duration=longest[o]",
}
for name,g in graphs.items():
    raw=f'{OUT}/_tmp_{name}.wav'
    if os.path.exists(raw): os.remove(raw)   # own scratch only
    run(['-i',SRC,'-filter_complex',g+';[o]aresample=48000,aformat=sample_fmts=flt[x]','-map','[x]','-c:a','pcm_f32le',raw])
    I,_=meas(raw); gain=-14.0-I
    for it in range(4):
        tmp=f'{OUT}/_tmp2_{name}.wav'
        if os.path.exists(tmp): os.remove(tmp)
        run(['-i',raw,'-af',f'volume={gain:.2f}dB,aresample=192000,alimiter=limit=0.84:attack=5:release=80:level=false,aresample=48000','-c:a','pcm_f32le',tmp])
        I2,TP=meas(tmp)
        if abs(I2+14)<=0.15: break
        gain+=-14.0-I2
    final=f'{OUT}/{name}_-14LUFS_bedonly.wav'
    run(['-i',tmp,'-c:a','pcm_s24le',final])
    I3,TP3=meas(final); print(name,'gain',round(gain,2),'dB  I',I3,'TP',TP3)
    os.remove(raw); os.remove(tmp)
