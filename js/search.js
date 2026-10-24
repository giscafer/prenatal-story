
(function () {
  const grid = document.getElementById('story-grid');
  if (!grid) return;
  const cards = Array.from(grid.querySelectorAll('.card'));
  const input = document.getElementById('story-search');
  const chips = Array.from(document.querySelectorAll('.chip'));
  const meta = document.getElementById('result-meta');
  const empty = document.getElementById('empty-state');
  const params = new URLSearchParams(location.search);
  let activeCat = params.get('cat') || 'all';
  let query = (params.get('q') || '').trim();

  function normalize(s) {
    return (s || '').toLowerCase().replace(/\s+/g, '');
  }

  function apply() {
    const q = normalize(query);
    let shown = 0;
    cards.forEach(card => {
      const cat = card.getAttribute('data-cat') || '';
      const hay = card.getAttribute('data-search') || '';
      const catOk = activeCat === 'all' || cat === activeCat;
      const qOk = !q || hay.indexOf(q) !== -1;
      const ok = catOk && qOk;
      card.classList.toggle('is-hidden', !ok);
      if (ok) shown++;
    });
    chips.forEach(c => {
      c.classList.toggle('active', c.getAttribute('data-cat') === activeCat);
    });
    if (meta) {
      const parts = [];
      if (activeCat !== 'all') {
        const label = (chips.find(c => c.getAttribute('data-cat') === activeCat) || {}).textContent || activeCat;
        parts.push('分类：' + label.replace(/\d+/g, '').trim());
      }
      if (query) parts.push('搜索「' + query + '」');
      parts.push('显示 ' + shown + ' / ' + cards.length + ' 篇');
      meta.textContent = parts.join(' · ');
    }
    if (empty) empty.classList.toggle('show', shown === 0);
    const url = new URL(location.href);
    if (activeCat === 'all') url.searchParams.delete('cat');
    else url.searchParams.set('cat', activeCat);
    if (!query) url.searchParams.delete('q');
    else url.searchParams.set('q', query);
    history.replaceState(null, '', url.pathname + url.search + (url.hash || ''));
  }

  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      activeCat = chip.getAttribute('data-cat') || 'all';
      apply();
    });
  });

  if (input) {
    input.value = query;
    let t;
    input.addEventListener('input', () => {
      clearTimeout(t);
      t = setTimeout(() => {
        query = input.value.trim();
        apply();
      }, 120);
    });
  }

  apply();
})();
