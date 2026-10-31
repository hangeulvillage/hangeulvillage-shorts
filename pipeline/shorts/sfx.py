"""Original sound effects: soft pop (block lands), whoosh (hook), chime (word complete)."""
import numpy as np, soundfile as sf
SR = 48000
def pop(path):
    t = np.arange(int(0.09 * SR)) / SR
    f = 900 * np.exp(-t * 30) + 380
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45)
    sf.write(path, (y * 0.6).astype(np.float32), SR)
def chime(path):
    t = np.arange(int(0.9 * SR)) / SR; y = np.zeros_like(t)
    for k, (fr, d) in enumerate([(1046.5, 0), (1318.5, 0.07), (1568.0, 0.14)]):
        tt = np.clip(t - d, 0, None); y += np.where(t >= d, np.sin(2 * np.pi * fr * tt) * np.exp(-tt * 5), 0)
    sf.write(path, (y / np.abs(y).max() * 0.45).astype(np.float32), SR)
def whoosh(path, seed=1):
    n = int(0.45 * SR); rng = np.random.default_rng(seed); x = rng.standard_normal(n)
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    k = 60; y = np.convolve(x, np.ones(k) / k, mode='same') * env
    sf.write(path, (y / np.abs(y).max() * 0.35).astype(np.float32), SR)
