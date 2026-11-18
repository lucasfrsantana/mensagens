import numpy as np, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S=2160; O=1080
rng=np.random.default_rng(5)
y,x=np.mgrid[0:S,0:S].astype(np.float32)/S
# céu: índigo -> roxo -> dourado
stops=[(0,(24,20,64)),(0.45,(88,56,130)),(0.7,(224,130,110)),(1.0,(255,205,120))]
img=np.zeros((S,S,3),np.float32)
for (a,ca),(b,cb) in zip(stops,stops[1:]):
    m=(y>=a)&(y<=b); t=((y-a)/(b-a))[...,None]
    img=np.where(m[...,None],np.array(ca)*(1-t)+np.array(cb)*t,img)
cx,cy=0.5,0.42
d=np.hypot(x-cx,y-cy)
img+=np.exp(-(d/0.28)**2)[...,None]*np.array([255,190,90])*0.55
ang=np.arctan2(y-cy,x-cx)
rays=(0.5+0.5*np.cos(ang*14))**6*np.exp(-(d/0.55)**2)*np.clip((cy+0.04-y)/0.12,0,1)
img+=rays[...,None]*np.array([255,220,150])*0.28
im=Image.fromarray(np.clip(img,0,255).astype(np.uint8)).convert('RGBA')
dr=ImageDraw.Draw(im)
# estrelas
for _ in range(60):
    sx,sy=rng.uniform(0.12,0.88),rng.uniform(0.08,0.38)
    if math.hypot(sx-.5,sy-.5)>0.42: continue
    r=rng.uniform(2,6); a=int(rng.uniform(140,255))
    dr.ellipse((sx*S-r,sy*S-r,sx*S+r,sy*S+r),fill=(255,245,220,a))
# sol
R=0.15*S; sc=(cx*S,cy*S)
glow=Image.new('RGBA',(S,S)); ImageDraw.Draw(glow).ellipse((sc[0]-R*1.25,sc[1]-R*1.25,sc[0]+R*1.25,sc[1]+R*1.25),fill=(255,230,150,160))
im=Image.alpha_composite(im,glow.filter(ImageFilter.GaussianBlur(60)))
sun=Image.new('RGBA',(S,S)); ds=ImageDraw.Draw(sun)
ds.ellipse((sc[0]-R,sc[1]-R,sc[0]+R,sc[1]+R),fill=(255,244,205,255))
# lua crescente cortando o sol (símbolo dia/noite)
m=Image.new('L',(S,S),0); dm=ImageDraw.Draw(m)
dm.ellipse((sc[0]-R,sc[1]-R,sc[0]+R,sc[1]+R),fill=255)
dm.ellipse((sc[0]-R+R*0.55,sc[1]-R-R*0.1,sc[0]+R+R*0.55,sc[1]+R-R*0.1),fill=0)
moon=Image.new('RGBA',(S,S),(255,250,225,255)); 
im=Image.alpha_composite(im,Image.composite(moon,Image.new('RGBA',(S,S),(0,0,0,0)),m))
# colinas
dr=ImageDraw.Draw(im)
def hill(off,amp,col,ph):
    pts=[(0,S)]+[(i,S*off+amp*S*math.sin(i/S*math.pi*1.6+ph)) for i in range(0,S+1,8)]+[(S,S)]
    dr.polygon(pts,fill=col)
hill(0.60,0.03,(70,45,100,255),0.5); hill(0.66,0.025,(40,28,75,255),2.0); hill(0.73,0.02,(22,16,50,255),3.5)
# textos
def vf(n,s,w=None):
    f=ImageFont.truetype('fonts/'+n,s)
    if w: f.set_variation_by_axes([w])
    return f
def ctext(t,f,yy,fill,glow=None):
    w=dr.textlength(t,font=f)
    if glow:
        g=Image.new('RGBA',(S,S)); ImageDraw.Draw(g).text(((S-w)/2,yy),t,font=f,fill=glow)
        return g.filter(ImageFilter.GaussianBlur(14))
    dr.text(((S-w)/2,yy),t,font=f,fill=fill)
NAME='Ternura e Afago'
sz=330
while ImageDraw.Draw(Image.new('L',(1,1))).textlength(NAME,font=vf('GreatVibes.ttf',sz))>1450: sz-=6
f1=vf('GreatVibes.ttf',sz); f2=vf('Montserrat.ttf',62,600)
g=ctext(NAME,f1,1250,None,(255,200,100,200)); im=Image.alpha_composite(im,g); dr=ImageDraw.Draw(im)
ctext(NAME,f1,1250,(255,244,210,255))
sub='MENSAGENS DE FÉ'; sp=10
w=sum(dr.textlength(c,font=f2)+sp for c in sub)-sp; xx=(S-w)/2
for c in sub: dr.text((xx,1650),c,font=f2,fill=(255,225,170,255)); xx+=dr.textlength(c,font=f2)+sp
# linha decorativa
dr.line((S/2-200,1610,S/2+200,1610),fill=(255,225,170,200),width=4)
im=im.convert('RGB').resize((O,O),Image.LANCZOS)
im.save('/home/lucas/Downloads/Logo_Ternura_e_Afago.png')
mask=Image.new('L',(O,O),0); ImageDraw.Draw(mask).ellipse((0,0,O-1,O-1),fill=255)
out=Image.new('RGBA',(O,O),(0,0,0,0)); out.paste(im,(0,0),mask); out.save('/home/lucas/Downloads/Logo_Ternura_e_Afago_redonda.png')
out.resize((400,400)).save('prev.png')
