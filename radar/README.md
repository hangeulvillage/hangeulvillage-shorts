# 지원금 레이더 shorts pipeline

Korean info shorts about government/local subsidies (YouTube @jiwongeumradar, channel id UCf_4uh8PjZKkUBU5ncjQJEg).
Separate brand from Hangeul Village; it only shares this repository.

1. `bash radar/setup.sh` (voice model Supertonic-3, Korean ASR checker, fonts if the system has no Noto CJK)
2. Write a card JSON (see `cards/2026-11-07_gg-youth-basic-income-q4.json`), then
   `python3 radar/make.py CARD.json OUT_DIR [--hook target|deadline|check] [--voice M5 (default) | M1-M5 | F1-F5]`
3. OUT_DIR gets `video.mp4` (25–40 s, 1080x1920), `thumb.jpg` (custom Shorts thumbnail), `copy.txt`
   (YouTube title/description/tags/pinned comment, Instagram and TikTok captions), `qa.png`
   (first frame, end of every scene, thumbnail) and `manifest.json` (`qa.pass`, `qa.issues`, voice check).

## Run (since 2026-11-16: use the runner, not make.py directly)
**Precedence:** where a scheduled-task prompt still says `python3 radar/make.py CARD OUT …` or `python3 radar/blog.py …`,
run the matching `run.py` command instead (same output files, plus validation and bundle.json). For the phone kit captions
use `python3 radar/run.py kit radar/videos/<date>_<slug>.txt`. If `yt_readback.js` says ok:false but the fields look right
on screen, trust the screen and continue (the dialog DOM can change); note it as a lesson.
1. Write the card (fact gate first), then:
   `python3 radar/run.py make radar/cards/CARD.json /tmp/radar_out --today YYYY-MM-DD`
   - Validates the card first (`validate_card.py`): missing fields, deadline < publish+3 days, Arabic digits in `say`,
     exaggeration words, numbers in title/headline not found in facts, missing `verified.at`. Errors stop it before rendering.
   - Renders (one automatic retry on a non-card failure) and writes `bundle.json`: YouTube title/description/tags/pinned
     comment, phone-kit captions (`kit.ig_caption`, `kit.tt_caption`: links removed, ≤ 5 hashtags), files, QA.
   - Exit 0 = ready to upload. Exit 1 = read the printed JSON (`step`: validate / render / qa) and fix; never upload past it.
2. After the YouTube upload gives the video id:
   `python3 radar/run.py blog radar/cards/CARD.json /tmp/radar_out/blog --yt VIDEO_ID` -> `tistory/` and `naver/` posts.
3. Browser helpers: `tools/browser/tistory_post.js` (body insert + length check), `tools/browser/yt_readback.js`
   (check the upload form really holds the title/description/not-for-kids before 예약).
4. Before any commit: `python3 tests/test_radar.py` and `bash tools/check_secrets.sh`.

## Card rules (the facts are the product: never guess)
- **Evidence (required for cards published from 2026-11-17):** `"evidence": [{"url": "<official page>", "quote": "<the exact
  sentences copied from it>"}]`. `validate_card.py` checks that EVERY number and date in `facts`, `amount`, `deadline`
  (and ranking items) appears in some quote — 349,700원 = 34.97만 원 and 2026.11.30 = 11월 30일 count as the same. A number
  with no quote is an error: copy the official sentence that contains it, or fix the fact. Quote official text only
  (news quotes only when the official page will not open, and then from 2 agreeing reports).
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

## Upload timing (since 2026-11-09, asked by the account owner: find the best upload time/interval from data and switch to it)
State lives in `radar_config.timing_test` (phase, history). The daily run collects data and applies the rules below by itself.
- Data (every run): for each of our public YouTube videos up to 4 days old, append `{at, age_h, views}` to `radar_videos.<id>.yt_views_log`
  (age from `scheduled_for`). Once a video has readings on both sides of 48 h, store `views_48h` (linear interpolation), `slot` (HH:MM KST)
  and `weekday`. Videos made public by hand at an unknown time (gg-youth-basic-income-2026q4) are left out.
- Phase `slot`: `publish_slots_kst` rotates 07:40 / 12:10 / 19:40 (slot_next). When every slot has >= 4 videos with `views_48h`, compare the
  median per slot. If the best median is >= 1.3x every other slot's median: `publish_slots_kst = [best, best, challenger]` (challenger = the
  runner-up slot; slot_next 0) and phase `interval`. No clear winner: keep rotating and decide again after 3 more videos per slot.
- Phase `interval`: `per_day` 2 for 7 days. YouTube gets both videos (both publish_date tomorrow, the two best different times);
  Facebook/TikTok still post one per day (the one in the better slot; the other gets fb_skipped "1 per day"). After 7 days compare the
  median `views_48h` per video and the average views per day (sum of `views_48h` / days) with the 7 days before. Keep `per_day` 2 only if
  the per-video median stayed >= 80 % of before AND views per day rose; otherwise back to 1. Then phase `steady`.
  If two topics cannot pass the fact gate on a day, make one: never lower the fact gate for volume.
- Phase `steady` (and `interval`): every 7 days, if the challenger slot has >= 4 videos and its median is >= 1.3x the best slot's, swap them;
  otherwise try the runner-up or a time 2 h from the best as the next challenger.
- Topic drives views more than time: use medians and the minimum counts above, never decide from one video; note outliers (>= 3x median) in
  `timing_test.notes`. If YouTube Studio 분석 → 시청자 shows "시청자가 YouTube를 이용하는 시간대", use it only as a tie-breaker.
- Every change to `publish_slots_kst` or `per_day`: append `{at, from, to, reason with the numbers}` to `timing_test.history`, say it in the run
  message and send a PushNotification.

## Viral structure (since 2026-11-14, asked by the account owner: "하루에 터지는 쇼츠 구조를 파악하고 같은 구조로")
Read-only study on 2026-11-14 of this week's top subsidy shorts on YouTube (e.g. 4.3만 views in 1 day, 3.2만 in 4 days,
1.8천 in 2 days; only titles, view counts and a few frames were looked at, nothing downloaded or reused). What they share:
a fixed 2-line headline at the top for the whole video, the picture changes every 3–6 s, news/loss framing
("바뀝니다", "오늘부터", "다시 나오기 시작", "15만 원 날려요"), a closing summary screen people can capture, 45–70 s.
Every card now uses it (structure only; our content, facts and design stay ours):
- `"structure": "viral"` (or `--structure viral`): fixed headline banner, background shift per scene, closing
  "한눈에 정리" recap card (+2.6 s, then the video loops). Duration limit 48 s.
- `"headline": [line1, line2]`: line1 = who, ≤ 14 chars (e.g. "만 65세 이상 부모님 계신 분"); line2 = the hook, ≤ 12 chars,
  one of: loss ("신청 안 하면 0원이에요"), news ("11월부터 이렇게 바뀝니다"), opened ("오늘부터 신청 시작"),
  closing ("마감 D-5, 아직 안 하셨나요"). Must be literally true for this program (the fact gate applies to it too);
  rotate the line2 type and record it as `headline_type` (loss|news|opened|closing).
- `"style"`: rotate navy → ember → forest by publish_date (day-of-year % 3) so videos do not all look the same.
- Topic choice: when two programs are equally solid, prefer the one with news value (just changed, opened in the
  last 3 days, or closes within 10 days).
- Weekly snapshot: compare views_48h by headline_type and style once each has ≥ 3 videos; keep the best, still
  try the others once a week.

## Weekly TOP 5 ranking (since 2026-11-15, asked by the account owner: "TOP 5 순위 주 1회 일반 영상 대신")
When the card's publish_date is a **Monday**, make a ranking card instead of a single-program card
(example: see the format below; renderer: `"format": "ranking"`, always uses the viral structure + a closing TOP-N recap).
- 4–5 programs ranked by ONE objective criterion written in `rank_by` ("마감 임박순 · M월 D일 기준" or "금액 큰 순"),
  never by opinion. Rank 1 = most urgent / biggest.
- Every item passes the same fact gate as a normal card, re-checked on its official page in this run (items from earlier
  cards may be reused only after that re-check). Deadline ≥ 3 days after publish_date (or 상시). Mixed regions are fine;
  put the region in `who`.
- `items`: [{rank, name, who, amount, deadline (YYYY-MM-DD or null), apply}]. `facts`: one entry per program + "신청".
- `beats.hook` (2 beats: what the list is, "일 위는 마지막에 공개할게요"), `beats.items` (one beat per item, each with
  `rank`, in PLAYBACK order: shuffled, e.g. 4,2,5,3,1 — #1 always last; make.py refuses otherwise), `beats.cta` as usual.
- `headline`: [line1 ≤ 14 chars, line2 with the key word in {braces}, e.g. "마감 임박 {TOP 5}"] — braces = accent colour.
- Title pattern "countdown"; title ≤ 40 chars, e.g. "이번 달 놓치면 끝, 마감 임박 지원금 TOP 5". Length 45–60 s is fine.
- In radar_videos record format "ranking"; compare its views_48h with the single cards of the same week in the report.
