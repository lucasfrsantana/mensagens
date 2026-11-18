from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=720,1280
def vf(n,s,w=None):
    f=ImageFont.truetype('fonts/'+n,s)
    if w: f.set_variation_by_axes([w])
    return f
script=vf('GreatVibes.ttf',150); serif=vf('PlayfairDisplay-Italic.ttf',38,500); sans=vf('Montserrat.ttf',30,600); sm=vf('Montserrat.ttf',24,600)
def layer(items,glow,blur):
    fg=Image.new('RGBA',(W,H)); sh=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(fg); ds=ImageDraw.Draw(sh)
    for t,f,fill,y in items:
        x=(W-d.textlength(t,font=f))/2; ds.text((x+2,y+3),t,font=f,fill=glow); d.text((x,y),t,font=f,fill=fill)
    return Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)),fg)
# gradientes
g=Image.new('RGBA',(W,H)); px=g.load()
for y in range(H):
    a=0
    if y<330: a=int(120*(1-y/330)**1.5)
    if y>740: a=int(190*((y-740)/540)**1.1)
    for x in range(W): px[x,y]=(15,20,5,a)
g.save('T0.png')
layer([('Boa tarde',script,(255,244,205,255),60)],(90,45,0,230),8).save('T1.png')
w=(255,255,255,255)
layer([('Que a luz de Deus ilumine',serif,w,800),('os seus passos e renove',serif,w,850),('a sua fé a cada tarde.',serif,w,900)],(0,15,0,240),5).save('T2.png')
L=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(L)
txt='Compartilhe com quem você ama'; heart=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',30)
tw=d.textlength(txt,font=sans); hw=d.textlength('♥',font=heart); gap=12; tot=tw+gap+hw; x0=(W-tot)/2; y=1130
d.rounded_rectangle((x0-30,y-18,x0+tot+30,y+54),radius=40,fill=(20,35,10,175),outline=(255,230,160,120),width=2)
d.text((x0,y),txt,font=sans,fill=w); d.text((x0+tw+gap,y+2),'♥',font=heart,fill=(255,80,100,255))
x=(W-d.textlength('e espalhe luz por onde passar',font=sm))/2
d.text((x,y+78),'e espalhe luz por onde passar',font=sm,fill=(255,240,200,240))
L.save('T3.png')
