// Link bridge, /reveal: turns https://<your host>/reveal#path=<encoded absolute path> into a
// reveal://reveal?path=<encoded absolute path> link, which the "Reveal in Finder" handler app on
// the user's Mac turns into `open -R <path>`: the item is selected in a Finder window. Nothing is
// opened, launched or executed, which is why this page forwards paths with so few questions.
//
// The path lives in the URL fragment (after #). Browsers never send the fragment to the server,
// so the host sees only "GET /reveal" and no file name ever reaches a log.
//
// Why not file://: browsers refuse to navigate from an https page to a file: URL, with no
// "always allow". A custom scheme is the only way through, and the handler is the real gate:
// the page checks shape, the handler checks the file system.

(function (root) {
  'use strict';

  var SCHEME = 'reveal';
  var ALLOWED_KEYS = ['path'];

  // Parse "a=1&b=x%2Fy" without URLSearchParams' "+ means space" rule: a literal + in a
  // file name must stay a +.
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

  // Two fragment forms. The short one is what a terminal status line shows, where every column
  // counts: "#dev/claude-statusline" (relative to the user's home folder, / kept readable) or
  // "#/Volumes/x/y" (absolute). The long one, "#path=<percent-encoded path>", is the original.
  // A relative path means "under the home folder"; the handler, which knows the home folder,
  // joins it. The page only checks shape.
  //
  // Returns {uri, target} or {error}.
  function buildRevealUri(fragment) {
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
      if (params.length === 0) return { error: 'This link carries no path to reveal.' };

      var seen = Object.create(null);
      var rejected = [];
      for (var i = 0; i < params.length; i++) {
        var k = params[i][0];
        if (ALLOWED_KEYS.indexOf(k) < 0) rejected.push(k);
        if (k in seen) return { error: 'The link repeats the parameter "' + k + '".' };
        seen[k] = params[i][1];
      }
      if (rejected.length) {
        return { error: 'This bridge only reveals files. It refused: ' + rejected.join(', ') + '.' };
      }
      target = seen.path;
    }
    if (!target) return { error: 'The link names no path (path= is empty).' };
    // Control characters and NUL have no place in a path and are a sign of tampering.
    if (/[\u0000-\u001f\u007f]/.test(target)) return { error: 'The path contains control characters.' };
    return {
      uri: SCHEME + '://reveal?path=' + encodeURIComponent(target),
      target: target.charAt(0) === '/' ? target : '~/' + target
    };
  }

  root.buildRevealUri = buildRevealUri;
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { buildRevealUri: buildRevealUri };
    return;
  }

  function render() {
    var result = buildRevealUri(root.location.hash);
    var status = document.getElementById('status');
    var where = document.getElementById('where');
    var button = document.getElementById('open');
    if (result.error) {
      status.textContent = result.error;
      where.textContent = '';
      button.hidden = true;
      return;
    }
    where.textContent = result.target;
    button.href = result.uri;
    button.hidden = false;
    var om = root.LinkBridgeOnMac;
    var remote = om && om.isRemoteBrowser();
    if (om) om.wireOnMac('reveal', { path: result.target }, 'Reveal on the Mac');
    if (remote) {
      status.textContent = 'This browser is not on the Mac; ask the Mac to reveal it:';
      return;
    }
    status.textContent = 'Revealing in Finder…';
    root.location.href = result.uri;
  }

  document.addEventListener('DOMContentLoaded', render);
  root.addEventListener('hashchange', render);
})(typeof window !== 'undefined' ? window : globalThis);
