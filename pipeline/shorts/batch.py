"""Render a week's batch of Hangeul Village shorts with platform copy.

usage: python3 batch.py plan.json OUT_DIR
plan.json: [{"fmt": "A", "names": ["Sofia"], "voice": "female"}, {"fmt": "C", "names": ["Lucas @luc_22", "Putri"], "voice": "male"}, ...]
Writes OUT_DIR/NN_<slug>.mp4, OUT_DIR/NN_<slug>.txt (copy for each platform) and OUT_DIR/manifest.json.
"""
import sys, os, json, subprocess, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import seo, qa
STUDIO = open(os.path.join(os.path.dirname(HERE), 'shorts-studio.html')).read()
DICT = set(re.findall(r"(\w+):'[\uAC00-\uD7A3 ]+'", STUDIO[STUDIO.find('const DICT'):STUDIO.find('};', STUDIO.find('const DICT'))]))
WORDF = ('D', 'E', 'Q', 'V')
WORDS = json.load(open(os.path.join(HERE, 'words.json')))
# app waitlist (Google Form, created 2026-11-06): one line in the YouTube description and the IG/FB caption.
# Not in TikTok captions (links are not clickable there).
APP_FORM = 'https://docs.google.com/forms/d/e/1FAIpQLSceVzM0W5d43HRfxSd3tBent7IcvT8MVTfNaT5NoYpmnkAosg/viewform'
APP_CTA = {
    'en': 'Our Hangeul Village app is coming in 2027. Get notified: ',
    'bn': 'Hangeul Village অ্যাপ আসছে ২০২৭ সালে। খবর পেতে: ',
    'fr': 'L\u2019appli Hangeul Village arrive en 2027. Pour être prévenu : ',
    'pt': 'O app Hangeul Village chega em 2027. Para ser avisado: ',
    'es': 'La app Hangeul Village llega en 2027. Para recibir aviso: ',
    'ja': 'Hangeul Villageアプリは2027年に登場予定。お知らせ登録はこちら：',
    'de': 'Die Hangeul Village App kommt 2027. Benachrichtigung erhalten: ',
}
def add_app_cta(pk, lang):
    line = APP_CTA.get(lang, APP_CTA['en']) + APP_FORM
    yd = pk['youtube']['description']
    if APP_FORM not in yd:
        parts = yd.rsplit('\n\n', 1)  # keep the hashtags block last
        pk['youtube']['description'] = (parts[0] + '\n\n' + line + '\n\n' + parts[1]) if len(parts) == 2 else yd + '\n\n' + line
    ic = pk['instagram']['caption']
    if APP_FORM not in ic:
        parts = ic.rsplit('\n\n', 1)
        pk['instagram']['caption'] = (parts[0] + '\n\n' + line + '\n\n' + parts[1]) if len(parts) == 2 else ic + '\n\n' + line
    return pk

L_ROM = ['g','kk','n','d','tt','r','m','b','pp','s','ss','','j','jj','ch','k','t','p','h']
V_ROM = ['a','ae','ya','yae','eo','e','yeo','ye','o','wa','wae','oe','yo','u','wo','we','wi','yu','eu','ui','i']
T_ROM = ['','k','k','k','n','n','n','t','l','k','m','l','l','l','p','l','m','p','p','t','t','ng','t','t','k','t','p','t']
def sounds_like(ko):
    out = []
    for w in ko.split(' '):
        parts = []
        for ch in w:
            c = ord(ch) - 0xAC00
            if 0 <= c < 11172: parts.append(L_ROM[c // 588] + V_ROM[(c % 588) // 28] + T_ROM[c % 28])
        out.append('-'.join(parts))
    return ' '.join(out)

def main(plan_path, out_dir):
    plan = json.load(open(plan_path)); os.makedirs(out_dir, exist_ok=True)
    manifest = []
    for n, job in enumerate(plan, 1):
        if job['fmt'] in WORDF and '=' not in job['names'][0]:  # look up vetted meaning + note
            w = {x[0]: x for x in WORDS[job['fmt']]}.get(job['names'][0].strip())
            if w: job['names'] = [f'{w[0]} = {w[1]} | {w[2]}' + (f' | {w[3]} | {w[4]}' if job['fmt'] == 'V' else '')]
            if w and job.get('lang', 'en') != 'en':
                import i18n; mn = i18n.mean(job['lang'], w[0])
                job['names'] = [f'{w[0]} = {mn}'] if mn else job['names']
        if job['fmt'] in WORDF:
            slug = re.sub(r'[^a-z0-9]+', '-', sounds_like(job['names'][0].split('=')[0].strip())).strip('-')
        else:
            slug = re.sub(r'[^a-z0-9]+', '-', '-'.join(x.split('@')[0].split('=')[0] for x in job['names']).lower()).strip('-')
        lang = job.get('lang', 'en')
        base = os.path.join(out_dir, f'{n:02d}_{job["fmt"]}_{slug}_{job.get("voice", "female")}' + ('' if lang == 'en' else '_' + lang))
        # opening-line variant for the A/B/C hook test: set by the plan, else stable per word (re-renders match)
        hook = int(job['hook']) if 'hook' in job else sum(ord(c) for c in job['names'][0].split('=')[0].strip()) % 3
        job['hook'] = hook
        # sound-effect set for the earshot A/B test: set by the plan, else stable per word (independent of the hook hash)
        if job.get('sfx') not in ('earshot', 'classic'):
            import hashlib
            job['sfx'] = 'earshot' if hashlib.md5(job['names'][0].split('=')[0].strip().encode()).digest()[0] % 2 == 0 else 'classic'
        res = subprocess.run([sys.executable, os.path.join(HERE, 'make_short.py'), job['fmt'], *job['names'], '--voice', job.get('voice', 'female'), '--lang', lang, '--hook', str(hook), '--sfx', job['sfx'], *(['--style', json.dumps(job['style'])] if job.get('style') else []), '--out', base + '.mp4'],
                             capture_output=True, text=True)
        line = [l for l in res.stdout.splitlines() if l.startswith('{')]
        if res.returncode or not line:
            manifest.append({'n': n, 'job': job, 'error': (res.stderr or res.stdout)[-800:]}); continue
        info = json.loads(line[-1])
        items = []
        if job['fmt'] in WORDF:
            m = re.match(r'^([\uAC00-\uD7A3 ]+)\s*=\s*([^|]+)(?:\|(.*))?$', job['names'][0].strip())
            rest = [x.strip() for x in (m.group(3) or '').split('|')]
            it = {'ko': m.group(1).strip(), 'en': m.group(2).strip(), 'note': rest[0], 'handle': ''}
            if job['fmt'] == 'V': it['wrong'], it['wrong_en'] = (rest + ['', '', ''])[1:3]
            items.append(it)
        for raw, ko in ([] if job['fmt'] in WORDF else zip(job['names'], info['korean'])):
            m = re.match(r'^(.*?)(\s+@[\w.\-]+)?$', re.sub(r'=[^@]*', ' ', raw).strip())
            items.append({'en': m.group(1).strip().title(), 'ko': ko, 'handle': (m.group(2) or '').strip()})
        snd = {i['ko']: sounds_like(i['ko']) for i in items}
        pk = seo.package(job['fmt'], items, snd, seed=n) if lang == 'en' else seo.localized(job['fmt'], items, snd, lang, seed=n)
        yt_tr = seo.translations(job['fmt'], items, snd) if lang == 'en' else {}
        pk = add_app_cta(pk, lang)
        ok = all(c[2] for c in info['voice_check'])
        exact = [('=' in raw) or all(p.lower() in DICT for p in re.sub(r'[^A-Za-z ]', ' ', i['en']).split()) for i, raw in zip(items, job['names'])] if job['fmt'] not in WORDF else []
        report = qa.check(job, items, pk, info, base + '.mp4', exact, lang)
        with open(base + '.txt', 'w') as f:
            f.write(f"[YouTube Shorts]\nTitle: {pk['youtube']['title']}\n\nDescription:\n{pk['youtube']['description']}\n\nTags: {', '.join(pk['youtube']['tags'])}\nAudience: Not made for kids\nPinned comment: {pk['youtube']['pinned_comment']}\n\n")
            f.write(f"[TikTok]\nCaption: {pk['tiktok']['caption']}\nPinned comment: {pk['tiktok']['pinned_comment']}\n\n")
            f.write(f"[Instagram Reels]\nCaption:\n{pk['instagram']['caption']}\n\nAlt text: {pk['instagram']['alt_text']}\nPinned comment: {pk['instagram']['pinned_comment']}\n")
            f.write(f"\n[Language] video/title language: {lang}\n")
            for lg, tr in yt_tr.items():
                f.write(f"\n[YouTube translation {lg}]\nTitle: {tr['title']}\nDescription:\n{tr['description']}\n")
        manifest.append({'n': n, 'job': job, 'video': base + '.mp4', 'copy': base + '.txt', 'items': items, 'voice_ok': ok, 'voice_check': info['voice_check'], 'package': pk, 'lang': lang, 'hook': info.get('hook', 0), 'sfx': info.get('sfx', job['sfx']), 'duration': info.get('duration'), 'yt_translations': yt_tr, 'qa': report})
    json.dump(manifest, open(os.path.join(out_dir, 'manifest.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps([{'n': m['n'], 'hook': m.get('hook'), 'sfx': m.get('sfx'), 'sec': round(m.get('duration') or 0, 1), 'qa_pass': (m.get('qa') or {}).get('pass'), 'issues': (m.get('qa') or {}).get('issues'), 'review': (m.get('qa') or {}).get('review'), 'video': os.path.basename(m.get('video', '')), 'error': m.get('error', '')[:200]} for m in manifest], ensure_ascii=False))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
