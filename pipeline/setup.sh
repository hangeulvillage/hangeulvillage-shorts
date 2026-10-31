#!/usr/bin/env bash
# Rebuilds the Hangeul Village shorts pipeline in a fresh workspace. Run from this folder.
set -e
cd "$(dirname "$0")"
pip install --break-system-packages -q "sherpa-onnx==1.12.40" soundfile supertonic numpy opencc-python-reimplemented >/dev/null 2>&1
(cd brand && npm install --silent @fontsource/noto-sans-kr@5.1.1 @fontsource/gowun-batang@5.1.1 @fontsource/bricolage-grotesque@5.1.1 @fontsource/noto-sans-tc@5.3.1 @fontsource/noto-sans-devanagari@5.3.0 @fontsource/noto-sans-bengali@5.3.0 @fontsource/noto-sans-arabic@5.3.0 @fontsource/noto-nastaliq-urdu@5.3.0 @fontsource/noto-sans@5.3.0 >/dev/null 2>&1)
if [ ! -d asr/sherpa-onnx-zipformer-korean-2024-06-24 ]; then
  curl -sSL -o asr/m.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-zipformer-korean-2024-06-24.tar.bz2
  (cd asr && tar xjf m.tar.bz2 && rm m.tar.bz2)
fi
python3 -c "from supertonic import TTS; TTS(model='supertonic-3')" >/dev/null 2>&1
echo "pipeline ready"
