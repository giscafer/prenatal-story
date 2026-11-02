#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate static pages. css/ and js/ are maintained source files."""
import html
import json
import math
import re
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STORIES_DIR = ROOT / "stories"
STORIES = json.loads((ROOT / "stories.json").read_text(encoding="utf-8"))
STORIES += json.loads((ROOT / "classics.json").read_text(encoding="utf-8"))
CATEGORY_ORDER = OrderedDict([
    ("classics", "世界经典童话"), ("nature", "自然与四季"),
    ("animals", "动物朋友"), ("family", "家人的爱"),
    ("virtue", "勇气与善良"), ("folklore", "中国传说改写"),
    ("lullaby", "睡前安抚"),
])


def esc(value):
    return html.escape(str(value), quote=True)


def spoken_chars(story):
    return len(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", story["body"]))


def reading_time(story):
    count = spoken_chars(story)
    low, high = max(1, math.ceil(count / 220)), max(1, math.ceil(count / 180))
    return f"约 {low} 分钟" if low == high else f"约 {low}–{high} 分钟"


def paragraphs(text):
    return "\n".join(f"<p>{esc(p.strip())}</p>" for p in text.split("\n\n") if p.strip())


def read_button(story):
    return (f'<button type="button" class="read-toggle" data-read-toggle="{story["id"]}" '
            f'data-story-title="{esc(story["title"])}" aria-pressed="false" hidden>'
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="1.7" aria-hidden="true"><path d="m5 12 4 4L19 6"/></svg>'
            '<span data-read-label>标为已读</span></button>')


def header(title, prefix=""):
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<meta name="description" content="温暖的胎教朗读故事集，原创故事与世界经典童话，留几分钟，把温柔读给你听。"/>
<title>{esc(title)}</title>
<link rel="stylesheet" href="{prefix}css/style.css"/>
<link rel="icon" href="{prefix}assets/favicon.ico" type="image/x-icon"/>
<link rel="icon" type="image/png" sizes="32x32" href="{prefix}assets/favicon-32.png"/>
<link rel="icon" type="image/png" sizes="16x16" href="{prefix}assets/favicon-16.png"/>
<link rel="apple-touch-icon" sizes="180x180" href="{prefix}assets/apple-touch-icon.png"/>
</head>
<body>
<a class="skip-link" href="#main">跳到正文</a>
<header class="site-header" id="top">
  <div class="wrap nav">
    <a class="brand" href="{prefix}index.html">
      <span class="logo"><img src="{prefix}assets/logo-header.png" alt="" width="40" height="40"/></span>
      <span class="brand-text"><strong>胎教故事集</strong><span>给未见面的你</span></span>
    </a>
    <nav class="nav-links" aria-label="主导航"><a href="{prefix}index.html#stories">全部故事</a><a href="{prefix}about.html">关于</a></nav>
  </div>
</header>
'''


def footer(prefix="", catalog=False):
    search_script = '<script src="js/search.js" defer></script>' if catalog else ""
    return f'''
<footer class="site-footer"><div class="wrap">
  <p>原创故事与经典童话精简改写 · 愿每一次朗读，都有温柔相伴。</p>
  <p><a class="brand-link" href="https://github.com/giscafer/prenatal-story" target="_blank" rel="noopener noreferrer">GitHub 源码</a>
  <a class="brand-link" href="https://giscafer.com" target="_blank" rel="noopener noreferrer">关于我 · giscafer.com</a></p>
</div></footer>
<div class="read-feedback" id="read-feedback" role="status" aria-live="polite"></div>
<script src="{prefix}js/reading.js" defer></script>
{search_script}
<script src="{prefix}js/back-top.js" defer></script>
</body>
</html>
'''


def validate_stories():
    ids = set()
    for s in STORIES:
        assert isinstance(s["id"], int) and s["id"] > 0 and s["id"] not in ids, "Story IDs must be unique positive integers"
        ids.add(s["id"])
        assert s["category"] in CATEGORY_ORDER, f"Unknown category: {s['category']}"
        assert s["category_name"] == CATEGORY_ORDER[s["category"]]
        for key in ("title", "teaser", "intro", "body", "tip"):
            assert isinstance(s[key], str) and s[key].strip(), f"Missing {key} in story {s['id']}"
        assert spoken_chars(s) <= 900, f"Story {s['id']} exceeds the five-minute editorial budget"
        if s["category"] == "classics":
            assert all(s.get(key) for key in ("author", "source_title", "source_url", "adaptation"))
            assert s["source_url"].startswith("https://www.gutenberg.org/")


def build():
    validate_stories()
    STORIES_DIR.mkdir(parents=True, exist_ok=True)
    counts = {key: sum(s["category"] == key for s in STORIES) for key in CATEGORY_ORDER}
    chips = [f'<button type="button" class="chip active" data-cat="all" aria-pressed="true">全部<span class="count">{len(STORIES)}</span></button>']
    chips += [f'<button type="button" class="chip" data-cat="{key}" aria-pressed="false">{esc(name)}<span class="count">{counts[key]}</span></button>' for key, name in CATEGORY_ORDER.items()]
    cards = []
    for s in STORIES:
        blob = re.sub(r"\s+", "", " ".join(s.get(key, "") for key in ("title", "teaser", "intro", "body", "category_name", "author", "tip")).lower())
        cards.append(f'''
<article class="card" data-cat="{s['category']}" data-search="{esc(blob)}" data-id="{s['id']}">
  <div class="num"><span>第 {s['id']:02d} 篇</span><span class="cat-tag">{esc(s['category_name'])}</span></div>
  <h2><a href="stories/{s['id']:02d}.html">{esc(s['title'])}</a></h2>
  <p class="teaser">{esc(s['teaser'])}</p>
  <div class="card-meta"><span>{reading_time(s)}朗读</span><span>{esc(s.get('author', '原创故事'))}</span></div>
  <div class="card-actions"><a class="more" href="stories/{s['id']:02d}.html">开始阅读 <span aria-hidden="true">→</span></a>{read_button(s)}</div>
</article>''')
    index = header("胎教故事集") + f'''
<main id="main">
  <section class="hero wrap">
    <h1>在见面以前，<br/>先把温柔读给你听</h1>
    <p class="hero-subtitle">从一朵小云的晚安，到一段熟悉的童话。<br class="mobile-break"/>留几分钟，一起走进故事里。</p>
    <div class="hero-meta"><span>{len(STORIES)} 篇故事</span><a href="?cat=classics#stories">{counts['classics']} 篇世界经典童话 →</a><span>每篇约 1–5 分钟</span></div>
  </section>
  <section class="wrap" id="stories" aria-labelledby="catalog-title">
    <div class="catalog-heading"><h2 class="section-title" id="catalog-title">故事目录</h2><p id="reading-summary" hidden></p></div>
    <div class="toolbar">
      <div class="search-wrap">
        <svg class="icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4.5 4.5"/></svg>
        <label class="sr-only" for="story-search">搜索标题、正文、作者或分类</label>
        <input id="story-search" type="search" placeholder="找一个故事，或一个熟悉的名字…" autocomplete="off" enterkeyhint="search"/>
      </div>
      <div class="chips" role="group" aria-label="故事分类">{''.join(chips)}</div>
      <div class="reading-filters" role="group" aria-label="阅读状态" hidden>
        <button type="button" class="state-filter active" data-state="all" aria-pressed="true">全部故事 <span data-state-count="all">{len(STORIES)}</span></button>
        <button type="button" class="state-filter" data-state="unread" aria-pressed="false">未读 <span data-state-count="unread">{len(STORIES)}</span></button>
        <button type="button" class="state-filter" data-state="read" aria-pressed="false">已读 <span data-state-count="read">0</span></button>
      </div>
      <p class="storage-note" id="storage-note">已读标记仅保存在当前浏览器，不跨设备同步；清除网站数据后会重置。</p>
      <noscript><p>启用 JavaScript 后可使用搜索和已读标记；所有故事仍可直接阅读。</p></noscript>
    </div>
    <div class="result-meta" id="result-meta" role="status" aria-live="polite">共 {len(STORIES)} 篇故事</div>
    <div class="grid" id="story-grid">{''.join(cards)}</div>
    <div class="empty-state" id="empty-state"><strong id="empty-title">没有找到匹配的故事</strong><p id="empty-description">试试其他关键词，或重置筛选重新挑选。</p><button class="reset-filters" id="reset-filters" type="button">重置所有筛选</button></div>
  </section>
</main>
''' + footer(catalog=True)
    (ROOT / "index.html").write_text(index, encoding="utf-8")

    for i, s in enumerate(STORIES):
        prev_s, next_s = STORIES[i - 1] if i > 0 else None, STORIES[i + 1] if i < len(STORIES) - 1 else None
        prev_link = f'<a rel="prev" href="{prev_s["id"]:02d}.html">← {esc(prev_s["title"])}</a>' if prev_s else "<span></span>"
        next_link = f'<a rel="next" href="{next_s["id"]:02d}.html">{esc(next_s["title"])} →</a>' if next_s else "<span></span>"
        source = ""
        if s.get("source_url"):
            source = f'''<aside class="story-source" aria-label="故事出处与改写说明"><h2>关于这个版本</h2><p>{esc(s['author'])} · <a href="{esc(s['source_url'])}" target="_blank" rel="noopener noreferrer">{esc(s['source_title'])}（原作参考）</a></p><p>本站中文精简改写，并非原文全译。{esc(s['adaptation'])}</p></aside>'''
        page = header(f"{s['title']} · 胎教故事集", "../") + f'''
<main class="article-shell" id="main">
  <nav class="crumb" aria-label="面包屑"><a href="../index.html">全部故事</a> / <a href="../index.html?cat={s['category']}">{esc(s['category_name'])}</a> / 第 {s['id']:02d} 篇</nav>
  <article data-story-id="{s['id']}">
    <header class="article-header">
      <div class="num"><span>第 {s['id']:02d} 篇</span><a class="cat-pill" href="../index.html?cat={s['category']}">{esc(s['category_name'])}</a></div>
      <h1>{esc(s['title'])}</h1>
      <div class="article-meta"><span>{reading_time(s)}朗读 · 正文 {spoken_chars(s)} 字</span><span>{esc(s.get('author', '原创故事'))}</span></div>
      <p class="intro">{esc(s['intro'])}</p>
      <p class="tip">朗读小提示：{esc(s['tip'])}</p>
      <div class="article-tools">{read_button(s)}<span class="reading-estimate">按每分钟 180–220 字估算，实际随语速和停顿变化。</span></div>
      <noscript><p>启用 JavaScript 后可标记已读。</p></noscript>
    </header>
    <div class="article-body">{paragraphs(s['body'])}</div>
    <div class="reading-finish"><p>这一篇，读给你听了。</p>{read_button(s)}<span>标记后，回到目录就能找到你的阅读记录。</span></div>
{source}
    <nav class="article-nav" aria-label="相邻故事">{prev_link}{next_link}</nav>
    <a class="back-home" href="../index.html#stories">返回故事目录</a>
  </article>
</main>
''' + footer("../")
        (STORIES_DIR / f"{s['id']:02d}.html").write_text(page, encoding="utf-8")

    about = header("关于 · 胎教故事集") + '''
<main id="main"><section class="wrap about-block">
  <img class="about-logo" src="assets/logo.png" alt="胎教故事 Logo" width="176" height="176"/>
  <h1 class="section-title">关于这本「故事集」</h1>
  <p>这里收录原创温暖故事与世界经典童话的中文精简改写，按自然与四季、动物朋友、家人的爱、勇气与善良、中国传说改写、睡前安抚、世界经典童话分类。挑一篇喜欢的，慢慢读给你爱的人听。</p>
  <p>每篇正文按 180–220 字／分钟估算朗读时间，尽量控制在五分钟内。估算不含导读与出处，实际时长会随语速、对话和停顿变化；不必赶时间。</p>
  <p>经典童话保留标志性人物与主要情节，对部分惊吓、暴力及结局作温和调整。每篇文末列出作者或整理者、原作参考链接与改写说明，不作为原作的完整译本。</p>
  <p>目录支持按标题、正文、作者和分类搜索。点击「标为已读」即可留下记录，也可再次点击撤销。记录仅存于当前浏览器的网站本地存储，无需登录，不跨设备同步；清除网站数据会重置记录。浏览器禁止存储时，会提示标记仅本次有效。</p>
  <p><a class="about-link" href="https://giscafer.com" target="_blank" rel="noopener noreferrer">关于作者 · giscafer.com</a></p>
  <p><a class="about-link" href="index.html#stories">← 返回故事目录</a></p>
</section></main>
''' + footer()
    (ROOT / "about.html").write_text(about, encoding="utf-8")
    (ROOT / "404.html").write_text(header("未找到 · 胎教故事集", "/") + '<main class="article-shell" id="main"><h1>这一页还在月光后面</h1><p><a href="/index.html">回到故事目录</a></p></main>' + footer("/"), encoding="utf-8")
    print(f"Built {len(STORIES)} stories; maximum spoken characters: {max(map(spoken_chars, STORIES))}")
    print("Categories:", {CATEGORY_ORDER[k]: counts[k] for k in CATEGORY_ORDER})


if __name__ == "__main__":
    build()
