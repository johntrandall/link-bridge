// Run: node --test test/
const test = require('node:test');
const assert = require('node:assert/strict');
const { buildVaultSetupUri } = require('../public/vault-setup.js');

test('short form becomes an obsidian-vault-setup://open?path= link', () => {
  const r = buildVaultSetupUri('#dev/claude-statusline');
  assert.equal(r.uri, 'obsidian-vault-setup://open?path=' + encodeURIComponent('dev/claude-statusline'));
  assert.equal(r.target, '~/dev/claude-statusline');
});

test('path= form and absolute paths', () => {
  const p = '/Users/me/a+b/Café — x';
  const r = buildVaultSetupUri('#path=' + encodeURIComponent(p));
  assert.equal(r.target, p);
  assert.equal(r.uri, 'obsidian-vault-setup://open?path=' + encodeURIComponent(p));
});

test('other parameters, empty and control characters are refused', () => {
  assert.match(buildVaultSetupUri('#path=%2Ftmp&profile=x').error, /refused: profile/);
  assert.match(buildVaultSetupUri('#path=').error, /empty/);
  assert.match(buildVaultSetupUri('#dev/a%0Ab').error, /control/);
  assert.ok(buildVaultSetupUri('').error);
  assert.ok(buildVaultSetupUri('#path=%E0%A4%A').error);
});

test('result is always the fixed scheme and host', () => {
  const r = buildVaultSetupUri('#' + encodeURIComponent('/javascript:alert(1)'));
  assert.ok(r.uri.startsWith('obsidian-vault-setup://open?path='));
});
