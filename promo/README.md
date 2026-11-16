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
