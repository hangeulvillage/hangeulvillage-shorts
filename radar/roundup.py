"""Weekly roundup post: "지금 신청 가능한 지원금 총정리" from cards that already passed the fact gate.

Usage: python3 radar/roundup.py OUT_DIR --today YYYY-MM-DD [--links LINKS.json] [--naver]
  LINKS.json: {"<card id>": "<Tistory post URL>", ...} (from radar_videos.blog.url) -> each program links to its own post.
Writes OUT_DIR/post.html, post.json {title, labels, description, qa}, preview.html.
No new facts: every line comes from a card verified within the last 30 days whose deadline is still ahead (or 상시).
Why: one evergreen, regularly refreshed hub post per week adds blog volume for AdSense and links the single posts together.
"""
import argparse, datetime as dt, glob, json, os, re
import blog
from blog import E, h2, p, table, deadline_text, ACC, INK, SUB, BG, LINE

HERE = os.path.dirname(os.path.abspath(__file__))


def pick(today, max_age=30):
    by_prog = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'cards', '*.json'))):
        c = json.load(open(f))
        if c.get('format') == 'ranking':
            continue
        at = (c.get('verified') or {}).get('at')
        if not at or (today - dt.date.fromisoformat(at)).days > max_age:
            continue
        d = c.get('deadline')
        if d and dt.date.fromisoformat(d) <= today:
            continue
        key = re.sub(r'\s*\([^)]*\)', '', c['program']).strip()
        by_prog[key] = c  # later cards win
    far = dt.date(9999, 1, 1)
    return sorted(by_prog.values(), key=lambda c: (dt.date.fromisoformat(c['deadline']) if c.get('deadline') else far, c['program']))


def build(cards, today, links):
    n = len(cards)
    rows = ''.join(
        f'<tr><td style="padding:9px 10px;border-bottom:1px solid {LINE}"><b>'
        + (f'<a href="{E(links[c["id"]])}" style="color:{ACC}">{E(c["program"])}</a>' if c['id'] in links else E(c['program']))
        + f'</b></td><td style="padding:9px 10px;border-bottom:1px solid {LINE};color:{INK}">{E(c["audience"])}</td>'
        f'<td style="padding:9px 10px;border-bottom:1px solid {LINE};color:{INK}">{E(c["amount"])}</td>'
        f'<td style="padding:9px 10px;border-bottom:1px solid {LINE};color:{ACC};white-space:nowrap">'
        f'{E(deadline_text(c) if not c.get("deadline") else f"{dt.date.fromisoformat(c["deadline"]).month}/{dt.date.fromisoformat(c["deadline"]).day} 마감")}</td></tr>'
        for c in cards)
    head = ''.join(f'<th style="text-align:left;padding:9px 10px;background:{BG};color:{ACC};border-bottom:1px solid {LINE}">{h}</th>'
                   for h in ('지원금', '대상', '금액', '마감'))
    out = [p(f'{today.month}월 {today.day}일 기준으로 <b>지금 신청할 수 있는 지원금 {n}가지</b>를 마감이 가까운 순서로 모았어요. '
             '모두 공식 공고에서 대상·금액·마감을 확인한 내용이에요.'),
           f'<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;border:1px solid {LINE};margin:12px 0 24px;font-size:.95em">'
           f'<tr>{head}</tr>{rows}</table></div>']
    srcs = []
    for c in cards:
        steps = c['beats'].get('steps', [])
        apply = steps[0]['main'] if steps else c['facts'].get('신청', '')
        out.append(h2(c['program']))
        out.append(table([('대상', E(f'{c["audience"]} · {c["audience_sub"]}')), ('금액', f'<b>{E(c["amount"])}</b>'),
                          ('기한', E(deadline_text(c))), ('신청', E(apply)), ('확인일', E(c['verified']['at']))]))
        if c['id'] in links:
            out.append(p(f'👉 <a href="{E(links[c["id"]])}" style="color:{ACC};font-weight:700">{E(c["program"])} 자세히 보기</a>'))
        srcs += c.get('source_urls', [])
    urls = ''.join(f'<li><a href="{E(u)}" rel="nofollow noopener" target="_blank">{E(u)}</a></li>' for u in dict.fromkeys(srcs))
    out.append(h2('출처') + (f'<ul style="line-height:1.8">{urls}</ul>' if urls else ''))
    out.append(f'<div style="margin-top:28px;padding:14px 16px;background:#f9fafb;border-radius:10px;color:{SUB};font-size:.92em;line-height:1.7">'
               '※ 정보 제공용 글입니다. 조건과 일정은 바뀔 수 있으니 신청 전 공고 원문을 꼭 확인하세요. 매주 새로 확인해 갱신해요.<br>'
               '💬 댓글에 "나이 + 사는 지역"을 남기시면 받을 수 있는 지원금을 찾아 답글로 알려드려요.</div>')
    title = f'지금 신청 가능한 지원금 총정리 {n}가지 ({today.month}월 {today.day}일 기준)'
    if blog.NAVER:
        title = f'{today.month}월 지원금 신청 총정리 {n}가지, 대상·금액·마감 한눈에 ({today.month}/{today.day} 기준)'
    return title, ''.join(out)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('--today', required=True)
    ap.add_argument('--links', default=None); ap.add_argument('--naver', action='store_true')
    a = ap.parse_args(); blog.NAVER = a.naver
    today = dt.date.fromisoformat(a.today)
    links = json.load(open(a.links)) if a.links else {}
    cards = pick(today)
    issues = [] if len(cards) >= 3 else [f'only {len(cards)} open programs: need at least 3 for a roundup']
    title, body = build(cards, today, links)
    body = f'<div style="font-size:16px;max-width:720px">{body}</div>'
    for bad in ('누구나', '무조건', '100%', '전원 지급'):
        if bad in title + re.sub(r'<[^>]+>', ' ', body): issues.append(f'banned word: {bad}')
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, 'post.html'), 'w').write(body)
    meta = {'title': title, 'labels': ['지원금', '정부지원금', '지원금총정리', '신청방법', '마감임박'],
            'description': f'{today.month}월 {today.day}일 기준 신청 가능한 지원금 {len(cards)}가지: 대상·금액·마감 정리',
            'programs': [c['id'] for c in cards], 'qa': {'pass': not issues, 'issues': issues}}
    json.dump(meta, open(os.path.join(a.out, 'post.json'), 'w'), ensure_ascii=False, indent=1)
    open(os.path.join(a.out, 'preview.html'), 'w').write(
        f'<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)}</title>'
        f'<body style="margin:0;font-family:system-ui,\'Noto Sans KR\',sans-serif"><div style="max-width:760px;margin:0 auto;padding:24px 16px">'
        f'<h1 style="font-size:1.6em;color:{INK};line-height:1.4">{E(title)}</h1>{body}</div>')
    print(json.dumps({'title': title, 'programs': len(cards), 'qa_pass': not issues, 'issues': issues}, ensure_ascii=False))


if __name__ == '__main__':
    main()
