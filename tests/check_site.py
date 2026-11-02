"""Dependency-free checks of published HTML, references and reproducible generation."""
import importlib.util
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("story_build", ROOT / "build.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path, self.ids, self.refs, self.stack = path, set(), [], []
        self.h1, self.cards, self.toggles = 0, 0, []
        self.feed(path.read_text(encoding="utf-8"))
        assert not self.stack, (path.name, "unclosed tags", self.stack)
        assert self.h1 == 1, (path.name, "expected one h1")

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, (self.path, "duplicate ID", attrs["id"])
            self.ids.add(attrs["id"])
        for attr in ("src", "href"):
            if attrs.get(attr):
                self.refs.append(attrs[attr])
        if tag == "h1":
            self.h1 += 1
        if tag == "article" and "card" in attrs.get("class", "").split():
            self.cards += 1
        if "data-read-toggle" in attrs:
            self.toggles.append(attrs["data-read-toggle"])
            assert attrs.get("type") == "button" and "aria-pressed" in attrs
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr", "path", "circle"}:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        # SVG path/circle are self-closing; other containers must be correctly nested.
        if tag in {"path", "circle"}:
            return
        assert self.stack and self.stack[-1] == tag, (self.path, "mismatched closing tag", tag, self.stack[-3:])
        self.stack.pop()


build.validate_stories()
paths = [ROOT / "index.html", ROOT / "about.html", ROOT / "404.html", *sorted((ROOT / "stories").glob("*.html"))]
before = {p: p.read_bytes() for p in paths}
build.build()
assert all(p.read_bytes() == content for p, content in before.items()), "Run build.py and commit all generated pages"
pages = {p.resolve(): Page(p) for p in paths}
for path, page in pages.items():
    for ref in page.refs:
        url = urlsplit(ref)
        if url.scheme or url.netloc:
            continue
        target = (ROOT / unquote(url.path).lstrip("/")) if url.path.startswith("/") else path.parent / unquote(url.path)
        target = (target if url.path else path).resolve()
        assert target.exists(), (path.name, "missing resource", ref)
        if url.fragment and target in pages:
            assert unquote(url.fragment) in pages[target].ids, (path.name, "missing anchor", ref)
catalog = pages[(ROOT / "index.html").resolve()]
assert catalog.cards == len(build.STORIES)
assert len(catalog.toggles) == len(set(catalog.toggles)) == len(build.STORIES)
assert len(list((ROOT / "stories").glob("*.html"))) == len(build.STORIES)
for story in build.STORIES:
    path = ROOT / "stories" / f"{story['id']:02d}.html"
    page = pages[path.resolve()]
    assert page.toggles == [str(story["id"])] * 2, (path.name, "article needs two synced controls")
    actual = re.search(r'<div class="article-body">(.*?)</div>', path.read_text(encoding="utf-8"), re.S).group(1)
    assert actual == build.paragraphs(story["body"]), (path.name, "story body differs from data")
print(f"PASS: {len(pages)} pages; IDs, nested tags, local assets/anchors, {len(build.STORIES)} bodies, reading budgets and reproducible build")
