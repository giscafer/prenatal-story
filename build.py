#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build prenatal education stories static site (100 stories, categories, search)."""
import json, html
from pathlib import Path
from collections import OrderedDict

ROOT = Path(__file__).resolve().parent
STORIES_DIR = ROOT / "stories"
CSS_DIR = ROOT / "css"
JS_DIR = ROOT / "js"

STORIES = json.loads((ROOT / "stories.json").read_text(encoding="utf-8"))
assert len(STORIES) == 100, len(STORIES)

CATEGORY_ORDER = OrderedDict([
    ("nature", "自然与四季"),
    ("animals", "动物朋友"),
    ("family", "家人的爱"),
    ("virtue", "勇气与善良"),
    ("folklore", "中国传说改写"),
    ("lullaby", "睡前安抚"),
])

CSS = r"""
:root {
  --bg: #faf6f1;
  --bg-soft: #f3ebe3;
  --card: #fffdf9;
  --ink: #3d3229;
  --ink-soft: #6b5a4c;
  --muted: #9a8776;
  --accent: #c4785a;
  --accent-soft: #e8b4a0;
  --line: #e8ddd2;
  --shadow: 0 10px 30px rgba(61, 50, 41, 0.06);
  --radius: 18px;
  --font: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", "Microsoft YaHei",
    "Source Han Sans SC", sans-serif;
  --serif: "Songti SC", "Noto Serif SC", "STSong", "SimSun", serif;
  --max: 720px;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: var(--font);
  color: var(--ink);
  background:
    radial-gradient(1200px 600px at 10% -10%, #f8e7dc 0%, transparent 55%),
    radial-gradient(900px 500px at 100% 0%, #efe4d8 0%, transparent 50%),
    var(--bg);
  line-height: 1.85;
  font-size: 17px;
  -webkit-font-smoothing: antialiased;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.wrap { width: min(100% - 2rem, 1100px); margin: 0 auto; }
.site-header {
  padding: 1.25rem 0 0.5rem;
  position: sticky; top: 0; z-index: 10;
  backdrop-filter: blur(12px);
  background: rgba(250, 246, 241, 0.85);
  border-bottom: 1px solid transparent;
}
.site-header.scrolled { border-bottom-color: var(--line); }
.nav {
  display: flex; align-items: center; justify-content: space-between; gap: 1rem;
}
.brand {
  display: flex; align-items: center; gap: 0.7rem; color: inherit; text-decoration: none;
}
.brand:hover { text-decoration: none; }
.logo {
  width: 40px; height: 40px; border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 6px 16px rgba(196, 120, 90, 0.22);
  background: #f7ebe3;
  display: block;
}
.logo img {
  width: 100%; height: 100%;
  object-fit: cover;
  display: block;
}
.brand-text strong { display: block; font-size: 1.05rem; letter-spacing: 0.04em; }
.brand-text span { font-size: 0.78rem; color: var(--muted); }
.nav-links { display: flex; gap: 1rem; font-size: 0.92rem; color: var(--ink-soft); flex-wrap: wrap; }
.hero { padding: 3.2rem 0 1.8rem; text-align: center; }
.hero .eyebrow {
  display: inline-block;
  padding: 0.25rem 0.8rem;
  border-radius: 999px;
  background: #f3e0d6;
  color: var(--accent);
  font-size: 0.85rem;
  margin-bottom: 1rem;
}
.hero h1 {
  font-family: var(--serif);
  font-weight: 600;
  font-size: clamp(1.9rem, 4vw, 2.7rem);
  line-height: 1.35;
  margin: 0 0 1rem;
  letter-spacing: 0.06em;
}
.hero p {
  max-width: 36em;
  margin: 0 auto 1.5rem;
  color: var(--ink-soft);
  font-size: 1.02rem;
}
.hero-meta {
  display: flex; justify-content: center; gap: 1.5rem; flex-wrap: wrap;
  color: var(--muted); font-size: 0.9rem;
}
.toolbar {
  display: flex; flex-direction: column; gap: 1rem;
  margin: 0 auto 1.5rem;
  max-width: 820px;
}
.search-wrap { position: relative; }
.search-wrap input {
  width: 100%;
  padding: 0.85rem 1rem 0.85rem 2.7rem;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--card);
  font-size: 1rem;
  font-family: inherit;
  color: var(--ink);
  outline: none;
  box-shadow: var(--shadow);
}
.search-wrap input:focus {
  border-color: var(--accent-soft);
  box-shadow: 0 0 0 3px rgba(196, 120, 90, 0.15);
}
.search-wrap .icon {
  position: absolute; left: 1rem; top: 50%; transform: translateY(-50%);
  color: var(--muted); pointer-events: none; font-size: 1rem;
}
.chips {
  display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center;
}
.chip {
  appearance: none; border: 1px solid var(--line);
  background: var(--card); color: var(--ink-soft);
  padding: 0.4rem 0.9rem; border-radius: 999px;
  font-size: 0.88rem; font-family: inherit; cursor: pointer;
  transition: background .15s, color .15s, border-color .15s;
}
.chip:hover { border-color: var(--accent-soft); color: var(--accent); }
.chip.active {
  background: var(--ink); color: #fff8f3; border-color: var(--ink);
}
.chip .count { opacity: 0.7; margin-left: 0.25rem; font-size: 0.8em; }
.result-meta {
  text-align: center; color: var(--muted); font-size: 0.9rem; min-height: 1.4em;
  margin-bottom: 0.8rem;
}
.section-title {
  font-family: var(--serif);
  font-size: 1.35rem;
  margin: 1.5rem 0 1rem;
  letter-spacing: 0.08em;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.1rem;
  padding-bottom: 2rem;
}
.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 1.25rem 1.3rem 1.35rem;
  box-shadow: var(--shadow);
  transition: transform .2s ease, box-shadow .2s ease;
  display: flex; flex-direction: column; gap: 0.55rem;
}
.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 16px 36px rgba(61, 50, 41, 0.09);
}
.card.is-hidden { display: none; }
.card .num {
  font-size: 0.78rem;
  color: var(--accent);
  letter-spacing: 0.12em;
  display: flex; justify-content: space-between; align-items: center; gap: 0.5rem;
}
.card .cat-tag, .cat-pill {
  display: inline-block;
  font-size: 0.75rem;
  letter-spacing: 0.04em;
  padding: 0.15rem 0.55rem;
  border-radius: 999px;
  background: #f3e0d6;
  color: #8a5a45;
  text-decoration: none;
}
.cat-pill:hover { text-decoration: none; filter: brightness(0.97); }
.card h2 {
  font-family: var(--serif);
  font-size: 1.2rem;
  margin: 0;
  font-weight: 600;
  letter-spacing: 0.04em;
}
.card h2 a { color: inherit; }
.card h2 a:hover { color: var(--accent); text-decoration: none; }
.card .teaser {
  color: var(--ink-soft);
  font-size: 0.95rem;
  margin: 0;
  flex: 1;
}
.card .more {
  font-size: 0.88rem;
  color: var(--accent);
  margin-top: 0.3rem;
}
.empty-state {
  display: none;
  text-align: center;
  padding: 3rem 1rem 4rem;
  color: var(--ink-soft);
  background: var(--card);
  border: 1px dashed var(--line);
  border-radius: var(--radius);
  margin-bottom: 2rem;
}
.empty-state.show { display: block; }
.empty-state strong { display: block; font-family: var(--serif); font-size: 1.2rem; margin-bottom: 0.5rem; color: var(--ink); }
.site-footer {
  border-top: 1px solid var(--line);
  padding: 2rem 0 3rem;
  color: var(--muted);
  font-size: 0.88rem;
  text-align: center;
}
.site-footer .brand-link {
  display: inline-flex; align-items: center; gap: 0.35rem;
  margin-top: 0.75rem;
  padding: 0.45rem 0.95rem;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: var(--card);
  color: var(--ink-soft);
  text-decoration: none;
  transition: border-color .15s, color .15s;
}
.site-footer .brand-link:hover {
  border-color: var(--accent-soft);
  color: var(--accent);
  text-decoration: none;
}
.article-shell { width: min(100% - 2rem, var(--max)); margin: 0 auto; padding: 1.5rem 0 4rem; }
.crumb { font-size: 0.88rem; color: var(--muted); margin-bottom: 1.5rem; }
.article-header { margin-bottom: 2rem; }
.article-header .num {
  color: var(--accent); letter-spacing: 0.14em; font-size: 0.85rem;
  display: flex; flex-wrap: wrap; gap: 0.6rem; align-items: center;
}
.article-header h1 {
  font-family: var(--serif);
  font-size: clamp(1.7rem, 3.5vw, 2.2rem);
  letter-spacing: 0.06em;
  margin: 0.5rem 0 0.8rem;
  line-height: 1.4;
}
.intro {
  color: var(--ink-soft);
  font-size: 1.05rem;
  border-left: 3px solid var(--accent-soft);
  padding-left: 1rem;
  margin: 1rem 0;
}
.tip {
  display: inline-flex;
  gap: 0.4rem;
  align-items: flex-start;
  background: #f6ebe3;
  color: #7a5644;
  padding: 0.7rem 1rem;
  border-radius: 12px;
  font-size: 0.9rem;
  margin: 1rem 0 0;
}
.article-body {
  font-family: var(--serif);
  font-size: 1.08rem;
  line-height: 2;
  color: #2f271f;
}
.article-body p { margin: 0 0 1.35em; text-indent: 2em; }
.article-nav {
  display: flex; justify-content: space-between; gap: 1rem;
  margin-top: 3rem; padding-top: 1.5rem;
  border-top: 1px dashed var(--line);
  font-size: 0.92rem;
}
.article-nav a { color: var(--ink-soft); }
.article-nav a:hover { color: var(--accent); }
.back-home {
  display: inline-block;
  margin-top: 2rem;
  padding: 0.65rem 1.2rem;
  border-radius: 999px;
  background: var(--ink);
  color: #fff8f3 !important;
  text-decoration: none !important;
  font-size: 0.9rem;
}
.back-home:hover { opacity: 0.9; }

/* Back to top + rocket */
.back-top {
  position: fixed;
  right: 1.15rem;
  bottom: 1.35rem;
  z-index: 40;
  width: 48px;
  height: 48px;
  border: 1px solid var(--line);
  border-radius: 50%;
  background: var(--card);
  color: var(--accent);
  box-shadow: 0 10px 24px rgba(61, 50, 41, 0.12);
  cursor: pointer;
  display: grid;
  place-items: center;
  font-size: 1.25rem;
  opacity: 0;
  visibility: hidden;
  transform: translateY(10px) scale(0.92);
  transition: opacity .25s ease, transform .25s ease, visibility .25s, background .15s, border-color .15s;
  padding: 0;
  font-family: inherit;
}
.back-top.is-visible {
  opacity: 1;
  visibility: visible;
  transform: translateY(0) scale(1);
}
.back-top:hover {
  background: #fff8f3;
  border-color: var(--accent-soft);
}
.back-top:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 3px;
}
.back-top .back-top-icon { line-height: 1; display: block; }
.rocket-fly {
  position: fixed;
  left: var(--rx, 50%);
  bottom: var(--ry, 5rem);
  z-index: 50;
  font-size: 1.8rem;
  pointer-events: none;
  opacity: 0;
  transform: translate(-50%, 0) rotate(-25deg);
  filter: drop-shadow(0 4px 8px rgba(196, 120, 90, 0.35));
}
.rocket-fly.is-launching {
  animation: rocketRise 1.05s cubic-bezier(0.22, 0.61, 0.36, 1) forwards;
}
@keyframes rocketRise {
  0% {
    opacity: 0;
    transform: translate(-50%, 20px) rotate(-20deg) scale(0.7);
  }
  12% {
    opacity: 1;
    transform: translate(-50%, 0) rotate(-25deg) scale(1);
  }
  100% {
    opacity: 0;
    transform: translate(-50%, -110vh) rotate(-10deg) scale(1.15);
  }
}
@media (max-width: 600px) {
  .back-top { right: 0.9rem; bottom: 1rem; width: 44px; height: 44px; }
}
@media (max-width: 600px) {
  body { font-size: 16px; }
  .nav-links a:not(:first-child) { display: none; }
  .hero { padding-top: 2.2rem; }
  .article-body { font-size: 1.05rem; line-height: 1.95; }
}
"""

JS = r"""
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
"""

BACK_TOP_JS = r"""
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
"""


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def nl2p(text: str) -> str:
    parts = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
    return "\n".join(f"<p>{esc(p)}</p>" for p in parts)


def search_blob(s: dict) -> str:
    return " ".join([
        s.get("title", ""),
        s.get("teaser", ""),
        s.get("intro", ""),
        s.get("body", ""),
        s.get("category_name", ""),
        s.get("tip", ""),
    ])


def header(home="index.html", css="css/style.css", asset_prefix="", subtitle="给未见面的你 · 一百篇温柔短章"):
    logo_src = f"{asset_prefix}assets/logo-header.png"
    favicon_ico = f"{asset_prefix}assets/favicon.ico"
    favicon_32 = f"{asset_prefix}assets/favicon-32.png"
    favicon_16 = f"{asset_prefix}assets/favicon-16.png"
    apple_touch = f"{asset_prefix}assets/apple-touch-icon.png"
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<meta name="description" content="一百篇原创胎教故事，按分类浏览，支持搜索，温暖文章排版，适合准爸妈轻声朗读。"/>
<title>{{title}}</title>
<link rel="stylesheet" href="{css}"/>
<link rel="icon" href="{favicon_ico}" type="image/x-icon"/>
<link rel="icon" type="image/png" sizes="32x32" href="{favicon_32}"/>
<link rel="icon" type="image/png" sizes="16x16" href="{favicon_16}"/>
<link rel="apple-touch-icon" sizes="180x180" href="{apple_touch}"/>
</head>
<body>
<header class="site-header" id="top">
  <div class="wrap nav">
    <a class="brand" href="{home}">
      <span class="logo"><img src="{logo_src}" alt="胎教故事" width="40" height="40"/></span>
      <div class="brand-text">
        <strong>胎教故事集</strong>
        <span>{esc(subtitle)}</span>
      </div>
    </a>
    <div class="nav-links">
      <a href="{home}#stories">全部故事</a>
      <a href="{home}#about">关于</a>
      <a href="https://giscafer.com" target="_blank" rel="noopener">关于我</a>
    </div>
  </div>
</header>
"""


def footer(js_path=None, asset_prefix=""):
    scripts = []
    if js_path:
        scripts.append(f'<script src="{js_path}"></script>')
    scripts.append(f'<script src="{asset_prefix}js/back-top.js"></script>')
    js = "\n".join(scripts)
    return f"""
<footer class="site-footer">
  <div class="wrap">
    <p>一百篇原创胎教短章 · 分类浏览 · 支持搜索</p>
    <p>内容为原创温暖叙事，适合朗读；非医疗建议。</p>
    <p>
      <a class="brand-link" href="https://giscafer.com" target="_blank" rel="noopener">
        ✨ 关于我 · giscafer.com
      </a>
    </p>
  </div>
</footer>
<script>
const h=document.querySelector('.site-header');
addEventListener('scroll',()=>h.classList.toggle('scrolled',scrollY>8),{{passive:true}});
</script>
{js}
</body>
</html>
"""


def build():
    STORIES_DIR.mkdir(parents=True, exist_ok=True)
    CSS_DIR.mkdir(parents=True, exist_ok=True)
    JS_DIR.mkdir(parents=True, exist_ok=True)
    (CSS_DIR / "style.css").write_text(CSS, encoding="utf-8")
    (JS_DIR / "search.js").write_text(JS, encoding="utf-8")
    (JS_DIR / "back-top.js").write_text(BACK_TOP_JS, encoding="utf-8")

    # counts per category
    counts = {k: 0 for k in CATEGORY_ORDER}
    for s in STORIES:
        counts[s["category"]] = counts.get(s["category"], 0) + 1

    chips = ['<button type="button" class="chip active" data-cat="all">全部<span class="count">' + str(len(STORIES)) + '</span></button>']
    for cid, name in CATEGORY_ORDER.items():
        chips.append(
            f'<button type="button" class="chip" data-cat="{cid}">{esc(name)}'
            f'<span class="count">{counts.get(cid, 0)}</span></button>'
        )

    cards = []
    for s in STORIES:
        blob = esc(search_blob(s).lower().replace(" ", ""))
        # keep raw for data-search without HTML entities issues - use attribute carefully
        raw_blob = search_blob(s).lower().replace(" ", "").replace('"', "")
        cards.append(f"""
<article class="card" data-cat="{esc(s['category'])}" data-search="{esc(raw_blob)}" data-id="{s['id']}">
  <div class="num"><span>第 {s['id']:02d} 篇</span><span class="cat-tag">{esc(s['category_name'])}</span></div>
  <h2><a href="stories/{s['id']:02d}.html">{esc(s['title'])}</a></h2>
  <p class="teaser">{esc(s['teaser'])}</p>
  <a class="more" href="stories/{s['id']:02d}.html">阅读全文 →</a>
</article>""")

    index = header().format(title="胎教故事集 · 一百篇温柔短章")
    index += f"""
<main>
  <section class="hero wrap">
    <div class="eyebrow">PRENATAL STORIES · 胎教朗读</div>
    <h1>在见面以前，<br/>先把温柔读给你听</h1>
    <p>一百篇原创短故事，六大分类。像一百扇小窗：月光、小溪、家人的饭香、睡前的空白磁带。支持搜索与分类筛选，方便准爸妈按心情挑选朗读。</p>
    <div class="hero-meta">
      <span>📖 {len(STORIES)} 篇原创故事</span>
      <span>🏷 六大分类</span>
      <span>🔍 即时搜索</span>
    </div>
  </section>
  <section class="wrap" id="stories">
    <h2 class="section-title">故事目录</h2>
    <div class="toolbar">
      <div class="search-wrap">
        <span class="icon">🔍</span>
        <input id="story-search" type="search" placeholder="搜索标题、正文或分类…" autocomplete="off" enterkeyhint="search"/>
      </div>
      <div class="chips" role="tablist" aria-label="故事分类">
        {''.join(chips)}
      </div>
    </div>
    <div class="result-meta" id="result-meta"></div>
    <div class="grid" id="story-grid">
      {''.join(cards)}
    </div>
    <div class="empty-state" id="empty-state">
      <strong>没有找到匹配的故事</strong>
      <span>换个关键词，或点「全部」看看其他分类吧。</span>
    </div>
  </section>
  <section class="wrap" id="about" style="padding-bottom:3rem;max-width:720px;margin:0 auto;">
    <h2 class="section-title">关于这本「故事集」</h2>
    <p style="color:var(--ink-soft)">分类包括：自然与四季、动物朋友、家人的爱、勇气与善良、中国传说改写、睡前安抚。语言短而暖，避免惊吓与沉重情节。每篇附有「适合孕期」小提示。可用顶部搜索即时过滤标题与正文。</p>
  </section>
</main>
"""
    index += footer(js_path="js/search.js")
    (ROOT / "index.html").write_text(index, encoding="utf-8")

    for i, s in enumerate(STORIES):
        prev_s = STORIES[i - 1] if i > 0 else None
        next_s = STORIES[i + 1] if i < len(STORIES) - 1 else None
        prev_link = f'<a href="{prev_s["id"]:02d}.html">← {esc(prev_s["title"])}</a>' if prev_s else "<span></span>"
        next_link = f'<a href="{next_s["id"]:02d}.html">{esc(next_s["title"])} →</a>' if next_s else "<span></span>"
        cat_link = f'<a class="cat-pill" href="../index.html?cat={esc(s["category"])}">{esc(s["category_name"])}</a>'

        page = header(home="../index.html", css="../css/style.css", asset_prefix="../").format(
            title=f"{s['title']} · 胎教故事集"
        )
        page += f"""
<main class="article-shell">
  <div class="crumb"><a href="../index.html">全部故事</a> / <a href="../index.html?cat={esc(s['category'])}">{esc(s['category_name'])}</a> / 第 {s['id']:02d} 篇</div>
  <article>
    <header class="article-header">
      <div class="num"><span>STORY {s['id']:02d}</span>{cat_link}</div>
      <h1>{esc(s['title'])}</h1>
      <p class="intro">{esc(s['intro'])}</p>
      <div class="tip">💡 {esc(s['tip'])}</div>
    </header>
    <div class="article-body">
      {nl2p(s['body'])}
    </div>
    <nav class="article-nav">
      {prev_link}
      {next_link}
    </nav>
    <a class="back-home" href="../index.html">返回目录</a>
  </article>
</main>
"""
        page += footer(asset_prefix="../")
        (STORIES_DIR / f"{s['id']:02d}.html").write_text(page, encoding="utf-8")

    (ROOT / "404.html").write_text(
        header().format(title="未找到 · 胎教故事集")
        + '<main class="article-shell"><h1>这一页还在月光后面</h1><p><a href="index.html">回到故事目录</a></p></main>'
        + footer(),
        encoding="utf-8",
    )

    lengths = [len(s["body"]) for s in STORIES]
    print(f"Built {len(STORIES)} stories")
    print(f"Body chars: min={min(lengths)} avg={sum(lengths)//len(lengths)} max={max(lengths)}")
    print("Categories:", {CATEGORY_ORDER[k]: counts[k] for k in CATEGORY_ORDER})
    print(f"Output: {ROOT}")


if __name__ == "__main__":
    build()
