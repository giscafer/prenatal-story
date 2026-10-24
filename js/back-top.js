
(function () {
  var btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'back-top';
  btn.setAttribute('aria-label', '回到顶部');
  btn.setAttribute('title', '回到顶部');
  btn.innerHTML = '<span class="back-top-icon" aria-hidden="true">🚀</span>';
  document.body.appendChild(btn);

  var rocket = document.createElement('div');
  rocket.className = 'rocket-fly';
  rocket.setAttribute('aria-hidden', 'true');
  rocket.textContent = '🚀';
  document.body.appendChild(rocket);

  var launching = false;

  function onScroll() {
    if (window.scrollY > 320) btn.classList.add('is-visible');
    else btn.classList.remove('is-visible');
  }

  function launchRocket() {
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
