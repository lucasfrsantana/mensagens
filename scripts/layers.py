from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=720,1280
F='fonts/'
def font(name,size,wght=None):
    f=ImageFont.truetype(F+name,size)
    if wght:
        try: f.set_variation_by_axes([wght])
        except Exception: pass
    return f
def text_layer(lines, glow=(0,0,0,170), blur=6):
    # lines: (text, font, fill, y)
    base=Image.new('RGBA',(W,H),(0,0,0,0))
    sh=Image.new('RGBA',(W,H),(0,0,0,0))
    ds=ImageDraw.Draw(sh); d=ImageDraw.Draw(base)
    for t,f,fill,y in lines:
        w=d.textlength(t,font=f); x=(W-w)/2
        ds.text((x+2,y+3),t,font=f,fill=glow)
        d.text((x,y),t,font=f,fill=fill)
    sh=sh.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(sh,base)

# gradientes (topo e base) para legibilidade
g=Image.new('RGBA',(W,H),(0,0,0,0)); px=g.load()
for y in range(H):
    a=0
    if y<420: a=int(150*(1-y/420)**1.6)
    if y>H-330: a=int(175*((y-(H-330))/330)**1.3)
    for x in range(W): px[x,y]=(20,10,0,a)
g.save('L0_grad.png')

script=font('GreatVibes.ttf',150)
serif=font('PlayfairDisplay-Italic.ttf',38,500)
sans=font('Montserrat.ttf',30,600)
gold=(255,236,180,255); white=(255,255,255,255)

text_layer([('Bom dia!',script,gold,60)],glow=(60,25,0,220),blur=8).save('L1_bomdia.png')
text_layer([('Que Deus abençoe o seu dia',serif,white,265),
            ('e encha o seu coração de paz.',serif,white,315)],blur=5).save('L2_msg.png')

# compartilhe + coração
L=text_layer([('Compartilhe com quem você ama',sans,white,1150)],blur=5)
d=ImageDraw.Draw(L)
hf=font('../fonts/../fonts/GreatVibes.ttf',10)
heart=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',40)
w=d.textlength('♥',font=heart); d.text(((W-w)/2+1,1093),'♥',font=heart,fill=(235,40,70,255))
L.save('L3_share.png')
