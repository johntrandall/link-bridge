// Link bridge, /wake: turns http://<bridge>/wake#<system>/<seat> into one confirmation button that
// asks the bridge on the Mac to run `watchbill resume <system> --seat <seat>` (POST /act/wake).
// Asked by watchbill 0.10.95 (D12 §8, intake 2026-11-05): its `_seats.md` lists every asleep seat
// with that command, which is dead text in an Obsidian note; this makes the row one click.
// Fragment forms: "#<system>/<seat>" or "#system=<system>&seat=<seat>". The seat is a watchbill
// seat kind (lead-designer, steward) or a session name (link-bridge-architect); it defaults to
// lead-designer when the fragment names only the system. Nothing here reaches the server until
// the button is pressed, and the server re-checks both names before it runs anything.

(function (root) {
  'use strict';

  // watchbill system names and seat names are slugs: letters, digits, dot, underscore, dash.
  var NAME = /^[a-z0-9][a-z0-9._-]{0,63}$/i;

  // Returns {system, seat, command} or {error}.
  function parseWakeFragment(fragment) {
    var text = String(fragment || '').replace(/^#/, '');
    if (!text) return { error: 'This link names no system to wake.' };
    var value;
    try {
      value = decodeURIComponent(text);
    } catch (e) {
      return { error: 'The link is not valid URL encoding.' };
    }
    var system = '', seat = '';
    if (value.indexOf('=') >= 0) {
      var pairs = value.split('&');
      if (pairs.length > 2) return { error: 'This link carries more than two parameters.' };
      for (var i = 0; i < pairs.length; i++) {
        var at = pairs[i].indexOf('=');
        var key = pairs[i].slice(0, at);
        var val = pairs[i].slice(at + 1);
        if (key === 'system') system = val;
        else if (key === 'seat') seat = val;
        else return { error: 'This bridge only wakes a watchbill seat. It refused: ' + key + '.' };
      }
    } else {
      var parts = value.replace(/\/+$/, '').split('/');
      if (parts.length > 2) return { error: 'The link has more than <system>/<seat>.' };
      system = parts[0];
      seat = parts[1] || '';
    }
    if (!seat) seat = 'lead-designer';
    if (!NAME.test(system)) return { error: 'The system name is not a watchbill slug.' };
    if (!NAME.test(seat)) return { error: 'The seat name is not a watchbill slug.' };
    system = system.toLowerCase();
    seat = seat.toLowerCase();
    return { system: system, seat: seat, command: 'watchbill resume ' + system + ' --seat ' + seat };
  }

  root.parseWakeFragment = parseWakeFragment;
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { parseWakeFragment: parseWakeFragment };
    return;
  }

  function render() {
    var result = parseWakeFragment(root.location.hash);
    var status = document.getElementById('status');
    var where = document.getElementById('where');
    var button = document.getElementById('onmac');
    if (result.error) {
      status.textContent = result.error;
      where.textContent = '';
      button.hidden = true;
      return;
    }
    where.textContent = result.command;
    status.textContent = 'Wake the ' + result.seat + ' of ' + result.system + '? The Mac runs:';
    var om = root.LinkBridgeOnMac;
    if (om) om.wireOnMac('wake', { system: result.system, seat: result.seat }, 'Wake it on the Mac');
  }

  document.addEventListener('DOMContentLoaded', render);
  root.addEventListener('hashchange', render);
})(typeof window !== 'undefined' ? window : globalThis);
