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


if __name__ == '__main__':
    for k, f in list(globals().items()):
        if k.startswith('test_'):
            f(); print('ok', k)
