// Run on studio.youtube.com/video/<id>/translations (Korean UI) after setting window.HV_TR = [[studioName, title, desc], ...].
// For each language: add it if missing, open its "title and description" editor, fill, publish. Result in window.HV_LOG.
(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const vis = e => e && e.offsetParent !== null;
  const rows = () => [...document.querySelectorAll('ytgn-video-translation-row')];
  const rowOf = name => rows().find(r => ((r.innerText || '').split('\n')[0] || '').trim() === name);
  const metaCell = r => r.querySelector('ytgn-video-translation-cell-metadata');
  const log = [];
  for (const [name, title, desc] of window.HV_TR) {
    try {
      let row = rowOf(name);
      if (row && /게시됨/.test(metaCell(row)?.innerText || '')) { log.push([name, 'already']); continue; }
      if (!row) {
        document.querySelector('#add-translations-button').click(); await sleep(1000);
        const opt = [...document.querySelectorAll('tp-yt-paper-item, [role=option]')].find(o => o.innerText.trim() === name);
        if (!opt) { log.push([name, 'no option']); document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })); continue; }
        opt.click(); await sleep(1800); row = rowOf(name);
      }
      if (!row) { log.push([name, 'no row']); continue; }
      const hc = metaCell(row).querySelector('ytgn-video-translation-hover-cell') || metaCell(row);
      for (const ev of ['mouseenter', 'mouseover', 'mousemove']) hc.dispatchEvent(new MouseEvent(ev, { bubbles: true }));
      await sleep(500);
      const add = metaCell(row).querySelector('#metadata-add');
      if (!add) { log.push([name, 'no add button']); continue; }
      add.click(); await sleep(1800);
      const tas = [...document.querySelectorAll('textarea')].filter(e => vis(e) && !e.closest('[disabled]'));
      if (tas.length < 2) { log.push([name, 'no editor']); continue; }
      const set = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
      const put = (el, v) => { el.focus(); set.call(el, v); el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); };
      put(tas[0], title); put(tas[1], desc); await sleep(600);
      const pub = [...document.querySelectorAll('ytcp-button, button')].find(b => vis(b) && b.innerText.trim() === '게시');
      if (!pub) { log.push([name, 'no publish']); continue; }
      pub.click(); await sleep(2500);
      log.push([name, /게시됨/.test(metaCell(rowOf(name))?.innerText || '') ? 'published' : 'check']);
    } catch (e) { log.push([name, 'error ' + e.message]); }
  }
  window.HV_LOG = log;
})();
