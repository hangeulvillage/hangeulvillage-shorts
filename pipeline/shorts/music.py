"""Procedural, royalty-free soft marimba + pad bed (original, generated here)."""
import numpy as np, soundfile as sf, sys
def make(path, dur, sr=48000, seed=3):
    rng = np.random.default_rng(seed)
    n = int(dur * sr) + sr; out = np.zeros(n, dtype=np.float32)
    bpm = 104; beat = 60 / bpm
    scale = [60, 62, 64, 67, 69, 72, 74, 76]  # C major pentatonic-ish
    chords = [[48, 55, 64], [45, 52, 60], [41, 48, 57], [43, 50, 59]]  # C Am F G
    def tone(freq, length, kind):
        t = np.arange(int(length * sr)) / sr
        if kind == 'mar':
            env = np.exp(-t * 7.5); w = np.sin(2*np.pi*freq*t) + 0.25*np.sin(2*np.pi*freq*4*t)*np.exp(-t*25)
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
