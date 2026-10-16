// Link bridge, /vault-setup: turns https://<your host>/vault-setup#<path> into an
// obsidian-vault-setup://open?path=<encoded path> link. The "Open in Obsidian" handler app
// (github.com/johntrandall/obsidian-vault-setup) opens the Obsidian vault at that folder's git
// repository root, or creates one first. This is the open-OR-create companion to /obsidian,
// which Obsidian itself answers with "Vault not found" for any folder that is not a vault yet.
//
// Fragment forms, as for /reveal: "#dev/project" (relative to the home folder), "#/abs/path",
// or "#path=<percent-encoded path>". The handler accepts only an existing directory under the
// home folder, so this page checks shape only. The path lives in the fragment and never reaches
// the server.

(function (root) {
  'use strict';

  var SCHEME = 'obsidian-vault-setup';
  var ALLOWED_KEYS = ['path'];

  function parseFragment(fragment) {
    var text = String(fragment || '').replace(/^#/, '');
    var params = [];
    if (!text) return params;
    text.split('&').forEach(function (pair) {
      if (!pair) return;
      var at = pair.indexOf('=');
      var key = at < 0 ? pair : pair.slice(0, at);
      var value = at < 0 ? '' : pair.slice(at + 1);
      params.push([decodeURIComponent(key), decodeURIComponent(value)]);
    });
    return params;
  }

  // Returns {uri, target} or {error}.
  function buildVaultSetupUri(fragment) {
    var text = String(fragment || '').replace(/^#/, '');
    var target;
    if (text && text.indexOf('=') < 0) {
      try {
        target = decodeURIComponent(text);
      } catch (e) {
        return { error: 'The link is not valid URL encoding.' };
      }
    } else {
      var params;
      try {
        params = parseFragment(fragment);
      } catch (e) {
        return { error: 'The link is not valid URL encoding.' };
      }
      if (params.length === 0) return { error: 'This link carries no folder.' };
      var seen = Object.create(null);
      var rejected = [];
      for (var i = 0; i < params.length; i++) {
        var k = params[i][0];
        if (ALLOWED_KEYS.indexOf(k) < 0) rejected.push(k);
        if (k in seen) return { error: 'The link repeats the parameter "' + k + '".' };
        seen[k] = params[i][1];
      }
      if (rejected.length) {
        return { error: 'This bridge only opens vault folders. It refused: ' + rejected.join(', ') + '.' };
      }
      target = seen.path;
    }
    if (!target) return { error: 'The link names no folder (path= is empty).' };
    if (/[\u0000-\u001f\u007f]/.test(target)) return { error: 'The path contains control characters.' };
    return {
      uri: SCHEME + '://open?path=' + encodeURIComponent(target),
      target: target.charAt(0) === '/' ? target : '~/' + target
    };
  }

  root.buildVaultSetupUri = buildVaultSetupUri;
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { buildVaultSetupUri: buildVaultSetupUri };
    return;
  }

  function render() {
    var result = buildVaultSetupUri(root.location.hash);
    var status = document.getElementById('status');
    var where = document.getElementById('where');
    var button = document.getElementById('open');
    if (result.error) {
      status.textContent = result.error;
      where.textContent = '';
      button.hidden = true;
      return;
    }
    status.textContent = 'Opening in Obsidian (creating the vault if needed)…';
    where.textContent = result.target;
    button.href = result.uri;
    button.hidden = false;
    root.location.href = result.uri;
  }

  document.addEventListener('DOMContentLoaded', render);
  root.addEventListener('hashchange', render);
})(typeof window !== 'undefined' ? window : globalThis);
