"""Language pack for Hangeul Village: languages by total speakers (Ethnologue 2026), after English.

ORDER          - rollout order for localized shorts (most speakers first)
UI[lang]       - on-screen strings for the renderer (shorts-studio.html reads window.HV_UI)
META[lang]     - YouTube/TikTok/Instagram copy templates
MEAN[lang][ko] - meanings of the vetted D/E words
NAMES[lang]    - common local first names with their usual Korean spelling (curated, not rule-based)
STUDIO[lang]   - words to type in YouTube Studio's (Korean UI) language picker
Chinese is written once in Simplified and converted to Traditional (Taiwan) with OpenCC.
All of this is machine-written: a native speaker should check a language before it scales up.
"""
try:
    import opencc
    _s2t = opencc.OpenCC('s2twp').convert
except Exception:  # OpenCC missing: Traditional falls back to Simplified text
    _s2t = lambda s: s

ORDER = ['zh-Hant', 'hi', 'es', 'ar', 'fr', 'bn', 'pt', 'id', 'ur', 'ru', 'ja', 'de']   # ja/de added 2026-11-05: high ad rates + big Korean-learning markets   # video rollout (Mandarin = Taiwan/HK/SEA on these platforms)
META_LANGS = ['zh-Hans', 'zh-Hant', 'hi', 'es', 'ar', 'fr', 'bn', 'pt', 'id', 'ur', 'ru', 'ja', 'de']  # YouTube translated titles/descriptions
RTL = {'ar', 'ur'}

STUDIO = {'en': '영어', 'zh-Hans': '중국어(간체)', 'zh-Hant': '중국어(번체)', 'hi': '힌디어', 'es': '스페인어', 'ar': '아랍어',
          'fr': '프랑스어', 'bn': '벵골어', 'pt': '포르투갈어', 'id': '인도네시아어', 'ur': '우르두어', 'ru': '러시아어', 'ja': '일본어', 'de': '독일어'}

_UI = {
 'zh': dict(hookA1='', hookA3='的韩文怎么写？', hookC1='你们点的名字', hookC2='韩文版', hookC3='来了！', quiz1='你看得懂', quiz2='这个名字吗？',
            Dchip='韩剧单词', D1='韩剧里', D2='天天听到', D3='你会念吗？', Echip='首尔招牌', E1='你看得懂', E2='这个招牌吗？',
            endWords='＝下一个单词是？', endName='＝告诉我你的名字！', endSub='在评论区留言'),
 'hi': dict(hookA1='कोरियन में', hookA3='कैसे लिखें?', hookC1='आपने माँगे थे', hookC2='आपके नाम', hookC3='कोरियन में', quiz1='क्या आप पढ़ सकते हैं', quiz2='यह नाम?',
            Dchip='के-ड्रामा शब्द', D1='यह आप सुनते हैं', D2='बार-बार', D3='पढ़ सकते हैं?', Echip='सियोल का साइनबोर्ड', E1='क्या आप पढ़ सकते हैं', E2='यह साइनबोर्ड?',
            endWords='= अगला शब्द कौन-सा?', endName='= अपना नाम बताइए!', endSub='कमेंट में लिखिए'),
 'es': dict(hookA1='¿Cómo se escribe', hookA3='en coreano?', hookC1='Ustedes pidieron.', hookC2='Sus nombres', hookC3='en coreano', quiz1='¿Puedes leer', quiz2='este nombre?',
            Dchip='PALABRA DE K-DRAMA', D1='La oyes', D2='TODO el tiempo', D3='¿Puedes leerla?', Echip='LETRERO EN SEÚL', E1='¿Puedes leer', E2='este letrero?',
            endWords='= ¿Qué palabra sigue?', endName='= ¡Dime tu nombre!', endSub='Escríbelo en los comentarios'),
 'ar': dict(hookA1='كيف تكتب', hookA3='بالكورية؟', hookC1='طلبتم', hookC2='أسماءكم', hookC3='بالكورية', quiz1='هل تستطيع قراءة', quiz2='هذا الاسم؟',
            Dchip='كلمة من الدراما الكورية', D1='تسمعها', D2='طوال الوقت', D3='هل تستطيع قراءتها؟', Echip='لافتة في سيول', E1='هل تستطيع قراءة', E2='هذه اللافتة؟',
            endWords='ما الكلمة التالية؟', endName='اكتب اسمك!', endSub='في التعليقات'),
 'fr': dict(hookA1='Comment écrire', hookA3='en coréen ?', hookC1='Vous avez demandé.', hookC2='Vos prénoms', hookC3='en coréen', quiz1='Tu sais lire', quiz2='ce prénom ?',
            Dchip='MOT DE K-DRAMA', D1='Tu l’entends', D2='TOUT le temps', D3='Tu sais le lire ?', Echip='PANNEAU À SÉOUL', E1='Tu sais lire', E2='ce panneau ?',
            endWords='= Quel mot ensuite ?', endName='= Dis-moi ton prénom !', endSub='Écris-le en commentaire'),
 'bn': dict(hookA1='কোরিয়ান ভাষায়', hookA3='কীভাবে লেখে?', hookC1='আপনারা চেয়েছিলেন', hookC2='আপনাদের নাম', hookC3='কোরিয়ান ভাষায়', quiz1='আপনি কি পড়তে পারবেন', quiz2='এই নামটা?',
            Dchip='কে-ড্রামার শব্দ', D1='এটা শুনবেন', D2='বারবার', D3='পড়তে পারবেন?', Echip='সিউলের সাইনবোর্ড', E1='আপনি কি পড়তে পারবেন', E2='এই সাইনবোর্ড?',
            endWords='= পরের শব্দ কোনটা?', endName='= আপনার নাম বলুন!', endSub='কমেন্টে লিখুন'),
 'pt': dict(hookA1='Como se escreve', hookA3='em coreano?', hookC1='Vocês pediram.', hookC2='Seus nomes', hookC3='em coreano', quiz1='Você consegue ler', quiz2='este nome?',
            Dchip='PALAVRA DE K-DRAMA', D1='Você ouve isso', D2='O TEMPO TODO', D3='Consegue ler?', Echip='PLACA EM SEUL', E1='Você consegue ler', E2='esta placa?',
            endWords='= Qual a próxima palavra?', endName='= Me diz seu nome!', endSub='Escreva nos comentários'),
 'id': dict(hookA1='Gimana nulis', hookA3='dalam bahasa Korea?', hookC1='Kalian minta.', hookC2='Nama kalian', hookC3='dalam bahasa Korea', quiz1='Bisa baca', quiz2='nama ini?',
            Dchip='KATA DRAMA KOREA', D1='Kamu sering dengar', D2='INI TERUS', D3='Bisa bacanya?', Echip='PAPAN DI SEOUL', E1='Bisa baca', E2='papan ini?',
            endWords='= Kata apa berikutnya?', endName='= Sebutkan namamu!', endSub='Tulis di kolom komentar'),
 'ur': dict(hookA1='کوریائی میں', hookA3='کیسے لکھتے ہیں؟', hookC1='آپ نے کہا تھا', hookC2='آپ کے نام', hookC3='کوریائی میں', quiz1='کیا آپ پڑھ سکتے ہیں', quiz2='یہ نام؟',
            Dchip='کے ڈرامہ کا لفظ', D1='یہ آپ سنتے ہیں', D2='بار بار', D3='پڑھ سکتے ہیں؟', Echip='سیول کا سائن بورڈ', E1='کیا آپ پڑھ سکتے ہیں', E2='یہ سائن بورڈ؟',
            endWords='اگلا لفظ کون سا؟', endName='اپنا نام بتائیں!', endSub='کمنٹ میں لکھیں'),
 'ru': dict(hookA1='Как написать', hookA3='по-корейски?', hookC1='Вы просили.', hookC2='Ваши имена', hookC3='по-корейски', quiz1='Сможешь прочитать', quiz2='это имя?',
            Dchip='СЛОВО ИЗ ДОРАМ', D1='Ты слышишь это', D2='ПОСТОЯННО', D3='Сможешь прочитать?', Echip='ВЫВЕСКА В СЕУЛЕ', E1='Сможешь прочитать', E2='эту вывеску?',
            endWords='= Какое слово дальше?', endName='= Напиши своё имя!', endSub='Пиши в комментариях'),
 'ja': dict(hookA1='', hookA3='を韓国語で書くと？', hookC1='リクエストの', hookC2='名前を', hookC3='韓国語で！', quiz1='この名前', quiz2='読める？',
            Dchip='韓ドラの言葉', D1='韓ドラで', D2='毎回聞く', D3='読める？', Echip='ソウルの看板', E1='この看板', E2='読める？',
            endWords='＝次の単語は？', endName='＝名前を教えて！', endSub='コメントで教えてね', ja=True),
 'de': dict(hookA1='Wie schreibt man', hookA3='auf Koreanisch?', hookC1='Ihr wolltet es.', hookC2='Eure Namen', hookC3='auf Koreanisch', quiz1='Kannst du', quiz2='diesen Namen lesen?',
            Dchip='K-DRAMA-WORT', D1='Du hörst es', D2='STÄNDIG', D3='Kannst du es lesen?', Echip='SCHILD IN SEOUL', E1='Kannst du', E2='dieses Schild lesen?',
            endWords='= Welches Wort als Nächstes?', endName='= Sag mir deinen Namen!', endSub='Schreib es in die Kommentare'),
}

_META = {
 'zh': dict(A_t='{en} 的韩文怎么写？{ko}', B_t='你看得懂这个韩文名字吗？{ko}', C_t='你们的名字韩文版：{names}', D_t='韩剧里的 {ko} 是什么意思？', E_t='你看得懂这个韩文招牌吗？{ko}',
            A_l='{en} 的韩文是 {ko}（{snd}）。', B_l='{ko} = {en}（{snd}）。', C_l='你们的名字韩文版：', D_l='{ko}（{snd}）的意思是「{mean}」。', E_l='这个招牌写着 {ko}（{snd}）：「{mean}」。',
            block='每个韩文音节都是一个方块：开头的辅音 + 元音（+ 收尾的辅音）。', cta_name='在评论区留下你的名字，下一支影片帮你写成韩文。', cta_word='下一个想学哪个单词？在评论区告诉我们。',
            tags='#学韩语 #韩文 #韩语'),
 'hi': dict(A_t='{en} को कोरियन में कैसे लिखें? {ko}', B_t='क्या आप यह कोरियन नाम पढ़ सकते हैं? {ko}', C_t='आपके नाम कोरियन में: {names}', D_t='के-ड्रामा में {ko} का मतलब क्या है?', E_t='क्या आप यह कोरियन साइन पढ़ सकते हैं? {ko}',
            A_l='कोरियन में {en} को {ko} ({snd}) लिखते हैं।', B_l='{ko} = {en} ({snd})।', C_l='आपके नाम कोरियन में:', D_l='{ko} ({snd}) का मतलब है "{mean}"।', E_l='इस साइन पर लिखा है {ko} ({snd}): "{mean}"।',
            block='हर कोरियन अक्षर एक ब्लॉक है: पहली ध्वनि + स्वर (+ आखिरी ध्वनि)।', cta_name='कमेंट में अपना नाम लिखिए, अगली वीडियो में उसे कोरियन में बनाएँगे।', cta_word='अगला कौन-सा शब्द सीखें? कमेंट में बताइए।',
            tags='#कोरियनसीखें #learnkorean #hangul'),
 'es': dict(A_t='{en} en coreano: {ko}', B_t='¿Puedes leer este nombre en coreano? {ko}', C_t='Sus nombres en coreano: {names}', D_t='¿Qué significa {ko}? Coreano de K-drama', E_t='¿Puedes leer este letrero coreano? {ko}',
            A_l='{en} en coreano se escribe {ko} ({snd}).', B_l='{ko} = {en} ({snd}).', C_l='Sus nombres en coreano:', D_l='{ko} ({snd}) significa "{mean}".', E_l='Este letrero dice {ko} ({snd}): "{mean}".',
            block='Cada sílaba coreana es un bloque: consonante inicial + vocal (+ consonante final).', cta_name='Escribe tu nombre en los comentarios y lo haremos en coreano.', cta_word='¿Qué palabra hacemos después? Dinos en los comentarios.',
            tags='#aprendercoreano #coreano #hangul'),
 'ar': dict(A_t='كيف تكتب {en} بالكورية؟ {ko}', B_t='هل تستطيع قراءة هذا الاسم الكوري؟ {ko}', C_t='أسماؤكم بالكورية: {names}', D_t='ما معنى {ko} في الدراما الكورية؟', E_t='هل تستطيع قراءة هذه اللافتة الكورية؟ {ko}',
            A_l='يُكتب {en} بالكورية هكذا: {ko} ({snd}).', B_l='{ko} = {en} ({snd}).', C_l='أسماؤكم بالكورية:', D_l='{ko} ({snd}) تعني "{mean}".', E_l='هذه اللافتة مكتوب عليها {ko} ({snd}): "{mean}".',
            block='كل مقطع كوري هو مكعّب: الصوت الأول + حرف العلة (+ الصوت الأخير).', cta_name='اكتب اسمك في التعليقات وسنكتبه بالكورية في الفيديو القادم.', cta_word='ما الكلمة التي تريد تعلّمها بعد ذلك؟ أخبرنا في التعليقات.',
            tags='#تعلم_الكورية #الكورية #hangul'),
 'fr': dict(A_t='{en} en coréen : {ko}', B_t='Tu sais lire ce prénom en coréen ? {ko}', C_t='Vos prénoms en coréen : {names}', D_t='Que veut dire {ko} ? Le coréen des K-dramas', E_t='Tu sais lire ce panneau coréen ? {ko}',
            A_l='{en} en coréen s’écrit {ko} ({snd}).', B_l='{ko} = {en} ({snd}).', C_l='Vos prénoms en coréen :', D_l='{ko} ({snd}) veut dire « {mean} ».', E_l='Ce panneau dit {ko} ({snd}) : « {mean} ».',
            block='Chaque syllabe coréenne est un bloc : son de départ + voyelle (+ son final).', cta_name='Écris ton prénom en commentaire et on l’écrira en coréen.', cta_word='Quel mot veux-tu apprendre ensuite ? Dis-le en commentaire.',
            tags='#apprendrelecoreen #coreen #hangul'),
 'bn': dict(A_t='{en} কোরিয়ান ভাষায় কীভাবে লেখে? {ko}', B_t='এই কোরিয়ান নামটা পড়তে পারবেন? {ko}', C_t='আপনাদের নাম কোরিয়ান ভাষায়: {names}', D_t='কে-ড্রামায় {ko} মানে কী?', E_t='এই কোরিয়ান সাইনবোর্ড পড়তে পারবেন? {ko}',
            A_l='কোরিয়ান ভাষায় {en} লেখা হয় {ko} ({snd})।', B_l='{ko} = {en} ({snd})।', C_l='আপনাদের নাম কোরিয়ান ভাষায়:', D_l='{ko} ({snd}) মানে "{mean}"।', E_l='এই সাইনবোর্ডে লেখা {ko} ({snd}): "{mean}"।',
            block='প্রতিটি কোরিয়ান অক্ষর একটি ব্লক: প্রথম ধ্বনি + স্বর (+ শেষ ধ্বনি)।', cta_name='কমেন্টে আপনার নাম লিখুন, পরের ভিডিওতে কোরিয়ানে লিখে দেব।', cta_word='পরের কোন শব্দটা শিখতে চান? কমেন্টে জানান।',
            tags='#কোরিয়ানশিখি #learnkorean #hangul'),
 'pt': dict(A_t='{en} em coreano: {ko}', B_t='Você consegue ler este nome em coreano? {ko}', C_t='Seus nomes em coreano: {names}', D_t='O que significa {ko}? Coreano de K-drama', E_t='Você consegue ler esta placa coreana? {ko}',
            A_l='{en} em coreano se escreve {ko} ({snd}).', B_l='{ko} = {en} ({snd}).', C_l='Seus nomes em coreano:', D_l='{ko} ({snd}) significa "{mean}".', E_l='Esta placa diz {ko} ({snd}): "{mean}".',
            block='Cada sílaba coreana é um bloco: som inicial + vogal (+ som final).', cta_name='Escreva seu nome nos comentários e a gente faz em coreano.', cta_word='Qual palavra a gente faz depois? Conta nos comentários.',
            tags='#aprendercoreano #coreano #hangul'),
 'id': dict(A_t='{en} dalam bahasa Korea: {ko}', B_t='Bisa baca nama Korea ini? {ko}', C_t='Nama kalian dalam bahasa Korea: {names}', D_t='Apa arti {ko}? Bahasa Korea di drakor', E_t='Bisa baca papan Korea ini? {ko}',
            A_l='{en} dalam bahasa Korea ditulis {ko} ({snd}).', B_l='{ko} = {en} ({snd}).', C_l='Nama kalian dalam bahasa Korea:', D_l='{ko} ({snd}) artinya "{mean}".', E_l='Papan ini bertuliskan {ko} ({snd}): "{mean}".',
            block='Setiap suku kata Korea adalah satu blok: bunyi awal + vokal (+ bunyi akhir).', cta_name='Tulis namamu di kolom komentar, nanti kami tulis dalam bahasa Korea.', cta_word='Mau belajar kata apa berikutnya? Tulis di komentar.',
            tags='#belajarbahasakorea #bahasakorea #hangul'),
 'ur': dict(A_t='{en} کو کوریائی میں کیسے لکھتے ہیں؟ {ko}', B_t='کیا آپ یہ کوریائی نام پڑھ سکتے ہیں؟ {ko}', C_t='آپ کے نام کوریائی میں: {names}', D_t='کے ڈرامہ میں {ko} کا مطلب کیا ہے؟', E_t='کیا آپ یہ کوریائی سائن بورڈ پڑھ سکتے ہیں؟ {ko}',
            A_l='کوریائی میں {en} کو {ko} ({snd}) لکھتے ہیں۔', B_l='{ko} = {en} ({snd})۔', C_l='آپ کے نام کوریائی میں:', D_l='{ko} ({snd}) کا مطلب ہے "{mean}"۔', E_l='اس سائن بورڈ پر لکھا ہے {ko} ({snd}): "{mean}"۔',
            block='ہر کوریائی حرف ایک بلاک ہے: پہلی آواز + حرفِ علت (+ آخری آواز)۔', cta_name='کمنٹ میں اپنا نام لکھیں، اگلی ویڈیو میں اسے کوریائی میں لکھیں گے۔', cta_word='اگلا کون سا لفظ سیکھنا ہے؟ کمنٹ میں بتائیں۔',
            tags='#کوریائی_سیکھیں #learnkorean #hangul'),
 'ru': dict(A_t='{en} по-корейски: {ko}', B_t='Сможешь прочитать это корейское имя? {ko}', C_t='Ваши имена по-корейски: {names}', D_t='Что значит {ko}? Корейский из дорам', E_t='Сможешь прочитать эту корейскую вывеску? {ko}',
            A_l='{en} по-корейски пишется {ko} ({snd}).', B_l='{ko} = {en} ({snd}).', C_l='Ваши имена по-корейски:', D_l='{ko} ({snd}) значит «{mean}».', E_l='На этой вывеске написано {ko} ({snd}): «{mean}».',
            block='Каждый корейский слог — это блок: начальный звук + гласный (+ конечный звук).', cta_name='Напиши своё имя в комментариях, и мы напишем его по-корейски.', cta_word='Какое слово выучим дальше? Пиши в комментариях.',
            tags='#корейскийязык #учимкорейский #hangul'),
 'ja': dict(A_t='{en}を韓国語で書くと？{ko}', B_t='この韓国語の名前、読める？{ko}', C_t='みんなの名前を韓国語で：{names}', D_t='韓ドラの「{ko}」ってどういう意味？', E_t='この韓国語の看板、読める？{ko}',
            A_l='{en}は韓国語で{ko}（{snd}）と書きます。', B_l='{ko}＝{en}（{snd}）。', C_l='みんなの名前を韓国語で：', D_l='{ko}（{snd}）は「{mean}」という意味です。', E_l='この看板は{ko}（{snd}）：「{mean}」。',
            block='ハングルは1文字が1ブロック：最初の音＋母音（＋最後の音）。', cta_name='コメントに名前を書いてね。次の動画で韓国語にします。', cta_word='次はどの単語を知りたい？コメントで教えてね。',
            tags='#韓国語 #韓国語勉強 #ハングル'),
 'de': dict(A_t='{en} auf Koreanisch: {ko}', B_t='Kannst du diesen koreanischen Namen lesen? {ko}', C_t='Eure Namen auf Koreanisch: {names}', D_t='Was heißt {ko}? Koreanisch aus K-Dramas', E_t='Kannst du dieses koreanische Schild lesen? {ko}',
            A_l='{en} schreibt man auf Koreanisch {ko} ({snd}).', B_l='{ko} = {en} ({snd}).', C_l='Eure Namen auf Koreanisch:', D_l='{ko} ({snd}) heißt „{mean}“.', E_l='Auf diesem Schild steht {ko} ({snd}): „{mean}“.',
            block='Jede koreanische Silbe ist ein Block: Anfangslaut + Vokal (+ Endlaut).', cta_name='Schreib deinen Namen in die Kommentare, wir schreiben ihn auf Koreanisch.', cta_word='Welches Wort sollen wir als Nächstes machen? Schreib es in die Kommentare.',
            tags='#koreanischlernen #koreanisch #hangul'),
}

# meanings of the vetted words: order zh, hi, es, ar, fr, bn, pt, id, ur, ru, ja, de
_ML = ['zh', 'hi', 'es', 'ar', 'fr', 'bn', 'pt', 'id', 'ur', 'ru', 'ja', 'de']
_MEAN = {
 '사랑해': ['我爱你', 'मुझे तुमसे प्यार है', 'Te quiero', 'أحبك', 'Je t’aime', 'আমি তোমাকে ভালোবাসি', 'Eu te amo', 'Aku cinta kamu', 'مجھے تم سے محبت ہے', 'Я тебя люблю', '愛してる', 'Ich liebe dich'],
 '화이팅': ['加油！', 'तुम कर सकते हो!', '¡Tú puedes!', 'تستطيع فعلها!', 'Tu peux le faire !', 'তুমি পারবে!', 'Você consegue!', 'Semangat!', 'تم کر سکتے ہو!', 'Ты сможешь!', 'がんばれ！', 'Du schaffst das!'],
 '대박': ['太棒了！', 'कमाल है!', '¡Increíble!', 'رائع!', 'Génial !', 'দারুণ!', 'Incrível!', 'Keren banget!', 'زبردست!', 'Круто!', 'すごい！', 'Krass!'],
 '언니': ['姐姐（女生用）', 'बड़ी बहन (लड़कियाँ कहती हैं)', 'Hermana mayor (lo dicen las chicas)', 'الأخت الكبرى (تقولها الفتيات)', 'Grande sœur (dit par une fille)', 'বড় বোন (মেয়েরা বলে)', 'Irmã mais velha (dito por meninas)', 'Kakak perempuan (dipakai perempuan)', 'بڑی بہن (لڑکیاں کہتی ہیں)', 'Старшая сестра (так говорят девушки)', 'お姉さん（女性が使う）', 'Ältere Schwester (sagen Mädchen)'],
 '오빠': ['哥哥（女生用）', 'बड़ा भाई (लड़कियाँ कहती हैं)', 'Hermano mayor (lo dicen las chicas)', 'الأخ الأكبر (تقولها الفتيات)', 'Grand frère (dit par une fille)', 'বড় ভাই (মেয়েরা বলে)', 'Irmão mais velho (dito por meninas)', 'Kakak laki-laki (dipakai perempuan)', 'بڑا بھائی (لڑکیاں کہتی ہیں)', 'Старший брат (так говорят девушки)', 'お兄さん（女性が使う）', 'Älterer Bruder (sagen Mädchen)'],
 '감사합니다': ['谢谢', 'धन्यवाद', 'Gracias', 'شكرًا', 'Merci', 'ধন্যবাদ', 'Obrigado', 'Terima kasih', 'شکریہ', 'Спасибо', 'ありがとうございます', 'Danke'],
 '진짜': ['真的吗？', 'सच में?', '¿En serio?', 'حقًا؟', 'Vraiment ?', 'সত্যি?', 'Sério?', 'Serius?', 'سچ میں؟', 'Правда?', '本当に？', 'Echt jetzt?'],
 '귀여워': ['好可爱！', 'कितना प्यारा!', '¡Qué lindo!', 'لطيف جدًا!', 'Trop mignon !', 'কী মিষ্টি!', 'Que fofo!', 'Lucu banget!', 'کتنا پیارا!', 'Так мило!', 'かわいい！', 'So süß!'],
 '보고 싶어': ['我想你', 'मुझे तुम्हारी याद आती है', 'Te extraño', 'اشتقت إليك', 'Tu me manques', 'তোমাকে মিস করি', 'Estou com saudade', 'Aku kangen kamu', 'مجھے تمہاری یاد آتی ہے', 'Я скучаю по тебе', '会いたい', 'Ich vermisse dich'],
 '아이고': ['哎呀！', 'अरे बाप रे!', '¡Ay, Dios!', 'يا إلهي!', 'Oh là là !', 'হায় রে!', 'Ai, meu Deus!', 'Aduh!', 'ارے بابا!', 'Ой-ой!', 'あらまあ！', 'Oje!'],
 '맛있어': ['好吃！', 'बहुत स्वादिष्ट!', '¡Está delicioso!', 'لذيذ!', 'C’est délicieux !', 'খুব মজা!', 'Está delicioso!', 'Enak!', 'بہت مزیدار!', 'Вкусно!', 'おいしい！', 'Lecker!'],
 '미안해': ['对不起', 'माफ़ करना', 'Lo siento', 'آسف', 'Désolé', 'দুঃখিত', 'Desculpa', 'Maaf', 'معاف کرنا', 'Прости', 'ごめんね', 'Tut mir leid'],
 '괜찮아': ['没关系', 'कोई बात नहीं', 'Está bien', 'لا بأس', 'Ça va', 'ঠিক আছে', 'Tudo bem', 'Nggak apa-apa', 'کوئی بات نہیں', 'Всё хорошо', '大丈夫', 'Alles gut'],
 '잘 자': ['晚安', 'शुभ रात्रि', 'Buenas noches', 'تصبح على خير', 'Bonne nuit', 'শুভ রাত্রি', 'Boa noite', 'Selamat tidur', 'شب بخیر', 'Спокойной ночи', 'おやすみ', 'Gute Nacht'],
 '안녕': ['你好 / 再见', 'हाय / बाय', 'Hola / Adiós', 'مرحبًا / وداعًا', 'Salut', 'হাই / বাই', 'Oi / Tchau', 'Hai / Dah', 'ہائے / بائے', 'Привет / Пока', 'やあ／バイバイ', 'Hallo / Tschüss'],
 '배고파': ['我饿了', 'मुझे भूख लगी है', 'Tengo hambre', 'أنا جائع', 'J’ai faim', 'আমার খিদে পেয়েছে', 'Estou com fome', 'Aku lapar', 'مجھے بھوک لگی ہے', 'Хочу есть', 'お腹すいた', 'Ich hab Hunger'],
 '행복해': ['我好幸福', 'मैं खुश हूँ', '¡Qué feliz!', 'أنا سعيد', 'Quel bonheur !', 'আমি খুশি', 'Estou feliz', 'Aku bahagia', 'میں خوش ہوں', 'Как я счастлив(а)!', '幸せ！', 'Ich bin so glücklich!'],
 '친구': ['朋友', 'दोस्त', 'Amigo', 'صديق', 'Ami', 'বন্ধু', 'Amigo', 'Teman', 'دوست', 'Друг', '友だち', 'Freund'],
 '짱': ['最棒！', 'सबसे बढ़िया!', '¡El mejor!', 'الأفضل!', 'Le top !', 'সেরা!', 'O melhor!', 'Terbaik!', 'سب سے بہترین!', 'Лучший!', '最高！', 'Der Beste!'],
 '헐': ['天哪！', 'हैं?!', '¡¿Qué?!', 'ماذا؟!', 'Quoi ?!', 'কী বলো!', 'Como assim?!', 'Hah?!', 'ہیں؟!', 'Ого!', 'えっ？！', 'Hä?!'],
 '출구': ['出口', 'निकास', 'Salida', 'مخرج', 'Sortie', 'বাহির', 'Saída', 'Pintu keluar', 'خارجی راستہ', 'Выход', '出口', 'Ausgang'],
 '입구': ['入口', 'प्रवेश', 'Entrada', 'مدخل', 'Entrée', 'প্রবেশপথ', 'Entrada', 'Pintu masuk', 'داخلی راستہ', 'Вход', '入口', 'Eingang'],
 '화장실': ['洗手间', 'शौचालय', 'Baño', 'دورة المياه', 'Toilettes', 'টয়লেট', 'Banheiro', 'Toilet', 'واش روم', 'Туалет', 'トイレ', 'Toilette'],
 '지하철': ['地铁', 'मेट्रो', 'Metro', 'مترو الأنفاق', 'Métro', 'মেট্রো', 'Metrô', 'Kereta bawah tanah', 'میٹرو', 'Метро', '地下鉄', 'U-Bahn'],
 '김밥': ['紫菜包饭', 'गिमबाप (कोरियन राइस रोल)', 'Gimbap', 'كيمباب', 'Gimbap', 'কিমবাপ', 'Gimbap', 'Gimbap', 'کمباپ', 'Кимпаб', 'キンパ', 'Gimbap'],
 '떡볶이': ['辣炒年糕', 'तोक्बोक्की (मसालेदार राइस केक)', 'Tteokbokki', 'تيوكبوكي', 'Tteokbokki', 'তোকবোক্কি', 'Tteokbokki', 'Tteokbokki', 'ٹوکبوکی', 'Токпокки', 'トッポッキ', 'Tteokbokki'],
 '비빔밥': ['拌饭', 'बिबिमबाप', 'Bibimbap', 'بيبيمباب', 'Bibimbap', 'বিবিমবাপ', 'Bibimbap', 'Bibimbap', 'بی بم باپ', 'Пибимпап', 'ビビンバ', 'Bibimbap'],
 '라면': ['韩国拉面', 'रामयन (कोरियन नूडल्स)', 'Ramyeon', 'رامين', 'Ramyeon', 'রামিয়ন', 'Ramyeon', 'Ramyeon', 'رامین', 'Рамён', '韓国ラーメン', 'Ramyeon'],
 '물': ['水', 'पानी', 'Agua', 'ماء', 'Eau', 'পানি', 'Água', 'Air', 'پانی', 'Вода', '水', 'Wasser'],
 '커피': ['咖啡', 'कॉफ़ी', 'Café', 'قهوة', 'Café', 'কফি', 'Café', 'Kopi', 'کافی', 'Кофе', 'コーヒー', 'Kaffee'],
 '편의점': ['便利店', 'सुविधा स्टोर', 'Tienda de conveniencia', 'بقالة', 'Supérette', 'কনভিনিয়েন্স স্টোর', 'Loja de conveniência', 'Minimarket', 'جنرل اسٹور', 'Круглосуточный магазин', 'コンビニ', 'Spätkauf / Minimarkt'],
 '계산서': ['账单', 'बिल', 'La cuenta', 'الفاتورة', 'L’addition', 'বিল', 'A conta', 'Bon', 'بل', 'Счёт', 'お会計', 'Die Rechnung'],
 '약국': ['药店', 'दवा की दुकान', 'Farmacia', 'صيدلية', 'Pharmacie', 'ফার্মেসি', 'Farmácia', 'Apotek', 'فارمیسی', 'Аптека', '薬局', 'Apotheke'],
 '은행': ['银行', 'बैंक', 'Banco', 'بنك', 'Banque', 'ব্যাংক', 'Banco', 'Bank', 'بینک', 'Банк', '銀行', 'Bank'],
 '병원': ['医院', 'अस्पताल', 'Hospital', 'مستشفى', 'Hôpital', 'হাসপাতাল', 'Hospital', 'Rumah sakit', 'ہسپتال', 'Больница', '病院', 'Krankenhaus'],
 '공항': ['机场', 'हवाई अड्डा', 'Aeropuerto', 'مطار', 'Aéroport', 'বিমানবন্দর', 'Aeroporto', 'Bandara', 'ہوائی اڈہ', 'Аэропорт', '空港', 'Flughafen'],
 '호텔': ['酒店', 'होटल', 'Hotel', 'فندق', 'Hôtel', 'হোটেল', 'Hotel', 'Hotel', 'ہوٹل', 'Отель', 'ホテル', 'Hotel'],
 '시장': ['市场', 'बाज़ार', 'Mercado', 'سوق', 'Marché', 'বাজার', 'Mercado', 'Pasar', 'بازار', 'Рынок', '市場', 'Markt'],
 '버스': ['公交车', 'बस', 'Autobús', 'حافلة', 'Bus', 'বাস', 'Ônibus', 'Bus', 'بس', 'Автобус', 'バス', 'Bus'],
 '택시': ['出租车', 'टैक्सी', 'Taxi', 'تاكسي', 'Taxi', 'ট্যাক্সি', 'Táxi', 'Taksi', 'ٹیکسی', 'Такси', 'タクシー', 'Taxi'],
}

# common local first names -> usual Korean spelling (외래어 표기). Shown in Latin letters on screen.
NAMES = {
 'zh-Hant': [('Wei', '웨이'), ('Mei', '메이'), ('Lin', '린'), ('Xinyi', '신이'), ('Jiahao', '자하오'), ('Yuting', '위팅'), ('Hao', '하오'), ('Ling', '링')],
 'hi': [('Priya', '프리야'), ('Aarav', '아라브'), ('Ananya', '아난야'), ('Rahul', '라훌'), ('Neha', '네하'), ('Rohan', '로한'), ('Riya', '리야'), ('Diya', '디야')],
 'es': [('Valentina', '발렌티나'), ('Mateo', '마테오'), ('Camila', '카밀라'), ('Santiago', '산티아고'), ('Lucia', '루시아'), ('Diego', '디에고'), ('Martina', '마르티나'), ('Isabella', '이사벨라')],
 'ar': [('Fatima', '파티마'), ('Omar', '오마르'), ('Layla', '라일라'), ('Youssef', '유세프'), ('Mariam', '마리암'), ('Ahmed', '아흐메드'), ('Nour', '누르'), ('Ali', '알리')],
 'fr': [('Lea', '레아'), ('Hugo', '위고'), ('Chloe', '클로에'), ('Louis', '루이'), ('Manon', '마농'), ('Jules', '쥘'), ('Camille', '카미유'), ('Emma', '에마')],
 'bn': [('Ayesha', '아이샤'), ('Rahim', '라힘'), ('Nusrat', '누스라트'), ('Tanvir', '탄비르'), ('Sadia', '사디아'), ('Arif', '아리프'), ('Rafi', '라피'), ('Mim', '밈')],
 'pt': [('Ana', '아나'), ('Joao', '주앙'), ('Beatriz', '베아트리스'), ('Pedro', '페드루'), ('Larissa', '라리사'), ('Gustavo', '구스타부'), ('Julia', '줄리아'), ('Rafael', '하파엘')],
 'id': [('Dewi', '데위'), ('Rizky', '리즈키'), ('Ayu', '아유'), ('Budi', '부디'), ('Siti', '시티'), ('Fajar', '파자르'), ('Intan', '인탄'), ('Bagus', '바구스')],
 'ur': [('Hamza', '함자'), ('Zainab', '자이나브'), ('Bilal', '빌랄'), ('Hira', '히라'), ('Usman', '우스만'), ('Sana', '사나'), ('Areeba', '아리바'), ('Danish', '다니시')],
 'ru': [('Anastasia', '아나스타시야'), ('Dmitry', '드미트리'), ('Ivan', '이반'), ('Polina', '폴리나'), ('Alexei', '알렉세이'), ('Daria', '다리야'), ('Artem', '아르툠'), ('Ksenia', '크세니야')],
 'ja': [('Yui', '유이'), ('Haruto', '하루토'), ('Sakura', '사쿠라'), ('Ren', '렌'), ('Hina', '히나'), ('Sota', '소타'), ('Yuki', '유키'), ('Aoi', '아오이')],
 'de': [('Mia', '미아'), ('Leon', '레온'), ('Hannah', '한나'), ('Lukas', '루카스'), ('Lena', '레나'), ('Felix', '펠릭스'), ('Paul', '파울'), ('Marie', '마리')],
}

def _key(lang):
    return 'zh' if lang.startswith('zh') else lang

def _conv(lang, s):
    return _s2t(s) if lang == 'zh-Hant' else s

def ui(lang):
    if lang in (None, '', 'en'): return {}
    d = {k: _conv(lang, v) for k, v in _UI[_key(lang)].items()}
    if lang in RTL: d['rtl'] = True
    d.pop('ja', None)
    if lang == 'ja': d['ja'] = True
    return d

def meta(lang):
    return {k: _conv(lang, v) for k, v in _META[_key(lang)].items()}

def mean(lang, ko):
    row = _MEAN.get(ko)
    return _conv(lang, row[_ML.index(_key(lang))]) if row else None
