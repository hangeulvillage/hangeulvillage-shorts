"""Photos -> short vertical promo video for a small business (the Kmong/Soomgo service).

Usage: python3 promo/make_promo.py BRIEF.json OUT_DIR
BRIEF.json (see promo/briefs/*.json):
  {"name": "모락 커피", "category": "카페", "tagline": "골목 끝, 매일 볶는 커피",
   "points": ["매일 아침 직접 로스팅", "핸드드립 4,500원부터", "조용한 2층 작업석"],
   "offer": "평일 오후 2~5시 아메리카노 1+1",
   "info": {"주소": "...", "영업": "매일 09:00~21:00", "문의": "010-0000-0000"},
   "cta": "지도에서 '모락 커피'를 검색하세요",
   "photos": ["photo1.jpg", ...],         # relative to the brief file; 1+ photos, reused if fewer than scenes
   "say": {"tagline": "...", "points": ["..."], "offer": "...", "cta": "..."},  # optional spoken versions (Hangul numbers)
   "voice": "F1"|"M5"|"none" (captions + music only), "accent": "#E8743B", "music": "marimba"|"lofi"|"bright", "sample": false}
Output: video.mp4 (1080x1920, 30 fps, -14 LUFS), thumb.jpg, qa.png, manifest.json {qa: {pass, issues}}.
The video says nothing that is not in the brief. Spoken text uses Hangul numbers (digits are converted automatically).
"""
import argparse, concurrent.futures as cf, json, os, re, subprocess, sys
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'radar'))
sys.path.insert(0, os.path.join(ROOT, 'pipeline', 'shorts'))
W, H, FPS, SR = 1080, 1920, 30, 44100
ISSUES, REVIEW = [], []

# ---------- fonts ----------
def _fp():
    s = '/usr/share/fonts/opentype/noto/'
    if os.path.exists(s + 'NotoSansCJK-Black.ttc'):
        return {'B': (s + 'NotoSansCJK-Black.ttc', 1), 'D': (s + 'NotoSansCJK-Bold.ttc', 1), 'R': (s + 'NotoSansCJK-Regular.ttc', 1)}
    d = os.path.join(ROOT, 'radar', 'fonts/')
    return {'B': (d + 'NotoSansCJKkr-Black.otf', 0), 'D': (d + 'NotoSansCJKkr-Bold.otf', 0), 'R': (d + 'NotoSansCJKkr-Regular.otf', 0)}
FP = _fp(); _fc = {}
def F(w, size):
    k = (w, int(size))
    if k not in _fc: _fc[k] = ImageFont.truetype(FP[w][0], int(size), index=FP[w][1])
    return _fc[k]
_m = ImageDraw.Draw(Image.new('RGB', (8, 8)))
def tw(t, f): return _m.textlength(t, font=f)
def fit(t, w, size, maxw, where):
    s = size
    while s > size * 0.55 and tw(t, F(w, s)) > maxw: s -= 2
    if tw(t, F(w, s)) > maxw: ISSUES.append(f'text too long ({where}): {t}')
    return s
def wrap(t, w, size, maxw):
    """One line if it fits; otherwise the balanced 2-line split (no lonely last word); 3+ lines only if unavoidable."""
    f = F(w, size)
    if tw(t, f) <= maxw: return [t]
    words = t.split(' ')
    for i in range(1, len(words)):  # a natural break after a comma wins if both halves fit
        if words[i - 1].endswith(',') and max(tw(' '.join(words[:i]), f), tw(' '.join(words[i:]), f)) <= maxw:
            return [' '.join(words[:i]), ' '.join(words[i:])]
    best = None
    for i in range(1, len(words)):
        a, b = ' '.join(words[:i]), ' '.join(words[i:])
        wmax = max(tw(a, f), tw(b, f))
        if best is None or wmax < best[0]: best = (wmax, [a, b])
    if best and best[0] <= maxw: return best[1]
    lines, cur = [], ''
    for x in words:
        nxt = (cur + ' ' + x).strip()
        if tw(nxt, f) <= maxw or not cur: cur = nxt
        else: lines.append(cur); cur = x
    return lines + [cur]

def hexrgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3

# ---------- photos ----------
def load_photo(path):
    im = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
    if min(im.size) < 700: REVIEW.append(f'{os.path.basename(path)} is small ({im.size[0]}x{im.size[1]}): ask the client for a larger original')
    return im
def cover(im, w, h, zoom=1.0, fx=0.5, fy=0.5):
    """Crop im to aspect w:h, zoomed in by `zoom` around focus (fx, fy), resized to (w, h)."""
    iw, ih = im.size; r = w / h
    cw, ch = (iw, iw / r) if iw / ih < r else (ih * r, ih)
    cw, ch = cw / zoom, ch / zoom
    x0 = min(max(0, fx * iw - cw / 2), iw - cw); y0 = min(max(0, fy * ih - ch / 2), ih - ch)
    return im.resize((w, h), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))

# ---------- scenes ----------
CARD = (60, 300, W - 60, 300 + 1100)   # photo card box (x0, y0, x1, y1)
BGX = 1.08   # background is drawn larger so it can drift opposite to the camera (parallax)
def bg_for(photo):
    w, h = int(W * BGX), int(H * BGX)
    b = cover(photo, w // 4, h // 4).filter(ImageFilter.GaussianBlur(10)).resize((w, h), Image.BILINEAR)
    return Image.blend(b, Image.new('RGB', (w, h), (10, 10, 14)), 0.55)

# camera moves: (zoom0, zoom1, fx0, fx1, fy0, fy1); eased so they start and stop softly like a slider/gimbal shot
MOVES = {
    'push':   (1.00, 1.16, .50, .50, .50, .50),   # slow push-in
    'pull':   (1.20, 1.02, .50, .50, .45, .50),   # reveal / pull-out
    'pan_r':  (1.18, 1.18, .30, .70, .50, .50),   # truck left -> right
    'pan_l':  (1.18, 1.18, .70, .30, .50, .50),
    'tilt':   (1.18, 1.22, .50, .50, .70, .35),   # tilt up toward the top of the frame
    'diag':   (1.10, 1.26, .35, .60, .60, .40),   # push in on a diagonal
}
def scene_plan(brief, photos):
    """Scene list with photo, camera move, entry direction and text; durations are set after TTS."""
    n = len(photos); P = lambda i: photos[i % n]
    order = ['pan_r', 'tilt', 'pan_l', 'diag', 'push']
    sc = [{'kind': 'hook', 'photo': P(0), 'move': 'push', 'text': brief['tagline'], 'say': brief.get('say', {}).get('tagline') or brief['tagline']}]
    for i, p in enumerate(brief['points']):
        say = (brief.get('say', {}).get('points') or [None] * 9)[i] or p
        sc.append({'kind': 'point', 'idx': i, 'photo': P(i + 1 if n > 1 else 0), 'move': order[i % len(order)], 'text': p, 'say': say})
    if brief.get('offer'):
        sc.append({'kind': 'offer', 'photo': P(len(brief['points']) + 1), 'move': 'diag', 'text': brief['offer'],
                   'say': brief.get('say', {}).get('offer') or brief['offer']})
    sc.append({'kind': 'cta', 'photo': P(0), 'move': 'pull', 'text': brief['cta'],
               'say': brief.get('say', {}).get('cta') or f"{brief['name']}. {brief['cta']}"})
    for j, x in enumerate(sc): x['enter'] = 0 if j == 0 else (1 if j % 2 else -1)   # card slides in from right / left
    return sc

def smooth(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)

def static_layer(brief, s, accent):
    """Everything that does not move in a scene (text panels), as one RGBA image."""
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    # brand chip top-left
    chip = brief['name']; f = F('D', 40); cw = tw(chip, f)
    d.rounded_rectangle((60, 150, 60 + cw + 56, 222), 36, fill=accent + (255,))
    d.text((88, 186), chip, font=f, fill=(255, 255, 255), anchor='lm')
    if brief.get('sample'): d.text((W - 60, 186), '샘플 · 가상 매장', font=F('R', 30), fill=(220, 220, 220), anchor='rm')
    k = s['kind']
    if k in ('hook', 'point', 'offer'):
        size = 76 if k == 'hook' else 64
        lines = wrap(s['text'], 'B', size, W - 200)
        if len(lines) > 2: ISSUES.append(f'{k} text needs more than 2 lines: {s["text"]}')
        lines = lines[:2]
        size = min(fit(x, 'B', size, W - 200, k) for x in lines)
        lh = int(size * 1.3); top = 1460
        head = 64 if k == 'offer' else 0   # offer box carries its own "지금 혜택" header inside
        box_h = lh * len(lines) + 70 + head
        fill = accent + (245,) if k == 'offer' else (255, 255, 255, 245)
        d.rounded_rectangle((60, top, W - 60, top + box_h), 34, fill=fill)
        if k == 'point':
            d.ellipse((90, top + 24, 150, top + 84), fill=accent + (255,))
            d.text((120, top + 54), str(s['idx'] + 1), font=F('B', 38), fill=(255, 255, 255), anchor='mm')
        if k == 'offer':
            d.text((W // 2, top + 52), '지금 혜택', font=F('D', 38), fill=(255, 255, 255, 215), anchor='mm')
        col = (255, 255, 255) if k == 'offer' else (20, 20, 24)
        for i, x in enumerate(lines):
            d.text((W // 2 + (30 if k == 'point' else 0), top + 35 + head + lh * i + lh // 2), x, font=F('B', size), fill=col, anchor='mm')
    else:  # cta: info card
        info = list((brief.get('info') or {}).items())[:4]
        top = 1240; rows = len(info); box_h = 150 + 78 * rows + 150
        d.rounded_rectangle((60, top, W - 60, top + box_h), 34, fill=(255, 255, 255, 248))
        nm = fit(brief['name'], 'B', 84, W - 200, 'name')
        d.text((W // 2, top + 82), brief['name'], font=F('B', nm), fill=accent, anchor='mm')
        for i, (kk, vv) in enumerate(info):
            y = top + 170 + 78 * i
            d.text((110, y), kk, font=F('D', 36), fill=(120, 120, 128), anchor='lm')
            vs = fit(str(vv), 'D', 40, W - 360, f'info {kk}')
            d.text((260, y), str(vv), font=F('D', vs), fill=(20, 20, 24), anchor='lm')
        cs = fit(s['text'], 'B', 46, W - 220, 'cta')
        cy = top + box_h - 80
        d.rounded_rectangle((100, cy - 46, W - 100, cy + 46), 46, fill=accent + (255,))
        d.text((W // 2, cy), s['text'], font=F('B', cs), fill=(255, 255, 255), anchor='mm')
    return L

def render_scene(args):
    i, out_dir = args
    s = G['scenes'][i]; n = s['frames']; accent = G['accent']
    bg = G['bgs'][i]; lay = G['layers'][i]
    x0, y0, x1, y1 = CARD; cw, ch = x1 - x0, y1 - y0
    mask = Image.new('L', (cw, ch), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw, ch), 40, fill=255)
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((x0 + 6, y0 + 18, x1 + 6, y1 + 18), 40, fill=(0, 0, 0, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', f'{out_dir}/s{i}.mp4'],
                         stdin=subprocess.PIPE)
    z0, z1, fx0, fx1, fy0, fy1 = MOVES[s['move']]
    bw, bh = bg.size; ent = s.get('enter', 0); TIN = 0.3 * FPS
    for k in range(n):
        t = smooth(k / max(1, n - 1))
        fx, fy = fx0 + (fx1 - fx0) * t, fy0 + (fy1 - fy0) * t
        # background drifts against the camera direction -> depth
        bx = int((bw - W) * (1 - fx)); by = int((bh - H) * (1 - fy))
        frame = bg.crop((bx, by, bx + W, by + H)).convert('RGBA'); frame.alpha_composite(shadow)
        ph = cover(s['photo'], cw, ch, zoom=z0 + (z1 - z0) * t, fx=fx, fy=fy)
        e = ease(k / TIN) if ent else 1.0
        if e < 1:   # entry: card whips in from the side with motion blur and settles
            ph = ph.filter(ImageFilter.BoxBlur(int(14 * (1 - e)))) if e < .85 else ph
            sc = 0.94 + 0.06 * e
            pw, phh = int(cw * sc), int(ch * sc)
            ph2 = ph.resize((pw, phh), Image.BILINEAR); m2 = mask.resize((pw, phh))
            ox = x0 + (cw - pw) // 2 + int(ent * 260 * (1 - e)); oy = y0 + (ch - phh) // 2
            m2 = m2.point(lambda v: int(v * min(1, e * 1.6)))
            frame.paste(ph2, (ox, oy), m2)
        else:
            frame.paste(ph, (x0, y0), mask)
        a = ease(k / (0.35 * FPS))          # text slides up and fades in over 0.35 s
        if a < 1:
            lay2 = lay.copy(); lay2.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
            frame.alpha_composite(lay2, (0, int(40 * (1 - a))))
        else:
            frame.alpha_composite(lay)
        # progress bar
        prog = (s['start'] + k / FPS) / G['total']
        ImageDraw.Draw(frame).rectangle((0, H - 14, int(W * prog), H), fill=accent + (255,))
        p.stdin.write(frame.convert('RGB').tobytes())
        if k == n // 2: frame.convert('RGB').save(f'{out_dir}/mid{i}.png')
    p.stdin.close(); p.wait()
    return p.returncode

# ---------- voice ----------
def make_voice(scenes, voice, work):
    from make import hangulize, lcs_ratio   # radar helpers: digits -> Hangul, similarity
    import sherpa_onnx
    from supertonic import TTS
    a = os.path.join(ROOT, 'radar', 'asr', 'sherpa-onnx-zipformer-korean-2024-06-24/')
    rec = sherpa_onnx.OfflineRecognizer.from_transducer(encoder=a + 'encoder-epoch-99-avg-1.int8.onnx', decoder=a + 'decoder-epoch-99-avg-1.onnx',
                                                        joiner=a + 'joiner-epoch-99-avg-1.int8.onnx', tokens=a + 'tokens.txt', num_threads=4)
    tts = TTS(model='supertonic-3'); st = tts.get_voice_style(voice)
    report = []
    for i, s in enumerate(scenes):
        say = re.sub(r'\d[\d,]*', lambda m: _kor_num(m.group().replace(',', '')), s['say'])
        target = hangulize(say); best = None
        for _ in range(6):
            w, _ = tts.synthesize(say, voice_style=st, lang='ko', speed=1.05, total_steps=32)
            y = np.asarray(w, dtype=np.float32).squeeze(); idx = np.where(np.abs(y) > 0.01)[0]
            if not len(idx): continue
            y = y[max(0, idx[0] - 600): idx[-1] + 2500]
            st_ = rec.create_stream(); st_.accept_waveform(SR, y); rec.decode_stream(st_); heard = st_.result.text.strip()
            sim = lcs_ratio(target, hangulize(heard))
            if best is None or sim > best[0]: best = (sim, y, heard)
            if sim >= 0.88: break
        if best is None: sys.exit(f'TTS produced only silence for scene {i}')
        sim, y, heard = best
        path = f'{work}/v{i}.wav'; sf.write(path, y / max(1e-6, np.abs(y).max()) * 0.85, SR)
        s['wav'] = path; s['vdur'] = len(y) / SR
        report.append({'scene': s['kind'], 'say': say, 'heard': heard, 'sim': round(sim, 2)})
        if sim < 0.75: ISSUES.append(f'voice check weak ({s["kind"]}): said "{say}" heard "{heard}"')
    return report

def _kor_num(n):
    from make import num2kor
    return num2kor(int(n)) if n.isdigit() else n

G = {}

def caption(brief):
    """Post text from the brief only (no new facts): hook, points, offer, info, up to 5 hashtags."""
    lines = [f"{brief['tagline']} | {brief['name']}", '']
    lines += [f'✔ {p}' for p in brief['points']]
    if brief.get('offer'): lines += ['', f"🎁 {brief['offer']}"]
    info = brief.get('info') or {}
    if info: lines += [''] + [f'📍 {k} {v}' if i == 0 else f'🕒 {k} {v}' for i, (k, v) in enumerate(info.items())]
    if brief.get('cta'): lines += ['', brief['cta']]
    tags = [brief['name'], brief.get('category', '')]
    addr = info.get('주소', '')
    m = re.match(r'\s*(\S+?(시|군|구))\b', addr)
    if m and 'OO' not in m.group(1): tags += [m.group(1) + brief.get('category', ''), m.group(1) + '맛집' if brief.get('category') in ('카페', '식당', '음식점') else '']
    tags.append('동네가게')
    tags = [re.sub(r'[^0-9A-Za-z가-힣]', '', t) for t in tags]
    tags = list(dict.fromkeys(t for t in tags if t))[:5]
    return '\n'.join(lines) + '\n\n' + ' '.join('#' + t for t in tags) + '\n'


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('brief'); ap.add_argument('out')
    ap.add_argument('--square', action='store_true', help='also write video_square.mp4 (1080x1080)')
    a = ap.parse_args()
    brief = json.load(open(a.brief)); base = os.path.dirname(os.path.abspath(a.brief))
    for k in ('name', 'tagline', 'points', 'cta', 'photos'):
        if not brief.get(k): sys.exit(f'brief missing {k}')
    if not 2 <= len(brief['points']) <= 4: sys.exit('brief needs 2-4 points')
    out = a.out; work = os.path.join(out, 'work'); os.makedirs(work, exist_ok=True)
    photos = [load_photo(p if os.path.isabs(p) else os.path.join(base, p)) for p in brief['photos']]
    accent = hexrgb(brief.get('accent', '#E8743B'))
    scenes = scene_plan(brief, photos)
    silent = brief.get('voice', 'F3') == 'none'   # captions + music only
    if silent:
        vrep = []
        for s in scenes: s['vdur'] = 2.6 if s['kind'] != 'cta' else 3.2
    else:
        vrep = make_voice(scenes, brief.get('voice', 'F3'), work)
    t = 0.0
    for s in scenes:
        s['start'] = t; s['voice_at'] = t + 0.25
        d = max(2.2, s['vdur'] + 0.7) + (0.8 if s['kind'] == 'cta' else 0)
        s['frames'] = int(round(d * FPS)); t += s['frames'] / FPS
    total = t
    if not 12 <= total <= 40: ISSUES.append(f'duration {total:.1f}s outside 12-40 s')
    G.update(scenes=scenes, accent=accent, total=total, bgs=[bg_for(s['photo']) for s in scenes],
             layers=[static_layer(brief, s, accent) for s in scenes])
    with cf.ProcessPoolExecutor(min(4, len(scenes))) as ex:
        if any(ex.map(render_scene, [(i, work) for i in range(len(scenes))])): sys.exit('render failed')
    with open(f'{work}/list.txt', 'w') as f:
        for i in range(len(scenes)): f.write(f"file 's{i}.mp4'\n")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{work}/list.txt', '-c', 'copy', f'{work}/v.mp4'], check=True)
    # audio: voices at their times + music bed ducked under the voice
    import music
    music.make(f'{work}/music.wav', total + 0.5, mood=brief.get('music', 'bright'))
    ins, flt = [], []
    if silent:
        ins = ['-i', f'{work}/music.wav']; mix = '[0:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[out]'
    else:
        for i, s in enumerate(scenes):
            ms = int(s['voice_at'] * 1000); ins += ['-i', s['wav']]; flt.append(f'[{i}:a]adelay={ms}|{ms},aresample=48000[a{i}]')
        m = len(scenes); ins += ['-i', f'{work}/music.wav']
        mix = ''.join(f'[a{i}]' for i in range(m)) + f'amix=inputs={m}:normalize=0,apad[vo];[vo]asplit=2[vk][vm];' \
              f'[{m}:a]volume=0.10[mu];[mu][vk]sidechaincompress=threshold=0.02:ratio=8:attack=10:release=400[md];' \
              f'[vm][md]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[out]'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + ins + ['-filter_complex', ';'.join(flt + [mix]), '-map', '[out]',
                    '-t', f'{total:.3f}', '-c:a', 'aac', '-b:a', '192k', f'{work}/a.m4a'], check=True)
    final = os.path.join(out, 'video.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{work}/v.mp4', '-i', f'{work}/a.m4a', '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-c:a', 'copy', '-shortest', '-movflags', '+faststart', final], check=True)
    # final gain so every delivery lands at -14 LUFS (loudnorm alone can end ~1 dB low on short clips)
    meas = subprocess.run(['ffmpeg', '-i', final, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    li = re.findall(r'I:\s+(-?[\d.]+) LUFS', meas)
    if li and abs(float(li[-1]) + 14) > 0.4:
        tmp = final + '.tmp.mp4'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', final, '-c:v', 'copy', '-af',
                        f'volume={-14 - float(li[-1]):.2f}dB,alimiter=limit=0.95:level=false', '-c:a', 'aac', '-b:a', '192k',
                        '-movflags', '+faststart', tmp], check=True)
        os.replace(tmp, final)
    # thumbnail = hook frame, QA sheet = middle frame of every scene
    Image.open(f'{work}/mid0.png').save(os.path.join(out, 'thumb.jpg'), quality=92)
    mids = [Image.open(f'{work}/mid{i}.png').resize((270, 480)) for i in range(len(scenes))]
    sheet = Image.new('RGB', (270 * len(mids), 480)); [sheet.paste(im, (270 * i, 0)) for i, im in enumerate(mids)]
    sheet.save(os.path.join(out, 'qa.png'))
    files = {'video': final, 'thumb': os.path.join(out, 'thumb.jpg'), 'qa_sheet': os.path.join(out, 'qa.png')}
    # post caption (DELUXE+): ready to paste on Instagram / 당근, no links, max 5 hashtags
    cap = os.path.join(out, 'caption.txt'); open(cap, 'w').write(caption(brief)); files['caption'] = cap
    if a.square:  # PREMIUM: 1080x1080 feed version, whole 9:16 frame kept over a blurred fill so no text is cut
        sq = os.path.join(out, 'video_square.mp4')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', final, '-filter_complex',
                        '[0:v]split[a][b];[a]scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080,boxblur=30:2,eq=brightness=-0.12[bg];'
                        '[b]scale=-2:1080[fg];[bg][fg]overlay=(W-w)/2:0,format=yuv420p',
                        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-c:a', 'copy', '-movflags', '+faststart', sq], check=True)
        files['square'] = sq
    man = {'name': brief['name'], 'duration': round(total, 2), 'scenes': [s['kind'] for s in scenes], 'voice_check': vrep,
           'qa': {'pass': not ISSUES, 'issues': ISSUES, 'review': REVIEW}, 'files': files}
    json.dump(man, open(os.path.join(out, 'manifest.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps({'qa_pass': not ISSUES, 'issues': ISSUES, 'review': REVIEW, 'duration': round(total, 2)}, ensure_ascii=False))
    sys.exit(0 if not ISSUES else 1)


if __name__ == '__main__':
    main()
