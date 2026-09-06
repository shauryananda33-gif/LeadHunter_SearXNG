from __future__ import annotations

import base64
import hmac
import http.server
import os
import urllib.error
import urllib.request

UPSTREAM = os.getenv("SEARXNG_UPSTREAM", "http://127.0.0.1:8080").rstrip("/")
PORT = int(os.getenv("PORT", "10000"))
AUTH_USER = os.environ["SEARX_AUTH_USER"]
AUTH_PASSWORD = os.environ["SEARX_AUTH_PASSWORD"]
MAX_PATH_LENGTH = 4096


class Server(http.server.ThreadingHTTPServer):
    allow_reuse_address = True


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def authorized(self) -> bool:
        value = self.headers.get("Authorization", "")
        if not value.startswith("Basic "):
            return False
        try:
            decoded = base64.b64decode(value[6:], validate=True).decode("utf-8")
            user, password = decoded.split(":", 1)
        except Exception:
            return False
        return hmac.compare_digest(user, AUTH_USER) and hmac.compare_digest(password, AUTH_PASSWORD)

    def send_body(self, status: int, body: bytes, content_type: str = "application/json; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/healthz":
            self.send_body(200, b'{"ok":true,"service":"leadhunter-searxng","status":"healthy"}')
            return
        if len(self.path) > MAX_PATH_LENGTH:
            self.send_body(414, b'{"ok":false,"error":"request_uri_too_long"}')
            return
        if not self.authorized():
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="LeadHunter SearXNG"')
            self.send_header("Content-Length", "0")
            self.send_header("Connection", "close")
            self.end_headers()
            return

        request = urllib.request.Request(
            UPSTREAM + self.path,
            headers={
                "User-Agent": "LeadHunter-Research-Worker/0.5.0",
                "Accept": self.headers.get("Accept", "application/json"),
                "Accept-Language": self.headers.get("Accept-Language", "en"),
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                self.send_body(response.status, response.read(), response.headers.get("Content-Type", "application/octet-stream"))
        except urllib.error.HTTPError as exc:
            self.send_body(exc.code, exc.read(), exc.headers.get("Content-Type", "application/json"))
        except Exception as exc:
            print(f"gateway upstream error: {exc}", flush=True)
            self.send_body(502, b'{"ok":false,"error":"searxng_upstream_unavailable"}')

    def do_POST(self) -> None:
        self.send_body(405, b'{"ok":false,"error":"method_not_allowed"}')

    def log_message(self, fmt: str, *args: object) -> None:
        print("gateway:", fmt % args, flush=True)


if __name__ == "__main__":
    print(f"LeadHunter SearXNG gateway listening on 0.0.0.0:{PORT}", flush=True)
    server = Server(("0.0.0.0", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
