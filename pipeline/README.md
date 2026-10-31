# Hangeul Village shorts pipeline
1. `bash setup.sh` (installs voice model Supertonic-3, Korean ASR checker, fonts)
2. Write a plan JSON: `[{"fmt":"A","names":["Sofia"],"voice":"female"}, ...]`
   - fmt A = name build, B = read-this quiz, C = comment requests (up to 3 names, "Name @handle"),
     D = K-drama word, E = Seoul sign. For D/E use "사랑해 = I love you | one-line note"
   - voice: female (F1 warm) or male (M2 warm)
3. `python3 shorts/batch.py plan.json OUT_DIR` -> mp4 + per-platform copy (.txt) + manifest.json
Every spoken syllable is regenerated until a Korean speech recognizer hears it (similar-sound tolerant).

## Languages (2026-10-31)
- `shorts/i18n.py`: top 10 languages by speakers after English (zh-Hant, hi, es, ar, fr, bn, pt, id, ur, ru): on-screen strings, copy templates, word meanings, local names with Korean spelling.
- Plan entries take `"lang"`; names can carry a fixed Korean spelling: `{"fmt":"A","names":["Priya=프리야"],"lang":"hi"}`.
- English videos get `yt_translations` (11 languages) in manifest.json; `shorts/yt_translate.js` adds them on the YouTube Studio translations page (set `window.HV_TR` first).
