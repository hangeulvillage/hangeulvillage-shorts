#!/usr/bin/env bash
# Prepares the 지원금 레이더 pipeline in a fresh workspace. Run from anywhere.
set -e
cd "$(dirname "$0")"
pip install --break-system-packages -q "sherpa-onnx==1.12.40" soundfile supertonic numpy pillow >/dev/null 2>&1
if [ ! -d asr/sherpa-onnx-zipformer-korean-2024-06-24 ]; then
  mkdir -p asr
  curl -sSL -o asr/m.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-zipformer-korean-2024-06-24.tar.bz2
  (cd asr && tar xjf m.tar.bz2 && rm m.tar.bz2)
fi
if [ ! -f /usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc ]; then
  mkdir -p fonts
  for w in Black Bold Regular; do
    [ -f fonts/NotoSansCJKkr-$w.otf ] || curl -sSL -o fonts/NotoSansCJKkr-$w.otf https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansCJKkr-$w.otf
  done
fi
python3 -c "from supertonic import TTS; TTS(model='supertonic-3')" >/dev/null 2>&1
echo "radar pipeline ready"
