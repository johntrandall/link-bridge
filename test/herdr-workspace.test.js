// Run: node --test test/
const test = require('node:test');
const assert = require('node:assert/strict');
const { buildHerdrWorkspaceUri } = require('../public/herdr-workspace.js');

test('short form: a bare id becomes herdr-jump://workspace/<id>', () => {
  const r = buildHerdrWorkspaceUri('#wBK');
  assert.equal(r.uri, 'herdr-jump://workspace/wBK');
  assert.equal(r.kind, 'id');
  assert.equal(r.target, 'wBK');
});

test('id= form is the same link', () => {
  assert.equal(buildHerdrWorkspaceUri('#id=w7P').uri, 'herdr-jump://workspace/w7P');
});

test('label= form carries the label, encoded, under /label/', () => {
  const r = buildHerdrWorkspaceUri('#label=' + encodeURIComponent('s-svc link-bridge'));
  assert.equal(r.uri, 'herdr-jump://workspace/label/s-svc%20link-bridge');
  assert.equal(r.kind, 'label');
  assert.equal(r.value, 's-svc link-bridge');
});

test('anything that is not one id or one label is refused', () => {
  assert.match(buildHerdrWorkspaceUri('').error, /names no workspace/);
  assert.match(buildHerdrWorkspaceUri('#').error, /names no workspace/);
  assert.match(buildHerdrWorkspaceUri('#BK').error, /not a herdr id/);
  assert.match(buildHerdrWorkspaceUri('#w').error, /not a herdr id/);
  assert.match(buildHerdrWorkspaceUri('#wBK/../x').error, /not a herdr id/);
  assert.match(buildHerdrWorkspaceUri('#w123456789').error, /not a herdr id/);
  assert.match(buildHerdrWorkspaceUri('#session=wBK').error, /refused: session/);
  assert.match(buildHerdrWorkspaceUri('#id=wBK&cmd=x').error, /more than one/);
  assert.match(buildHerdrWorkspaceUri('#label=').error, /empty, too long/);
  assert.match(buildHerdrWorkspaceUri('#label=' + 'x'.repeat(81)).error, /empty, too long/);
  assert.match(buildHerdrWorkspaceUri('#label=a%0Ab').error, /control/);
  assert.match(buildHerdrWorkspaceUri('#%E0%A4%A').error, /encoding/);
});

test('result is always the fixed scheme and host', () => {
  assert.ok(buildHerdrWorkspaceUri('#wBK').uri.startsWith('herdr-jump://workspace/'));
  assert.ok(buildHerdrWorkspaceUri('#label=x').uri.startsWith('herdr-jump://workspace/label/'));
});
