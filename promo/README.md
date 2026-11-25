# 홍보 영상 엔진 (사진 → 15~25초 세로 홍보 영상)

크몽·숨고 판매용. `python3 promo/make_promo.py BRIEF.json OUT_DIR` → `video.mp4`, `thumb.jpg`, `qa.png`, `manifest.json`.

- 브리프 형식: `make_promo.py` 맨 위 설명, 예시는 `briefs/sample_*.json`.
- 장면: 한 줄 소개 → 강점 2~4개 → 혜택(선택) → 매장 정보와 행동 유도. 사진은 카드 안에서 천천히 확대·이동.
- 음성: AI 성우(Supertonic, F1 여성 / M5 남성). 장면마다 음성인식으로 받아써서 검증해요. 숫자는 한글로 읽어요.
  자연스러운 읽기가 필요하면 `say`에 따로 적어요.
- 음악: 직접 생성한 저작권 없는 배경음(`music`: marimba / lofi / bright). 음성이 나올 때 자동으로 작아져요.
- 음량 -14 LUFS (유튜브·인스타 기준).
- QA: 글자 넘침, 2줄 초과, 길이 12~40초, 음성 유사도 0.75 미만이면 실패(exit 1). 사진이 700px 미만이면 원본 요청 메모.
- 의뢰인이 준 사진과 문구만 써요. 없는 사실(가격·혜택)을 지어내지 않아요.
- 샘플(`sample: true`)에는 "샘플 · 가상 매장" 표시가 붙어요. 샘플 사진은 scikit-image 내장 공개 이미지예요.

## 주문 처리 (어느 Claude 세션이든 이대로)
1. 운영자가 붙여넣은 질문지 답변과 사진을 받는다. 사진은 작업 폴더의 `orders/<YYYYMMDD>_<가게>/`에 저장한다(저장소에 커밋하지 않음: 고객 자료).
2. 답변으로 브리프를 쓴다. 강점 2~4개는 화면용 짧은 문구(한 줄 18자 안팎)로 다듬되, 의미를 바꾸거나 없는 사실을 더하지 않는다.
   `say`에는 숫자를 한글로 풀어 쓴다. 분위기는 차분한=lofi, 밝고 경쾌한=bright, 따뜻한=marimba. 대표 색은 `accent`, 음성 없음은 `voice: "none"`.
3. `python3 promo/make_promo.py brief.json OUT` → exit 0이어야 한다. qa.png와 thumb.jpg를 직접 보고, 글자가 사진 위 중요한 부분을 가리지 않는지 확인한다.
4. video.mp4와 thumb.jpg를 운영자에게 보낸다(SendUserFile). 고객 사진이 700px 미만이면 원본을 다시 받으라고 한 줄 덧붙인다.
5. 패키지별 납품물 (2026-11-16 개편):
   - STANDARD: video.mp4 1편 + thumb.jpg
   - DELUXE: 2편 + 편마다 caption.txt(게시글 문구·해시태그 5개 이하, 링크 없음)
   - PREMIUM: 4편 + caption.txt + `--square`로 만든 video_square.mp4(1080x1080 피드용)
   여러 편은 강점 순서와 한 줄 소개를 바꾼 브리프로 만든다. 같은 문구를 반복하지 않는다.
6. 수정 요청은 브리프만 고쳐서 다시 렌더한다.

## 숨고 (2026-11-24, owner approved)
- Profile: 가게쇼츠공방, 영상 광고 (+ SNS/콘텐츠 마케팅, 썸네일), 활동 지역 인천 남동구, 범위 전국.
- Concept (2026-11-24): "3시간 가게쇼츠". One-liner on every platform: "사진만 주시면 3시간 안에, 광고 같은 가게 홍보 쇼츠를 만들어 드려요. 결제 전 첫 장면 무료 미리보기." Show quality with proof (free preview, samples), never with superlatives.
- Delivery promise (2026-11-24, owner): work starts the moment materials (or payment after the free preview) are confirmed.
  09:00-22:00 KST: delivered within 3 hours; night: by 11:00 next day. Watch task: 크몽·숨고 주문 감시 hourly, 09:37-22:37.
- Prices on 숨고 (견적 costs ~5,000-6,500 캐시 each, no fee on the deal): 맛보기 49,000원 (1편 + 썸네일) /
  추천 119,000원 (3편 + 게시글 문구 + 정사각형) / 월 정기 199,000원 (주 2편, 8편).
  The first quote (설영진, 노인 욕실의자, 2026-11-24) went out at 29,000원 and is honoured if accepted.
- Quote rules (updated 2026-11-24 16:31, owner: "판단기준을 만들고 니가 알아서 견적서 넣어줘, 하루 최대 5건"):
  - Daily cap: 5 quotes total = 숨고 스마트견적 (auto, max 3/day, 24,000캐시/day, resets 09:00) + Claude manual (max 2/day).
  - 스마트견적 (registered 2026-11-24): 영상 광고, 유튜브+SNS, 영상 제작 필요=네, 기간 1회성/1·3·6개월/상담 후 결정, 전국,
    "49,000원부터" + generic text (3 packages, free preview, no on-site filming).
  - SEND when ALL: (a) result can be made from photos/screenshots as a 15-60 s vertical video (가게·제품·서비스 홍보,
    SNS/릴스/쇼츠, 광고 영상); (b) < 5 quotes so far (지정요청 to us: any count); (c) no stated budget under 50,000원;
    (d) no on-site filming, interviews, long-form (> 60 s) editing, motion-graphics/3D/animation work, or event coverage;
    (e) today's manual count < 2. Price: 49,000 if 1편 wanted, 119,000 if several/unclear, 199,000/월 if ongoing ≥ 1 month.
    Tailor the first 2 lines to the request; always offer the free first-scene preview.
  - SKIP: 촬영 필요 (현장/출장/360), 모션그래픽·애니메이션, 롱폼 편집, 5+ quotes, app UI demo series that need screen recording,
    vague SNS-account management with no video.
  - Live chat: when the owner says "숨고", Claude checks, applies the rules, sends or skips, then reports one line each.
  - Scheduled watch tasks still only report and draft (no cash spending from a scheduled run).
  - AUTO-REPLY (owner 2026-11-25 15:42): Claude answers 숨고 customer messages itself (live chat and the hourly watch task),
    from listing facts only; custom price / refund / dispute / unclear -> hold and ask the owner. 크몽 replies stay drafts.
  - Order confirmed -> Claude makes the video(s) at once and sends them to the OWNER first; deliver to the client only after
    the owner confirms. Pre-payment free preview: make it and show the owner, who sends it.
- Kmong: 작업일 2/2/3 -> 1/1/1 and the same 3-hour wording after the first order (editing an approved gig can trigger re-review).
- Kmong keeps 29,000 / 59,000 / 99,000 until 5 reviews, then 39,000 / 79,000 / 129,000.
