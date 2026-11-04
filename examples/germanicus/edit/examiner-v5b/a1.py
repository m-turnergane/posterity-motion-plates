import json, numpy as np, soundfile as sf, subprocess
exec(open('../examiner-v1e/audio/e1.py').read().split('O={}')[0])
B=E+'_build_v5final/audio_v5b/'
raw=subprocess.run(['ffmpeg','-v','error','-i','/workspace/posterity/renders/posterity-germanicus-v5b-ROUGH.mp4','-f','f32le','-ac','2','-ar','48000','-'],capture_output=True).stdout
M=np.frombuffer(raw,np.float32).reshape(-1,2).astype(np.float64)
bed,_=sf.read(B+'stem_bed_postlim.wav'); vo,_=sf.read(B+'stem_vo_postlim.wav'); sfx,_=sf.read(B+'stem_sfx_postlim.wav'); src,_=sf.read(B+'music_seg_spliced.wav')
for a in ('vo','sfx','src'):
    if globals()[a].ndim==1: globals()[a]=np.stack([globals()[a]]*2,1)
O={}
n=min(len(M),len(bed),len(vo),len(sfx)); res=M[:n]-bed[:n]-vo[:n]-sfx[:n]
O['lens']=[len(M)/SR,len(bed)/SR,len(vo)/SR,len(sfx)/SR,len(src)/SR]
O['resid_db']=round(float(10*np.log10(np.mean(res**2)/np.mean(M[:n]**2))),1)
# residual over time (1s) to catch any unlisted SFX
t,er=env((res**2).mean(1),1.0,0.5); t,em=env((M[:n]**2).mean(1),1.0,0.5); O['resid_rel_max']=[round(float((er-em).max()),1),float(t[np.argmax(er-em)])]
# SFX stem spans
a=np.abs(sfx).max(1); nz=np.where(a>1e-5)[0]
O['sfx_nonzero']=[round(nz[0]/SR,3),round(nz[-1]/SR,3)] if len(nz) else None
blocks=[];
if len(nz):
    br=np.where(np.diff(nz)>SR*0.5)[0]; s=[nz[0]]+list(nz[br+1]); e=list(nz[br])+[nz[-1]]; blocks=[(round(x/SR,3),round(y/SR,3)) for x,y in zip(s,e)]
O['sfx_blocks']=blocks
k=slice(int(60.9*SR),int(65.6*SR))
def db(x): return round(float(10*np.log10(np.mean(x**2)+1e-15)),1)
O['seqC_rms']=dict(sfx=db(sfx[k]),bed=db(bed[k]),vo=db(vo[k]),master=db(M[k]))
ts,es=env((sfx**2).mean(1),0.1,0.02); O['sfx_edges_100ms']={f'{x:.2f}':round(float(y),1) for x,y in zip(ts,es) if 60.7<=x<=61.4 or 65.0<=x<=65.8}
# bed metrics
live=(3,111.4); d={}
ENV={}
for nm,p in (('mono',bed.mean(1)**2),('L',bed[:,0]**2),('R',bed[:,1]**2),('stereo',(bed**2).mean(1)),('src_stereo',(src**2).mean(1))):
    t1,e1=env(p,1.0,0.1); t4,e4=env(p,0.4,0.05); ENV[nm]=(t1,e1)
    d[nm]=dict(s1=stats(t1,e1,*live),s400=stats(t4,e4,*live),move1s=maxmove(t1,e1,1.0,*live),move400_in1s=maxmove(t4,e4,1.0,*live))
    for z in (33.5,76.5):
        kk=(t1>=z-2)&(t1<=z+2); d[nm][f'z{z}_1s']=dict(range=round(float(np.ptp(e1[kk])),2),at_z=round(float(np.interp(z,t1,e1)),2),med=round(float(np.median(e1[(t1>=3)&(t1<=111)])),2))
        kk=(t4>=z-1.5)&(t4<=z+1.5); d[nm][f'z{z}_400ms_range']=round(float(np.ptp(e4[kk])),2)
for nm,x in (('bed',bed),('src',src),('master',M)):
    pk=(kw(x)**2).sum(1); tS,eS=env(pk,3.0,0.1); eS-=0.691; tM,eM=env(pk,0.4,0.05); eM-=0.691
    ENV['S_'+nm]=(tS,eS); ENV['M_'+nm]=(tM,eM)
    d['K_'+nm]=dict(st3=stats(tS,eS,4.5,110),st3_move3s=maxmove(tS,eS,3.0,4.5,110),events_gt2_in3s=events(tS,eS,3.0,2.0,4.5,110),mom=stats(tM,eM,*live),mom_move1s=maxmove(tM,eM,1.0,*live))
    for z in (33.5,76.5): d['K_'+nm][f'z{z}']=dict(st3=round(float(np.interp(z,tS,eS)),2),st3_range4s=round(float(np.ptp(eS[(tS>=z-2)&(tS<=z+2)])),2),mom_range3s=round(float(np.ptp(eM[(tM>=z-1.5)&(tM<=z+1.5)])),2))
O['bed']=d
tS,eS=ENV['S_bed']; O['bed_Kst3_profile']={f'{a:.0f}':round(float(b),1) for a,b in zip(tS,eS) if abs(a-round(a))<0.01}
t1,e1=ENV['mono']; O['bed_mono1s_profile']={f'{a:.0f}':round(float(b),1) for a,b in zip(t1,e1) if abs(a-round(a))<0.01}
# master LUFS-ish integrated by region
np.savez_compressed('env_v5b.npz',**{k:np.stack(v) for k,v in ENV.items()})
json.dump(O,open('a1.json','w'),indent=1,default=float)
print(json.dumps({k:O[k] for k in O if k not in('bed_Kst3_profile','bed_mono1s_profile','bed')},default=float))
for k,v in d.items(): print(k,json.dumps(v,default=float))
print('KST',O['bed_Kst3_profile']); print('MONO',O['bed_mono1s_profile'])
