"""Fast checks (no rendering): python3 -m pytest -q tests  (or: python3 tests/test_radar.py)"""
import glob, json, os, sys, copy
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'radar'))
from validate_card import validate
from run import kit_caption

CARDS = sorted(glob.glob(os.path.join(ROOT, 'radar', 'cards', '*.json')))
BASE = json.load(open(next(c for c in CARDS if 'basic-pension' in c)))


def test_all_real_cards_pass():
    for c in CARDS:
        E, _ = validate(json.load(open(c)))
        assert not E, (c, E)


def test_catches_mistakes():
    c = copy.deepcopy(BASE)
    c['beats']['hook'][0]['say'] = '65세 이상'
    c['title'] = '누구나 받는 기초연금'
    c['deadline'] = c['publish_date']
    c['verified'] = {'note': 'x'}
    E, _ = validate(c)
    joined = ' '.join(E)
    for frag in ('Arabic digits', '누구나', 'less than 3 days'):
        assert frag in joined, (frag, E)


def test_past_publish_date():
    import datetime as dt
    E, _ = validate(copy.deepcopy(BASE), today=dt.date(2030, 1, 1))
    assert any('in the past' in e for e in E)


def test_missing_field_stops():
    c = copy.deepcopy(BASE); c.pop('facts')
    E, _ = validate(c)
    assert E == ['missing field: facts']


def test_kit_caption_strips_links_and_limits_tags():
    s = kit_caption('제목\n\n본문 https://example.com/x\n\n#a #b #c #d #e #f #shorts')
    assert 'http' not in s and '#shorts' not in s
    assert s.count('#') == 5


def test_kit_from_copy_file():
    import subprocess
    f = sorted(glob.glob(os.path.join(ROOT, 'radar', 'videos', '*.txt')))[-1]
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'radar', 'run.py'), 'kit', f], capture_output=True, text=True)
    d = json.loads(r.stdout)
    assert d['ok'] and 'http' not in d['ig_caption'] and d['tt_caption'].count('#') <= 5


def test_evidence_required_and_matched():
    c = copy.deepcopy(BASE); c['publish_date'] = '2026-11-17'
    E, _ = validate(c)
    assert any('evidence missing' in e for e in E)
    q = ('2026년 기준연금액 월 349,700원. 단독가구 월 247만원, 부부가구 월 395.2만원. 근로소득 기본공제액 월 116만원. '
         '국민연금 월 524,550원 이하. 부부 각 20% 감액. 만 65세 이상. 1개월 전부터. 매월 25일. 문의 129, 1355. 2026.1~12월')
    c['evidence'] = [{'url': 'https://basicpension.mohw.go.kr/', 'quote': q}]
    assert validate(c)[0] == []
    c['evidence'][0]['quote'] = q.replace('349,700', '339,700')
    assert any('349700' in e for e in validate(c)[0])


def test_number_forms_match():
    from validate_card import num_values
    assert set(num_values('34.97만 원')) == set(num_values('349,700원'))
    assert set(num_values('11월 30일')) == set(num_values('2026.11.30'))
    assert ('n', 3952000.0) in num_values('395만 2천원')


if __name__ == '__main__':
    for k, f in list(globals().items()):
        if k.startswith('test_'):
            f(); print('ok', k)
