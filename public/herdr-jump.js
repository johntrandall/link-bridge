// Link bridge, /herdr-jump: turns https://<your host>/herdr-jump#<session uuid> into a
// herdr-jump://session/<uuid> link. A handler on the Mac (the herdr open-links plugin) resolves the
// Claude session id to its herdr pane and focuses that tab. Nothing else happens: no command, no
// file. The page checks only that the fragment is a UUID, so a crafted link can at most focus a
// pane that exists. Fragment forms: "#<uuid>" (short) or "#session=<uuid>". The id travels in the
// fragment and never reaches the server.

(function (root) {
  'use strict';

  var SCHEME = 'herdr-jump';
  var UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

  // Returns {uri, target} or {error}.
  function buildHerdrJumpUri(fragment) {
    var text = String(fragment || '').replace(/^#/, '');
    if (!text) return { error: 'This link carries no session id.' };
    var value;
    try {
      value = decodeURIComponent(text);
    } catch (e) {
      return { error: 'The link is not valid URL encoding.' };
    }
    if (value.indexOf('=') >= 0) {
      var pairs = value.split('&');
      if (pairs.length !== 1) return { error: 'This link carries more than one parameter.' };
      var at = pairs[0].indexOf('=');
      var key = pairs[0].slice(0, at);
      if (key !== 'session') return { error: 'This bridge only jumps to a session. It refused: ' + key + '.' };
      value = pairs[0].slice(at + 1);
    }
    if (!UUID.test(value)) return { error: 'The session id is not a UUID.' };
    var id = value.toLowerCase();
    return { uri: SCHEME + '://session/' + id, target: id };
  }

  root.buildHerdrJumpUri = buildHerdrJumpUri;
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { buildHerdrJumpUri: buildHerdrJumpUri };
    return;
  }

  function render() {
    var result = buildHerdrJumpUri(root.location.hash);
    var status = document.getElementById('status');
    var where = document.getElementById('where');
    var button = document.getElementById('open');
    if (result.error) {
      status.textContent = result.error;
      where.textContent = '';
      button.hidden = true;
      return;
    }
    status.textContent = 'Jumping to the session in herdr…';
    where.textContent = result.target;
    button.href = result.uri;
    button.hidden = false;
    root.location.href = result.uri;
  }

  document.addEventListener('DOMContentLoaded', render);
  root.addEventListener('hashchange', render);
})(typeof window !== 'undefined' ? window : globalThis);
