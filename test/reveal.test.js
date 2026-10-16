// Run: node --test test/
const test = require('node:test');
const assert = require('node:assert/strict');
const { buildRevealUri } = require('../public/reveal.js');

test('absolute path becomes a reveal://reveal?path= link', () => {
  const r = buildRevealUri('#path=' + encodeURIComponent('/Users/me/admin-technical/README.md'));
  assert.equal(r.uri, 'reveal://reveal?path=' + encodeURIComponent('/Users/me/admin-technical/README.md'));
  assert.equal(r.target, '/Users/me/admin-technical/README.md');
});

test('directories are fine, spaces, plus signs and unicode survive', () => {
  const p = '/Users/me/a+b/Café — x';
  const r = buildRevealUri('#path=' + encodeURIComponent(p));
  assert.equal(r.target, p);
  assert.equal(r.uri, 'reveal://reveal?path=' + encodeURIComponent(p));
});

test('short form: a bare fragment is a path, relative to the home folder unless absolute', () => {
  const r = buildRevealUri('#dev/claude-statusline');
  assert.equal(r.uri, 'reveal://reveal?path=' + encodeURIComponent('dev/claude-statusline'));
  assert.equal(r.target, '~/dev/claude-statusline');
  const a = buildRevealUri('#/Volumes/x/y%20z');
  assert.equal(a.uri, 'reveal://reveal?path=' + encodeURIComponent('/Volumes/x/y z'));
  assert.equal(a.target, '/Volumes/x/y z');
  assert.match(buildRevealUri('#dev/a%0Ab').error, /control/);
});

test('path= form: a relative path is home-relative too; empty paths and control characters are refused', () => {
  assert.equal(buildRevealUri('#path=README.md').target, '~/README.md');
  assert.match(buildRevealUri('#path=').error, /empty/);
  assert.match(buildRevealUri('#path=' + encodeURIComponent('/tmp/a\nb')).error, /control/);
  assert.match(buildRevealUri('#path=' + encodeURIComponent('/tmp/a\u0000b')).error, /control/);
});

test('any other parameter is refused', () => {
  assert.match(buildRevealUri('#path=%2Ftmp&open=1').error, /refused: open/);
  assert.match(buildRevealUri('#path=%2Ftmp&__proto__=1').error, /refused: __proto__/);
  assert.match(buildRevealUri('#path=%2Fa&path=%2Fb').error, /repeats/);
});

test('empty or broken input is refused', () => {
  assert.ok(buildRevealUri('').error);
  assert.ok(buildRevealUri('#').error);
  assert.ok(buildRevealUri('#path=%E0%A4%A').error);
});

test('result is always a reveal:// URI with the fixed host', () => {
  const r = buildRevealUri('#path=' + encodeURIComponent('/javascript:alert(1)'));
  assert.ok(r.uri.startsWith('reveal://reveal?path='));
});
