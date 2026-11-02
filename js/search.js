(function () {
  'use strict';
  const grid = document.getElementById('story-grid');
  if (!grid) return;
  const cards = Array.from(grid.querySelectorAll('.card'));
  const input = document.getElementById('story-search');
  const chips = Array.from(document.querySelectorAll('[data-cat].chip'));
  const stateButtons = Array.from(document.querySelectorAll('[data-state]'));
  const meta = document.getElementById('result-meta');
  const empty = document.getElementById('empty-state');
  const summary = document.getElementById('reading-summary');
  let activeCat = 'all';
  let activeState = 'all';
  let query = '';
  let timer;
  const normalize = text => (text || '').toLowerCase().replace(/\s+/g, '');
  const isRead = card => window.StoryReading?.isRead(card.dataset.id) || false;

  function apply(updateUrl = true) {
    const q = normalize(query);
    let shown = 0, categoryRead = 0, categoryTotal = 0;
    const totalRead = cards.filter(isRead).length;
    cards.forEach(card => {
      const read = isRead(card);
      const matches = (activeCat === 'all' || card.dataset.cat === activeCat) && (!q || card.dataset.search.includes(q));
      if (matches) { categoryTotal++; if (read) categoryRead++; }
      const visible = matches && (activeState === 'all' || (activeState === 'read' ? read : !read));
      card.classList.toggle('is-hidden', !visible);
      if (visible) shown++;
    });
    chips.forEach(chip => {
      const active = chip.dataset.cat === activeCat;
      chip.classList.toggle('active', active);
      chip.setAttribute('aria-pressed', String(active));
    });
    stateButtons.forEach(button => {
      const active = button.dataset.state === activeState;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    const counts = { all: categoryTotal, unread: categoryTotal - categoryRead, read: categoryRead };
    document.querySelectorAll('[data-state-count]').forEach(span => { span.textContent = counts[span.dataset.stateCount]; });
    summary.hidden = false;
    summary.textContent = '已读 ' + totalRead + ' / ' + cards.length + ' 篇';
    const parts = [];
    if (activeCat !== 'all') {
      const chip = chips.find(item => item.dataset.cat === activeCat);
      parts.push(chip.firstChild.textContent.trim());
    }
    if (query) parts.push('搜索「' + query + '」');
    if (activeState !== 'all') parts.push(activeState === 'read' ? '已读故事' : '未读故事');
    parts.push('显示 ' + shown + ' 篇');
    meta.textContent = parts.join(' · ');
    empty.classList.toggle('show', shown === 0);
    document.getElementById('empty-title').textContent = activeState === 'read' && !totalRead ? '还没有已读记录' : activeState === 'unread' && categoryTotal > 0 && categoryRead === categoryTotal ? '这些故事都读过了' : '没有找到匹配的故事';
    document.getElementById('empty-description').textContent = activeState === 'read' && !totalRead ? '读完后点击「标为已读」，下次就能在这里找到。' : '换个关键词或分类，也可以重置筛选再挑一篇。';
    if (updateUrl) {
      const url = new URL(location.href);
      [['cat', activeCat, 'all'], ['state', activeState, 'all'], ['q', query, '']].forEach(([name, value, fallback]) => {
        if (value === fallback) url.searchParams.delete(name);
        else url.searchParams.set(name, value);
      });
      try { history.replaceState(null, '', url.pathname + url.search + url.hash); }
      catch (_) { /* Filtering also works when opened directly as a local file. */ }
    }
  }

  function restoreUrl() {
    clearTimeout(timer);
    const params = new URLSearchParams(location.search);
    activeCat = chips.some(chip => chip.dataset.cat === params.get('cat')) ? params.get('cat') : 'all';
    activeState = ['read', 'unread'].includes(params.get('state')) ? params.get('state') : 'all';
    query = (params.get('q') || '').trim();
    input.value = query;
    apply();
  }
  chips.forEach(chip => chip.addEventListener('click', () => { activeCat = chip.dataset.cat; apply(); }));
  stateButtons.forEach(button => button.addEventListener('click', () => { activeState = button.dataset.state; apply(); }));
  input.addEventListener('input', () => {
    clearTimeout(timer);
    timer = setTimeout(() => { query = input.value.trim(); apply(); }, 100);
  });
  document.getElementById('reset-filters').addEventListener('click', () => {
    clearTimeout(timer);
    activeCat = 'all'; activeState = 'all'; query = ''; input.value = '';
    apply(); input.focus({ preventScroll: true });
  });
  document.addEventListener('story:readchange', () => apply(false));
  window.addEventListener('popstate', restoreUrl);
  restoreUrl();
})();
