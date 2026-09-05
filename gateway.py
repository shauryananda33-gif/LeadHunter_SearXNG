import base64
import http.server
import os
import subprocess
import threading
import urllib.parse
import urllib.error

UPSTREAM_HOST = "127.0.0.1"
UPSTREAM_PORT = 8080
PUBLIC_PORT = int(os.environ.get("PORT", "10000"))

AUTH_USER = os.environ["SEARX_AUTH_USER"]
AUTH_PASSWORD = os.environ["SEARX_AUTH_PASSWORD"]

class Gateway(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _authorized(self):
        header = self.headers.get("Authorization", "")
        if not header.startswith("Basic "):
            return False
        try:
            raw = base64.b64decode(header[6:]).decode("utf-8")
            user, password = raw.split(":", 1)
            return user == AUTH_USER and password == AUTH_PASSWORD
        except Exception:
            return False

    def _send(self, status, body=b"", content_type="text/plain; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_GET(self):
        if self.path == "/healthz":
            self._send(200, b'{"ok":true,"service":"leadhunter-searxng","status":"healthy"}',
                       "application/json")
            return

        if not self._authorized():
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="LeadHunter Search"')
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        # Proxy GET to SearXNG. This covers /search and the normal UI.
        import urllib.request
        url = f"http://{UPSTREAM_HOST}:{UPSTREAM_PORT}{self.path}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "LeadHunter-Research-Worker/1.0"},
        )
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                data = r.read()
                ctype = r.headers.get("Content-Type", "text/html; charset=utf-8")
                self._send(r.status, data, ctype)
        except urllib.error.HTTPError as e:
            data = e.read()
            self._send(e.code, data, e.headers.get("Content-Type", "text/plain"))
        except Exception as e:
            self._send(502, f"upstream error: {e}".encode())

    def log_message(self, fmt, *args):
        print("gateway:", fmt % args, flush=True)

def run_searxng():
    os.execvp("python3", ["python3", "-m", "searx.webapp"])

if __name__ == "__main__":
    t = threading.Thread(target=run_searxng, daemon=True)
    t.start()

    # Wait for SearXNG to bind, then serve the authenticated gateway.
    import time
    time.sleep(8)

    server = http.server.ThreadingHTTPServer(("0.0.0.0", PUBLIC_PORT), Gateway)
    print(f"LeadHunter SearXNG gateway listening on 0.0.0.0:{PUBLIC_PORT}", flush=True)
    server.serve_forever()
