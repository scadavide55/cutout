#!/usr/bin/env python3
"""Static server for public/, bound to the whole LAN so a phone can reach it.

Same headers as server.py, but listening on 0.0.0.0 instead of 127.0.0.1.
Only run this on a network you trust: anyone on the same Wi-Fi can open the
page while it is up.
"""
import http.server, socketserver, sys, os, socket

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def end_headers(self):
        # No caching, so edits show up on reload while testing.
        self.send_header("Cache-Control", "no-store")
        # These two enable multi-threaded WebAssembly, which makes inference
        # noticeably faster. Without them the page still works, just slower.
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "credentialless")
        super().end_headers()

    def log_message(self, fmt, *args):
        print("  %s - %s" % (self.address_string(), fmt % args), flush=True)


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))          # no traffic sent, just picks the route
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
socketserver.ThreadingTCPServer.allow_reuse_address = True
socketserver.ThreadingTCPServer.daemon_threads = True

with socketserver.ThreadingTCPServer(("0.0.0.0", port), Handler) as httpd:
    print("Cutout is being served from: %s" % ROOT, flush=True)
    print("", flush=True)
    print("  On this Mac   : http://127.0.0.1:%d/" % port, flush=True)
    print("  On your phone : http://%s:%d/" % (lan_ip(), port), flush=True)
    print("", flush=True)
    print("Phone and Mac must be on the same Wi-Fi. Ctrl+C to stop.", flush=True)
    httpd.serve_forever()
