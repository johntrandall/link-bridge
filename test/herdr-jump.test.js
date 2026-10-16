// Run: node --test test/
const test = require('node:test');
const assert = require('node:assert/strict');
const { buildHerdrJumpUri } = require('../public/herdr-jump.js');

const ID = '7d8bff0b-ffc2-4ad6-9033-53a3646c6740';

test('short form: a bare uuid becomes herdr-jump://session/<uuid>', () => {
  const r = buildHerdrJumpUri('#' + ID);
  assert.equal(r.uri, 'herdr-jump://session/' + ID);
  assert.equal(r.target, ID);
});

test('session= form, and upper case is lowered', () => {
  const r = buildHerdrJumpUri('#session=' + ID.toUpperCase());
  assert.equal(r.uri, 'herdr-jump://session/' + ID);
});

test('anything that is not one uuid is refused', () => {
  assert.match(buildHerdrJumpUri('').error, /no session id/);
  assert.match(buildHerdrJumpUri('#').error, /no session id/);
  assert.match(buildHerdrJumpUri('#not-a-uuid').error, /not a UUID/);
  assert.match(buildHerdrJumpUri('#' + ID + '/../x').error, /not a UUID/);
  assert.match(buildHerdrJumpUri('#pane=w1:p2').error, /refused: pane/);
  assert.match(buildHerdrJumpUri('#session=' + ID + '&cmd=x').error, /more than one/);
  assert.match(buildHerdrJumpUri('#%E0%A4%A').error, /encoding/);
});

test('result is always the fixed scheme and host', () => {
  assert.ok(buildHerdrJumpUri('#' + ID).uri.startsWith('herdr-jump://session/'));
});
