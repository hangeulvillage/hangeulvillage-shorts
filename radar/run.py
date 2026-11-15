"""One-command runner for the cloud steps of the daily radar task (same steps, same order, every time).

  python3 radar/run.py make CARD.json OUT_DIR [--today YYYY-MM-DD] [make.py options...]
      1) validate_card.py  -> stop with the error list if the card is wrong (nothing rendered)
      2) make.py           -> video.mp4, thumb.jpg, copy.txt, qa.png, manifest.json
      3) bundle.json       -> everything the upload steps need in one file:
         yt {title, description, tags, pinned_comment}, kit {ig_caption, tt_caption} (no links,
         at most 5 hashtags), files, qa, validation warnings.
      Retries the render once if it fails for a non-card reason (TTS/ffmpeg hiccup).

  python3 radar/run.py blog CARD.json OUT_DIR --yt VIDEO_ID
      blog.py twice: OUT_DIR/tistory (embedded video) and OUT_DIR/naver (--naver variant).
      Prints both titles and QA results; exit 1 if either QA fails.

Exit code 0 = ready, 1 = stop and read the printed JSON.
"""
import argparse, datetime as dt, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from validate_card import validate  # noqa: E402


def out(obj, code):
    print(json.dumps(obj, ensure_ascii=False, indent=1))
    sys.exit(code)


def kit_caption(text, max_tags=5):
    """Phone-kit caption: no URLs (links in captions hurt reach / look spammy), at most max_tags hashtags."""
    text = re.sub(r'https?://\S+', '', text)
    tags = re.findall(r'#\S+', text)
    body = re.sub(r'#\S+', '', text)
    body = re.sub(r'[ \t]+\n', '\n', body)
    body = re.sub(r'\n{3,}', '\n\n', body).strip()
    keep = list(dict.fromkeys(t for t in tags if t.lower() != '#shorts'))[:max_tags]
    return (body + ('\n\n' + ' '.join(keep) if keep else '')).strip()


def cmd_make(a, extra):
    card = json.load(open(a.card))
    today = dt.date.fromisoformat(a.today) if a.today else None
    E, W = validate(card, today)
    if E:
        out({'ok': False, 'step': 'validate', 'errors': E, 'warnings': W}, 1)
    os.makedirs(a.out, exist_ok=True)
    cmd = [sys.executable, os.path.join(HERE, 'make.py'), a.card, a.out] + extra
    res = None
    for attempt in (1, 2):
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            break
        if 'card missing' in (res.stderr or '') or 'ranking:' in (res.stderr or ''):
            break  # card problem: retrying will not help
    if res.returncode != 0:
        out({'ok': False, 'step': 'render', 'attempts': attempt, 'stderr': (res.stderr or '')[-1500:]}, 1)
    man = json.load(open(os.path.join(a.out, 'manifest.json')))
    c = man['copy']
    bundle = {
        'id': man['id'], 'publish_date': card['publish_date'], 'format': man['format'], 'duration': man['duration'],
        'yt': {'title': c['yt_title'] + ' #shorts', 'description': c['description'], 'tags': c['tags'],
               'pinned_comment': c['pinned_comment']},
        'kit': {'ig_caption': kit_caption(c['instagram_caption']), 'tt_caption': kit_caption(c['tiktok_caption'])},
        'files': man['files'], 'qa': man['qa'], 'voice_min_sim': min((v.get('sim', 1) for v in man.get('voice_check') or []), default=None),
        'validation_warnings': W,
    }
    json.dump(bundle, open(os.path.join(a.out, 'bundle.json'), 'w'), ensure_ascii=False, indent=1)
    ready = man['qa']['pass']
    out({'ok': ready, 'step': 'done' if ready else 'qa', 'bundle': os.path.join(a.out, 'bundle.json'),
         'title': bundle['yt']['title'], 'duration': man['duration'], 'qa': man['qa'], 'warnings': W}, 0 if ready else 1)


def cmd_blog(a, extra):
    results = {}
    for name, flags in (('tistory', []), ('naver', ['--naver'])):
        d = os.path.join(a.out, name)
        r = subprocess.run([sys.executable, os.path.join(HERE, 'blog.py'), a.card, d, '--yt', a.yt] + flags,
                           capture_output=True, text=True)
        if r.returncode != 0:
            out({'ok': False, 'step': f'blog:{name}', 'stderr': r.stderr[-1500:]}, 1)
        results[name] = json.loads(r.stdout.strip().splitlines()[-1])
        results[name]['dir'] = d
    ok = all(v['qa_pass'] for v in results.values())
    out({'ok': ok, **results}, 0 if ok else 1)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    m = sub.add_parser('make'); m.add_argument('card'); m.add_argument('out'); m.add_argument('--today', default=None)
    b = sub.add_parser('blog'); b.add_argument('card'); b.add_argument('out'); b.add_argument('--yt', required=True)
    a, extra = ap.parse_known_args()
    (cmd_make if a.cmd == 'make' else cmd_blog)(a, extra)


if __name__ == '__main__':
    main()
