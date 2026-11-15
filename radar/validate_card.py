"""Validate a 지원금 레이더 card BEFORE rendering (structured check + clear error list).

Usage: python3 radar/validate_card.py CARD.json [--today YYYY-MM-DD]
Exit code 0 = ok (warnings may be printed), 1 = errors. Prints JSON {ok, errors, warnings}.
Catches the mistakes that are cheap to catch here and expensive after rendering/uploading:
missing fields, deadline too close or before publish_date, Arabic digits in spoken lines,
numbers in the title/headline that appear nowhere in the facts, missing verification notes.
"""
import argparse, datetime as dt, json, os, re, sys

SINGLE_REQ = ['id', 'program', 'audience', 'audience_sub', 'amount', 'publish_date', 'beats', 'facts', 'source', 'verified', 'title']
RANK_REQ = ['id', 'program', 'publish_date', 'beats', 'facts', 'source', 'items', 'headline', 'rank_by', 'title']
BANNED = ['누구나', '무조건', '100%', '전원 지급', '100프로']


def nums(s):
    """Numbers as they would be compared: '34.97', '349,700' -> '349700', '1/3'."""
    out = set()
    for m in re.findall(r'\d+(?:[.,/]\d+)*', s or ''):
        out.add(m.replace(',', ''))
    return out


EVIDENCE_FROM = dt.date(2026, 11, 17)  # cards published from this date must quote the official text
SNAPSHOT_FROM = dt.date(2026, 11, 18)  # ... and keep the raw page text the quote was copied from


def squash(t):
    """Compare text ignoring spacing, line breaks and bullet/quote marks."""
    return re.sub(r'[\s\u00a0·•\-–—"\'“”‘’()\[\]]+', '', t or '')


def num_values(text):
    """Comparable values in a text: dates -> ('d', month, day); amounts -> ('n', value) with 만/천 expanded.
    '349,700원' and '34.97만 원' give the same value; '2026.11.30', '11월 30일' and '11.30' the same date."""
    t = re.sub(r'(?<=\d),(?=\d{3})', '', text or '')
    out = []
    def date(m, mo, d):
        mo, d = int(mo), int(d)
        if 1 <= mo <= 12 and 1 <= d <= 31:
            out.append(('d', mo, d)); return ' '
        return m.group(0)
    t = re.sub(r'(?<![\d.])(\d{4})\s*[.\-/년]\s*(\d{1,2})\s*[.\-/월]\s*(\d{1,2})\s*일?', lambda m: date(m, m.group(2), m.group(3)), t)
    t = re.sub(r'(?<![\d.])(\d{1,2})\s*(?:월\s*|[./])(\d{1,2})\s*일?(?![\d.]|\s*만)', lambda m: date(m, m.group(1), m.group(2)), t)
    for m in re.finditer(r'(?<![\d.])(\d+(?:\.\d+)?)\s*(억|만|천)?(?:\s*(\d+)\s*천)?', t):
        v = float(m.group(1)); unit = {'억': 1e8, '만': 1e4, '천': 1e3}.get(m.group(2), 1)
        v = v * unit + (float(m.group(3)) * 1e3 if m.group(3) else 0)
        out.append(('n', round(v, 2)))
    return out


def check_evidence(card, E, W):
    """Every number/date in the facts (and amount, deadline) must appear in a quoted sentence from the source."""
    ev = card.get('evidence') or []
    pub = dt.date.fromisoformat(card['publish_date'])
    if not ev:
        (E if pub >= EVIDENCE_FROM else W).append(
            'evidence missing: add [{"url", "quote"}] with the official sentences the facts come from')
        return
    have = set()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for i, e in enumerate(ev):
        if not e.get('url') or not e.get('quote'):
            E.append('evidence item needs url and quote'); continue
        # anti-fabrication: the quote must be found word for word in the saved raw page text
        snap = e.get('snapshot')
        if not snap:
            (E if pub >= SNAPSHOT_FROM else W).append(
                f'evidence[{i}] has no snapshot: save the page text (get_page_text / WebFetch output) to radar/evidence/<card id>/<n>.txt')
        else:
            path = snap if os.path.isabs(snap) else os.path.join(root, snap)
            if not os.path.exists(path):
                E.append(f'evidence[{i}] snapshot file not found: {snap}')
            else:
                page = open(path, encoding='utf-8').read()
                if len(page) < 800:
                    E.append(f'evidence[{i}] snapshot is only {len(page)} chars: save the whole page text, not an excerpt')
                if squash(e['quote']) not in squash(page):
                    E.append(f'evidence[{i}] quote is not in its page snapshot word for word: copy it exactly from the page')
        have.update(num_values(e['quote']))
    texts = [str(v) for v in card['facts'].values()] + [str(card.get('amount') or '')]
    for it in card.get('items', []):
        texts += [str(it.get('amount', '')), str(it.get('who', ''))]
    need = []
    for tx in texts:
        need += num_values(tx)
    for d in [card.get('deadline')] + [it.get('deadline') for it in card.get('items', [])]:
        if d:
            dd = dt.date.fromisoformat(d); need.append(('d', dd.month, dd.day))
    missing = []
    for x in need:
        if x not in have and x not in missing:
            missing.append(x)
    if missing:
        shown = ', '.join(f'{x[1]}/{x[2]}' if x[0] == 'd' else ('%g' % x[1]) for x in missing[:12])
        (E if pub >= EVIDENCE_FROM else W).append(
            f'numbers in facts not found in any evidence quote: {shown} — quote the official sentence or fix the fact')


def validate(card, today=None):
    E, W = [], []
    ranking = card.get('format') == 'ranking'
    for k in (RANK_REQ if ranking else SINGLE_REQ):
        if k not in card or card[k] in (None, '', [], {}):
            E.append(f'missing field: {k}')
    if E:
        return E, W
    try:
        pub = dt.date.fromisoformat(card['publish_date'])
    except ValueError:
        return [f'publish_date not YYYY-MM-DD: {card["publish_date"]}'], W
    if today and pub < today:
        E.append(f'publish_date {pub} is in the past')

    def check_deadline(d, label):
        if not d:
            return
        try:
            dd = dt.date.fromisoformat(d)
        except ValueError:
            E.append(f'{label}: deadline not YYYY-MM-DD: {d}'); return
        if (dd - pub).days < 3:
            E.append(f'{label}: deadline {dd} is less than 3 days after publish_date {pub}')

    if ranking:
        ranks = sorted(it.get('rank') for it in card['items'])
        if ranks != list(range(1, len(ranks) + 1)):
            E.append(f'ranking: ranks must be 1..N, got {ranks}')
        order = [b.get('rank') for b in card['beats'].get('items', [])]
        if sorted(order) != ranks:
            E.append('ranking: beats.items must cover every rank once')
        elif order and order[-1] != 1:
            E.append('ranking: #1 must be the last item beat')
        for it in card['items']:
            for k in ('name', 'who', 'amount'):
                if not it.get(k):
                    E.append(f'ranking item {it.get("rank")}: missing {k}')
            check_deadline(it.get('deadline'), f'item {it.get("name")}')
            if it.get('name') and not any(it['name'] in k for k in card['facts']):
                W.append(f'ranking item {it["name"]} has no facts entry')
    else:
        check_deadline(card.get('deadline'), 'card')

    # beats: every beat has say + cap; spoken lines use Hangul numerals
    for scene, beats in card['beats'].items():
        for i, b in enumerate(beats):
            if not b.get('say') or not b.get('cap'):
                E.append(f'beat {scene}[{i}] needs say and cap')
                continue
            if re.search(r'\d', b['say']):
                E.append(f'beat {scene}[{i}] say has Arabic digits (TTS reads them badly): "{b["say"][:40]}"')
            for x in b.get('expect', []):
                if str(x) not in b['cap']:
                    W.append(f'beat {scene}[{i}] expect "{x}" not in its cap')

    # title / headline: length, banned words, numbers must exist in the verified facts
    title = card['title']
    if len(title) > 60:
        E.append(f'title is {len(title)} chars (max 60)')
    facts_text = ' '.join(str(v) for v in card['facts'].values()) + ' ' + ' '.join(
        f'{it.get("amount", "")} {it.get("deadline", "")}' for it in card.get('items', []))
    facts_text += ' ' + str(card.get('amount', '')) + ' ' + str(card.get('deadline_text', ''))
    fact_nums = nums(facts_text) | nums(json.dumps(card.get('items', []), ensure_ascii=False))
    # same values in other units/forms: 349700 -> 34.97 (만 원), 2026-12-01 -> 12/1, D-N days
    for n in list(fact_nums):
        try:
            v = float(n)
        except ValueError:
            continue
        if v >= 10000:
            man = v / 10000
            fact_nums.add(('%.2f' % man).rstrip('0').rstrip('.'))
    for a_, b_ in re.findall(r'(\d+)만\s*(\d)천', facts_text):  # 313만 5천 -> 313.5
        fact_nums.add(f'{a_}.{b_}')
    dates = [card.get('deadline')] + [it.get('deadline') for it in card.get('items', [])]
    dates += re.findall(r'\d{4}-\d{2}-\d{2}', facts_text + ' ' + json.dumps(card.get('verified', {}), ensure_ascii=False))
    for d in filter(None, dates):
        try:
            dd = dt.date.fromisoformat(d)
        except ValueError:
            continue
        fact_nums.update({f'{dd.month}/{dd.day}', str(dd.month), str(dd.day), str((dd - pub).days)})
    head = ' '.join(h.replace('{', '').replace('}', '') for h in card.get('headline', []) or [])
    for label, text in (('title', title), ('headline', head), ('hook_line', card.get('hook_line', ''))):
        for w in BANNED:
            if w in text:
                E.append(f'{label} uses exaggeration "{w}"')
        for n in nums(text):
            if n in ('1', '2', '3', '4', '5') and ranking:  # TOP 5 / ranks
                continue
            if n not in fact_nums and not any(n in f for f in fact_nums):
                W.append(f'{label} number "{n}" not found in facts — check it')
    if card.get('headline') and len(card['headline']) >= 2:
        l1, l2 = card['headline'][0], card['headline'][1].replace('{', '').replace('}', '')
        if len(l1) > 16: W.append(f'headline line 1 is {len(l1)} chars (aim ≤ 14)')
        if len(l2) > 14: W.append(f'headline line 2 is {len(l2)} chars (aim ≤ 12)')

    # verification record
    v = card.get('verified') or {}
    if not v.get('at'):
        E.append('verified.at missing (date the facts were checked)')
    if not (v.get('official_page_opened') or len(card.get('source_urls', [])) >= 2):
        W.append('no official page opened and fewer than 2 source_urls: check the fact gate')
    if not card.get('source_urls'):
        W.append('source_urls empty (the blog post shows no source links)')
    check_evidence(card, E, W)
    return E, W


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('card'); ap.add_argument('--today', default=None)
    a = ap.parse_args()
    card = json.load(open(a.card))
    today = dt.date.fromisoformat(a.today) if a.today else None
    E, W = validate(card, today)
    print(json.dumps({'ok': not E, 'errors': E, 'warnings': W}, ensure_ascii=False, indent=1))
    sys.exit(0 if not E else 1)


if __name__ == '__main__':
    main()
