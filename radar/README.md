# 지원금 레이더 shorts pipeline

Korean info shorts about government/local subsidies (YouTube @jiwongeumradar, channel id UCf_4uh8PjZKkUBU5ncjQJEg).
Separate brand from Hangeul Village; it only shares this repository.

1. `bash radar/setup.sh` (voice model Supertonic-3, Korean ASR checker, fonts if the system has no Noto CJK)
2. Write a card JSON (see `cards/2026-11-07_gg-youth-basic-income-q4.json`), then
   `python3 radar/make.py CARD.json OUT_DIR [--hook target|deadline|check] [--voice M2|F1]`
3. OUT_DIR gets `video.mp4` (25–40 s, 1080x1920), `thumb.jpg` (custom Shorts thumbnail), `copy.txt`
   (YouTube title/description/tags/pinned comment, Instagram and TikTok captions), `qa.png`
   (first frame, end of every scene, thumbnail) and `manifest.json` (`qa.pass`, `qa.issues`, voice check).

## Card rules (the facts are the product: never guess)
- Every number, date, condition and exclusion must come from the official notice (government/city site,
  복지로, 정부24, 고용24, 잡아바 …) or, if the official page will not open, from at least two news
  reports that agree. Record what was checked in `verified`. If a fact cannot be confirmed, leave the topic.
- Only programs that are open now or open within 7 days, with a deadline at least 3 days after publish_date
  (or 상시 신청). Nationwide or big-region (서울/경기/인천/부산 …) programs first.
- `beats.<scene>[].say` is what the voice reads: write numbers in Hangul (이천일 년, 이십오만 원, 십이월 일일,
  오후 여섯 시). `cap` is the caption with digits. `expect` lists digit strings the speech checker must hear.
- Scenes: hook (2 beats: audience, then amount), check (2–5 conditions; `bad: true` = exclusion),
  steps (2–4), deadline (1 beat, omit for 상시), cta (2 beats, keep as in the example).
- Hooks (A/B/C test): `target` (audience big), `deadline` (D-N big; give `hook_beats.deadline` voice lines,
  e.g. "마감 이십사 일 전, …"), `check` (3초 체크). Thumbnail and first frame always show audience + amount.
- Title ≤ 60 chars: audience + amount + action + (M/D 마감). No exaggeration ("누구나", "무조건" are banned)
  and no promise that the viewer will be selected.

## Thumbnail / click design
- Yellow band: who it is for (the viewer recognises themself), huge amount, red deadline + D-N badge.
- The first video frame repeats the same three facts, so a viewer who taps the thumbnail sees them instantly.

## Title hooks (since 2026-11-06)
- Write 5 `title_candidates` per card, one per pattern: `loss` (신청 안 하면 못 받아요 / 지나면 못 받아요), `surprise` (소득·취업 상관없이…),
  `question` (…세요? …받으셨어요?), `countdown` (마감 N일 남았어요), `check` (…면 나와요, 아직 안 받으셨죠?).
- Pick the strongest as `title` + `title_pattern`: audience in the first ~8 chars, amount in the first ~20, one loss/surprise/urgency element,
  ≤ 40 chars where possible (Shorts cuts the rest). Every word must be true for the verified facts; no 누구나/무조건/100%.
- Rotate patterns so each gets tried; the daily run records `title_pattern` per video and compares 48 h views and "계속 시청함" by pattern.
- `hook_line` (≤ 16 chars) is the same hook in short form: it goes on the thumbnail (yellow line) and should match the first spoken line.

## Opening hold
The video opens on the thumbnail itself (slow zoom-out) while the first hook line is spoken, then cuts to the hook scene.
Length = `intro_s` (default 1.2 s, `--intro` overrides, 0 = off), never longer than the first voice line or 2 s.
Because frame 0 = the thumbnail, "동영상에서 선택 → first frame" in YouTube Studio gives the designed thumbnail even without custom-thumbnail rights.
