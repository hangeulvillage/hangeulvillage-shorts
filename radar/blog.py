"""지원금 레이더 blog post: card JSON -> post.html (body for Blogger) + post.json (title, labels, description).

Usage: python3 radar/blog.py CARD.json OUT_DIR [--yt VIDEO_ID]
Inline styles only (Blogger keeps them; <style> blocks can be stripped). Every fact comes from the card,
which already passed the fact gate; nothing here adds numbers.
"""
import argparse, datetime as dt, html, json, os, re

E = html.escape
ACC = '#c2410c'; INK = '#1f2937'; SUB = '#6b7280'; BG = '#fff7ed'; LINE = '#fed7aa'

def ddate(s):
    return dt.date.fromisoformat(s) if s else None

def deadline_text(card, d=None):
    d = d if d is not None else ddate(card.get('deadline'))
    if not d: return '상시 신청'
    t = f' {card["deadline_time"]}' if card.get('deadline_time') else ''
    wd = '월화수목금토일'[d.weekday()]
    return f'{d.year}년 {d.month}월 {d.day}일({wd}){t}까지'

def table(rows):
    tr = ''.join(f'<tr><th style="text-align:left;white-space:nowrap;padding:10px 14px;background:{BG};color:{ACC};'
                 f'border-bottom:1px solid {LINE};width:22%">{E(k)}</th>'
                 f'<td style="padding:10px 14px;border-bottom:1px solid {LINE};color:{INK}">{v}</td></tr>' for k, v in rows)
    return f'<table style="width:100%;border-collapse:collapse;border:1px solid {LINE};border-radius:12px;overflow:hidden;margin:12px 0 24px">{tr}</table>'

def h2(t):
    return f'<h2 style="font-size:1.3em;color:{INK};border-left:5px solid {ACC};padding-left:10px;margin:32px 0 12px">{E(t)}</h2>'

def p(t, color=INK):
    return f'<p style="line-height:1.8;color:{color};margin:8px 0">{t}</p>'

def video(yt):
    if not yt: return ''
    return (f'<p style="text-align:center;margin:16px 0"><iframe width="315" height="560" src="https://www.youtube.com/embed/{E(yt)}" '
            'title="30초 요약 영상" style="max-width:100%;border:0;border-radius:12px" allowfullscreen="true"></iframe></p>')

def footer(card):
    v = card.get('verified', {})
    urls = ''.join(f'<li><a href="{E(u)}" rel="nofollow noopener" target="_blank">{E(u)}</a></li>' for u in card.get('source_urls', []))
    return (h2('출처') + p(f'{E(card["source"])}' + (f' · 확인일 {E(v["at"])}' if v.get('at') else '')) +
            (f'<ul style="line-height:1.8">{urls}</ul>' if urls else '') +
            f'<div style="margin-top:28px;padding:14px 16px;background:#f9fafb;border-radius:10px;color:{SUB};font-size:.92em;line-height:1.7">'
            '※ 정보 제공용 글입니다. 조건과 일정은 바뀔 수 있으니 신청 전 공고 원문을 꼭 확인하세요.<br>'
            '💬 댓글에 "나이 + 사는 지역"을 남기시면 받을 수 있는 지원금을 찾아 답글로 알려드려요.</div>')

def single(card, yt):
    b = card['beats']; d = ddate(card.get('deadline'))
    steps = b.get('steps', [])
    rows = [('대상', E(f'{card["audience"]} · {card["audience_sub"]}')), ('금액', f'<b>{E(card["amount"])}</b>'),
            ('기한', E(deadline_text(card))), ('신청', E(steps[0]['main'] if steps else card['facts'].get('신청', '')))]
    out = [p(f'<b>{E(card["program"])}</b>, 핵심만 정리했어요. 대상과 금액, 신청 방법, 마감일을 공식 공고 기준으로 확인했습니다.'),
           f'<div style="background:{BG};border:1px solid {LINE};border-radius:14px;padding:6px 14px 2px;margin:16px 0">'
           f'<p style="font-weight:700;color:{ACC};margin:10px 0 0">한눈에 보기</p>{table(rows)}</div>', video(yt)]
    checks = b.get('check', [])
    if checks:
        out.append(h2('누가 받을 수 있나요?'))
        li = ''.join(f'<li style="margin:6px 0">{"❌" if c.get("bad") else "✅"} <b>{E(c["main"])}</b>'
                     + (f'<br><span style="color:{SUB}">{E(c["sub"])}</span>' if c.get('sub') else '') + '</li>' for c in checks)
        out.append(f'<ul style="list-style:none;padding-left:0;line-height:1.7">{li}</ul>')
    if steps:
        out.append(h2('신청 방법'))
        li = ''.join(f'<li style="margin:8px 0"><b>{E(s["main"])}</b>' + (f'<br><span style="color:{SUB}">{E(s["sub"])}</span>' if s.get('sub') else '') + '</li>' for s in steps)
        out.append(f'<ol style="line-height:1.7;padding-left:22px">{li}</ol>')
    out.append(h2('자세한 조건'))
    out.append(table([(k, E(v)) for k, v in card['facts'].items()]))
    if d:
        out.append(h2('마감일'))
        out.append(p(f'<b style="color:{ACC}">{E(deadline_text(card))}</b> 신청해야 해요. 마감이 가까우면 접속이 몰릴 수 있으니 미리 신청하세요.'))
    out.append(footer(card))
    dl = f' ({d.month}/{d.day} 마감)' if d else ''
    prog = re.sub(r'\s*\([^)]*\)', '', card['program']).strip()
    title = card.get('blog_title') or f'{prog} 신청 방법·대상·금액 총정리{dl}'
    return title, ''.join(out)

def ranking(card, yt):
    out = [p(f'{E(card["rank_by"])}으로 정리한 <b>{E(card["program"])}</b>입니다. 모두 공식 공고 기준으로 확인했어요.'), video(yt)]
    for it in sorted(card['items'], key=lambda x: x['rank']):
        d = ddate(it.get('deadline'))
        out.append(h2(f'{it["rank"]}위. {it["name"]}'))
        out.append(table([('대상', E(it['who'])), ('금액', f'<b>{E(it["amount"])}</b>'),
                          ('기한', E(deadline_text({}, d)) if d else '상시 신청'), ('신청', E(it.get('apply', '')))]))
        if it['name'] in card['facts']: out.append(p(E(card['facts'][it['name']]), SUB))
    out.append(footer(card))
    return card.get('title') or card['program'], ''.join(out)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('card'); ap.add_argument('out'); ap.add_argument('--yt', default=None)
    a = ap.parse_args(); card = json.load(open(a.card)); os.makedirs(a.out, exist_ok=True)
    title, body = (ranking if card.get('format') == 'ranking' else single)(card, a.yt or card.get('yt_id'))
    body = f'<div style="font-size:16px;max-width:720px">{body}</div>'
    labels = list(dict.fromkeys(card.get('tags', [])[:5] + ['지원금', '정부지원금']))
    desc = re.sub(r'\s+', ' ', f'{card["program"]}: ' + ' / '.join(f'{k} {v}' for k, v in list(card['facts'].items())[:2]))[:150]
    issues = []
    if len(title) > 70: issues.append(f'title {len(title)} chars')
    for bad in ('누구나', '무조건', '100%', '전원 지급'):
        if bad in title + re.sub(r'<[^>]+>', ' ', body): issues.append(f'banned word: {bad}')
    open(os.path.join(a.out, 'post.html'), 'w').write(body)
    json.dump({'title': title, 'labels': labels, 'description': desc, 'qa': {'pass': not issues, 'issues': issues}},
              open(os.path.join(a.out, 'post.json'), 'w'), ensure_ascii=False, indent=1)
    # standalone preview page for proofreading
    open(os.path.join(a.out, 'preview.html'), 'w').write(
        f'<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{E(title)}</title><body style="margin:0;background:#fff;font-family:system-ui,\'Noto Sans KR\',sans-serif">'
        f'<div style="max-width:760px;margin:0 auto;padding:24px 16px"><h1 style="font-size:1.6em;color:{INK};line-height:1.4">{E(title)}</h1>{body}</div>')
    print(json.dumps({'title': title, 'labels': labels, 'qa_pass': not issues, 'issues': issues}, ensure_ascii=False))

if __name__ == '__main__':
    main()
