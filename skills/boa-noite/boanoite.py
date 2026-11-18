import numpy as np, subprocess, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage

import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1]; OUT = sys.argv[2]
CFG = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else {}
def cfg(k, d): return CFG.get(k, d)
FPS, DUR = 30, 12.0
N = int(FPS * DUR)
OW, OH = (720, 1280) if cfg('fast', False) else (1080, 1920)
SK = OW / 1080
rng = np.random.default_rng(7)

# ---------- canvas base ----------
src = Image.open(SRC).convert('RGB')
C = 1200 / src.width                      # orig -> canvas
CW, CH = 1200, round(src.height * C)
base = np.asarray(src.resize((CW, CH), Image.LANCZOS)).astype(np.float32) / 255
def P(x, y): return x * C, y * C          # orig coords -> canvas

def gauss(r, s):
    y, x = np.mgrid[-r:r+1, -r:r+1]
    return np.exp(-(x*x + y*y) / (2*s*s)).astype(np.float32)

def add(canvas, spr, cx, cy, color, k):
    if k <= 0.003: return
    r = spr.shape[0] // 2; cx, cy = int(round(cx)), int(round(cy))
    x0, y0, x1, y1 = cx-r, cy-r, cx+r+1, cy+r+1
    sx0, sy0 = max(0, -x0), max(0, -y0)
    x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(canvas.shape[1], x1), min(canvas.shape[0], y1)
    if x1 <= x0 or y1 <= y0: return
    s = spr[sy0:sy0+(y1-y0), sx0:sx0+(x1-x0)]
    canvas[y0:y1, x0:x1] += s[..., None] * np.array(color, np.float32) * k

def blend(canvas, spr, cx, cy, color, a):
    if a <= 0.003: return
    r = spr.shape[0] // 2; cx, cy = int(round(cx)), int(round(cy))
    x0, y0, x1, y1 = cx-r, cy-r, cx+r+1, cy+r+1
    sx0, sy0 = max(0, -x0), max(0, -y0)
    x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(canvas.shape[1], x1), min(canvas.shape[0], y1)
    if x1 <= x0 or y1 <= y0: return
    m = spr[sy0:sy0+(y1-y0), sx0:sx0+(x1-x0)][..., None] * a
    canvas[y0:y1, x0:x1] = canvas[y0:y1, x0:x1] * (1-m) + np.array(color, np.float32) * m

# ---------- star detection ----------
L = base.mean(axis=2)
peaks = (L == ndimage.maximum_filter(L, 9)) & (L > 0.78)
ys, xs = np.nonzero(peaks)
mx, my = P(*cfg('moon', [1142, 578])[:2]); mr = cfg('moon', [1142, 578, 206])[2] * C if len(cfg('moon', [0,0,206])) > 2 else 206 * C
stars = []
for x, y in zip(xs, ys):
    if y > P(0, cfg('stars_max_y', 1600))[1]: continue
    if math.hypot(x-mx, y-my) < mr * 1.35: continue
    sat = base[y, x].max() - base[y, x].min()
    if sat > 0.35: continue
    stars.append((x, y, L[y, x]))
stars.sort(key=lambda s: -s[2]); stars = stars[:90]
star_ph = rng.uniform(0, 2*np.pi, len(stars)); star_f = rng.uniform(0.25, 0.9, len(stars))
star_big = np.array([s[2] for s in stars]) > 0.9

def flare(r, s):
    y, x = np.mgrid[-r:r+1, -r:r+1].astype(np.float32)
    core = np.exp(-(x*x+y*y)/(2*s*s))
    rays = np.exp(-np.abs(y)/0.9) * np.exp(-np.abs(x)/(r*0.32)) + np.exp(-np.abs(x)/0.9) * np.exp(-np.abs(y)/(r*0.32))
    return (core + 0.55*rays).astype(np.float32)
FL_BIG, FL_SM = flare(26, 2.4), flare(14, 1.6)

# ---------- moon glow ----------
yy, xx = np.mgrid[0:CH, 0:CW].astype(np.float32)
dm = np.hypot(xx-mx, yy-my)
moon_glow = (np.exp(-((dm/(mr*2.2))**2)) * np.clip((dm - mr*0.2)/(mr*0.9), 0, 1)).astype(np.float32)[..., None]

# ---------- windows ----------
wx, wy = P(*cfg('windows', [1092, 1893]))
HAS_WIN = 'windows' in CFG or not CFG
win_glow = np.exp(-(((xx-wx)/(95*C))**2 + ((yy-wy)/(55*C))**2)).astype(np.float32)[..., None]

# ---------- water ripple ----------
HAS_WATER = 'water' in CFG or not CFG
w_top, w_bot = P(0, cfg('water', [2045, 2420])[0])[1], P(0, cfg('water', [2045, 2420])[1])[1]
band = np.clip((yy[:, 0]-w_top)/40, 0, 1) * np.clip((w_bot-yy[:, 0])/60, 0, 1)
reflect = np.exp(-(((xx-P(cfg('reflection_x', 1000),0)[0])/(380*C))**2)) * band[:, None]   # brilho do reflexo
rows = np.arange(CH)

# ---------- fireflies ----------
NF = 48
ff = dict(x=rng.uniform(0, CW, NF), y=rng.uniform(P(0,1950)[1], CH-20, NF),
          ax=rng.uniform(15, 45, NF), ay=rng.uniform(10, 35, NF),
          fx=rng.uniform(0.05, 0.18, NF), fy=rng.uniform(0.07, 0.22, NF),
          ph=rng.uniform(0, 6.3, NF), pf=rng.uniform(0.3, 0.8, NF), sz=rng.uniform(0.7, 1.3, NF))
FF = gauss(22, 6); FFc = gauss(5, 1.6)

# ---------- smoke ----------
chx, chy = P(*cfg('chimney', [1122, 1792]))
HAS_SMOKE = 'chimney' in CFG or not CFG
SMK = [gauss(r, r/2.6) for r in range(6, 40)]
smoke_spawn = np.arange(-6, DUR, 0.35)

# ---------- shooting star ----------
ss0, ss1 = np.array(P(*cfg('shooting_from', [560, 420]))), np.array(P(*cfg('shooting_to', [130, 760]))); ss_t0, ss_d = 5.2, 0.9
SS = gauss(6, 1.8)

# ---------- text layers (output coords) ----------
def vfont(name, size, wght=None):
    f = ImageFont.truetype(F+name, size)
    if wght:
        try: f.set_variation_by_axes([wght])
        except Exception: pass
    return f
F = os.path.join(HERE, 'fonts') + '/'
script = vfont('GreatVibes.ttf', int(180*SK))
serif = vfont('PlayfairDisplay-Italic.ttf', int(50*SK), 500)
sans = vfont('Montserrat.ttf', int(40*SK), 600)
sans_s = vfont('Montserrat.ttf', int(34*SK), 600)

def layer(draw_fn, glow_col, blur, glow_k=1.0):
    fg = Image.new('RGBA', (OW, OH)); draw_fn(ImageDraw.Draw(fg), None)
    sh = Image.new('RGBA', (OW, OH)); draw_fn(ImageDraw.Draw(sh), glow_col)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(sh).astype(np.float32)/255; a[..., 3] *= glow_k
    b = np.asarray(fg).astype(np.float32)/255
    return a, b

def centered(d, t, f, y, fill, col):
    w = d.textlength(t, font=f); d.text(((OW-w)/2, y), t, font=f, fill=col or fill)

TITLE_Y = int(cfg('title_y', 70)*SK)
def d_title(d, col): centered(d, cfg('title', 'Boa noite'), script, TITLE_Y, (255, 238, 196, 255), col)
title = layer(d_title, (255, 210, 120, 200), 18, 0.9)
title_sh = layer(d_title, (10, 5, 30, 230), 6)
tb = np.nonzero(title[1][..., 3].max(0) > 0)[0]; TX0, TX1 = tb.min(), tb.max()

L1 = layer(lambda d, c: centered(d, cfg('line1', 'Entregue a Deus o cansaço de hoje.'), serif, int(640*SK), (255, 255, 255, 255), c), (8, 4, 30, 235), 6)
L2 = layer(lambda d, c: (centered(d, cfg('line2a', 'Ele vela o seu sono enquanto'), serif, int(730*SK), (236, 228, 255, 255), c),
                         centered(d, cfg('line2b', 'as estrelas cuidam do céu.'), serif, int(795*SK), (236, 228, 255, 255), c)), (8, 4, 30, 235), 6)

# pill de compartilhamento
txt = cfg('share', 'Envie esta paz para quem você ama')
tmp = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
tw = tmp.textlength(txt, font=sans)
heart_f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', int(44*SK))
heart_big = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 44)
hw = tmp.textlength('♥', font=heart_f); gap = int(16*SK)
tot = tw + gap + hw; px0 = (OW - tot)/2; PY = int(1700*SK)
pill = Image.new('RGBA', (OW, OH)); dp = ImageDraw.Draw(pill)
dp.rounded_rectangle((px0-40*SK, PY-24*SK, px0+tot+40*SK, PY+(50+24)*SK), radius=int(60*SK), fill=(22, 12, 48, 175), outline=(255, 220, 150, 120), width=2)
dp.text((px0, PY), txt, font=sans, fill=(255, 255, 255, 255))
w2 = dp.textlength(cfg('share2', 'e durma com o coração leve'), font=sans_s)
dp.text(((OW-w2)/2, PY+int(108*SK)), cfg('share2', 'e durma com o coração leve'), font=sans_s, fill=(255, 236, 196, 235))
shp = Image.new('RGBA', (OW, OH)); ImageDraw.Draw(shp).text(((OW-w2)/2+2, PY+int(111*SK)), cfg('share2', 'e durma com o coração leve'), font=sans_s, fill=(0, 0, 20, 255))
shp = shp.filter(ImageFilter.GaussianBlur(5))
pill = Image.alpha_composite(shp, pill)
PILL = np.asarray(pill).astype(np.float32)/255
HX, HY = px0 + tw + gap + hw/2, PY + int(30*SK)
heart_img = Image.new('RGBA', (90, 90)); ImageDraw.Draw(heart_img).text((45, 45), '♥', font=heart_big, fill=(255, 80, 110, 255), anchor='mm')

# vinheta
oy, ox = np.mgrid[0:OH, 0:OW].astype(np.float32)
vig = (1 - 0.35*np.clip(((ox-OW/2)/(OW*0.75))**2 + ((oy-OH/2)/(OH*0.7))**2, 0, 1))[..., None]

def over(img, lay, a):
    if a <= 0: return img
    al = lay[..., 3:4]*a
    return img*(1-al) + lay[..., :3]*al

def ease(t): t = min(max(t, 0), 1); return t*t*(3-2*t)

ff_cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
          '-i', sys.argv[3], '-c:v', 'libx264', '-crf', '18', '-preset', 'slow', '-pix_fmt', 'yuv420p',
          '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', OUT]
proc = subprocess.Popen(ff_cmd, stdin=subprocess.PIPE)

for i in range(N):
    t = i / FPS
    cv = base.copy()
    # lago ondulando
    if not HAS_WATER: dx = 0*rows
    else: dx = 2.2*np.sin(rows*0.11 - t*2.2) * band
    for yrow in np.nonzero(band > 0.01)[0]:
        s = int(round(dx[yrow]))
        if s: cv[yrow] = np.roll(cv[yrow], s, axis=0)
    cv += (0.05 + 0.04*np.sin(rows*0.05 - t*1.5))[:, None, None] * reflect[..., None] * np.array([0.8, 0.8, 1.0], np.float32)
    # lua
    cv += moon_glow * (0.10 + 0.04*math.sin(t*1.3)) * np.array([1.0, 0.9, 0.65], np.float32)
    # janelas
    flick = 0.12 + 0.05*math.sin(t*7.3) + 0.03*math.sin(t*13.1+1) + 0.02*math.sin(t*3.1)
    if HAS_WIN: cv += win_glow * flick * np.array([1.0, 0.7, 0.3], np.float32)
    # estrelas
    for k, (x, y, _) in enumerate(stars):
        v = max(0.0, math.sin(t*2*math.pi*star_f[k] + star_ph[k]))**3
        add(cv, FL_BIG if star_big[k] else FL_SM, x, y, (1.0, 0.95, 0.85), 0.75*v)
    # estrela cadente
    u = (t - ss_t0)/ss_d
    if 0 <= u <= 1.25:
        head = ss0 + (ss1-ss0)*min(u, 1)
        fade = 1 if u <= 1 else 1-(u-1)/0.25
        for j in range(40):
            q = j/40; p = head - (ss1-ss0)*q*0.35
            add(cv, SS, p[0], p[1], (1, 0.95, 0.85), (1-q)**1.5 * 0.9 * fade * min(1, u*6))
        add(cv, gauss(18, 5), head[0], head[1], (1, 0.9, 0.7), 0.5*fade)
    # fumaça
    for s0 in (smoke_spawn if HAS_SMOKE else []):
        age = t - s0
        if 0 < age < 6:
            q = age/6
            sx = chx + 34*q + 10*math.sin(age*1.4 + s0)
            sy = chy - 150*C*q*1.9
            r = int(6 + 30*q); a = 0.16*math.sin(math.pi*q)
            blend(cv, SMK[min(r-6, len(SMK)-1)], sx, sy, (0.78, 0.76, 0.88), a)
    # vaga-lumes
    for k in range(NF):
        x = ff['x'][k] + ff['ax'][k]*math.sin(t*2*math.pi*ff['fx'][k] + ff['ph'][k])
        y = ff['y'][k] + ff['ay'][k]*math.sin(t*2*math.pi*ff['fy'][k] + 2*ff['ph'][k]) - 6*t
        b = (0.5 + 0.5*math.sin(t*2*math.pi*ff['pf'][k] + ff['ph'][k]*3))**2
        add(cv, FF, x, y, (1.0, 0.82, 0.35), 0.55*b*ff['sz'][k])
        add(cv, FFc, x, y, (1.0, 0.95, 0.7), 0.9*b)
    # zoom lento (Ken Burns)
    z = 1.0 + 0.09*ease(t/DUR)
    ch_ = (CW/0.5625)/z if CW/0.5625 <= CH else CH/z
    cw_ = ch_*0.5625
    cx_, cy_ = CW/2, CH/2 - 30*ease(t/DUR)
    box = (cx_-cw_/2, cy_-ch_/2, cx_+cw_/2, cy_+ch_/2)
    img8 = Image.fromarray((np.clip(cv, 0, 1)*255).astype(np.uint8))
    fr = np.asarray(img8.resize((OW, OH), Image.BICUBIC, box=box)).astype(np.float32)/255
    fr *= vig
    # fade in geral
    fr *= ease(t/0.8)
    # título com revelação da esquerda p/ direita
    rev = TX0 - 120 + (TX1 - TX0 + 240) * ease((t-0.8)/2.0)
    m = np.clip((rev - ox[0])/120, 0, 1)[None, :, None]
    if t > 0.8:
        pulse = 0.85 + 0.15*math.sin(t*2.0)
        sh, _ = title_sh; gl, fg = title
        fr = fr*(1-sh[..., 3:4]*m) + sh[..., :3]*sh[..., 3:4]*m
        fr = fr + gl[..., :3]*gl[..., 3:4]*m*0.55*pulse
        fr = fr*(1-fg[..., 3:4]*m) + fg[..., :3]*fg[..., 3:4]*m
    for (sh, fg), t0 in ((L1, 3.0), (L2, 4.3)):
        a = ease((t-t0)/1.0)
        if a > 0:
            off = int(18*(1-a))
            sh_, fg_ = np.roll(sh, off, axis=0), np.roll(fg, off, axis=0)
            fr = over(fr, sh_, a); fr = over(fr, fg_, a)
    a = ease((t-6.2)/1.0)
    if a > 0:
        fr = over(fr, np.roll(PILL, int(24*(1-a)), axis=0), a)
        beat = 1 + 0.16*max(0, math.sin(t*2*math.pi*1.1))**8
        hs = int(90*SK*beat); hi = heart_img.resize((hs, hs), Image.LANCZOS)
        H = np.asarray(hi).astype(np.float32)/255
        y0 = int(HY - hs/2 + 24*(1-a)); x0 = int(HX - hs/2)
        reg = fr[y0:y0+hs, x0:x0+hs]
        al = H[..., 3:4]*a
        fr[y0:y0+hs, x0:x0+hs] = reg*(1-al) + H[..., :3]*al
    proc.stdin.write((np.clip(fr, 0, 1)*255).astype(np.uint8).tobytes())
    if i % 60 == 0: print('frame', i, flush=True)

proc.stdin.close(); proc.wait()
print('ok', len(stars), 'estrelas')
