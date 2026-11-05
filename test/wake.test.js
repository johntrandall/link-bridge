// Run: node --test test/
const test = require('node:test');
const assert = require('node:assert/strict');
const { parseWakeFragment } = require('../public/wake.js');

test('path form: #<system>/<seat> names the command', () => {
  const r = parseWakeFragment('#link-bridge/lead-designer');
  assert.equal(r.system, 'link-bridge');
  assert.equal(r.seat, 'lead-designer');
  assert.equal(r.command, 'watchbill resume link-bridge --seat lead-designer');
});

test('system alone defaults the seat to lead-designer; a session name is a seat too', () => {
  assert.equal(parseWakeFragment('#watchbill').command, 'watchbill resume watchbill --seat lead-designer');
  assert.equal(parseWakeFragment('#watchbill/').seat, 'lead-designer');
  assert.equal(parseWakeFragment('#outreach/outreach-steward-ho3').seat, 'outreach-steward-ho3');
});

test('key=value form, in either order, and upper case is lowered', () => {
  assert.equal(parseWakeFragment('#system=Watchbill&seat=Steward').command, 'watchbill resume watchbill --seat steward');
  assert.equal(parseWakeFragment('#seat=steward&system=watchbill').system, 'watchbill');
});

test('anything that is not two slugs is refused', () => {
  assert.match(parseWakeFragment('').error, /no system/);
  assert.match(parseWakeFragment('#a/b/c').error, /more than/);
  assert.match(parseWakeFragment('#../etc').error, /system name/);
  assert.match(parseWakeFragment('#watchbill/--help').error, /seat name/);
  assert.match(parseWakeFragment('#watchbill/a b').error, /seat name/);
  assert.match(parseWakeFragment('#watchbill/' + 'x'.repeat(65)).error, /seat name/);
  assert.match(parseWakeFragment('#system=watchbill&cmd=x').error, /refused: cmd/);
  assert.match(parseWakeFragment('#system=a&seat=b&c=d').error, /more than two/);
  assert.match(parseWakeFragment('#%E0%A4%A').error, /encoding/);
});
