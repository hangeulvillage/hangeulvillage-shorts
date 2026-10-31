"""Korean voice for Hangeul Village shorts: Supertonic-3 (OpenRAIL), warm EQ, every take verified by Korean ASR.
Set HV_VOICE=female|male."""
import os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); SCR = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SCR, 'asr'))
from check import hear
from supertonic import TTS
SR = 44100
import subprocess, tempfile, soundfile as sf
# chosen voices: female = F1 warm (picked 10/30), male = candidate until the user picks
VOICES = {
    'female': ('F1', 'lowshelf=f=220:g=2.5,highshelf=f=2800:g=-6,lowpass=f=6000'),
    'male':   ('M2', 'lowshelf=f=160:g=1.5,highshelf=f=3200:g=-4,lowpass=f=6500'),  # M2 picked 10/30
}
VOICE = os.environ.get('HV_VOICE', 'female')
_tts = None; _styles = {}
def _load():
    global _tts
    if _tts is None: _tts = TTS(model='supertonic-3')
    name = VOICES[VOICE][0]
    if name not in _styles: _styles[name] = _tts.get_voice_style(name)
    return _tts, _styles[name]
def _warm(y):
    chain = VOICES[VOICE][1]
    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, 'a.wav'), os.path.join(d, 'b.wav'); sf.write(a, y, SR)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', a, '-af', chain, '-ar', str(SR), b], check=True)
        z, _ = sf.read(b)
    return z.astype(np.float32)
def trim(x, sr=SR, thr=0.04, pad=0.03):
    x = np.asarray(x, dtype=np.float32).squeeze()
    hop = int(sr * 0.005); env = np.array([np.sqrt((x[i:i+hop] ** 2).mean()) for i in range(0, len(x), hop)])
    on = np.where(env > env.max() * thr)[0]
    if not len(on): return x
    a = max(0, on[0] * hop - int(pad * sr)); b = min(len(x), (on[-1] + 1) * hop + int(pad * sr))
    y = x[a:b].copy(); f = int(0.008 * sr); y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f)
    return y
_DIG = {'0': '영', '1': '일', '2': '이', '3': '삼', '4': '사', '5': '오', '6': '육', '7': '칠', '8': '팔', '9': '구'}
def _norm(s):
    s = ''.join(_DIG.get(ch, ch) for ch in s)  # the recognizer writes 사 as "4", 일 as "1" ...
    return ''.join(ch for ch in s if '\uac00' <= ch <= '\ud7a3')
_L='ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'; _V='ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'; _T=' ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ'
def _jamo(s):
    out = []
    for ch in s:
        c = ord(ch) - 0xAC00
        if 0 <= c < 11172:
            out += [_L[c // 588], _V[(c % 588) // 28]]
            t = _T[c % 28].strip()
            if t: out.append(t)
    return out
_GROUPS = ['ㄷㅌㄸ', 'ㅂㅍㅃ', 'ㄱㅋㄲ', 'ㅈㅊㅉ', 'ㅅㅆ', 'ㄴㄹ', 'ㅔㅐㅙㅞㅚ', 'ㅓㅗ', 'ㅜㅡ', 'ㅕㅛ', 'ㅖㅒ', 'ㅢㅣ']
def _cost(a, b):
    if a == b: return 0
    for g in _GROUPS:
        if a in g and b in g: return 0.3 if g not in ('ㅓㅗ', 'ㅜㅡ', 'ㄴㄹ') else 0.5
    return 1
def _sim(a, b):
    """1 - normalized edit distance over jamo."""
    x, y = _jamo(a), _jamo(b)
    if not x or not y: return 0.0
    d = list(range(len(y) + 1))
    for i in range(1, len(x) + 1):
        p, d[0] = d[0], i
        for j in range(1, len(y) + 1):
            p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + _cost(x[i - 1], y[j - 1]))
    return 1 - d[len(y)] / max(len(x), len(y))
def say(text, speed=0.9, tries=None):
    """Return (samples, sr, heard, ok). Exact match wins; otherwise the take whose recognition is closest (jamo similarity)."""
    tts, st = _load(); target = _norm(text)
    single = len(target) == 1
    tries = tries or (10 if single else 5)
    best = None
    for k in range(tries):
        w, _ = tts.synthesize(text, voice_style=st, lang='ko', speed=speed, total_steps=10)
        y = _warm(trim(w)); h = _norm(hear(y, SR))
        if single and not h:  # recognizer often drops a lone short syllable: try it doubled ("사 사")
            gap = np.zeros(int(0.18 * SR), dtype=np.float32)
            h2 = _norm(hear(np.concatenate([y, gap, y]), SR))
            if h2: h = h2
        cand = h[:1] if single else h
        score = 1.0 if (cand == target or target in h) else _sim(target, cand)
        if best is None or score > best[0]: best = (score, y, h)
        if score >= 1.0: break
    ok = best[0] >= (0.65 if single else 0.75)
    return best[1], SR, f"{best[2]} ({best[0]:.2f})", ok
