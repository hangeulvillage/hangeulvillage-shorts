# Hangeul Village shorts pipeline
1. `bash setup.sh` (installs voice model Supertonic-3, Korean ASR checker, fonts)
2. Write a plan JSON: `[{"fmt":"A","names":["Sofia"],"voice":"female"}, ...]`
   - fmt A = name build, B = read-this quiz, C = comment requests (up to 3 names, "Name @handle"),
     D = K-drama word, E = Seoul sign, Q = guess the English word written in Hangul (커피, 노트북),
     V = "1 or 2?" choice quiz. For D/E/Q/V give just the Korean word from words.json (meaning, note and
     the V distractor are looked up), or "사랑해 = I love you | one-line note"
   - voice: female (F1 warm) or male (M2 warm)
3. `python3 shorts/batch.py plan.json OUT_DIR` -> mp4 + per-platform copy (.txt) + manifest.json
Every spoken syllable is regenerated until a Korean speech recognizer hears it (similar-sound tolerant).

## Languages (2026-10-31)
- `shorts/i18n.py`: top 10 languages by speakers after English (zh-Hant, hi, es, ar, fr, bn, pt, id, ur, ru): on-screen strings, copy templates, word meanings, local names with Korean spelling.
- Plan entries take `"lang"`; names can carry a fixed Korean spelling: `{"fmt":"A","names":["Priya=프리야"],"lang":"hi"}`.
- English videos get `yt_translations` (11 languages) in manifest.json; `shorts/yt_translate.js` adds them on the YouTube Studio translations page (set `window.HV_TR` first).

## Quiz formats (2026-11-04)
- Q and V ask viewers to answer in the comments before a 3-2-1 countdown, then build the answer.
- Vetted lists: words.json Q (English loanwords, incl. Konglish like 노트북 = laptop) and V (correct, meaning, note, distractor, distractor meaning).
- English copy only (no YouTube translations yet).
