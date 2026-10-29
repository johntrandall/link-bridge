// Run: node --test test/
const test = require('node:test');
const assert = require('node:assert/strict');
const { buildHerdrOwnerUri } = require('../public/herdr-owner.js');

const ID = '7d8bff0b-ffc2-4ad6-9033-53a3646c6740';

test('short form: a bare uuid becomes herdr-jump://owner/<uuid>', () => {
  const r = buildHerdrOwnerUri('#' + ID);
  assert.equal(r.uri, 'herdr-jump://owner/' + ID);
  assert.equal(r.target, ID);
});

test('session= form, and upper case is lowered', () => {
  assert.equal(buildHerdrOwnerUri('#session=' + ID.toUpperCase()).uri, 'herdr-jump://owner/' + ID);
});

test('anything that is not one uuid is refused', () => {
  assert.match(buildHerdrOwnerUri('').error, /no session id/);
  assert.match(buildHerdrOwnerUri('#not-a-uuid').error, /not a UUID/);
  assert.match(buildHerdrOwnerUri('#' + ID + '/../x').error, /not a UUID/);
  assert.match(buildHerdrOwnerUri('#owner=' + ID).error, /refused: owner/);
  assert.match(buildHerdrOwnerUri('#session=' + ID + '&cmd=x').error, /more than one/);
  assert.match(buildHerdrOwnerUri('#%E0%A4%A').error, /encoding/);
});
