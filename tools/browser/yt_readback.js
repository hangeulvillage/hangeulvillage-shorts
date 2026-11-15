// Paste into javascript_tool in the YouTube Studio upload dialog BEFORE pressing 예약/게시.
// Reads back what the form really holds (React ignores JS-set values, so fields are typed with real keys;
// this checks the typing landed). Pass EXPECT_TITLE as a JS string. Returns JSON; ok=false -> fix before saving.
(() => {
  const EXPECT_TITLE = __EXPECT_TITLE__;
  const boxes = [...document.querySelectorAll('ytcp-uploads-dialog #textbox, ytcp-video-metadata-editor #textbox')];
  const title = (boxes[0]?.innerText || '').trim(), desc = (boxes[1]?.innerText || '').trim();
  const kidsNo = document.querySelector('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]');
  const r = {title, title_ok: title === EXPECT_TITLE.trim(), desc_len: desc.length,
             not_for_kids: kidsNo ? kidsNo.hasAttribute('checked') || kidsNo.getAttribute('aria-checked') === 'true' : null};
  r.ok = r.title_ok && r.desc_len > 50 && r.not_for_kids !== false;
  return JSON.stringify(r);
})();
