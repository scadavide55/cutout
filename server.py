#!/usr/bin/env python3
"""Tiny static file server for local testing of the site."""
import http.server, socketserver, sys, os

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "public"), **kw)
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
    print(f"serving on http://127.0.0.1:{port}", flush=True)
    httpd.serve_forever()
