// Link bridge, /herdr-workspace: turns https://<your host>/herdr-workspace#<workspace id> into a
// herdr-jump://workspace/<id> link, the workspace twin of /herdr-jump (which focuses one session's
// tab). The handler on the Mac (Jump to Session.app, or the herdr open-links plugin inside a pane)
// runs `herdr workspace focus <id>`. Nothing else happens: no command, no file.
//
// Fragment forms: "#<id>" or "#id=<id>" (a herdr workspace id such as wBK), or "#label=<text>"
// (the workspace's tab-bar label; the handler ignores the lifecycle glyphs in front of it and
// matches case-insensitively, so a label survives a herdr restart that renumbers ids). The page
// checks shape only; the handler decides what exists. The fragment never reaches the server.

(function (root) {
  'use strict';

  var SCHEME = 'herdr-jump';
  var WORKSPACE_ID = /^w[A-Za-z0-9]{1,8}$/;
  var LABEL_MAX = 80;

  function badLabel(text) {
    if (!text || text.length > LABEL_MAX) return true;
    for (var i = 0; i < text.length; i++) {
      var c = text.charCodeAt(i);
      if (c < 0x20 || c === 0x7f) return true;
    }
    return false;
  }

  // Returns {uri, target, kind, value} or {error}.
  function buildHerdrWorkspaceUri(fragment) {
    var text = String(fragment || '').replace(/^#/, '');
    if (!text) return { error: 'This link names no workspace.' };
    var value;
    try {
      value = decodeURIComponent(text);
    } catch (e) {
      return { error: 'The link is not valid URL encoding.' };
    }
    var key = 'id';
    var at = value.indexOf('=');
    if (at >= 0) {
      if (value.indexOf('&') >= 0) return { error: 'This link carries more than one parameter.' };
      key = value.slice(0, at);
      value = value.slice(at + 1);
      if (key !== 'id' && key !== 'label') return { error: 'This bridge only focuses a workspace by id or label. It refused: ' + key + '.' };
    }
    if (key === 'id') {
      if (!WORKSPACE_ID.test(value)) return { error: 'The workspace id is not a herdr id (like wBK).' };
      return { uri: SCHEME + '://workspace/' + value, target: value, kind: 'id', value: value };
    }
    if (badLabel(value)) return { error: 'The workspace label is empty, too long, or holds control characters.' };
    return { uri: SCHEME + '://workspace/label/' + encodeURIComponent(value), target: value, kind: 'label', value: value };
  }

  root.buildHerdrWorkspaceUri = buildHerdrWorkspaceUri;
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { buildHerdrWorkspaceUri: buildHerdrWorkspaceUri };
    return;
  }

  function render() {
    var result = buildHerdrWorkspaceUri(root.location.hash);
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
    if (om) {
      var payload = result.kind === 'id' ? { workspace: result.value } : { label: result.value };
      om.wireOnMac('herdr-workspace', payload, 'Focus on the Mac');
    }
    if (remote) {
      status.textContent = 'This browser is not on the Mac; ask the Mac to focus the workspace:';
      return;
    }
    status.textContent = 'Focusing the workspace in herdr…';
    root.location.href = result.uri;
  }

  document.addEventListener('DOMContentLoaded', render);
  root.addEventListener('hashchange', render);
})(typeof window !== 'undefined' ? window : globalThis);
