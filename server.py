#!/usr/bin/env python3
"""Tiny static file server for local testing of the site.

Serves the folder this file lives in, on 127.0.0.1 only. Browsers restrict
some features on file:// pages, so index.html is opened through this instead.
"""
import http.server, socketserver, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))

# Only these files are ever served. Everything else in this folder has no
# business on a web server: the git history, this script, the README.
SITE = {"index.html", "favicon.ico", "robots.txt"}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=HERE, **kw)

    def translate_path(self, path):
        name = path.split("?")[0].split("#")[0].lstrip("/") or "index.html"
        if name not in SITE:
            return os.path.join(HERE, "__not_a_served_file__")   # -> 404
        return os.path.join(HERE, name)

    def list_directory(self, path):
        self.send_error(404, "Not found")                        # no folder listings
        return None

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "credentialless")
        super().end_headers()

    def log_message(self, *a):
        pass


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
    print(f"Cutout is being served from: {HERE}", flush=True)
    print(f"  http://127.0.0.1:{port}/", flush=True)
    httpd.serve_forever()
