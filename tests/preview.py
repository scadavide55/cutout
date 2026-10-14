#!/usr/bin/env python3
"""Allowlisted localhost preview WITHOUT isolation headers, like GitHub Pages.
Run: python3 tests/preview.py 8091
"""
import http.server
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TYPES = {'index.html':'text/html; charset=utf-8', 'sw.js':'application/javascript', 'og.png':'image/png'}

class Handler(http.server.BaseHTTPRequestHandler):
    def serve(self, body):
        name = self.path.split('?')[0].lstrip('/') or 'index.html'
        if name not in TYPES:
            self.send_error(404)
            return
        data = (ROOT / name).read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', TYPES[name])
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        if body: self.wfile.write(data)

    def do_GET(self): self.serve(True)
    def do_HEAD(self): self.serve(False)
    def log_message(self, *args): pass

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8091
with http.server.ThreadingHTTPServer(('127.0.0.1', port), Handler) as server:
    print('Headerless preview: http://localhost:%d/' % port, flush=True)
    server.serve_forever()
