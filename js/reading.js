(function () {
  'use strict';
  const KEY = 'prenatal-story:read:v1';
  let readIds = new Set();
  let memoryOnly = false;
  let feedbackTimer;
  const feedback = document.getElementById('read-feedback');
  const note = document.getElementById('storage-note');
  const buttons = Array.from(document.querySelectorAll('[data-read-toggle]'));

  function announce(message, persistent) {
    if (!feedback) return;
    clearTimeout(feedbackTimer);
    feedback.textContent = message;
    feedback.classList.add('visible');
    if (!persistent) feedbackTimer = setTimeout(() => feedback.classList.remove('visible'), 4500);
  }

  function unavailable() {
    memoryOnly = true;
    const message = '当前浏览器无法保存已读记录，标记仅本次页面有效。请允许网站本地存储后重试。';
    if (note) note.textContent = message;
    announce(message, true);
  }

  function load() {
    if (memoryOnly) return;
    let raw;
    try { raw = localStorage.getItem(KEY); }
    catch (_) { unavailable(); return; }
    if (raw === null) { readIds = new Set(); return; }
    try {
      const data = JSON.parse(raw);
      if (!data || data.version !== 1 || !Array.isArray(data.readIds) ||
          !data.readIds.every(id => typeof id === 'string' && /^[1-9]\d*$/.test(id))) {
        throw new Error('Invalid read record');
      }
      readIds = new Set(data.readIds);
    } catch (_) {
      readIds = new Set();
      const message = '已读记录格式异常，暂时显示为空。可重新标记，故事阅读不受影响。';
      if (note) note.textContent = message;
      announce(message, true);
    }
  }

  function render() {
    buttons.forEach(button => {
      const read = readIds.has(button.dataset.readToggle);
      button.hidden = false;
      button.classList.toggle('is-read', read);
      button.setAttribute('aria-pressed', String(read));
      button.setAttribute('aria-label', (read ? '撤销已读：' : '标为已读：') + button.dataset.storyTitle);
      button.querySelector('[data-read-label]').textContent = read ? '已读 · 撤销' : '标为已读';
    });
    document.querySelectorAll('.card[data-id]').forEach(card => {
      card.classList.toggle('is-read', readIds.has(card.dataset.id));
    });
    const filters = document.querySelector('.reading-filters');
    if (filters) filters.hidden = false;
    document.dispatchEvent(new CustomEvent('story:readchange'));
  }

  buttons.forEach(button => button.addEventListener('click', () => {
    // Merge the latest saved state before changing one ID, including other tabs' edits.
    load();
    const id = button.dataset.readToggle;
    const nextRead = !readIds.has(id);
    if (nextRead) readIds.add(id);
    else readIds.delete(id);
    if (!memoryOnly) {
      try {
        localStorage.setItem(KEY, JSON.stringify({ version: 1, readIds: Array.from(readIds).sort((a, b) => Number(a) - Number(b)) }));
      } catch (_) { unavailable(); }
    }
    render();
    if (!memoryOnly) announce(nextRead ? '已标记《' + button.dataset.storyTitle + '》为已读，可再次点击撤销。' : '已撤销《' + button.dataset.storyTitle + '》的已读标记。');
    if (button.closest('.card')?.classList.contains('is-hidden')) {
      const next = document.querySelector('.card:not(.is-hidden) [data-read-toggle]') || document.querySelector('.state-filter.active');
      if (next) next.focus({ preventScroll: true });
    }
  }));

  window.StoryReading = { isRead: id => readIds.has(String(id)) };
  window.addEventListener('storage', event => {
    if (event.key === KEY || event.key === null) { load(); render(); }
  });
  window.addEventListener('pageshow', () => { load(); render(); });
  load();
  render();

  const header = document.querySelector('.site-header');
  if (header) {
    const scroll = () => header.classList.toggle('scrolled', scrollY > 8);
    window.addEventListener('scroll', scroll, { passive: true });
    scroll();
  }
})();
