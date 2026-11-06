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


## 2026-11-05 update: faster pacing, hook test, ja/de
- **Pacing v3:** syllables land every 0.6 s (was 0.85), the word holds 2.0 s, end card 2.0 s, countdown 0.8 s per number. Shorts now run 8-12 s (were 11-14 s). QA accepts 6-35 s and flags anything over 12.5 s for review.
- **Hook A/B/C test:** D/E/Q/V have 3 opening variants (on-screen line + Korean voice line). `job.hook` picks one; without it, a stable hash of the word does. The manifest records `hook` and `duration`. Localized videos always use variant 0.
- **Titles:** YouTube titles prefer candidates of 60 chars or less (before ` #shorts`), so they aren't cut off in the Shorts feed.
- **Japanese (ja) and German (de)** language packs: UI, copy, all vetted word meanings, local names, Noto Sans JP font.

## 2026-11-06 update: the first frame is the hook
YouTube Studio showed 90.5% of Shorts-feed viewers swiping away, while those who stayed watched to the end. The old frame 0 was an empty background, with text fading in after 0.2-0.5 s. Now the opening scene is drawn fully formed from frame 0 (`INSTANT`: every fade in the first scene is complete). D shows the word card at once, A shows "? ? ?" tiles under the name, and the Korean voice line starts at 0.05 s (A now says "한국어로 어떻게 쓸까요?").

## App waitlist (2026-11-06)
batch.py adds one line with the Google Form link ("Hangeul Village 앱 알림 신청", answers go to the owner's Google account) to every YouTube description and Instagram/Facebook caption. It goes before the hashtags, in the video's language for en/bn/fr/pt/es/ja/de. TikTok captions get no link because links there are not clickable.
