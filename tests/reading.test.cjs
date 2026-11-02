const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const reading = fs.readFileSync(path.join(__dirname, '../js/reading.js'), 'utf8');
const search = fs.readFileSync(path.join(__dirname, '../js/search.js'), 'utf8');
const KEY = 'prenatal-story:read:v1';

class Element {
  constructor(dataset = {}, text = '') {
    this.dataset = dataset; this.textContent = text; this.hidden = true;
    this.attrs = {}; this.listeners = {}; this.classes = new Set();
    this.classList = {
      add: c => this.classes.add(c), remove: c => this.classes.delete(c),
      contains: c => this.classes.has(c),
      toggle: (c, on) => on ? this.classes.add(c) : this.classes.delete(c),
    };
    this.firstChild = { textContent: text };
  }
  setAttribute(k, v) { this.attrs[k] = v; }
  querySelector() { return this.label; }
  closest() { return this.card || null; }
  addEventListener(name, fn) { (this.listeners[name] ||= []).push(fn); }
  emit(name) { for (const fn of this.listeners[name] || []) fn(); }
  click() { this.emit('click'); }
  focus() { this.focused = true; }
}

function fixture(options = {}) {
  const store = options.store || new Map();
  const feedback = new Element(), note = new Element();
  const filters = new Element(), summary = new Element();
  const counts = ['all', 'read', 'unread'].map(state => new Element({ stateCount: state }));
  const cards = [new Element({ id: '1', cat: 'nature', search: 'cloud自然' }), new Element({ id: '101', cat: 'classics', search: 'duck安徒生' })];
  const buttons = ['1', '101', '101'].map(id => {
    const b = new Element({ readToggle: id, storyTitle: id });
    b.label = new Element(); b.card = options.article ? null : cards.find(c => c.dataset.id === id);
    return b;
  });
  const chips = ['all', 'nature', 'classics'].map(cat => new Element({ cat }, cat));
  const states = ['all', 'read', 'unread'].map(state => new Element({ state }));
  const ids = { 'story-grid': new Element(), 'story-search': new Element(), 'result-meta': new Element(), 'empty-state': new Element(), 'reading-summary': summary, 'reset-filters': new Element(), 'empty-title': new Element(), 'empty-description': new Element(), 'read-feedback': feedback, 'storage-note': note };
  ids['story-grid'].querySelectorAll = () => cards;
  const winEvents = {}, docEvents = {};
  const document = {
    getElementById: id => ids[id] || null,
    querySelectorAll: selector => ({ '[data-read-toggle]': buttons, '.card[data-id]': cards, '[data-cat].chip': chips, '[data-state]': states, '[data-state-count]': counts }[selector] || []),
    querySelector: selector => selector === '.reading-filters' ? filters : selector === '.state-filter.active' ? states.find(s => s.classes.has('active')) : null,
    addEventListener: (name, fn) => (docEvents[name] ||= []).push(fn),
    dispatchEvent: event => (docEvents[event.type] || []).forEach(fn => fn(event)),
  };
  let context;
  const sandbox = {
    document, console, URL, URLSearchParams, CustomEvent: class { constructor(type) { this.type = type; } },
    setTimeout: fn => { sandbox.pending = fn; return 1; }, clearTimeout: () => { sandbox.pending = null; },
    localStorage: {
      getItem: key => { if (options.denyRead) throw Error('disabled'); return store.get(key) ?? null; },
      setItem: (key, value) => { if (options.denyWrite) throw Error('quota'); store.set(key, value); },
    },
    location: { href: 'https://stories.test/' + (options.query || ''), search: options.query || '' },
    history: { replaceState: (_, __, url) => { sandbox.lastUrl = url; } },
    addEventListener: (name, fn) => (winEvents[name] ||= []).push(fn),
  };
  sandbox.window = sandbox;
  context = vm.createContext(sandbox);
  vm.runInContext(reading, context);
  if (options.catalog) vm.runInContext(search, context);
  return { ...sandbox, context, buttons, cards, states, chips, ids, counts, feedback, note, store, emit: (name, event) => (winEvents[name] || []).forEach(fn => fn(event)), flush: () => sandbox.pending?.() };
}

test('mark, reload and undo keep stable IDs and update both article controls', () => {
  const a = fixture({ article: true });
  assert.equal(a.buttons[1].attrs['aria-pressed'], 'false');
  a.buttons[1].click();
  assert.equal(a.buttons[2].attrs['aria-pressed'], 'true');
  assert.deepEqual(JSON.parse(a.store.get(KEY)).readIds, ['101']);
  const b = fixture({ store: a.store, article: true });
  assert.equal(b.buttons[2].attrs['aria-pressed'], 'true');
  b.buttons[2].click();
  assert.deepEqual(JSON.parse(b.store.get(KEY)).readIds, []);
});

test('latest edits from another tab are merged before a toggle', () => {
  const f = fixture();
  f.store.set(KEY, JSON.stringify({ version: 1, readIds: ['1'] }));
  f.buttons[1].click();
  assert.deepEqual(JSON.parse(f.store.get(KEY)).readIds, ['1', '101']);
});

test('storage events and bfcache return refresh visible state, including clear', () => {
  const f = fixture();
  f.store.set(KEY, JSON.stringify({ version: 1, readIds: ['101'] }));
  f.emit('storage', { key: KEY });
  assert.equal(f.buttons[1].attrs['aria-pressed'], 'true');
  f.store.clear(); f.emit('storage', { key: null });
  assert.equal(f.buttons[1].attrs['aria-pressed'], 'false');
  f.store.set(KEY, JSON.stringify({ version: 1, readIds: ['1'] }));
  f.emit('pageshow', {});
  assert.equal(f.buttons[0].attrs['aria-pressed'], 'true');
});

test('malformed and wrong-version data recover without breaking reading', () => {
  for (const raw of ['broken', 'null', '{}', '{"version":2,"readIds":[]}', '{"version":1,"readIds":[null]}']) {
    const f = fixture({ store: new Map([[KEY, raw]]) });
    assert.match(f.note.textContent, /格式异常/);
    f.buttons[1].click();
    assert.deepEqual(JSON.parse(f.store.get(KEY)).readIds, ['101']);
  }
});

test('blocked storage and failed writes keep controls usable and show an honest warning', () => {
  for (const mode of ['denyRead', 'denyWrite']) {
    const f = fixture({ [mode]: true });
    f.buttons[1].click();
    assert.equal(f.buttons[2].attrs['aria-pressed'], 'true');
    assert.match(f.feedback.textContent, /仅本次页面有效/);
    assert.equal(f.store.has(KEY), false);
    f.buttons[1].click();
    assert.equal(f.buttons[2].attrs['aria-pressed'], 'false');
  }
});

test('category, text and read status combine; counts and reset stay consistent', () => {
  const f = fixture({ catalog: true });
  f.buttons[1].click();
  f.chips[2].click();
  f.states[2].click();
  assert.equal(f.cards.every(c => c.classes.has('is-hidden')), true);
  assert.match(f.ids['empty-title'].textContent, /都读过/);
  f.states[1].click();
  assert.equal(f.cards[1].classes.has('is-hidden'), false);
  assert.equal(f.counts.find(c => c.dataset.stateCount === 'read').textContent, 1);
  f.ids['story-search'].value = '不存在'; f.ids['story-search'].emit('input'); f.flush();
  assert.equal(f.cards.every(c => c.classes.has('is-hidden')), true);
  f.ids['reset-filters'].click();
  assert.equal(f.cards.every(c => !c.classes.has('is-hidden')), true);
  assert.equal(f.ids['story-search'].value, '');
});

test('shared URLs restore filters and invalid filter values fall back safely', () => {
  const a = fixture({ catalog: true, query: '?cat=classics&state=unread&q=DUCK' });
  assert.equal(a.cards[0].classes.has('is-hidden'), true);
  assert.equal(a.cards[1].classes.has('is-hidden'), false);
  const b = fixture({ catalog: true, query: '?cat=missing&state=bad' });
  assert.equal(b.cards.every(c => !c.classes.has('is-hidden')), true);
});

test('reading filters refresh after another tab marks a story', () => {
  const f = fixture({ catalog: true, query: '?state=read' });
  assert.match(f.ids['empty-title'].textContent, /还没有已读/);
  f.store.set(KEY, JSON.stringify({ version: 1, readIds: ['101'] }));
  f.emit('storage', { key: KEY });
  assert.equal(f.cards[1].classes.has('is-hidden'), false);
  assert.match(f.ids['reading-summary'].textContent, /已读 1/);
});
