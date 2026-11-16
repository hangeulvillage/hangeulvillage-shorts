"""Kmong/Soomgo listing images from the sample videos' frames: thumb (4:3) + detail (tall)."""
import os, sys, subprocess
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from make_promo import F, tw
OUT = sys.argv[1]; SRC = sys.argv[2:]  # sample OUT dirs (each has work/mid*.png)
os.makedirs(OUT, exist_ok=True)
ACC = (232, 100, 46); INK = (24, 24, 30); BG = (250, 246, 240)

def phone(img, w):
    h = int(w * 16 / 9); im = img.resize((w, h)); r = int(w * 0.09)
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w, h), r, fill=255)
    pad = 10; o = Image.new('RGBA', (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(o).rounded_rectangle((0, 0, w + pad * 2, h + pad * 2), r + pad, fill=(20, 20, 24, 255))
    o.paste(im, (pad, pad), m); return o

def shadowed(base, el, xy):
    s = Image.new('RGBA', base.size, (0, 0, 0, 0)); a = el.split()[-1]
    s.paste((0, 0, 0, 90), (xy[0] + 10, xy[1] + 20), a); s = s.filter(ImageFilter.GaussianBlur(18))
    base.alpha_composite(s); base.alpha_composite(el, xy)

frames = [[Image.open(os.path.join(d, 'work', f'mid{i}.png')).convert('RGB') for i in (0, 4, 5)] for d in SRC]

# ---- thumbnail 1304x978 (4:3) ----
W, H = 1304, 978
t = Image.new('RGBA', (W, H), BG + (255,)); d = ImageDraw.Draw(t)
d.text((80, 150), '사진만 주세요', font=F('B', 92), fill=INK)
d.text((80, 270), '가게 홍보 릴스·쇼츠', font=F('B', 64), fill=ACC)
d.text((80, 355), '영상 만들어 드려요', font=F('B', 64), fill=INK)
for i, txt in enumerate(['자막 + AI 성우 + 배경음악', '문구 정리까지 대신', '2일 안 납품']):
    y = 500 + i * 74
    d.ellipse((84, y + 10, 116, y + 42), fill=ACC); d.text((100, y + 26), '✓', font=F('B', 24), fill=(255, 255, 255), anchor='mm')
    d.text((136, y + 26), txt, font=F('D', 44), fill=INK, anchor='lm')
d.rounded_rectangle((80, 770, 470, 870), 50, fill=ACC)
d.text((275, 820), '29,000원부터', font=F('B', 50), fill=(255, 255, 255), anchor='mm')
ph = [phone(frames[k][0], 230) for k in range(min(3, len(frames)))]
xs = [730, 880, 1030]; ys = [190, 110, 230]
for p_, x, y in zip(ph, xs, ys): shadowed(t, p_, (x, y))
t.convert('RGB').save(os.path.join(OUT, 'kmong_thumb.jpg'), quality=92)

# ---- detail image 1304 x N ----
rows = []
def section(title, h):
    im = Image.new('RGBA', (W, h), (255, 255, 255, 255)); dd = ImageDraw.Draw(im)
    dd.text((W // 2, 90), title, font=F('B', 64), fill=INK, anchor='mm'); return im, dd
im, dd = section('이렇게 만들어져요', 960)
for k, (lab, fr) in enumerate(zip(['한 줄 소개', '혜택', '매장 정보'], frames[0])):
    p_ = phone(fr, 330); x = 70 + k * 400; shadowed(im, p_, (x, 200))
    dd.text((x + 175, 880), lab, font=F('D', 44), fill=ACC, anchor='mm')
rows.append(im)
im, dd = section('작업 순서', 760)
for k, (a, b) in enumerate([('1', '질문지 답변 + 사진 3~8장 보내기'), ('2', '문구 정리 → 영상 제작'), ('3', '미리보기 확인, 수정 요청'), ('4', '최종 MP4 받기')]):
    y = 200 + k * 130
    dd.ellipse((150, y, 240, y + 90), fill=ACC); dd.text((195, y + 45), a, font=F('B', 48), fill=(255, 255, 255), anchor='mm')
    dd.text((280, y + 45), b, font=F('D', 50), fill=INK, anchor='lm')
rows.append(im)
im, dd = section('패키지', 820)
for k, (nm, pr, de, ex) in enumerate([('STANDARD', '29,000원', '영상 1편 · 수정 1회 · 2일', '세로 영상 + 썸네일'), ('DELUXE', '59,000원', '영상 2편 · 수정 2회 · 2일', '+ 게시글 문구·해시태그'), ('PREMIUM', '99,000원', '영상 4편 · 수정 2회 · 3일', '+ 문구 + 정사각 피드 버전')]):
    y = 190 + k * 200
    dd.rounded_rectangle((120, y, W - 120, y + 160), 30, fill=BG, outline=(235, 220, 205), width=3)
    dd.text((180, y + 80), nm, font=F('B', 48), fill=ACC, anchor='lm')
    dd.text((500, y + 80), pr, font=F('B', 52), fill=INK, anchor='lm')
    dd.text((W - 170, y + 55), de, font=F('R', 34), fill=(90, 90, 100), anchor='rm')
    dd.text((W - 170, y + 110), ex, font=F('B', 34), fill=ACC, anchor='rm')
rows.append(im)
im, dd = section('', 240)
dd.text((W // 2, 90), '샘플은 가상 매장이에요. 내레이션은 AI 성우입니다.', font=F('R', 36), fill=(110, 110, 120), anchor='mm')
dd.text((W // 2, 150), '주신 사진과 정보만 사용하고, 없는 가격·혜택은 넣지 않아요.', font=F('R', 36), fill=(110, 110, 120), anchor='mm')
rows.append(im)
tot = sum(r.height for r in rows); det = Image.new('RGB', (W, tot), (255, 255, 255)); y = 0
for r in rows: det.paste(r.convert('RGB'), (0, y)); y += r.height
det.save(os.path.join(OUT, 'kmong_detail.jpg'), quality=90)
print('ok', det.size)
