"""Vexor.uz brend uslubidagi vertikal (1080x1920) animatsion video.
Foydalanish: python3 tools/make_video.py scenes.json out.mp4
scenes.json: [{"title":"...", "accent":"...", "body":"..."}, ...]  (3-6 sahna)
Har sahna ~3.5 soniya, matn silliq paydo bo'ladi. Oxirgi kadr: CTA."""
import json, sys, subprocess, os, tempfile
from PIL import Image, ImageDraw, ImageFont
W,H,FPS,SCENE=1080,1920,30,3.5
F="/usr/share/fonts/opentype/inter/"
b=lambda s:ImageFont.truetype(F+"Inter-Bold.otf",s)
r=lambda s:ImageFont.truetype(F+"Inter-Regular.otf",s)
GOLD=(217,168,108); WHITE=(242,239,233); MUTE=(154,167,189); NAVY=(11,23,48)
def bg():
    img=Image.new("RGB",(W,H),NAVY); d=ImageDraw.Draw(img)
    for y in range(H):
        t=y/H; d.line([(0,y),(W,y)],fill=(int(11+10*t),int(23+12*t),int(48+18*t)))
    d.rounded_rectangle([60,60,W-60,H-60],radius=40,outline=(42,58,92),width=2,fill=(16,31,61))
    d.text((110,130),"VEXOR.UZ",font=b(36),fill=GOLD)
    return img
BG=bg()
def mix(c,a): return tuple(int(16+(x-16)*a) if i==0 else int([31,61][i-1]+(x-[31,61][i-1])*a) for i,x in enumerate(c))
def lines(d,text,font,maxw):
    out=[];line=""
    for w in text.split():
        t=(line+" "+w).strip()
        if d.textlength(t,font=font)>maxw and line: out.append(line); line=w
        else: line=t
    if line: out.append(line)
    return out
def ease(x): x=max(0,min(1,x)); return 1-(1-x)**3
def frame(scene,t,idx,total):
    img=BG.copy(); d=ImageDraw.Draw(img)
    d.text((W-110,130),f"{idx}/{total}",font=r(34),fill=MUTE,anchor="ra")
    y=520
    for k,(txt,font,col,lh) in enumerate([(scene.get("title",""),b(96),WHITE,110),(scene.get("accent",""),b(96),GOLD,110)]):
        a=ease((t-0.15*k)/0.6); dy=int(40*(1-a))
        for ln in lines(d,txt,font,W-220):
            d.text((110,y+dy),ln,font=font,fill=mix(col,a)); y+=lh
    a=ease((t-0.5)/0.6)
    d.line([(110,y+40),(110+int(260*a),y+40)],fill=GOLD,width=8); y+=100
    a=ease((t-0.7)/0.7); dy=int(30*(1-a))
    for ln in lines(d,scene.get("body",""),r(54),W-220):
        d.text((110,y+dy),ln,font=r(54),fill=mix(WHITE,a)); y+=76
    # progress bar
    p=(idx-1+t/SCENE)/total
    d.rounded_rectangle([110,H-200,W-110,H-188],radius=6,fill=(42,58,92))
    d.rounded_rectangle([110,H-200,110+int((W-220)*p),H-188],radius=6,fill=GOLD)
    d.text((110,H-160),"@ergashev_395  ·  Bepul konsultatsiya",font=r(36),fill=MUTE)
    return img
def main(src,out):
    scenes=json.load(open(src)); n=len(scenes)
    tmp=tempfile.mkdtemp(); i=0
    for s_i,s in enumerate(scenes,1):
        for f in range(int(SCENE*FPS)):
            frame(s,f/FPS,s_i,n).save(f"{tmp}/{i:05d}.png"); i+=1
    subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",f"{tmp}/%05d.png",
        "-c:v","libx264","-preset","veryfast","-crf","23","-pix_fmt","yuv420p","-movflags","+faststart",out],check=True)
    print(out, os.path.getsize(out)//1024,"KB")
if __name__=="__main__": main(sys.argv[1],sys.argv[2])
