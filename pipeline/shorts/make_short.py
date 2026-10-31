"""Render a Hangeul Village short with Korean voice.
usage: python3 make_short.py FORMAT "Name[ @handle]" ["Name2" ...] --out file.mp4
"""
import sys, os, json, subprocess, asyncio, base64, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
SCR = os.path.dirname(HERE)
ap = argparse.ArgumentParser(); ap.add_argument('fmt'); ap.add_argument('names', nargs='+'); ap.add_argument('--out', required=True); ap.add_argument('--voice', default='female', choices=['female', 'male']); ap.add_argument('--lang', default='en')
a = ap.parse_args()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import i18n
UI = i18n.ui(a.lang)
# 'Priya=프리야' fixes the Korean spelling of a name (curated local names)
FIX = {n.split('=')[0].strip(): n.split('=')[1].strip() for n in a.names if '=' in n and a.fmt not in ('D', 'E')}
if a.fmt not in ('D', 'E'): a.names = [n.split('=')[0].strip() for n in a.names]

# ---- page with local fonts ----
studio = open(os.path.join(SCR, 'shorts-studio.html')).read()
fonts = '<link rel="stylesheet" href="brand/common.css">'
page = os.path.join(SCR, '_render.html')
open(page, 'w').write('<!doctype html><html><head><meta charset=utf8>' + fonts + '</head><body>' + studio + '</body></html>')

async def record():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1200, 'height': 1000})
        got = {}
        async def save(b64, name):
            got['data'] = base64.b64decode(b64); got['name'] = name
        await pg.expose_function('__saveFile', save)
        await pg.add_init_script("""window.claude={use:n=>Promise.resolve(n==='downloads'?{save:async({filename,data})=>{const buf=new Uint8Array(await data.arrayBuffer());let s='';for(let i=0;i<buf.length;i+=32768)s+=String.fromCharCode.apply(null,buf.subarray(i,i+32768));await window.__saveFile(btoa(s),filename);return {status:'saved'}}}:null)}""")
        await pg.add_init_script('window.HV_UI = ' + json.dumps(UI, ensure_ascii=False) + ';')
        await pg.goto('file://' + page)
        await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(500)
        sample = ' '.join(v for v in UI.values() if isinstance(v, str))
        if sample:
            await pg.evaluate('''async (s) => { for (const f of ["Noto Sans TC","Noto Sans Devanagari","Noto Sans Bengali","Noto Sans Arabic","Noto Nastaliq Urdu","Noto Sans","Bricolage Grotesque"]) { try { await document.fonts.load('700 64px "' + f + '"', s); } catch (e) {} } }''', sample)
            await pg.wait_for_timeout(300)
        await pg.check(f'input[value={a.fmt}]')
        await pg.fill('#names', '\n'.join(a.names)); await pg.wait_for_timeout(600)
        for en, ko in FIX.items():
            sel = '#fix-' + ''.join(c if c.isalnum() else '-' for c in en.lower())
            await pg.fill(sel, ko); await pg.dispatch_event(sel, 'change'); await pg.wait_for_timeout(300)
        info = await pg.evaluate("""()=>[...document.querySelectorAll('#ko-fix input')].map(i=>i.value)""")
        await pg.click('#rec')
        for _ in range(120):
            if 'data' in got: break
            await pg.wait_for_timeout(500)
        await b.close()
        return got, info
got, kos = asyncio.run(record())
vid = os.path.join(HERE, '_video.' + got['name'].split('.')[-1])
open(vid, 'wb').write(got['data'])

# ---- timings (mirror of buildPlan in the studio) ----
def nsyl(ko): return len(ko.replace(' ', ''))
lines = []  # (time, text, speed)
text_word, text_idx = {}, {}
def syl_lines(ko, base, per):
    for k, ch in enumerate(ko.replace(' ', '')):
        text_word[len(lines)] = ko; text_idx[len(lines)] = k
        lines.append((base + 0.5 + per * k + 0.55, ch, 0.8))
t = 0
sfx = []  # (time, kind)
def land_sfx(base, per, n):
    for k in range(n): sfx.append((base + 0.5 + per * k + 0.53, 'pop'))
if a.fmt == 'A':
    ko = kos[0]; t = 2.2; sfx.append((0.05, 'whoosh'))
    syl_lines(ko, t, 0.85); land_sfx(t, 0.85, nsyl(ko))
    done = t + 0.5 + 0.85 * nsyl(ko) + 0.2; sfx.append((done, 'chime'))
    lines += [(done + 0.45, ko, 0.85), (done + 1.5, ko, 0.85)]
    t += 0.6 + 0.85 * nsyl(ko) + 2.4
elif a.fmt == 'B':
    ko = kos[0]; sfx.append((0.05, 'whoosh'))
    lines.append((1.0, '읽을 수 있어요?', 0.9))
    t = 4.2
    syl_lines(ko, t, 0.85); land_sfx(t, 0.85, nsyl(ko))
    done = t + 0.5 + 0.85 * nsyl(ko) + 0.2; sfx.append((done, 'chime'))
    lines.append((done + 0.45, ko, 0.85))
    t += 0.6 + 0.85 * nsyl(ko) + 2.6
elif a.fmt in ('D', 'E'):
    ko = kos[0]; sfx.append((0.05, 'whoosh'))
    lines.append((0.7, '이 말, 들어 봤죠?' if a.fmt == 'D' else '이 표지판, 읽을 수 있어요?', 0.9))
    t = 2.4 if a.fmt == 'D' else 3.0
    syl_lines(ko, t, 0.85); land_sfx(t, 0.85, nsyl(ko))
    done = t + 0.5 + 0.85 * nsyl(ko) + 0.2; sfx.append((done, 'chime'))
    lines += [(done + 0.45, ko, 0.85), (done + 1.6, ko, 0.85)]
    t += 0.6 + 0.85 * nsyl(ko) + 3.0
else:
    t = 2.0; sfx.append((0.05, 'whoosh'))
    lines.append((0.5, '여러분이 요청한 이름들.', 0.95))
    for ko in kos:
        syl_lines(ko, t, 0.75); land_sfx(t, 0.75, nsyl(ko))
        done = t + 0.5 + 0.75 * nsyl(ko) + 0.2; sfx.append((done, 'chime'))
        lines.append((done + 0.4, ko, 0.85))
        t += 0.5 + 0.75 * nsyl(ko) + 1.8
lines.append((t + 0.35, '다음 단어를 추천해 주세요!' if a.fmt in ('D', 'E') else '이름을 알려 주세요!', 0.9))

# ---- TTS (Supertonic-3, voice F2, each clip verified by speech recognition) ----
os.environ['HV_VOICE'] = a.voice
sys.path.insert(0, HERE); import voice
import soundfile as sf, numpy as np
inputs, filt, report = [], [], []
def norm(x):
    x = np.asarray(x, dtype=np.float32)
    v = x[np.abs(x) > 0.02 * np.abs(x).max()]
    r = float(np.sqrt((v ** 2).mean())) if len(v) else 1.0
    g = min(0.14 / max(r, 1e-6), 0.95 / max(float(np.abs(x).max()), 1e-6))
    return x * g
for i, (ts, text, sp) in enumerate(lines):
    y, sr, heard, ok = voice.say(text, speed=0.85 if len(text) == 1 else 0.9)
    report.append((text, heard, ok))
    f = os.path.join(HERE, f'_v{i}.wav'); sf.write(f, norm(y), sr)
    inputs += ['-i', f]; ms = int(ts * 1000)
    filt.append(f'[{i+1}:a]adelay={ms}|{ms}[a{i}]')
# voice: clean up each clip (upsample, band-limit, light denoise, gentle compression, tiny room)
VCHAIN = 'aresample=48000:resampler=soxr,highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=5:release=80'
filt = [f.replace('[a', ',' + VCHAIN + '[a', 1) if False else f for f in filt]
filt = [f.split('[a')[0] + ',' + VCHAIN + '[a' + f.split('[a')[1] for f in filt]
vdur = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',vid],capture_output=True,text=True).stdout.strip()
import sfx as _sfx
_paths = {k: os.path.join(HERE, f'_sfx_{k}.wav') for k in ('pop', 'chime', 'whoosh')}
_sfx.pop(_paths['pop']); _sfx.chime(_paths['chime']); _sfx.whoosh(_paths['whoosh'])
sfx_inputs, sfx_filt = [], []
base_idx = len(lines) + 1
for j, (ts, kind) in enumerate(sfx):
    sfx_inputs += ['-i', _paths[kind]]; ms = max(0, int(ts * 1000))
    vol = {'pop': 0.55, 'chime': 0.5, 'whoosh': 0.45}[kind]
    sfx_filt.append(f'[{base_idx + j}:a]adelay={ms}|{ms},volume={vol}[s{j}]')
sys.path.insert(0, HERE); import music
mpath = os.path.join(HERE, '_music.wav'); music.make(mpath, float(vdur))
mi = len(lines) + 1 + len(sfx)
vmix = ''.join(f'[a{i}]' for i in range(len(lines))) + f'amix=inputs={len(lines)}:normalize=0,apad[voice]'
smix = ''.join(f'[s{j}]' for j in range(len(sfx))) + f'amix=inputs={len(sfx)}:normalize=0,apad[fx]'
duck = f'[voice]asplit=2[vk][vm];[{mi}:a]volume=0.06[mus];[mus][vk]sidechaincompress=threshold=0.015:ratio=12:attack=10:release=450[mduck];[vm][mduck][fx]amix=inputs=3:normalize=0,volume=6.7,alimiter=limit=0.89:level=false,aresample=48000[aout]'
cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', vid] + inputs + sfx_inputs + ['-i', mpath, '-filter_complex', ';'.join(filt + sfx_filt) + ';' + vmix + ';' + smix + ';' + duck,
       '-map', '0:v', '-map', '[aout]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', '30',
       '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', vdur, a.out]
subprocess.run(cmd, check=True)
# final pass: static gain so every short lands at -14 LUFS
import re as _re
meas = subprocess.run(['ffmpeg', '-i', a.out, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
I = float(_re.findall(r'I:\s+(-?[\d.]+) LUFS', meas)[-1])
tmp = a.out + '.tmp.mp4'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', a.out, '-c:v', 'copy', '-af', f'volume={-14 - I:.2f}dB,alimiter=limit=0.95:level=false', '-c:a', 'aac', '-b:a', '192k', tmp], check=True)
os.replace(tmp, a.out)
print(json.dumps({'out': a.out, 'korean': kos, 'voice_check': report}, ensure_ascii=False))
