// Run: node --test test/
const test = require('node:test');
const assert = require('node:assert/strict');
const { buildFolderUris } = require('../public/folder.js');

test('one fragment, two links: Finder and Obsidian, same encoded path', () => {
  const r = buildFolderUris('#dev/claude-plugin-watchbill/dev-docs/runs');
  assert.equal(r.finder, 'reveal://reveal?path=dev%2Fclaude-plugin-watchbill%2Fdev-docs%2Fruns');
  assert.equal(r.obsidian, 'reveal://obsidian?path=dev%2Fclaude-plugin-watchbill%2Fdev-docs%2Fruns');
  assert.equal(r.target, '~/dev/claude-plugin-watchbill/dev-docs/runs');
});

test('the long path= form and absolute paths work too', () => {
  assert.equal(buildFolderUris('#path=%2FVolumes%2Fx%2Fy').obsidian, 'reveal://obsidian?path=%2FVolumes%2Fx%2Fy');
  assert.equal(buildFolderUris('#/Volumes/x/y z').finder, 'reveal://reveal?path=%2FVolumes%2Fx%2Fy%20z');
});

test('what /reveal refuses, /folder refuses', () => {
  assert.ok(buildFolderUris('').error);
  assert.ok(buildFolderUris('#path=x&cmd=y').error);
  assert.ok(buildFolderUris('#%E0%A4%A').error);
});
