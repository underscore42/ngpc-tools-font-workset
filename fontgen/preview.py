#!/usr/bin/env python3
"""Render the font at 1x and 4x, on light and dark, for all three styles."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import mkfont as F
from PIL import Image, ImageDraw

SAMPLES = ["ABCDEFGHIJKLM", "NOPQRSTUVWXYZ", "0123456789 +-",
           "STAGE 1  LIFE 3", "HI 005000", "PRESS START"]
SCHEMES = [
    ("on ice  (Pengu)",     (204,238,255), (34,85,204),  (255,255,255)),
    ("on sand (Pengu 2)",   (238,204,119), (34,34,51),   (255,238,187)),
    ("on black (arcade)",   (0,0,0),       (255,255,255),(80,80,120)),
]

def draw(img, d, style, text, ox, oy, bg, c1, c2, z):
    for i, ch in enumerate(text):
        if ch not in F.G: ch = ' '
        idx = F.cell(ch, style)
        for y in range(8):
            for x in range(8):
                v = idx[y][x]
                if v == 0: continue
                col = c1 if v == 1 else c2
                d.rectangle([ox+(i*8+x)*z, oy+y*z, ox+(i*8+x)*z+z-1, oy+y*z+z-1],
                            fill=col)

for style in ('plain','shadow','outline'):
    Z=3; W=8*16*Z+40; rowh=8*Z+6
    H=len(SCHEMES)*(len(SAMPLES)*rowh+34)+30
    img=Image.new('RGB',(W,H),(24,24,28)); d=ImageDraw.Draw(img)
    y=10
    for name,bg,c1,c2 in SCHEMES:
        d.text((10,y),'%s   -   %s' % (style, name), fill=(235,235,235)); y+=16
        d.rectangle([10,y,W-10,y+len(SAMPLES)*rowh+6], fill=bg)
        yy=y+4
        for s in SAMPLES:
            draw(img,d,style,s,16,yy,bg,c1,c2,Z); yy+=rowh
        y+= len(SAMPLES)*rowh+22
    img.save('/mnt/user-data/outputs/ngpcfont-%s.png' % style)

# 1x reality check: all three styles, all three backgrounds
Z=1
line="HI 005000  STAGE 1"
img=Image.new('RGB',(len(line)*8+20, 3*3*10+20),(24,24,28)); d=ImageDraw.Draw(img)
y=6
for style in ('plain','shadow','outline'):
    for name,bg,c1,c2 in SCHEMES:
        d.rectangle([6,y,6+len(line)*8+6,y+9],fill=bg)
        draw(img,d,style,line,10,y+1,bg,c1,c2,1)
        y+=10
img.resize((img.width*4,img.height*4),Image.NEAREST).save('/mnt/user-data/outputs/ngpcfont-1x.png')
print('previews rendered')
