
(function () {
  var btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'back-top';
  btn.setAttribute('aria-label', '回到顶部');
  btn.setAttribute('title', '回到顶部');
  btn.innerHTML = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="m6 12 6-6 6 6M12 6v14"/></svg>';
  document.body.appendChild(btn);

  var rocket = document.createElement('div');
  rocket.className = 'rocket-fly';
  rocket.setAttribute('aria-hidden', 'true');
  rocket.innerHTML = '<svg width="30" height="36" viewBox="0 0 24 28" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 2c-5 4-6 10-4 17h8c2-7 1-13-4-17ZM7 12l-4 7 5-1m9-6 4 7-5-1M10 22l2 4 2-4"/><circle cx="12" cy="11" r="2"/></svg>';
  document.body.appendChild(rocket);

  var launching = false;

  function onScroll() {
    if (window.scrollY > 320) btn.classList.add('is-visible');
    else btn.classList.remove('is-visible');
  }

  function launchRocket() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      window.scrollTo({ top: 0, behavior: 'instant' });
      return;
    }
    if (launching) return;
    launching = true;
    var rect = btn.getBoundingClientRect();
    rocket.style.setProperty('--rx', (rect.left + rect.width / 2) + 'px');
    rocket.style.setProperty('--ry', (window.innerHeight - rect.top) + 'px');
    rocket.classList.remove('is-launching');
    void rocket.offsetWidth;
    rocket.classList.add('is-launching');
    window.scrollTo({ top: 0, behavior: 'smooth' });
    setTimeout(function () {
      rocket.classList.remove('is-launching');
      launching = false;
    }, 1100);
  }

  btn.addEventListener('click', launchRocket);
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();
