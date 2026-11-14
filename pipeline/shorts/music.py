"""Procedural, royalty-free soft marimba + pad bed (original, generated here)."""
import numpy as np, soundfile as sf, sys
MOODS = {  # bpm, melody scale, chord loop, melody brightness
    'marimba': (104, [60, 62, 64, 67, 69, 72, 74, 76], [[48, 55, 64], [45, 52, 60], [41, 48, 57], [43, 50, 59]], 4),   # C Am F G (original)
    'lofi':    (82, [57, 60, 62, 64, 67, 69, 72], [[45, 52, 60, 67], [41, 48, 57, 64], [48, 55, 64, 71], [43, 50, 59, 65]], 2),  # Am7 Fmaj7 Cmaj7 G7, mellow
    'bright':  (124, [62, 64, 66, 69, 71, 74, 76, 78], [[50, 57, 66], [47, 54, 62], [43, 50, 59], [45, 52, 61]], 6),   # D Bm G A, upbeat
}
def make(path, dur, sr=48000, seed=3, mood='marimba'):
    rng = np.random.default_rng(seed)
    n = int(dur * sr) + sr; out = np.zeros(n, dtype=np.float32)
    bpm, scale, chords, bright = MOODS.get(mood, MOODS['marimba']); beat = 60 / bpm
    def tone(freq, length, kind):
        t = np.arange(int(length * sr)) / sr
        if kind == 'mar':
            env = np.exp(-t * (bright + 3.5)); w = np.sin(2*np.pi*freq*t) + 0.25*np.sin(2*np.pi*freq*4*t)*np.exp(-t*25)
        else:
            env = np.minimum(1, t / 0.4) * np.exp(-t * 0.6); w = np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*2*t)
        return (w * env).astype(np.float32)
    mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
    t = 0.0; step = 0; bar = 0
    while t < dur:
        if step % 8 == 0:
            for m in chords[bar % 4]:
                s = tone(mtof(m), beat * 4.2, 'pad') * 0.05; i = int(t * sr); out[i:i+len(s)] += s[:max(0, n - i)]
            bar += 1
        if step % 2 == 0 or rng.random() < 0.35:
            m = scale[rng.integers(len(scale))]
            s = tone(mtof(m), 1.2, 'mar') * (0.11 if step % 4 == 0 else 0.07); i = int(t * sr); out[i:i+len(s)] += s[:max(0, n - i)]
        t += beat / 2; step += 1
    out = out[:int(dur * sr)]
    f = int(0.6 * sr); out[-f:] *= np.linspace(1, 0, f)
    sf.write(path, out / max(1e-6, np.abs(out).max()) * 0.5, sr)
if __name__ == '__main__': make(sys.argv[1], float(sys.argv[2]))
