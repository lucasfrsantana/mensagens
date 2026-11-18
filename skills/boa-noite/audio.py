import numpy as np, wave
SR=44100; D=12.0; n=int(SR*D); t=np.arange(n)/SR
rng=np.random.default_rng(3)
def hz(m): return 440*2**((m-69)/12)
out=np.zeros(n)
# pad: Fmaj7 - Am7 - Dm9 - Bbmaj7 (3s cada)
chords=[[53,57,60,64],[57,60,64,67],[50,57,60,64],[46,53,57,62]]
for ci,ch in enumerate(chords):
    s=ci*3.0; e=s+4.2
    m=(t>=s)&(t<e); tt=t[m]-s
    env=np.minimum(1,tt/1.2)*np.clip((4.2-tt)/1.4,0,1)
    for note in ch:
        f=hz(note)
        for det in (-0.12,0.12):
            out[m]+=0.05*env*np.sin(2*np.pi*f*(1+det/100)*tt+rng.uniform(0,6))
        out[m]+=0.012*env*np.sin(2*np.pi*2*f*tt)
# caixinha de música
mel=[(0.9,77),(1.6,81),(2.3,84),(3.0,79),(4.3,81),(5.0,76),(6.2,77),(6.9,81),(7.6,84),(8.3,86),(9.4,84),(10.4,81)]
for st,nm in mel:
    m=t>=st; tt=t[m]-st; f=hz(nm)
    env=np.exp(-tt*2.2)*np.minimum(1,tt/0.005)
    out[m]+=0.09*env*(np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2*f*tt)+0.08*np.sin(2*np.pi*3.01*f*tt))
# reverb simples
rev=np.zeros(n)
for d,g in ((0.031,0.5),(0.047,0.45),(0.071,0.4),(0.113,0.35),(0.173,0.3),(0.251,0.25)):
    k=int(d*SR); r=np.zeros(n); r[k:]=out[:-k]*g; rev+=r
out=out+0.6*rev
# grilos
cr=np.zeros(n)
for c0 in np.arange(0.5,D,0.9):
    for j in range(3):
        s=c0+j*0.06+rng.uniform(0,0.02); m=(t>=s)&(t<s+0.035); tt=t[m]-s
        cr[m]+=np.sin(2*np.pi*4300*tt)*np.sin(np.pi*tt/0.035)
cr2=np.roll(cr,int(0.37*SR))*0.6
out+=0.010*cr+0.007*np.roll(cr2,int(0.2*SR))
fade=np.minimum(1,t/1.0)*np.clip((D-t)/1.5,0,1)
out*=fade; out=out/np.abs(out).max()*0.6
st=np.stack([out,np.roll(out,int(0.012*SR))],1)
with wave.open('trilha.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes())
