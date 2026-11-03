// Link bridge, /folder: a folder link that lets the reader choose where it opens (John,
// 2026-11-03: "reveal the folder in Finder or in its obsidian vault"). The page builds two links
// from one fragment, the same forms /reveal accepts ("#dev/project" home-relative, "#/abs/path",
// or "#path=<encoded>"): reveal://reveal?path=… (select in Finder) and reveal://obsidian?path=…
// (show the folder in the Obsidian vault that holds it; the handler app finds the vault and
// refuses a folder outside every vault). Nothing opens until a button is pressed. The fragment
// never reaches the server.

(function (root) {
  'use strict';

  function build(fragment) {
    var make = (typeof module !== 'undefined' && module.exports) ? require('./reveal.js').buildRevealUri : root.buildRevealUri;
    var r = make(fragment);
    if (r.error) return r;
    return { finder: r.uri, obsidian: r.uri.replace(/^reveal:\/\/reveal\?/, 'reveal://obsidian?'), target: r.target };
  }

  root.buildFolderUris = build;
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { buildFolderUris: build };
    return;
  }

  function render() {
    var result = build(root.location.hash);
    var status = document.getElementById('status');
    var where = document.getElementById('where');
    var finder = document.getElementById('finder');
    var obsidian = document.getElementById('obsidian');
    if (result.error) {
      status.textContent = result.error;
      where.textContent = '';
      finder.hidden = obsidian.hidden = true;
      return;
    }
    where.textContent = result.target;
    var om = root.LinkBridgeOnMac;
    if (om && om.isRemoteBrowser()) {
      status.textContent = 'This browser is not on the Mac; ask the Mac to show the folder:';
      om.wireOnMac('reveal', { path: result.target }, 'Reveal in Finder on the Mac', 'onmac');
      om.wireOnMac('folder-obsidian', { path: result.target }, 'Open in Obsidian on the Mac', 'onmac2');
      return;
    }
    status.textContent = 'Where should this folder open?';
    finder.href = result.finder; finder.hidden = false;
    obsidian.href = result.obsidian; obsidian.hidden = false;
  }

  document.addEventListener('DOMContentLoaded', render);
  root.addEventListener('hashchange', render);
})(typeof window !== 'undefined' ? window : globalThis);
