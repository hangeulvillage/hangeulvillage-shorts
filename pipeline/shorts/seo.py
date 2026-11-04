"""Platform-specific upload copy for Hangeul Village shorts.

YouTube Shorts: keyword-first title (<=70 chars), searchable description, tags, 3-5 hashtags.
TikTok: short caption (<=150 chars) with search keywords + 4-5 hashtags.
Instagram Reels: hook line, breakdown, CTA, 5 hashtags, alt text.
Spanish/Portuguese lines reach the big Mexico/Brazil learner base.
"""
import random

def _sylls(ko):
    from_ = []
    for ch in ko.replace(' ', ''):
        c = ord(ch) - 0xAC00
        if 0 <= c < 11172:
            L = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'[c // 588]
            V = 'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'[(c % 588) // 28]
            T = ' ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ'[c % 28].strip()
            from_.append(L + '+' + V + ('+' + T if T else '') + '=' + ch)
    return ' · '.join(from_)

def _sentence(x):
    x = (x or '').strip()
    return x if not x or x[-1] in '.!?' else x + '.'

def _fit(text, tags, limit):
    out = text
    for t in tags.split():
        if len(out) + 1 + len(t) <= limit: out += ' ' + t
    return out

def quiz_package(fmt, it, snd, seed=0):
    r = random.Random(seed); ko, mean, note = it['ko'], it['en'], _sentence(it.get('note', ''))
    if fmt == 'Q':
        title = r.choice([f'Guess the English word: {ko} #shorts', f'Can you read this? It is English! {ko} #shorts', f'{ko} = ? Comment your guess #shorts'])
        tags = ['konglish', 'korean loanwords', 'english words in korean', 'korean quiz', 'learn korean', 'hangul', 'read korean', f'{mean.lower()} in korean']
        tt = f'Guess the English word: {ko}. Comment your guess before the answer!'
        tt_tags = '#learnkorean #koreanquiz #konglish #hangul #korean'; ig_tags = '#learnkorean #koreanquiz #konglish #hangul #studykorean'
        lead = f'{ko} ({snd}) is "{mean}" written in Hangul.'
        ask = 'Did you guess it before the answer? Comment your guess on the next one!'
        pin = r.choice(['How fast did you read it? Comment your time!', 'Got it right? Comment the next English word you want to see in Hangul.'])
    else:
        wrong, wrong_en = it.get('wrong', ''), it.get('wrong_en', '')
        title = r.choice([f'Which one means "{mean}"? 1 or 2 #shorts', f'Korean quiz: "{mean}" is 1 or 2? #shorts', f'1 or 2? Find "{mean}" in Korean #shorts'])
        tags = ['korean quiz', 'korean words', 'learn korean', 'kdrama korean', 'hangul', 'korean for beginners', f'{mean.lower()} in korean']
        tt = f'Which one means "{mean}" in Korean? Comment 1 or 2!'
        tt_tags = '#learnkorean #koreanquiz #kdrama #hangul #korean'; ig_tags = '#learnkorean #koreanquiz #kdrama #hangul #studykorean'
        lead = f'"{mean}" in Korean is {ko} ({snd}).' + (f' The other one, {wrong}, means "{wrong_en}".' if wrong and wrong_en else '')
        ask = 'Comment 1 or 2 before the answer next time!'
        pin = r.choice(['Did you pick the right number? Comment 1 or 2!', 'What was your answer? Comment 1 or 2 and we will make the next quiz harder.'])
    desc = (f"{lead}\n{_sylls(ko)}\n{note}\n\nEvery Korean syllable is a block: first sound + vowel (+ final sound).\n"
            f"{ask}\n\n#learnkorean #hangul #koreanquiz #shorts")
    ig = f'{ko} = {mean} ✍️\n\n{_sylls(ko)}\n{note}\n\n{ask}\n\n{ig_tags}'
    return {'youtube': {'title': title[:95], 'description': desc, 'tags': tags, 'made_for_kids': False, 'pinned_comment': pin},
            'tiktok': {'caption': _fit(tt, tt_tags, 150), 'pinned_comment': pin},
            'instagram': {'caption': ig, 'alt_text': f'Quiz animation building the Korean word {ko} ({mean}) from Hangul blocks.', 'pinned_comment': pin}}

def word_package(fmt, it, snd, seed=0):
    if fmt in ('Q', 'V'): return quiz_package(fmt, it, snd, seed)
    r = random.Random(seed); ko, mean, note = it['ko'], it['en'], _sentence(it.get('note', ''))
    if fmt == 'D':
        title = r.choice([f'What does {ko} mean? (K-drama Korean) #shorts', f'{ko} = {mean} | Korean you hear in every K-drama #shorts', f'Read this K-drama word: {ko} #shorts'])
        tags = ['kdrama korean', 'korean words', 'learn korean with kdrama', 'kpop korean words', 'korean phrases', 'learn korean', 'hangul', f'{snd.replace("-", "")} meaning', f'what does {ko} mean']
        tt_tags = '#kdrama #learnkorean #koreanwords #hangul #kpop'; ig_tags = '#kdrama #learnkorean #koreanwords #koreanlanguage #hangul'
        lead = f'{ko} ({snd}) means "{mean}".'
    else:
        title = r.choice([f'Can you read this Korean sign? {ko} #shorts', f'{ko} = {mean} | Korean for your Seoul trip #shorts', f'Read this sign in Seoul: {ko} #shorts'])
        tags = ['korean signs', 'korea travel', 'seoul travel tips', 'korean for travel', 'learn korean', 'hangul', 'read korean', f'{snd.replace("-", "")} korean', f'{mean.lower()} in korean']
        tt_tags = '#koreatravel #seoul #learnkorean #hangul #koreanwords'; ig_tags = '#koreatravel #seoul #learnkorean #hangul #studykorean'
        lead = f'This sign says {ko} ({snd}): "{mean}".'
    title = title[:95]
    desc = (f"{lead}\n{_sylls(ko)}\n{note}\n\nEvery Korean syllable is a block: first sound + vowel (+ final sound).\n"
            f"Which word should we build next? Tell us in the comments.\n\n#learnkorean #hangul #shorts")
    tt = _fit(f'{ko} = {_sentence(mean)} {note} Which word next?'.replace('  ', ' '), tt_tags, 150)
    ig = f'{ko} = {mean} ✍️\n\n{_sylls(ko)}\n{note}\n\nWhich word next? Comment below.\n\n{ig_tags}'
    pin = r.choice(['Which Korean word should we build next? Comment it!', 'Drop a word you hear in K-dramas and we will build it next.'])
    return {'youtube': {'title': title, 'description': desc, 'tags': tags, 'made_for_kids': False, 'pinned_comment': pin},
            'tiktok': {'caption': tt, 'pinned_comment': pin},
            'instagram': {'caption': ig, 'alt_text': f'Animation building the Korean word {ko} ({mean}) from Hangul blocks.', 'pinned_comment': pin}}

def package(fmt, items, sounds, seed=0):
    if fmt in ('D', 'E', 'Q', 'V'):
        return word_package(fmt, items[0], sounds.get(items[0]['ko'], ''), seed)
    """items: [{'en','ko','handle'}]; sounds: {ko: 'so-pi-a'}"""
    r = random.Random(seed)
    it = items[0]; en, ko = it['en'], it['ko']; snd = sounds.get(ko, '')
    names = ', '.join(i['en'] for i in items)
    kos = ' · '.join(i['ko'] for i in items)
    handles = ' '.join(i['handle'] for i in items if i.get('handle'))
    if fmt == 'A':
        yt_title = r.choice([f'{en} in Korean (Hangul) #shorts', f'How to write {en} in Korean #shorts', f'Your name in Korean: {en} = {ko} #shorts'])
        hook = f'{en} in Korean is {ko}'
    elif fmt == 'B':
        yt_title = r.choice([f'Can you read this Korean name? {ko} #shorts', f'Read this Korean name in 3 seconds #shorts', f'Guess the name: {ko} #shorts'])
        hook = f'Could you read {ko}? It says {en}'
    else:
        yt_title = r.choice([f'Your names in Korean: {names} #shorts', f'Writing your names in Hangul #shorts', f'You asked, I built it: {kos} #shorts'])
        hook = f'Your names in Korean: {names}'
    yt_title = yt_title[:95]
    breakdown = '\n'.join(f"{i['en']} = {i['ko']} ({sounds.get(i['ko'], '')})\n{_sylls(i['ko'])}" for i in items)
    es_pt = f"ES: Tu nombre en coreano: {kos} · PT: Seu nome em coreano: {kos}"
    thanks = f'\nThanks {handles} for the request!' if handles else ''
    yt_desc = (f"{hook}.\n\n{breakdown}\n\nEvery Korean syllable is a block: first sound + vowel (+ final sound). "
               f"Learn to read Hangul one name at a time.{thanks}\n\nComment your name and we will build it in Korean next.\n\n"
               f"{es_pt}\n\n#learnkorean #hangul #koreanname #shorts")
    yt_tags = ['learn korean', 'korean name', 'name in korean', 'hangul', 'korean alphabet', 'how to write my name in korean',
               'korean for beginners', 'learn hangul', f'{en.lower()} in korean', f'{en.lower()} korean name', 'tu nombre en coreano', 'seu nome em coreano']
    tt = r.choice([f'{en} in Korean = {ko}. Comment your name!', f'How to write {en} in Korean. Want yours? Comment it!', f'{hook}. Your name next?'])
    if fmt == 'B': tt = f'Can you read {ko}? Answer at the end. Comment your name!'
    if fmt == 'C': tt = f'Your names in Korean: {names}. Comment yours!'
    tt_caption = _fit(tt, '#learnkorean #koreanname #hangul #korean #studykorean', 150)
    ig_caption = (f"{hook} ✍️\n\n{breakdown}\n\nComment your name and we will build it next.{thanks}\n\n{es_pt}\n\n"
                  f"#learnkorean #koreanlanguage #hangul #koreanname #studykorean")
    ig_alt = f'Animation building the Korean name {kos} from colour-coded Hangul letter blocks.'
    pin = r.choice(['Comment your name below and we will write it in Korean in a future short.',
                    'Name requests are open: comment yours!', 'Next video could be your name. Comment it below.'])
    return {
        'youtube': {'title': yt_title, 'description': yt_desc, 'tags': yt_tags, 'made_for_kids': False, 'pinned_comment': pin},
        'tiktok': {'caption': tt_caption, 'pinned_comment': pin},
        'instagram': {'caption': ig_caption, 'alt_text': ig_alt, 'pinned_comment': pin},
    }

REPLY_TEMPLATES = {
    'name_request': ['Got it! {name} is on the list. It will be in an upcoming short.', 'Added {name} to the queue. Coming soon!',
                     'Love it. {name} will get its own Hangul blocks soon.'],
    'done': ['Here it is! {name} = {ko}. Hope you like it.', 'Your name is up: {name} = {ko}!'],
    'thanks': ['Thank you for watching!', 'Glad you liked it!'],
    'question': None,  # questions are answered individually in the draft, never by template
}


# ---------- other languages (i18n.py) ----------
def _loc_parts(fmt, items, sounds, lang):
    import i18n
    if fmt in ('Q', 'V'): return None  # quiz formats: English copy only for now
    m = i18n.meta(lang)
    it = items[0]; ko = it['ko']; snd = sounds.get(ko, '')
    names = ', '.join(i['en'] for i in items)
    if fmt in ('D', 'E'):
        mn = i18n.mean(lang, ko)
        if not mn: return None
        title = m[fmt + '_t'].format(ko=ko)
        lead = m[fmt + '_l'].format(ko=ko, snd=snd, mean=mn)
        body = f"{lead}\n{_sylls(ko)}\n\n{m['block']}\n{m['cta_word']}"
    elif fmt == 'C':
        title = m['C_t'].format(names=names)
        lines = '\n'.join(f"{i['en']} = {i['ko']} ({sounds.get(i['ko'], '')})\n{_sylls(i['ko'])}" for i in items)
        body = f"{m['C_l']}\n{lines}\n\n{m['block']}\n{m['cta_name']}"
    else:
        title = m[fmt + '_t'].format(en=it['en'], ko=ko)
        lead = m[fmt + '_l'].format(en=it['en'], ko=ko, snd=snd)
        body = f"{lead}\n{_sylls(ko)}\n\n{m['block']}\n{m['cta_name']}"
    return m, title, body

def translations(fmt, items, sounds):
    """YouTube 'Title and description' translations for one video: {lang: {title, description}}."""
    import i18n
    out = {}
    for lang in i18n.META_LANGS:
        p = _loc_parts(fmt, items, sounds, lang)
        if not p: continue
        m, title, body = p
        out[lang] = {'title': (title + ' #shorts')[:100], 'description': f"{body}\n\n{m['tags']} #shorts"}
    return out

def localized(fmt, items, sounds, lang, seed=0):
    """Copy for a short whose on-screen text is in `lang` (same shape as package())."""
    m, title, body = _loc_parts(fmt, items, sounds, lang)
    tags_extra = ['learn korean', 'hangul', 'korean name' if fmt in 'ABC' else 'korean words']
    yt_title = (title + ' #shorts')[:100]
    tags = ' '.join(dict.fromkeys((m['tags'] + ' #learnkorean #hangul').split()))
    desc = f"{body}\n\n{tags} #shorts"
    tt = _fit(title, tags, 150)
    ig = f"{body}\n\n{tags}"
    pin = m['cta_word'] if fmt in ('D', 'E') else m['cta_name']
    alt = f"Hangul blocks building {', '.join(i['ko'] for i in items)}."
    return {'youtube': {'title': yt_title, 'description': desc, 'tags': tags_extra, 'made_for_kids': False, 'pinned_comment': pin},
            'tiktok': {'caption': tt, 'pinned_comment': pin},
            'instagram': {'caption': ig, 'alt_text': alt, 'pinned_comment': pin},
            'lang': lang}
