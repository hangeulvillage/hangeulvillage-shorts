// Post + pin a comment on the current youtube.com/watch page as the expected channel.
// Usage (javascript_tool): paste this file, then: await ytPin('Hangeul Village', 'text')
// Returns {status: 'pinned'|'already_pinned'|'wrong_identity'|'error', ...}. Never posts as the wrong channel.
async function ytPin(expectAuthor, text) {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  for (let i = 0; i < 15 && !document.querySelector('ytd-comments #simplebox-placeholder'); i++) {
    document.querySelector('ytd-comments')?.scrollIntoView(); window.scrollBy(0, 400); await sleep(1000);
  }
  await sleep(1500);
  const threads = () => [...document.querySelectorAll('ytd-comment-thread-renderer')];
  if (threads().some(t => /님이 고정함|Pinned by/.test(t.innerText.slice(0, 80)))) return {status: 'already_pinned'};
  document.querySelector('ytd-comments #simplebox-placeholder').scrollIntoView({block: 'center'}); await sleep(800);
  let author = '';
  for (let i = 0; i < 8 && !author; i++) { author = document.querySelector('ytd-comments img')?.alt || ''; if (!author) await sleep(1000); }
  if (author !== expectAuthor) return {status: 'wrong_identity', author};
  document.querySelector('ytd-comments #simplebox-placeholder').click(); await sleep(1200);
  const ed = document.querySelector('ytd-comments #contenteditable-root'); ed.focus();
  document.execCommand('insertText', false, text); await sleep(500);
  const plain = x => x.replace(/[^\p{L}\p{N}]/gu, '');  // emoji render as <img>, so compare letters/digits only
  if (plain(ed.innerText) !== plain(text)) return {status: 'error', why: 'text mismatch', got: ed.innerText};
  document.querySelector('ytd-comments #submit-button button').click();
  let mine;
  for (let i = 0; i < 10 && !mine; i++) { await sleep(1000); mine = threads().find(t => plain(t.innerText).includes(plain(text).slice(0, 25))); }
  if (!mine) return {status: 'error', why: 'comment not visible after posting'};
  mine.scrollIntoView({block: 'center'}); await sleep(500);
  mine.querySelector('#action-menu button').click(); await sleep(1200);
  const item = [...document.querySelectorAll('ytd-menu-popup-renderer tp-yt-paper-item')]
    .find(x => ['고정', 'Pin'].includes(x.innerText.trim()) && x.getBoundingClientRect().width > 0);
  if (!item) return {status: 'error', why: 'pin menu item not found'};
  item.click(); await sleep(1500);
  const dlg = [...document.querySelectorAll('yt-confirm-dialog-renderer')].find(x => x.getBoundingClientRect().width > 0);
  const btn = dlg && (dlg.querySelector('#confirm-button button') || dlg.querySelector('#confirm-button'));
  if (!btn) return {status: 'error', why: 'confirm dialog not found'};
  btn.click(); await sleep(2500);
  const ok = threads().some(t => /님이 고정함|Pinned by/.test(t.innerText.slice(0, 80)) && plain(t.innerText).includes(plain(text).slice(0, 25)));
  return {status: ok ? 'pinned' : 'error', why: ok ? '' : 'pin not confirmed'};
}
