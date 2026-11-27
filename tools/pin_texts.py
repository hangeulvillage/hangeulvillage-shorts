"""Pinned-comment text for Hangeul Village shorts (same wording as pipeline/shorts/seo.py).

Usage: python3 tools/pin_texts.py SHORTS_DIR [DAYS]
SHORTS_DIR = folder of DB `shorts` docs saved as JSON (ArtifactData list out_dir).
Prints yt_id, public time, format/lang, pin text for every YouTube video that is
public now (scheduled_for <= now) within DAYS (default 3) and has no `yt_pinned: true`.
"""
import json, sys, glob, os, datetime as dt
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pipeline', 'shorts'))
import i18n

EN = {
    'Q': 'Got it right? Comment the next English word you want to see in Hangul.',
    'V': 'What was your answer? Comment 1 or 2 and we will make the next quiz harder.',
    'D': 'Which Korean word should we build next? Comment it!',
    'E': 'Which Korean word should we build next? Comment it!',
    'A': 'Comment your name below and we will write it in Korean in a future short.',
    'B': 'Comment your name below and we will write it in Korean in a future short.',
    'C': 'Comment your name below and we will write it in Korean in a future short.',
}

def pin_text(fmt, lang):
    if lang and lang != 'en':
        m = i18n._META.get('zh' if lang.startswith('zh') else lang)
        if m:
            return m['cta_word'] if fmt in ('D', 'E') else m['cta_name']
    return EN.get(fmt, EN['A'])

def due(shorts_dir, days=3, now=None):
    KST = dt.timezone(dt.timedelta(hours=9))
    now = now or dt.datetime.now(KST)
    out = []
    for f in sorted(glob.glob(os.path.join(shorts_dir, '*.json'))):
        d = json.load(open(f))
        if not d.get('yt_id') or d.get('yt_pinned') is True:
            continue
        when = d.get('scheduled_for') or d.get('createdAt')
        if not when:
            continue
        t = dt.datetime.fromisoformat(when)
        if t <= now and now - t <= dt.timedelta(days=days):
            out.append((os.path.basename(f)[:-5], d['yt_id'], when, d.get('format'), d.get('lang', 'en'),
                        pin_text(d.get('format'), d.get('lang', 'en'))))
    return out

if __name__ == '__main__':
    for row in due(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3):
        print('\t'.join(str(x) for x in row))
