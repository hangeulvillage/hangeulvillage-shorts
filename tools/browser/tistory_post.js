// Paste into javascript_tool on the Tistory editor page (…/manage/newpost). Replace __HTML__ with post.html
// as a JS string literal (JSON.stringify of the file). Returns a JSON report.
// AFTER this: press End, space, BackSpace with real keystrokes, or Tistory saves an empty body (lesson 2026-11-15).
(() => {
  window.alert = m => console.log('[alert suppressed]', m);   // alerts freeze the tab
  window.confirm = () => true;
  const html = __HTML__;
  const ed = window.tinymce && tinymce.activeEditor;
  if (!ed) return JSON.stringify({ok: false, why: 'no tinymce editor: is this the newpost page in basic mode?'});
  ed.focus();
  ed.execCommand('mceInsertContent', false, html);
  const len = ed.getContent().length;
  return JSON.stringify({ok: len > html.length * 0.8, body_len: len, expected_min: Math.round(html.length * 0.8),
                         next: 'real keys End, space, BackSpace; then set title/labels; then 예약 발행'});
})();
