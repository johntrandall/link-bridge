// "On the Mac": when the browser is not on the Mac that runs this bridge (an iPad reading a
// status line through Moshi), a custom scheme like reveal:// or herdr-jump:// has no handler
// here. The page then asks the bridge itself to perform the action on the Mac: a same-origin
// POST to /act/<action> with a custom header (which makes any cross-origin attempt a CORS
// preflight the server never answers). The bridge re-checks the request with the same gates as
// the handler apps. Only reachable where the bridge is: loopback, or the tailnet via Tailscale
// Serve. Pages call wireOnMac(action, payload, isRemote) after they have built their URI.
(function (root) {
  'use strict';

  // iPhone, iPad (which reports itself as a Mac with touch points), and anything else that is
  // not a desktop Mac. Chrome/Safari on the Mac itself keep the scheme navigation.
  function isRemoteBrowser() {
    var ua = navigator.userAgent || '';
    if (/iPhone|iPad|iPod|Android/.test(ua)) return true;
    if (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1) return true;
    return !/Macintosh/.test(ua);
  }

  function wireOnMac(action, payload, label) {
    var button = document.getElementById('onmac');
    var status = document.getElementById('status');
    if (!button) return;
    button.hidden = false;
    button.textContent = label;
    button.onclick = function (ev) {
      ev.preventDefault();
      status.textContent = 'Asking the Mac…';
      fetch('/act/' + action, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Link-Bridge': '1' },
        body: JSON.stringify(payload)
      }).then(function (r) { return r.json().then(function (j) { return [r.status, j]; }); })
        .then(function (res) {
          status.textContent = res[1].ok ? 'Done on the Mac.' : ('The Mac said no: ' + (res[1].error || res[0]));
        })
        .catch(function () { status.textContent = 'Could not reach the Mac (is the bridge served on this network?).'; });
    };
  }

  root.LinkBridgeOnMac = { isRemoteBrowser: isRemoteBrowser, wireOnMac: wireOnMac };
})(typeof window !== 'undefined' ? window : globalThis);
