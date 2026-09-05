import base64
import http.server
import os
import urllib.error
import urllib.request

UPSTREAM = "http://127.0.0.1:8080"
PORT = int(os.environ.get("PORT", "10000"))
AUTH_USER = os.environ["SEARX_AUTH_USER"]
AUTH_PASSWORD = os.environ["SEARX_AUTH_PASSWORD"]

class Gateway(http.server.ThreadingHTTPServer):
    allow_reuse_address = True

class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _auth_ok(self):
        value = self.headers.get("Authorization", "")
        if not value.startswith("Basic "):
            return False
        try:
            decoded = base64.b64decode(value[6:]).decode("utf-8")
            user, password = decoded.split(":", 1)
            return user == AUTH_USER and password == AUTH_PASSWORD
        except Exception:
            return False

    def _response(self, status, body, content_type="text/plain; charset=utf-8",
                  extra_headers=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/healthz":
            self._response(
                200,
                b'{"ok":true,"service":"leadhunter-searxng","status":"healthy"}',
                "application/json",
            )
            return

        if not self._auth_ok():
            self._response(
                401,
                b"",
                extra_headers={"WWW-Authenticate": 'Basic realm="LeadHunter Search"'},
            )
            return

        target = UPSTREAM + self.path
        request = urllib.request.Request(
            target,
            headers={
                "User-Agent": "LeadHunter-Research-Worker/1.0",
                "Accept": self.headers.get("Accept", "*/*"),
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read()
                content_type = response.headers.get(
                    "Content-Type", "text/html; charset=utf-8"
                )
                self._response(response.status, body, content_type)
        except urllib.error.HTTPError as error:
            body = error.read()
            self._response(
                error.code,
                body,
                error.headers.get("Content-Type", "text/plain; charset=utf-8"),
            )
        except Exception as error:
            print(f"Gateway upstream error: {error}", flush=True)
            self._response(502, b'{"ok":false,"error":"upstream_unavailable"}',
                           "application/json")

    def do_POST(self):
        self._response(405, b'{"ok":false,"error":"method_not_allowed"}',
                       "application/json")

    def log_message(self, format_string, *args):
        print("gateway:", format_string % args, flush=True)

if __name__ == "__main__":
    print(f"LeadHunter SearXNG gateway listening on :{PORT}", flush=True)
    Gateway(("0.0.0.0", PORT), Handler).serve_forever()
