#!/usr/bin/env python3
"""Decide what a reveal:// link may reveal. Prints the path, or nothing (exit 1) when refused.

The "Reveal in Finder" applet runs this before acting, so the rules live in one testable place.
A reveal:// link can arrive from any app or web page once the scheme is registered, so the link
is untrusted. The action is only ever `open -R <path>` (select the item in a Finder window):
nothing is opened, launched or executed, which keeps these rules short.

Accepted:  reveal://reveal?path=<percent-encoded path>  where the path exists, and (0.1.14)
           reveal://obsidian?path=<percent-encoded path>, the same rules, acted on by
           reveal_obsidian.py (open the folder in the Obsidian vault that holds it). An absolute path
           is taken as is; a relative one ("dev/project", or "~/dev/project") is under the home
           folder, which keeps the links a status line shows short.
Refused:   any other scheme or host, any other parameter, an empty path, control characters,
           a path that does not exist, and a path inside an application or plug-in bundle
           (revealing a bundle's innards is never what a link means; the bundle itself is fine).
"""
import os
import sys
import urllib.parse

SCHEME = "reveal"
HOST = "reveal"
HOSTS = ("reveal", "obsidian")
HOME = os.path.expanduser("~")
BUNDLE_SUFFIXES = (".app", ".framework", ".bundle", ".plugin", ".appex", ".kext", ".xpc", ".prefPane")


def decode(url):
    try:
        p = urllib.parse.urlsplit(url)
    except ValueError:
        return None
    if p.scheme != SCHEME or p.netloc not in HOSTS:
        return None
    params = urllib.parse.parse_qsl(p.query, keep_blank_values=True)
    if len(params) != 1 or params[0][0] != "path":
        return None
    path = params[0][1]
    if not path or any(ord(c) < 0x20 or ord(c) == 0x7F for c in path):
        return None
    if path.startswith("~/"):
        path = path[2:]
    if not path.startswith("/"):
        path = os.path.join(HOME, path)
    real = os.path.realpath(path)
    if not os.path.exists(real):
        return None
    parts = real.split(os.sep)[:-1]          # every ancestor, not the item itself
    if any(part.endswith(BUNDLE_SUFFIXES) for part in parts if part):
        return None
    return real


def host(url):
    """"reveal" or "obsidian" for an accepted link, else None."""
    try:
        return urllib.parse.urlsplit(url).netloc if urllib.parse.urlsplit(url).netloc in HOSTS else None
    except ValueError:
        return None


def main(argv):
    """Prints the decoded path (exit 0), or nothing (exit 1). With --host, prints "<host> <path>"."""
    args = [a for a in argv[1:] if a != "--host"]
    if len(args) != 1:
        print("usage: reveal_decode.py [--host] <reveal-url>", file=sys.stderr)
        return 2
    path = decode(args[0])
    if path is None:
        return 1
    print(f"{host(args[0])} {path}" if "--host" in argv else path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
