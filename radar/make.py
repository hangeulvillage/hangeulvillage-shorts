"""지원금 레이더 shorts: card JSON -> video.mp4, thumb.jpg, copy.txt, qa.png, manifest.json.

Usage: python3 radar/make.py CARD.json OUT_DIR [--hook target|deadline|check] [--voice M2|F1]
"""
import argparse, concurrent.futures as cf, datetime as dt, glob, hashlib, json, math, os, re, subprocess, sys
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, SR = 1080, 1920, 30, 44100
OFF = 110  # content layer vertical offset (keeps text out of the Shorts UI)

# ---------------- fonts ----------------
def _font_paths():
    sysdir = '/usr/share/fonts/opentype/noto/'
    if os.path.exists(sysdir + 'NotoSansCJK-Black.ttc'):
        return {'B': (sysdir + 'NotoSansCJK-Black.ttc', 1), 'D': (sysdir + 'NotoSansCJK-Bold.ttc', 1),
                'R': (sysdir + 'NotoSansCJK-Regular.ttc', 1)}
    d = os.path.join(HERE, 'fonts/')
    return {'B': (d + 'NotoSansCJKkr-Black.otf', 0), 'D': (d + 'NotoSansCJKkr-Bold.otf', 0),
            'R': (d + 'NotoSansCJKkr-Regular.otf', 0)}
FP = _font_paths()
_fc = {}
def F(w, size):
    size = max(8, int(size)); k = (w, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(FP[w][0], size, index=FP[w][1])
    return _fc[k]

YEL = (255, 212, 59); WHITE = (255, 255, 255); RED = (255, 77, 77); GREEN = (46, 204, 113)
GRAY = (150, 162, 185); CARD = (27, 41, 68); NAVY = (11, 18, 32); LINE = (60, 84, 128)
# Visual styles (--style): palette + background pattern, so videos do not all look the same.
STYLES = {
    'navy':   {'bg_top': (10, 17, 31), 'bg_bot': (22, 36, 64), 'pat': (34, 50, 82), 'glow': (40, 60, 110), 'pattern': 'dots',
               'YEL': (255, 212, 59), 'CARD': (27, 41, 68), 'NAVY': (11, 18, 32), 'LINE': (60, 84, 128)},
    'ember':  {'bg_top': (30, 9, 14), 'bg_bot': (62, 18, 26), 'pat': (84, 32, 40), 'glow': (120, 44, 44), 'pattern': 'stripes',
               'YEL': (255, 190, 80), 'CARD': (66, 24, 32), 'NAVY': (28, 8, 12), 'LINE': (130, 62, 72)},
    'forest': {'bg_top': (5, 26, 22), 'bg_bot': (12, 50, 42), 'pat': (22, 70, 60), 'glow': (30, 100, 84), 'pattern': 'grid',
               'YEL': (120, 240, 200), 'CARD': (16, 58, 50), 'NAVY': (4, 22, 18), 'LINE': (50, 110, 96)},
}
STYLE = dict(STYLES['navy'])
def set_style(name):
    st = STYLES.get(name or 'navy', STYLES['navy']); STYLE.clear(); STYLE.update(st)
    globals().update({k: st[k] for k in ('YEL', 'CARD', 'NAVY', 'LINE')})
ISSUES = []
REVIEW = []  # soft notes for the proofreader (do not fail QA)

_meas = ImageDraw.Draw(Image.new('RGB', (10, 10)))
def fit(txt, w, size, maxw, minsize=None, where=''):
    """Largest font size <= size whose text width fits maxw."""
    minsize = minsize or int(size * 0.6)
    s = size
    while s > minsize and _meas.textlength(txt, font=F(w, s)) > maxw: s -= 2
    if _meas.textlength(txt, font=F(w, s)) > maxw:
        ISSUES.append(f'text too long ({where}): {txt}')
    return s

# ---------------- easing ----------------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x, s=1.70158):
    x = clamp(x); x -= 1; return x * x * ((s + 1) * x + s) + 1

def text(base, xy, txt, w, size, fill, scale=1.0, alpha=1.0, anchor='mm', stroke=0):
    if alpha <= 0.01 or scale <= 0.02: return
    layer = Image.new('RGBA', base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.text(xy, txt, font=F(w, size * scale), fill=fill + (int(255 * alpha),), anchor=anchor,
           stroke_width=stroke, stroke_fill=NAVY + (int(255 * alpha),))
    base.alpha_composite(layer)

def rrect(base, box, r, fill, outline=None, width=0, alpha=1.0):
    layer = Image.new('RGBA', base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, int(r), fill=fill + (int(255 * alpha),),
                        outline=(outline + (int(255 * alpha),)) if outline else None, width=width)
    base.alpha_composite(layer)

# ---------------- dates ----------------
WD = '월화수목금토일'
def ddate(card):
    if not card.get('deadline'): return None
    return dt.date.fromisoformat(card['deadline'])
def dday(card):
    d = ddate(card)
    if not d: return None
    return (d - dt.date.fromisoformat(card['publish_date'])).days

# ---------------- voice ----------------
SINO = '영일이삼사오육칠팔구'
def num2kor(n):
    if n == 0: return '영'
    out = ''
    for unit, name in ((10 ** 8, '억'), (10 ** 4, '만'), (1, '')):
        q = n // unit; n %= unit
        if not q: continue
        s = ''
        for u, un in ((1000, '천'), (100, '백'), (10, '십'), (1, '')):
            dgt = q // u; q %= u
            if dgt: s += ('' if dgt == 1 and un else SINO[dgt]) + un
        out += s + name
    return out
def hangulize(t):
    t = re.sub(r'\d+', lambda m: num2kor(int(m.group())), t)
    return re.sub(r'[^가-힣]', '', t)
def lcs_ratio(a, b):
    if not a: return 1.0
    m = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a)):
        for j in range(len(b)):
            m[i + 1][j + 1] = m[i][j] + 1 if a[i] == b[j] else max(m[i][j + 1], m[i + 1][j])
    return m[-1][-1] / len(a)

VOICE_STEPS, VOICE_SPEED = 32, 1.02  # 2026-11-06: higher quality, a bit slower = less robotic
def make_voice(card, voice, work):
    import sherpa_onnx
    from supertonic import TTS
    asr_dir = os.path.join(HERE, 'asr/sherpa-onnx-zipformer-korean-2024-06-24/')
    rec = sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=asr_dir + 'encoder-epoch-99-avg-1.int8.onnx', decoder=asr_dir + 'decoder-epoch-99-avg-1.onnx',
        joiner=asr_dir + 'joiner-epoch-99-avg-1.int8.onnx', tokens=asr_dir + 'tokens.txt', num_threads=4)
    def hear(y):
        s = rec.create_stream(); s.accept_waveform(SR, y.astype(np.float32)); rec.decode_stream(s); return s.result.text.strip()
    tts = TTS(model='supertonic-3'); st = tts.get_voice_style(voice)
    warm = 'lowshelf=f=160:g=1.0,highshelf=f=6000:g=-1.5'
    report = []
    for scene in ('hook', 'check', 'steps', 'deadline', 'cta'):
        for k, b in enumerate(card['beats'].get(scene, [])):
            target = hangulize(b['say']); best = None
            for attempt in range(12 if b.get('expect') else 6):
                w, _ = tts.synthesize(b['say'], voice_style=st, lang='ko', speed=b.get('speed', VOICE_SPEED), total_steps=VOICE_STEPS)
                y = np.asarray(w, dtype=np.float32).squeeze()
                idx = np.where(np.abs(y) > 0.01)[0]; y = y[max(0, idx[0] - 600): idx[-1] + 2500]
                sf.write(f'{work}/_in.wav', y, SR)
                subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{work}/_in.wav', '-af', warm, '-ar', str(SR),
                                f'{work}/_out.wav'], check=True)
                y, _ = sf.read(f'{work}/_out.wav'); y = y.astype(np.float32)
                heard = hear(y); sim = lcs_ratio(target, hangulize(heard))
                exp_ok = all(e in heard.replace(' ', '') for e in b.get('expect', []))
                score = sim + (0.3 if exp_ok else 0)
                if best is None or score > best[0]: best = (score, y, heard, sim, exp_ok)
                if sim >= 0.85 and exp_ok: break
            _, y, heard, sim, exp_ok = best
            y = y / max(1e-6, np.abs(y).max()) * 0.85
            path = f'{work}/{scene}{k}.wav'; sf.write(path, y, SR)
            b['wav'] = path; b['dur'] = round(len(y) / SR, 3)
            report.append({'beat': f'{scene}{k}', 'say': b['say'], 'heard': heard, 'sim': round(sim, 2), 'expect_ok': exp_ok})
            if sim < 0.75 or not exp_ok:
                ISSUES.append(f'voice check weak {scene}{k}: said "{b["say"]}" heard "{heard}"')
    return report

# ---------------- timeline ----------------
def build_timeline(card):
    tl = []; cur = 0.0
    tails = {'hook': 0.35, 'check': 0.35, 'steps': 0.4, 'deadline': 0.9, 'cta': 1.2}
    for scene in ('hook', 'check', 'steps', 'deadline', 'cta'):
        beats = card['beats'].get(scene, [])
        if not beats: continue
        start = cur; t = start + (0.05 if scene == 'hook' else 0.12)
        for b in beats:
            b['t'] = round(t, 3); t += b['dur'] + 0.12
        end = t - 0.12 + tails[scene]
        tl.append({'name': scene, 'start': start, 'end': end, 'beats': beats})
        cur = end
    return tl

# ---------------- background ----------------
def make_bg(card, chrome=True):
    y = np.linspace(0, 1, H)[:, None]
    top = np.array(STYLE['bg_top']); bot = np.array(STYLE['bg_bot'])
    arr = (top + (bot - top) * y[..., None]).repeat(W, axis=1).astype(np.uint8)
    im = Image.fromarray(arr, 'RGB'); d = ImageDraw.Draw(im)
    if STYLE['pattern'] == 'stripes':
        for k in range(-H, W, 56): d.line([(k, 0), (k + H, H)], fill=STYLE['pat'], width=3)
    elif STYLE['pattern'] == 'grid':
        for gx in range(0, W, 90): d.line([(gx, 0), (gx, H)], fill=STYLE['pat'], width=1)
        for gy in range(0, H, 90): d.line([(0, gy), (W, gy)], fill=STYLE['pat'], width=1)
    else:
        for gy in range(0, H, 60):
            for gx in range(30, W, 60): d.ellipse([gx - 2, gy - 2, gx + 2, gy + 2], fill=STYLE['pat'])
    glow = Image.new('RGB', (W, H), (0, 0, 0)); ImageDraw.Draw(glow).ellipse([140, 300, 940, 1100], fill=STYLE['glow'])
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    im = Image.fromarray(np.clip(np.asarray(im).astype(int) + np.asarray(glow).astype(int) // 2, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    if not chrome: return im
    pill = card.get('pill', card['program'])
    s = fit(pill, 'D', 40, 860, 28, 'pill'); tw = d.textlength(pill, font=F('D', s))
    d.rounded_rectangle([W / 2 - tw / 2 - 34, 230, W / 2 + tw / 2 + 34, 302], 36, fill=YEL)
    d.text((W / 2, 266), pill, font=F('D', s), fill=NAVY, anchor='mm')
    src = '출처: ' + card['source']
    d.text((W / 2, 1462), src, font=F('R', fit(src, 'R', 30, 900, 22, 'source')), fill=GRAY, anchor='mm')
    return im

# ---------------- scenes ----------------
def deadline_label(card):
    d = ddate(card)
    return f'{d.month}월 {d.day}일 마감' if d else '상시 신청'

def scene_hook(im, sc, t, T, card, hook):
    b = sc['beats']; pulse_t = b[1]['t'] - sc['start'] if len(b) > 1 else 99
    amount = card['amount']
    pulse = 0.82 + 0.18 * back(t / 0.3)
    if t >= pulse_t - 0.1: pulse = 1 + 0.14 * math.exp(-(t - pulse_t + 0.1) * 7) * math.cos((t - pulse_t + 0.1) * 14)
    glowp = clamp((t - pulse_t + 0.1) / 0.15) * math.exp(-max(0, t - pulse_t) * 1.2)
    if hook == 'deadline' and dday(card) is not None and dday(card) >= 0:
        top_txt, top_col, top_size = f'D-{dday(card)}', RED, 190
        sub = '마감 전에 신청하세요'
        chip = f'{card["audience"]} {card.get("audience_noun", "")}'.strip()
    else:
        top_txt, top_col, top_size = card['audience'], YEL, 150
        sub = card['audience_sub']; chip = None
    if hook == 'check':
        text(im, (W / 2, 250), '3초 체크', 'B', 56, WHITE, alpha=1.0)
    s = fit(top_txt, 'B', top_size, 920, 90, 'hook top')
    text(im, (W / 2, 360), top_txt, 'B', s, top_col, scale=0.85 + 0.15 * back(t / 0.25), stroke=6)
    text(im, (W / 2, 520), sub, 'B', fit(sub, 'B', 96, 940, 60, 'hook sub'), WHITE)
    if glowp > 0.01:
        g = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([140, 620, 940, 900], fill=(255, 212, 59, int(110 * glowp)))
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(60)))
    text(im, (W / 2, 760), amount, 'B', fit(amount, 'B', 178, 980, 100, 'amount'), WHITE, scale=pulse, stroke=4)
    if chip:
        tag, col = chip, CARD
    else:
        tag, col = deadline_label(card), RED
    p = 0.85 + 0.15 * back(t / 0.3)
    ts = fit(tag, 'B', 60, 860, 40, 'hook tag'); tw = _meas.textlength(tag, font=F('B', ts))
    rrect(im, [W / 2 - (tw / 2 + 40) * p, 980 - 52 * p, W / 2 + (tw / 2 + 40) * p, 980 + 52 * p], 30 * p, col)
    text(im, (W / 2, 978), tag, 'B', ts, WHITE, scale=p)
    note = card.get('pay_note', '')
    if note: text(im, (W / 2, 1100), note, 'D', fit(note, 'D', 40, 940, 30, 'pay_note'), GRAY)

def check_icon(d, cx, cy, r, color, p, cross=False):
    if p <= 0: return
    rr = r * back(p); d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=color)
    if p <= 0.4: return
    q = clamp((p - 0.4) / 0.6); w = max(4, int(r * 0.22))
    if cross:
        k = r * 0.38 * q
        d.line([cx - k, cy - k, cx + k, cy + k], fill=WHITE, width=w); d.line([cx - k, cy + k, cx + k, cy - k], fill=WHITE, width=w)
        return
    pts = [(cx - r * 0.42, cy + r * 0.02), (cx - r * 0.12, cy + r * 0.32), (cx + r * 0.45, cy - r * 0.3)]
    if q < 0.5:
        a = q / 0.5; pts = [pts[0], (pts[0][0] + (pts[1][0] - pts[0][0]) * a, pts[0][1] + (pts[1][1] - pts[0][1]) * a)]
    else:
        a = (q - 0.5) / 0.5; pts = [pts[0], pts[1], (pts[1][0] + (pts[2][0] - pts[1][0]) * a, pts[1][1] + (pts[2][1] - pts[1][1]) * a)]
    d.line(pts, fill=WHITE, width=w, joint='curve')

def scene_check(im, sc, t, T, card, hook):
    title = card.get('check_title', '나도 받을 수 있을까?')
    text(im, (W / 2, 330), title, 'B', fit(title, 'B', 84, 960, 56, 'check title'), WHITE, scale=0.9 + 0.1 * ease_out(t / 0.2))
    items = sc['beats']; n = len(items)
    gap = min(175, 690 / max(n, 1))
    for i, it in enumerate(items):
        lt = T - it['t']
        if lt < 0: continue
        p = ease_out(lt / 0.28); bad = it.get('bad', False); sub = it.get('sub')
        h = min(150 if sub else 120, gap - 18); y = 450 + i * gap; x = 90 + (1 - p) * 700
        rrect(im, [x, y, x + 900, y + h], 28, (70, 30, 40) if bad else CARD, RED if bad else LINE, 3, alpha=p)
        d = ImageDraw.Draw(im)
        check_icon(d, x + 75, y + h / 2, 38, RED if bad else GREEN, clamp((lt - 0.12) / 0.3), cross=bad)
        ms = fit(it['main'], 'B', 50, 730, 34, 'check main')
        if sub:
            d.text((x + 140, y + h * 0.36), it['main'], font=F('B', ms), fill=WHITE, anchor='lm')
            d.text((x + 140, y + h * 0.74), sub, font=F('D', fit(sub, 'D', 34, 730, 24, 'check sub')),
                   fill=(255, 170, 170) if bad else GRAY, anchor='lm')
        else:
            d.text((x + 140, y + h / 2), it['main'], font=F('B', ms), fill=WHITE, anchor='lm')

def scene_steps(im, sc, t, T, card, hook):
    text(im, (W / 2, 330), card.get('steps_title', '신청 방법'), 'B', 84, WHITE, scale=0.9 + 0.1 * ease_out(t / 0.2))
    steps = sc['beats']; n = len(steps); gap = min(240, 720 / max(n, 1)); h = min(170, gap - 50)
    for i, st in enumerate(steps):
        lt = T - st['t']
        if lt < 0: continue
        p = ease_out(lt / 0.3); y = 450 + i * gap + (1 - p) * 60; hi = i == n - 1
        rrect(im, [90, y, 990, y + h], 30, (60, 52, 18) if hi else CARD, YEL if hi else LINE, 3, alpha=p)
        d = ImageDraw.Draw(im)
        r = 46 * back(clamp((lt - 0.05) / 0.3))
        if r > 1:
            d.ellipse([170 - r, y + h / 2 - r, 170 + r, y + h / 2 + r], fill=YEL)
            d.text((170, y + h / 2 - 2), str(i + 1), font=F('B', 56 * r / 46), fill=NAVY, anchor='mm')
        if p > 0.05:
            d.text((250, y + h * 0.35), st['main'], font=F('B', fit(st['main'], 'B', 50, 700, 34, 'step main')), fill=WHITE, anchor='lm')
            if st.get('sub'):
                d.text((250, y + h * 0.72), st['sub'], font=F('D', fit(st['sub'], 'D', 36, 700, 24, 'step sub')),
                       fill=YEL if hi else GRAY, anchor='lm')
        if i < n - 1 and T > steps[i + 1]['t'] - 0.1:
            ay = 450 + i * gap + h + 8
            d.polygon([(W / 2 - 22, ay), (W / 2 + 22, ay), (W / 2, ay + 26)], fill=(90, 110, 150))

def scene_deadline(im, sc, t, T, card, hook):
    d0 = ddate(card); p = back(t / 0.35); cx, top = W / 2, 330
    cw = ch = 560 * p
    rrect(im, [cx - cw / 2, top + 10, cx + cw / 2, top + 10 + ch], 40, (0, 0, 0), alpha=0.35)
    rrect(im, [cx - cw / 2, top, cx + cw / 2, top + ch], 40, WHITE)
    rrect(im, [cx - cw / 2, top, cx + cw / 2, top + 150 * p], 40, RED)
    rrect(im, [cx - cw / 2, top + 100 * p, cx + cw / 2, top + 150 * p], 0, RED)
    if p > 0.6:
        if d0:
            text(im, (cx, top + 78), f'{d0.year}년 {d0.month}월', 'B', 64, WHITE, scale=p)
            text(im, (cx - 40, top + 345), str(d0.day), 'B', 300 if d0.day < 10 else 240, NAVY, scale=p)
            text(im, (cx + (120 if d0.day < 10 else 190), top + 400), f'({WD[d0.weekday()]})', 'B', 64, NAVY, scale=p)
        else:
            text(im, (cx, top + 78), '신청 기간', 'B', 64, WHITE, scale=p)
            text(im, (cx, top + 345), '상시', 'B', 200, NAVY, scale=p)
    q = ease_out((t - 0.4) / 0.3)
    big = f'{card["deadline_time"]} 마감' if d0 and card.get('deadline_time') else deadline_label(card)
    text(im, (W / 2, 1010), big, 'B', fit(big, 'B', 104, 960, 60, 'deadline big'), YEL, alpha=q, scale=0.9 + 0.1 * q, stroke=4)
    n = dday(card); stamp_t = sc['beats'][-1]['t'] + sc['beats'][-1]['dur'] - 0.15
    st = T - stamp_t
    if n is not None and 0 <= n <= 60 and st > 0:
        s = 1 + 1.4 * (1 - ease_out(st / 0.18)); a = clamp(st / 0.1)
        stamp = Image.new('RGBA', (520, 260), (0, 0, 0, 0)); sd = ImageDraw.Draw(stamp)
        sd.rounded_rectangle([10, 10, 510, 250], 30, outline=RED + (int(235 * a),), width=14)
        sd.text((260, 128), f'D-{n}' if n else 'D-DAY', font=F('B', 150 if n < 100 else 120), fill=RED + (int(235 * a),), anchor='mm')
        stamp = stamp.rotate(-12, expand=True, resample=Image.BICUBIC)
        stamp = stamp.resize((int(stamp.width * s * 0.62), int(stamp.height * s * 0.62)), Image.BICUBIC)
        im.alpha_composite(stamp, (int(W / 2 + 270 - stamp.width / 2), int(860 - stamp.height / 2)))

def scene_cta(im, sc, t, T, card, hook):
    text(im, (W / 2, 330), '댓글로 남겨 주세요', 'B', 84, WHITE, scale=0.9 + 0.1 * ease_out(t / 0.2))
    p = back((t - 0.1) / 0.35)
    if p > 0:
        bw, bh = 820 * p, 300 * p; cx, cy = W / 2, 640
        layer = Image.new('RGBA', im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
        ld.rounded_rectangle([cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2], int(50 * p), fill=WHITE + (255,))
        ld.polygon([(cx + 200 * p, cy + bh / 2 - 2), (cx + 320 * p, cy + bh / 2 - 2), (cx + 330 * p, cy + bh / 2 + 70 * p)], fill=WHITE + (255,))
        im.alpha_composite(layer)
        if p > 0.7:
            text(im, (cx, cy - 50), '나이 + 사는 지역', 'B', 80, NAVY, scale=p)
            ex = card.get('cta_example', '예) 26살 · 인천 부평구'); n = int(len(ex) * clamp((t - 0.6) / 1.0))
            d = ImageDraw.Draw(im); d.text((cx - d.textlength(ex, font=F('D', 50)) / 2, cy + 60), ex[:n], font=F('D', 50), fill=(90, 100, 120), anchor='lm')
    if len(sc['beats']) > 1:
        q = ease_out((T - sc['beats'][1]['t']) / 0.3)
        if q > 0:
            text(im, (W / 2, 950), '받을 수 있는 지원금', 'B', 76, YEL, alpha=q, scale=0.9 + 0.1 * q)
            text(im, (W / 2, 1050), '찾아서 답글로 알려드려요', 'B', 62, WHITE, alpha=q)
    if t > 1.0:
        bb = math.sin((t - 1.0) * 6) * 12; x, y = 960, 1130 + bb
        ImageDraw.Draw(im).polygon([(x - 34, y - 40), (x + 34, y - 40), (x, y + 10)], fill=YEL)

RENDER = {'hook': scene_hook, 'check': scene_check, 'steps': scene_steps, 'deadline': scene_deadline, 'cta': scene_cta}

def caption(im, T, tl):
    for sc in tl:
        for i, b in enumerate(sc['beats']):
            nxt = sc['beats'][i + 1]['t'] if i + 1 < len(sc['beats']) else sc['end']
            if b['t'] - (0.05 if b['t'] < 0.1 else 0) <= T < nxt - 0.05 and b.get('cap'):
                p = 1.0 if b['t'] < 0.1 else ease_out((T - b['t']) / 0.12)
                s = fit(b['cap'], 'B', 54, 940, 38, 'caption'); tw = _meas.textlength(b['cap'], font=F('B', s)); y = 1240 + (1 - p) * 14
                rrect(im, [W / 2 - tw / 2 - 30, y - 50, W / 2 + tw / 2 + 30, y + 46], 20, (0, 0, 0), alpha=0.67 * p)
                text(im, (W / 2, y), b['cap'], 'B', s, WHITE, alpha=p)
                return

G = {}
def intro_frame(T):
    """Opening hold: the thumbnail itself (title hook + audience + amount + deadline) with a slow zoom-out."""
    th = G['thumb_im']; p = ease_out(T / max(0.1, G['intro_end']))
    s = 1.06 - 0.06 * p; w, h = int(W * s), int(H * s)
    big = th.resize((w, h), Image.LANCZOS)
    return big.crop(((w - W) // 2, (h - H) // 2, (w - W) // 2 + W, (h - H) // 2 + H))

def frame(T):
    card, tl, hook, bg = G['card'], G['tl'], G['hook'], G['bg']
    if G.get('intro_end', 0) > 0 and T < G['intro_end']: return intro_frame(T)
    for sc in tl:
        if sc['start'] <= T < sc['end'] + 1e-6:
            im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            RENDER[sc['name']](im, sc, T - sc['start'], T, card, hook)
            caption(im, T, tl)
            out = bg.convert('RGBA'); out.alpha_composite(im, (0, OFF))
            return out.convert('RGB')
    return bg.copy()

def render_scene(args):
    idx, work = args
    sc = G['tl'][idx]; start = int(round(sc['start'] * FPS)); n = int(round(sc['end'] * FPS)) - start
    tmp = f'{work}/scene{idx}.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for k in range(n): p.stdin.write(frame((start + k) / FPS).tobytes())
    p.stdin.close(); rc = p.wait()
    if rc == 0: os.replace(tmp, f'{work}/scene{idx}.mp4')
    return rc, n

# ---------------- audio ----------------
def make_audio(card, tl, work, dur):
    N = int(dur * SR); rng = np.random.default_rng(int(hashlib.md5(card['id'].encode()).hexdigest()[:6], 16))
    def place(buf, y, t, g=1.0):
        i = int(t * SR); j = min(N, i + len(y))
        if i < N: buf[i:j] += y[: j - i] * g
    voice = np.zeros(N, np.float32)
    for sc in tl:
        for b in sc['beats']:
            y, _ = sf.read(b['wav']); place(voice, y.astype(np.float32), b['t'])
    sf.write(f'{work}/voice.wav', voice, SR)
    progs = [[[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [261.63, 329.63, 392.0], [196.0, 246.94, 293.66]],
             [[261.63, 329.63, 392.0], [196.0, 246.94, 293.66], [220.0, 261.63, 329.63], [174.61, 220.0, 261.63]],
             [[174.61, 220.0, 261.63], [196.0, 246.94, 293.66], [220.0, 261.63, 329.63], [220.0, 277.18, 329.63]]]
    chords = progs[rng.integers(3)]; bpm = [96, 100, 104][rng.integers(3)]; beat = 60 / bpm
    music = np.zeros(N, np.float32)
    def note(f, d, a):
        t = np.arange(int(d * SR)) / SR; env = np.exp(-t * 5) * (1 - np.exp(-t * 300))
        return (a * env * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) + 0.1 * np.sin(6 * np.pi * f * t))).astype(np.float32)
    def kick():
        t = np.arange(int(0.25 * SR)) / SR; f = 50 + 90 * np.exp(-t * 30)
        return (0.6 * np.exp(-t * 14) * np.sin(2 * np.pi * np.cumsum(f) / SR)).astype(np.float32)
    def hat():
        t = np.arange(int(0.05 * SR)) / SR; n = np.diff(rng.standard_normal(len(t)), prepend=0)
        return (0.05 * np.exp(-t * 90) * n).astype(np.float32)
    b = 0; t = 0.0
    while t < dur:
        ch = chords[(b // 4) % 4]
        for s in range(2): place(music, note(ch[(b * 2 + s) % 3] * 2, beat * 0.9, 0.12), t + s * beat / 2)
        if b % 4 == 0: place(music, note(ch[0] / 2, beat * 3.5, 0.18), t)
        place(music, kick(), t, 0.7 if b % 2 == 0 else 0.35); place(music, hat(), t + beat / 2)
        b += 1; t = b * beat
    sf.write(f'{work}/music.wav', music, SR)
    sfx = np.zeros(N, np.float32)
    def pop():
        t = np.arange(int(0.12 * SR)) / SR; f = 600 + 900 * np.exp(-t * 40)
        return (0.35 * np.exp(-t * 35) * np.sin(2 * np.pi * np.cumsum(f) / SR)).astype(np.float32)
    def stamp():
        t = np.arange(int(0.35 * SR)) / SR; f = 45 + 120 * np.exp(-t * 25)
        return (0.8 * (np.exp(-t * 12) * np.sin(2 * np.pi * np.cumsum(f) / SR) + np.exp(-t * 200) * rng.standard_normal(len(t)) * 0.4)).astype(np.float32)
    def whoosh():
        L = int(0.35 * SR); n = np.convolve(rng.standard_normal(L), np.ones(40) / 40, 'same')
        return (0.5 * np.sin(np.linspace(0, np.pi, L)) ** 2 * n).astype(np.float32)
    place(sfx, stamp(), 0.02, 0.5)
    if card.get('_intro_end'): place(sfx, whoosh(), max(0, card['_intro_end'] - 0.2), 0.8)
    for sc in tl:
        if sc['start'] > 0: place(sfx, whoosh(), max(0, sc['start'] - 0.2))
        if sc['name'] in ('check', 'steps'):
            for bt in sc['beats']: place(sfx, pop(), bt['t'])
        if sc['name'] == 'hook' and len(sc['beats']) > 1: place(sfx, stamp(), sc['beats'][1]['t'] - 0.12)
        if sc['name'] == 'deadline' and dday(card) is not None and 0 <= dday(card) <= 60:
            place(sfx, stamp(), sc['beats'][-1]['t'] + sc['beats'][-1]['dur'] - 0.17)
    sf.write(f'{work}/sfx.wav', sfx, SR)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{work}/voice.wav', '-i', f'{work}/music.wav', '-i', f'{work}/sfx.wav',
                    '-filter_complex',
                    f'[1]volume=0.35,afade=t=out:st={dur - 0.8:.2f}:d=0.8[m];[0]asplit[v1][v2];'
                    '[m][v1]sidechaincompress=threshold=0.015:ratio=10:attack=10:release=400[md];'
                    '[v2][md][2]amix=inputs=3:normalize=0:weights=1 1 0.8,alimiter=limit=0.95[a]',
                    '-map', '[a]', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', f'{work}/mix.m4a'], check=True)

# ---------------- thumbnail ----------------
def make_thumb(card, path):
    im = make_bg(card, chrome=False).convert('RGBA'); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 560], fill=YEL)
    aud = card['audience']; d.text((W / 2, 250), aud, font=F('B', fit(aud, 'B', 190, 980, 100, 'thumb audience')), fill=NAVY, anchor='mm')
    sub = card.get('thumb_sub') or card['audience_sub']
    d.text((W / 2, 440), sub, font=F('B', fit(sub, 'B', 110, 980, 64, 'thumb sub')), fill=NAVY, anchor='mm')
    amt = card.get('amount_short', card['amount'])
    g = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([90, 660, 990, 1120], fill=(255, 212, 59, 90))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(70))); d = ImageDraw.Draw(im)
    d.text((W / 2, 880), amt, font=F('B', fit(amt, 'B', 300, 1000, 150, 'thumb amount')), fill=WHITE, anchor='mm', stroke_width=8, stroke_fill=NAVY)
    tag = deadline_label(card) + (f'  D-{dday(card)}' if dday(card) is not None and 0 <= dday(card) <= 60 else '')
    s = fit(tag, 'B', 84, 900, 50, 'thumb tag'); tw = d.textlength(tag, font=F('B', s))
    d.rounded_rectangle([W / 2 - tw / 2 - 50, 1180, W / 2 + tw / 2 + 50, 1320], 40, fill=RED)
    d.text((W / 2, 1248), tag, font=F('B', s), fill=WHITE, anchor='mm')
    hl = card.get('hook_line') or '대상 · 금액 · 신청방법 30초 정리'
    hs = fit(hl, 'B', 76, 980, 48, 'thumb hook_line')
    d.text((W / 2, 1430), hl, font=F('B', hs), fill=YEL if card.get('hook_line') else WHITE, anchor='mm', stroke_width=4, stroke_fill=NAVY)
    im.convert('RGB').save(path, quality=92)

# ---------------- copy ----------------
def make_copy(card):
    d0 = ddate(card); dl = f'{d0.month}/{d0.day} 마감' if d0 else '상시 신청'
    title = card.get('title') or f'{card["audience"]} {card.get("audience_noun", "")} {card.get("amount_short", card["amount"])} 신청하세요 ({dl})'
    title = re.sub(r'\s+', ' ', title).strip()
    if len(title) > 60: ISSUES.append(f'title over 60 chars: {title}')
    for bad in ('누구나', '무조건', '100%', '전원 지급', '모두 받'):
        if bad in title: ISSUES.append(f'banned word in title: {bad}')
    if len(title) > 40: REVIEW.append(f'title {len(title)} chars: Shorts shows ~40, put the hook first')
    amt = card.get('amount_short', '')
    if amt and amt not in title[:22]: REVIEW.append('amount not in the first ~20 chars of the title')
    if not card.get('title_pattern'): REVIEW.append('title_pattern missing (loss|surprise|question|countdown|check)')
    tags = card.get('tags', [])
    hashtags = ' '.join('#' + t.replace(' ', '') for t in (tags[:4] + ['지원금', '정부지원금']))
    hashtags = ' '.join(dict.fromkeys(hashtags.split()))
    facts = '\n'.join(f'✔ {k}: {v}' for k, v in card['facts'].items())
    src = '\n'.join(card.get('source_urls', []))
    desc = (f'{card["program"]} 핵심만 30초로 정리했어요.\n\n{facts}\n\n'
            f'📌 출처: {card["source"]}\n{src}\n\n'
            '💬 댓글에 "나이 + 사는 지역"을 남기면 받을 수 있는 지원금을 찾아 답글로 알려드려요.\n\n'
            '※ 정보 제공용 영상입니다. 조건과 일정은 바뀔 수 있으니 신청 전 공고 원문을 꼭 확인하세요. 영상 속 목소리는 AI 음성입니다.\n\n'
            f'{hashtags} #shorts')
    pinned = f'📌 {card["program"]} 신청: {card["facts"].get("신청", "")}\n다른 지원금이 궁금하면 "나이 + 사는 지역" 댓글로 남겨 주세요 👇'
    ig = (f'{title}\n\n{facts}\n\n출처: {card["source"]}\n'
          '💬 "나이 + 사는 지역" 댓글 남기면 받을 수 있는 지원금 찾아드려요\n'
          '※ 신청 전 공고 원문 꼭 확인하세요\n\n' + hashtags)
    tt = f'{title} 💬 나이+지역 댓글 남기면 지원금 찾아드려요 {hashtags}'
    return {'title': title, 'yt_title': title, 'description': desc, 'tags': tags, 'pinned_comment': pinned,
            'instagram_caption': ig, 'tiktok_caption': tt}

# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('card'); ap.add_argument('out')
    ap.add_argument('--hook', default=None); ap.add_argument('--voice', default='M5'); ap.add_argument('--style', default=None, choices=list(STYLES))
    ap.add_argument('--intro', type=float, default=None, help='seconds the thumbnail is held at the start (0 = off; default card intro_s or 1.2)')
    a = ap.parse_args()
    card = json.load(open(a.card)); hook = a.hook or card.get('hook', 'target')
    style = a.style or card.get('style', 'navy'); set_style(style)
    if card.get('hook_beats', {}).get(hook): card['beats']['hook'] = card['hook_beats'][hook]
    out = a.out; work = os.path.join(out, 'work'); os.makedirs(work, exist_ok=True)
    for k in ('id', 'program', 'audience', 'audience_sub', 'amount', 'publish_date', 'beats', 'facts', 'source'):
        if k not in card: sys.exit(f'card missing {k}')
    vreport = make_voice(card, a.voice, work)
    tl = build_timeline(card); dur = tl[-1]['end']
    G.update(card=card, tl=tl, hook=hook, bg=make_bg(card))
    make_thumb(card, os.path.join(out, 'thumb.jpg'))
    # Opening hold: show the thumbnail while the first hook line is spoken (a.intro seconds, clamped to that line).
    b0 = tl[0]['beats'][0]; intro = a.intro if a.intro is not None else card.get('intro_s', 1.2)
    G['intro_end'] = round(min(max(0.0, intro), b0['t'] + b0['dur'] + 0.05, 2.0), 3) if intro else 0.0
    G['thumb_im'] = Image.open(os.path.join(out, 'thumb.jpg')).convert('RGB')
    with cf.ProcessPoolExecutor(min(5, len(tl))) as ex:
        res = list(ex.map(render_scene, [(i, work) for i in range(len(tl))]))
    if any(r[0] for r in res): sys.exit('render failed')
    with open(f'{work}/list.txt', 'w') as f:
        for i in range(len(tl)): f.write(f"file 'scene{i}.mp4'\n")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{work}/list.txt', '-c', 'copy', f'{work}/video.mp4'], check=True)
    vdur = sum(r[1] for r in res) / FPS
    G['card']['_intro_end'] = G.get('intro_end', 0)
    make_audio(card, tl, work, vdur)
    final = os.path.join(out, 'video.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{work}/video.mp4', '-i', f'{work}/mix.m4a', '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-bsf:v', 'h264_metadata=sample_aspect_ratio=1/1', '-c:a', 'copy', '-shortest', '-movflags', '+faststart', final], check=True)
    copy = make_copy(card)
    with open(os.path.join(out, 'copy.txt'), 'w') as f:
        f.write(f'[YouTube 제목]\n{copy["yt_title"]} #shorts\n\n[YouTube 설명]\n{copy["description"]}\n\n[태그]\n{", ".join(copy["tags"])}\n\n'
                f'[고정 댓글]\n{copy["pinned_comment"]}\n\n[Instagram]\n{copy["instagram_caption"]}\n\n[TikTok]\n{copy["tiktok_caption"]}\n')
    # QA stills: first frame, hook pulse, end of each scene, plus thumbnail
    times = [0.0, G.get('intro_end', 0) + 0.15] + [min(sc['end'] - 0.1, sc['beats'][-1]['t'] + sc['beats'][-1]['dur'] + 0.3) for sc in tl]
    shots = [frame(t) for t in times] + [Image.open(os.path.join(out, 'thumb.jpg'))]
    sheet = Image.new('RGB', (360 * 4, 640 * 2), (0, 0, 0))
    for i, s in enumerate(shots[:8]): sheet.paste(s.resize((360, 640)), ((i % 4) * 360, (i // 4) * 640))
    sheet.save(os.path.join(out, 'qa.png'))
    if not (18 <= vdur <= 45): ISSUES.append(f'duration {vdur:.1f}s outside 18-45s')
    manifest = {'id': card['id'], 'hook': hook, 'voice': a.voice, 'style': style, 'duration': round(vdur, 2), 'title': copy['yt_title'],
                'copy': copy, 'voice_check': vreport, 'qa': {'pass': not ISSUES, 'issues': ISSUES, 'review': REVIEW}, 'intro_s': G.get('intro_end', 0),
                'title_pattern': card.get('title_pattern'), 'title_candidates': card.get('title_candidates', []),
                'files': {'video': final, 'thumb': os.path.join(out, 'thumb.jpg'), 'qa_sheet': os.path.join(out, 'qa.png')}}
    json.dump(manifest, open(os.path.join(out, 'manifest.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps({'qa_pass': not ISSUES, 'issues': ISSUES, 'review': REVIEW, 'intro_s': G.get('intro_end', 0), 'duration': round(vdur, 2), 'title': copy['yt_title']}, ensure_ascii=False))

if __name__ == '__main__':
    main()
