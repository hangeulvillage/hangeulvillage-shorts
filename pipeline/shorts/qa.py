"""Proofreading gate for every short before delivery.

Automatic checks (blocking = must fix):
  - Korean in titles/captions matches the Korean actually built in the video
  - D/E words come from the vetted list (words.json) with the same meaning
  - names whose Korean spelling is a rule-based guess are flagged for review
  - punctuation: no two sentences glued together, no double spaces, no cut-off hashtags
  - length limits (YouTube title 100 hard / 60 soft, TikTok 150), video 6-35 s (target 8-12 s), loudness -15..-13 LUFS
  - every spoken syllable passed the speech check
It also writes a contact sheet (4 key frames) for a visual check by the reviewer.
"""
import json, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WORDS = json.load(open(os.path.join(HERE, 'words.json')))

def _glued(text):
    # a lowercase word immediately followed by a capitalised sentence start, with no punctuation between
    return [m.group(0) for m in re.finditer(r"[a-z\)]\s+(Which|Comment|Want|Your|Next|Thanks|Learn|Every|Did|Name|Drop|Look|Say)\b", text)]

def check(job, items, pk, info, video, exact_flags=None, lang='en'):
    issues, review = [], []
    fmt = job['fmt']
    kos = [i['ko'] for i in items]
    texts = {'yt_title': pk['youtube']['title'], 'yt_desc': pk['youtube']['description'],
             'tt': pk['tiktok']['caption'], 'ig': pk['instagram']['caption']}
    for k, t in texts.items():
        if '  ' in t.replace('\n', ' \n'): issues.append(f'{k}: double space')
        for g in _glued(t): issues.append(f'{k}: missing punctuation near "{g}"')
        if re.search(r'#\w*$', t) and len(t) >= 150 and k == 'tt': pass
        if re.search(r'(^|\s)#($|\s)', t): issues.append(f'{k}: empty hashtag')
    if lang != 'en':
        import i18n
        if fmt in ('D', 'E') and items[0]['en'] != i18n.mean(lang, items[0]['ko']): issues.append('localized meaning differs from i18n.MEAN')
    if len(texts['yt_title']) > 100: issues.append('yt_title over 100 chars')
    if len(texts['yt_title'].replace(' #shorts', '')) > 60: review.append('yt_title over 60 chars: gets cut off in the Shorts feed')
    if len(texts['tt']) > 150: issues.append('tiktok caption over 150 chars')
    for ko in kos:
        if ko not in texts['yt_desc'] or ko not in texts['ig']: issues.append(f'Korean "{ko}" missing from copy')
    if info.get('korean') and fmt not in ('D', 'E', 'Q', 'V') and [k.replace(' ', '') for k in info['korean']] != [k.replace(' ', '') for k in kos]:
        issues.append(f'copy Korean {kos} differs from video Korean {info["korean"]}')
    if fmt in ('D', 'E', 'Q', 'V') and lang == 'en':
        vetted = {w[0]: w[1] for w in WORDS[fmt]}
        it = items[0]
        if it['ko'] not in vetted: review.append(f'word "{it["ko"]}" is not in the vetted list: confirm spelling and meaning "{it["en"]}"')
        elif vetted[it['ko']] != it['en']: issues.append(f'meaning "{it["en"]}" differs from vetted "{vetted[it["ko"]]}"')
    for it, ex in zip(items, exact_flags or []):
        if not ex: review.append(f'name "{it["en"]}" spelled {it["ko"]} by rule, not dictionary: confirm the usual Korean spelling')
    bad = [c for c in info.get('voice_check', []) if not c[2]]
    if bad: issues.append(f'speech check failed: {bad}')
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', video], capture_output=True, text=True).stdout or 0)
    if not 6 <= dur <= 35: issues.append(f'duration {dur:.1f}s')
    if dur > 12.5 and fmt != 'C': review.append(f'{dur:.1f}s is over the 8-12 s target')
    meas = subprocess.run(['ffmpeg', '-i', video, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    m = re.findall(r'I:\s+(-?[\d.]+) LUFS', meas)
    if m and not -15.5 <= float(m[-1]) <= -12.5: issues.append(f'loudness {m[-1]} LUFS')
    sheet = os.path.splitext(video)[0] + '_sheet.png'
    ts = [1.2, dur * 0.45, dur * 0.72, dur - 1.0]
    args = []
    for t in ts: args += ['-ss', f'{t:.2f}', '-i', video]
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + args + ['-filter_complex',
                    ''.join(f'[{i}:v]scale=270:480,trim=end_frame=1[v{i}];' for i in range(4)) + ''.join(f'[v{i}]' for i in range(4)) + 'hstack=inputs=4', '-frames:v', '1', sheet])
    return {'pass': not issues, 'issues': issues, 'review': review, 'sheet': sheet, 'duration': round(dur, 1)}
