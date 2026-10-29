// Link bridge, /herdr-owner: turns https://<your host>/herdr-owner#<claude session uuid> into a
// herdr-jump://owner/<uuid> link. The handler on the Mac asks `herdr-lifecycle owner <uuid>` who
// holds that session's SEAT now (the session itself while live, else its relief or handoff
// successor, else the highest live -hoN of its name, else its system's doorbell seat) and focuses
// that session's herdr tab. /herdr-jump#<uuid> goes to the session itself when it is live, even if
// it has handed off and is now a historian; this route goes to whoever owns the work today
// (watchbill decision cards: "talk to the seat that holds it now", John 2026-10-29).
// Fragment forms: "#<uuid>" or "#session=<uuid>". The id never reaches the server.

(function (root) {
  'use strict';

  var SCHEME = 'herdr-jump';
  var UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

  // Returns {uri, target} or {error}.
  function buildHerdrOwnerUri(fragment) {
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
      if (key !== 'session') return { error: 'This bridge only resolves a session to its seat owner. It refused: ' + key + '.' };
      value = pairs[0].slice(at + 1);
    }
    if (!UUID.test(value)) return { error: 'The session id is not a UUID.' };
    var id = value.toLowerCase();
    return { uri: SCHEME + '://owner/' + id, target: id };
  }

  root.buildHerdrOwnerUri = buildHerdrOwnerUri;
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { buildHerdrOwnerUri: buildHerdrOwnerUri };
    return;
  }

  function render() {
    var result = buildHerdrOwnerUri(root.location.hash);
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
    if (om) om.wireOnMac('herdr-owner', { session: result.target }, 'Find the owner on the Mac');
    if (remote) {
      status.textContent = 'This browser is not on the Mac; ask the Mac to focus the seat owner:';
      return;
    }
    status.textContent = 'Finding who holds this seat now…';
    root.location.href = result.uri;
  }

  document.addEventListener('DOMContentLoaded', render);
  root.addEventListener('hashchange', render);
})(typeof window !== 'undefined' ? window : globalThis);
