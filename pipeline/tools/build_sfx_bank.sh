#!/usr/bin/env bash
# Re-render the sound-effect bank in brand/sfx with earshot (https://github.com/Leonxlnx/earshot, MIT).
# Only needed to change the sounds: the daily pipeline just reads the committed WAV files (no earshot, no torch).
# All sounds are synthesized in code by earshot's bank (no recordings), so there is no third-party audio licence.
set -euo pipefail
cd "$(dirname "$0")/.."
VENV=${VENV:-/tmp/earshot-venv}
[ -x "$VENV/bin/earshot" ] || { python3 -m venv "$VENV"; "$VENV/bin/pip" install -q "git+https://github.com/Leonxlnx/earshot@v0.4.1" || "$VENV/bin/pip" install -q git+https://github.com/Leonxlnx/earshot; }
E="$VENV/bin/earshot"; B=brand/sfx; mkdir -p "$B"
i=0; for p in G4 A4 B4 C5 D5 E5; do "$E" sfx render knock/wood --pitch $p --sr 48000 -o "$B/pop_$i.wav" >/dev/null; i=$((i+1)); done  # block lands, rising per block
"$E" sfx render pro_notify/ding_2045 --sr 48000 -o "$B/chime.wav" >/dev/null   # word complete
"$E" sfx render mallet/glock        --sr 48000 -o "$B/reveal.wav" >/dev/null   # V: answer revealed
"$E" sfx render swish/bright        --sr 48000 -o "$B/whoosh.wav" >/dev/null   # opening frame
"$E" sfx render hover_tick/mid      --sr 48000 -o "$B/tick.wav" >/dev/null     # countdown 3-2-1 (B, Q, V)
for f in "$B"/*.wav; do "$E" sfx check "$f" | tail -1; done
